"""Fondos VERTICALES diseñados para reels (1080×1920), sin la «sombra» del centro.

Ronda 2026-10-07: al dueño no le gustó la sombra oscura que `fondo_orbital` ponía en la zona central (el entorno de las
presentaciones atenuado en un rectángulo). Aquí el fondo se compone PARA el reel: el cielo con estrellas queda limpio detrás
del diagrama y la decoración del tema vive en la franja de abajo (y < −8.2, la que Instagram tapa con su interfaz), con un
resplandor suave que sube sin bordes. Se usa sin atenuar: `preparar_serie(..., fondo="reel")`.

Generadores: «solar» (limbo del Sol con granulación, oscurecimiento al borde, corona en rayos, protuberancias y manchas).
`modo="cuerpo"` deja el limbo en la franja baja; `modo="cierre"` lo sube un poco (detrás del logo del cierre).
"""
import os
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw
from scipy.ndimage import gaussian_filter, gaussian_filter1d

W, H = 1080, 1920
_CACHE = Path(__file__).resolve().parents[3] / "exports" / "estudio" / "_fondos" / "reel"
VERSION = 12


def fila(y):
    """y de la escena (cuadro de 25.28 de alto) → fila de píxel."""
    return (12.64 - y) / 25.28 * H


def _rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], float) / 255


def _rampa(v, colores):
    cs = np.array([_rgb(c) for c in colores])
    v = np.clip(v, 0, 1) * (len(cs) - 1)
    i = np.minimum(v.astype(int), len(cs) - 2)
    f = (v - i)[..., None]
    return cs[i] * (1 - f) + cs[i + 1] * f


def _ruido(sigma, semilla):
    r = gaussian_filter(np.random.default_rng(semilla).random((H, W)), sigma)
    return (r - r.min()) / (r.max() - r.min() + 1e-9)


def _estrellas(img, n, semilla, hasta_fila):
    rng = np.random.default_rng(semilla)
    capa = np.zeros((H, W))
    ys = rng.uniform(0, hasta_fila, n).astype(int)
    xs = rng.uniform(0, W, n).astype(int)
    capa[ys, xs] = rng.uniform(0.25, 1.0, n) ** 2
    capa = gaussian_filter(capa, 0.7) * 4
    img += capa[..., None] * _rgb("#FFF4EA")[None, None] * 0.9


def solar(var=0, modo="cuerpo"):
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.ones((H, W, 3)) * _rgb("#0C0503")
    cima = fila(-9.35) if modo == "cuerpo" else fila(-7.0)               # punto más alto del limbo
    R = 2400.0
    cx = W / 2 + (0, -260, 300)[var % 3]
    cy = cima + R
    _estrellas(img, 520, 31 + var, cima - 120)
    r = np.hypot(xx - cx, yy - cy)
    ang = np.arctan2(yy - cy, xx - cx)
    # resplandor cálido que sube desde el limbo, sin bordes (no hay rectángulo atenuado)
    fuera = np.clip(r - R, 0, None)
    rng = np.random.default_rng(700 + var)
    rayos = gaussian_filter(rng.random(1440), 4, mode="wrap")
    rayos = 0.55 + 0.9 * (rayos - rayos.min()) / (rayos.max() - rayos.min())
    k = ((ang + np.pi) / (2 * np.pi) * 1440).astype(int) % 1440
    dentro = np.clip((R + 1.5 - r) / 3.0, 0, 1)
    corona = (np.exp(-fuera / 26) * 0.85 + np.exp(-fuera / 150) * 0.30 * rayos[k] + np.exp(-fuera / 520) * 0.10) * (1 - dentro)
    img += corona[..., None] * _rgb("#FFA65C")
    # disco: granulación + oscurecimiento al limbo + manchas
    mu = np.sqrt(np.clip(1 - (r / R) ** 2, 0, 1))
    gran = 0.55 * _ruido(2.2, 900 + var) + 0.45 * _ruido(9, 901 + var)
    brillo = (0.30 + 0.70 * mu ** 0.5) * (0.55 + 0.6 * gran)
    for dx, dy, s in ((-180, 70, 22), (-140, 95, 12), (230, 120, 16)):          # manchas: más frías, se ven oscuras
        d = np.hypot(xx - (W / 2 + dx), yy - (cima + dy))
        brillo *= 1 - 0.75 * np.exp(-(d / s) ** 2) - 0.25 * np.exp(-(d / (2.4 * s)) ** 2)
    sol = _rampa(brillo ** 1.25, ["#4A1002", "#A82E08", "#E2530C", "#FB923C", "#FDBA74", "#FFF1D0"])
    img = img * (1 - dentro[..., None]) + sol * dentro[..., None]
    # protuberancias en arco sobre el limbo
    capa = Image.new("L", (W, H), 0)
    dib = ImageDraw.Draw(capa)
    for a0, alto in ((-1.66, 48), (-1.42, 32), (-1.80, 28)):
        a0 += rng.uniform(-0.03, 0.03) + (0, 0.05, -0.05)[var % 3]
        a1 = a0 + rng.uniform(0.025, 0.045)
        p0 = np.array([cx + R * np.cos(a0), cy + R * np.sin(a0)])
        p2 = np.array([cx + R * np.cos(a1), cy + R * np.sin(a1)])
        am = (a0 + a1) / 2
        p1 = np.array([cx + (R + 2.2 * alto) * np.cos(am), cy + (R + 2.2 * alto) * np.sin(am)])
        for j in range(5):
            off = (j - 2) * 2.5
            t = np.linspace(0, 1, 80)[:, None]
            pts = (1 - t) ** 2 * p0 + 2 * (1 - t) * t * (p1 + off) + t ** 2 * p2
            dib.line([tuple(p) for p in pts], fill=150, width=6)
    prot = gaussian_filter(np.asarray(capa, float) / 255, 3.2) * (1 - dentro)
    img += prot[..., None] * _rgb("#FF5A2D") * 0.9 + gaussian_filter(prot, 12)[..., None] * _rgb("#FF3D1F") * 1.0
    return np.clip(img, 0, 1)


