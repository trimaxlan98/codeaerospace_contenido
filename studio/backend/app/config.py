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

        # Narracion de proyectos (guion + TTS). Comparte credenciales y
        # feature-flag con el asistente IA; escribe fuera de render_jobs/
        # (requiere ReadWritePaths sobre guiones/ en la unidad systemd).
        self.guiones_dir = Path(os.environ.get(
            "MS_GUIONES_DIR", str(self.workspace / "guiones")))
        self.gemini_model_tts = os.environ.get(
            "MS_GEMINI_MODEL_TTS", "gemini-2.5-flash-preview-tts")
        # Proveedores de voz (ver app/tts.py). `MS_TTS_PROVIDER` es el
        # preferido; si no esta disponible se cae al primero que sintetice
        # (edge -> piper -> vertex). `MS_TTS_PROVEEDORES` acota cuales se
        # ofrecen (los tests lo usan para simular "sin voz").
        self.tts_provider = os.environ.get("MS_TTS_PROVIDER", "edge")
        self.tts_proveedores = tuple(
            p.strip() for p in os.environ.get(
                "MS_TTS_PROVEEDORES", "vertex,edge,piper,archivo").split(",")
            if p.strip())
        self.tts_voice_vertex = os.environ.get("MS_TTS_VOICE", "Charon")
        self.tts_voice = self.tts_voice_vertex  # compatibilidad
        self.tts_voice_edge = os.environ.get("MS_TTS_VOICE_EDGE",
                                             "es-MX-JorgeNeural")
        self.tts_voice_piper = os.environ.get("MS_TTS_VOICE_PIPER",
                                              "es_MX-claude-high")
        # Modelos .onnx de Piper. Fuera del repo por defecto (63 MB por voz).
        self.piper_voices_dir = Path(os.environ.get(
            "MS_PIPER_VOICES_DIR", "/etc/manimstudio/voces"))
        # Subidas de narracion propia: tope del cuerpo (un WAV estereo a
        # 48 kHz de 45 s son ~8.6 MB; 25 MB deja aire para 2 min).
        self.max_upload_audio_mb = int(os.environ.get("MS_MAX_UPLOAD_AUDIO_MB", "25"))

        # Peliculas montadas (los clips de un curso unidos en un archivo). Van
        # bajo exports/, que ya era el sitio de los cursos muxeados a mano y
        # esta en .gitignore. Requiere ReadWritePaths sobre exports/ en la
        # unidad systemd, igual que guiones/.
        # El runner tiene esta MISMA ruta como constante relativa
        # ("exports/peliculas"): si una cambia, la otra tambien.
        self.peliculas_dir = Path(os.environ.get(
            "MS_PELICULAS_DIR", str(self.workspace / "exports" / "peliculas")))
        # Presentaciones: fragmentos, posters y el .pptx que se descarga. El
        # runner tiene esta MISMA ruta como constante relativa
        # ("exports/presentaciones"): si una cambia, la otra tambien.
        self.presentaciones_dir = Path(os.environ.get(
            "MS_PRESENTACIONES_DIR",
            str(self.workspace / "exports" / "presentaciones")))
        # Banco de sonidos audible: los wavs sueltos de la paleta de sfx.py.
        # El runner tiene esta misma ruta como constante ("exports/sfx").
        self.sfx_dir = Path(os.environ.get(
            "MS_SFX_DIR", str(self.workspace / "exports" / "sfx")))

        # Biblioteca curada de primitivas de Manim (solo lectura: la consume
        # el asistente via conocimiento.py y los demos de Animaciones).
        self.manim_extensions_dir = Path(os.environ.get(
            "MS_MANIM_EXTENSIONS_DIR",
            str(self.workspace / "studio" / "content" / "manim_extensions")))


settings: Settings | None = None


def get_settings() -> Settings:
    global settings
    if settings is None:
        settings = Settings()
    return settings
