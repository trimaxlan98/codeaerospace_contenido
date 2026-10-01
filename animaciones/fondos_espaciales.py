"""Fondos espaciales procedurales para las presentaciones «espaciales» (sin fotos ni recursos externos).

Todo se genera con numpy/scipy: campo de estrellas en capas (temperatura de color, halos y espigas),
Vía Láctea con polvo, nebulosas de ruido fractal, limbo planetario con atmósfera, rejilla HUD y
trazos orbitales. Cada entorno de decks_espaciales.py pide sus fondos por tipo de diapositiva.

Regla del «hueco de video»: si se pasa `zona` (rectángulo del video en pulgadas), toda la decoración
(nebulosa, planeta, viñeta) se desvanece a `base` exacta en el borde del rectángulo; así el video,
recoloreado a esa misma `base`, se funde con la diapositiva sin marco visible. Las estrellas sí cruzan.

Uso:  python3 fondos_espaciales.py  → escribe muestras en exports/presentaciones/espaciales/_fondos/
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter

_ESC = float(os.environ.get("FONDOS_ESCALA", "1"))  # 0.5 para iterar rápido
ANCHO, ALTO = int(3200 * _ESC), int(1800 * _ESC)
PX = ANCHO / 13.333  # píxeles por pulgada de diapositiva
EXP = Path(__file__).resolve().parent.parent / "exports"
CACHE = EXP / "presentaciones" / "espaciales" / ("_fondos" if _ESC == 1 else "_fondos_prev")  # las pruebas a escala reducida no ensucian la caché


def rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], np.float32) / 255


def _malla():
    yy, xx = np.mgrid[0:ALTO, 0:ANCHO].astype(np.float32)
    return xx, yy


XX, YY = _malla()


def suave(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def ruido(escala, octavas=5, semilla=0, persist=0.55):
    """Ruido fractal (value noise) en [0, 1], escala en píxeles de la octava base."""
    rng = np.random.default_rng(semilla)
    out = np.zeros((ALTO, ANCHO), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octavas):
        f = 2 ** o
        gh, gw = max(2, int(ALTO / escala * f) + 3), max(2, int(ANCHO / escala * f) + 3)
        g = rng.random((gh, gw)).astype(np.float32)
        capa = np.asarray(Image.fromarray(g, "F").resize((ANCHO, ALTO), Image.BICUBIC))
        out += amp * capa
        tot += amp
        amp *= persist
    out = gaussian_filter(out / tot, 2)
    lo, hi = np.percentile(out, (1, 99))
    return np.clip((out - lo) / (hi - lo), 0, 1)


# ---------------------------------------------------------------- estrellas
TEMPERATURAS = np.array([[0.70, 0.80, 1.00], [0.85, 0.90, 1.00], [1.00, 1.00, 1.00],
                         [1.00, 0.95, 0.85], [1.00, 0.85, 0.70]], np.float32)
PESO_T = np.array([0.18, 0.30, 0.30, 0.14, 0.08])


def estrellas(n, semilla=1, brillo=1.0, mascara=None, grandes=0, espigas=True, tinte=None):
    """Capa aditiva HxWx3 de estrellas. `mascara` (HxW en [0,1]) modula la densidad (Vía Láctea)."""
    rng = np.random.default_rng(semilla)
    x = rng.uniform(0, ANCHO - 1, n)
    y = rng.uniform(0, ALTO - 1, n)
    if mascara is not None:
        keep = rng.random(n) < mascara[y.astype(int), x.astype(int)]
        x, y = x[keep], y[keep]
    m = len(x)
    b = np.clip(rng.pareto(2.6, m) * 0.22 + 0.06, 0, 2.2) * brillo
    col = TEMPERATURAS[rng.choice(len(TEMPERATURAS), m, p=PESO_T)]
    if tinte is not None:
        col = col * 0.6 + rgb(tinte) * 0.4
    capa = np.zeros((ALTO, ANCHO, 3), np.float32)
    xi, yi = x.astype(int), y.astype(int)
    np.add.at(capa, (yi, xi), col * b[:, None])
    fina = gaussian_filter(capa, (0.75, 0.75, 0)) * 3.2
    medias = np.zeros_like(capa)
    sel = b > 0.55
    np.add.at(medias, (yi[sel], xi[sel]), col[sel] * b[sel, None])
    halo = gaussian_filter(medias, (3.0, 3.0, 0)) * 6.0
    out = fina + halo
    if grandes:
        orden = np.argsort(-b)[:grandes]
        for k in orden:
            _estrella_grande(out, x[k], y[k], col[k], 0.8 + rng.random() * 0.7, espigas, rng)
    return out


def _estrella_grande(capa, x, y, col, fuerza, espigas, rng):
    r = 90
    x0, x1 = int(max(0, x - r)), int(min(ANCHO, x + r))
    y0, y1 = int(max(0, y - r)), int(min(ALTO, y + r))
    xx, yy = XX[y0:y1, x0:x1] - x, YY[y0:y1, x0:x1] - y
    d2 = xx * xx + yy * yy
    g = np.exp(-d2 / (2 * 2.2 ** 2)) * 1.6 + np.exp(-d2 / (2 * 9 ** 2)) * 0.35 + np.exp(-d2 / (2 * 28 ** 2)) * 0.08
    if espigas:
        L = 55 + rng.random() * 30
        g += (np.exp(-np.abs(xx) / (L / 3)) * np.exp(-yy * yy / 1.2) + np.exp(-np.abs(yy) / (L / 3)) * np.exp(-xx * xx / 1.2)) * 0.55
    capa[y0:y1, x0:x1] += g[..., None] * col * fuerza


# ---------------------------------------------------------------- estructuras grandes
def via_lactea(angulo=-22, centro=(0.55, 0.45), ancho=0.16, semilla=3, colores=("#6d7bb8", "#c9a27a")):
    """Banda difusa con polvo oscuro. Devuelve (capa HxWx3, densidad HxW para estrellas extra)."""
    a = np.deg2rad(angulo)
    cx, cy = centro[0] * ANCHO, centro[1] * ALTO
    d = (-(XX - cx) * np.sin(a) + (YY - cy) * np.cos(a)) / ALTO
    banda = np.exp(-(d / ancho) ** 2)
    n1 = ruido(420, 6, semilla)
    n2 = ruido(180, 5, semilla + 7)
    polvo = suave(0.45, 0.8, ruido(260, 6, semilla + 11)) * np.exp(-(d / (ancho * 0.45)) ** 2)
    brillo = banda * (0.35 + 0.65 * n1) * (1 - 0.85 * polvo)
    c1, c2 = rgb(colores[0]), rgb(colores[1])
    mezcla = n2[..., None]
    capa = brillo[..., None] * (c1 * (1 - mezcla) + c2 * mezcla) * 0.22
    return capa, np.clip(banda * (0.4 + 0.6 * n1) * (1 - 0.7 * polvo), 0, 1)


def nebulosa(colores, escala=600, semilla=5, fuerza=0.5, centro=None, radio=0.6, contraste=1.6):
    """Nube fractal coloreada por una rampa (lista de hex). `centro`=(fx, fy) la concentra en una zona."""
    n = ruido(escala, 6, semilla, 0.58)
    f = ruido(escala * 0.45, 5, semilla + 3, 0.5)
    v = np.clip(n * 0.75 + f * 0.25, 0, 1) ** contraste
    if centro is not None:
        dx = (XX / ANCHO - centro[0]) * (ANCHO / ALTO)
        dy = YY / ALTO - centro[1]
        v = v * np.exp(-(dx * dx + dy * dy) / (radio ** 2))
    rampa = np.array([rgb(c) for c in colores])
    t = np.clip(n, 0, 0.999) * (len(rampa) - 1)
    i = t.astype(int)
    w = (t - i)[..., None]
    col = rampa[i] * (1 - w) + rampa[np.minimum(i + 1, len(rampa) - 1)] * w
    return col * v[..., None] * fuerza


def planeta(img, cx, cy, R, atm="#00d9ff", luz=-60, cuerpo="#03050d", fuerza=1.0, textura=0.06, semilla=9,
            luces=None):
    """Limbo planetario (cx, cy, R en px; el centro suele quedar fuera del lienzo). Ocluye lo de atrás."""
    dx, dy = XX - cx, YY - cy
    d = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    lf = 0.12 + 0.88 * np.clip(np.cos(ang - np.deg2rad(luz)), 0, 1) ** 1.6
    dentro = suave(R + 1.5, R - 1.5, d)
    cuerpo_c = rgb(cuerpo)
    tex = ruido(R * 0.18, 5, semilla) if textura else 0
    creciente = np.exp(-np.clip(R - d, 0, None) / (0.012 * R)) * lf ** 2
    cuerpo_img = cuerpo_c + (textura * tex)[..., None] * rgb(atm) * 0.5 * (0.3 + lf[..., None]) \
        + creciente[..., None] * rgb(atm) * 0.28 * fuerza
    if luces is not None:  # ciudades en el lado nocturno: puntos cálidos tenues
        rng = np.random.default_rng(semilla + 1)
        pts = np.zeros((ALTO, ANCHO), np.float32)
        k = 9000
        px_ = rng.uniform(0, ANCHO - 1, k).astype(int)
        py_ = rng.uniform(0, ALTO - 1, k).astype(int)
        grupo = ruido(R * 0.12, 4, semilla + 2)
        ok = (d[py_, px_] < R * 0.995) & (rng.random(k) < grupo[py_, px_] ** 3)
        np.add.at(pts, (py_[ok], px_[ok]), rng.uniform(0.3, 1, ok.sum()))
        noche = 1 - lf
        cuerpo_img = cuerpo_img + gaussian_filter(pts, 1.1)[..., None] * rgb(luces) * 2.2 * noche[..., None]
    img[:] = img * (1 - dentro[..., None]) + cuerpo_img * dentro[..., None]
    fuera = np.clip(d - R, 0, None)
    borde = np.exp(-((d - R) / (0.0022 * R + 1.2)) ** 2)
    halo = (np.exp(-fuera / (0.012 * R)) * 0.75 + np.exp(-fuera / (0.06 * R)) * 0.22) * (1 - dentro)
    brillo = halo + borde * 0.9
    img += (brillo * lf * fuerza)[..., None] * rgb(atm)
    # núcleo blanco del borde iluminado
    img += (borde * np.clip(np.cos(ang - np.deg2rad(luz)), 0, 1) ** 6 * 0.7 * fuerza)[..., None]
    return (cx + R * np.cos(np.deg2rad(luz)), cy + R * np.sin(np.deg2rad(luz)))


def destello(img, x, y, fuerza=1.0, col="#fff4e0", racha="#00d9ff"):
    """Sol asomando por el limbo: núcleo, halo y racha anamórfica horizontal."""
    dx, dy = XX - x, YY - y
    d2 = dx * dx + dy * dy
    g = np.exp(-d2 / (2 * 7 ** 2)) * 2.5 + np.exp(-d2 / (2 * 40 ** 2)) * 0.6 + np.exp(-d2 / (2 * 160 ** 2)) * 0.18
    img += (g * fuerza)[..., None] * rgb(col)
    r = np.exp(-(dx / 900) ** 2) * np.exp(-(dy / 2.2) ** 2) * 0.55 + np.exp(-(dx / 420) ** 2) * np.exp(-(dy / 9) ** 2) * 0.12
    img += (r * fuerza)[..., None] * rgb(racha)


def vineta(fuerza=0.55, radio=0.95):
    dx = (XX / ANCHO - 0.5) * 2
    dy = (YY / ALTO - 0.5) * 2
    d = np.sqrt(dx * dx * 0.8 + dy * dy)
    return 1 - fuerza * suave(radio * 0.55, radio * 1.45, d)


def lineas(dibujo, color, alfa=0.35, sobre=2):
    """Rasteriza un dibujo vectorial (función ImageDraw → None) con antialias. Devuelve capa HxWx3 aditiva."""
    L = Image.new("L", (ANCHO * sobre, ALTO * sobre), 0)
    dibujo(ImageDraw.Draw(L), sobre)
    L = L.resize((ANCHO, ALTO), Image.LANCZOS)
    return (np.asarray(L, np.float32) / 255 * alfa)[..., None] * rgb(color)


def mascara_zona(zona, caida=0.75):
    """1 lejos del rectángulo, 0 sobre su borde (y dentro). zona = (x, y, w, h) en pulgadas."""
    x, y, w, h = [v * PX for v in zona]
    dx = np.maximum(np.maximum(x - XX, XX - (x + w)), 0)
    dy = np.maximum(np.maximum(y - YY, YY - (y + h)), 0)
    d = np.sqrt(dx * dx + dy * dy)
    return suave(0, caida * PX, d)


def a_imagen(img):
    return Image.fromarray((np.clip(img, 0, 1) * 255 + 0.5).astype(np.uint8), "RGB")


def guardar(img, nombre, calidad=92):
    CACHE.mkdir(parents=True, exist_ok=True)
    ruta = CACHE / f"{nombre}.jpg"
    a_imagen(img).save(ruta, "JPEG", quality=calidad, subsampling=0, optimize=True)
    return ruta


# ---------------------------------------------------------------- dibujo vectorial (líneas)
def _rot_x(p, a):
    c, s = np.cos(a), np.sin(a)
    x, y, z = p
    return np.array([x, y * c - z * s, y * s + z * c])


def _rot_y(p, a):
    c, s = np.cos(a), np.sin(a)
    x, y, z = p
    return np.array([x * c + z * s, y, -x * s + z * c])


def globo_alambre(cx, cy, R, tilt=20, rot=25, orbitas=((1.3, 55, 30, 0.3), (1.52, 80, -50, 0.62), (1.85, 18, 10, 0.12)),
                  frente=1.0, atras=0.16, ancho=2, meridianos=12, paralelos=(-60, -40, -20, 0, 20, 40, 60), sats=True,
                  estacion=None):
    """Globo de alambre en proyección ortográfica con órbitas inclinadas (r/R, inclinación°, RAAN°, fase del satélite).
    Devuelve una función de dibujo para `lineas()` (los valores de gris codifican frente/atrás)."""
    t = np.deg2rad(tilt)

    def proyecta(p):
        q = _rot_x(p, -t)
        return cx + R * q[0], cy - R * q[1], q[2]

    def trazo(d, s, pts3, oculta_disco):
        X, Y, Z = proyecta(pts3)
        for k in range(len(X) - 1):
            vis = Z[k] > 0 or (oculta_disco and (X[k] - cx) ** 2 + (Y[k] - cy) ** 2 > (R * 1.004) ** 2)
            v = frente if vis else atras
            if v <= 0:
                continue
            d.line([(X[k] * s, Y[k] * s), (X[k + 1] * s, Y[k + 1] * s)], fill=int(255 * v), width=int(ancho * s))

    def dibujo(d, s):
        u = np.linspace(0, 2 * np.pi, 361)
        r0 = np.deg2rad(rot)
        # contorno
        d.ellipse([(cx - R) * s, (cy - R) * s, (cx + R) * s, (cy + R) * s], outline=int(255 * frente), width=int(ancho * 1.4 * s))
        for la in paralelos:
            f = np.deg2rad(la)
            p = np.array([np.cos(f) * np.sin(u), np.full_like(u, np.sin(f)), np.cos(f) * np.cos(u)])
            trazo(d, s, p, False)
        for m in range(meridianos):
            lam = m * np.pi / meridianos * 2 + r0
            f = np.linspace(-np.pi / 2, np.pi / 2, 181)
            p = np.array([np.cos(f) * np.sin(lam), np.sin(f), np.cos(f) * np.cos(lam)])
            trazo(d, s, p, False)
        for (rr, inc, raan, fase) in orbitas:
            p = np.array([rr * np.cos(u), np.zeros_like(u), rr * np.sin(u)])
            p = _rot_y(_rot_x(p, np.deg2rad(inc)), np.deg2rad(raan))
            trazo(d, s, p, True)
            if sats:
                k = int(fase * 360) % 360
                X, Y, Z = proyecta(p[:, k:k + 1])
                vis = Z[0] > 0 or (X[0] - cx) ** 2 + (Y[0] - cy) ** 2 > R * R
                if vis:
                    r = 7 * s
                    d.ellipse([X[0] * s - r, Y[0] * s - r, X[0] * s + r, Y[0] * s + r], fill=255)
                    r2 = 16 * s
                    d.ellipse([X[0] * s - r2, Y[0] * s - r2, X[0] * s + r2, Y[0] * s + r2], outline=200, width=int(1.5 * s))
        if estacion is not None:  # estación terrena: punto sobre la superficie visible
            la, lo = np.deg2rad(estacion[0]), np.deg2rad(estacion[1]) + r0
            p = np.array([[np.cos(la) * np.sin(lo)], [np.sin(la)], [np.cos(la) * np.cos(lo)]])
            X, Y, Z = proyecta(p)
            if Z[0] > 0:
                r = 9 * s
                d.polygon([(X[0] * s, Y[0] * s - r), (X[0] * s + r, Y[0] * s + r * 0.8), (X[0] * s - r, Y[0] * s + r * 0.8)], fill=255)
    return dibujo


def rejilla(paso_menor=0.25, paso_mayor=1.0, menor=0.35, mayor=0.8, cruces=True):
    """Rejilla de consola (en pulgadas de diapositiva) con cruces en las intersecciones mayores."""
    def dibujo(d, s):
        w, h = ANCHO * s, ALTO * s
        pm, pM = paso_menor * PX * s, paso_mayor * PX * s
        x = 0.0
        while x <= w:
            d.line([(x, 0), (x, h)], fill=int(255 * menor), width=max(1, int(0.6 * s)))
            x += pm
        y = 0.0
        while y <= h:
            d.line([(0, y), (w, y)], fill=int(255 * menor), width=max(1, int(0.6 * s)))
            y += pm
        x = 0.0
        while x <= w:
            d.line([(x, 0), (x, h)], fill=int(255 * mayor), width=max(1, int(1.0 * s)))
            x += pM
        y = 0.0
        while y <= h:
            d.line([(0, y), (w, y)], fill=int(255 * mayor), width=max(1, int(1.0 * s)))
            y += pM
    return dibujo


def reglas(margen=0.32, paso=0.1, color=1.0):
    """Reglas con marcas en los cuatro bordes (estilo instrumento)."""
    def dibujo(d, s):
        w, h = ANCHO * s, ALTO * s
        m = margen * PX * s
        p = paso * PX * s
        k, x = 0, m
        while x <= w - m:
            L = (0.12 if k % 10 == 0 else 0.07 if k % 5 == 0 else 0.035) * PX * s
            for y0, sg in ((m, 1), (h - m, -1)):
                d.line([(x, y0), (x, y0 + sg * L)], fill=int(255 * color), width=max(1, int(1.2 * s)))
            x += p
            k += 1
        k, y = 0, m
        while y <= h - m:
            L = (0.12 if k % 10 == 0 else 0.07 if k % 5 == 0 else 0.035) * PX * s
            for x0, sg in ((m, 1), (w - m, -1)):
                d.line([(x0, y), (x0 + sg * L, y)], fill=int(255 * color), width=max(1, int(1.2 * s)))
            y += p
            k += 1
        d.line([(m, m), (w - m, m)], fill=int(255 * color * 0.6), width=max(1, int(1 * s)))
        d.line([(m, h - m), (w - m, h - m)], fill=int(255 * color * 0.6), width=max(1, int(1 * s)))
        d.line([(m, m), (m, h - m)], fill=int(255 * color * 0.6), width=max(1, int(1 * s)))
        d.line([(w - m, m), (w - m, h - m)], fill=int(255 * color * 0.6), width=max(1, int(1 * s)))
    return dibujo


def radar(cx, cy, radios, marcas=True):
    """Anillos concéntricos con graduación angular (px de lienzo)."""
    def dibujo(d, s):
        for i, r in enumerate(radios):
            v = 0.9 if i == len(radios) - 1 else 0.5
            d.ellipse([(cx - r) * s, (cy - r) * s, (cx + r) * s, (cy + r) * s], outline=int(255 * v), width=int(1.6 * s))
        if marcas:
            r = radios[-1]
            for a in range(0, 360, 2):
                L = 34 if a % 30 == 0 else 18 if a % 10 == 0 else 8
                c, sn = np.cos(np.deg2rad(a)), np.sin(np.deg2rad(a))
                d.line([((cx + r * c) * s, (cy + r * sn) * s), ((cx + (r - L) * c) * s, (cy + (r - L) * sn) * s)],
                       fill=int(255 * (0.9 if a % 30 == 0 else 0.55)), width=int(1.4 * s))
        d.line([((cx - radios[-1]) * s, cy * s), ((cx + radios[-1]) * s, cy * s)], fill=90, width=int(1 * s))
        d.line([(cx * s, (cy - radios[-1]) * s), (cx * s, (cy + radios[-1]) * s)], fill=90, width=int(1 * s))
    return dibujo


def barrido(cx, cy, r, ang=-35, abertura=55):
    """Cuña de barrido de radar (intensidad HxW que decae hacia atrás del haz)."""
    a = np.rad2deg(np.arctan2(YY - cy, XX - cx))
    da = (ang - a) % 360
    d = np.sqrt((XX - cx) ** 2 + (YY - cy) ** 2)
    return np.where(da < abertura, 1 - da / abertura, 0) ** 2 * (d < r) * (0.4 + 0.6 * d / r)


def elipses_orbitales(cx, cy, orbitas, puntos=True):
    """Elipses (rx, ry, ángulo°, intensidad, fase) con un punto-satélite. Estilo línea técnica."""
    def dibujo(d, s):
        for (rx, ry, ang, v, fase) in orbitas:
            u = np.linspace(0, 2 * np.pi, 400)
            a = np.deg2rad(ang)
            x = rx * np.cos(u)
            y = ry * np.sin(u)
            X = cx + x * np.cos(a) - y * np.sin(a)
            Y = cy + x * np.sin(a) + y * np.cos(a)
            d.line([(X[k] * s, Y[k] * s) for k in range(len(X))], fill=int(255 * v), width=int(1.8 * s))
            if puntos and fase is not None:
                k = int(fase * 399)
                r = 9 * s
                d.ellipse([X[k] * s - r, Y[k] * s - r, X[k] * s + r, Y[k] * s + r], fill=255)
    return dibujo


def puntos_rejilla(paso=0.3, r=1.6, v=1.0):
    def dibujo(d, s):
        p = paso * PX * s
        y = p / 2
        while y < ALTO * s:
            x = p / 2
            while x < ANCHO * s:
                d.ellipse([x - r * s, y - r * s, x + r * s, y + r * s], fill=int(255 * v))
                x += p
            y += p
    return dibujo


def capa_lineas(dibujo, sobre=2):
    """Como lineas() pero devuelve la cobertura HxW en [0, 1] (para mezclar con cualquier color)."""
    L = Image.new("L", (ANCHO * sobre, ALTO * sobre), 0)
    dibujo(ImageDraw.Draw(L), sobre)
    L = L.resize((ANCHO, ALTO), Image.LANCZOS)
    return np.asarray(L, np.float32) / 255


# ---------------------------------------------------------------- composiciones por entorno
ATMOSFERAS = ["#00d9ff", "#37CFA0", "#F59E0B", "#a78bfa", "#ff3c6e", "#38bdf8", "#fbbf24", "#34d399"]


def _fundir_zona(img, base, capa_estrellas, zona, caida=0.75):
    """Deja `base` exacta en el borde del video; las estrellas se conservan."""
    if zona is None:
        return img + capa_estrellas
    m = mascara_zona(zona, caida)[..., None]
    return base + (img - base) * m + capa_estrellas


def orbita(tipo, var=0, zona=None):
    """Entorno «Órbita»: espacio profundo de la marca (#0a0e27), Vía Láctea, nebulosa cian y horizonte planetario."""
    base = rgb("#0a0e27")
    img = np.zeros((ALTO, ANCHO, 3), np.float32) + base
    sem = 11 + var * 17
    if tipo in ("portada", "cierre"):
        izq = tipo == "portada"
        mw, dens = via_lactea(angulo=-18 if izq else 20, centro=(0.5, 0.35), ancho=0.14, semilla=sem)
        img += mw
        img += nebulosa(["#0a0e27", "#0b3a5c", "#00d9ff", "#37CFA0"], 700, sem + 1, 0.22, (0.15 if izq else 0.85, 0.2), 0.55)
        img += nebulosa(["#0a0e27", "#3b1d6e", "#ff3c6e"], 600, sem + 2, 0.12, (0.9 if izq else 0.1, 0.15), 0.4)
        st = estrellas(5000, sem, 0.9) + estrellas(4000, sem + 1, 0.7, mascara=dens) + estrellas(40, sem + 2, 1.0, grandes=6)
        img += st
        if izq:
            p = planeta(img, ANCHO * 0.62, ALTO * 3.3, ALTO * 2.55, atm="#00d9ff", luz=-100, luces="#ffb347", semilla=sem)
        else:
            p = planeta(img, ANCHO * 0.30, ALTO * 3.25, ALTO * 2.5, atm="#37CFA0", luz=-72, luces="#ffb347", semilla=sem)
        destello(img, p[0], p[1] - 4, 0.9)
        img *= vineta(0.5)[..., None]
        return img
    if tipo == "seccion":
        atm = ATMOSFERAS[var % len(ATMOSFERAS)]
        mw, dens = via_lactea(angulo=-30 + var * 13, centro=(0.4, 0.4), ancho=0.13, semilla=sem)
        img += mw * 0.9
        img += nebulosa(["#0a0e27", "#0b2a4c", atm], 650, sem + 3, 0.20, (0.1, 0.15), 0.5)
        img += estrellas(5200, sem, 0.9) + estrellas(3000, sem + 1, 0.6, mascara=dens) + estrellas(30, sem + 2, 1.0, grandes=4)
        p = planeta(img, ANCHO * 0.96, ALTO * 1.98, ALTO * 1.06, atm=atm, luz=-128, semilla=sem, textura=0.08)
        destello(img, p[0], p[1] - 3, 0.55, racha=atm)
        img *= vineta(0.45)[..., None]
        return img
    # contenido y video: campo estelar sobrio, nebulosa en las esquinas
    mw, dens = via_lactea(angulo=-24, centro=(0.62, 0.3), ancho=0.12, semilla=sem)
    deco = img + mw * 0.55
    deco += nebulosa(["#0a0e27", "#0b3a5c", "#00d9ff"], 700, sem + 4, 0.16, (0.02, 0.05), 0.42)
    deco += nebulosa(["#0a0e27", "#123a3a", "#37CFA0"], 650, sem + 5, 0.10, (1.0, 1.0), 0.45)
    deco *= vineta(0.45)[..., None]
    st = estrellas(4200, sem, 0.75) + estrellas(2200, sem + 1, 0.55, mascara=dens) + estrellas(14, sem + 2, 0.8, grandes=3)
    return _fundir_zona(deco, base, st, zona if tipo == "video" else None)


def mision(tipo, var=0, zona=None):
    """Entorno «Control de misión»: consola casi negra con rejilla, reglas, radar y globo de alambre."""
    base = rgb("#050b16")
    img = np.zeros((ALTO, ANCHO, 3), np.float32) + base
    sem = 31 + var * 7
    img += nebulosa(["#050b16", "#0a2a3a", "#00d9ff"], 800, sem, 0.07, (0.8, 0.3), 0.8)
    img += estrellas(1800, sem, 0.45)
    cian, ambar = rgb("#22d3ee"), rgb("#FFB020")
    img += capa_lineas(rejilla(0.25, 1.0, 0.3, 0.7))[..., None] * cian * 0.16
    img += capa_lineas(reglas())[..., None] * cian * 0.5
    if tipo in ("portada", "cierre"):
        cx = ANCHO * (0.74 if tipo == "portada" else 0.26)
        g = capa_lineas(globo_alambre(cx, ALTO * 0.52, ALTO * 0.3, tilt=20, rot=30 + var * 40, estacion=(19.4, -99.1 - 30 - var * 40)))
        halo = gaussian_filter(g, 12)
        img += g[..., None] * cian * 0.75 + halo[..., None] * cian * 0.35
        img += capa_lineas(radar(cx, ALTO * 0.52, [ALTO * 0.66], True))[..., None] * cian * 0.3
    elif tipo == "seccion":
        cx, cy = ANCHO * 0.78, ALTO * 0.52
        rs = [ALTO * f for f in (0.12, 0.22, 0.32, 0.42)]
        img += capa_lineas(radar(cx, cy, rs))[..., None] * cian * 0.45
        img += barrido(cx, cy, rs[-1], ang=-35 - var * 50, abertura=60)[..., None] * cian * 0.18
        img += capa_lineas(elipses_orbitales(cx, cy, [(rs[2] * 1.05, rs[2] * 0.45, -20 - var * 11, 0.9, 0.2 + var * 0.1)]))[..., None] * ambar * 0.7
    else:  # contenido y video: arcos de radar en la esquina, muy tenues
        cx, cy = ANCHO * 1.02, ALTO * 1.05
        img += capa_lineas(radar(cx, cy, [ALTO * f for f in (0.35, 0.55, 0.75)]))[..., None] * cian * 0.16
    img *= vineta(0.35)[..., None]
    return img if tipo != "video" else _fundir_zona(img, base, 0, None)


def nebulosa_entorno(tipo, var=0, zona=None):
    """Entorno «Nebulosa»: gas violeta, magenta y turquesa, polvo y cúmulos; el texto va sobre penumbra."""
    base = rgb("#07051a")
    img = np.zeros((ALTO, ANCHO, 3), np.float32) + base
    sem = 51 + var * 13
    rampas = [["#07051a", "#2a0f4f", "#7b2cbf", "#ff3c8e", "#ffd6a5"],
              ["#07051a", "#0a1f4a", "#2563eb", "#22d3ee", "#e0f2fe"],
              ["#07051a", "#3b0a2a", "#be185d", "#fb923c", "#fef3c7"],
              ["#07051a", "#12213f", "#7c3aed", "#f0abfc", "#fdf4ff"]]
    rampa = rampas[var % len(rampas)] if tipo == "seccion" else rampas[0]
    rampa2 = ["#07051a", "#0b3040", "#14b8a6", "#a5f3fc"]
    if tipo in ("portada", "cierre", "seccion"):
        cen = {"portada": (0.72, 0.45), "cierre": (0.3, 0.5), "seccion": (0.8, 0.55)}[tipo]
        img += nebulosa(rampa, 900, sem, 0.85, cen, 0.75, contraste=1.8)
        img += nebulosa(rampa2, 700, sem + 1, 0.45, (cen[0] + 0.15, cen[1] + 0.3), 0.5, contraste=1.6)
        polvo = suave(0.5, 0.85, ruido(300, 6, sem + 2))
        img *= (1 - 0.6 * polvo * np.exp(-((XX / ANCHO - cen[0]) ** 2 + (YY / ALTO - cen[1]) ** 2) / 0.12))[..., None]
        img += estrellas(6000, sem, 0.9) + estrellas(50, sem + 3, 1.1, grandes=8)
        if tipo == "cierre":
            _anillado(img, ANCHO * 0.78, ALTO * 0.55, ALTO * 0.2)
        # penumbra donde va el texto
        lado = 0 if tipo != "cierre" else 1
        fx = XX / ANCHO if lado == 0 else 1 - XX / ANCHO
        img *= (0.35 + 0.65 * suave(0.18, 0.62, fx))[..., None] if tipo != "cierre" else 1
    else:
        img += nebulosa(rampa, 900, sem, 0.55, (0.95, 0.1), 0.6, contraste=1.8)
        img += nebulosa(rampa2, 700, sem + 1, 0.35, (0.05, 1.0), 0.55, contraste=1.6)
        img += estrellas(5000, sem, 0.8) + estrellas(12, sem + 3, 0.9, grandes=3)
        img *= vineta(0.4)[..., None]
    return img


def _anillado(img, cx, cy, R, atm="#ffd6a5", inc=0.28, ang=-18):
    """Planeta con anillos (parte trasera del anillo tapada por el planeta)."""
    a = np.deg2rad(ang)
    x, y = XX - cx, YY - cy
    xr = x * np.cos(a) + y * np.sin(a)
    yr = -x * np.sin(a) + y * np.cos(a)
    r_el = np.sqrt(xr ** 2 + (yr / inc) ** 2)
    anillo = (suave(R * 1.35, R * 1.45, r_el) - suave(R * 2.05, R * 2.25, r_el)) * (0.55 + 0.45 * np.sin(r_el / R * 40) ** 2)
    detras = (yr < 0)
    d = np.sqrt(x * x + y * y)
    dentro = suave(R + 1.5, R - 1.5, d)
    col = rgb(atm)
    img += (anillo * detras)[..., None] * col * 0.35
    luz = np.clip((-(x) * 0.6 - y * 0.8) / R, -1, 1)
    cuerpo = rgb("#1b0f2e") + (np.clip(luz, 0, 1) ** 1.5)[..., None] * rgb("#ffb4a2") * 0.55 \
        + (np.sin(yr / R * 9) * 0.03)[..., None]
    img[:] = img * (1 - dentro[..., None]) + cuerpo * dentro[..., None]
    img += (anillo * (~detras) * (1 - dentro * 0))[..., None] * col * 0.45
    borde = np.exp(-((d - R) / 2.5) ** 2) * np.clip(luz + 0.3, 0, 1)
    img += borde[..., None] * col * 0.8


def estacion(tipo, var=0, zona=None):
    """Entorno «Estación» (claro): papel técnico azulado, línea orbital fina y globo de alambre."""
    base = rgb("#F3F6FB")
    img = np.zeros((ALTO, ANCHO, 3), np.float32) + base
    azul, naranja = rgb("#1d4ed8"), rgb("#ea580c")
    # luz suave arriba a la izquierda
    img += (np.exp(-(((XX / ANCHO) - 0.1) ** 2 + ((YY / ALTO) - 0.0) ** 2) / 0.25) * 0.03)[..., None]

    def mezcla(cob, col, a):
        img[:] = img * (1 - cob[..., None] * a) + col * cob[..., None] * a

    mezcla(capa_lineas(puntos_rejilla(0.3, 1.5)), rgb("#94a3b8"), 0.5)
    if tipo in ("portada", "cierre"):
        cx = ANCHO * (0.78 if tipo == "portada" else 0.22)
        g = capa_lineas(globo_alambre(cx, ALTO * 0.55, ALTO * 0.32, tilt=22, rot=10 + var * 30, frente=1.0, atras=0.3, ancho=2.6,
                                      estacion=(19.4, -99.1 - 10 - var * 30)))
        mezcla(g, azul, 0.8)
    elif tipo == "seccion":
        cx, cy = ANCHO * 0.8, ALTO * 0.5
        orb = [(ALTO * 0.55, ALTO * 0.2, -18, 0.9, 0.15 + var * 0.1), (ALTO * 0.42, ALTO * 0.3, 25, 0.6, 0.6),
               (ALTO * 0.7, ALTO * 0.12, -5, 0.5, None)]
        mezcla(capa_lineas(elipses_orbitales(cx, cy, orb)), azul, 0.6)
        r0 = ALTO * .085
        disco = capa_lineas(lambda d, s: d.ellipse([(cx - r0) * s, (cy - r0) * s, (cx + r0) * s, (cy + r0) * s], fill=255))
        mezcla(disco, rgb("#dbe6fb"), 1.0)
        c = capa_lineas(globo_alambre(cx, cy, r0, orbitas=(), sats=False, meridianos=8, paralelos=(-45, 0, 45)))
        mezcla(c, azul, 0.7)
    else:
        orb = [(ALTO * 0.9, ALTO * 0.28, -14, 0.8, 0.3), (ALTO * 0.7, ALTO * 0.4, 30, 0.5, None)]
        mezcla(capa_lineas(elipses_orbitales(ANCHO * 1.02, ALTO * -0.02, orb)), azul, 0.32)
    return img


ENTORNOS_FONDO = {"orbita": orbita, "mision": mision, "nebulosa": nebulosa_entorno, "estacion": estacion}
GENERADORES = ENTORNOS_FONDO  # nombre → función(tipo, var, zona) → imagen HxWx3 float; los temas nuevos pueden registrar el suyo


def registrar_generador(nombre, funcion):
    """Un tema nuevo con fondo propio: `funcion(tipo, var, zona)` devuelve la imagen (ver orbita() como modelo)."""
    GENERADORES[nombre] = funcion


_T = np.array([[0.299, 0.587, 0.114], [0.596, -0.274, -0.322], [0.211, -0.523, 0.312]])  # RGB → YIQ


def rotar_matiz(x, grados):
    """Gira el matiz en el espacio YIQ (conserva la luminancia). Sirve para una imagen HxWx3 o un color rgb(3,) en [0, 1]."""
    a = np.deg2rad(grados)
    R = np.array([[1, 0, 0], [0, np.cos(a), -np.sin(a)], [0, np.sin(a), np.cos(a)]])
    M = np.linalg.inv(_T) @ R @ _T
    return np.clip(np.asarray(x, np.float32) @ M.T.astype(np.float32), 0, None)


def rotar_hex(h, grados):
    if not grados:
        return h
    c = np.clip(rotar_matiz(rgb(h), grados), 0, 1)
    return "#%02X%02X%02X" % tuple(int(round(v * 255)) for v in c)


def fondo(clave, generador, tipo, var=0, zona=None, tinte=0.0, rehacer=False):
    """Ruta JPEG (en caché, por `clave` = id del tema) del fondo de ese tipo de diapositiva.
    `generador`: nombre en GENERADORES o función; `tinte`: grados de giro de matiz (temas derivados)."""
    nombre = f"{clave}_{tipo}_{var}" + ("_z" if zona and tipo == "video" else "")
    ruta = CACHE / f"{nombre}.jpg"
    if ruta.exists() and not rehacer:
        return ruta
    gen = GENERADORES[generador] if isinstance(generador, str) else generador
    img = gen(tipo, var, zona)
    if tinte:
        img = rotar_matiz(img, tinte)
    return guardar(img, nombre)


if __name__ == "__main__":
    import sys
    for e in sys.argv[1:] or list(GENERADORES):
        for t in ("portada", "seccion", "contenido", "video", "cierre"):
            print(fondo(e, e, t, 0, (1.822, 1.5, 9.689, 5.45), rehacer=True))