def espectro(var=0, modo="cuerpo"):
    """SDR: el «horizonte» es el trazo del espectro (picos en las portadoras) y debajo cae la cascada con la S del Doppler
    de un pase; arriba, cielo limpio con pocas estrellas y una rejilla de frecuencia muy tenue que se apaga al subir."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    base = _rgb("#050A0F")
    img = np.ones((H, W, 3)) * base
    cima = fila(-9.75) if modo == "cuerpo" else fila(-7.2)
    rng = np.random.default_rng(1200 + var)
    _estrellas(img, 380, 61 + var, cima - 160)
    # portadoras fijas y la del satélite (Doppler en S a lo largo de la cascada)
    xs = np.arange(W)
    portadoras = [(0.18 + 0.04 * var, 0.55, 3.0), (0.47, 0.35, 2.2), (0.79 - 0.03 * var, 0.6, 3.5), (0.90, 0.25, 1.8)]
    banda = yy >= cima
    t = np.clip((yy - cima) / (H - cima), 0, 1)
    grano = gaussian_filter(rng.random((H, W)), (1.0, 0.7)); grano = (grano - grano.mean()) / grano.std()
    lento = gaussian_filter(rng.random((H, W)), (30, 60)); lento = (lento - lento.mean()) / lento.std()
    cas = 0.27 + 0.07 * grano + 0.06 * lento - 0.10 * t
    for fx, a, w in portadoras:
        cas += a * 0.8 * np.exp(-((xx - fx * W) / w) ** 2) * (0.75 + 0.25 * np.sin(yy / 23 + fx * 9))
    sat_x = W * (0.56 - 0.20 * np.tanh((t - 0.45) / 0.16) + (0, -0.08, 0.06)[var % 3])
    cas += 0.95 * np.exp(-((xx - sat_x) / 4.0) ** 2) * np.exp(-((t - 0.45) / 0.5) ** 2)
    for y0 in rng.uniform(0.15, 0.9, 5):                                   # ráfagas cortas
        x0 = rng.uniform(0.1, 0.9) * W
        cas += 0.45 * np.exp(-((yy - (cima + y0 * (H - cima))) / 3.0) ** 2) * np.exp(-((xx - x0) / 60) ** 2)
    colores = _rampa(np.clip(cas, 0, 1) ** 1.1, ["#03070C", "#06202E", "#0B4A60", "#0E7490", "#22D3EE", "#A5F3FC", "#FDE047"])
    img = np.where(banda[..., None], colores, img)
    # trazo del espectro (el horizonte), con resplandor que sube sin bordes
    ruido = gaussian_filter1d(rng.random(W), 2) * 0.25
    amp = ruido + sum(a * 1.6 * np.exp(-((xs - fx * W) / (w * 2.5)) ** 2) for fx, a, w in portadoras)
    amp += 1.5 * np.exp(-((xs - W * (0.56 + 0.20 + (0, -0.08, 0.06)[var % 3])) / 9) ** 2)
    linea_y = cima - 6 - amp * 58
    d = yy - linea_y[None, :]
    trazo = np.exp(-(d / 2.2) ** 2)
    bajo = (d > 0) & (yy < cima)                                           # entre el trazo y la cascada: relleno tenue
    img += trazo[..., None] * _rgb("#67E8F9") * 1.2 + gaussian_filter(trazo, 6)[..., None] * _rgb("#22D3EE") * 0.8
    img = np.where(bajo[..., None], img * 0.7 + _rgb("#0E7490") * 0.18, img)
    fuera = np.clip(cima - yy, 0, None)
    img += (np.exp(-fuera / 40) * 0.30 + np.exp(-fuera / 220) * 0.17 + np.exp(-fuera / 1000) * 0.13)[..., None] * _rgb("#22D3EE") * (yy < cima)[..., None]
    # rejilla de frecuencia, tenue y solo cerca de la franja
    reja = np.zeros((H, W))
    for gx in np.linspace(0, W, 13)[1:-1]:
        reja += np.exp(-((xx - gx) / 0.8) ** 2)
    img += (reja * np.exp(-fuera / 380) * (yy < cima) * 0.10)[..., None] * _rgb("#22D3EE")
    return np.clip(img, 0, 1)


def neuronal(var=0, modo="cuerpo"):
    """IA: el «horizonte» es la capa de entrada de una red neuronal (nodos unidos por un trazo luminoso); debajo, capas
    más profundas con conexiones de peso positivo (turquesa) y negativo (violeta) y algunos pulsos de activación."""
    from PIL import ImageFilter
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    img = np.ones((H, W, 3)) * _rgb("#120C24")
    cima = fila(-9.75) if modo == "cuerpo" else fila(-7.2)
    rng = np.random.default_rng(1500 + var)
    _estrellas(img, 340, 81 + var, cima - 160)
    curva = lambda x: cima + ((x - W / 2) / (W / 2)) ** 2 * 34          # horizonte apenas curvo
    filas = []
    for k in range(7):
        n = 13 + (k % 2) + (var % 2)
        xsn = np.linspace(-0.02, 1.02, n) * W + rng.uniform(-18, 18, n)
        filas.append([(x, curva(x) + k * 62 + (rng.uniform(-6, 6) if k else 0)) for x in xsn])
    lin_pos = Image.new("L", (W, H), 0); lin_neg = Image.new("L", (W, H), 0); nodos = Image.new("L", (W, H), 0)
    dp, dn, dd = ImageDraw.Draw(lin_pos), ImageDraw.Draw(lin_neg), ImageDraw.Draw(nodos)
    for a, b in zip(filas[:-1], filas[1:]):
        for (x0, y0) in a:
            for (x1, y1) in sorted(b, key=lambda q: abs(q[0] - x0))[:3]:
                w = rng.uniform(0.25, 1.0)
                (dp if rng.random() < 0.55 else dn).line([(x0, y0), (x1, y1)], fill=int(150 * w), width=2)
    for k, f in enumerate(filas):
        for (x, y) in f:
            r = 6 if k == 0 else 4.5
            dd.ellipse([x - r, y - r, x + r, y + r], fill=255 if k == 0 else int(rng.uniform(120, 230)))
    dd.line([(x, y) for (x, y) in filas[0]], fill=110, width=2)          # el horizonte: la capa de entrada unida
    P = np.asarray(lin_pos, float) / 255; N = np.asarray(lin_neg, float) / 255; D = np.asarray(nodos, float) / 255
    pulso = np.zeros((H, W))
    for _ in range(16):                                                 # activaciones viajando por algunas aristas
        k = rng.integers(0, 6); (x0, y0) = filas[k][rng.integers(0, len(filas[k]))]
        (x1, y1) = sorted(filas[k + 1], key=lambda q: abs(q[0] - x0))[0]; f = rng.uniform(0.2, 0.8)
        pulso += np.exp(-(((xx - (x0 + f * (x1 - x0))) ** 2 + (yy - (y0 + f * (y1 - y0))) ** 2) / 30.0))
    debajo = (yy >= curva(xx) - 2)
    img = np.where(debajo[..., None], img * 0.7 + _rgb("#1B1036") * 0.3, img)
    img += P[..., None] * _rgb("#2DD4BF") * 0.75 + N[..., None] * _rgb("#C084FC") * 0.75
    img += gaussian_filter(P + N, 3)[..., None] * _rgb("#7C3AED") * 0.35
    img += D[..., None] * _rgb("#F3EEFF") + gaussian_filter(D, 5)[..., None] * _rgb("#C084FC") * 1.6
    img += pulso[..., None] * _rgb("#F9A8D4") + gaussian_filter(pulso, 6)[..., None] * _rgb("#F9A8D4") * 1.5
    fuera = np.clip(curva(xx) - yy, 0, None)
    img += (np.exp(-fuera / 40) * 0.22 + np.exp(-fuera / 220) * 0.15 + np.exp(-fuera / 1000) * 0.12)[..., None] * _rgb("#A855F7") * (~debajo)[..., None]
    return np.clip(img, 0, 1)


def robotica(var=0, modo="cuerpo"):
    """Robótica: el «horizonte» es una hilera de engranes de metal con borde naranja de seguridad; el resplandor sube por distancia
    a los engranes (sin bordes). Cielo grafito con estrellas finas y una regla de cotas en el borde inferior."""
    from scipy.ndimage import distance_transform_edt
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    base = _rgb("#111820")
    img = np.ones((H, W, 3)) * base
    cima = fila(-9.75) if modo == "cuerpo" else fila(-7.2)
    rng = np.random.default_rng(1700 + var)
    _estrellas(img, 300, 91 + var, cima - 200)
    gears = [(-0.02, 250, 22), (0.31, 175, 18), (0.58, 215, 20), (0.93, 270, 24)]
    gears = [(g[0] + (0, 0.04, -0.03)[var % 3], g[1], g[2]) for g in gears]
    masc = Image.new("L", (W, H), 0); dm = ImageDraw.Draw(masc)
    huecos = Image.new("L", (W, H), 0); dh = ImageDraw.Draw(huecos)
    for fx, R, nt in gears:
        cx, cy = fx * W, cima + R * 0.62
        pts = []
        for k in range(nt * 4):
            a = 2 * np.pi * k / (nt * 4) + 0.3 * fx
            r = R if (k % 4) in (0, 1) else R * 0.86
            pts.append((cx + r * np.cos(a), cy + r * np.sin(a)))
        dm.polygon(pts, fill=255)
        dh.ellipse([cx - R * 0.32, cy - R * 0.32, cx + R * 0.32, cy + R * 0.32], fill=255)
        for j in range(6):
            a = 2 * np.pi * j / 6
            hx, hy = cx + R * 0.62 * np.cos(a), cy + R * 0.62 * np.sin(a)
            dh.ellipse([hx - R * 0.06, hy - R * 0.06, hx + R * 0.06, hy + R * 0.06], fill=255)
    M = np.asarray(masc, float) / 255; Hh = np.asarray(huecos, float) / 255
    lo_alto = M * (1 - Hh)
    d_fuera = distance_transform_edt(M < 0.5)                                  # distancia al engrane más cercano (afuera)
    d_dentro = distance_transform_edt(M >= 0.5)
    cepillado = gaussian_filter(rng.random((H, W)), (0.6, 40)); cepillado = (cepillado - cepillado.mean()) / (cepillado.std() + 1e-9)
    metal = _rgb("#2A3644")[None, None] * (0.75 + 0.35 * np.clip((yy - cima) / 220, 0, 1))[..., None] + 0.025 * cepillado[..., None]
    img = np.where((M >= 0.5)[..., None], metal, img)
    img = np.where((Hh >= 0.5)[..., None], base * 0.7, img)                       # núcleo y tornillos: huecos oscuros
    borde = np.exp(-(np.abs(np.where(M >= 0.5, d_dentro, d_fuera)) / 1.6) ** 2) * np.clip(1 - np.abs(Hh - 0.5) * 0, 0, 1)
    img += borde[..., None] * _rgb("#FF7A1A") * 1.1
    fuera = np.where(M < 0.5, d_fuera, 0.0)
    img += ((np.exp(-fuera / 40) * 0.30 + np.exp(-fuera / 200) * 0.14 + np.exp(-fuera / 900) * 0.07) * (M < 0.5))[..., None] * _rgb("#FF7A1A")
    # regla de cotas en el borde inferior
    for x in range(0, W, 24):
        largo = 26 if x % 120 == 0 else 12
        img[H - 8 - largo:H - 8, x:x + 2] = _rgb("#FF7A1A") * 0.55
    return np.clip(img, 0, 1)


def electromagnetismo(var=0, modo="cuerpo"):
    """Electromagnetismo: el «horizonte» es el limbo de la Tierra (siempre azul) con una cortina de aurora verde y unas pocas líneas
    del campo dipolar (r = L·sen²θ) que salen del limbo y vuelven a él, solo en la franja baja. Resplandor azul que sube sin bordes."""
    yy, xx = np.mgrid[0:H, 0:W].astype(float)
    base = _rgb("#0A1124")
    img = np.ones((H, W, 3)) * base
    cima = fila(-9.6) if modo == "cuerpo" else fila(-7.2)
    rng = np.random.default_rng(2300 + var)
    _estrellas(img, 320, 131 + var, cima - 260)
    R = 3000.0
    cx = W * (0.5 + (0.0, 0.08, -0.08)[var % 3])
    cy = cima + R
    d = np.hypot(xx - cx, yy - cy)
    dentro = d < R
    prof = np.clip((R - d) / 140, 0, 1)
    nubes = _ruido(4, 77 + var)
    tierra = _rampa(prof, ["#2C86D6", "#14478C", "#0B2A57", "#071A38"]) * (0.9 + 0.25 * nubes[..., None])
    img = np.where(dentro[..., None], tierra, img)
    fuera = np.clip(d - R, 0, None)
    img += (np.exp(-fuera / 6) * 0.45 * ~dentro + np.exp(-(R - d).clip(0) / 5) * 0.25 * dentro)[..., None] * _rgb("#8FD8FF")   # atmósfera: borde fino
    img += ((np.exp(-fuera / 40) * 0.16 + np.exp(-fuera / 200) * 0.09 + np.exp(-fuera / 900) * 0.045) * ~dentro)[..., None] * _rgb("#3B9CFF")
    # aurora: cortina de rayos verticales sobre el limbo (verde abajo, violeta arriba), más intensa hacia un lado
    cortina = gaussian_filter1d(rng.random(W), 2.0); cortina = (cortina - cortina.min()) / (np.ptp(cortina) + 1e-9)
    lado = np.exp(-((np.arange(W) - W * (0.28, 0.7, 0.45)[var % 3]) / (W * 0.30)) ** 2)
    alto = 28 + 55 * cortina * lado
    perfil = np.clip(fuera / 8, 0, 1) * np.exp(-np.clip(fuera - 8, 0, None) / alto[None, :]) * (fuera < 260)
    inten = (0.2 + 0.8 * cortina[None, :] ** 2) * lado[None, :] * perfil * ~dentro
    mezcla = np.clip(fuera / 110, 0, 1)[..., None]
    img += inten[..., None] * (_rgb("#3DFF9A") * (1 - mezcla) * 0.75 + _rgb("#B07CFF") * mezcla * 0.5)
    # líneas de campo: arcos dipolares con los pies sobre el limbo, solo por debajo de y = −8.3
    capa = Image.new("L", (W, H), 0); dl = ImageDraw.Draw(capa)
    tope = fila(-8.3) if modo == "cuerpo" else cima - 200
    alto_max = max(cima - tope, 40)
    for k, (x0, ancho) in enumerate(((0.5, 0.95), (0.5, 0.7), (0.5, 0.48), (0.5, 0.28))):
        th = np.linspace(0.0, np.pi, 400)
        xs_ = W * (x0 + (0.0, 0.08, -0.08)[var % 3]) - np.cos(th) * W * ancho / 2
        ys_ = cima - alto_max * (ancho / 0.95) ** 0.8 * np.sin(th) ** 3
        pts = [(float(a), float(b) + (R - np.sqrt(max(R * R - (a - cx) ** 2, 0)))) for a, b in zip(xs_, ys_)]
        dl.line(pts, fill=int(120 - 20 * k), width=2)
    lineas = gaussian_filter(np.asarray(capa, float) / 255, 0.7)
    img += lineas[..., None] * _rgb("#8CC8FF") * 0.55 * ~dentro[..., None]
    return np.clip(img, 0, 1)

GENERADORES = {"solar": solar, "espectro": espectro, "neuronal": neuronal, "robotica": robotica, "electromagnetismo": electromagnetismo}


def fondo_reel(tema, var=0, modo="cuerpo"):
    """Ruta del PNG (en caché, escritura atómica: varios renders a la vez)."""
    _CACHE.mkdir(parents=True, exist_ok=True)
    ruta = _CACHE / f"{tema}_{modo}_{var}_v{VERSION}.png"
    if ruta.exists():
        return ruta
    img = GENERADORES[tema](var, modo)
    tmp = ruta.with_suffix(f".{os.getpid()}.tmp.png")
    Image.fromarray((img * 255).astype(np.uint8)).save(tmp)
    tmp.replace(ruta)
    return ruta


def tiene(tema):
    return tema in GENERADORES


if __name__ == "__main__":
    for v in range(3):
        for m in ("cuerpo", "cierre"):
            print(fondo_reel("solar", v, m), fondo_reel("espectro", v, m), fondo_reel("neuronal", v, m), fondo_reel("robotica", v, m))
