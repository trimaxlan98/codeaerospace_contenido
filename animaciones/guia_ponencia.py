"""Genera ../exports/GUIA_PONENCIA.md desde catalogo.py + duraciones reales de los mp4."""
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from catalogo import BLOQUES  # noqa: E402
from empaquetar_ponencia import EXP, nombre_legible, slug  # noqa: E402


def dur(carpeta, clase):
    p = EXP / carpeta / "oscuro" / f"{clase}.mp4"
    if not p.exists():
        return 0.0
    return float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                          "-of", "csv=p=0", str(p)]).decode())


def main():
    L = ["# Guía de la ponencia — material animado", "",
         "Las 65 piezas están ordenadas como un posible hilo de charla. **Nada se descarta**: la columna ⭐ solo",
         "marca una selección sugerida para una charla (los totales están al final). Cada video dura 13–27 s",
         "y está pensado para proyectarse mientras se habla encima.", "",
         "Archivos: videos `exports/<tema>/{oscuro,claro}/`, PNG y stickers `exports/png/`, ",
         "presentaciones `exports/presentaciones/`, montajes por bloque `exports/montajes/`.", ""]
    tot_all = tot_rec = 0.0
    for i, (bloque, carpeta, piezas) in enumerate(BLOQUES, 1):
        L += [f"## {i}. {bloque}", "", f"Carpeta: `{carpeta}` · montaje: `montajes/{i:02d}_{slug(bloque)}_oscuro.mp4`", "",
              "| ⭐ | Pieza | Qué muestra | Cuándo usarla | Dur. |", "|---|---|---|---|---|"]
        for clase, muestra, uso, rec in piezas:
            d = dur(carpeta, clase)
            tot_all += d
            tot_rec += d if rec else 0
            L.append(f"| {'⭐' if rec else ''} | {nombre_legible(clase)} (`{clase}`) | {muestra} | {uso} | {d:.0f} s |")
        L.append("")
    n_rec = sum(1 for _, _, ps in BLOQUES for p in ps if p[3])
    L += ["## Totales", "", f"- Todas: 65 piezas, {tot_all / 60:.1f} min.",
          f"- Sugeridas ⭐: {n_rec} piezas, {tot_rec / 60:.1f} min (`presentaciones/ponencia_seleccion_*.pptx`, "
          "`montajes/reel_recomendadas_*.mp4`).", ""]
    (EXP / "GUIA_PONENCIA.md").write_text("\n".join(L), encoding="utf-8")
    print("GUIA_PONENCIA.md", f"{tot_all / 60:.1f} min / {tot_rec / 60:.1f} min sugeridas")


main()
