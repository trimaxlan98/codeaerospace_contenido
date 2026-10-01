"""Fondos procedurales de los temas por materia de Co.De Aerospace (complementan a fondos_espaciales.py).

  robotica · electronica · calculo · fisica · electromagnetismo · lunar · marte · lanzamiento

Cada generador tiene la firma de los demás, `funcion(tipo, var, zona) → imagen HxWx3 float`, con tipo en
portada | seccion | contenido | video | cierre, y se registra en fondos_espaciales.GENERADORES al importar este módulo
(los temas de animaciones/temas/*.py lo importan). Reglas comunes:
  · el arte va a la derecha (la columna de texto de la portada, el cierre y las secciones queda libre);
  · en `contenido` y `video` la decoración es tenue y de esquina, para no pelear con el texto;
  · con `zona` (rectángulo del video) todo se funde a la base exacta en su borde.
Medidas en fracciones de ALTO (H) para que sirva igual a otra resolución (FONDOS_ESCALA=0.5 para iterar).
Vista previa: python3 fondos_tematicos.py [tema …]  → hoja de contacto en exports/presentaciones/espaciales/_fondos/
"""
import math
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy.ndimage import gaussian_filter, gaussian_filter1d

import fondos_espaciales as F

W, H = F.ANCHO, F.ALTO
E = H / 1800.0                       # grosor de trazo relativo al lienzo completo
XX, YY = F.XX, F.YY
rgb = F.rgb
FUENTES = Path.home() / ".local/share/fonts/codeaerospace"


# ---------------------------------------------------------------- utilidades de dibujo
@lru_cache(maxsize=None)
def _fuente(nombre, tam):
    for ruta in (FUENTES / f"{nombre}.ttf", Path("/usr/share/fonts/truetype/dejavu") / f"{nombre}.ttf"):
        if ruta.exists():
            return ImageFont.truetype(str(ruta), max(6, tam))
    return ImageFont.load_default()


def _l(d, s, pts, v=1.0, w=1.6):
    if len(pts) > 1:
        d.line([(x * s, y * s) for x, y in pts], fill=int(255 * min(v, 1)), width=max(1, round(w * E * s)), joint="curve")


