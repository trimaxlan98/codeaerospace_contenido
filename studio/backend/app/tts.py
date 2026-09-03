"""Proveedores de voz (texto a voz) para la narracion.

La narracion solo le pide dos cosas a un proveedor: `tts(texto, voz)`, que
devuelve PCM s16le mono a TTS_RATE, y opcionalmente `guion(system, user)`,
que escribe el guion cronometrado (solo Vertex sabe hacerlo). Todo lo demas
-recorte de silencio, alineado por secciones, ajuste al limite, WAV- es
aritmetica de bytes en `narracion.py` y no depende del motor.

Proveedores:

- `vertex`  Gemini TTS + Gemini para el guion. De pago; el 403 "dunning"
            del 2026-09 (facturacion en mora) es lo que motivo los demas.
- `edge`    edge-tts (voces neuronales de Microsoft Edge, 45 en espanol).
            Gratis, necesita red DESDE EL BACKEND (el contenedor de render
            no la tiene). Devuelve MP3; se decodifica con miniaudio.
- `piper`   Piper, offline, un modelo .onnx por voz en MS_PIPER_VOICES_DIR.
            Corre como subproceso para que su memoria (~250 MB con
            onnxruntime) no viva dentro del backend.
- `archivo` No sintetiza: la narracion la graba y la sube el dueno
            (PUT /narracion/{cid}/audio). Existe para que "proveedor"
            sea un concepto cerrado y el estado diga de donde salio la voz.

Cada proveedor se importa perezoso y se declara disponible o no con un
motivo legible: la UI enseña el motivo en vez de un boton muerto.
"""

from __future__ import annotations

import asyncio
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Protocol

TTS_RATE = 24_000  # PCM mono 16-bit; el mismo de Gemini TTS y de sfx.py

INSTRUCCION_TTS = (
    "Lee el siguiente guion de un video de divulgación científica en "
    "español, con tono cálido, claro y pausado, como la voz en off de un "
    "documental:\n\n"
)

GUION_SCHEMA = {
    "type": "object",
    "properties": {
        "secciones": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "t_inicio": {"type": "number"},
                    "t_fin": {"type": "number"},
                    "momento": {"type": "string"},
                    "texto": {"type": "string"},
                },
                "required": ["t_inicio", "t_fin", "momento", "texto"],
            },
        },
    },
    "required": ["secciones"],
}

PROVEEDORES = ("vertex", "edge", "piper", "archivo")

# Voces en espanol de edge-tts (listado medido el 2026-09-03: 45). Las
# primeras son las recomendadas para narrar; el resto sigue disponible.
EDGE_VOCES = [
    ("es-MX-JorgeNeural", "Jorge · Mexico"),
    ("es-MX-DaliaNeural", "Dalia · Mexico"),
    ("es-ES-AlvaroNeural", "Alvaro · Espana"),
    ("es-ES-ElviraNeural", "Elvira · Espana"),
    ("es-US-AlonsoNeural", "Alonso · EE. UU."),
    ("es-US-PalomaNeural", "Paloma · EE. UU."),
    ("es-AR-TomasNeural", "Tomas · Argentina"),
    ("es-AR-ElenaNeural", "Elena · Argentina"),
    ("es-CO-GonzaloNeural", "Gonzalo · Colombia"),
    ("es-CO-SalomeNeural", "Salome · Colombia"),
    ("es-CL-LorenzoNeural", "Lorenzo · Chile"),
    ("es-CL-CatalinaNeural", "Catalina · Chile"),
    ("es-PE-AlexNeural", "Alex · Peru"),
    ("es-PE-CamilaNeural", "Camila · Peru"),
    ("es-VE-SebastianNeural", "Sebastian · Venezuela"),
    ("es-VE-PaolaNeural", "Paola · Venezuela"),
    ("es-UY-MateoNeural", "Mateo · Uruguay"),
    ("es-UY-ValentinaNeural", "Valentina · Uruguay"),
    ("es-ES-XimenaNeural", "Ximena · Espana"),
    ("es-GT-AndresNeural", "Andres · Guatemala"),
    ("es-GT-MartaNeural", "Marta · Guatemala"),
    ("es-CR-JuanNeural", "Juan · Costa Rica"),
    ("es-CR-MariaNeural", "Maria · Costa Rica"),
    ("es-PA-RobertoNeural", "Roberto · Panama"),
    ("es-PA-MargaritaNeural", "Margarita · Panama"),
    ("es-DO-EmilioNeural", "Emilio · R. Dominicana"),
    ("es-DO-RamonaNeural", "Ramona · R. Dominicana"),
    ("es-EC-LuisNeural", "Luis · Ecuador"),
    ("es-EC-AndreaNeural", "Andrea · Ecuador"),
    ("es-BO-MarceloNeural", "Marcelo · Bolivia"),
    ("es-BO-SofiaNeural", "Sofia · Bolivia"),
    ("es-PY-MarioNeural", "Mario · Paraguay"),
    ("es-PY-TaniaNeural", "Tania · Paraguay"),
    ("es-CU-ManuelNeural", "Manuel · Cuba"),
    ("es-CU-BelkysNeural", "Belkys · Cuba"),
    ("es-HN-CarlosNeural", "Carlos · Honduras"),
    ("es-HN-KarlaNeural", "Karla · Honduras"),
    ("es-NI-FedericoNeural", "Federico · Nicaragua"),
    ("es-NI-YolandaNeural", "Yolanda · Nicaragua"),
    ("es-SV-RodrigoNeural", "Rodrigo · El Salvador"),
    ("es-SV-LorenaNeural", "Lorena · El Salvador"),
    ("es-PR-VictorNeural", "Victor · Puerto Rico"),
    ("es-PR-KarinaNeural", "Karina · Puerto Rico"),
    ("es-GQ-JavierNeural", "Javier · Guinea Ecuatorial"),
    ("es-GQ-TeresaNeural", "Teresa · Guinea Ecuatorial"),
]
EDGE_VOZ_DEFECTO = "es-MX-JorgeNeural"

