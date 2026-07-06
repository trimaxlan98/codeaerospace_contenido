"""Fable 5 (Anthropic): genera primitivas nuevas de Manim (Mobjects o
Animations autocontenidos) a partir de una descripcion en lenguaje natural,
para la biblioteca curada de studio/content/manim_extensions/.

Feature-flag: sin API key de Anthropic configurada, el asistente queda
deshabilitado y el resto de la app funciona igual (igual patron que ai.py
con Vertex AI).
"""

import asyncio
import re
import time
from collections import deque

from .config import Settings

MAX_DESCRIPTION_CHARS = 4_000
MAX_FEEDBACK_CHARS = 2_000
MAX_PREVIOUS_CODE_CHARS = 20_000
REQUEST_TIMEOUT_S = 600  # Fable 5 puede tardar varios minutos por turno

_PRIMITIVE_FENCE_RE = re.compile(r"```python:primitive\s*\n(.*?)```", re.DOTALL)
_DEMO_FENCE_RE = re.compile(r"```python:demo\s*\n(.*?)```", re.DOTALL)

SYSTEM_PROMPT = (
    "Eres un experto en Manim Community Edition (v0.20+) que investiga "
    "tecnicas de animacion poco comunes o nunca antes vistas. El usuario "
    "describe un efecto visual nuevo; devuelve DOS bloques de codigo Python "
    "en tu respuesta:\n\n"
    "1. Un bloque marcado exactamente ```python:primitive``` con UNA unica "
    "clase autocontenida (Mobject o Animation de Manim CE) que implemente el "
    "efecto. Debe ser importable como `from primitive import <NombreClase>`, "
    "sin dependencias externas, sin red ni acceso a archivos.\n"
    "2. Un bloque marcado exactamente ```python:demo``` con un script "
    "completo: `from manim import *`, la linea "
    "`from primitive import <NombreClase>` y EXACTAMENTE una clase que "
    "herede de Scene (o variante de Scene) que use la primitiva para "
    "mostrar el efecto en menos de 15 segundos de animacion.\n\n"
    "Responde con una linea de explicacion breve antes de ambos bloques, y "
    "nada de texto adicional despues."
)


class FableError(Exception):
    def __init__(self, status: int, detail: str) -> None:
        super().__init__(detail)
        self.status = status
        self.detail = detail


class FableRateLimiter:
    """~N peticiones/min. Mismo diseño que AIRateLimiter (ai.py)."""

    def __init__(self, per_minute: int) -> None:
        self.per_minute = per_minute
        self._hits: deque[float] = deque()

    def check(self) -> None:
        now = time.time()
        while self._hits and now - self._hits[0] > 60:
            self._hits.popleft()
        if len(self._hits) >= self.per_minute:
            wait = int(60 - (now - self._hits[0])) + 1
            raise FableError(429, f"Limite de Fable 5 alcanzado. Espera {wait} s.")
        self._hits.append(now)


class FableAssistant:
    def __init__(self, cfg: Settings) -> None:
        self.cfg = cfg
        self.limiter = FableRateLimiter(cfg.fable_rate_limit_per_min)
        self._client = None

    @property
    def enabled(self) -> bool:
        return bool(self.cfg.anthropic_api_key)

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.Anthropic(api_key=self.cfg.anthropic_api_key)
        return self._client

    def _call_model(self, user: str) -> str:
        """Llamada bloqueante al SDK (se ejecuta en thread; mockeada en tests)."""
        client = self._get_client()
        resp = client.messages.create(
            model=self.cfg.fable_model,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            output_config={"effort": "high"},
            betas=["server-side-fallback-2026-06-01"],
            fallbacks=[{"model": "claude-opus-4-8"}],
            messages=[{"role": "user", "content": user}],
        )
        return "".join(b.text for b in resp.content if b.type == "text")

    async def propose_primitive(self, description: str, feedback: str | None = None,
                                previous_code: str | None = None) -> dict:
        if not self.enabled:
            raise FableError(503, "Fable 5 no configurado")
        self.limiter.check()

        user = f"DESCRIPCION DEL EFECTO:\n{_clip(description, MAX_DESCRIPTION_CHARS)}"
        if previous_code and feedback:
            user += (
                "\n\nVERSION ANTERIOR DE LA PRIMITIVA (rechazada):\n"
                f"{_clip(previous_code, MAX_PREVIOUS_CODE_CHARS)}\n\n"
                f"FEEDBACK PARA CORREGIR:\n{_clip(feedback, MAX_FEEDBACK_CHARS)}"
            )

        try:
            text = await asyncio.wait_for(
                asyncio.to_thread(self._call_model, user),
                timeout=REQUEST_TIMEOUT_S + 30)
        except asyncio.TimeoutError:
            raise FableError(504, "Fable 5 no respondio a tiempo")
        except FableError:
            raise
        except Exception as e:
            raise FableError(502, f"Error de Fable 5: {type(e).__name__}: {e}")

        primitive_code = _extract(text, _PRIMITIVE_FENCE_RE)
        demo_code = _extract(text, _DEMO_FENCE_RE)
        if not primitive_code or not demo_code:
            raise FableError(502,
                             "Fable 5 no devolvio los dos bloques de codigo esperados")

        explanation = text.split("```")[0].strip()
        return {"primitive_code": primitive_code, "demo_scene_code": demo_code,
                "explanation": explanation}


def _clip(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n… [truncado]"


def _extract(text: str, pattern: re.Pattern) -> str:
    m = pattern.search(text)
    return (m.group(1).strip() + "\n") if m else ""
