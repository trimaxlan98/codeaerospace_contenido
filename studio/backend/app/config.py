"""Configuracion central de ManimStudio (variables de entorno con prefijo MS_)."""

import os
from pathlib import Path


def _req(name: str) -> str:
    val = os.environ.get(name, "")
    if not val:
        raise RuntimeError(f"Falta la variable de entorno obligatoria {name}")
    return val


class Settings:
    def __init__(self) -> None:
        self.admin_user: str = _req("MS_ADMIN_USER")
        self.admin_password_hash: str = _req("MS_ADMIN_PASSWORD_HASH")
        self.secret_key: str = _req("MS_SECRET_KEY")

        self.workspace = Path(os.environ.get("MS_WORKSPACE", "/var/www/codeaerospace_contenido"))
        self.render_jobs_dir = self.workspace / "render_jobs"
        self.db_path = Path(os.environ.get("MS_DB_PATH", str(self.workspace / "studio" / "manimstudio.db")))
        self.runner_socket = os.environ.get("MS_RUNNER_SOCKET", "/run/manimstudio/runner.sock")
        self.lessons_dir = Path(os.environ.get(
            "MS_LESSONS_DIR", str(self.workspace / "studio" / "content" / "lessons")))
        self.animations_dir = Path(os.environ.get(
            "MS_ANIMATIONS_DIR", str(self.workspace / "studio" / "content" / "animations")))

        self.cookie_name = "ms_session"
        self.cookie_secure = os.environ.get("MS_COOKIE_SECURE", "1") == "1"
        self.session_max_age = int(os.environ.get("MS_SESSION_MAX_AGE", "43200"))  # 12 h

        # Fuerza bruta: tras N fallos consecutivos, bloquear el login.
        self.login_max_failures = int(os.environ.get("MS_LOGIN_MAX_FAILURES", "5"))
        self.login_lockout_seconds = int(os.environ.get("MS_LOGIN_LOCKOUT", "900"))

        self.max_script_bytes = int(os.environ.get("MS_MAX_SCRIPT_BYTES", "200000"))
        self.default_timeout = int(os.environ.get("MS_DEFAULT_TIMEOUT", "600"))
        self.max_timeout = int(os.environ.get("MS_MAX_TIMEOUT", "1800"))

        self.metrics_interval = float(os.environ.get("MS_METRICS_INTERVAL", "4.0"))
        self.metrics_snapshot_path = Path(os.environ.get(
            "MS_METRICS_SNAPSHOT", str(self.db_path.parent / "metrics_history.json")))
        self.metrics_snapshot_interval = float(os.environ.get("MS_METRICS_SNAPSHOT_INTERVAL", "120.0"))

        # Cuota total de disco para render_jobs/ (videos + scripts + logs).
        self.max_storage_mb = int(os.environ.get("MS_MAX_STORAGE_MB", "2048"))

        # Asistente IA (Vertex AI). Feature-flag: sin credenciales, la app
        # funciona igual y la UI de IA se oculta.
        # Por defecto fuera del arbol montado en el contenedor de render
        # (/var/www/codeaerospace_contenido = /workspace ahi dentro): el
        # mount read-only ya evita la escritura, esto evita tambien la
        # lectura del secreto desde codigo no confiable.
        self.gcp_key_path = Path(os.environ.get(
            "MS_GCP_KEY_PATH", "/etc/manimstudio/gcp-key.json"))
        self.gcp_location = os.environ.get("MS_GCP_LOCATION", "us-central1")
        self.gemini_model_fast = os.environ.get("MS_GEMINI_MODEL_FAST", "gemini-2.5-flash")
        self.gemini_model_deep = os.environ.get("MS_GEMINI_MODEL_DEEP", "gemini-2.5-pro")
        self.ai_rate_limit_per_min = int(os.environ.get("MS_AI_RATE_LIMIT", "10"))

        # Fable 5 (Anthropic) — genera primitivas nuevas de Manim para la
        # biblioteca curada de studio/content/manim_extensions/. Feature-flag:
        # sin API key, el asistente queda deshabilitado y la app funciona igual.
        self.anthropic_api_key = os.environ.get("MS_ANTHROPIC_API_KEY", "")
        self.fable_model = os.environ.get("MS_FABLE_MODEL", "claude-fable-5")
        self.fable_rate_limit_per_min = int(os.environ.get("MS_FABLE_RATE_LIMIT", "5"))
        self.manim_extensions_dir = Path(os.environ.get(
            "MS_MANIM_EXTENSIONS_DIR",
            str(self.workspace / "studio" / "content" / "manim_extensions")))
        self.pending_primitives_dir = Path(os.environ.get(
            "MS_PENDING_PRIMITIVES_DIR", str(self.workspace / "pending_primitives")))


settings: Settings | None = None


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
