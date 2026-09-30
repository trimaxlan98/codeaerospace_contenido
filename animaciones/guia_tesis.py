"""Guía de las piezas de la tesis (seminario y comité) desde catalogo_tesis.py + duraciones reales.

Salida: exports/GUIA_TESIS_PIEZAS.md. Uso: python3 guia_tesis.py
"""
import subprocess
from pathlib import Path

from catalogo_tesis import COMITE, SEMINARIO

EXP = Path(__file__).resolve().parent.parent / "exports"


def dur(carpeta, clase):
    mp4 = EXP / carpeta / "oscuro" / f"{clase}.mp4"
    if not mp4.exists():
        return "—"
    s = subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)])
    return f"{float(s):.1f} s"


L = ["# Piezas de la tesis — seminario de divulgación y comité tutorial", "",
     "Animaciones nuevas (sin títulos ni narración; ≤3 palabras por etiqueta), 1080p30 en fondo oscuro y claro. "
     "Videos: `exports/<archivo>/{oscuro,claro}/<Pieza>.mp4`; copia sin el fundido final (termina en el último cuadro legible, "
     "es la que se incrusta en PowerPoint): `exports/<archivo>/{oscuro,claro}_final/`. PNG 8K: `exports/png/<tema>/<archivo>/`; "
     "stickers: `exports/png/stickers/`. Las piezas que muestran contribuciones propias llevan el chip «En desarrollo»; "
     "las de terceros, su chip de origen; las cifras de ejemplo, «Ilustrativo».", ""]
for titulo, bloques in (("Seminario de divulgación", SEMINARIO), ("Comité tutorial", COMITE)):
    L += [f"## {titulo}", ""]
    for bloque, carpeta, piezas in bloques:
        L += [f"### {bloque} · `{carpeta}.py`", "", "| Pieza | Duración | Qué muestra | Cuándo usarla |", "|---|---|---|---|"]
        L += [f"| `{c}` | {dur(carpeta, c)} | {m} | {u} |" for c, m, u in piezas]
        L.append("")
(EXP / "GUIA_TESIS_PIEZAS.md").write_text("\n".join(L), encoding="utf-8")
print("GUIA_TESIS_PIEZAS.md", sum(len(p) for _, _, p in SEMINARIO + COMITE), "piezas")
