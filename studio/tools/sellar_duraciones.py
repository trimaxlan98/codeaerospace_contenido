#!/usr/bin/env python3
"""Escribe en cada `clip.json` la duracion REAL de su render.

    studio/backend/venv/bin/python studio/tools/sellar_duraciones.py \\
        studio/content/verticales/<slug>
    ... --fps 60          los fps que TIENE que tener el render (defecto 60)
    ... --seco            enseña lo que haria y no toca nada

Por que existe: `verifica_vertical.py` compara `duracion_objetivo` con la
duracion del render y falla si no cuadran, porque la voz se alinea contra
el manifiesto. Con veinte piezas, rellenar ese campo a mano es una fuente
de errores tonta y silenciosa.

Y por que lleva un guardian de fps: **el redondeo a fotograma de 60 fps no
es el de 30**. Sellar aqui la duracion de un render `ql` (30 fps) y
publicar luego el `qh` (60 fps) deja el manifiesto desfasado unas
centesimas en cada pieza — suficiente para que la voz entre tarde y para
que `verifica_vertical` marque veinte fallos que nadie entiende. Asi que
esta herramienta se NIEGA a sellar un render que no este a los fps
esperados, y hay que correrla DESPUES del `qh`, no antes.
"""
import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "tools"))

from render_vertical import cargar_curso, datos_video  # noqa: E402

SALIDA = REPO / "render_jobs" / "verticales"


def main() -> int:
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("curso_dir", type=Path)
    p.add_argument("--fps", type=int, default=60)
    p.add_argument("--seco", action="store_true",
                   help="enseña lo que haria y no escribe nada")
    args = p.parse_args()

    curso = cargar_curso(args.curso_dir.resolve())
    slug = curso.get("slug") or args.curso_dir.name

    cambios, faltan, malos = 0, [], []
    for clip in curso["_piezas"]:
        base = clip["_slug"]
        video = SALIDA / slug / base / "video.mp4"
        if not video.is_file():
            print(f"[{clip['_n']:02d}] {base}: FALTA el render")
            faltan.append(base)
            continue
        d = datos_video(video)
        if abs(d["fps"] - args.fps) > 0.5:
            print(f"[{clip['_n']:02d}] {base}: el render esta a "
                  f"{d['fps']:.0f} fps y se esperan {args.fps}. NO se sella")
            malos.append(base)
            continue

        manifiesto = clip["_dir"] / "clip.json"
        datos = json.loads(manifiesto.read_text())
        antes = datos.get("duracion_objetivo")
        nueva = round(float(d["dur"]), 2)
        if antes is not None and abs(float(antes) - nueva) < 5e-3:
            print(f"[{clip['_n']:02d}] {base}: ya estaba en {nueva:.2f} s")
            continue
        print(f"[{clip['_n']:02d}] {base}: "
              f"{'(nada)' if antes is None else f'{antes}'} -> {nueva:.2f} s")
        if not args.seco:
            datos["duracion_objetivo"] = nueva
            manifiesto.write_text(
                json.dumps(datos, ensure_ascii=False, indent=2) + "\n")
        cambios += 1

    print(f"\n{cambios} manifiestos {'a sellar' if args.seco else 'sellados'}"
          f", {len(faltan)} sin render, {len(malos)} a los fps equivocados")
    return 1 if (faltan or malos) else 0


if __name__ == "__main__":
    raise SystemExit(main())
