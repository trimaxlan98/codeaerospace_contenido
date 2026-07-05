"""Autenticacion de ManimStudio: usuario unico, cookie firmada, anti fuerza bruta.

- Password verificada contra hash bcrypt sembrado por variable de entorno.
- Sesion: token firmado con itsdangerous (TimestampSigner) en cookie
  httpOnly + Secure + SameSite=Strict. SameSite=Strict + API solo-JSON
  actua ademas como defensa CSRF para esta app de un solo usuario.
- Fuerza bruta: contador de fallos por IP y global; al superar el limite se
  bloquea el login durante un periodo fijo. La comparacion de usuario usa
  secrets.compare_digest y ante usuario inexistente se verifica igualmente
  un hash dummy para no filtrar por timing.
"""

import secrets
import time

import bcrypt
from fastapi import Depends, HTTPException, Request, Response
from itsdangerous import BadSignature, SignatureExpired, TimestampSigner

from .config import Settings, get_settings

# Hash dummy para igualar tiempos cuando el usuario no coincide.
_DUMMY_HASH = bcrypt.hashpw(b"dummy-password-for-timing", bcrypt.gensalt(rounds=12))


class LoginRateLimiter:
    """Fallos consecutivos -> bloqueo temporal. En memoria: proceso unico."""

    def __init__(self, max_failures: int, lockout_seconds: int) -> None:
        self.max_failures = max_failures
        self.lockout_seconds = lockout_seconds
        self._failures: dict[str, list[float]] = {}
        self._locked_until: dict[str, float] = {}

    def _keys(self, ip: str) -> tuple[str, str]:
        return (f"ip:{ip}", "global")

    def check(self, ip: str) -> float:
        """Devuelve segundos restantes de bloqueo (0 si puede intentar)."""
        now = time.time()
        remaining = 0.0
        for key in self._keys(ip):
            until = self._locked_until.get(key, 0)
            if until > now:
                remaining = max(remaining, until - now)
        return remaining

    def record_failure(self, ip: str) -> None:
        now = time.time()
        window = self.lockout_seconds
        for key in self._keys(ip):
            fails = [t for t in self._failures.get(key, []) if now - t < window]
            fails.append(now)
            self._failures[key] = fails
            # El umbral global es mas laxo (x3) para que un atacante no pueda
            # bloquear al usuario legitimo tan facilmente desde otra IP.
            limit = self.max_failures if key.startswith("ip:") else self.max_failures * 3
            if len(fails) >= limit:
                self._locked_until[key] = now + self.lockout_seconds

    def record_success(self, ip: str) -> None:
        for key in self._keys(ip):
            self._failures.pop(key, None)
            self._locked_until.pop(key, None)


_rate_limiter: LoginRateLimiter | None = None


def get_rate_limiter(cfg: Settings) -> LoginRateLimiter:
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = LoginRateLimiter(cfg.login_max_failures, cfg.login_lockout_seconds)
    return _rate_limiter


def client_ip(request: Request) -> str:
    # nginx local es el unico proxy delante; X-Real-IP lo fija el.
    return request.headers.get("x-real-ip") or (request.client.host if request.client else "?")


def verify_credentials(cfg: Settings, username: str, password: str) -> bool:
    user_ok = secrets.compare_digest(username.encode(), cfg.admin_user.encode())
    target_hash = cfg.admin_password_hash.encode() if user_ok else _DUMMY_HASH
    try:
        pass_ok = bcrypt.checkpw(password.encode(), target_hash)
    except ValueError:
        pass_ok = False
    return user_ok and pass_ok


def _signer(cfg: Settings) -> TimestampSigner:
    return TimestampSigner(cfg.secret_key, salt="manimstudio-session")


def create_session(cfg: Settings, response: Response) -> None:
    token = _signer(cfg).sign(f"{cfg.admin_user}:{secrets.token_hex(16)}".encode()).decode()
    response.set_cookie(
        cfg.cookie_name,
        token,
        max_age=cfg.session_max_age,
        httponly=True,
        secure=cfg.cookie_secure,
        samesite="strict",
        path="/",
    )


def clear_session(cfg: Settings, response: Response) -> None:
    response.delete_cookie(cfg.cookie_name, path="/")


def session_valid(cfg: Settings, request: Request) -> bool:
    token = request.cookies.get(cfg.cookie_name)
    if not token:
        return False
    try:
        value = _signer(cfg).unsign(token, max_age=cfg.session_max_age)
    except (BadSignature, SignatureExpired):
        return False
    return value.decode().split(":", 1)[0] == cfg.admin_user


def require_auth(request: Request, cfg: Settings = Depends(get_settings)) -> None:
    """Dependencia obligatoria en TODA ruta salvo login/health."""
    if not session_valid(cfg, request):
        raise HTTPException(status_code=401, detail="No autenticado")
