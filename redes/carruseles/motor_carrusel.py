#!/usr/bin/env python3
"""Motor de carruseles de Instagram de Co.De Aerospace: una especificación JSON → láminas PNG 1080×1350.

Diseño (sistema fijo, el contenido cambia):
  · Fondo PANORÁMICO: un solo paisaje espacial procedural (los entornos de las diapositivas, ver
    animaciones/fondos_espaciales.py) del ancho de todo el carrusel, cortado en láminas. Al deslizar,
    el horizonte y las estrellas continúan: invita a seguir pasando.
  · Rejilla: márgenes de 84 px, cabecera (emblema + CO.DE AEROSPACE + contador) y pie (cuenta, barra de
    avance y «DESLIZA»). El texto nunca entra en los 84 px del borde.
  · Tipografía oficial de codeaerospace.com: Rajdhani (títulos), DM Sans (texto), Space Mono (etiquetas
    y cifras chicas), Orbitron (cifras grandes); Montserrat para la marca (la del logo).
  · Paleta del tema Órbita: tinta #F1F5F9, tenue #93A4BD, cian #00D9FF, turquesa #37CFA0, ámbar #F59E0B.
  · Énfasis en línea: [[texto]] sale en cian; **texto** en negrita.

Tipos de lámina: portada · texto · dato · lista · pasos · comparacion · cita · imagen · cierre.
Esquema completo y reglas de contenido: redes/carruseles/ESQUEMA.md.

Uso:
  python3 motor_carrusel.py specs/serie/id.json [...]      → exports/estudio/carruseles/<serie>/<id>/
  python3 motor_carrusel.py --todos                         → todas las specs de redes/carruseles/specs/
  python3 motor_carrusel.py --validar specs/...             → solo valida (sin render)
  python3 motor_carrusel.py --estricto specs/...            → falla si algún texto no cabe ni al tamaño mínimo
"""
import json
import re
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "animaciones"))
SPECS = REPO / "redes" / "carruseles" / "specs"
SALIDA = REPO / "exports" / "estudio" / "carruseles"
CACHE_FONDOS = REPO / "exports" / "estudio" / "_fondos"
FUENTES = Path.home() / ".local/share/fonts/codeaerospace"
MONTSERRAT = REPO / "studio/content/manim_extensions/fonts"
STICKERS = REPO / "exports/png/stickers_finales/t_orbita"
DERIVADOS = REPO / "marca/derivados"
LOGO = REPO / "marca/logo-codeaerospace-plata.png"

W, H = 1080, 1350
M = 84                                  # margen de seguridad
TINTA, TENUE, CIAN, TURQ, AMBAR, PANEL = "#F1F5F9", "#93A4BD", "#00D9FF", "#37CFA0", "#F59E0B", "#0A0E27"
CUENTA = "@co.de_aero"
SITIO = "codeaerospace.com"

F = {
    "titulo": FUENTES / "Rajdhani-Bold.ttf",
    "titulo_semi": FUENTES / "Rajdhani-SemiBold.ttf",
    "cuerpo": FUENTES / "DMSans-400.ttf",
    "cuerpo_medio": FUENTES / "DMSans-500.ttf",
    "cuerpo_negrita": FUENTES / "DMSans-700.ttf",
    "mono": FUENTES / "SpaceMono-Regular.ttf",
    "mono_negrita": FUENTES / "SpaceMono-Bold.ttf",
    "display": FUENTES / "Orbitron-700.ttf",
    "marca": MONTSERRAT / "Montserrat-SemiBold.ttf",
    "formula": Path("/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"),     # λ, Δ, √, subíndices
    "formula_txt": Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
}
# Las láminas con stickers de la tesis NO se publican (repositorio privado): se rechazan al validar.
PROHIBIDO_IMAGEN = ("tesis_", "CicloPADA", "CompuertasValidacion", "MargenAdaptativo", "PipelineCompuertas")


@lru_cache(maxsize=None)
def fuente(clave, tam):
    return ImageFont.truetype(str(F[clave]), int(tam))


def hex2rgb(h, a=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (a,)


# ── Fondo panorámico ──────────────────────────────────────────────────────────────────────────

def fondo_panoramico(tema, n, tipo="portada", var=0):
    """Paisaje de n láminas (n·1080 × 1350) con el entorno del tema (caché atómica en exports/estudio/_fondos)."""
    from fondos_a_medida import fondo_a_medida
    return Image.open(fondo_a_medida(tema, tipo, var, n * W, H)).convert("RGB")


def oscurecer(img, arriba=0.55, abajo=0.65, atenuar=0.22):
    """Degradados arriba (cabecera) y abajo (pie y texto) y una atenuación general (`atenuar`) para que las
    curvas y nodos de los fondos temáticos no compitan con el texto."""
    a = np.asarray(img, np.float32)
    y = np.linspace(0, 1, img.height)[:, None, None]
    k = (1 - atenuar) * (1 - arriba * np.clip(1 - y / 0.22, 0, 1) ** 1.6 - abajo * np.clip((y - 0.45) / 0.55, 0, 1) ** 1.4)
    return Image.fromarray(np.clip(a * k, 0, 255).astype(np.uint8))


def vidrio(img, caja, radio=30, oscuro=0.62, desenfoque=16, borde=CIAN, alfa_borde=90):
    """Panel de vidrio esmerilado: desenfoca y oscurece el fondo bajo `caja`, con borde fino cian."""
    x0, y0, x1, y1 = [int(v) for v in caja]
    region = img.crop((x0, y0, x1, y1)).filter(ImageFilter.GaussianBlur(desenfoque))
    region = Image.fromarray((np.asarray(region, np.float32) * (1 - oscuro) + np.array(hex2rgb(PANEL)[:3]) * oscuro * 0.6)
                             .clip(0, 255).astype(np.uint8))
    mascara = Image.new("L", region.size, 0)
    ImageDraw.Draw(mascara).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1), radio, fill=255)
    img.paste(region, (x0, y0), mascara)
    d = ImageDraw.Draw(img, "RGBA")
    d.rounded_rectangle((x0, y0, x1 - 1, y1 - 1), radio, outline=hex2rgb(borde, alfa_borde), width=2)


# ── Texto con énfasis y ajuste medido ────────────────────────────────────────────────────────