VERTEX_VOCES = [
    ("Charon", "Charon · grave, informativa"),
    ("Kore", "Kore · firme"),
    ("Puck", "Puck · animada"),
    ("Fenrir", "Fenrir · energica"),
    ("Aoede", "Aoede · fresca"),
    ("Zephyr", "Zephyr · brillante"),
    ("Orus", "Orus · firme"),
    ("Leda", "Leda · juvenil"),
]


class Narrador(Protocol):
    id: str
    model_tts: str

    def tts(self, texto: str, voz: str) -> bytes: ...

    def guion(self, system: str, user: str) -> dict: ...


def _instalado(modulo: str) -> bool:
    return importlib.util.find_spec(modulo) is not None


# ── decodificacion (mp3/wav/flac/ogg -> PCM s16 mono @ TTS_RATE) ────────────

def decodificar(datos: bytes, sugerencia: str = "") -> bytes:
    """Cualquier audio que miniaudio entienda (mp3, wav, flac, ogg vorbis)
    a PCM s16le mono a TTS_RATE. Se hace aqui, en el backend, para no pagar
    un contenedor por cada seccion sintetizada. Lo que miniaudio no
    entiende (m4a/aac, opus en webm) va por el runner con ffmpeg."""
    import miniaudio  # perezoso: solo cuando hay que decodificar

    dec = miniaudio.decode(datos, output_format=miniaudio.SampleFormat.SIGNED16,
                           nchannels=1, sample_rate=TTS_RATE)
    return bytes(dec.samples)


def decodificable(nombre: str) -> bool:
    return Path(nombre).suffix.lower() in {".mp3", ".wav", ".flac", ".ogg"}


# ── Vertex (Gemini) ──────────────────────────────────────────────────────────

class VertexNarrador:
    """Cliente Vertex para guion (JSON) y TTS. Llamadas bloqueantes: usarlo
    desde un thread (asyncio.to_thread) o desde un CLI."""

    id = "vertex"

    def __init__(self, key_path: Path, location: str, model_guion: str,
                 model_tts: str) -> None:
        if not key_path.is_file():
            raise RuntimeError(
                f"No existe la service account {key_path}: la narracion "
                "necesita el mismo acceso a Vertex AI que el asistente IA.")
        from google import genai
        from google.oauth2 import service_account

        self.types = __import__("google.genai.types", fromlist=["types"])
        self.model_guion = model_guion
        self.model_tts = model_tts
        project = json.loads(key_path.read_text())["project_id"]
        creds = service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self.client = genai.Client(vertexai=True, project=project,
                                   location=location, credentials=creds)

    def guion(self, system: str, user: str) -> dict:
        t = self.types
        resp = self.client.models.generate_content(
            model=self.model_guion,
            contents=user,
            config=t.GenerateContentConfig(
                system_instruction=system,
                temperature=0.6,
                max_output_tokens=8192,
                response_mime_type="application/json",
                response_schema=GUION_SCHEMA,
            ),
        )
        return json.loads(resp.text)

    def tts(self, texto: str, voz: str) -> bytes:
        t = self.types
        for intento in (1, 2, 3):
            try:
                resp = self.client.models.generate_content(
                    model=self.model_tts,
                    contents=INSTRUCCION_TTS + texto,
                    config=t.GenerateContentConfig(
                        response_modalities=["AUDIO"],
                        speech_config=t.SpeechConfig(
                            voice_config=t.VoiceConfig(
                                prebuilt_voice_config=t.PrebuiltVoiceConfig(
                                    voice_name=voz))),
                    ),
                )
                part = resp.candidates[0].content.parts[0]
                return part.inline_data.data
            except Exception:
                if intento == 3:
                    raise
                time.sleep(5 * intento)
        raise RuntimeError("unreachable")


