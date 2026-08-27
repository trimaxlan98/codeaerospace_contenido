#!/usr/bin/env python3
"""Sonoriza las piezas de un curso vertical y las une en un solo video.

El curso se renderiza pieza a pieza (`render_vertical.py`) para que rehacer
una no obligue a rehacer las demas; aqui se cierra el circulo:

  1. a cada pieza se le pega su audio — la cama de SFX del bloque "audio"
     de su `clip.json` y, si existe, la voz ya sintetizada y alineada;
  2. se mide el pico de cada una (vienen calientes de fabrica);
  3. se concatenan **sin re-encodear** en el orden del manifiesto:
     intro + clip 1 + ... + clip n + cierre.

    studio/backend/venv/bin/python studio/tools/unir_vertical.py \
        studio/content/verticales/<slug>
    ... --solo-sonido      sonoriza las piezas y no concatena
    ... --solo-unir        concatena lo que ya haya en piezas/
    ... --sin-voz          ignora los wav de voz (montaje mudo de prueba)
    ... --pieza 3          solo esa pieza (repetible), para rehacer una

Rutas:

    render_jobs/verticales/<slug>/<pieza>/video.mp4   entrada (mudo)
    exports/verticales/<slug>/voz/<pieza>.wav         voz bajada del VPS
    exports/verticales/<slug>/piezas/<pieza>.mp4      pieza sonorizada
    exports/verticales/<slug>/concat.txt                 orden del montaje
    exports/verticales/<slug>/<slug>_vertical.mp4        LA ENTREGA

`sfx.py` sintetiza con numpy y trae su propio canario; si el numpy del host
no le sirve, esta herramienta reintenta la mezcla dentro del contenedor.
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "tools"))

from render_vertical import cargar_curso, datos_video  # noqa: E402

IMAGEN = "codeaerospace_contenido-manim"
SFX = REPO / "studio" / "tools" / "sfx.py"
PICO_MAX_DB = -0.5       # por encima de esto, la pieza va a recortar


def pico_db(video: Path) -> float | None:
    """max_volume de la pista de audio, en dBFS (None si no tiene audio)."""
    salida = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-i", str(video),
         "-af", "volumedetect", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    for linea in salida.splitlines():
        if "max_volume:" in linea:
            return float(linea.split("max_volume:")[1].split("dB")[0].strip())
    return None


def mezclar(pieza_dir: Path, video: Path, salida: Path,
            voz: Path | None) -> bool:
    """`sfx.py promo` en el host; si el numpy no sirve, en el contenedor.

    El interprete es el `python3` del SISTEMA, no el venv del backend: el
    venv no trae numpy (no lo necesita) y `sfx.py` sintetiza con numpy. Si
    ese python tampoco sirve —el canario del propio sfx.py sale con 2, o
    falta el modulo— la mezcla se rehace dentro del contenedor de render,
    que siempre lo tiene.
    """
    args = [str(pieza_dir), str(video), str(salida)]
    if voz:
        args.append(str(voz))
    proc = subprocess.run(["python3", str(SFX), "promo", *args],
                          capture_output=True, text=True)
    if proc.returncode == 0:
        return True

    print("    (el python del host no sirve para sfx: al contenedor)")
    if proc.returncode not in (2,) and "No module named" not in proc.stderr:
        print(proc.stdout.strip())
        print(proc.stderr.strip()[-600:])
    rel = [str(Path(a).resolve().relative_to(REPO)) for a in args]
    cmd = ["docker", "run", "--rm", "--network", "none",
           "-v", f"{REPO}:/workspace", "-w", "/workspace", IMAGEN,
           "python3", "studio/tools/sfx.py", "promo",
           *[f"/workspace/{r}" for r in rel]]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        print(proc.stderr.strip()[-800:])
        return False
    return True


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("curso_dir", type=Path)
    p.add_argument("--pieza", type=int, action="append", default=[])
    p.add_argument("--solo-sonido", action="store_true", dest="solo_sonido")
    p.add_argument("--solo-unir", action="store_true", dest="solo_unir")
    p.add_argument("--sin-voz", action="store_true", dest="sin_voz")
    args = p.parse_args()

    curso_dir = args.curso_dir.resolve()
    curso = cargar_curso(curso_dir)
    slug = curso.get("slug") or curso_dir.name
    entrada = REPO / "render_jobs" / "verticales" / slug
    destino = REPO / "exports" / "verticales" / slug
    (destino / "piezas").mkdir(parents=True, exist_ok=True)
    (destino / "voz").mkdir(parents=True, exist_ok=True)

    piezas = curso["_piezas"]
    if args.pieza:
        piezas = [c for c in piezas if c["_n"] in args.pieza]

    hechas, fallos = [], []
    if not args.solo_unir:
        for clip in piezas:
            base = clip["_slug"]
            video = entrada / base / "video.mp4"
            if not video.is_file():
                print(f"[{clip['_n']:02d}] FALTA el render: "
                      f"{video.relative_to(REPO)}")
                fallos.append(base)
                continue
            voz = destino / "voz" / f"{base}.wav"
            usar_voz = voz if (voz.is_file() and not args.sin_voz) else None
            salida = destino / "piezas" / f"{base}.mp4"
            print(f"[{clip['_n']:02d}] {clip['name']}"
                  f"{'  (con voz)' if usar_voz else '  (solo SFX)'}")
            if not mezclar(clip["_dir"], video, salida, usar_voz):
                fallos.append(base)
                continue
            pico = pico_db(salida)
            d = datos_video(salida)
            aviso = ""
            if pico is not None and pico > PICO_MAX_DB:
                aviso = (f"   <-- PICO ALTO, baja pico_db en "
                         f"{clip['_slug']}/clip.json")
            print(f"    {d['dur']:.2f} s · pico "
                  f"{'n/d' if pico is None else f'{pico:.1f} dB'}{aviso}")
            hechas.append(base)

    if args.solo_sonido:
        print(f"\n{len(hechas)} piezas sonorizadas, {len(fallos)} fallos")
        return 1 if fallos else 0

    # --- montaje: el orden lo manda el manifiesto, no el disco ------
    orden = []
    for clip in curso["_piezas"]:
        base = clip["_slug"]
        mp4 = destino / "piezas" / f"{base}.mp4"
        if not mp4.is_file():
            print(f"FALTA la pieza sonorizada {mp4.relative_to(REPO)}")
            return 1
        orden.append(mp4)

    lista = destino / "concat.txt"
    lista.write_text("".join(f"file 'piezas/{m.name}'\n" for m in orden))
    final = destino / f"{slug}_vertical.mp4"
    proc = subprocess.run(
        ["ffmpeg", "-y", "-nostdin", "-v", "error", "-f", "concat",
         "-safe", "0", "-i", str(lista), "-c", "copy", str(final)],
        capture_output=True, text=True, cwd=destino)
    if proc.returncode != 0:
        print(proc.stderr.strip()[-900:])
        return 1

    d = datos_video(final)
    total = sum(datos_video(m)["dur"] for m in orden)
    print(f"\n{final.relative_to(REPO)}")
    print(f"    {d['ancho']}x{d['alto']} @ {d['fps']:.0f} fps · "
          f"{d['dur'] / 60:.2f} min ({d['dur']:.2f} s) · "
          f"{len(orden)} piezas")
    if abs(d["dur"] - total) > 0.5:
        print(f"    AVISO: la suma de las piezas da {total:.2f} s y el "
              "montaje otra cosa: el concat perdio algo")
    pico = pico_db(final)
    print(f"    pico del montaje: "
          f"{'n/d' if pico is None else f'{pico:.1f} dB'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