def _tokens(texto):
    """'Hola [[mundo]] **ya**' → [(palabra, estilo)] con estilo ∈ {'', 'acento', 'negrita'}."""
    salida = []
    for trozo in re.split(r"(\[\[.*?\]\]|\*\*.*?\*\*)", texto):
        if not trozo:
            continue
        estilo = "acento" if trozo.startswith("[[") else "negrita" if trozo.startswith("**") else ""
        limpio = trozo[2:-2] if estilo else trozo
        for i, p in enumerate(re.split(r"(\s+)", limpio)):
            if p and not p.isspace():
                salida.append((p, estilo))
            elif p and "\n" in p:
                salida.append(("\n", ""))
    return salida


@lru_cache(maxsize=None)
def _cmap(clave):
    from fontTools.ttLib import TTFont
    return set(TTFont(str(F[clave]), lazy=True).getBestCmap())


def _fuente_estilo(base, estilo, tam, palabra=""):
    """Fuente del token; si le faltan glifos (Δ, μ, ≈, subíndices en Rajdhani/Space Mono) cae a DejaVu."""
    clave = base
    if estilo == "negrita":
        clave = {"cuerpo": "cuerpo_negrita", "cuerpo_medio": "cuerpo_negrita", "titulo_semi": "titulo"}.get(base, base)
    if palabra and any(ord(c) not in _cmap(clave) for c in palabra):
        return fuente("formula_txt", tam)
    return fuente(clave, tam)


PEGADA = tuple(".,;:!?)…»”%")


def _sep(palabra, esp):
    """Espacio antes de `palabra` (cero si empieza con puntuación que va pegada)."""
    return 0.0 if palabra.startswith(PEGADA) else esp


def partir(texto, base, tam, ancho):
    """Líneas de tokens que caben en `ancho` (medido con la fuente real)."""
    lineas, actual, x = [], [], 0.0
    esp = fuente(base, tam).getlength(" ")
    for palabra, estilo in _tokens(texto):
        if palabra == "\n":
            lineas.append(actual); actual, x = [], 0.0
            continue
        w = _fuente_estilo(base, estilo, tam, palabra).getlength(palabra)
        if actual and x + _sep(palabra, esp) + w > ancho:
            lineas.append(actual); actual, x = [], 0.0
        x += (_sep(palabra, esp) if actual else 0) + w
        actual.append((palabra, estilo))
    if actual:
        lineas.append(actual)
    return lineas


def ajustar(texto, base, tam_max, ancho, alto, interlineado=1.18, tam_min=18):
    """El tamaño más grande (≤ tam_max) con el que el texto cabe en ancho×alto."""
    tam = tam_max
    while tam > tam_min:
        lineas = partir(texto, base, tam, ancho)
        if len(lineas) * tam * interlineado <= alto:
            return tam, lineas
        tam -= 2
    return tam_min, partir(texto, base, tam_min, ancho)


AVISOS_RENDER = []          # textos que no cupieron ni al tamaño mínimo (se informan al final del render)


def medir(texto, base, tam_max, ancho, alto, interlineado=1.18, mayus=False):
    """(alto usado, tamaño) sin dibujar."""
    if mayus:
        texto = texto.upper()
    tam, lineas = ajustar(texto, base, tam_max, ancho, alto, interlineado)
    return len(lineas) * tam * interlineado, tam


def escribir(img, xy, texto, base, tam_max, ancho, alto, color=TINTA, interlineado=1.18, alinear="izq",
             mayus=False, acento=CIAN, tracking=0.0, sombra=True):
    """Escribe ajustando; devuelve (alto usado, tamaño). `xy` es la esquina superior izquierda de la caja.

    La sombra se calcula solo en el recuadro del texto (no en toda la lámina): rápido."""
    if mayus:
        texto = texto.upper()
    tam, lineas = ajustar(texto, base, tam_max, ancho, alto, interlineado)
    usado = len(lineas) * tam * interlineado
    if usado > alto + 1:
        AVISOS_RENDER.append(f"no cabe: «{texto[:40]}…» ({int(usado)} px en {int(alto)})")
    pad = int(tam * 0.6) + 8
    x0, y0 = xy
    caja = (max(0, int(x0 - pad)), max(0, int(y0 - pad)), min(img.width, int(x0 + ancho + pad)),
            min(img.height, int(y0 + usado + tam * 0.4 + pad)))
    capa = Image.new("RGBA", (caja[2] - caja[0], caja[3] - caja[1]), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa, "RGBA")
    ox, oy = caja[0], caja[1]
    y = y0
    esp = fuente(base, tam).getlength(" ") + tracking * tam
    for linea in lineas:
        anchos = [_fuente_estilo(base, e, tam, p).getlength(p) + tracking * tam * (len(p) - 1) for p, e in linea]
        total = sum(anchos) + sum(_sep(p, esp) for p, _ in linea[1:])
        x = x0 + (ancho - total) / 2 if alinear == "centro" else x0 + ancho - total if alinear == "der" else x0
        for k, ((p, e), w) in enumerate(zip(linea, anchos)):
            if k:
                x += _sep(p, esp)
            f = _fuente_estilo(base, e, tam, p)
            col = acento if e == "acento" else color
            if tracking:
                cx = x
                for ch in p:
                    d.text((cx - ox, y - oy), ch, font=f, fill=hex2rgb(col))
                    cx += f.getlength(ch) + tracking * tam
            else:
                d.text((x - ox, y - oy), p, font=f, fill=hex2rgb(col))
            x += w
        y += tam * interlineado
    region = img.crop(caja).convert("RGBA")
    if sombra:
        sm = Image.new("RGBA", capa.size, (2, 4, 12, 0))
        sm.putalpha(capa.getchannel("A").filter(ImageFilter.GaussianBlur(max(4, tam * 0.16))).point(lambda v: int(v * 0.85)))
        region.alpha_composite(sm)
    region.alpha_composite(capa)
    img.paste(region.convert("RGB"), caja[:2])
    return usado, tam


# ── Imágenes ─────────────────────────────────────────────────────────────────────────────────

