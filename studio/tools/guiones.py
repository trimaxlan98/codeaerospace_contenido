#!/usr/bin/env python3
"""Guiones de audio para los cursos: Gemini escribe, Gemini TTS narra.

Ejecucion aparte del render (no toca la cola de jobs ni los videos):

    studio/backend/venv/bin/python studio/tools/guiones.py "Fractales"
    ... --clips 1,3-5      solo esos clips (posiciones 1-based)
    ... --solo-guion       texto sin sintetizar audio
    ... --solo-audio       re-sintetiza desde los .txt ya generados
    ... --voz Kore         voz prebuilt de Gemini TTS (defecto: Charon)
    ... --force            regenera aunque el hash no haya cambiado

Por cada clip del proyecto produce en guiones/<slug-proyecto>/:
  NN-<slug>.md   guion con secciones cronometradas y la narracion
  NN-<slug>.txt  narracion plana (entrada del TTS)
  NN-<slug>.wav  voz sintetizada (PCM 24 kHz mono)
  estado.json    hashes y duraciones para detectar clips desactualizados

El guion se ajusta a la duracion real del video renderizado (leida del
atomo mvhd del mp4, sin ffprobe): ~2.2 palabras/s con margen del 10 %.
Si el audio sintetizado excede la duracion del video se reintenta una
vez con un presupuesto de palabras mas corto; si aun asi no cabe, se
conserva y se avisa (el montaje puede estirar el video o cortar pausas).

Reusa la service account del asistente IA (/etc/manimstudio/gcp-key.json,
feature-flag: sin credenciales el comando falla con un mensaje claro) y
la misma logica de composicion estilo+script del backend.
"""

import argparse
import hashlib
import json
import os
import re
import struct
import sys
import time
import unicodedata
import wave
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.projects import compose_script  # noqa: E402

ENV_FILE = Path("/etc/manimstudio/env")
DEFAULT_DB = "/var/www/codeaerospace_contenido/studio/backend/manimstudio.db"
DEFAULT_KEY = "/etc/manimstudio/gcp-key.json"

MODEL_GUION = os.environ.get("MS_GEMINI_MODEL_DEEP", "gemini-2.5-pro")
MODEL_TTS = os.environ.get("MS_GEMINI_MODEL_TTS", "gemini-2.5-flash-preview-tts")
LOCATION = os.environ.get("MS_GCP_LOCATION", "us-central1")

# Narracion en español pausada: ~2.2 palabras/s, y solo se apunta al 90 %
# de la duracion del video para dejar aire entre secciones.
PALABRAS_POR_SEGUNDO = 2.2
MARGEN = 0.9
TTS_RATE = 24_000  # PCM mono 16-bit que devuelve Gemini TTS
TTS_MAX_CHARS = 3_000  # por llamada; las secciones se agrupan hasta este tope
PAUSA_ENTRE_TROZOS_S = 0.35

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


def cargar_env() -> None:
    """Completa el entorno con /etc/manimstudio/env sin pisar lo ya definido."""
    if not ENV_FILE.is_file():
        return
    for line in ENV_FILE.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k, v)


def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
    return slug or "clip"


def duracion_mp4(path: Path) -> float | None:
    """Duracion en segundos leyendo el atomo moov/mvhd (sin ffprobe)."""
    try:
        data = path.read_bytes()
    except OSError:
        return None
    pos, end = 0, len(data)
    while pos + 8 <= end:  # nivel raiz: buscar moov
        size, kind = struct.unpack(">I4s", data[pos:pos + 8])
        if size < 8:
            return None
        if kind == b"moov":
            inner, inner_end = pos + 8, pos + size
            while inner + 8 <= min(inner_end, end):
                isize, ikind = struct.unpack(">I4s", data[inner:inner + 8])
                if isize < 8:
                    return None
                if ikind == b"mvhd":
                    body = data[inner + 8:inner + isize]
                    version = body[0]
                    if version == 1:
                        timescale, duration = struct.unpack(">IQ", body[20:32])
                    else:
                        timescale, duration = struct.unpack(">II", body[12:20])
                    return duration / timescale if timescale else None
                inner += isize
            return None
        pos += size
    return None