def _c(d, s, cx, cy, r, v=1.0, w=1.6, lleno=False):
    box = [(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s]
    if lleno:
        d.ellipse(box, fill=int(255 * min(v, 1)))
    else:
        d.ellipse(box, outline=int(255 * min(v, 1)), width=max(1, round(w * E * s)))


def _r(d, s, x0, y0, x1, y1, v=1.0, w=1.6, lleno=False):
    box = [min(x0, x1) * s, min(y0, y1) * s, max(x0, x1) * s, max(y0, y1) * s]
    if lleno:
        d.rectangle(box, fill=int(255 * min(v, 1)))
    else:
        d.rectangle(box, outline=int(255 * min(v, 1)), width=max(1, round(w * E * s)))


def _arco(d, s, cx, cy, r, a0, a1, v=1.0, w=1.6):
    """Arco en grados (sentido horario en pantalla, 0° = derecha)."""
    a0, a1 = sorted((a0, a1))
    d.arc([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], a0, a1, fill=int(255 * min(v, 1)), width=max(1, round(w * E * s)))


def _txt(d, s, x, y, texto, tam, v=1.0, fuente="JetBrainsMono-400"):
    d.text((x * s, y * s), texto, font=_fuente(fuente, int(tam * E * s)), fill=int(255 * min(v, 1)))


def _punteada(d, s, pts, v=1.0, w=1.6, raya=14, hueco=10):
    """Polilínea discontinua (raya/hueco en px de lienzo a escala 1800)."""
    pts = np.asarray(pts, np.float64)
    seg = np.hypot(*np.diff(pts, axis=0).T)
    total = seg.sum()
    if total <= 0:
        return
    paso = (raya + hueco) * E
    acum = np.concatenate([[0], np.cumsum(seg)])
    t = 0.0
    while t < total:
        t1 = min(t + raya * E, total)
        muestras = np.linspace(t, t1, max(2, int((t1 - t) / (3 * E)) + 1))
        xs = np.interp(muestras, acum, pts[:, 0])
        ys = np.interp(muestras, acum, pts[:, 1])
        _l(d, s, list(zip(xs, ys)), v, w)
        t += paso


def cap(dibujo):
    return F.capa_lineas(dibujo)


def pintar(img, capa, color, fuerza=1.0, brillo=0.0):
    """Suma `capa` (HxW, 0-1) teñida de `color`; `brillo` añade un resplandor gaussiano de esa fuerza."""
    c = rgb(color)
    img += capa[..., None] * c * fuerza
    if brillo:
        img += gaussian_filter(capa, 10 * E)[..., None] * c * brillo


def base_color(hex_):
    return np.zeros((H, W, 3), np.float32) + rgb(hex_)


def fin(img, base_hex, tipo, zona, vig=0.4, estr=None):
    """Viñeta y, en `video`, fundido a la base exacta en el borde del rectángulo del video."""
    base = rgb(base_hex)
    img = img * F.vineta(vig)[..., None]
    extra = 0.0 if estr is None else estr
    if tipo == "video":
        return F._fundir_zona(img, base, extra, zona)
    return img + extra


def _masc_esq(cx, cy, radio_h):
    """Máscara radial 1→0 (radio en fracciones de H)."""
    return 1 - F.suave(0, radio_h * H, np.hypot(XX - cx, YY - cy))


def iso(f, n, ancho=1.3):
    """Curvas de nivel antialias de un campo escalar: (intensidad de líneas HxW, índice de nivel HxW)."""
    gy, gx = np.gradient(f)
    g = np.hypot(gx, gy) + 1e-9
    fr = f * n
    k = np.round(fr)
    dist = np.abs(fr - k) / (g * n)
    return np.exp(-(dist / (ancho * E + 0.35)) ** 2).astype(np.float32), k


def mezcla(a, b, t):
    return a * (1 - t) + b * t


def _rampa(t, colores):
    """Colores interpolados: t (HxW en 0-1) → HxWx3."""
    c = np.array([rgb(h) for h in colores], np.float32)
    x = np.clip(t, 0, 1) * (len(c) - 1)
    i = np.minimum(x.astype(int), len(c) - 2)
    w = (x - i)[..., None]
    return c[i] * (1 - w) + c[i + 1] * w


# ================================================================ ROBÓTICA
def _capsula(d, s, p, q, h, v=1.0, w=2.0):
    (x0, y0), (x1, y1) = p, q
    a = math.atan2(y1 - y0, x1 - x0)
    nx, ny = -math.sin(a) * h, math.cos(a) * h
    _l(d, s, [(x0 + nx, y0 + ny), (x1 + nx, y1 + ny)], v, w)
    _l(d, s, [(x0 - nx, y0 - ny), (x1 - nx, y1 - ny)], v, w)
    ad = math.degrees(a)
    _arco(d, s, x0, y0, h, ad + 90, ad + 270, v, w)
    _arco(d, s, x1, y1, h, ad - 90, ad + 90, v, w)


def _engrane(d, s, cx, cy, r, dientes=18, prof=0.13, rot=0.0, v=1.0, w=2.0, radios=6):
    pts = []
    for i in range(dientes * 4 + 1):
        a = rot + 2 * math.pi * i / (dientes * 4)
        rr = r * (1 + prof) if i % 4 in (1, 2) else r
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    _l(d, s, pts, v, w)
    _c(d, s, cx, cy, r * 0.78, v * 0.6, w * 0.7)
    _c(d, s, cx, cy, r * 0.22, v * 0.8, w)
    _c(d, s, cx, cy, r * 0.08, v, w, lleno=True)
    for k in range(radios):
        a = rot + 2 * math.pi * k / radios
        _l(d, s, [(cx + r * 0.25 * math.cos(a), cy + r * 0.25 * math.sin(a)), (cx + r * 0.78 * math.cos(a), cy + r * 0.78 * math.sin(a))], v * 0.5, w * 0.7)


def _brazo(d, s, base, largos, angulos, hw, v=1.0):
    pts = [base]
    for L, a in zip(largos, angulos):
        x, y = pts[-1]
        pts.append((x + L * math.cos(math.radians(a)), y + L * math.sin(math.radians(a))))
    for i in range(len(pts) - 1):
        _capsula(d, s, pts[i], pts[i + 1], hw[i], v, 2.2)
    for i, p in enumerate(pts[:-1]):
        _c(d, s, p[0], p[1], hw[i] * 1.28, v, 2.0)
        _c(d, s, p[0], p[1], hw[i] * 0.5, v * 0.85, 1.6)
        _c(d, s, p[0], p[1], hw[i] * 0.14, v, 1.6, lleno=True)
        if i:  # arco de ángulo de la articulación y cota
            a0, a1 = angulos[i - 1] + 180, angulos[i]
            _arco(d, s, p[0], p[1], hw[i] * 2.6, min(a0, a1 + 360), max(a0, a1 + 360) if a1 + 360 - a0 < 180 else a1, v * 0.7, 1.4)
    # pinza
    x, y = pts[-1]
    a = math.radians(angulos[-1])
    for sg in (-1, 1):
        nx, ny = -math.sin(a) * sg, math.cos(a) * sg
        _l(d, s, [(x, y), (x + nx * hw[-1] * 1.1, y + ny * hw[-1] * 1.1),
                  (x + nx * hw[-1] * 1.1 + math.cos(a) * hw[-1] * 1.5, y + ny * hw[-1] * 1.1 + math.sin(a) * hw[-1] * 1.5)], v, 2.2)
    return pts


def _hexagonos(d, s, r, v=0.6):
    dx, dy = 1.5 * r, math.sqrt(3) * r
    for i in range(int(W / dx) + 2):
        for j in range(int(H / dy) + 2):
            cx, cy = i * dx, j * dy + (dy / 2 if i % 2 else 0)
            _l(d, s, [(cx + r * math.cos(math.pi / 3 * k), cy + r * math.sin(math.pi / 3 * k)) for k in range(7)], v, 1.0)


def _bezier(p0, p1, p2, n=80):
    t = np.linspace(0, 1, n)[:, None]
    return ((1 - t) ** 2 * np.array(p0) + 2 * (1 - t) * t * np.array(p1) + t * t * np.array(p2))


def robotica(tipo, var=0, zona=None):
    """Taller robótico: grafito con metal cepillado, panal hexagonal, brazo articulado con cotas y engranes; acento naranja de seguridad."""
    BASE = "#0B0F14"
    acero, naranja = "#7DD3FC", "#FF7A1A"
    rng = np.random.default_rng(101 + var * 13)
    img = base_color(BASE)
    cep = gaussian_filter(rng.standard_normal((H, W)).astype(np.float32), (0.6, 45 * E))
    img += (cep / (cep.std() + 1e-6))[..., None] * np.array([0.004, 0.005, 0.007], np.float32)
    hexa = cap(lambda d, s: _hexagonos(d, s, 64 * E, 0.55))
    if tipo in ("portada", "cierre"):
        der = F.suave(0.42 * W, 0.95 * W, XX)
        pintar(img, hexa * (0.07 + 0.30 * der), acero)
        S = 1.0 if tipo == "portada" else 1.12
        base_xy = (1.34 * H if tipo == "portada" else 1.30 * H, 0.97 * H)
        largos, ang = (0.40 * H, 0.36 * H, 0.19 * H), ((-112, -38, 26) if tipo == "portada" else (-100, -55, 8))
        hw = (0.046 * H, 0.037 * H, 0.028 * H)
        pts = []

        def arte(d, s):
            pts.extend(_brazo(d, s, base_xy, largos, ang, hw, 0.95))
            _r(d, s, base_xy[0] - 0.13 * H, base_xy[1] - 0.05 * H, base_xy[0] + 0.13 * H, base_xy[1] + 0.05 * H, 0.9, 2.2)
            _engrane(d, s, 1.70 * H, 0.98 * H, 0.30 * H, 20, rot=0.1 * var, v=0.55)
            _engrane(d, s, 1.02 * H + 0.06 * H, 0.20 * H, 0.10 * H, 14, rot=0.3, v=0.5)
            ex, ey = base_xy[0] - 0.42 * H, base_xy[1] - 0.80 * H
            tray = _bezier((1.16 * H, 0.24 * H), (1.46 * H, 0.06 * H), (1.72 * H, 0.30 * H))
            _punteada(d, s, tray, 0.75, 1.8)
            for k in (0, 40, 79):
                x, y = tray[k]
                _r(d, s, x - 9 * E, y - 9 * E, x + 9 * E, y + 9 * E, 0.9, 1.8)
                _l(d, s, [(x - 22 * E, y), (x + 22 * E, y)], 0.6, 1.2)
                _l(d, s, [(x, y - 22 * E), (x, y + 22 * E)], 0.6, 1.2)
            _txt(d, s, tray[40][0] + 26 * E, tray[40][1] - 34 * E, "Q3 = 62.4°", 24, 0.8, "JetBrainsMono-400")

        c = cap(arte)
        pintar(img, c, acero, 0.95, 0.35)
        x, y = pts[-1]
        dx, dy = XX - x, YY - y
        img += (np.exp(-(dx * dx + dy * dy) / (2 * (0.05 * H) ** 2)) * 0.55 + np.exp(-(dx * dx + dy * dy) / (2 * (0.012 * H) ** 2)) * 0.9)[..., None] * rgb(naranja)
        # remates naranja en las articulaciones
        for p in pts[:-1]:
            dx, dy = XX - p[0], YY - p[1]
            img += (np.exp(-(dx * dx + dy * dy) / (2 * (0.010 * H) ** 2)) * 0.5)[..., None] * rgb(naranja)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        r0 = 0.46 * H
        cx, cy = W - 0.10 * H - 0.06 * H * (var % 3), 0.55 * H
        c = cap(lambda d, s: (_engrane(d, s, cx, cy, r0, 26, rot=0.2 * var, v=0.85, w=2.4),
                              _engrane(d, s, cx - 0.72 * r0 - 0.04 * H, cy + 0.74 * r0, 0.36 * r0, 16, rot=0.11 + 0.2 * var, v=0.7),
                              _arco(d, s, cx, cy, r0 * 1.22, 150, 240, 0.8, 1.6),
                              _arco(d, s, cx, cy, r0 * 1.30, 160, 230, 0.5, 1.2)))
        pintar(img, c, acero, 0.85, 0.3)
        n = cap(lambda d, s: [_arco(d, s, cx, cy, r0 * 1.12, 168 + k * 14, 172 + k * 14, 1.0, 5) for k in range(4)])
        pintar(img, n, naranja, 0.8, 0.4)
        pintar(img, hexa * (0.06 + 0.22 * F.suave(0.5 * W, W, XX)), acero)
        return fin(img, BASE, tipo, zona, 0.5)
    # contenido / video: panal y medio engrane en esquinas, muy tenues
    m1 = _masc_esq(W, 0, 0.55)
    m2 = _masc_esq(0, H, 0.45)
    pintar(img, hexa * (m1 * 0.26 + m2 * 0.16), acero)
    c = cap(lambda d, s: _engrane(d, s, W + 0.02 * H, 1.03 * H, 0.30 * H, 22, rot=0.3 * var, v=0.8))
    pintar(img, c, acero, 0.28)
    n = cap(lambda d, s: _arco(d, s, W + 0.02 * H, 1.03 * H, 0.345 * H, 180, 215, 1.0, 3.4))
    pintar(img, n, naranja, 0.55)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ ELECTRÓNICA
def _bus(d, s, x0, y0, n, g, curvas, x_fin, sentido=1, v=0.9, w=2.0, pad=True, rng=None, vias=True):
    """n pistas paralelas separadas g: salen de x0 y se doblan a 45° en cada (xa, dy); terminan en x_fin (mismas reglas de PCB)."""
    finales = []
    for k in range(n):
        y = y0 + k * g
        pts = [(x0, y)]
        for xa, dy in curvas:
            sg = 1 if dy > 0 else -1
            xk = xa - 0.4142 * g * k * sg
            pts += [(xk, y), (xk + abs(dy), y + dy)]
            y += dy
        pts.append((x_fin, y))
        pts = [(x0 + sentido * (px - x0), py) for px, py in pts]
        _l(d, s, pts, v, w)
        if pad:
            px, py = pts[-1]
            _c(d, s, px, py, 0.0095 * H, v, 2.0)
            _c(d, s, px, py, 0.0035 * H, v, 1.4, lleno=True)
        if vias and rng is not None and len(pts) > 3 and rng.random() < 0.5:
            px, py = pts[2 + int(rng.integers(0, max(1, len(pts) - 3)))]
            _c(d, s, px, py, 0.0075 * H, v, 1.6)
        finales.append(pts[-1])
    return finales


def _chip(d, s, cx, cy, w, h, pines, rng, v=1.0):
    x0, y0, x1, y1 = cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2
    _r(d, s, x0, y0, x1, y1, v, 2.6)
    _r(d, s, x0 + 0.025 * H, y0 + 0.025 * H, x1 - 0.025 * H, y1 - 0.025 * H, v * 0.5, 1.4)
    _r(d, s, cx - w * 0.22, cy - h * 0.22, cx + w * 0.22, cy + h * 0.22, v * 0.7, 1.6)
    _c(d, s, x0 + 0.04 * H, y0 + 0.04 * H, 0.010 * H, v, 2.0, lleno=True)
    L = 0.024 * H
    lados = {"t": (0, -1), "b": (0, 1), "l": (-1, 0), "r": (1, 0)}
    pitch_h, pitch_v = w / pines, h / pines
    for lado, (ux, uy) in lados.items():
        sg = 1 if rng.random() < 0.5 else -1
        nx, ny = -uy, ux
        for i in range(pines):
            t = (i + 0.5) / pines
            if lado in "tb":
                px = x0 + t * w
                py = y0 if lado == "t" else y1
                pitch = pitch_h
            else:
                px = x0 if lado == "l" else x1
                py = y0 + t * h
                pitch = pitch_v
            e0 = (px + ux * L, py + uy * L)
            _l(d, s, [(px, py), e0], v, 2.6)
            rank = i if sg > 0 else pines - 1 - i
            l1 = 0.02 * H + 0.4142 * pitch * rank + rng.uniform(0, 0.03) * H * 0
            dd = 0.045 * H + rng.uniform(0, 0.05) * H * 0
            p1 = (e0[0] + ux * l1, e0[1] + uy * l1)
            p2 = (p1[0] + ux * dd + nx * sg * dd, p1[1] + uy * dd + ny * sg * dd)
            l2 = rng.uniform(0.04, 0.22) * H
            p3 = (p2[0] + ux * l2, p2[1] + uy * l2)
            _l(d, s, [e0, p1, p2, p3], v * 0.85, 1.9)
            _c(d, s, p3[0], p3[1], 0.0085 * H, v * 0.85, 1.8)
            _c(d, s, p3[0], p3[1], 0.003 * H, v * 0.85, 1.2, lleno=True)


def electronica(tipo, var=0, zona=None):
    """Circuito: verde de PCB casi negro, pistas a 45° en bus, pads de cobre, vías, chip QFP y serigrafía (U1, R12, VCC 3V3)."""
    BASE = "#04120D"
    verde, cobre, sil = "#34E5A0", "#F2B84B", "#D9F5EA"
    rng = np.random.default_rng(202 + var * 11)
    img = base_color(BASE)
    img += F.nebulosa(["#04120D", "#06231A", "#0A4630"], 900, 7 + var, 0.10, (0.8, 0.4), 0.9)
    puntos = cap(F.puntos_rejilla(0.25, 1.4, 1.0))
    pintar(img, puntos, verde, 0.08)
    if tipo in ("portada", "cierre"):
        der = 0.18 + 0.82 * F.suave(0.40 * W, 0.95 * W, XX)
        cx, cy = 1.30 * H, 0.52 * H

        def arte(d, s):
            _chip(d, s, cx, cy, 0.42 * H, 0.42 * H, 12, np.random.default_rng(5 + var), 1.0)
            _bus(d, s, 0, 0.90 * H, 7, 0.022 * H, [(0.46 * H, -0.12 * H), (0.80 * H, 0.20 * H)], 1.05 * H, 1, 0.75, 2.0, True, rng)
            _txt(d, s, cx - 0.17 * H, cy - 0.29 * H, "U1  ·  SoC", 26, 0.9)
            _txt(d, s, cx + 0.04 * H, cy + 0.255 * H, "VCC 3V3", 22, 0.7)
            _txt(d, s, 1.03 * H, 0.83 * H, "R12  10k", 22, 0.7)
            _txt(d, s, 1.52 * H, 0.09 * H, "C4  100n", 22, 0.7)
        c = cap(arte)
        pintar(img, c * der, verde, 0.72, 0.25)
        # cobre en pads: realce cálido donde hay puntos de relleno (aproximado con el mismo trazo, muy suave)
        pintar(img, gaussian_filter(c, 1.5 * E) * der * 0.35 * F.suave(0.8 * W, W, XX), cobre, 0.4)
        dx, dy = XX - cx, YY - cy
        img += (np.exp(-(dx * dx + dy * dy) / (2 * (0.22 * H) ** 2)) * 0.06)[..., None] * rgb(verde)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        x0 = 0.42 * W
        c = cap(lambda d, s: _bus(d, s, x0 + var * 0.02 * W, 0.22 * H, 10, 0.026 * H,
                                  [(x0 + 0.20 * H, 0.24 * H), (x0 + 0.72 * H, 0.22 * H)], W + 0.05 * W, 1, 0.9, 2.2, True, rng))
        c2 = cap(lambda d, s: _bus(d, s, x0 + 0.1 * W, 0.98 * H, 6, 0.024 * H, [(x0 + 0.5 * H, -0.18 * H)], W, 1, 0.7, 2.0, True, rng))
        der = 0.25 + 0.75 * F.suave(0.35 * W, 0.8 * W, XX)
        pintar(img, (c + c2) * der, verde, 0.70, 0.22)
        pintar(img, cap(lambda d, s: _chip(d, s, W - 0.12 * H, 0.66 * H, 0.26 * H, 0.26 * H, 8, np.random.default_rng(9 + var), 1.0)),
               cobre, 0.45, 0.12)
        return fin(img, BASE, tipo, zona, 0.5)
    # contenido / video: haces de pistas en dos esquinas
    c = cap(lambda d, s: (_bus(d, s, W + 0.02 * H, 0.06 * H, 6, 0.022 * H, [(W - 0.35 * H, 0.16 * H)], W - 0.9 * H, -1, 0.9, 2.0, True, rng),
                          _bus(d, s, -0.02 * H, H - 0.20 * H, 5, 0.022 * H, [(0.22 * H, 0.14 * H)], 0.80 * H, 1, 0.9, 2.0, True, rng)))
    pintar(img, c, verde, 0.22, 0.05)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ CÁLCULO
def _campo_calculo(sem):
    rng = np.random.default_rng(sem)
    u, v = XX / H, YY / H
    f = np.zeros_like(u)
    for _ in range(7):
        cx, cy = rng.uniform(0.1, W / H), rng.uniform(0.05, 0.95)
        a, sg = rng.choice([-1, 1]) * rng.uniform(0.6, 1.2), rng.uniform(0.16, 0.36)
        f += a * np.exp(-((u - cx) ** 2 + (v - cy) ** 2) / (2 * sg * sg))
    f += 0.22 * (u - 0.9) * (v - 0.5)
    return f.astype(np.float32)


def _funcion(x):
    """Curva didáctica: suave, con un máximo y un valle (x en 0..1)."""
    return 0.55 * np.sin(2.2 * np.pi * x + 0.4) * np.exp(-0.6 * x) + 0.35 * x + 0.1


def calculo(tipo, var=0, zona=None):
    """Cálculo: medianoche con curvas de nivel de un paisaje, ejes, tangente y secante en la derivada, sumas de Riemann; tiza ámbar."""
    BASE = "#080C1B"
    indigo, ambar, tiza = "#6366F1", "#FBBF24", "#F3EFE6"
    img = base_color(BASE)
    img += F.nebulosa(["#080C1B", "#10163A", "#1E2A6B"], 900, 21 + var, 0.10, (0.85, 0.4), 0.9)
    f = _campo_calculo(31 + var * 7)
    fino, k = iso(f, 9, 1.1)
    mayor = fino * (np.mod(k, 4) == 0)
    if tipo in ("portada", "cierre"):
        der = 0.06 + 0.94 * F.suave(0.42 * W, 0.92 * W, XX)
        pintar(img, fino * der, indigo, 0.42)
        pintar(img, mayor * der, ambar, 0.22)
        x0, xw = 1.05 * H, 0.66 * H
        y_eje, alto = 0.83 * H, 0.52 * H
        xs = np.linspace(0, 1, 160)
        curva = [(x0 + x * xw, y_eje - _funcion(x) * alto) for x in xs]
        a_, h_ = 0.36, 0.17
        pa = (x0 + a_ * xw, y_eje - _funcion(a_) * alto)
        pb = (x0 + (a_ + h_) * xw, y_eje - _funcion(a_ + h_) * alto)
        pend = (_funcion(a_ + 1e-4) - _funcion(a_ - 1e-4)) / 2e-4 * alto / xw

        def arte(d, s):
            _l(d, s, [(x0 - 0.04 * H, y_eje), (x0 + xw + 0.06 * H, y_eje)], 0.9, 2.0)
            _l(d, s, [(x0, y_eje + 0.03 * H), (x0, y_eje - 0.66 * H)], 0.9, 2.0)
            for i in range(1, 9):
                xx_ = x0 + i * xw / 8
                _l(d, s, [(xx_, y_eje - 7 * E), (xx_, y_eje + 7 * E)], 0.8, 1.6)
            _l(d, s, curva, 1.0, 4.0)
            t0 = 0.11 * H
            _l(d, s, [(pa[0] - t0, pa[1] + pend * t0), (pa[0] + 2.4 * t0, pa[1] - pend * 2.4 * t0)], 0.85, 2.2)  # tangente
            _l(d, s, [(pa[0] - 0.4 * t0, pa[1] + (pb[1] - pa[1]) / (pb[0] - pa[0]) * (-0.4 * t0)),
                      (pb[0] + 0.5 * t0, pb[1] + (pb[1] - pa[1]) / (pb[0] - pa[0]) * 0.5 * t0)], 0.55, 1.6)  # secante
            for p in (pa, pb):
                _punteada(d, s, [(p[0], p[1]), (p[0], y_eje)], 0.7, 1.4, 8, 7)
                _c(d, s, p[0], p[1], 0.0085 * H, 1.0, 2.0, lleno=True)
            _l(d, s, [(pa[0], y_eje + 0.045 * H), (pb[0], y_eje + 0.045 * H)], 0.8, 1.6)
            _txt(d, s, pa[0] - 0.012 * H, y_eje + 0.06 * H, "x", 34, 0.9, "DejaVuSerif-Italic")
            _txt(d, s, (pa[0] + pb[0]) / 2 - 0.006 * H, y_eje + 0.06 * H, "h", 34, 0.9, "DejaVuSerif-Italic")
            fu = _fuente("DejaVuSerif-Italic", int(44 * E * s))
            x_f, y_f = 1.02 * H, 0.17 * H
            _txt(d, s, x_f, y_f, "f ′(x) = lim  [ f(x + h) − f(x) ] / h", 44, 0.85, "DejaVuSerif-Italic")
            x_lim = x_f + fu.getlength("f ′(x) = ") / s
            _txt(d, s, x_lim + 0.004 * H, y_f + 0.052 * H, "h→0", 26, 0.7, "DejaVuSerif-Italic")
        c = cap(arte)
        pintar(img, c, tiza, 0.62, 0.0)
        pintar(img, cap(lambda d, s: [_l(d, s, curva, 1.0, 4.5)]), ambar, 0.85, 0.35)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        der = 0.05 + 0.95 * F.suave(0.30 * W, 0.85 * W, XX)
        pintar(img, fino * der, indigo, 0.30)
        pintar(img, mayor * der, ambar, 0.16)
        x0, xw, y_eje, alto = 0.66 * W, 0.30 * W, 0.82 * H, 0.50 * H
        xs = np.linspace(0, 1, 200)
        curva = [(x0 + x * xw, y_eje - _funcion(x * 0.9 + 0.05) * alto) for x in xs]
        n = 16 + 4 * (var % 3)

        def arte(d, s):
            _l(d, s, [(x0 - 0.03 * H, y_eje), (x0 + xw + 0.04 * H, y_eje)], 0.9, 2.0)
            for i in range(n):
                xa = x0 + i * xw / n
                ya = y_eje - _funcion((i + 0.5) / n * 0.9 + 0.05) * alto
                _r(d, s, xa, ya, xa + xw / n, y_eje, 0.6, 1.5)
            _l(d, s, curva, 1.0, 4.0)
            _txt(d, s, x0 - 0.02 * H, 0.14 * H, "∫", 620, 0.12, "DejaVuSerif-Italic")
            _txt(d, s, x0 + 0.03 * W, y_eje + 0.045 * H, "Σ f(xᵢ) Δx  →  ∫ f(x) dx", 34, 0.75, "DejaVuSerif-Italic")
        c = cap(arte)
        pintar(img, c, tiza, 0.55)
        pintar(img, cap(lambda d, s: [_l(d, s, curva, 1.0, 4.5)]), ambar, 0.85, 0.3)
        return fin(img, BASE, tipo, zona, 0.5)
    # contenido / video: curvas de nivel solo en dos esquinas
    m = np.maximum(_masc_esq(W, 0, 0.62), _masc_esq(0, H, 0.52))
    pintar(img, fino * m, indigo, 0.50)
    pintar(img, mayor * m, ambar, 0.26)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ FÍSICA
def _rejilla_curva(d, s, masas, paso, v=0.6, w=1.2):
    def warp(x, y):
        for cx, cy, A, sg in masas:
            dx, dy = x - cx, y - cy
            k = 1 - A * math.exp(-(dx * dx + dy * dy) / (2 * sg * sg))
            x, y = cx + dx * k, cy + dy * k
        return x, y
    pasos = np.arange(-paso, max(W, H) + paso, 10 * E)
    for gx in np.arange(-paso, W + paso, paso):
        _l(d, s, [warp(gx, y) for y in np.arange(-paso, H + paso, 10 * E)], v, w)
    for gy in np.arange(-paso, H + paso, paso):
        _l(d, s, [warp(x, gy) for x in np.arange(-paso, W + paso, 10 * E)], v, w)
    del pasos


def _agujero(img, cx, cy, R, semilla=3, inc=0.24, rot=-14):
    """Agujero negro: sombra, disco de acreción inclinado con efecto Doppler, arco lenteado y anillo de fotones."""
    dx, dy = XX - cx, YY - cy
    r = np.hypot(dx, dy)
    c, s_ = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    u, v = dx * c + dy * s_, (-dx * s_ + dy * c) / inc
    rd = np.hypot(u, v)
    a = np.arctan2(v, u)
    ruido_ = F.ruido(R * 0.35, 4, semilla)
    disco = (R * 1.9 / np.maximum(rd, 1)) ** 2.0 * F.suave(R * 1.55, R * 1.95, rd) * F.suave(R * 6.6, R * 3.0, rd)
    disco *= (0.35 + 0.95 * (0.5 - 0.5 * np.cos(a))) * (0.7 + 0.6 * ruido_)
    col_d = _rampa(F.suave(R * 1.7, R * 5.2, rd), ["#FFF2D0", "#FFB347", "#E8531E", "#5A1408"])
    frente = F.suave(-0.03 * R, 0.03 * R, v * inc)  # mitad inferior: pasa por delante del hueco
    lente = np.exp(-((r - R * 1.42) / (0.32 * R)) ** 2) * F.suave(0.35 * R, -0.75 * R, dy) * (0.45 + 0.75 * (0.5 - 0.5 * np.cos(np.arctan2(dy, dx))))
    img += np.exp(-(r / (5.5 * R)) ** 2)[..., None] * rgb("#E8531E") * 0.06
    img += lente[..., None] * rgb("#FFC978") * 0.9
    img += (disco * (1 - frente))[..., None] * col_d * 1.4 * F.suave(R * 0.98, R * 1.6, r)[..., None]
    img *= (1 - F.suave(R + 1.5, R - 1.5, r))[..., None]
    img += (disco * frente)[..., None] * col_d * 1.6
    anillo = np.exp(-((r - 1.035 * R) / (0.028 * R + 1.2)) ** 2)
    img += anillo[..., None] * rgb("#FFF4DC") * 0.9 + (np.exp(-((r - 1.05 * R) / (0.10 * R)) ** 2) * 0.25)[..., None] * rgb("#FFB347")


def _trazas(origen, rng, n, radio0=0.16, pasos=420):
    """Trazas de partículas en un campo magnético: espirales que pierden energía (cámara de burbujas)."""
    trazas = []
    for _ in range(n):
        ang = rng.uniform(0, 2 * math.pi)
        x, y = origen
        w = rng.choice([-1, 1]) * rng.uniform(0.010, 0.035) * (radio0 / 0.16)
        vel = 12.0 * E * rng.uniform(0.8, 1.6)
        pts = [(x, y)]
        for _i in range(pasos):
            ang += w
            x += vel * math.cos(ang)
            y += vel * math.sin(ang)
            vel *= 0.9975
            w *= 1.0035
            pts.append((x, y))
            if vel < 0.6 * E:
                break
        trazas.append(pts)
    return trazas


def fisica(tipo, var=0, zona=None):
    """Física: negro con tinte índigo; rejilla espaciotemporal curvada por masas, agujero negro con lente gravitacional y trazas de partículas."""
    BASE = "#06060F"
    violeta, cian, oro = "#8B8CFF", "#22D3EE", "#FDE68A"
    img = base_color(BASE)
    sem = 41 + var * 9
    mw, dens = F.via_lactea(angulo=-28, centro=(0.62, 0.4), ancho=0.12, semilla=sem, colores=("#3b3b8f", "#7a5fb0"))
    img += mw * 0.6
    est = F.estrellas(2600, sem, 0.7) + F.estrellas(1800, sem + 1, 0.55, mascara=dens) + F.estrellas(12, sem + 2, 0.9, grandes=3)
    if tipo in ("portada", "cierre"):
        cx, cy, R = (1.30 if tipo == "portada" else 1.46) * H, 0.52 * H, (0.105 if tipo == "portada" else 0.095) * H
        masas = [(cx, cy, 0.86, 0.26 * H), (cx - 0.62 * H, cy + 0.42 * H, 0.35, 0.16 * H)]
        rej = cap(lambda d, s: _rejilla_curva(d, s, masas, 0.085 * H, 0.9, 1.3))
        alc = 0.10 + 0.90 * (1 - F.suave(0.08 * H, 0.95 * H, np.hypot(XX - cx, (YY - cy) * 1.2)))
        alc *= 0.25 + 0.75 * F.suave(0.30 * W, 0.80 * W, XX)
        pintar(img, rej * alc, violeta, 0.55)
        img += est
        _agujero(img, cx, cy, R, sem)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        rng = np.random.default_rng(700 + var)
        o = (0.74 * W, (0.48 + 0.08 * (var % 3 - 1)) * H)
        tr = _trazas(o, rng, 18)
        colores = [violeta, cian, oro]
        for ci, colr in enumerate(colores):
            capa = cap(lambda d, s: [_l(d, s, pts, 0.9, 1.5) for j, pts in enumerate(tr) if j % 3 == ci])
            pintar(img, capa * (0.25 + 0.75 * F.suave(0.35 * W, 0.8 * W, XX)), colr, 0.78, 0.18)
        img += (np.exp(-((XX - o[0]) ** 2 + (YY - o[1]) ** 2) / (2 * (0.012 * H) ** 2)))[..., None] * rgb("#ffffff") * 0.9
        img += est
        return fin(img, BASE, tipo, zona, 0.5)
    m = _masc_esq(W, H, 0.6)
    rej = cap(lambda d, s: _rejilla_curva(d, s, [(W * 1.02, H * 1.02, 0.8, 0.22 * H)], 0.085 * H, 0.9, 1.2))
    pintar(img, rej * m, violeta, 0.30)
    return fin(img, BASE, tipo, zona, 0.45, est * 0.65)


# ================================================================ ELECTROMAGNETISMO
def _campo_E(cargas, x, y):
    ex = ey = 0.0
    for cx, cy, q in cargas:
        dx, dy = x - cx, y - cy
        r3 = (dx * dx + dy * dy) ** 1.5 + 1e-9
        ex += q * dx / r3
        ey += q * dy / r3
    return ex, ey


def _lineas_campo(cargas, n, paso, r0, sentido=1, pasos=2600):
    """Líneas de campo de las cargas positivas (integración de punto medio) hasta otra carga o salir del lienzo."""
    out = []
    for cx, cy, q in cargas:
        if q * sentido <= 0:
            continue
        for i in range(n):
            a = 2 * math.pi * (i + 0.5) / n
            x, y = cx + r0 * math.cos(a), cy + r0 * math.sin(a)
            pts = [(x, y)]
            for _ in range(pasos):
                ex, ey = _campo_E(cargas, x, y)
                m = math.hypot(ex, ey)
                if m < 1e-14:
                    break
                mx, my = x + 0.5 * paso * sentido * ex / m, y + 0.5 * paso * sentido * ey / m
                ex, ey = _campo_E(cargas, mx, my)
                m = math.hypot(ex, ey)
                x, y = x + paso * sentido * ex / m, y + paso * sentido * ey / m
                pts.append((x, y))
                if not (-0.2 * W < x < 1.2 * W and -0.3 * H < y < 1.3 * H):
                    break
                if any(q2 * sentido < 0 and math.hypot(x - c2x, y - c2y) < r0 * 0.9 for c2x, c2y, q2 in cargas):
                    break
            out.append(pts)
    return out


def _carga(img, cx, cy, r, positiva, col):
    dx, dy = XX - cx, YY - cy
    d2 = dx * dx + dy * dy
    img += (np.exp(-d2 / (2 * (r * 2.4) ** 2)) * 0.28 + np.exp(-d2 / (2 * (r * 1.0) ** 2)) * 0.5)[..., None] * rgb(col)
    disco = F.suave(r + 1.5, r - 1.5, np.sqrt(d2))
    img[:] = img * (1 - disco[..., None]) + disco[..., None] * rgb(col) * 0.95


def electromagnetismo(tipo, var=0, zona=None):
    """Electromagnetismo: azul noche con campo de un dipolo (E magenta, equipotenciales azules), cargas brillantes y onda EM con E y B perpendiculares."""
    BASE = "#050914"
    azul, magenta, oro = "#3B9CFF", "#FF4D7A", "#FFC857"
    img = base_color(BASE)
    img += F.nebulosa(["#050914", "#0A1A3D", "#153D7A"], 900, 51 + var, 0.09, (0.8, 0.3), 0.9)
    img += F.estrellas(700, 61 + var, 0.35)
    if tipo in ("portada", "cierre"):
        c1, c2 = (1.12 * H, 0.50 * H, 1.0), (1.56 * H, 0.50 * H, -1.0)
        if tipo == "cierre":
            c1, c2 = (1.10 * H, 0.42 * H, 1.0), (1.60 * H, 0.64 * H, -1.0)
        cargas = [c1, c2]
        V = sum(q / (np.hypot(XX - x, YY - y) + 6) for x, y, q in cargas) * H
        u = np.sign(V) * np.log1p(np.abs(V) * 1.6)
        eq, _ = iso(u.astype(np.float32), 3.2, 1.0)
        alc = 0.12 + 0.88 * F.suave(0.30 * W, 0.78 * W, XX)
        pintar(img, eq * alc, azul, 0.34)
        lin = _lineas_campo(cargas, 22, 4.0 * E, 0.022 * H)
        capa = cap(lambda d, s: [_l(d, s, pts, 0.95, 1.9) for pts in lin])
        pintar(img, capa * alc, magenta, 0.85, 0.22)
        _carga(img, c1[0], c1[1], 0.030 * H, True, magenta)
        _carga(img, c2[0], c2[1], 0.030 * H, False, azul)
        sig = cap(lambda d, s: (_l(d, s, [(c1[0] - 0.014 * H, c1[1]), (c1[0] + 0.014 * H, c1[1])], 1, 3.6),
                                _l(d, s, [(c1[0], c1[1] - 0.014 * H), (c1[0], c1[1] + 0.014 * H)], 1, 3.6),
                                _l(d, s, [(c2[0] - 0.014 * H, c2[1]), (c2[0] + 0.014 * H, c2[1])], 1, 3.6)))
        img -= sig[..., None] * 0.9
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        ang = math.radians(-12 + 6 * (var % 3))
        x0, x1 = 0.36 * W, W + 0.02 * W
        oy = 0.52 * H
        ax = (math.cos(ang), math.sin(ang))
        uE = (0.0, -1.0)
        uB = (0.80, 0.56)
        A, lam = 0.20 * H, 0.46 * H
        ts = np.linspace(0, x1 - x0, 500)

        def punto(t, amp, u, fase=0.0):
            x, y = x0 + t * ax[0], oy + t * ax[1]
            e = amp * math.sin(2 * math.pi * t / lam + fase) * (0.15 + 0.85 * min(1, t / (0.25 * W)))
            return x + u[0] * e, y + u[1] * e

        def arte_e(d, s):
            _l(d, s, [(x0, oy), (x0 + ts[-1] * ax[0], oy + ts[-1] * ax[1])], 0.7, 1.6)
            _l(d, s, [punto(t, A, uE) for t in ts], 1.0, 4.0)
            for t in ts[::14]:
                _l(d, s, [(x0 + t * ax[0], oy + t * ax[1]), punto(t, A, uE)], 0.45, 1.3)

        def arte_b(d, s):
            _l(d, s, [punto(t, A * 0.9, uB) for t in ts], 1.0, 4.0)
            for t in ts[::14]:
                _l(d, s, [(x0 + t * ax[0], oy + t * ax[1]), punto(t, A * 0.9, uB)], 0.45, 1.3)
        alc = 0.12 + 0.88 * F.suave(0.30 * W, 0.78 * W, XX)
        pintar(img, cap(arte_e) * alc, magenta, 0.85, 0.22)
        pintar(img, cap(arte_b) * alc, azul, 0.85, 0.22)
        pintar(img, cap(lambda d, s: _l(d, s, [(x0, oy), (x1, oy + (x1 - x0) * ax[1] / ax[0])], 0.7, 1.4)), "#FFFFFF", 0.25)
        return fin(img, BASE, tipo, zona, 0.5)
    # contenido / video: líneas de campo de un dipolo en la esquina inferior derecha, tenues
    cargas = [(W * 0.93, H * 1.02, 1.0), (W * 1.06, H * 0.80, -1.0)]
    lin = _lineas_campo(cargas, 18, 5.0 * E, 0.02 * H)
    m = _masc_esq(W, H, 0.6)
    capa = cap(lambda d, s: [_l(d, s, pts, 0.9, 1.6) for pts in lin])
    pintar(img, capa * m, magenta, 0.30)
    V = sum(q / (np.hypot(XX - x, YY - y) + 6) for x, y, q in cargas) * H
    eq, _ = iso((np.sign(V) * np.log1p(np.abs(V) * 1.6)).astype(np.float32), 5, 1.0)
    pintar(img, eq * m, azul, 0.18)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ LUNAR
def _relieve(sem, n=120, rmin=10, rmax=300, luz=-40):
    """Sombreado rasante de un campo de cráteres (HxW en ~[-1, 1])."""
    rng = np.random.default_rng(sem)
    h = np.zeros((H, W), np.float32)
    radios = rmin * E * (rmax / rmin) ** rng.random(n) ** 1.8
    for r in radios:
        cx, cy = rng.uniform(-r, W + r), rng.uniform(-r, H + r)
        x0, x1 = int(max(0, cx - 1.6 * r)), int(min(W, cx + 1.6 * r))
        y0, y1 = int(max(0, cy - 1.6 * r)), int(min(H, cy + 1.6 * r))
        if x1 <= x0 or y1 <= y0:
            continue
        d = np.hypot(XX[y0:y1, x0:x1] - cx, YY[y0:y1, x0:x1] - cy) / r
        prof = -(1 - d * d) * (d < 1) * 0.55 + np.exp(-((d - 1.0) / 0.13) ** 2) * 0.30
        h[y0:y1, x0:x1] += prof * r * 0.25
    h += (F.ruido(60 * E, 5, sem + 1) - 0.5) * 6 * E
    h = gaussian_filter(h, 1.0)
    gy, gx = np.gradient(h)
    a = math.radians(luz)
    sombra = (gx * math.cos(a) + gy * math.sin(a))
    return np.clip(sombra / (np.abs(sombra).std() * 3 + 1e-6), -1, 1)


def _esfera(img, cx, cy, r, sem, luz=(-0.62, -0.42)):
    """Tierra: océano, continentes y nubes con ruido, terminador y borde atmosférico."""
    dx, dy = (XX - cx) / r, (YY - cy) / r
    rr = np.hypot(dx, dy)
    z = np.sqrt(np.clip(1 - rr * rr, 0, 1))
    n = np.array([dx, dy, z])
    L = np.array([luz[0], luz[1], 0.66])
    L /= np.linalg.norm(L)
    lam = np.clip(n[0] * L[0] + n[1] * L[1] + n[2] * L[2], 0, 1)
    tierra = F.suave(0.52, 0.56, F.ruido(r * 1.1, 5, sem, 0.5))
    nubes = F.suave(0.58, 0.85, F.ruido(r * 0.55, 6, sem + 1, 0.6)) * 0.7
    seco = F.ruido(r * 0.9, 3, sem + 2)[..., None]
    oceano, verde, arena = rgb("#0E4C9E"), rgb("#2F6B35"), rgb("#9C7F4C")
    col = oceano * (1 - tierra[..., None]) + mezcla(verde, arena, seco) * tierra[..., None]
    col = col * (1 - nubes[..., None] * 0.8) + nubes[..., None] * 0.8 * rgb("#F4F8FF")
    col = col * (0.05 + 0.95 * lam ** 0.75)[..., None]
    borde = (1 - z) ** 2.5
    col = col + borde[..., None] * rgb("#7CC4FF") * 0.55 * (0.25 + lam)[..., None]
    dentro = F.suave(1 + 1.5 / r, 1 - 1.5 / r, rr)
    fuera = np.clip(rr - 1, 0, None)
    img += (np.exp(-fuera / 0.05) * 0.45 + np.exp(-fuera / 0.25) * 0.12)[..., None] * rgb("#5AA9FF") * (1 - dentro[..., None]) * 0.6
    img[:] = img * (1 - dentro[..., None]) + col * dentro[..., None]


def lunar(tipo, var=0, zona=None):
    """Luna: negro neutro con estrellas, horizonte regolítico con cráteres y la Tierra saliendo; acento azul hielo."""
    BASE = "#0A0B0F"
    hielo = "#8FD3FF"
    img = base_color(BASE)
    sem = 71 + var * 13
    mw, dens = F.via_lactea(angulo=-20, centro=(0.5, 0.3), ancho=0.10, semilla=sem, colores=("#5f6b8f", "#b3a08a"))
    est = F.estrellas(4200, sem, 0.85) + F.estrellas(2200, sem + 1, 0.6, mascara=dens) + F.estrellas(16, sem + 2, 0.9, grandes=4)
    if tipo in ("portada", "cierre"):
        img += mw * 0.55
        img += est
        _esfera(img, (1.38 if tipo == "portada" else 1.56) * H, (0.33 if tipo == "portada" else 0.30) * H, (0.14 if tipo == "portada" else 0.115) * H, sem)
        # horizonte: limbo de un cuerpo enorme + relieve dentro
        R, hcx, hcy = 3.1 * H, 1.0 * W * 0.46, 1.0 * H + 3.1 * H * 0.0 + (3.1 - 0.17) * H
        d = np.hypot(XX - hcx, YY - hcy)
        dentro = F.suave(R + 1.5, R - 1.5, d)
        rel = _relieve(sem + 5, 140, 10, 260)
        ilum = 0.5 + 0.5 * rel
        grano = 0.10 + 0.22 * ilum
        sup = (grano * (0.35 + 0.65 * F.suave(R, R - 0.30 * H, d)))[..., None] * rgb("#C7CBD3")
        img[:] = img * (1 - dentro[..., None]) + (rgb("#0E0F13") + sup) * dentro[..., None]
        fuera = np.clip(d - R, 0, None)
        borde = np.exp(-((d - R) / (0.004 * H + 1.2)) ** 2)
        img += ((np.exp(-fuera / (0.012 * H)) * 0.4 + borde * 0.8) * F.suave(0.15 * W, 0.85 * W, XX))[..., None] * rgb("#DDE6F2")
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        rel = _relieve(sem + 6, 160, 12, 340, luz=-30 + 25 * (var % 3))
        ilum = 0.5 + 0.5 * rel
        suelo = (0.04 + 0.20 * ilum)[..., None] * rgb("#BFC4CC")
        img += suelo * (0.04 + 0.96 * F.suave(0.28 * W, 0.85 * W, XX))[..., None]
        img += est * 0.25
        _esfera(img, 1.50 * H, 0.26 * H, 0.085 * H, sem + 2)
        return fin(img, BASE, tipo, zona, 0.5)
    img += est * 0.85
    # contenido / video: limbo lunar al borde inferior, muy bajo
    R, hcx, hcy = 4.6 * H, W * 0.70, H * 0.985 + 4.6 * H
    d = np.hypot(XX - hcx, YY - hcy)
    dentro = F.suave(R + 1.5, R - 1.5, d)
    img[:] = img * (1 - dentro[..., None]) + (rgb("#0F1014") + 0.06 * rgb("#C7CBD3")) * dentro[..., None]
    borde = np.exp(-((d - R) / (0.003 * H + 1.2)) ** 2) * 0.5
    img += (borde * F.suave(0.2 * W, 0.9 * W, XX))[..., None] * rgb("#DDE6F2")
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ MARTE
def _cresta(sem, base, amp, rugos=1.0):
    """Silueta 1D de dunas: y (px) por columna."""
    rng = np.random.default_rng(sem)
    n = gaussian_filter1d(rng.standard_normal(W).astype(np.float32), 170 * E * rugos)
    n = n / (n.std() + 1e-6)
    m = gaussian_filter1d(rng.standard_normal(W).astype(np.float32), 60 * E * rugos)
    m = m / (m.std() + 1e-6)
    x = np.arange(W) / W
    return base * H + amp * H * (0.8 * n + 0.18 * m + 0.35 * np.sin(2 * np.pi * (x * rng.uniform(0.8, 1.6) + rng.random())))


def marte(tipo, var=0, zona=None):
    """Marte: cielo de polvo óxido con el atardecer azul, capas de dunas con luz rasante y estrellas arriba; acento óxido."""
    BASE = "#130A0C"
    sem = 81 + var * 11
    img = base_color(BASE)
    y = YY / H
    cielo = _rampa(np.clip((y - 0.05) / 0.85, 0, 1) ** 1.3, ["#0A0510", "#241018", "#6A2B20", "#C2622F"])
    cielo = mezcla(base_color(BASE), cielo, {"contenido": 0.55, "video": 0.12}.get(tipo, 1.0))  # en video el cielo casi no se tiñe: el video se funde a la base
    img = cielo.copy()
    polvo = F.nebulosa(["#130A0C", "#3A1810", "#B5522B"], 800, sem, 0.35 if tipo in ("portada", "cierre", "seccion") else 0.08, (0.8, 0.85), 0.8)
    img += polvo * 0.55
    sky = 1 - F.suave(0.30 * H, 0.66 * H, YY)
    est = (F.estrellas(3400, sem, 0.85, mascara=sky) + F.estrellas(18, sem + 1, 0.9, mascara=sky, grandes=3))
    if tipo in ("portada", "cierre"):
        sx, sy = (1.26 if tipo == "portada" else 1.16) * H, 0.66 * H
        dx, dy = XX - sx, YY - sy
        d2 = dx * dx + dy * dy
        img += (np.exp(-d2 / (2 * (0.32 * H) ** 2)) * 0.28)[..., None] * rgb("#E0703A")
        img += (np.exp(-d2 / (2 * (0.12 * H) ** 2)) * 0.45 + np.exp(-d2 / (2 * (0.035 * H) ** 2)) * 0.6)[..., None] * rgb("#7DD3FC")
        img += (np.exp(-d2 / (2 * (0.010 * H) ** 2)) * 1.6)[..., None] * rgb("#EAF6FF")
        niveles = [(0.72, 0.016), (0.80, 0.022), (0.88, 0.028), (0.96, 0.030)]
        cols = [("#7A3A26", "#B4582E"), ("#5C2A1E", "#8E4124"), ("#3C1C15", "#612D1B"), ("#1E0E0C", "#3A1A12")]
    elif tipo == "seccion":
        sx, sy = 1.40 * H, 0.52 * H
        dx, dy = XX - sx, YY - sy
        img += (np.exp(-(dx * dx + dy * dy) / (2 * (0.45 * H) ** 2)) * 0.22)[..., None] * rgb("#E0703A")
        niveles = [(0.82, 0.020), (0.92, 0.028)]
        cols = [("#5C2A1E", "#8E4124"), ("#2A1310", "#4A2117")]
    else:
        niveles = [(0.94, 0.012)]
        cols = [("#2A1310", "#3A1A12")]
    img += est * (0.65 if tipo in ("contenido", "video") else 1.0)
    for i, ((b, a), (c_lejos, c_cerca)) in enumerate(zip(niveles, cols)):
        yc = _cresta(sem + 10 * i, b, a)
        m = F.suave(yc[None, :] - 1.2, yc[None, :] + 1.2, YY)
        prof = np.clip((YY - b * H) / (0.22 * H), 0, 1)
        color = mezcla(rgb(c_cerca), rgb(c_lejos) * 0.45, prof[..., None])
        img[:] = img * (1 - m[..., None]) + color * m[..., None]
        # luz rasante en la cresta (lado que mira al Sol, a la derecha)
        pend = np.gradient(yc)
        luz = np.exp(-((YY - yc[None, :]) / (2.4 * E + 1)) ** 2) * np.clip(-pend[None, :] * 0.8 + 0.3, 0, 1)
        img += luz[..., None] * rgb("#FFB27A") * (0.55 if tipo in ("portada", "cierre") else 0.30)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ LANZAMIENTO
def _estela(img, p0, p1, p2, ancho, sem, largo_util=1.0):
    """Estela de un cohete: Bézier con núcleo blanco, penacho naranja y brasa roja que se ensancha y se apaga."""
    tray = _bezier(p0, p1, p2, 420)
    n = len(tray)
    capas = []
    for grosor, cerca in ((1.0, 1.0), (2.6, 0.7), (6.0, 0.45)):
        im = Image.new("L", (W, H), 0)
        dd = ImageDraw.Draw(im)
        for i in range(n - 1):
            t = i / (n - 1)  # 0 = cola, 1 = cabeza
            w_ = max(1, int((ancho * E) * grosor * (0.25 + 1.3 * (1 - t) ** 0.6)))
            v = int(255 * (t ** 1.6) * cerca)
            dd.line([tuple(tray[i]), tuple(tray[i + 1])], fill=v, width=w_)
        capas.append(np.asarray(im, np.float32) / 255)
    nucleo = gaussian_filter(capas[0], 2.5 * E)
    plumaje = gaussian_filter(capas[1], 10 * E)
    brasa = gaussian_filter(capas[2], 28 * E)
    tur = 0.75 + 0.5 * F.ruido(40 * E, 4, sem)
    img += (brasa * tur * 0.9)[..., None] * rgb("#C2410C") + (plumaje * tur * 1.2)[..., None] * rgb("#FF8A3D") + (nucleo * 1.6)[..., None] * rgb("#FFF1D6")
    hx, hy = tray[-1]
    dx, dy = XX - hx, YY - hy
    d2 = dx * dx + dy * dy
    img += (np.exp(-d2 / (2 * (0.05 * H) ** 2)) * 0.6 + np.exp(-d2 / (2 * (0.011 * H) ** 2)) * 1.4)[..., None] * rgb("#FFE9C4")
    return tray


def lanzamiento(tipo, var=0, zona=None):
    """Lanzamiento: noche con bandas de atmósfera, estela de ascenso con penacho, escalera de altitud y eventos (MAX-Q, MECO, SEP)."""
    BASE = "#07080D"
    naranja, hielo = "#FF8A3D", "#7DD3FC"
    sem = 91 + var * 17
    img = base_color(BASE)
    alt = 1 - F.suave(0.0, 1.0, YY / H)
    img += (F.suave(0.55, 1.0, YY / H) ** 2.2)[..., None] * rgb("#0F2F5C") * (0.55 if tipo in ("portada", "cierre") else 0.25)
    est = F.estrellas(3600, sem, 0.8, mascara=1 - F.suave(0.4, 0.85, YY / H)) + F.estrellas(12, sem + 1, 0.9, grandes=3)
    if tipo in ("portada", "cierre"):
        img += est
        img += F.nebulosa(["#07080D", "#0B1A33", "#14407A"], 800, sem + 2, 0.12, (0.9, 0.9), 0.7)
        # limbo atmosférico al fondo
        F.planeta(img, W * 0.72, H * 3.45, H * 2.55, atm="#5EC8FF", luz=-90, cuerpo="#03060C", fuerza=0.9, textura=0.03, semilla=sem)
        if tipo == "portada":
            tray = _estela(img, (1.52 * H, 1.00 * H), (1.56 * H, 0.42 * H), (1.30 * H, 0.14 * H), 11, sem)
        else:
            tray = _estela(img, (1.30 * H, 1.00 * H), (1.42 * H, 0.46 * H), (1.62 * H, 0.16 * H), 11, sem)
        ev = [(0.42, "MAX-Q"), (0.70, "MECO"), (0.90, "SEP")]

        def arte(d, s):
            for k in range(0, 101, 10):  # escalera de altitud en el borde derecho
                yy_ = H * (0.05 + 0.90 * k / 100)
                L = (0.05 if k % 50 == 0 else 0.028) * H
                _l(d, s, [(W - 0.10 * H, yy_), (W - 0.10 * H - L, yy_)], 0.8, 1.6)
            _l(d, s, [(W - 0.10 * H, 0.05 * H), (W - 0.10 * H, 0.95 * H)], 0.6, 1.6)
            _txt(d, s, W - 0.42 * H, 0.05 * H - 14 * E, "100 km · KÁRMÁN", 22, 0.8, "IBMPlexMono-400")
            for t, nombre in ev:
                x, y = tray[int(t * (len(tray) - 1))]
                _c(d, s, x, y, 0.011 * H, 0.9, 1.8)
                _l(d, s, [(x + 0.016 * H, y), (x + 0.09 * H, y - 0.03 * H)], 0.6, 1.4)
                _txt(d, s, x + 0.095 * H, y - 0.055 * H, nombre, 24, 0.85, "IBMPlexMono-400")
            _punteada(d, s, _bezier((1.16 * H, 1.0 * H), (1.24 * H, 0.50 * H), (1.12 * H, 0.05 * H)), 0.4, 1.4, 10, 12)
        pintar(img, cap(arte) * (0.3 + 0.7 * F.suave(0.35 * W, 0.8 * W, XX)), hielo, 0.60)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        img += est * 0.8
        tray = _estela(img, (1.05 * H, 1.04 * H), (1.72 * H, 0.66 * H), (1.46 * H, 0.10 * H), 5, sem)
        alc = 0.2 + 0.8 * F.suave(0.30 * W, 0.78 * W, XX)

        def arte(d, s):
            for k in range(0, 41):
                yy_ = H * (0.06 + 0.88 * k / 40)
                _l(d, s, [(W - 0.09 * H, yy_), (W - 0.09 * H - (0.05 if k % 10 == 0 else 0.022) * H, yy_)], 0.7, 1.5)
            for t in (0.25, 0.55, 0.85):
                x, y = tray[int(t * (len(tray) - 1))]
                _c(d, s, x, y, 0.010 * H, 0.9, 1.8)
                _c(d, s, x, y, 0.028 * H, 0.45, 1.3)
        pintar(img, cap(arte) * alc, hielo, 0.55)
        return fin(img, BASE, tipo, zona, 0.5)
    img += est * 0.8

    def esc(d, s):
        for k in range(0, 41):
            yy_ = H * (0.10 + 0.80 * k / 40)
            _l(d, s, [(W - 0.05 * H, yy_), (W - 0.05 * H - (0.04 if k % 10 == 0 else 0.018) * H, yy_)], 0.7, 1.4)
    pintar(img, cap(esc), hielo, 0.26)
    pintar(img, cap(lambda d, s: _punteada(d, s, _bezier((W * 0.98, H * 1.04), (W * 1.04, H * 0.5), (W * 0.93, -H * 0.02)), 0.6, 1.5, 12, 12)), naranja, 0.22)
    return fin(img, BASE, tipo, zona, 0.45)


# ---------------------------------------------------------------- registro
GENERADORES_TEMATICOS = {"robotica": robotica, "electronica": electronica, "calculo": calculo, "fisica": fisica,
                         "electromagnetismo": electromagnetismo, "lunar": lunar, "marte": marte, "lanzamiento": lanzamiento}
for _n, _f in GENERADORES_TEMATICOS.items():
    F.registrar_generador(_n, _f)


def hoja_contacto(ids, var=0, rehacer=True, ancho=560):
    """Una fila por tema con los cinco tipos de diapositiva; devuelve la ruta del JPG."""
    zona = (1.822, 1.5, 9.689, 5.45)
    tipos = ("portada", "seccion", "contenido", "video", "cierre")
    filas = []
    for i in ids:
        ims = []
        for t in tipos:
            ruta = F.fondo(i, i, t, var, zona if t == "video" else None, 0.0, rehacer)
            im = Image.open(ruta).convert("RGB")
            ims.append(im.resize((ancho, int(ancho * im.height / im.width)), Image.LANCZOS))
        fila = Image.new("RGB", (len(ims) * (ancho + 6) + 6, ims[0].height + 6), (24, 26, 32))
        for k, im in enumerate(ims):
            fila.paste(im, (6 + k * (ancho + 6), 6))
        filas.append(fila)
    hoja = Image.new("RGB", (filas[0].width, sum(f.height for f in filas)), (24, 26, 32))
    y = 0
    for f in filas:
        hoja.paste(f, (0, y))
        y += f.height
    ruta = F.CACHE / ("hoja_tematicos.jpg" if len(ids) > 1 else f"hoja_{ids[0]}.jpg")
    hoja.save(ruta, quality=88)
    return ruta


if __name__ == "__main__":
    import sys
    ids = sys.argv[1:] or list(GENERADORES_TEMATICOS)
    print(hoja_contacto(ids))