def cargar_imagen(ref):
    if ref in ("logo",):
        return Image.open(LOGO).convert("RGBA")
    if ref.startswith("marca:"):
        return Image.open(DERIVADOS / f"{Path(ref[6:]).name}.png").convert("RGBA")
    if ref.startswith("sticker:"):
        rel = ref[8:]
        if any(p in rel for p in PROHIBIDO_IMAGEN) or ".." in rel:
            raise ValueError(f"imagen no publicable: {ref}")
        return Image.open(STICKERS / f"{rel}.png").convert("RGBA")
    raise ValueError(f"imagen desconocida «{ref}» (usa sticker:, marca: o logo)")


def pegar_ajustado(img, im, caja, alinear="centro", sombra=True, ampliar=True):
    """Pega `im` lo más grande posible dentro de `caja` (también AMPLÍA los stickers chicos)."""
    x0, y0, x1, y1 = [int(v) for v in caja]
    if x1 - x0 < 20 or y1 - y0 < 20:
        return (x0, y0, x0, y0)
    k = min((x1 - x0) / im.width, (y1 - y0) / im.height)
    if not ampliar:
        k = min(k, 1.0)
    im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.LANCZOS)
    x = int(x0 + (x1 - x0 - im.width) / 2) if alinear == "centro" else int(x0)
    y = int(y0 + (y1 - y0 - im.height) / 2)
    if sombra:
        halo = Image.new("RGBA", im.size, (0, 217, 255, 0))
        halo.putalpha(im.getchannel("A").filter(ImageFilter.GaussianBlur(14)).point(lambda v: int(v * 0.35)))
        img.paste(halo, (x, y), halo)
    img.paste(im, (x, y), im)
    return (x, y, x + im.width, y + im.height)


# ── Marco común ───────────────────────────────────────────────────────────────────────────────

def marco(img, i, n, final=False, acento=CIAN):
    d = ImageDraw.Draw(img, "RGBA")
    emb = Image.open(DERIVADOS / "simbolo-plata.png").convert("RGBA")
    emb.thumbnail((70, 70), Image.LANCZOS)
    img.paste(emb, (M, 52), emb)
    d.text((M + emb.width + 16, 52 + emb.height / 2), "CO.DE AEROSPACE", font=fuente("marca", 25),
           fill=hex2rgb(TINTA, 235), anchor="lm")
    cont = f"{i + 1:02d} / {n:02d}"
    d.text((W - M, 52 + emb.height / 2), cont, font=fuente("mono", 25), fill=hex2rgb(TENUE), anchor="rm")
    yb = H - 70
    d.text((M, yb), CUENTA if not final else SITIO, font=fuente("mono", 24), fill=hex2rgb(TENUE), anchor="lm")
    seg_w, gap = 26, 8
    total = n * seg_w + (n - 1) * gap
    x = (W - total) / 2
    for k in range(n):
        col = hex2rgb(acento) if k == i else hex2rgb(TINTA, 70)
        d.rounded_rectangle((x, yb - 3, x + seg_w, yb + 3), 3, fill=col)
        x += seg_w + gap
    if not final:
        d.text((W - M - 30, yb), "DESLIZA", font=fuente("mono_negrita", 24), fill=hex2rgb(acento), anchor="rm")
        ax = W - M - 22
        d.line((ax, yb, ax + 20, yb), fill=hex2rgb(acento), width=3)
        d.polygon([(ax + 22, yb), (ax + 12, yb - 7), (ax + 12, yb + 7)], fill=hex2rgb(acento))


SELLOS = {"ilustracion": "ILUSTRACIÓN", "simulacion": "SIMULACIÓN", "grabacion": "GRABACIÓN IQ",
          "beta": "BETA", "meta": "META, NO HECHO", "mito": "MITO", "realidad": "REALIDAD",
          "dato": "DATO REAL"}


def sello(img, clave):
    """Etiqueta de rigor en la esquina inferior derecha de la zona de contenido (ámbar)."""
    texto = SELLOS.get(clave, clave.upper())
    d = ImageDraw.Draw(img, "RGBA")
    f = fuente("mono_negrita", 22)
    w = f.getlength(texto) + 40
    x1, y1 = W - M, H - 112
    d.rounded_rectangle((x1 - w, y1 - 44, x1, y1), 22, outline=hex2rgb(AMBAR), width=2, fill=hex2rgb(PANEL, 200))
    d.text((x1 - w / 2, y1 - 22), texto, font=f, fill=hex2rgb(AMBAR), anchor="mm")


ZONA = (M, 170, W - M, H - 130)        # caja útil de contenido (entre cabecera y pie)
X0, Y0, X1, Y1 = ZONA
ANCHO = X1 - X0


# ── Láminas ───────────────────────────────────────────────────────────────────────────────────
# Las láminas de contenido reciben `dy` (desplazamiento vertical) y devuelven la última y usada: el
# render las dibuja una vez en una copia para medir y otra centrada en la zona (sin mitad vacía abajo).

def kicker(img, y, texto, color=CIAN):
    d = ImageDraw.Draw(img, "RGBA")
    d.line((M, y + 15, M + 38, y + 15), fill=hex2rgb(color), width=3)
    d.ellipse((M + 38, y + 10, M + 48, y + 20), fill=hex2rgb(color))
    escribir(img, (M + 62, y), texto, "mono_negrita", 26, ANCHO - 62, 40, color, mayus=True, tracking=0.08)


def cabeza(img, s, y, tam_titulo=82, alto_titulo=260):
    """numero · kicker · título; devuelve la y siguiente."""
    if s.get("numero"):
        ImageDraw.Draw(img, "RGBA").text((M, y - 8), s["numero"], font=fuente("titulo", 96), fill=hex2rgb(CIAN, 235))
        y += 104
    if s.get("kicker"):
        kicker(img, y, s["kicker"]); y += 58
    if s.get("titulo"):
        h, _ = escribir(img, (M, y), s["titulo"], "titulo", tam_titulo, ANCHO, alto_titulo, TINTA, interlineado=1.02)
        y += h + 34
    return y


def cuerpo_vidrio(img, y, texto, alto_max, tam=46):
    """Texto en panel de vidrio a la medida; devuelve la y siguiente."""
    h, _ = medir(texto, "cuerpo", tam, ANCHO - 72, alto_max - 64, 1.36)
    vidrio(img, (M - 4, y, W - M + 4, y + h + 60))
    escribir(img, (M + 36, y + 30), texto, "cuerpo", tam, ANCHO - 72, alto_max - 64, TINTA, interlineado=1.36)
    return y + h + 60


