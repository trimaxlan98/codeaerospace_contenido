#!/usr/bin/env python3
"""Fotogramas de un mp4: la hoja de contactos y la figura suelta.

Dos cosas que en la terminal se hacen desde siempre (`render_local.py
--frames N`, un `ffmpeg -ss` a mano) y que dentro de la app no existian: el
unico resultado de un render era el mp4.

    python3 studio/tools/hoja_contactos.py tira VIDEO DESTINO --n 8 [--ancho 480]
    python3 studio/tools/hoja_contactos.py figura VIDEO DESTINO --t 12.5 --ancho 1920

`tira` deja `NN.png` (n fotogramas equiespaciados) y `final.png` (el ultimo
fotograma REAL) mas un `indice.json` con el instante de cada uno; `figura`
deja un solo PNG a la resolucion pedida, para una figura de tesis.

Se corre DENTRO del contenedor manim-render (el backend no tiene ffmpeg),
igual que `promo_verifica.py`: rutas fijas que deriva el runner, informe JSON
en la ultima linea de stdout.

Las dos trampas que justifican que esto sea un script y no dos `ffmpeg`
sueltos del runner:

  - **Un `-ss` al filo de la duracion sale con exito SIN escribir nada.**
    El ultimo fotograma se saca con `-sseof -COLA_FINAL -update 1`, que es
    como lo hacen `promo_verifica.py` y `verifica_vertical.py`. Y como el
    instante de la figura lo manda el `<video>` del navegador —que al
    terminar marca `currentTime == duration`— cualquier `t` dentro de la
    cola final se atiende por ese mismo camino, o el operador pediria el
    ultimo fotograma y se llevaria un PNG que no existe.
  - **Un contenedor por fotograma cuesta mas que los fotogramas.** Arrancar
    `docker compose run` son ~1,5 s; doce arranques son veinte segundos para
    doce PNG de un cuarto de segundo. Un solo contenedor los saca todos.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

# Cola desde el final para pescar el ultimo fotograma real. 0.4 s cubre de
# sobra un GOP a 15 fps (el peor caso: `-ql`).
COLA_FINAL = 0.4
# Ancho de la hoja de contactos: se mira en una rejilla, no se imprime.
ANCHO_TIRA = 480
# Techo del ancho de una figura (4K); mas alla no hay pantalla ni pagina.
ANCHO_MAX = 3840
N_MAX = 24


class ErrorFotograma(Exception):
    pass


def _ff(*args: str) -> None:
    subprocess.run(["ffmpeg", "-nostdin", "-v", "error", *args],
                   capture_output=True, check=True)


def _probe(video: Path, campos: str, stream: str | None = None) -> str:
    cmd = ["ffprobe", "-v", "error"]
    if stream:
        cmd += ["-select_streams", stream, "-show_entries", f"stream={campos}"]
    else:
        cmd += ["-show_entries", f"format={campos}"]
    cmd += ["-of", "csv=p=0", str(video)]
    return subprocess.run(cmd, capture_output=True, text=True,
                          check=True).stdout.strip()


def duracion(video: Path) -> float:
    try:
        return float(_probe(video, "duration"))
    except (subprocess.CalledProcessError, ValueError) as e:
        raise ErrorFotograma(f"no se pudo leer la duracion: {e}") from e


def medidas(png: Path) -> tuple[int, int]:
    """WxH REAL del PNG escrito. La resolucion que ensena la interfaz es la
    medida sobre el archivo, no la que se pidio: `scale=W:-2` redondea el
    alto a par y un `-1` de mas mentiria en la ficha de una figura."""
    try:
        ancho, alto = _probe(png, "width,height", stream="v:0").split(",")[:2]
        return int(ancho), int(alto)
    except (subprocess.CalledProcessError, ValueError):
        return 0, 0


def _sacar(video: Path, t: float, destino: Path, ancho: int,
           dur: float) -> None:
    """Un fotograma en `t`, escalado a `ancho`. Dentro de la cola final se
    usa `-sseof`: ver la nota del encabezado."""
    escala = ["-vf", f"scale={ancho}:-2"] if ancho else []
    if t >= dur - COLA_FINAL:
        _ff("-sseof", f"-{COLA_FINAL}", "-i", str(video), *escala,
            "-update", "1", "-y", str(destino))
    else:
        _ff("-ss", f"{t:.4f}", "-i", str(video), *escala,
            "-frames:v", "1", "-y", str(destino))
    if not destino.is_file() or destino.stat().st_size == 0:
        raise ErrorFotograma(f"ffmpeg no escribio nada en t={t:.3f}s")


def tira(video: Path, destino: Path, n: int, ancho: int) -> dict:
    """n fotogramas equiespaciados + el ultimo real, con su instante."""
    if not (1 <= n <= N_MAX):
        raise ErrorFotograma(f"n fuera de rango (1-{N_MAX})")
    dur = duracion(video)
    destino.mkdir(parents=True, exist_ok=True)
    for viejo in destino.glob("*.png"):
        viejo.unlink()

    fotogramas = []
    for i in range(n):
        # El mismo reparto que `render_local.py`: se evitan el primer y el
        # ultimo instante, que suelen ser fundidos a negro y no ensenan nada.
        t = dur * (i + 0.5) / n
        nombre = f"{i + 1:02d}.png"
        _sacar(video, t, destino / nombre, ancho, dur)
        w, h = medidas(destino / nombre)
        fotogramas.append({"archivo": nombre, "t": round(t, 3),
                           "ancho": w, "alto": h})

    _sacar(video, dur, destino / "final.png", ancho, dur)
    w, h = medidas(destino / "final.png")
    informe = {
        "ok": True, "n": n, "duracion": round(dur, 3), "ancho": ancho,
        "frames": fotogramas,
        "final": {"archivo": "final.png", "t": round(dur, 3),
                  "ancho": w, "alto": h},
    }
    # El indice se guarda AL LADO de los PNG: con el, el backend puede
    # volver a servir la hoja (y saber que ya esta hecha para ese n) sin
    # arrancar un contenedor. Esa es toda la idempotencia.
    (destino / "indice.json").write_text(json.dumps(informe, indent=1),
                                         encoding="utf-8")
    return informe


def figura(video: Path, destino: Path, t: float, ancho: int) -> dict:
    """Un fotograma a la resolucion pedida: la salida estatica de una tesis."""
    if not (16 <= ancho <= ANCHO_MAX):
        raise ErrorFotograma(f"ancho fuera de rango (16-{ANCHO_MAX})")
    dur = duracion(video)
    if t < 0 or t > dur + COLA_FINAL:
        raise ErrorFotograma(f"instante fuera del video (0-{dur:.3f}s)")
    destino.parent.mkdir(parents=True, exist_ok=True)
    _sacar(video, min(t, dur), destino, ancho, dur)
    w, h = medidas(destino)
    return {"ok": True, "archivo": destino.name, "t": round(min(t, dur), 3),
            "ancho": w, "alto": h, "bytes": destino.stat().st_size,
            "duracion": round(dur, 3)}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="modo", required=True)

    a = sub.add_parser("tira", help="hoja de contactos")
    a.add_argument("video", type=Path)
    a.add_argument("destino", type=Path, help="directorio de los PNG")
    a.add_argument("--n", type=int, default=8)
    a.add_argument("--ancho", type=int, default=ANCHO_TIRA)

    b = sub.add_parser("figura", help="un fotograma a resolucion")
    b.add_argument("video", type=Path)
    b.add_argument("destino", type=Path, help="archivo PNG de salida")
    b.add_argument("--t", type=float, required=True)
    b.add_argument("--ancho", type=int, default=1920)

    args = p.parse_args()
    if not args.video.is_file():
        print(json.dumps({"ok": False, "error": "el video no existe"}))
        return 1
    try:
        informe = (tira(args.video, args.destino, args.n, args.ancho)
                   if args.modo == "tira"
                   else figura(args.video, args.destino, args.t, args.ancho))
    except (ErrorFotograma, subprocess.CalledProcessError) as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 1
    print(json.dumps(informe))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