# ── edge-tts ─────────────────────────────────────────────────────────────────

class EdgeNarrador:
    """Voces neuronales de Edge via edge-tts. `rate` en la sintaxis del
    servicio ("-5%" = un poco mas pausado, lo que pide una narracion)."""

    id = "edge"
    model_tts = "edge-tts"

    def __init__(self, rate: str = "-5%") -> None:
        if not _instalado("edge_tts"):
            raise RuntimeError("edge-tts no esta instalado en el venv")
        if not _instalado("miniaudio"):
            raise RuntimeError("miniaudio no esta instalado en el venv")
        self.rate = rate

    def guion(self, system: str, user: str) -> dict:
        raise RuntimeError("edge-tts no escribe guiones: escribelo a mano "
                           "(o con Vertex) y narralo con solo_audio")

    async def _mp3(self, texto: str, voz: str) -> bytes:
        import edge_tts

        com = edge_tts.Communicate(texto, voz, rate=self.rate)
        trozos = []
        async for chunk in com.stream():
            if chunk["type"] == "audio":
                trozos.append(chunk["data"])
        return b"".join(trozos)

    def tts(self, texto: str, voz: str) -> bytes:
        ultimo: Exception | None = None
        for intento in (1, 2, 3):
            try:
                # Corre en un thread sin loop (asyncio.to_thread desde el
                # servicio, o un CLI): un loop propio por llamada.
                mp3 = asyncio.run(self._mp3(texto, voz))
                if not mp3:
                    raise RuntimeError("edge-tts devolvio audio vacio")
                return decodificar(mp3, ".mp3")
            except Exception as e:  # red, 403 del servicio, decodificacion
                ultimo = e
                if intento < 3:
                    time.sleep(3 * intento)
        raise RuntimeError(f"edge-tts fallo tras 3 intentos: {ultimo}")


# ── Piper (offline) ──────────────────────────────────────────────────────────

class PiperNarrador:
    """Piper como subproceso del mismo interprete (`python -m piper`). El
    modelo se carga por llamada (~0.3 s para 60 MB): mas barato que tener
    onnxruntime residente dentro de un servicio con MemoryMax."""

    id = "piper"
    model_tts = "piper"

    def __init__(self, voces_dir: Path, largo: float = 1.05) -> None:
        if not _instalado("piper"):
            raise RuntimeError("piper-tts no esta instalado en el venv")
        if not _instalado("miniaudio"):
            raise RuntimeError("miniaudio no esta instalado en el venv")
        self.voces_dir = Path(voces_dir)
        self.largo = largo  # length_scale: >1 mas pausado
        if not self.voces():
            raise RuntimeError(
                f"no hay ningun modelo .onnx en {self.voces_dir} "
                "(python -m piper.download_voices es_MX-claude-high)")

    def voces(self) -> list[tuple[str, str]]:
        out = []
        for p in sorted(self.voces_dir.glob("*.onnx")):
            if (p.with_suffix(".onnx.json")).is_file():
                out.append((p.stem, p.stem.replace("_", " ").replace("-", " · ")))
        return out

    def guion(self, system: str, user: str) -> dict:
        raise RuntimeError("Piper no escribe guiones: escribelo a mano "
                           "(o con Vertex) y narralo con solo_audio")

    def tts(self, texto: str, voz: str) -> bytes:
        modelo = self.voces_dir / f"{voz}.onnx"
        if not modelo.is_file() or ".." in voz or "/" in voz:
            raise RuntimeError(f"voz de Piper desconocida: {voz}")
        with tempfile.TemporaryDirectory(prefix="piper-") as tmp:
            salida = Path(tmp) / "voz.wav"
            argv = [sys.executable, "-m", "piper", "--model", str(modelo),
                    "--output_file", str(salida),
                    "--length_scale", str(self.largo),
                    "--sentence_silence", "0.35"]
            proc = subprocess.run(argv, input=texto.encode(), capture_output=True,
                                  timeout=600)
            if proc.returncode != 0 or not salida.is_file():
                raise RuntimeError("piper fallo: "
                                   + proc.stderr.decode(errors="replace")[-300:])
            return _atenuar(decodificar(salida.read_bytes(), ".wav"), 0.7)