def l_portada(img, s, dy=0):
    if s.get("imagen"):
        pegar_ajustado(img, cargar_imagen(s["imagen"]), (X0 + 10, Y0 + 10, X1 - 10, Y0 + 540))
    elif s.get("logo", True):
        pegar_ajustado(img, cargar_imagen("logo"), (X0 + 220, Y0 + 30, X1 - 220, Y0 + 470))
    y = 770
    if s.get("kicker"):
        kicker(img, y - 70, s["kicker"])
    h, _ = escribir(img, (M, y), s["titulo"], "titulo", 118, ANCHO, 300, TINTA, interlineado=1.0)
    if s.get("subtitulo"):
        escribir(img, (M, y + h + 24), s["subtitulo"], "cuerpo", 40, ANCHO, 170, TENUE, interlineado=1.3)
    return Y1


def l_texto(img, s, dy=0):
    y = cabeza(img, s, Y0 + 20 + dy)
    if s.get("cuerpo"):
        y = cuerpo_vidrio(img, y, s["cuerpo"], (Y1 - y) * (0.55 if s.get("imagen") else 1.0)) + 24
    if s.get("imagen"):
        caja = pegar_ajustado(img, cargar_imagen(s["imagen"]), (M, y + 6, W - M, Y1 - 10 + dy * 0))
        y = caja[3]
    return y


def l_dato(img, s, dy=0):
    y = Y0 + 30 + dy
    if s.get("kicker"):
        kicker(img, y, s["kicker"]); y += 70
    d = ImageDraw.Draw(img, "RGBA")
    # Cifra en Rajdhani Bold: el 0 de Orbitron va tachado y se lee «Ø» (0.949 → Ø.949).
    cifra, tam = s["cifra"], 330
    while fuente("titulo", tam).getlength(cifra) > ANCHO and tam > 90:
        tam -= 6
    d.text((M - 8, y - tam * 0.16), cifra, font=fuente("titulo", tam), fill=hex2rgb(CIAN))
    y += tam * 0.92
    if s.get("unidad"):
        escribir(img, (M, y), s["unidad"], "mono_negrita", 40, ANCHO, 60, TURQ, mayus=True, tracking=0.06)
        y += 76
    h, _ = escribir(img, (M, y + 10), s["titulo"], "titulo", 72, ANCHO, 250, TINTA, interlineado=1.04)
    y += h + 44
    if s.get("nota"):
        h, _ = escribir(img, (M, y), s["nota"], "cuerpo", 34, ANCHO, Y1 - y, TENUE, interlineado=1.35)
        y += h
    return y


def l_lista(img, s, dy=0):
    y = cabeza(img, s, Y0 + 20 + dy, 80, 230)
    items = s["items"]
    disponible = Y1 - y - 40
    tam = 44
    for it in items:
        t = medir(it, "cuerpo", tam, ANCHO - 130, disponible / len(items) - 40, 1.3)[1]
        tam = min(tam, t)
    alturas = [medir(it, "cuerpo", tam, ANCHO - 130, 9999, 1.3)[0] for it in items]
    total = sum(alturas) + 46 * (len(items) - 1) + 64
    vidrio(img, (M - 4, y, W - M + 4, y + total))
    d = ImageDraw.Draw(img, "RGBA")
    yy = y + 32
    for it, hh in zip(items, alturas):
        cy = yy + tam * 0.62
        d.ellipse((M + 40, cy - 9, M + 58, cy + 9), outline=hex2rgb(CIAN), width=3)
        d.ellipse((M + 46, cy - 3, M + 52, cy + 3), fill=hex2rgb(CIAN))
        escribir(img, (M + 86, yy), it, "cuerpo", tam, ANCHO - 130, hh + 4, TINTA, interlineado=1.3)
        yy += hh + 46
    return y + total


def l_pasos(img, s, dy=0):
    y = cabeza(img, s, Y0 + 20 + dy, 80, 230) + 6
    pasos = s["pasos"]
    d = ImageDraw.Draw(img, "RGBA")
    xl = M + 34
    ancho_t = W - xl - 60 - M
    alturas = []
    for p in pasos:
        ht = medir(p["t"], "titulo_semi", 52, ancho_t, 130, 1.0)[0]
        hd = medir(p["d"], "cuerpo", 36, ancho_t, 160, 1.3)[0] + 8 if p.get("d") else 0
        alturas.append(max(64, ht + hd) + 40)
    if sum(alturas) > Y1 - y:                     # no cabe: reparte la altura disponible
        k = (Y1 - y) / sum(alturas)
        alturas = [a * k for a in alturas]
    ys = [y]
    for a in alturas[:-1]:
        ys.append(ys[-1] + a)
    d.line((xl, y + 30, xl, ys[-1] + 30), fill=hex2rgb(CIAN, 120), width=3)
    for k, (p, yy) in enumerate(zip(pasos, ys)):
        d.ellipse((xl - 26, yy + 4, xl + 26, yy + 56), fill=hex2rgb(PANEL), outline=hex2rgb(CIAN), width=3)
        d.text((xl, yy + 30), str(k + 1), font=fuente("mono_negrita", 28), fill=hex2rgb(CIAN), anchor="mm")
        hh, _ = escribir(img, (xl + 60, yy), p["t"], "titulo_semi", 52, ancho_t, 130, TINTA, interlineado=1.0)
        if p.get("d"):
            escribir(img, (xl + 60, yy + hh + 8), p["d"], "cuerpo", 36, ancho_t, alturas[k] - hh - 40, TENUE, interlineado=1.3)
    return ys[-1] + alturas[-1]


