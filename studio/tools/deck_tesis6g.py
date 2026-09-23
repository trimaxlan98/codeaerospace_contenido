#!/usr/bin/env python3
"""Reune las piezas limpias de la tesis 6G en una entrega para PowerPoint.

Las piezas se renderizan una a una con `empaquetar_presentacion.py` (un
directorio por pieza y fondo). Esta herramienta las junta:

    studio/backend/venv/bin/python studio/tools/deck_tesis6g.py \\
        --origen render_jobs/validacion/tesis6g-piezas --calidad qh

y deja en `exports/presentaciones/tesis-6g/<fondo>/`:

    piezas-<fondo>-video.pptx   todas las piezas, un slide por paso, en mp4
                                (mejor imagen; el autoplay se verifica una vez)
    piezas-<fondo>-gif.pptx     lo mismo en GIF (arranca solo en cualquier
                                PowerPoint; 256 colores)
    NN-<pieza>/                 completa.mp4, fragmentos/, posters/ y el
                                .pptx de esa pieza sola
    LEEME.md                    que hay y como meterlo en el deck propio

Los dos fondos (`navy` = #0B1F3A de los slides oscuros del deck del
seminario, `blanco` = los claros) salen por separado: una pieza se inserta
sobre el slide de SU color y no se nota el borde.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "studio" / "backend"))
from app.presentaciones import construir_deck  # noqa: E402

FONDOS = {"navy": "#0B1F3A", "blanco": "#FFFFFF"}


def duracion(mp4: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                        "-of", "csv=p=0", str(mp4)], capture_output=True, text=True)
    return float(r.stdout.strip() or 0)


def fragmentos_de(pieza_dir: Path, nombre: str) -> list[dict]:
    pasos = json.loads((pieza_dir / "pasos.json").read_text(encoding="utf-8"))["pasos"]
    salida = []
    for i, mp4 in enumerate(sorted((pieza_dir / "fragmentos").glob("*.mp4"))):
        etiqueta = pasos[i]["etiqueta"] if i < len(pasos) else f"Paso {i + 1}"
        salida.append({"nombre": mp4.stem, "escena": nombre, "etiqueta": etiqueta,
                       "mp4": str(mp4), "gif": str(mp4.with_suffix(".gif")),
                       "poster": str(pieza_dir / "posters" / f"{mp4.stem}.png"),
                       "duracion": duracion(mp4)})
    return salida


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origen", type=Path, required=True)
    ap.add_argument("--calidad", default="qh")
    ap.add_argument("--destino", type=Path, default=REPO / "exports/presentaciones/tesis-6g")
    ap.add_argument("--piezas", nargs="*", help="orden y seleccion (defecto: todas)")
    a = ap.parse_args()
    origen = a.origen if a.origen.is_absolute() else REPO / a.origen

    piezas = a.piezas or sorted(p.name for p in origen.iterdir() if p.is_dir())
    for fondo, color in FONDOS.items():
        dst = a.destino / fondo
        todos, filas = [], []
        for nombre in piezas:
            src = origen / nombre / f"{fondo}-{a.calidad}"
            if not (src / "completa.mp4").exists():
                print(f"  falta {nombre} {fondo}-{a.calidad}: se salta")
                continue
            out = dst / nombre
            if out.exists():
                shutil.rmtree(out)
            out.mkdir(parents=True)
            for sub in ("fragmentos", "posters"):
                shutil.copytree(src / sub, out / sub)
            for f in ("completa.mp4", "pasos.json"):
                shutil.copy2(src / f, out / f)
            for pp in src.glob("*.pptx"):
                shutil.copy2(pp, out / f"{nombre}-{fondo}.pptx")
            frs = fragmentos_de(out, nombre)
            todos += frs
            filas.append((nombre, len(frs), sum(f["duracion"] for f in frs)))
        if not todos:
            continue
        for tipo in ("video", "gif"):
            p = construir_deck(todos, dst / f"piezas-{fondo}-{tipo}.pptx", 16 / 9, color, tipo)
            print(f"  {p.relative_to(REPO)}  {p.stat().st_size / 1e6:.1f} MB")
        lineas = [f"# Piezas limpias de la tesis 6G — fondo {fondo} ({color})", "",
                  "Animaciones sin titulos ni subtitulos: el texto lo pone el slide.",
                  "Cada pieza avanza con el clic (un slide por paso, empalme invisible).", "",
                  "| pieza | pasos | segundos |", "|---|---|---|"]
        lineas += [f"| {n} | {k} | {s:.1f} |" for n, k, s in filas]
        lineas += ["", "## Como meterlas en tu deck", "",
                   f"- Abre `piezas-{fondo}-video.pptx`, copia los slides de la pieza y",
                   "  pegalos en tu presentacion con *Mantener formato de origen*.",
                   "- O inserta los mp4 de `NN-pieza/fragmentos/` en tus propios slides",
                   f"  (fondo {color}); el primer fotograma de cada uno esta en `posters/`.",
                   "- Si el video no arranca solo en tu PowerPoint, usa el deck `-gif`:",
                   "  el GIF arranca siempre (pierde algo de color)."]
        (dst / "LEEME.md").write_text("\n".join(lineas) + "\n", encoding="utf-8")
        print(f"  {fondo}: {len(filas)} piezas, {len(todos)} slides")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
