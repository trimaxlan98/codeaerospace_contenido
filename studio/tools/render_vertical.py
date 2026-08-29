#!/usr/bin/env python3
"""Renderiza las piezas de un CURSO VERTICAL (9:16) para redes.

Tercer hermano de `render_local.py` (cursos 16:9) y `render_promo.py`
(promos de 8-15 s en bucle). Un curso vertical es la mezcla de los dos:

  - el lienzo es el 9:16 REAL de `promo.formato()`, no un 16:9 con bandas;
  - las piezas duran 30-45 s como un clip de curso, no 12 como un promo;
  - **no lleva subtitulos**: la imagen enseña, y el audio (voz alineada a
    mano + cama de SFX) se pega despues con `unir_vertical.py`;
  - se renderiza pieza a pieza y se unen al final, que es lo que permite
    rehacer una sola sin tocar las demas.

    studio/backend/venv/bin/python studio/tools/render_vertical.py \
        studio/content/verticales/<slug>
    ... --clip 3 --clip 5        por numero (1-based sobre `piezas`)
    ... --todos                  todas las piezas del curso
    ... --calidad qh             ql (defecto, lado corto 540) | qm | qh
    ... --frames 10              frames PNG equiespaciados para la revision
    ... --guias                  dibuja la zona que la app NO tapa
    ... --solo-componer          escribe el scene.py y sale (sin Docker)

Deja todo en `render_jobs/verticales/<slug>/<pieza>/`:

    scene.py          el script compuesto, tal cual lo ve manim
    video.mp4         el render
    final.png         el ULTIMO frame real (el empalme con la pieza siguiente)
    frames/NN.png     frames equiespaciados

El repo se monta READ-ONLY en el contenedor, igual que en produccion.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "backend"))

from app import branding  # noqa: E402
from app.projects import compose_script  # noqa: E402

IMAGEN = "codeaerospace_contenido-manim"
SALIDA = REPO / "render_jobs" / "verticales"
CALIDADES = ("ql", "qm", "qh")
FORMATOS = ("vertical", "horizontal", "cuadrado")

# Rango por defecto de una pieza de curso. Las piezas de marca (intro y
# cierre) declaran `"tipo": "marca"` y quedan fuera del rango.
DURACION_MIN = 30.0
DURACION_MAX = 45.0
COLA_FINAL = 0.35        # ver render_promo: el ultimo frame no sale con -ss


def cargar_curso(curso_dir: Path) -> dict:
    """Lee curso.json y el clip.json de cada pieza. Falla claro si algo falta."""
    manifest = curso_dir / "curso.json"
    if not manifest.is_file():
        sys.exit(f"no existe {manifest}")
    curso = json.loads(manifest.read_text())
    if not curso.get("piezas"):
        sys.exit(f"{manifest}: falta la lista 'piezas'")

    estilo_comun = curso_dir / curso.get("style_block", "style_block.py")
    if not estilo_comun.is_file():
        sys.exit(f"no existe {estilo_comun}")
    estilo_comun = estilo_comun.read_text()

    piezas = []
    for i, spec in enumerate(curso["piezas"], start=1):
        pdir = curso_dir / spec["dir"]
        cjson = pdir / "clip.json"
        if not cjson.is_file():
            sys.exit(f"pieza {i}: no existe {cjson}")
        clip = json.loads(cjson.read_text())
        for campo in ("name", "scene", "file"):
            if not clip.get(campo):
                sys.exit(f"{cjson}: falta '{campo}'")
        escena = pdir / clip["file"]
        if not escena.is_file():
            sys.exit(f"pieza {i}: no existe {escena}")
        propio = pdir / clip["style_block"] if clip.get("style_block") else None
        clip["_style"] = (propio.read_text() if propio and propio.is_file()
                          else estilo_comun)
        clip["_script"] = escena.read_text()
        clip["_dir"] = pdir
        clip["_n"] = i
        clip["_slug"] = pdir.name
        clip["_tipo"] = spec.get("tipo") or clip.get("tipo") or "clip"
        piezas.append(clip)
    curso["_piezas"] = piezas
    curso["_min"] = float(curso.get("duracion_min", DURACION_MIN))
    curso["_max"] = float(curso.get("duracion_max", DURACION_MAX))
    return curso


def ffprobe(video: Path, campos: str, stream: bool = False) -> str:
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", "v:0", "-show_entries", f"stream={campos}"]
    else:
        cmd += ["-show_entries", f"format={campos}"]
    cmd += ["-of", "csv=p=0", str(video)]
    return subprocess.run(cmd, capture_output=True, text=True,
                          check=True).stdout.strip()


def datos_video(video: Path) -> dict:
    dur = float(ffprobe(video, "duration"))
    ancho, alto, tasa = ffprobe(video, "width,height,r_frame_rate",
                                stream=True).split(",")
    num, _, den = tasa.partition("/")
    return {"dur": dur, "ancho": int(ancho), "alto": int(alto),
            "fps": float(num) / float(den or 1)}


def frame_final(video: Path, destino: Path):
    """El ULTIMO frame real: se decodifica la cola con -update 1 (un -ss al
    filo de la duracion sale con exito SIN escribir nada)."""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-sseof",
                    f"-{COLA_FINAL}", "-i", str(video), "-update", "1", "-y",
                    str(destino)], check=True)


def extraer_frames(video: Path, destino: Path, cuantos: int, dur: float) -> int:
    destino.mkdir(parents=True, exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()
    for i in range(cuantos):
        t = dur * (i + 0.5) / cuantos
        subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss",
                        f"{t:.4f}", "-i", str(video), "-frames:v", "1", "-y",
                        str(destino / f"{i + 1:02d}.png")], check=True)
    return len(list(destino.glob("*.png")))


def renderizar(clip: dict, curso: dict, slug: str, args) -> bool:
    nombre_dir = clip["_slug"]
    trabajo = SALIDA / slug / nombre_dir
    trabajo.mkdir(parents=True, exist_ok=True)
    # Manim escribe en videos/scene/<resolucion>/, asi que un render previo
    # en OTRA calidad deja su carpeta ahi. Sin borrarla, la busqueda del mp4
    # puede quedarse con el archivo viejo — y "1920p60" ordena antes que
    # "960p30", asi que un `ql` posterior a un `qh` devolvia el `qh`. Se
    # limpia antes de renderizar y ademas se elige por fecha.
    if (trabajo / "videos").exists():
        shutil.rmtree(trabajo / "videos")
    scene_py = trabajo / "scene.py"
    scene_py.write_text(branding.aplicar(
        compose_script(clip["_style"], clip["_script"])))

    print(f"\n[{clip['_n']:02d}] {clip['name']}  "
          f"[{args.formato} · {args.calidad}]")
    print(f"    compuesto: {scene_py.relative_to(REPO)}")
    if args.solo_componer:
        return True

    entorno = {"PROMO_FORMATO": args.formato, "PROMO_CALIDAD": args.calidad,
               "PROMO_GUIAS": "1" if args.guias else "0"}
    cmd = ["docker", "run", "--rm", "--network", "none",
           "--user", f"{os.getuid()}:{os.getgid()}"]
    for k, v in entorno.items():
        cmd += ["-e", f"{k}={v}"]
    cmd += ["-v", f"{REPO}:/workspace:ro", "-v", f"{trabajo}:/media",
            IMAGEN, "manim", "render", "-qh", "--disable_caching",
            "--media_dir", "/media",
            "/media/scene.py", clip["scene"]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cola = "\n".join(proc.stderr.strip().splitlines()[-18:])
        print(f"    FALLO el render (exit {proc.returncode}):\n{cola}")
        return False

    candidatos = sorted((trabajo / "videos").rglob(f"{clip['scene']}.mp4"),
                        key=lambda p: p.stat().st_mtime, reverse=True)
    if not candidatos:
        print(f"    render sin video en {trabajo / 'videos'}")
        return False
    video = trabajo / "video.mp4"
    video.write_bytes(candidatos[0].read_bytes())

    d = datos_video(video)
    print(f"    {d['ancho']}x{d['alto']} @ {d['fps']:.0f} fps · "
          f"{d['dur']:.2f} s")
    if d["alto"] <= d["ancho"] and args.formato == "vertical":
        print("    ERROR: el video NO es vertical — el mundo se quedo en "
              "16:9 (¿el style_block llama a promo.formato()?)")
        return False

    if clip["_tipo"] != "marca":
        if not (curso["_min"] <= d["dur"] <= curso["_max"]):
            print(f"    AVISO: {d['dur']:.2f} s fuera del rango "
                  f"{curso['_min']:.0f}-{curso['_max']:.0f} s")
    objetivo = clip.get("duracion_objetivo")
    if objetivo and abs(d["dur"] - float(objetivo)) > 0.5:
        print(f"    AVISO: el manifiesto dice {objetivo} s y el render dio "
              f"{d['dur']:.2f} s (la voz se alinea con el manifiesto: "
              "cuadralos antes de narrar)")

    frame_final(video, trabajo / "final.png")
    if args.frames:
        n = extraer_frames(video, trabajo / "frames", args.frames, d["dur"])
        print(f"    {n} frames en {(trabajo / 'frames').relative_to(REPO)}")
    return True


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("curso_dir", type=Path,
                   help="studio/content/verticales/<slug>")
    p.add_argument("--clip", type=int, action="append", default=[],
                   help="numero de pieza (1-based); repetible")
    p.add_argument("--todos", action="store_true")
    p.add_argument("--formato", default="vertical", choices=FORMATOS)
    p.add_argument("--calidad", default="ql", choices=CALIDADES)
    p.add_argument("--frames", type=int, default=0)
    p.add_argument("--guias", action="store_true")
    p.add_argument("--solo-componer", action="store_true",
                   dest="solo_componer")
    args = p.parse_args()

    curso_dir = args.curso_dir.resolve()
    curso = cargar_curso(curso_dir)
    piezas = curso["_piezas"]
    if args.todos:
        elegidas = piezas
    elif args.clip:
        malos = [n for n in args.clip if not 1 <= n <= len(piezas)]
        if malos:
            sys.exit(f"pieza fuera de rango: {malos} (hay {len(piezas)})")
        elegidas = [piezas[n - 1] for n in args.clip]
    else:
        sys.exit("elige --clip N o --todos")

    slug = curso.get("slug") or curso_dir.name
    fallos = [c["name"] for c in elegidas
              if not renderizar(c, curso, slug, args)]
    print()
    print(f"{len(elegidas) - len(fallos)}/{len(elegidas)} piezas renderizadas")
    for f in fallos:
        print(f"   FALLO: {f}")
    return 1 if fallos else 0


if __name__ == "__main__":
    sys.exit(main())