def l_comparacion(img, s, dy=0):
    """Dos tarjetas APILADAS a todo el ancho (letra grande; ideal para mito/realidad, antes/después)."""
    y = cabeza(img, s, Y0 + 20 + dy, 78, 220)
    lados = (s["izq"], s["der"])
    disponible = (Y1 - y - 30) / 2
    for j, lado in enumerate(lados):
        color = TENUE if j == 0 else CIAN
        ht = medir(lado["t"], "titulo", 54, ANCHO - 72, 120, 1.0)[0]
        tam = 48
        for it in lado["items"]:
            tam = min(tam, medir(it, "cuerpo", tam, ANCHO - 120, (disponible - ht - 80) / max(1, len(lado["items"])), 1.28)[1])
        alturas = [medir(it, "cuerpo", tam, ANCHO - 120, 999, 1.28)[0] for it in lado["items"]]
        alto = 30 + ht + 18 + sum(alturas) + 20 * len(alturas) + 20
        vidrio(img, (M - 4, y, W - M + 4, y + alto), borde=color, alfa_borde=120 if j else 70)
        escribir(img, (M + 36, y + 30), lado["t"], "titulo", 54, ANCHO - 72, 120, color, interlineado=1.0)
        yy = y + 30 + ht + 18
        d = ImageDraw.Draw(img, "RGBA")
        for it, hh in zip(lado["items"], alturas):
            d.rounded_rectangle((M + 36, yy + tam * 0.42, M + 52, yy + tam * 0.42 + 16), 4, fill=hex2rgb(color))
            escribir(img, (M + 72, yy), it, "cuerpo", tam, ANCHO - 120, hh + 4, TINTA, interlineado=1.28)
            yy += hh + 20
        y += alto + 28
    return y


def l_termino(img, s, dy=0):
    """Glosario: término grande, nombre completo, definición en vidrio, ejemplo y (opcional) imagen."""
    y = Y0 + 20 + dy
    if s.get("kicker"):
        kicker(img, y, s["kicker"]); y += 58
    tam = 150
    while fuente("titulo", tam).getlength(s["termino"]) > ANCHO and tam > 60:
        tam -= 6
    ImageDraw.Draw(img, "RGBA").text((M - 4, y - tam * 0.12), s["termino"], font=fuente("titulo", tam), fill=hex2rgb(CIAN))
    y += tam * 0.98
    if s.get("nombre"):
        h, _ = escribir(img, (M, y), s["nombre"], "mono", 30, ANCHO, 90, TENUE, interlineado=1.25)
        y += h + 26
    y = cuerpo_vidrio(img, y, s["definicion"], (Y1 - y) * (0.5 if s.get("imagen") else 0.75), tam=44) + 28
    if s.get("ejemplo"):
        escribir(img, (M, y), "EJEMPLO", "mono_negrita", 24, ANCHO, 40, TURQ, tracking=0.12)
        h, _ = escribir(img, (M, y + 42), s["ejemplo"], "cuerpo", 36, ANCHO, 200, TINTA, interlineado=1.32)
        y += 42 + h + 20
    if s.get("imagen"):
        y = pegar_ajustado(img, cargar_imagen(s["imagen"]), (M, y + 6, W - M, Y1 - 10))[3]
    return y


def l_formula(img, s, dy=0):
    """Un cálculo a la vista: fórmula grande, sustitución paso a paso y resultado destacado."""
    y = cabeza(img, s, Y0 + 20 + dy, 76, 220)
    tam = 110
    while fuente("formula", tam).getlength(s["formula"]) > ANCHO - 60 and tam > 40:
        tam -= 4
    alto_f = tam * 1.5 + 40
    vidrio(img, (M - 4, y, W - M + 4, y + alto_f), borde=CIAN, alfa_borde=130)
    ImageDraw.Draw(img, "RGBA").text((W / 2, y + alto_f / 2), s["formula"], font=fuente("formula", tam),
                                      fill=hex2rgb(TINTA), anchor="mm")
    y += alto_f + 34
    for p in s.get("pasos", []):
        h, _ = escribir(img, (M + 20, y), p, "formula_txt", 36, ANCHO - 40, 120, TINTA, interlineado=1.25)
        y += h + 16
    if s.get("resultado"):
        y += 10
        h, _ = escribir(img, (M, y), s["resultado"], "titulo", 72, ANCHO, 200, CIAN, interlineado=1.0)
        y += h + 20
    if s.get("nota"):
        h, _ = escribir(img, (M, y), s["nota"], "cuerpo", 32, ANCHO, Y1 - y, TENUE, interlineado=1.32)
        y += h
    return y


def _ticks_bonitos(lo, hi, n=5):
    """Marcas de eje en números redondos (1, 2, 2.5, 5 × 10^k)."""
    rango = max(hi - lo, 1e-9)
    paso = rango / max(n - 1, 1)
    mag = 10 ** np.floor(np.log10(paso))
    paso = min((m * mag for m in (1, 2, 2.5, 5, 10) if m * mag >= paso), default=10 * mag)
    ini = np.ceil(lo / paso) * paso
    return [round(float(v), 10) for v in np.arange(ini, hi + paso * 0.01, paso)]


def _fmt_x(v, modo):
    if modo == "mmss":
        v = int(round(v))
        return f"{v // 60}:{v % 60:02d}"
    return f"{v:g}"


