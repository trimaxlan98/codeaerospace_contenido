#!/usr/bin/env python3
"""Guiones de audio para los cursos: Gemini escribe, Gemini TTS narra.

CLI sobre la logica compartida de `app.narracion` (la misma que usa el boton
"Generar narracion" de la web). Ejecucion aparte del render (no toca la cola
de jobs ni los videos):

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
Si el audio no cabe en el video se ataca en tres niveles: se comprimen los
silencios entre secciones, se piden hasta MAX_INTENTOS_GUION guiones mas
cortos (conservando el que mejor encaja, no el ultimo) y, si aun asi sobra,
el mux.sh del zip lo acelera con atempo al montar. La voz nunca se corta.

Reusa la service account del asistente IA (/etc/manimstudio/gcp-key.json,
feature-flag: sin credenciales el comando falla con un mensaje claro).
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

BACKEND = Path(__file__).resolve().parent.parent / "backend"
sys.path.insert(0, str(BACKEND))

from app.narracion import (TOLERANCIA_AUDIO,  # noqa: E402
                           duracion_mp4, etiqueta_clip, generar_clip,
                           hash_guion, sintetizar, slugify)
from app.tts import narrador_desde_entorno  # noqa: E402
from app.projects import compose_script  # noqa: E402

ENV_FILE = Path("/etc/manimstudio/env")
DEFAULT_DB = "/var/www/codeaerospace_contenido/studio/backend/manimstudio.db"
DEFAULT_KEY = "/etc/manimstudio/gcp-key.json"


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


RE_FILA_MD = re.compile(r"^\| (\d+)–\d+ s \| .*? \| (.*) \|$")


def cargar_secciones(destino: Path, etiqueta: str) -> list[dict] | None:
    """Secciones para --solo-audio, de mejor a peor fuente: secciones.json
    (tiempos exactos) > tabla del .md (tiempos re-parseados) > .txt (sin
    tiempos: narracion de corrido)."""
    sj = destino / f"{etiqueta}.secciones.json"
    if sj.is_file():
        return json.loads(sj.read_text())
    md = destino / f"{etiqueta}.md"
    if md.is_file():
        secciones = []
        for line in md.read_text().splitlines():
            m = RE_FILA_MD.match(line)
            if m:
                secciones.append({"t_inicio": float(m.group(1)),
                                  "texto": m.group(2).replace("\\|", "|")})
        if len(secciones) > 1:
            return secciones
    txt = destino / f"{etiqueta}.txt"
    if txt.is_file():
        return [{"texto": p.strip()} for p in txt.read_text().split("\n\n")
                if p.strip()]
    return None


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
    ap.add_argument("--voz", default=None,
                    help="voz del proveedor (defecto: la suya)")
    ap.add_argument("--proveedor", default=None,
                    choices=["vertex", "edge", "piper"],
                    help="quien pone la voz (defecto: MS_TTS_PROVIDER o el "
                    "primero disponible). Solo vertex escribe el guion; con "
                    "otro se usa el .secciones.json existente")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--solo-guion", action="store_true")
    ap.add_argument("--solo-audio", action="store_true",
                    help="re-sintetiza desde los .txt existentes")
    ap.add_argument("--salida", help="directorio base (defecto: guiones/ "
                    "junto al workspace)")
    args = ap.parse_args()

    cargar_env()
    db_path = os.environ.get("MS_DB_PATH", DEFAULT_DB)
    try:
        vertex, voz = narrador_desde_entorno(args.proveedor, args.voz)
    except RuntimeError as e:
        sys.exit(str(e))
    print(f"voz: {vertex.id} · {voz}")

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

    curso = {"name": proyecto["name"], "description": proyecto["description"],
             "total_clips": len(clips)}
    resumen = []

    for clip in clips:
        if clip["position"] not in seleccion:
            continue
        etiqueta = etiqueta_clip(clip["position"], clip["title"])
        md_path = destino / f"{etiqueta}.md"
        txt_path = destino / f"{etiqueta}.txt"
        wav_path = destino / f"{etiqueta}.wav"

        job = jobs.get(clip["job_id"]) or {}
        video_s = None
        if job.get("status") == "done" and job.get("video_path"):
            video_s = duracion_mp4(Path(job["video_path"]))

        compuesto = compose_script(proyecto["style_block"], clip["script"] or "")
        h = hash_guion(compuesto, clip["scene"] or "", video_s, voz)
        previo = estado.get(clip["id"], {})

        if args.solo_audio:
            secciones = cargar_secciones(destino, etiqueta)
            if not secciones:
                print(f"[{etiqueta}] sin guion previo, saltado (genera el "
                      "guion primero)")
                continue
            con_t = all("t_inicio" in s for s in secciones)
            print(f"[{etiqueta}] re-sintetizando audio "
                  + ("alineado a los tiempos del guion…" if con_t
                     else "de corrido (sin tiempos)…"))
            audio_s = sintetizar(vertex, secciones, voz, wav_path,
                                 video_s and video_s * TOLERANCIA_AUDIO)
            previo.update({"audio_s": round(audio_s, 1), "voz": voz,
                           "generado": time.time()})
            estado[clip["id"]] = previo
            estado_path.write_text(json.dumps(estado, indent=2))
            resumen.append((etiqueta, video_s, audio_s))
            continue

        if not args.force and previo.get("hash") == h and md_path.is_file() \
                and (args.solo_guion or wav_path.is_file()):
            print(f"[{etiqueta}] al día (hash sin cambios), saltado")
            continue

        # Un proveedor que no escribe guiones usa el .secciones.json que haya
        secciones = None
        if vertex.id != "vertex":
            secciones = cargar_secciones(destino, etiqueta)
            if not secciones:
                print(f"[{etiqueta}] {vertex.id} no escribe guiones y no hay "
                      ".secciones.json: escribelo (app > Guion y voz) o usa "
                      "--proveedor vertex")
                continue
        entry = generar_clip(vertex, curso, clip, compuesto, video_s, voz,
                             destino, etiqueta, solo_guion=args.solo_guion,
                             secciones=secciones)
        estado[clip["id"]] = entry
        estado_path.write_text(json.dumps(estado, indent=2))
        resumen.append((etiqueta, video_s, entry["audio_s"]))

    if resumen:
        print("\nResumen:")
        for etiqueta, video_s, audio_s in resumen:
            v = f"{video_s:6.1f} s" if video_s else "   sin render"
            a = f"{audio_s:6.1f} s" if audio_s else "   sin audio"
            ok = ""
            if video_s and audio_s:
                ok = ("  ✓" if audio_s <= video_s * TOLERANCIA_AUDIO
                      else "  ⚠ largo")
            print(f"  {etiqueta:44s} video {v}  audio {a}{ok}")
    print(f"\nSalida: {destino}")


if __name__ == "__main__":
    main()