def hash_guion(script_compuesto: str, scene: str, video_s: float | None,
               voz: str) -> str:
    """Detecta guiones desactualizados: cambia el script, la escena, la
    duracion del render (redondeada al segundo) o la voz -> stale."""
    h = hashlib.sha256(script_compuesto.encode())
    h.update(f"\n# scene: {scene}".encode())
    h.update(f"\n# video_s: {round(video_s) if video_s else 0}".encode())
    h.update(f"\n# voz: {voz}".encode())
    return h.hexdigest()


# ── Vertex AI ────────────────────────────────────────────────────────────────

class Vertex:
    def __init__(self, key_path: Path) -> None:
        if not key_path.is_file():
            sys.exit(f"No existe la service account {key_path}: el generador "
                     "de guiones necesita el mismo acceso a Vertex AI que el "
                     "asistente IA del estudio.")
        from google import genai
        from google.oauth2 import service_account

        self.types = __import__("google.genai.types", fromlist=["types"])
        project = json.loads(key_path.read_text())["project_id"]
        creds = service_account.Credentials.from_service_account_file(
            str(key_path),
            scopes=["https://www.googleapis.com/auth/cloud-platform"])
        self.client = genai.Client(vertexai=True, project=project,
                                   location=LOCATION, credentials=creds)

    def guion(self, system: str, user: str) -> dict:
        t = self.types
        resp = self.client.models.generate_content(
            model=MODEL_GUION,
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
                    model=MODEL_TTS,
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
            except Exception as e:
                if intento == 3:
                    raise
                print(f"    TTS fallo ({type(e).__name__}), reintento {intento}…")
                time.sleep(5 * intento)
        raise RuntimeError("unreachable")


def prompt_guion(curso: dict, clip: dict, script_compuesto: str,
                 video_s: float | None, max_palabras: int) -> tuple[str, str]:
    dur = f"{video_s:.1f} segundos" if video_s else "desconocida (sin render)"
    system = (
        "Eres guionista de divulgación científica en español (estilo "
        "3Blue1Brown: cercano, preciso, sin grandilocuencia). Recibes el "
        "script de Manim de un clip de video ya renderizado: los comentarios, "
        "los textos en pantalla y los run_time/wait te dicen qué se ve y "
        "cuándo. Escribe la narración en off que acompaña al video.\n"
        "Reglas:\n"
        "- Divide la narración en secciones alineadas con los momentos "
        "visuales del script; t_inicio/t_fin en segundos aproximados según "
        "los run_time y wait acumulados.\n"
        f"- La narración completa NO debe superar {max_palabras} palabras "
        "(el video dura " + dur + " y la voz debe caber con aire).\n"
        "- No leas en voz alta los textos que ya aparecen en pantalla: "
        "complétalos o coméntalos, no los repitas literalmente.\n"
        "- Frases cortas, aptas para texto-a-voz: sin fórmulas en notación "
        "matemática (di «zeta al cuadrado más c», no «z^2+c»), sin "
        "paréntesis largos ni siglas sin desarrollar.\n"
        "- 'momento' es una etiqueta breve de lo que se ve en pantalla."
    )
    user = (
        f"CURSO: {curso['name']}\n"
        f"DESCRIPCION DEL CURSO: {curso['description']}\n"
        f"CLIP {clip['position'] + 1} de {curso['total_clips']}: {clip['title']}\n"
        f"ESCENA: {clip['scene']}\n"
        f"DURACION REAL DEL VIDEO: {dur}\n\n"
        f"SCRIPT MANIM (estilo del curso + clip):\n{script_compuesto}"
    )
    return system, user


def render_md(curso: dict, clip: dict, secciones: list[dict], narracion: str,
              video_s: float | None, voz: str) -> str:
    lineas = [
        f"# {clip['title']}",
        "",
        f"- **Curso:** {curso['name']}",
        f"- **Escena:** `{clip['scene']}`",
        f"- **Duración del video:** "
        + (f"{video_s:.1f} s" if video_s else "sin render"),
        f"- **Voz:** {voz} ({MODEL_TTS})",
        f"- **Palabras:** {len(narracion.split())}",
        "",
        "## Guion por secciones",
        "",
        "| Tiempo | Momento visual | Narración |",
        "|---|---|---|",
    ]
    for s in secciones:
        texto = s["texto"].replace("|", "\\|").replace("\n", " ")
        momento = s["momento"].replace("|", "\\|")
        lineas.append(f"| {s['t_inicio']:.0f}–{s['t_fin']:.0f} s "
                      f"| {momento} | {texto} |")
    lineas += ["", "## Narración completa", "", narracion, ""]
    return "\n".join(lineas)


def sintetizar(vertex: Vertex, secciones: list[dict], voz: str,
               wav_path: Path) -> float:
    """TTS por trozos (secciones agrupadas hasta TTS_MAX_CHARS) con una
    pausa breve entre trozos. Devuelve la duracion del audio en segundos."""
    trozos: list[str] = []
    actual = ""
    for s in secciones:
        candidato = (actual + "\n\n" + s["texto"]).strip()
        if actual and len(candidato) > TTS_MAX_CHARS:
            trozos.append(actual)
            actual = s["texto"]
        else:
            actual = candidato
    if actual:
        trozos.append(actual)

    pausa = b"\x00\x00" * int(TTS_RATE * PAUSA_ENTRE_TROZOS_S)
    pcm = b""
    for i, trozo in enumerate(trozos):
        if i:
            pcm += pausa
        pcm += vertex.tts(trozo, voz)

    with wave.open(str(wav_path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(TTS_RATE)
        w.writeframes(pcm)
    return len(pcm) / 2 / TTS_RATE


def parse_clips_arg(spec: str, total: int) -> set[int]:
    """'1,3-5' -> posiciones 0-based {0,2,3,4}."""
    out: set[int] = set()
    for parte in spec.split(","):
        parte = parte.strip()
        if "-" in parte:
            a, b = parte.split("-", 1)
            out.update(range(int(a) - 1, int(b)))
        elif parte:
            out.add(int(parte) - 1)
    return {p for p in out if 0 <= p < total}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("proyecto", help="id o parte del nombre del proyecto")
    ap.add_argument("--clips", help="posiciones 1-based, ej. 1,3-5")
    ap.add_argument("--voz", default="Charon")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--solo-guion", action="store_true")
    ap.add_argument("--solo-audio", action="store_true",
                    help="re-sintetiza desde los .txt existentes")
    ap.add_argument("--salida", help="directorio base (defecto: guiones/ "
                    "junto al workspace)")
    args = ap.parse_args()

    cargar_env()
    db_path = os.environ.get("MS_DB_PATH", DEFAULT_DB)
    key_path = Path(os.environ.get("MS_GCP_KEY_PATH", DEFAULT_KEY))

    import sqlite3
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row

    proyectos = [dict(r) for r in db.execute("SELECT * FROM projects")]
    q = args.proyecto.lower()
    match = [p for p in proyectos
             if p["id"] == args.proyecto or q in p["name"].lower()]
    if len(match) != 1:
        nombres = ", ".join(f"{p['name']} ({p['id']})" for p in proyectos)
        sys.exit(f"Proyecto '{args.proyecto}' "
                 + ("ambiguo" if match else "no encontrado")
                 + f". Disponibles: {nombres}")
    proyecto = match[0]

    clips = [dict(r) for r in db.execute(
        "SELECT * FROM clips WHERE project_id=? ORDER BY position",
        (proyecto["id"],))]
    jobs = {c["job_id"]: dict(db.execute(
        "SELECT * FROM jobs WHERE id=?", (c["job_id"],)).fetchone() or {})
        for c in clips if c["job_id"]}

    seleccion = (parse_clips_arg(args.clips, len(clips))
                 if args.clips else set(range(len(clips))))

    base = Path(args.salida) if args.salida else (
        Path(os.environ.get("MS_WORKSPACE",
                            str(BACKEND.parent.parent))) / "guiones")
    destino = base / slugify(proyecto["name"])
    destino.mkdir(parents=True, exist_ok=True)
    estado_path = destino / "estado.json"
    estado = (json.loads(estado_path.read_text())
              if estado_path.is_file() else {})

    vertex = Vertex(key_path)
    curso = {"name": proyecto["name"], "description": proyecto["description"],
             "total_clips": len(clips)}
    resumen = []

    for clip in clips:
        if clip["position"] not in seleccion:
            continue
        etiqueta = f"{clip['position'] + 1:02d}-{slugify(clip['title'])}"
        md_path = destino / f"{etiqueta}.md"
        txt_path = destino / f"{etiqueta}.txt"
        wav_path = destino / f"{etiqueta}.wav"

        job = jobs.get(clip["job_id"]) or {}
        video_s = None
        if job.get("status") == "done" and job.get("video_path"):
            video_s = duracion_mp4(Path(job["video_path"]))

        compuesto = compose_script(proyecto["style_block"], clip["script"] or "")
        h = hash_guion(compuesto, clip["scene"] or "", video_s, args.voz)
        previo = estado.get(clip["id"], {})

        if args.solo_audio:
            if not txt_path.is_file():
                print(f"[{etiqueta}] sin .txt previo, saltado (genera el "
                      "guion primero)")
                continue
            print(f"[{etiqueta}] re-sintetizando audio desde {txt_path.name}…")
            secciones = [{"texto": p} for p in
                         txt_path.read_text().split("\n\n") if p.strip()]
            audio_s = sintetizar(vertex, secciones, args.voz, wav_path)
            previo.update({"audio_s": round(audio_s, 1), "voz": args.voz,
                           "generado": time.time()})
            estado[clip["id"]] = previo
            estado_path.write_text(json.dumps(estado, indent=2))
            resumen.append((etiqueta, video_s, audio_s))
            continue

        if not args.force and previo.get("hash") == h and md_path.is_file() \
                and (args.solo_guion or wav_path.is_file()):
            print(f"[{etiqueta}] al día (hash sin cambios), saltado")
            continue

        max_palabras = (int(video_s * PALABRAS_POR_SEGUNDO * MARGEN)
                        if video_s else 160)
        print(f"[{etiqueta}] guion… (video "
              + (f"{video_s:.0f} s, tope {max_palabras} palabras)"
                 if video_s else "sin render, tope 160 palabras)"))
        system, user = prompt_guion(curso, clip, compuesto, video_s,
                                    max_palabras)
        data = vertex.guion(system, user)
        secciones = data["secciones"]
        narracion = "\n\n".join(s["texto"].strip() for s in secciones)

        audio_s = None
        if not args.solo_guion:
            print(f"[{etiqueta}] narrando con {args.voz}…")
            audio_s = sintetizar(vertex, secciones, args.voz, wav_path)
            if video_s and audio_s > video_s * 1.05:
                print(f"[{etiqueta}] audio {audio_s:.0f} s > video "
                      f"{video_s:.0f} s: reintento con guion más corto…")
                system, user = prompt_guion(
                    curso, clip, compuesto, video_s,
                    int(max_palabras * video_s / audio_s * 0.95))
                data = vertex.guion(system, user)
                secciones = data["secciones"]
                narracion = "\n\n".join(s["texto"].strip() for s in secciones)
                audio_s = sintetizar(vertex, secciones, args.voz, wav_path)
                if audio_s > video_s * 1.05:
                    print(f"[{etiqueta}] AVISO: el audio ({audio_s:.0f} s) "
                          "sigue más largo que el video; revisar en montaje.")

        md_path.write_text(render_md(curso, clip, secciones, narracion,
                                     video_s, args.voz))
        txt_path.write_text(narracion + "\n")
        estado[clip["id"]] = {
            "hash": h, "etiqueta": etiqueta, "voz": args.voz,
            "video_s": round(video_s, 1) if video_s else None,
            "audio_s": round(audio_s, 1) if audio_s else None,
            "palabras": len(narracion.split()),
            "generado": time.time(),
        }
        estado_path.write_text(json.dumps(estado, indent=2))
        resumen.append((etiqueta, video_s, audio_s))

    if resumen:
        print("\nResumen:")
        for etiqueta, video_s, audio_s in resumen:
            v = f"{video_s:6.1f} s" if video_s else "   sin render"
            a = f"{audio_s:6.1f} s" if audio_s else "   sin audio"
            ok = ""
            if video_s and audio_s:
                ok = "  ✓" if audio_s <= video_s * 1.05 else "  ⚠ largo"
            print(f"  {etiqueta:44s} video {v}  audio {a}{ok}")
    print(f"\nSalida: {destino}")


if __name__ == "__main__":
    main()