def l_grafica(img, s, dy=0):
    """Gráfica de UNA serie (línea): título que dice qué se grafica (sin leyenda), ejes con marcas redondas,
    cuadrícula discreta, marcador con anillo del color del panel y etiquetas solo en los puntos clave.
    Campos: x, y (listas), y_escala (divide y), y_unidad, y_etiqueta, x_etiqueta, x_modo ("mmss"|""),
    marcas [{x, texto, lado: "arriba"|"abajo"|"izq"|"der"}], nota."""
    y = cabeza(img, s, Y0 + 20 + dy, 76, 220)
    SS = 2
    esc = float(s.get("y_escala", 1.0))
    xs = np.asarray(s["x"], float)
    ys = np.asarray(s["y"], float) / esc
    alto_panel = min(840, int(Y1 - y - (170 if s.get("nota") else 30)))
    caja = (M - 4, int(y), W - M + 4, int(y) + alto_panel)
    vidrio(img, caja)
    cx0, cy0, cx1, cy1 = caja
    ml, mr, mt, mb = 118, 46, 56, 92                       # márgenes internos del panel
    px0, px1, py0, py1 = cx0 + ml, cx1 - mr, cy0 + mt, cy1 - mb
    lo, hi = float(ys.min()), float(ys.max())
    pad = (hi - lo) * 0.20                                  # holgura arriba y abajo para las etiquetas
    ty = _ticks_bonitos(lo - pad, hi + pad, 5)
    ymin, ymax = min(ty[0], lo - pad), max(ty[-1], hi + pad)
    xmin, xmax = float(xs.min()), float(xs.max())
    fx = lambda v: px0 + (v - xmin) / (xmax - xmin) * (px1 - px0)
    fy = lambda v: py1 - (v - ymin) / (ymax - ymin) * (py1 - py0)
    modo = s.get("x_modo", "")
    paso_x = 60 if modo == "mmss" and (xmax - xmin) > 150 else None
    tx = list(np.arange(0, xmax + 0.1, paso_x)) if paso_x else _ticks_bonitos(xmin, xmax, 6)

    capa = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(capa, "RGBA")
    S_ = lambda p: (p[0] * SS, p[1] * SS)
    gris = hex2rgb(TINTA, 40)
    for v in ty:                                           # cuadrícula: hairline discreta
        yy = fy(v)
        d.line([S_((px0, yy)), S_((px1, yy))], fill=hex2rgb(TINTA, 150 if abs(v) < 1e-9 else 40), width=SS * (2 if abs(v) < 1e-9 else 1))
    for v in tx:
        d.line([S_((fx(v), py1)), S_((fx(v), py1 + 10))], fill=hex2rgb(TENUE, 160), width=SS)
    pts = [S_((fx(a), fy(b))) for a, b in zip(xs, ys)]
    d.line(pts, fill=hex2rgb(CIAN), width=SS * 4, joint="curve")             # línea de 4 px a 1080 (≈ 2 px de diseño)
    for a, b in zip(pts[:1] + pts[-1:], [0, 0]):
        pass
    marcas = s.get("marcas", [])
    for m in marcas:                                       # marcador ≥ 8 px con anillo del color del panel
        i = int(np.argmin(np.abs(xs - m["x"])))
        cxm, cym = fx(xs[i]), fy(ys[i])
        d.ellipse([S_((cxm - 12, cym - 12)), S_((cxm + 12, cym + 12))], fill=hex2rgb(PANEL))
        d.ellipse([S_((cxm - 8, cym - 8)), S_((cxm + 8, cym + 8))], fill=hex2rgb(CIAN))
    cap = capa.resize((W, H), Image.LANCZOS)
    base = img.convert("RGBA")
    base.alpha_composite(cap)
    img.paste(base.convert("RGB"))
    d2 = ImageDraw.Draw(img, "RGBA")
    f_t = fuente("mono", 22)
    for v in ty:
        d2.text((px0 - 16, fy(v)), f"{v:g}", font=f_t, fill=hex2rgb(TENUE), anchor="rm")
    for v in tx:
        d2.text((fx(v), py1 + 22), _fmt_x(v, modo), font=f_t, fill=hex2rgb(TENUE), anchor="mt")
    if s.get("y_etiqueta"):
        escribir(img, (cx0 + 28, cy0 + 14), s["y_etiqueta"], "mono_negrita", 22, cx1 - cx0 - 56, 34, TENUE, tracking=0.06, sombra=False)
    if s.get("x_etiqueta"):
        d2.text(((px0 + px1) / 2, cy1 - 30), s["x_etiqueta"], font=fuente("mono_negrita", 22), fill=hex2rgb(TENUE), anchor="mm")
    for m in marcas:                                       # etiquetas directas en tinta (nunca en el color de la serie)
        i = int(np.argmin(np.abs(xs - m["x"])))
        cxm, cym = fx(xs[i]), fy(ys[i])
        lado = m.get("lado", "arriba")
        f_m = fuente("cuerpo_negrita", 28)
        tw = f_m.getlength(m["texto"])
        off = {"arriba": (0, -34), "abajo": (0, 34), "izq": (-26 - tw / 2, 0), "der": (26 + tw / 2, 0)}[lado]
        tx_, ty_ = min(max(cxm + off[0], px0 + tw / 2 + 6), px1 - tw / 2 - 6), cym + off[1] + m.get("dy", 0)
        d2.text((tx_, ty_), m["texto"], font=f_m, fill=hex2rgb(TINTA), anchor="mm")
    fin = int(y) + alto_panel + 22
    if s.get("nota"):
        h, _ = escribir(img, (M, fin), s["nota"], "cuerpo", 30, ANCHO, Y1 - fin, TENUE, interlineado=1.32)
        fin += h
    return fin


def l_cita(img, s, dy=0):
    d = ImageDraw.Draw(img, "RGBA")
    d.text((M - 8, Y0 + 40), "“", font=fuente("titulo", 260), fill=hex2rgb(CIAN, 200))
    h, _ = escribir(img, (M, Y0 + 300), s["frase"], "titulo_semi", 84, ANCHO, 560, TINTA, interlineado=1.08)
    if s.get("autor"):
        d.line((M, Y0 + 330 + h, M + 60, Y0 + 330 + h), fill=hex2rgb(CIAN), width=3)
        escribir(img, (M, Y0 + 350 + h), s["autor"], "mono", 28, ANCHO, 90, TENUE, interlineado=1.3)
    return Y1


def l_imagen(img, s, dy=0):
    y = cabeza(img, s, Y0 + 20, 76, 200)
    pie_h = medir(s["pie"], "cuerpo", 36, ANCHO, 200, 1.32)[0] + 20 if s.get("pie") else 0
    caja = pegar_ajustado(img, cargar_imagen(s["imagen"]), (M - 30, y, W - M + 30, Y1 - pie_h - 10))
    if s.get("pie"):
        escribir(img, (M, caja[3] + 20), s["pie"], "cuerpo", 36, ANCHO, 200, TENUE, interlineado=1.32)
    return Y1


def l_cierre(img, s, dy=0):
    pegar_ajustado(img, cargar_imagen("logo"), (X0 + 250, Y0 + 20, X1 - 250, Y0 + 400))
    y = Y0 + 450
    h, _ = escribir(img, (M, y), s["titulo"], "titulo", 84, ANCHO, 240, TINTA, interlineado=1.02, alinear="centro")
    y += h + 30
    if s.get("texto"):
        hh, _ = escribir(img, (M + 30, y), s["texto"], "cuerpo", 38, ANCHO - 60, 160, TENUE, interlineado=1.32, alinear="centro")
        y += hh + 34
    chips = s.get("cta", ["Guárdalo", "Compártelo", "Síguenos"])
    f = fuente("mono_negrita", 26)
    anchos = [f.getlength(c.upper()) + 56 for c in chips]
    total = sum(anchos) + 18 * (len(chips) - 1)
    x = (W - total) / 2
    d = ImageDraw.Draw(img, "RGBA")
    for c, w in zip(chips, anchos):
        d.rounded_rectangle((x, y, x + w, y + 62), 31, outline=hex2rgb(CIAN), width=3, fill=hex2rgb(PANEL, 170))
        d.text((x + w / 2, y + 31), c.upper(), font=f, fill=hex2rgb(CIAN), anchor="mm")
        x += w + 18
    return Y1


