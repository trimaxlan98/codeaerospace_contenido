"""Post-proceso de los PNG 8K: stickers recortados + hojas de conjunto.

Entrada : ../exports/png/{oscuro,claro}/<tema>/<Pieza>.png   (8K, transparente)
Salida  : ../exports/png/stickers/{oscuro,claro}/<tema>/<Pieza>.png   (recorte al contenido, margen 3 %)
          ../exports/png/conjunto/{oscuro,claro}_<tema>.png y _todas.png (hojas 8K sobre fondo del tema)
"""
from pathlib import Path
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent / "exports" / "png"
FONDOS = {"oscuro": (11, 31, 58), "claro": (255, 255, 255)}
Image.MAX_IMAGE_PIXELS = None


def sticker(src, dst, margen=0.03):
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        return True  # incremental: ya está al día
    im = Image.open(src).convert("RGBA")
    caja = im.getchannel("A").point(lambda a: 255 if a > 8 else 0).getbbox()
    if not caja:
        return False
    x0, y0, x1, y1 = caja
    m = int(max(x1 - x0, y1 - y0) * margen)
    caja = (max(0, x0 - m), max(0, y0 - m), min(im.width, x1 + m), min(im.height, y1 + m))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.crop(caja).save(dst, compress_level=3)
    return True


def hoja(archivos, dst, fondo, cols, celda=(1920, 1080), ancho_total=7680):
    filas = -(-len(archivos) // cols)
    w = ancho_total // cols
    h = int(w * celda[1] / celda[0])
    lienzo = Image.new("RGB", (w * cols, h * filas), fondo)
    for i, a in enumerate(archivos):
        im = Image.open(a).convert("RGBA")
        im.thumbnail((w, h), Image.LANCZOS)
        cx, cy = (i % cols) * w + (w - im.width) // 2, (i // cols) * h + (h - im.height) // 2
        lienzo.paste(im, (cx, cy), im)
    dst.parent.mkdir(parents=True, exist_ok=True)
    lienzo.save(dst, compress_level=3)


def main():
    for tema in ("oscuro", "claro"):
        base = RAIZ / tema
        if not base.exists():
            continue
        todas = []
        for carpeta in sorted(p for p in base.iterdir() if p.is_dir()):
            pngs = sorted(carpeta.glob("*.png"))
            for p in pngs:
                sticker(p, RAIZ / "stickers" / tema / carpeta.name / p.name)
            todas += pngs
            hoja(pngs, RAIZ / "conjunto" / f"{tema}_{carpeta.name}.png", FONDOS[tema], cols=3)
        hoja(todas, RAIZ / "conjunto" / f"{tema}_todas.png", FONDOS[tema], cols=8)
        print(tema, len(todas), "piezas")


main()
