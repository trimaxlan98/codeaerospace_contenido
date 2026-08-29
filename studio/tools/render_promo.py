#!/usr/bin/env python3
"""Renderiza un clip de PROMOCION para redes en el formato que se le pida.

Hermano de `render_local.py`, con tres diferencias que vienen del formato:

  1. **La escena elige su lienzo.** El promo no vive en 16:9: la herramienta
     pasa el formato por entorno (PROMO_FORMATO) y la escena lo aplica con
     `promo.formato()`. Un mismo archivo sale en 9:16 y en 16:9.
  2. **No hay regla de 28-45 s.** Un promo dura 8-15 s.
  3. **Mide la costura del bucle**: compara el PRIMER frame con el ULTIMO y
     dice si el corte se va a notar cuando la app repita el video. Es la
     verificacion que hace o deshace un promo, y a ojo no se hace bien.

    studio/backend/venv/bin/python studio/tools/render_promo.py \
        studio/content/promos/<slug>
    ... --formato horizontal    vertical (defecto) | horizontal | cuadrado
    ... --calidad qh            ql (defecto, lado corto 540) | qm | qh (1080)
    ... --frames 8              frames PNG equiespaciados para la revision
    ... --guias                 dibuja la zona que la app NO tapa
    ... --solo-componer         escribe el scene.py y sale (sin Docker)

Deja todo en `render_jobs/promos/<slug>/<formato>/`:

    scene.py          el script compuesto, tal cual lo ve manim
    video.mp4         el render
    frames/NN.png     frames equiespaciados
    bucle/{primero,ultimo}.png  y  bucle/costura.png (los dos juntos)

El repo se monta READ-ONLY en el contenedor, igual que en produccion.
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

# La medicion (costura del bucle, audio, frames) vive en UN solo sitio: el
# mismo modulo que ejecuta el runner de ManimStudio dentro del contenedor.
sys.path.insert(0, str(Path(__file__).resolve().parent))
from promo_verifica import (datos_video, extraer_frames,  # noqa: E402
                            medir_bucle)

IMAGEN = "codeaerospace_contenido-manim"
SALIDA = REPO / "render_jobs" / "promos"
FORMATOS = ("vertical", "horizontal", "cuadrado")
CALIDADES = ("ql", "qm", "qh")



def cargar_promo(promo_dir: Path) -> dict:
    """Lee y valida promo.json. Sale con mensaje claro ante cualquier falta."""
    manifest = promo_dir / "promo.json"
    if not manifest.is_file():
        sys.exit(f"no existe {manifest}")
    promo = json.loads(manifest.read_text())
    for campo in ("name", "scene", "file"):
        if not promo.get(campo):
            sys.exit(f"{manifest}: falta '{campo}'")
    escena = promo_dir / promo["file"]
    if not escena.is_file():
        sys.exit(f"no existe {escena}")
    style_path = promo_dir / promo.get("style_block", "style_block.py")
    promo["_style"] = style_path.read_text() if style_path.is_file() else ""
    promo["_script"] = escena.read_text()
    return promo


def renderizar(promo: dict, slug: str, args) -> bool:
    trabajo = SALIDA / slug / args.formato
    trabajo.mkdir(parents=True, exist_ok=True)
    scene_py = trabajo / "scene.py"
    scene_py.write_text(branding.aplicar(
        compose_script(promo["_style"], promo["_script"])))

    print(f"\n{promo['name']}  [{args.formato} · {args.calidad}]")
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
            "/media/scene.py", promo["scene"]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cola = "\n".join(proc.stderr.strip().splitlines()[-15:])
        print(f"    FALLO el render (exit {proc.returncode}):\n{cola}")
        return False

    # La carpeta de salida de manim depende de la resolucion y los fps
    # (1920p60, 960p30...): se busca en vez de darla por sabida. Y se coge
    # el MAS RECIENTE, no el primero por nombre: si el mismo promo ya se
    # rendrizo en otra calidad, "1920p60" ordena antes que "960p60" y la
    # herramienta medía el archivo viejo diciendo que era el nuevo.
    candidatos = list((trabajo / "videos").rglob(f"{promo['scene']}.mp4"))
    if not candidatos:
        print(f"    render sin video en {trabajo / 'videos'}")
        return False
    reciente = max(candidatos, key=lambda p: p.stat().st_mtime)
    video = trabajo / "video.mp4"
    video.write_bytes(reciente.read_bytes())

    datos = datos_video(video)
    print(f"    video: {video.relative_to(REPO)}")
    print(f"    {datos['ancho']}x{datos['alto']} @ {datos['fps']:.0f} fps"
          f" · {datos['dur']:.2f} s")

    objetivo = promo.get("duracion_objetivo")
    if objetivo and abs(datos["dur"] - float(objetivo)) > 0.35:
        print(f"    AVISO: duracion {datos['dur']:.2f} s, el manifiesto dice"
              f" {objetivo} s")

    bucle = medir_bucle(video, datos, trabajo / "bucle")
    marca = "BUCLE LIMPIO" if bucle["ok"] else "BUCLE VISIBLE"
    print(f"    {marca}: dif media {bucle['media']:.3f}/255 ·"
          f" {bucle['pct']:.3f} % de subpixeles con salto visible"
          f"   (suelo del codec: {bucle['piso_media']:.3f} ·"
          f" {bucle['piso_pct']:.3f} %)")
    if not bucle["ok"]:
        print("      -> el ultimo frame NO es el primero; mira"
              f" {(trabajo / 'bucle' / 'costura.png').relative_to(REPO)}")

    if args.frames:
        n = len(extraer_frames(video, trabajo / "frames", args.frames,
                               datos["dur"]))
        print(f"    {n} frames en {(trabajo / 'frames').relative_to(REPO)}")
    return True


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("promo_dir", type=Path)
    p.add_argument("--formato", default="vertical", choices=FORMATOS)
    p.add_argument("--calidad", default="ql", choices=CALIDADES)
    p.add_argument("--frames", type=int, default=0)
    p.add_argument("--guias", action="store_true")
    p.add_argument("--solo-componer", action="store_true", dest="solo_componer")
    args = p.parse_args()

    promo_dir = args.promo_dir.resolve()
    promo = cargar_promo(promo_dir)
    return 0 if renderizar(promo, promo_dir.name, args) else 1


if __name__ == "__main__":
    sys.exit(main())