LAMINAS = {"portada": l_portada, "texto": l_texto, "dato": l_dato, "lista": l_lista, "pasos": l_pasos,
           "comparacion": l_comparacion, "termino": l_termino, "formula": l_formula, "grafica": l_grafica, "cita": l_cita,
           "imagen": l_imagen, "cierre": l_cierre}
CENTRABLES = {"texto", "dato", "lista", "pasos", "comparacion", "termino", "formula", "grafica"}
REQUERIDOS = {"portada": ["titulo"], "texto": ["titulo"], "dato": ["cifra", "titulo"], "lista": ["titulo", "items"],
              "pasos": ["titulo", "pasos"], "comparacion": ["titulo", "izq", "der"], "termino": ["termino", "definicion"],
              "formula": ["formula"], "grafica": ["titulo", "x", "y"], "cita": ["frase"], "imagen": ["imagen"], "cierre": ["titulo"]}


# ── Validación ────────────────────────────────────────────────────────────────────────────────

def validar(spec):
    errores, avisos = [], []
    for k in ("id", "serie", "laminas", "fuentes", "pie_texto"):
        if k not in spec:
            errores.append(f"falta «{k}»")
    lams = spec.get("laminas", [])
    if not 3 <= len(lams) <= 10:
        errores.append(f"{len(lams)} láminas (usa de 3 a 10)")
    if lams and lams[0].get("tipo") != "portada":
        avisos.append("la primera lámina no es portada")
    if lams and lams[-1].get("tipo") != "cierre":
        avisos.append("la última lámina no es cierre")
    for i, l in enumerate(lams):
        t = l.get("tipo")
        if t not in LAMINAS:
            errores.append(f"lámina {i + 1}: tipo desconocido «{t}»")
            continue
        for k in REQUERIDOS[t]:
            if k not in l:
                errores.append(f"lámina {i + 1} ({t}): falta «{k}»")
        img = l.get("imagen", "")
        if img and any(p in img for p in PROHIBIDO_IMAGEN):
            errores.append(f"lámina {i + 1}: imagen de la tesis (privada) «{img}»")
        if img.startswith("sticker:") and not (STICKERS / f"{img[8:]}.png").exists():
            errores.append(f"lámina {i + 1}: no existe el sticker «{img}»")
        if t == "grafica" and (len(l.get("x", [])) != len(l.get("y", [])) or len(l.get("x", [])) < 10):
            errores.append(f"lámina {i + 1} (grafica): x e y deben tener la misma longitud (≥ 10 puntos)")
        if t == "lista" and not 2 <= len(l.get("items", [])) <= 5:
            avisos.append(f"lámina {i + 1}: lista de {len(l.get('items', []))} ítems (mejor 2–5)")
        procedencia = l.get("nota", "") + " " + " ".join(spec.get("cuidado", []))
        if t == "dato" and not re.search(r"20\d\d|est[áa]ndar|c[áa]lculo|calculad|de libro|presupuesto|constante", procedencia, re.I):
            avisos.append(f"lámina {i + 1}: cifra sin procedencia (fecha de verificación, o «estándar»/«cálculo» en la nota)")
        largo = len(l.get("titulo", ""))
        if largo > 70:
            avisos.append(f"lámina {i + 1}: título de {largo} caracteres (mejor ≤ 60)")
        if len(l.get("cuerpo", "")) > 330:
            avisos.append(f"lámina {i + 1}: cuerpo de {len(l['cuerpo'])} caracteres (mejor ≤ 280)")
    return errores, avisos


# ── Render ────────────────────────────────────────────────────────────────────────────────────

def renderizar(spec, destino=None):
    errores, avisos = validar(spec)
    if errores:
        raise ValueError(f"{spec.get('id')}: " + "; ".join(errores))
    lams = spec["laminas"]
    n = len(lams)
    f = spec.get("fondo", {})
    pano = fondo_panoramico(f.get("tema", "orbita"), n, f.get("tipo", "portada"), f.get("var", 0))
    destino = Path(destino or SALIDA / spec["serie"] / spec["id"])
    destino.mkdir(parents=True, exist_ok=True)
    rutas = []
    AVISOS_RENDER.clear()
    for i, l in enumerate(lams):
        img = oscurecer(pano.crop((i * W, 0, (i + 1) * W, H)), atenuar=f.get("atenuar", 0.22)).convert("RGB")
        dibujar = LAMINAS[l["tipo"]]
        if l["tipo"] in CENTRABLES:
            # 1ª pasada en una copia para medir dónde acaba; 2ª centrada (algo arriba del centro óptico)
            fin = dibujar(img.copy(), l, 0)
            dy = max(0.0, (Y1 - fin) * 0.42)
            n_av = len(AVISOS_RENDER)
            dibujar(img, l, dy)
            del AVISOS_RENDER[n_av:]                       # los avisos de la 2ª pasada repiten los de la 1ª
        else:
            dibujar(img, l)
        if l.get("sello"):
            sello(img, l["sello"])
        marco(img, i, n, final=(i == n - 1))
        ruta = destino / f"{spec['id']}_{i + 1:02d}.png"
        img.save(ruta, compress_level=6)
        rutas.append(ruta)
    avisos = avisos + [f"render: {a}" for a in dict.fromkeys(AVISOS_RENDER)]
    hoja(rutas, destino / f"{spec['id']}_hoja.jpg")
    (destino / f"{spec['id']}_pie.txt").write_text(spec["pie_texto"].strip() + "\n\nFuentes: " + "; ".join(spec["fuentes"]) + "\n",
                                                   encoding="utf-8")
    (destino / f"{spec['id']}_alt.txt").write_text(
        "Texto alternativo por lámina (Instagram → Configuración avanzada → Escribir texto alternativo):\n\n"
        + "\n".join(f"{i + 1:02d}. {alt_texto(l)}" for i, l in enumerate(lams)) + "\n", encoding="utf-8")
    if spec.get("cuidado"):
        (destino / f"{spec['id']}_CUIDADO.txt").write_text("\n".join("⚠️ " + c for c in spec["cuidado"]) + "\n", encoding="utf-8")
    return rutas, avisos


