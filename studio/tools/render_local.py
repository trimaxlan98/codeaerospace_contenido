#!/usr/bin/env python3
"""Renderiza clips de un curso versionado en Docker, igual que produccion.

Herramienta de validacion local: compone el script exactamente como lo hace
el backend (style_block + clip + identidad CO.DE Academy anexada) y lo
renderiza en la imagen `codeaerospace_contenido-manim`, sin pasar por la cola
del Studio. Sirve para revisar un clip frame a frame ANTES de subirlo.

    studio/backend/venv/bin/python studio/tools/render_local.py \
        studio/content/cursos/<slug> --clip 3
    ... --clip 3 --clip 5      varios clips (por numero, 1-based)
    ... --todos                los 8 clips del curso
    ... --calidad qh           calidad del render (defecto: ql)
    ... --frames 8             frames PNG por clip para revision visual
    ... --solo-componer        escribe el scene.py y sale (sin Docker)

Deja todo en `render_jobs/validacion/<slug>/NN-<escena>/`:

    scene.py              el script compuesto, tal cual lo ve manim
    video.mp4             el render
    frames/NN.png         frames equiespaciados para la revision visual

El repo se monta READ-ONLY en el contenedor (como en produccion); lo unico
escribible es el directorio de salida del clip. La revision visual de los
frames es obligatoria antes de dar un clip por bueno: la regla dura del
proyecto es que NADA quede encimado.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "backend"))

from app import branding  # noqa: E402
from app.projects import compose_script  # noqa: E402

IMAGEN = "codeaerospace_contenido-manim"
SALIDA = REPO / "render_jobs" / "validacion"

# Duraciones que el pipeline da por buenas (ver PLAN.md): un clip mas corto
# no alcanza a contar nada y uno mas largo se cae del formato.
DURACION_MIN = 28.0
DURACION_MAX = 45.0

# Subdirectorio que manim usa dentro de --media_dir segun la calidad.
RESOLUCIONES = {"ql": "480p15", "qm": "720p30", "qh": "1080p60",
                "qk": "2160p60"}


def cargar_clips(curso_dir: Path) -> tuple[str, list[dict]]:
    """(style_block, clips) de un curso versionado. Falla claro si falta algo."""
    manifest = curso_dir / "curso.json"
    if not manifest.is_file():
        sys.exit(f"no existe {manifest}")
    curso = json.loads(manifest.read_text())

    style_path = curso_dir / curso.get("style_block", "style_block.py")
    style = style_path.read_text() if style_path.is_file() else ""

    clips = []
    for i, spec in enumerate(curso["clips"], start=1):
        ruta = curso_dir / spec["file"]
        if not ruta.is_file():
            sys.exit(f"clip {i}: no existe {ruta}")
        clips.append({"n": i, "escena": spec["scene"],
                      "titulo": spec.get("title") or ruta.stem,
                      "script": ruta.read_text()})
    return style, clips


def componer(style: str, script: str) -> str:
    """El script tal cual lo ejecuta el runner: style + clip + identidad."""
    return branding.aplicar(compose_script(style, script))


def duracion(video: Path) -> float | None:
    """Segundos de un mp4 segun ffprobe, o None si no se puede leer."""
    try:
        salida = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
            capture_output=True, text=True, check=True).stdout.strip()
        return float(salida)
    except (subprocess.CalledProcessError, ValueError, FileNotFoundError):
        return None


def extraer_frames(video: Path, destino: Path, cuantos: int) -> int:
    """Frames equiespaciados del video, para la revision visual."""
    total = duracion(video)
    if not total or cuantos < 1:
        return 0
    destino.mkdir(parents=True, exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()
    # Se evitan el primer y el ultimo instante: suelen ser fundidos a negro.
    for i in range(cuantos):
        t = total * (i + 0.5) / cuantos
        subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.3f}",
             "-i", str(video), "-frames:v", "1", "-y",
             str(destino / f"{i + 1:02d}.png")], check=False)
    return len(list(destino.glob("*.png")))


def renderizar(clip: dict, style: str, slug: str, calidad: str,
               frames: int, solo_componer: bool) -> bool:
    """Compone, renderiza y extrae frames de un clip. True si salio bien."""
    trabajo = SALIDA / slug / f"{clip['n']:02d}-{clip['escena']}"
    trabajo.mkdir(parents=True, exist_ok=True)
    scene_py = trabajo / "scene.py"
    scene_py.write_text(componer(style, clip["script"]))

    print(f"\n[{clip['n']}] {clip['titulo']}  ({clip['escena']})")
    print(f"    compuesto: {scene_py.relative_to(REPO)}")
    if solo_componer:
        return True

    # El repo va read-only (como en produccion); solo el dir del clip es rw.
    #
    # OJO: manim lee el script por /media/scene.py, NO por
    # /workspace/render_jobs/... Desde que `render_jobs` y `exports` son
    # ENLACES SIMBOLICOS al segundo disco (migracion 2026-08-28), la ruta
    # dentro de /workspace es un enlace COLGANDO: el destino no esta
    # montado y manim moria con "scene.py not found" en los cuatro clips.
    # El propio dir de trabajo ya va montado en /media, asi que se apunta
    # ahi y el enlace deja de importar.
    cmd = ["docker", "run", "--rm", "--network", "none",
           "--user", f"{os.getuid()}:{os.getgid()}",
           "-v", f"{REPO}:/workspace:ro", "-v", f"{trabajo}:/media",
           IMAGEN, "manim", "render", f"-{calidad}", "--disable_caching",
           "--media_dir", "/media",
           "/media/scene.py", clip["escena"]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cola = "\n".join(proc.stderr.strip().splitlines()[-15:])
        print(f"    FALLO el render (exit {proc.returncode}):\n{cola}")
        return False

    origen = (trabajo / "videos" / "scene" / RESOLUCIONES[calidad]
              / f"{clip['escena']}.mp4")
    if not origen.is_file():
        print(f"    render sin video en {origen}")
        return False
    video = trabajo / "video.mp4"
    video.write_bytes(origen.read_bytes())

    segs = duracion(video)
    if segs is None:
        print(f"    video: {video.relative_to(REPO)}  (duracion ilegible)")
    else:
        if segs < DURACION_MIN:
            aviso = f"  <-- CORTO (minimo {DURACION_MIN:.0f} s)"
        elif segs > DURACION_MAX:
            aviso = f"  <-- LARGO (tope duro {DURACION_MAX:.0f} s)"
        else:
            aviso = ""
        print(f"    video: {video.relative_to(REPO)}  {segs:.1f} s{aviso}")

    if frames:
        n = extraer_frames(video, trabajo / "frames", frames)
        print(f"    frames: {n} en {(trabajo / 'frames').relative_to(REPO)}"
              "  (revisalos: nada encimado)")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("curso", type=Path, help="studio/content/cursos/<slug>")
    p.add_argument("--clip", type=int, action="append", default=[],
                   help="numero de clip (1-based); repetible")
    p.add_argument("--todos", action="store_true", help="todos los clips")
    p.add_argument("--calidad", default="ql", choices=sorted(RESOLUCIONES))
    p.add_argument("--frames", type=int, default=6,
                   help="frames PNG por clip (0 para ninguno)")
    p.add_argument("--solo-componer", action="store_true",
                   help="escribe scene.py y sale, sin renderizar")
    args = p.parse_args()

    curso_dir = args.curso if args.curso.is_absolute() else REPO / args.curso
    style, clips = cargar_clips(curso_dir)

    if args.todos:
        elegidos = clips
    elif args.clip:
        por_n = {c["n"]: c for c in clips}
        faltan = [n for n in args.clip if n not in por_n]
        if faltan:
            sys.exit(f"el curso no tiene clip(s) {faltan} "
                     f"(hay {len(clips)})")
        elegidos = [por_n[n] for n in sorted(set(args.clip))]
    else:
        sys.exit("elige --clip N (repetible) o --todos")

    slug = curso_dir.name
    print(f"curso: {slug}  ({len(elegidos)} clip(s), calidad {args.calidad})")
    fallos = [c["n"] for c in elegidos
              if not renderizar(c, style, slug, args.calidad, args.frames,
                                args.solo_componer)]
    if fallos:
        print(f"\nclips con fallo: {fallos}")
        return 1
    print("\nlisto. Revision visual de los frames antes de subir_curso.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
