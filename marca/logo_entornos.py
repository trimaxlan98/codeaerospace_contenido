#!/usr/bin/env python3
"""El logo de Co.De Aerospace en los entornos espaciales de las diapositivas (los 18 temas registrados).

Para cada tema y formato genera el fondo procedural a la medida (fondos_espaciales.tamano) y compone
encima el logo oficial (plata sobre fondos oscuros, tinta sobre los claros) con un halo suave del acento
del tema. Sirve para elegir entornos de marca: portadas, fondos de pantalla, cabeceras, reels.

Salida: exports/estudio/logo_entornos/<formato>/<tema>.jpg y una hoja de contacto por formato.
Uso:    python3 marca/logo_entornos.py [tema …] [--formatos 16x9,4x5,9x16] [--tipo portada]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "animaciones"))
import fondos_espaciales as FE  # noqa: E402
import temas_espaciales as TE  # noqa: E402

SALIDA = REPO / "exports/estudio/logo_entornos"
FORMATOS = {"16x9": (1920, 1080), "4x5": (1080, 1350), "9x16": (1080, 1920)}
CLAROS = {"estacion", "cuaderno"}
FUENTE = Path.home() / ".local/share/fonts/codeaerospace/SpaceMono-Regular.ttf"


def logo(claro):
    return Image.open(REPO / "marca" / ("logo-codeaerospace-negro.png" if claro else "logo-codeaerospace-plata.png")).convert("RGBA")


def componer(fondo, tema, claro, acento):
    W, H = fondo.size
    lg = logo(claro)
    alto = int(min(W, H) * (0.46 if W >= H else 0.62))
    lg = lg.resize((int(lg.width * alto / lg.height), alto), Image.LANCZOS)
    # 16:9: tercio izquierdo (donde van los títulos de las diapositivas; la decoración de los temas vive a la
    # derecha). Vertical: centrado, un poco arriba (el horizonte de los entornos queda abajo).
    if W > H:
        x, y = int(W * 0.30 - lg.width / 2), int(H * 0.46 - lg.height / 2)
    else:
        x, y = (W - lg.width) // 2, int(H * 0.42 - lg.height / 2)
    img = fondo.convert("RGBA")
    a = lg.getchannel("A")
    r, g, b = (int(acento[i:i + 2], 16) for i in (1, 3, 5))
    for radio, fuerza in ((60, 0.30), (18, 0.35)):                 # halo del acento del tema
        halo = Image.new("RGBA", img.size, (r, g, b, 0))
        capa = Image.new("L", img.size, 0)
        capa.paste(a, (x, y))
        halo.putalpha(capa.filter(ImageFilter.GaussianBlur(radio)).point(lambda v: int(v * fuerza)))
        img.alpha_composite(halo)
    sombra = Image.new("RGBA", img.size, (0, 0, 0, 0))
    capa = Image.new("L", img.size, 0)
    capa.paste(a, (x + 6, y + 10))
    sombra.putalpha(capa.filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * (0.25 if claro else 0.6))))
    img.alpha_composite(sombra)
    img.alpha_composite(lg, (x, y))
    return img.convert("RGB")


def generar(tema, formato, tipo="portada", var=0):
    W, H = FORMATOS[formato]
    t = TE.obtener(tema)
    from fondos_a_medida import fondo_a_medida
    fondo = Image.open(fondo_a_medida(tema, tipo, var, W, H)).convert("RGB")   # vertical: ventana sobre la decoración
    acento = t.color.get("acento", "#00D9FF")
    img = componer(fondo, tema, tema in CLAROS, acento)
    destino = SALIDA / formato / f"{tema}.jpg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    img.save(destino, quality=92)
    return destino


def hoja(formato, temas):
    W, H = FORMATOS[formato]
    alto = 360
    ancho = int(alto * W / H)
    cols = 6 if W < H else 4
    filas = (len(temas) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (ancho + 10) + 10, filas * (alto + 44) + 10), (5, 8, 16))
    d = ImageDraw.Draw(sheet)
    f = ImageFont.truetype(str(FUENTE), 20)
    for k, tema in enumerate(temas):
        im = Image.open(SALIDA / formato / f"{tema}.jpg").resize((ancho, alto), Image.LANCZOS)
        x, y = 10 + (k % cols) * (ancho + 10), 10 + (k // cols) * (alto + 44)
        sheet.paste(im, (x, y))
        d.text((x, y + alto + 8), tema, font=f, fill=(150, 165, 190))
    sheet.save(SALIDA / f"HOJA_{formato}.jpg", quality=85)


def main(args):
    TE.cargar_plugins()
    formatos = list(FORMATOS)
    tipo = "portada"
    if "--formatos" in args:
        i = args.index("--formatos"); formatos = args[i + 1].split(","); del args[i:i + 2]
    if "--tipo" in args:
        i = args.index("--tipo"); tipo = args[i + 1]; del args[i:i + 2]
    temas = args or TE.ids()
    for fmt in formatos:
        for tema in temas:
            print(generar(tema, fmt, tipo))
        hoja(fmt, temas)


if __name__ == "__main__":
    main(sys.argv[1:])