def _limpio(t):
    return re.sub(r"\[\[|\]\]|\*\*", "", t or "").strip()


def alt_texto(l):
    """Texto alternativo de una lámina (accesibilidad): lo que dice + qué muestra la imagen."""
    t = l["tipo"]
    partes = []
    if t == "dato":
        partes.append(f"{l['cifra']} {l.get('unidad', '')}".strip() + ": " + _limpio(l["titulo"]))
    elif t == "termino":
        partes.append(f"{l['termino']}" + (f" ({l['nombre']})" if l.get("nombre") else "") + ": " + _limpio(l["definicion"]))
    elif t == "formula":
        partes.append(f"Fórmula {l['formula']}" + (f", resultado {_limpio(l['resultado'])}" if l.get("resultado") else ""))
    elif t == "grafica":
        partes.append(f"Gráfica: {_limpio(l['titulo'])}. Eje horizontal {l.get('x_etiqueta', 'tiempo')}, eje vertical {l.get('y_etiqueta', '')}"
                      + ("; puntos señalados: " + "; ".join(_limpio(m["texto"]) for m in l.get("marcas", [])) if l.get("marcas") else ""))
    elif t == "cita":
        partes.append(f"Cita: «{_limpio(l['frase'])}»")
    elif t == "lista":
        partes.append(_limpio(l["titulo"]) + ": " + "; ".join(_limpio(i) for i in l["items"]))
    elif t == "pasos":
        partes.append(_limpio(l["titulo"]) + ": " + "; ".join(_limpio(p["t"]) for p in l["pasos"]))
    elif t == "comparacion":
        partes.append(_limpio(l["titulo"]) + f". {l['izq']['t']}: " + "; ".join(map(_limpio, l["izq"]["items"]))
                      + f". {l['der']['t']}: " + "; ".join(map(_limpio, l["der"]["items"])))
    else:
        partes.append(_limpio(l.get("titulo", "")))
        if l.get("cuerpo"):
            partes.append(_limpio(l["cuerpo"]))
    img = l.get("imagen", "")
    if img.startswith("sticker:"):
        nombre = re.sub(r"(?<!^)(?=[A-Z])", " ", img.split("/")[-1]).lower()
        partes.append(f"Ilustración animada: {nombre}")
    elif img in ("logo",) or (t in ("portada", "cierre") and not img):
        partes.append("Logo de Co.De Aerospace sobre un paisaje espacial")
    if l.get("sello"):
        partes.append(f"Etiqueta: {SELLOS.get(l['sello'], l['sello'])}")
    salida = ""
    for p in (x for x in partes if x):
        salida += ("" if not salida else (" " if salida.rstrip().endswith((".", "!", "?", "»", ":")) else ". ")) + p
    return salida


def hoja(rutas, salida, alto=600, cols=4):
    """Hoja de contacto en cuadrícula (4 columnas): se lee bien aunque el carrusel tenga 10 láminas."""
    ims = [Image.open(r) for r in rutas]
    ancho = int(alto * W / H)
    filas = (len(ims) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (ancho + 14) + 14, filas * (alto + 14) + 14), (5, 8, 16))
    for k, im in enumerate(ims):
        sheet.paste(im.resize((ancho, alto), Image.LANCZOS), (14 + (k % cols) * (ancho + 14), 14 + (k // cols) * (alto + 14)))
    sheet.save(salida, quality=86)


def expandir_variantes(spec):
    """Spec base + sus variantes A/B. Cada variante es un parche: {"sufijo": "b", "fondo": {...},
    "portada": {campos de la lámina 1}, "cierre": {campos de la última}}; hereda todo lo demás."""
    import copy
    salida = [spec]
    for v in spec.get("variantes", []):
        s2 = copy.deepcopy({k: x for k, x in spec.items() if k != "variantes"})
        s2["id"] = f"{spec['id']}-{v['sufijo']}"
        s2["variante_de"] = spec["id"]
        if "fondo" in v:
            s2["fondo"] = {**spec.get("fondo", {}), **v["fondo"]}
        if "portada" in v:
            s2["laminas"][0] = {**s2["laminas"][0], **v["portada"]}
        if "cierre" in v:
            s2["laminas"][-1] = {**s2["laminas"][-1], **v["cierre"]}
        if "pie_texto" in v:
            s2["pie_texto"] = v["pie_texto"]
        salida.append(s2)
    return salida


def main(args):
    solo_validar = "--validar" in args
    estricto = "--estricto" in args                 # texto que no cabe = error (para CI / antes de publicar)
    args = [a for a in args if a not in ("--validar", "--estricto")]
    if "--todos" in args or not args:
        rutas = sorted(SPECS.rglob("*.json"))
    else:
        rutas = [Path(a) for a in args]
    ok = 0
    for r in rutas:
        base = json.loads(Path(r).read_text(encoding="utf-8"))
        for spec in expandir_variantes(base):
            errores, avisos = validar(spec)
            if errores:
                print(f"✗ {r} [{spec.get('id')}]: " + "; ".join(errores))
                continue
            if not solo_validar:
                try:
                    _, avisos = renderizar(spec)
                except Exception as e:                       # un spec roto no detiene el lote
                    print(f"✗ {spec.get('id')}: {type(e).__name__}: {e}")
                    continue
                if estricto and any(a.startswith("render: no cabe") for a in avisos):
                    print(f"✗ {spec['serie']}/{spec['id']}: texto que no cabe → " + "; ".join(a for a in avisos if "no cabe" in a))
                    continue
            ok += 1
            print(f"✓ {spec['serie']}/{spec['id']}" + (f"  (avisos: {'; '.join(avisos)})" if avisos else ""))
    print(f"{ok} carruseles (de {len(rutas)} specs, contando variantes)")


if __name__ == "__main__":
    main(sys.argv[1:])
