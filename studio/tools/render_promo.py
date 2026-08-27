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

IMAGEN = "codeaerospace_contenido-manim"
SALIDA = REPO / "render_jobs" / "promos"
FORMATOS = ("vertical", "horizontal", "cuadrado")
CALIDADES = ("ql", "qm", "qh")

# Un promo se ve en bucle: el ultimo frame tiene que ser el primero. Estos
# son los umbrales por debajo de los cuales el corte NO se percibe, y se
# aplican SOBRE EL SUELO DEL CODEC (ver `medir_bucle`).
COSTURA_DIF_MEDIA = 0.5     # diferencia media por canal (0-255)
COSTURA_PCT_PIXELES = 0.20  # % de subpixeles que cambian de forma visible


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
    """Duracion, dimensiones y fps reales del mp4 renderizado."""
    dur = float(ffprobe(video, "duration"))
    ancho, alto, tasa = ffprobe(video, "width,height,r_frame_rate",
                                stream=True).split(",")
    num, _, den = tasa.partition("/")
    fps = float(num) / float(den or 1)
    return {"dur": dur, "ancho": int(ancho), "alto": int(alto), "fps": fps}


# El ultimo frame NO se saca con `-ss dur-epsilon`: si el salto cae despues
# del ultimo paquete, ffmpeg sale con exito y no escribe nada. Se decodifica
# la cola con `-update 1` (cada frame pisa al anterior) y lo que queda al
# terminar ES el ultimo frame.
COLA_FINAL = 0.35


def _frame(video: Path, t: float, destino: Path):
    """El frame que hay en el instante t, en PNG."""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.4f}",
                    "-i", str(video), "-frames:v", "1", "-y",
                    str(destino)], check=True)


def _frame_final(video: Path, destino: Path):
    """El ULTIMO frame del video, en PNG."""
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-sseof",
                    f"-{COLA_FINAL}", "-i", str(video), "-update", "1", "-y",
                    str(destino)], check=True)


def _crudo(video: Path, t: float, ancho: int) -> bytes:
    """Un frame como bytes RGB, reducido: comparar 6 MP en Python puro es
    lento y no hace falta — la costura de un bucle no es cosa de un pixel."""
    return subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-ss", f"{t:.4f}", "-i",
         str(video), "-vf", f"scale={ancho}:-2", "-frames:v", "1",
         "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout


def _crudo_final(video: Path, ancho: int, tam: int) -> bytes:
    """El ULTIMO frame como bytes RGB: se decodifica la cola entera y se
    devuelven los ultimos `tam` bytes, que son el frame final completo."""
    cola = subprocess.run(
        ["ffmpeg", "-nostdin", "-v", "error", "-sseof", f"-{COLA_FINAL}",
         "-i", str(video), "-vf", f"scale={ancho}:-2", "-f", "rawvideo",
         "-pix_fmt", "rgb24", "-"],
        capture_output=True, check=True).stdout
    return cola[-tam:] if len(cola) >= tam else b""


def _comparar(a: bytes, b: bytes) -> tuple[float, float]:
    """(diferencia media por subpixel, % de subpixeles con salto visible)."""
    if not a or len(a) != len(b):
        return float("nan"), float("nan")
    total = sum(abs(x - y) for x, y in zip(a, b))
    visibles = sum(1 for x, y in zip(a, b) if abs(x - y) > 8)
    return total / len(a), 100.0 * visibles / len(a)


def medir_bucle(video: Path, datos: dict, destino: Path) -> dict:
    """Compara el primer frame con el ultimo: ¿se nota el corte al repetir?

    La comparacion se hace CONTRA EL SUELO DEL CODEC. Dos frames que en la
    escena son identicos (el 0 y el 1, dentro del respiro inicial) no salen
    identicos del h264: en un fondo plano y oscuro la cuantizacion deja una
    diferencia de fondo que puede llegar al 0.18 % de los subpixeles. Sin
    descontarla, un bucle perfecto parece sucio y uno sucio parece limpio.
    """
    destino.mkdir(parents=True, exist_ok=True)
    _frame(video, 0.0, destino / "primero.png")
    _frame_final(video, destino / "ultimo.png")
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", "-y",
                    "-i", str(destino / "primero.png"),
                    "-i", str(destino / "ultimo.png"), "-filter_complex",
                    "[0:v][1:v]hstack=inputs=2", str(destino / "costura.png")],
                   check=True)

    a = _crudo(video, 0.0, 240)
    b = _crudo_final(video, 240, len(a))
    media, pct = _comparar(a, b)
    # El suelo: dos frames consecutivos del respiro inicial, que en la
    # escena son el MISMO dibujo.
    piso_media, piso_pct = _comparar(a, _crudo(video, 1.5 / datos["fps"], 240))
    if media != media:  # NaN
        return {"ok": False, "media": media, "pct": pct,
                "piso_media": piso_media, "piso_pct": piso_pct}
    return {"ok": (media - piso_media) <= COSTURA_DIF_MEDIA
            and (pct - piso_pct) <= COSTURA_PCT_PIXELES,
            "media": media, "pct": pct,
            "piso_media": piso_media, "piso_pct": piso_pct}


def extraer_frames(video: Path, destino: Path, cuantos: int,
                   dur: float) -> int:
    destino.mkdir(parents=True, exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()
    for i in range(cuantos):
        _frame(video, dur * (i + 0.5) / cuantos, destino / f"{i + 1:02d}.png")
    return len(list(destino.glob("*.png")))


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
            f"/workspace/{scene_py.relative_to(REPO)}", promo["scene"]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        cola = "\n".join(proc.stderr.strip().splitlines()[-15:])
        print(f"    FALLO el render (exit {proc.returncode}):\n{cola}")
        return False

    # La carpeta de salida de manim depende de la resolucion y los fps
    # (1920p60, 960p30...): se busca en vez de darla por sabida.
    candidatos = sorted((trabajo / "videos").rglob(f"{promo['scene']}.mp4"))
    if not candidatos:
        print(f"    render sin video en {trabajo / 'videos'}")
        return False
    video = trabajo / "video.mp4"
    video.write_bytes(candidatos[0].read_bytes())

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
        n = extraer_frames(video, trabajo / "frames", args.frames,
                           datos["dur"])
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
