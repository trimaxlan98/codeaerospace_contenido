"""Asistente IA de depuracion via Vertex AI (Gemini 2.5, solo us-central1).

Unico modulo del backend con salida a red (HTTPS a *-aiplatform.googleapis.com).
Feature-flag: si no existe la service account (gcp-key.json) todo el asistente
queda deshabilitado y la app funciona igual.

El SDK se importa de forma perezosa para no cargar ~decenas de MB en cada
arranque si la funcion no se usa (el servicio corre con MemoryMax=512M).
"""

import asyncio
import json
import re
import time
from collections import deque

from .config import Settings

# Presupuesto de entrada acotado: el script y los logs se truncan antes de
# enviarse (evita facturas sorpresa y prompts gigantes).
MAX_SCRIPT_CHARS = 20_000
MAX_LOG_CHARS = 8_000
MAX_PROMPT_CHARS = 4_000
REQUEST_TIMEOUT_S = 90

_FENCE_RE = re.compile(r"```(?:python)?\s*\n(.*?)```", re.DOTALL)


class AIError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


class AIRateLimiter:
    """~N peticiones/min. App de sesion unica: un solo cubo en memoria."""

    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._hits: deque[float] = deque()

    def check(self) -> None:
        now = time.time()
        while self._hits and now - self._hits[0] > 60:
            self._hits.popleft()
        if len(self._hits) >= self.per_minute:
            wait = int(60 - (now - self._hits[0])) + 1
            raise AIError(429, f"Limite del asistente alcanzado. Espera {wait} s.")
        self._hits.append(now)


class Assistant:
    def __init__(self, cfg: Settings, conocimiento=None) -> None:
        self.cfg = cfg
        self.conocimiento = conocimiento  # Conocimiento del proyecto (opcional)
        self.limiter = AIRateLimiter(cfg.ai_rate_limit_per_min)
        self._client = None
        self._project_id: str | None = None

    def _contexto_proyecto(self) -> str:
        """Paquete de conocimiento (primitivas + convenciones) para que las
        respuestas usen la biblioteca del canal en vez de inventar APIs."""
        if self.conocimiento is None:
            return ""
        try:
            return "\n\n" + self.conocimiento.contexto()
        except Exception:
            return ""  # el asistente debe funcionar aunque el paquete falle

    @property
    def enabled(self) -> bool:
        return self.cfg.gcp_key_path.is_file()

    def _get_client(self):
        if self._client is None:
            from google import genai
            from google.oauth2 import service_account

            with open(self.cfg.gcp_key_path, encoding="utf-8") as f:
                self._project_id = json.load(f)["project_id"]
            creds = service_account.Credentials.from_service_account_file(
                str(self.cfg.gcp_key_path),
                scopes=["https://www.googleapis.com/auth/cloud-platform"],
            )
            self._client = genai.Client(
                vertexai=True, project=self._project_id,
                location=self.cfg.gcp_location, credentials=creds,
            )
        return self._client

    def _call_model(self, model: str, system: str, user: str) -> str:
        """Llamada bloqueante al SDK (se ejecuta en thread; mockeada en tests)."""
        from google.genai import types
        client = self._get_client()
        resp = client.models.generate_content(
            model=model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                temperature=0.2,
                max_output_tokens=8192,
                http_options=types.HttpOptions(timeout=REQUEST_TIMEOUT_S * 1000),
            ),
        )
        return resp.text or ""

    async def _generate(self, model: str, system: str, user: str) -> str:
        if not self.enabled:
            raise AIError(503, "Asistente IA no configurado")
        self.limiter.check()
        try:
            text = await asyncio.wait_for(
                asyncio.to_thread(self._call_model, model, system, user),
                timeout=REQUEST_TIMEOUT_S + 10)
        except asyncio.TimeoutError:
            raise AIError(504, "Vertex AI no respondio a tiempo")
        except AIError:
            raise
        except Exception as e:
            raise AIError(502, f"Error de Vertex AI: {type(e).__name__}: {e}")
        if not text.strip():
            raise AIError(502, "Vertex AI devolvio una respuesta vacia")
        return text.strip()

    # ── acciones ─────────────────────────────────────────────────────────────

    async def explain(self, script: str, logs: str) -> str:
        system = (
            "Eres un experto en Manim Community Edition. Recibes un script de "
            "manim y el log de un render fallido. Explica EN ESPAÑOL, en pocas "
            "lineas y sin rodeos: (1) que fallo, (2) por que, (3) como "
            "arreglarlo. Usa texto plano, sin encabezados ni bloques de codigo "
            "largos; como mucho referencias breves a lineas o nombres."
        )
        user = (f"SCRIPT:\n{_clip(script, MAX_SCRIPT_CHARS)}\n\n"
                f"LOG DEL RENDER (final):\n{_clip_tail(logs, MAX_LOG_CHARS)}")
        return await self._generate(self.cfg.gemini_model_fast, system, user)

    async def fix(self, script: str, logs: str) -> str:
        system = (
            "Eres un experto en Manim Community Edition. Recibes un script de "
            "manim que fallo al renderizar y su log de error. Devuelve el "
            "script COMPLETO corregido, funcional con `manim render`. Manten "
            "el estilo y la intencion del original; corrige solo lo necesario. "
            "Responde UNICAMENTE con el codigo Python dentro de un bloque "
            "```python```. Sin explicaciones fuera del bloque."
        ) + self._contexto_proyecto()
        user = (f"SCRIPT:\n{_clip(script, MAX_SCRIPT_CHARS)}\n\n"
                f"LOG DEL RENDER (final):\n{_clip_tail(logs, MAX_LOG_CHARS)}")
        text = await self._generate(self.cfg.gemini_model_deep, system, user)
        return _extract_code(text)

    async def generate(self, prompt: str) -> str:
        system = (
            "Eres un experto en Manim Community Edition (v0.20). El usuario "
            "describe una animacion; devuelve un script manim completo: "
            "`from manim import *`, UNA clase Scene con `construct`, sin "
            "dependencias externas, sin acceso a red ni a archivos. Apunta a "
            "renders cortos (10-20 s de animacion). Sigue la guia del "
            "proyecto y USA sus primitivas cuando encajen (con las lineas de "
            "sys.path del inicio). Responde UNICAMENTE con el codigo dentro "
            "de un bloque ```python```."
        ) + self._contexto_proyecto()
        text = await self._generate(self.cfg.gemini_model_deep, system,
                                    _clip(prompt, MAX_PROMPT_CHARS))
        return _extract_code(text)


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncado]"


def _clip_tail(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return "[truncado] …\n" + text[-limit:]


def _extract_code(text: str) -> str:
    m = _FENCE_RE.search(text)
    if m:
        return m.group(1).strip() + "\n"
    # Sin fence: si ya parece Python puro, devolverlo tal cual.
    return text.strip() + "\n"