def _atenuar(pcm: bytes, factor: float) -> bytes:
    """Piper entrega a escala completa (0 dBFS); Gemini y edge rondan -3 dB.
    Se iguala para que la mezcla con la cama no recorte."""
    import array
    a = array.array("h")
    a.frombytes(pcm[:len(pcm) // 2 * 2])
    for i, v in enumerate(a):
        a[i] = int(v * factor)
    return a.tobytes()


# ── archivo (narracion propia) ───────────────────────────────────────────────

class ArchivoNarrador:
    id = "archivo"
    model_tts = "grabacion propia"

    def guion(self, system: str, user: str) -> dict:
        raise RuntimeError("el proveedor 'archivo' no escribe guiones")

    def tts(self, texto: str, voz: str) -> bytes:
        raise RuntimeError("el proveedor 'archivo' no sintetiza: sube la "
                           "grabacion del clip (PUT .../narracion/{cid}/audio)")


# ── catalogo y fabrica ───────────────────────────────────────────────────────

def catalogo(cfg) -> list[dict]:
    """Los cuatro proveedores con `disponible`, `motivo` y sus voces. Es lo
    que la UI enseña; no instancia clientes (ver `fabricar`)."""
    permitidos = set(cfg.tts_proveedores)
    out = []

    disponible = cfg.gcp_key_path.is_file() and _instalado("google.genai")
    out.append({
        "id": "vertex", "nombre": "Gemini TTS (Vertex AI)",
        "disponible": disponible and "vertex" in permitidos,
        "motivo": None if disponible else "falta la service account de Vertex",
        "escribe_guion": bool(disponible and "vertex" in permitidos
                              and cfg.tts_guionista == "vertex"),
        "offline": False,
        "voz_defecto": cfg.tts_voice_vertex,
        "voces": [{"id": v, "nombre": n} for v, n in VERTEX_VOCES],
    })

    falta = [m for m in ("edge_tts", "miniaudio") if not _instalado(m)]
    out.append({
        "id": "edge", "nombre": "Edge (edge-tts, gratis)",
        "disponible": not falta and "edge" in permitidos,
        "motivo": None if not falta else f"falta instalar {', '.join(falta)}",
        "escribe_guion": False, "offline": False,
        "voz_defecto": cfg.tts_voice_edge,
        "voces": [{"id": v, "nombre": n} for v, n in EDGE_VOCES],
    })

    voces_piper: list[tuple[str, str]] = []
    motivo = None
    if not _instalado("piper") or not _instalado("miniaudio"):
        motivo = "falta instalar piper-tts"
    else:
        try:
            voces_piper = PiperNarrador(cfg.piper_voices_dir).voces()
        except RuntimeError as e:
            motivo = str(e)
    out.append({
        "id": "piper", "nombre": "Piper (offline)",
        "disponible": motivo is None and "piper" in permitidos,
        "motivo": motivo,
        "escribe_guion": False, "offline": True,
        "voz_defecto": (cfg.tts_voice_piper
                        if any(v == cfg.tts_voice_piper for v, _ in voces_piper)
                        else (voces_piper[0][0] if voces_piper else None)),
        "voces": [{"id": v, "nombre": n} for v, n in voces_piper],
    })

    out.append({
        "id": "archivo", "nombre": "Grabacion propia",
        "disponible": True, "motivo": None,
        "escribe_guion": False, "offline": True,
        "voz_defecto": "propia",
        "voces": [{"id": "propia", "nombre": "la voz del dueno"}],
    })
    return out


def disponibles(cfg) -> list[dict]:
    return [p for p in catalogo(cfg) if p["disponible"]]


def proveedor_defecto(cfg) -> str | None:
    """El configurado si esta disponible; si no, el primero que sintetiza."""
    cat = {p["id"]: p for p in catalogo(cfg)}
    if cfg.tts_provider in cat and cat[cfg.tts_provider]["disponible"]:
        return cfg.tts_provider
    for pid in ("edge", "piper", "vertex"):
        if cat[pid]["disponible"]:
            return pid
    return None


def voz_defecto(cfg, proveedor: str) -> str:
    for p in catalogo(cfg):
        if p["id"] == proveedor:
            return p["voz_defecto"] or ""
    return ""


def fabricar(cfg, proveedor: str) -> Narrador:
    if proveedor == "vertex":
        return VertexNarrador(cfg.gcp_key_path, cfg.gcp_location,
                              cfg.gemini_model_deep, cfg.gemini_model_tts)
    if proveedor == "edge":
        return EdgeNarrador()
    if proveedor == "piper":
        return PiperNarrador(cfg.piper_voices_dir)
    if proveedor == "archivo":
        return ArchivoNarrador()
    raise ValueError(f"proveedor de voz desconocido: {proveedor}")


def hay_ffmpeg() -> bool:
    return shutil.which("ffmpeg") is not None


def entorno_tts() -> dict:
    """Para /api/health y los tests: que hay instalado."""
    return {m: _instalado(m) for m in ("edge_tts", "piper", "miniaudio",
                                       "google.genai")} | {
        "ffmpeg_host": hay_ffmpeg(),
        "piper_voices_dir": os.environ.get("MS_PIPER_VOICES_DIR"),
    }
