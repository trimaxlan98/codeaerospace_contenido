"""Muestrario de los temas espaciales: convierte los .pptx a PDF (LibreOffice) y arma hojas de contacto.

  exports/presentaciones/espaciales/MUESTRARIO_TEMAS[_EN].jpg   mismas 6 diapositivas del seminario en cada tema registrado
  exports/presentaciones/espaciales/<tema>/<archivo>_<tema>.pdf + _hoja.jpg (todas las diapositivas)
  (también recorre espaciales/mezcla/ y los temas nuevos de animaciones/temas/)
Uso: python3 muestrario_espacial.py [--en] [tema …] [--nombre=MUESTRARIO_X]   (con temas solo esos; sin ellos, todos)
"""
import glob
import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from decks_espaciales import SALIDA  # noqa: E402
from temas_espaciales import TEMAS  # noqa: E402

FUENTE = Path.home() / ".local/share/fonts/codeaerospace/SpaceMono-Bold.ttf"
MUESTRA = [1, 3, 2, 5, 10, 40]  # portada, sección, texto, video, cita, cierre (seminario)


def a_pdf(pptx):
    pdf = pptx.with_suffix(".pdf")
    if pdf.exists() and pdf.stat().st_mtime >= pptx.stat().st_mtime:
        return pdf
    with tempfile.TemporaryDirectory() as perfil:
        subprocess.run(["soffice", f"-env:UserInstallation=file://{perfil}", "--headless", "--convert-to", "pdf",
                        "--outdir", str(pptx.parent), str(pptx)], capture_output=True, timeout=900)
    return pdf


def paginas(pdf, res, cuales=None):
    with tempfile.TemporaryDirectory() as d:
        if cuales:
            for p in cuales:
                subprocess.run(["pdftoppm", "-r", str(res), "-png", "-f", str(p), "-l", str(p), str(pdf), f"{d}/p{p:03d}"], check=True)
        else:
            subprocess.run(["pdftoppm", "-r", str(res), "-png", str(pdf), f"{d}/p"], check=True)
        return [Image.open(f).convert("RGB") for f in sorted(glob.glob(f"{d}/*.png"))]


def hoja(ims, cols, fondo=(28, 30, 38), sep=8, titulo=None):
    w, h = ims[0].size
    filas = (len(ims) + cols - 1) // cols
    top = 70 if titulo else 0
    sh = Image.new("RGB", (cols * (w + sep) + sep, filas * (h + sep) + sep + top), fondo)
    if titulo:
        ImageDraw.Draw(sh).text((sep + 6, 18), titulo, font=ImageFont.truetype(str(FUENTE), 30), fill=(230, 235, 245))
    for i, im in enumerate(ims):
        sh.paste(im, (sep + (i % cols) * (w + sep), top + sep + (i // cols) * (h + sep)))
    return sh


def main(argv=()):
    en = "--en" in argv
    ids = [a for a in argv if not a.startswith("--")]
    nombre_out = next((a.split("=", 1)[1] for a in argv if a.startswith("--nombre=")), "MUESTRARIO_TEMAS")
    patron = "seminar_*" if en else "seminario_*"
    filas = []
    f = ImageFont.truetype(str(FUENTE), 34)
    for e, E in TEMAS.items():
        if ids and e not in ids:
            continue
        carpeta = SALIDA / e
        for pptx in sorted(carpeta.glob("*.pptx")):
            pdf = a_pdf(pptx)
            hoja(paginas(pdf, 36), 6, titulo=f"{E.nombre.upper()}  ·  {pptx.stem}").save(
                pptx.with_name(pptx.stem + "_hoja.jpg"), quality=85)
            print(pptx.name, "→ pdf y hoja")
        sem = next(iter(sorted(carpeta.glob(patron + ".pdf"))), None)
        if sem:
            ims = paginas(sem, 50, MUESTRA)
            fila = hoja(ims, len(ims), sep=10)
            et = Image.new("RGB", (fila.width, 64), (28, 30, 38))
            fu = E.fuentes
            ImageDraw.Draw(et).text((14, 14), f"{E.nombre.upper()}   ·   {fu['titulo']} / {fu['cuerpo']} / {fu['etiqueta']}",
                                    font=f, fill=(230, 235, 245))
            filas += [et, fila]
    for pptx in sorted((SALIDA / "mezcla").glob("*.pptx")) if not ids and (SALIDA / "mezcla").is_dir() else []:
        pdf = a_pdf(pptx)
        hoja(paginas(pdf, 36), 6, titulo=f"MEZCLA  ·  {pptx.stem}").save(pptx.with_name(pptx.stem + "_hoja.jpg"), quality=85)
        print(pptx.name, "→ pdf y hoja")
    if filas:
        W = max(x.width for x in filas)
        out = Image.new("RGB", (W, sum(x.height for x in filas)), (28, 30, 38))
        y = 0
        for x in filas:
            out.paste(x, (0, y))
            y += x.height
        nombre = f"{nombre_out}{'_EN' if en else ''}.jpg"
        out.save(SALIDA / nombre, quality=86)
        print(nombre)


if __name__ == "__main__":
    main(sys.argv[1:])
