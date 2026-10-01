"""Segunda tanda de fondos por materia (misma firma y reglas que fondos_tematicos.py).

  espectro      SDR: cascada (waterfall) con portadoras, ráfagas y la curva Doppler de un pase, y el trazo del espectro
  neuronal      IA: red neuronal con pesos (positivos/negativos), pulsos de activación y matriz de atención
  caos          Atractor de Lorenz integrado (σ=10, ρ=28, β=8/3) y diagrama de bifurcación del mapa logístico
  aerodinamica  Flujo potencial alrededor de un perfil de Joukowski (condición de Kutta) y cono de Mach con su ángulo
  solar         Limbo del Sol con granulación, oscurecimiento al borde, corona y protuberancias en arco
  cuaderno      CLARO: papel milimétrico de ingeniería con bocetos a tinta (elipse orbital, transferencia de Hohmann)
Vista previa: python3 fondos_tematicos_2.py [tema …]  (FONDOS_ESCALA=0.5 para iterar)
"""
import math

import numpy as np
from scipy.ndimage import gaussian_filter, gaussian_filter1d

import fondos_espaciales as F
from fondos_tematicos import (E, H, W, XX, YY, _bezier, _c, _l, _masc_esq, _punteada, _rampa, _txt, base_color, cap, fin,
                              hoja_contacto, iso, mezcla, pintar, rgb)


# ================================================================ ESPECTRO (SDR)
def _cascada(sem, x0, x1, y0, y1, doppler=True):
    """Intensidad (0-1) de una cascada en el rectángulo (px): tiempo hacia abajo, frecuencia a lo ancho."""
    rng = np.random.default_rng(sem)
    w, h = int(x1 - x0), int(y1 - y0)
    f = np.linspace(0, 1, w)[None, :]
    t = np.linspace(0, 1, h)[:, None]
    piso = 0.10 + 0.05 * gaussian_filter(rng.random((h, w)).astype(np.float32), (0.8, 1.5))
    sen = np.zeros((h, w), np.float32)
    for fc, ancho, nivel in ((0.18, 0.004, 0.55), (0.31, 0.010, 0.35), (0.72, 0.003, 0.65), (0.86, 0.006, 0.40)):
        deriva = fc + 0.004 * np.sin(2 * np.pi * (t * rng.uniform(1, 3) + rng.random()))
        fluct = 0.75 + 0.25 * gaussian_filter1d(rng.random(h).astype(np.float32), 6)[:, None]
        sen += nivel * fluct * np.exp(-((f - deriva) / ancho) ** 2)
    if doppler:  # pase de un satélite: la frecuencia baja en S (Doppler) alrededor del máximo acercamiento
        fd = 0.52 + 0.075 * np.tanh(-(t - 0.5) * 7)
        sen += 0.9 * np.exp(-((f - fd) / 0.0055) ** 2) * (0.35 + 0.65 * np.exp(-((t - 0.5) / 0.32) ** 2))
    for _ in range(14):  # ráfagas de paquetes
        fb, tb, lb = rng.uniform(0.05, 0.95), rng.uniform(0, 1), rng.uniform(0.01, 0.04)
        sen += 0.45 * np.exp(-((f - fb) / 0.006) ** 2) * ((t > tb) & (t < tb + lb))
    return np.clip(piso + sen, 0, 1)


def _pegar(img, x0, y0, rgbimg, alfa):
    h, w = rgbimg.shape[:2]
    y1, x1 = min(H, y0 + h), min(W, x0 + w)
    img[y0:y1, x0:x1] = img[y0:y1, x0:x1] * (1 - alfa[: y1 - y0, : x1 - x0, None]) + rgbimg[: y1 - y0, : x1 - x0] * alfa[: y1 - y0, : x1 - x0, None]


VIRIDIS = ["#050A0F", "#13234A", "#1D5C7A", "#1FA187", "#73D055", "#FDE725"]


def espectro(tipo, var=0, zona=None):
    """SDR: cascada con portadoras, ráfagas y la S del Doppler de un pase, trazo del espectro y escala en MHz/dB."""
    BASE = "#050A0F"
    cian, amarillo = "#22D3EE", "#FDE047"
    img = base_color(BASE)
    sem = 301 + var * 7
    if tipo in ("portada", "cierre", "seccion"):
        x0 = int(0.40 * W) if tipo != "seccion" else int(0.30 * W)
        y0, y1 = int(0.30 * H), H
        c = _cascada(sem, x0, W, y0, y1)
        col = _rampa(c ** 0.9, VIRIDIS)
        a = (F.suave(x0, x0 + 0.30 * W, XX[y0:y1, x0:W]) * (0.55 + 0.45 * F.suave(y0, y0 + 0.25 * H, YY[y0:y1, x0:W])))
        _pegar(img, x0, y0, col, a * (0.85 if tipo != "seccion" else 0.6))
        # trazo del espectro: promedio de las últimas filas, arriba de la cascada
        perfil = gaussian_filter1d(c[-60:].mean(0), 2)
        xs = np.arange(x0, W)
        ytr = y0 - 0.04 * H - (perfil - perfil.min()) / (np.ptp(perfil) + 1e-6) * 0.18 * H

        def traza(d, s):
            pts = list(zip(xs[::2], ytr[::2]))
            _l(d, s, pts, 1.0, 2.0)
        capa = cap(traza)
        pintar(img, capa * F.suave(x0, x0 + 0.25 * W, XX), cian, 0.9, 0.35)

        def escala(d, s):
            for k, db in enumerate((-40, -60, -80, -100)):
                yy = y0 - 0.04 * H - (3 - k) / 3 * 0.18 * H
                _punteada(d, s, [(x0 + 0.18 * W, yy), (W - 0.02 * W, yy)], 0.35, 1.0, 6, 10)
                _txt(d, s, W - 0.105 * W, yy - 26 * E, f"{db} dBm", 20, 0.7)
            for k, mhz in enumerate(("137.100", "137.500", "137.900", "138.300")):
                xx = x0 + (0.30 + 0.19 * k) * (W - x0)
                _l(d, s, [(xx, y0 - 0.005 * H), (xx, y0 + 0.012 * H)], 0.8, 1.4)
                _txt(d, s, xx - 0.03 * W, y0 + 0.018 * H, mhz, 20, 0.75)
            _txt(d, s, x0 + 0.30 * (W - x0), y0 - 0.27 * H, "FFT 4096  ·  2.4 MS/s  ·  NOAA / METEOR", 22, 0.7)
        pintar(img, cap(escala) * F.suave(x0, x0 + 0.20 * W, XX), "#9FB8C8", 0.75)
        img += (np.exp(-((XX - W) ** 2 + (YY - 0.55 * H) ** 2) / (2 * (0.45 * H) ** 2)) * 0.05)[..., None] * rgb(amarillo)
        return fin(img, BASE, tipo, zona, 0.45)
    # contenido / video: tira de cascada en el borde derecho y trazo tenue abajo
    x0 = int(W - 0.07 * W)
    c = _cascada(sem, x0, W, 0, H, doppler=False)
    _pegar(img, x0, 0, _rampa(c, VIRIDIS), F.suave(x0, W, XX[:, x0:W]) * 0.55)

    def traza(d, s):
        xs = np.linspace(0.55 * W, W, 400)
        rng = np.random.default_rng(sem)
        y = H - 0.05 * H - 0.025 * H * (np.exp(-((xs - 0.8 * W) / (0.01 * W)) ** 2) + 0.4 * np.exp(-((xs - 0.68 * W) / (0.006 * W)) ** 2)) \
            - 0.004 * H * gaussian_filter1d(rng.random(400), 1.5)
        _l(d, s, list(zip(xs, y)), 1.0, 1.6)
    pintar(img, cap(traza) * F.suave(0.55 * W, 0.80 * W, XX), cian, 0.35)
    return fin(img, BASE, tipo, zona, 0.4)


# ================================================================ NEURONAL (IA)
def _red(cx, cy, ancho, alto, capas, sem):
    rng = np.random.default_rng(sem)
    nodos = []
    for i, n in enumerate(capas):
        x = cx - ancho / 2 + ancho * i / (len(capas) - 1)
        ys = [cy - alto / 2 + alto * (j + 0.5) / n for j in range(n)]
        nodos.append([(x, y) for y in ys])
    aristas = []
    for i in range(len(capas) - 1):
        for a in nodos[i]:
            for b in nodos[i + 1]:
                aristas.append((a, b, rng.normal()))
    return nodos, aristas


def neuronal(tipo, var=0, zona=None):
    """IA: red neuronal con pesos positivos (turquesa) y negativos (magenta), pulsos de activación y matriz de atención."""
    BASE = "#0A0714"
    turq, mag, violeta = "#2DD4BF", "#E879F9", "#A78BFA"
    img = base_color(BASE)
    img += F.nebulosa(["#0A0714", "#1A1038", "#3B1D6E"], 900, 401 + var, 0.10, (0.85, 0.35), 0.9)
    img += F.estrellas(600, 411 + var, 0.3)
    sem = 421 + var * 5
    if tipo in ("portada", "cierre"):
        nodos, aristas = _red(1.30 * H, 0.52 * H, 0.78 * H, 0.80 * H, (4, 7, 9, 7, 3), sem)
        alc = 0.15 + 0.85 * F.suave(0.38 * W, 0.80 * W, XX)
        pos = cap(lambda d, s: [_l(d, s, [a, b], min(1, 0.25 + 0.35 * abs(wt)), 1.1) for a, b, wt in aristas if wt > 0])
        neg = cap(lambda d, s: [_l(d, s, [a, b], min(1, 0.25 + 0.35 * abs(wt)), 1.1) for a, b, wt in aristas if wt <= 0])
        pintar(img, pos * alc, turq, 0.40)
        pintar(img, neg * alc, mag, 0.30)
        rng = np.random.default_rng(sem + 1)
        camino = [nodos[0][1]] + [nodos[i][rng.integers(len(nodos[i]))] for i in range(1, len(nodos))]
        hot = cap(lambda d, s: _l(d, s, camino, 1.0, 3.0))
        pintar(img, hot, "#F5F3FF", 0.85, 0.6)
        for capa_n in nodos:
            for (x, y) in capa_n:
                dx, dy = XX - x, YY - y
                d2 = dx * dx + dy * dy
                r = 0.017 * H
                anillo = np.exp(-((np.sqrt(d2) - r) / (0.0025 * H)) ** 2)
                img += (anillo * 0.9 + np.exp(-d2 / (2 * (r * 1.8) ** 2)) * 0.18)[..., None] * rgb(violeta) * alc[..., None]
        for (x, y) in camino:  # neuronas activas
            d2 = (XX - x) ** 2 + (YY - y) ** 2
            img += (np.exp(-d2 / (2 * (0.012 * H) ** 2)) * 1.1)[..., None] * rgb("#FFFFFF")
        # pulsos que viajan por el camino activo
        for k in range(len(camino) - 1):
            (ax, ay), (bx, by) = camino[k], camino[k + 1]
            t = 0.35 + 0.3 * ((k * 0.37 + var * 0.2) % 1)
            px, py = ax + (bx - ax) * t, ay + (by - ay) * t
            img += (np.exp(-((XX - px) ** 2 + (YY - py) ** 2) / (2 * (0.008 * H) ** 2)) * 1.2)[..., None] * rgb(turq)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        # matriz de atención (transformer): fichas en diagonal con intensidad ~ softmax
        n = 12
        lado = 0.062 * H
        x0, y0 = W - 0.08 * W - n * lado, 0.5 * H - n * lado / 2
        rng = np.random.default_rng(sem)
        logits = rng.normal(size=(n, n)) + 3.2 * np.eye(n) + 1.6 * np.eye(n, k=-1)
        att = np.exp(logits) / np.exp(logits).sum(1, keepdims=True)
        att = att / att.max()

        def celdas(d, s):
            for i in range(n):
                for j in range(n):
                    v = float(att[i, j]) ** 0.6
                    x, y = x0 + j * lado, y0 + i * lado
                    d.rectangle([(x + 3 * E) * s, (y + 3 * E) * s, (x + lado - 3 * E) * s, (y + lado - 3 * E) * s], fill=int(255 * v))
        c = cap(celdas)
        pintar(img, c, violeta, 0.55, 0.25)
        pintar(img, c ** 3, turq, 0.55)
        marco = cap(lambda d, s: d.rectangle([(x0 - 6 * E) * s, (y0 - 6 * E) * s, (x0 + n * lado + 6 * E) * s, (y0 + n * lado + 6 * E) * s],
                                             outline=200, width=max(1, int(1.5 * E * s))))
        pintar(img, marco, violeta, 0.5)
        etq = cap(lambda d, s: (_txt(d, s, x0, y0 - 0.06 * H, "softmax(QKᵀ / √d) · V", 30, 0.85, "DejaVuSerif-Italic"),
                                _txt(d, s, x0, y0 + n * lado + 0.02 * H, "12 tokens · 1 cabeza", 22, 0.7)))
        pintar(img, etq, "#E9E3FF", 0.7)
        return fin(img, BASE, tipo, zona, 0.5)
    nodos, aristas = _red(W - 0.08 * H, H - 0.20 * H, 0.42 * H, 0.42 * H, (3, 5, 4), sem)
    m = _masc_esq(W, H, 0.55)
    c = cap(lambda d, s: ([_l(d, s, [a, b], 0.6, 1.0) for a, b, _ in aristas], [_c(d, s, x, y, 0.012 * H, 1, 1.4) for cn in nodos for x, y in cn]))
    pintar(img, c * m, violeta, 0.35)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ CAOS
def _lorenz(n=60000, dt=0.004, sigma=10.0, rho=28.0, beta=8 / 3):
    p = np.empty((n, 3))
    x, y, z = 0.1, 0.0, 20.0
    for i in range(n):  # RK2: suficiente para un dibujo y estable con este paso
        dx, dy, dz = sigma * (y - x), x * (rho - z) - y, x * y - beta * z
        mx, my, mz = x + dx * dt / 2, y + dy * dt / 2, z + dz * dt / 2
        x += sigma * (my - mx) * dt
        y += (mx * (rho - mz) - my) * dt
        z += (mx * my - beta * mz) * dt
        p[i] = (x, y, z)
    return p[1000:]


def caos(tipo, var=0, zona=None):
    """Caos: atractor de Lorenz con color por tiempo y diagrama de bifurcación del mapa logístico."""
    BASE = "#07060A"
    ambar, rosa, violeta = "#FBBF24", "#FB7185", "#A78BFA"
    img = base_color(BASE)
    img += F.nebulosa(["#07060A", "#1A0E1C", "#3A1630"], 900, 501 + var, 0.08, (0.85, 0.4), 0.9)
    if tipo in ("portada", "cierre", "contenido", "video"):
        p = _lorenz()
        ang = math.radians(25 + 15 * var)
        u = p[:, 0] * math.cos(ang) + p[:, 1] * math.sin(ang)
        v = p[:, 2]
        if tipo in ("portada", "cierre"):
            cx, cy, esc = 1.32 * H, 0.52 * H, 0.0145 * H
        else:
            cx, cy, esc = W - 0.12 * H, H - 0.16 * H, 0.0075 * H
        X = cx + u * esc
        Y = cy - (v - 25) * esc
        colores = (ambar, rosa, violeta)
        trozos = np.array_split(np.arange(len(X)), 3)
        for ci, idx in enumerate(trozos):
            pts = list(zip(X[idx], Y[idx]))
            capa = cap(lambda d, s, pts=pts: _l(d, s, pts, 0.55, 0.9))
            fz = 0.75 if tipo in ("portada", "cierre") else 0.30
            pintar(img, capa * (0.2 + 0.8 * F.suave(0.35 * W, 0.75 * W, XX)), colores[ci], fz, 0.2 * fz)
        if tipo in ("portada", "cierre"):
            ecu = cap(lambda d, s: (_txt(d, s, 1.00 * H, 0.08 * H, "ẋ = σ(y − x)    ẏ = x(ρ − z) − y    ż = xy − βz", 34, 0.8, "DejaVuSerif-Italic"),
                                    _txt(d, s, 1.00 * H, 0.13 * H, "σ = 10   ρ = 28   β = 8/3", 26, 0.6, "DejaVuSerif-Italic")))
            pintar(img, ecu, "#F3E8EE", 0.7)
        return fin(img, BASE, tipo, zona, 0.5 if tipo in ("portada", "cierre") else 0.45)
    # sección: diagrama de bifurcación del mapa logístico x → r·x·(1 − x)
    r = np.linspace(2.8, 4.0, 2400)
    x = np.full_like(r, 0.5)
    for _ in range(400):
        x = r * x * (1 - x)
    dens = np.zeros((H, W), np.float32)
    x0, x1, y0, y1 = 0.42 * W, 0.97 * W, 0.12 * H, 0.90 * H
    for _ in range(300):
        x = r * x * (1 - x)
        px = (x0 + (r - 2.8) / 1.2 * (x1 - x0)).astype(int)
        py = (y1 - x * (y1 - y0)).astype(int)
        np.add.at(dens, (np.clip(py, 0, H - 1), np.clip(px, 0, W - 1)), 1.0)
    dens = gaussian_filter(dens, 0.8 * E + 0.3)
    dens = np.clip(dens / np.percentile(dens[dens > 0], 97), 0, 1) ** 0.6
    col = _rampa(F.suave(x0, x1, XX), [ambar, rosa, violeta])
    img += dens[..., None] * col * 0.85 * (0.2 + 0.8 * F.suave(0.38 * W, 0.6 * W, XX))[..., None]
    ejes = cap(lambda d, s: (_l(d, s, [(x0, y1 + 0.02 * H), (x1, y1 + 0.02 * H)], 0.8, 1.4),
                             [_l(d, s, [(x0 + (rr - 2.8) / 1.2 * (x1 - x0), y1 + 0.02 * H), (x0 + (rr - 2.8) / 1.2 * (x1 - x0), y1 + 0.035 * H)], 0.8, 1.4)
                              for rr in (3.0, 3.4495, 3.5441, 3.8284, 4.0)],
                             _txt(d, s, x0, y1 + 0.045 * H, "r = 3.0        3.449   3.544                3.828     4.0", 22, 0.7),
                             _txt(d, s, x0, y0 - 0.07 * H, "x  →  r · x · (1 − x)", 32, 0.8, "DejaVuSerif-Italic")))
    pintar(img, ejes, "#E7DDE8", 0.6)
    return fin(img, BASE, tipo, zona, 0.5)


# ================================================================ AERODINÁMICA
def _joukowski(cx, cy, cuerda, alfa_deg=6.0, camber=0.08, espesor=0.09, U=1.0):
    """Función de corriente ψ (HxW) del flujo potencial alrededor de un perfil de Joukowski con condición de Kutta,
    rapidez |V| y máscara del perfil. La cuerda del perfil ≈ 4c (px)."""
    c = cuerda / 4.0
    mu = complex(-espesor * c, camber * c)
    R = abs(c - mu)
    alfa = math.radians(alfa_deg)
    beta = math.atan2(-(c - mu).imag, (c - mu).real) * -1  # ángulo del borde de salida respecto al centro
    gamma = 4 * math.pi * U * R * math.sin(alfa + beta)
    z = ((XX - cx) + 1j * (cy - YY)) * np.exp(1j * alfa)  # y hacia arriba; marco del perfil: la corriente libre queda horizontal
    s = np.sqrt(z * z - 4 * c * c)
    z1, z2 = (z + s) / 2, (z - s) / 2
    zeta = np.where(np.abs(z1 - mu) >= np.abs(z2 - mu), z1, z2)
    zp = zeta - mu
    dentro = np.abs(zp) < R * 1.0005
    zp = np.where(dentro, R * 1.0005 * np.exp(1j * np.angle(zp + 1e-12)), zp)
    Wc = U * (zp * np.exp(-1j * alfa) + R * R * np.exp(1j * alfa) / zp) + 1j * gamma / (2 * math.pi) * np.log(zp)
    dW = U * (np.exp(-1j * alfa) - R * R * np.exp(1j * alfa) / zp ** 2) + 1j * gamma / (2 * math.pi * zp)
    dz = 1 - c * c / (zp + mu) ** 2
    vel = np.abs(dW / np.where(np.abs(dz) < 1e-6, 1e-6, dz))
    return Wc.imag.astype(np.float32), np.clip(vel, 0, 3).astype(np.float32), dentro


def aerodinamica(tipo, var=0, zona=None):
    """Aerodinámica: líneas de corriente sobre un perfil de Joukowski (rapidez en color) y cono de Mach con su ángulo."""
    BASE = "#06101A"
    hielo, azul, ambar = "#BAE6FD", "#38BDF8", "#FBBF24"
    img = base_color(BASE)
    img += F.nebulosa(["#06101A", "#0A2033", "#123B5C"], 900, 601 + var, 0.10, (0.8, 0.4), 0.9)
    if tipo in ("portada", "cierre"):
        cx, cy = 1.28 * H, 0.52 * H
        psi, vel, dentro = _joukowski(cx, cy, 0.95 * H, alfa_deg=7 + 2 * var)
        lineas, _ = iso(psi / H, 26, 1.2)
        alc = 0.10 + 0.90 * F.suave(0.36 * W, 0.78 * W, XX)
        rap = _rampa(np.clip((vel - 0.6) / 1.2, 0, 1), ["#1E3A5F", azul, hielo, "#FFFFFF"])
        img += lineas[..., None] * rap * 0.85 * alc[..., None] * (1 - dentro[..., None])
        perfil = gaussian_filter(dentro.astype(np.float32), 1.2)
        borde = np.clip(perfil * (1 - perfil) * 4, 0, 1)
        img[:] = img * (1 - perfil[..., None]) + perfil[..., None] * rgb("#0B1826")
        img += borde[..., None] * rgb(hielo) * 0.9 + gaussian_filter(borde, 6 * E)[..., None] * rgb(azul) * 0.5
        etq = cap(lambda d, s: (_txt(d, s, 1.00 * H, 0.10 * H, "Γ = 4π U R sin(α + β)   ·   Kutta", 30, 0.8, "DejaVuSerif-Italic"),
                                _txt(d, s, 1.00 * H, 0.15 * H, f"α = {7 + 2 * var}°   ·   perfil de Joukowski", 26, 0.6, "DejaVuSerif-Italic")))
        pintar(img, etq, hielo, 0.65)
        return fin(img, BASE, tipo, zona, 0.5)
    if tipo == "seccion":
        M = 2.0 + 0.2 * (var % 3)
        mu = math.asin(1 / M)
        nx, ny = 0.50 * W, 0.52 * H  # punta del cuerpo
        L = 0.62 * W

        def arte(d, s):
            semi = math.radians(10)
            cuerpo = [(nx, ny), (nx + L * 0.55, ny - L * 0.55 * math.tan(semi)), (nx + L * 0.55, ny + L * 0.55 * math.tan(semi))]
            _l(d, s, cuerpo + [cuerpo[0]], 1.0, 2.6)
            ch = mu + math.radians(9)  # el choque oblicuo va algo más abierto que la onda de Mach
            for sg in (-1, 1):
                _l(d, s, [(nx, ny), (nx + L, ny + sg * L * math.tan(ch))], 1.0, 3.0)
                _punteada(d, s, [(nx, ny), (nx + L, ny + sg * L * math.tan(mu))], 0.7, 1.6, 10, 9)
            for k in range(9):  # corrientes que se desvían al cruzar el choque
                y = ny + (k - 4) * 0.075 * H
                if abs(k - 4) < 1:
                    continue
                xc = nx + abs(y - ny) / math.tan(ch)
                desv = math.copysign(math.tan(math.radians(10)), y - ny)
                _l(d, s, [(0.40 * W, y), (xc, y), (W, y + desv * (W - xc))], 0.45, 1.2)
            r = 0.16 * H
            d.arc([(nx - r) * s, (ny - r) * s, (nx + r) * s, (ny + r) * s], -math.degrees(mu), 0, fill=230, width=max(1, int(1.6 * E * s)))
            _txt(d, s, nx + r + 0.01 * H, ny - 0.07 * H, f"μ = arcsin(1/M) = {math.degrees(mu):.1f}°", 26, 0.9, "DejaVuSerif-Italic")
            _txt(d, s, 0.42 * W, ny - 0.36 * H, f"M∞ = {M:.1f}", 34, 0.9, "DejaVuSerif-Italic")
        pintar(img, cap(arte) * (0.25 + 0.75 * F.suave(0.38 * W, 0.62 * W, XX)), hielo, 0.75, 0.25)
        return fin(img, BASE, tipo, zona, 0.5)
    psi, vel, dentro = _joukowski(W + 0.05 * H, H + 0.02 * H, 0.70 * H, alfa_deg=4)
    lineas, _ = iso(psi / H, 26, 1.0)
    pintar(img, lineas * _masc_esq(W, H, 0.60) * (1 - dentro), azul, 0.40)
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ SOLAR
def solar(tipo, var=0, zona=None):
    """Heliofísica: limbo del Sol con granulación y oscurecimiento al borde, corona en rayos y protuberancias en arco."""
    BASE = "#0C0503"
    img = base_color(BASE)
    sem = 701 + var * 3
    img += F.estrellas(900, sem, 0.45)
    if tipo in ("portada", "cierre"):
        cx, cy, R = 1.64 * H, 1.64 * H, 1.0 * H  # el limbo queda abajo a la derecha, fuera de la columna de texto
    elif tipo == "seccion":
        cx, cy, R = 1.42 * H, 0.52 * H, 0.26 * H
    else:
        cx, cy, R = W + 0.25 * H, H + 0.25 * H, 0.42 * H
    dx, dy = XX - cx, YY - cy
    r = np.sqrt(dx * dx + dy * dy)
    ang = np.arctan2(dy, dx)
    dentro = F.suave(R + 1.5, R - 1.5, r)
    mu_ = np.sqrt(np.clip(1 - (r / R) ** 2, 0, 1))
    oscur = 0.35 + 0.65 * mu_ ** 0.6  # oscurecimiento al limbo
    gran = F.ruido(0.010 * H + 2, 4, sem) * 0.5 + F.ruido(0.05 * H, 3, sem + 1) * 0.5
    sol = _rampa(np.clip(gran * oscur, 0, 1), ["#7A1E04", "#D9480F", "#F97316", "#FDBA74", "#FFF1D0"])
    fuerte = 1.0 if tipo in ("portada", "cierre", "seccion") else 0.6
    img[:] = img * (1 - dentro[..., None]) + sol * dentro[..., None] * fuerte
    fuera = np.clip(r - R, 0, None)
    rayos = 0.6 + 0.4 * gaussian_filter1d(np.random.default_rng(sem).random(720), 3)
    k = ((ang + np.pi) / (2 * np.pi) * 720).astype(int) % 720
    corona = (np.exp(-fuera / (0.06 * R)) * 0.75 + np.exp(-fuera / (0.30 * R)) * 0.25 * rayos[k]) * (1 - dentro)
    img += corona[..., None] * rgb("#FFB070") * fuerte
    if tipo in ("portada", "cierre", "seccion"):
        rng = np.random.default_rng(sem + 2)
        angs = (np.array([-78, -64, -92, -52]) if tipo != "seccion" else np.array([-60, -20, 200, 150])) + rng.uniform(-4, 4, 4)

        def arcos(d, s):
            for a0 in angs:
                a = math.radians(a0)
                ab = a + math.radians(rng.uniform(5, 11))
                p0 = (cx + R * math.cos(a), cy + R * math.sin(a))
                p2 = (cx + R * math.cos(ab), cy + R * math.sin(ab))
                am = (a + ab) / 2
                h = R * rng.uniform(0.10, 0.22) if tipo != "seccion" else R * rng.uniform(0.25, 0.45)
                p1 = (cx + (R + h * 2) * math.cos(am), cy + (R + h * 2) * math.sin(am))
                for k in range(5):
                    off = (k - 2) * 0.003 * R
                    q1 = (p1[0] + off, p1[1] + off)
                    _l(d, s, [tuple(q) for q in _bezier(p0, q1, p2, 60)], 0.8, 2.2)
        prot = cap(arcos)
        prot = gaussian_filter(prot, 1.5 * E) * (1 - dentro)
        img += prot[..., None] * rgb("#FF6A3D") * 1.1 + gaussian_filter(prot, 8 * E)[..., None] * rgb("#FF3D1F") * 0.6
    return fin(img, BASE, tipo, zona, 0.45)


# ================================================================ CUADERNO (claro)
def _boceto(pts, rng, amp=1.6):
    """Trazo «a mano»: pequeño temblor suave sobre la polilínea."""
    pts = np.asarray(pts, np.float64)
    n = len(pts)
    ruido = gaussian_filter1d(rng.normal(size=(n, 2)), max(2, n / 10), axis=0) * amp * E * 6
    return [tuple(p) for p in pts + ruido]


def cuaderno(tipo, var=0, zona=None):
    """Cuaderno de ingeniería (claro): papel milimétrico crema, margen rojo y bocetos a tinta azul con notas a mano."""
    BASE = "#FBF8F1"
    tinta, roja, lapiz = "#1E3A8A", "#C2410C", "#475569"
    img = base_color(BASE)
    img += (F.ruido(0.3 * H, 4, 801) - 0.5)[..., None] * 0.018  # fibra del papel
    malla_fina = cap(F.rejilla(0.1, 0.5, 0.35, 0.0, False))
    malla_gruesa = cap(F.rejilla(0.5, 0.5, 0.0, 0.9, False))

    def tinta_sobre(capa, color, a):
        img[:] = img * (1 - capa[..., None] * a) + rgb(color) * capa[..., None] * a

    tinta_sobre(malla_fina, "#7DA7D9", 0.18)
    tinta_sobre(malla_gruesa, "#7DA7D9", 0.30)
    tinta_sobre(cap(lambda d, s: _l(d, s, [(0.055 * W, 0), (0.055 * W, H)], 1.0, 1.6)), "#E06C6C", 0.55)
    rng = np.random.default_rng(811 + var)
    nota = "Caveat-700"
    if tipo in ("portada", "cierre"):
        cx, cy = 1.40 * H, 0.55 * H
        a_, b_ = 0.34 * H, 0.23 * H  # b/a = 0.676 → e ≈ 0.74 (Molniya), a la derecha de la columna de texto
        e = math.sqrt(1 - (b_ / a_) ** 2)
        fx = cx + a_ * e  # foco (Tierra) a la derecha del centro
        t = np.linspace(0, 2 * np.pi, 300)
        elipse = list(zip(cx + a_ * np.cos(t), cy + b_ * np.sin(t)))
        tp = 2.2
        sat = (cx + a_ * math.cos(tp), cy + b_ * math.sin(tp))

        def dibujo(d, s):
            _l(d, s, _boceto(elipse, rng), 1.0, 2.4)
            _c(d, s, fx, cy, 0.055 * H, 1.0, 2.4)
            _l(d, s, _boceto([(cx - a_, cy), (cx + a_, cy)], rng), 0.7, 1.4)
            _l(d, s, _boceto([(fx, cy), sat], rng), 0.9, 1.8)
            _c(d, s, sat[0], sat[1], 0.012 * H, 1.0, 2.0, lleno=True)
            vx, vy = -a_ * math.sin(tp), b_ * math.cos(tp)
            nv = math.hypot(vx, vy)
            tip = (sat[0] + vx / nv * 0.14 * H, sat[1] + vy / nv * 0.14 * H)
            _l(d, s, _boceto([sat, tip], rng), 1.0, 2.2)
            ang = math.atan2(tip[1] - sat[1], tip[0] - sat[0])
            for sgn in (-1, 1):
                _l(d, s, [tip, (tip[0] - 0.025 * H * math.cos(ang + sgn * 0.45), tip[1] - 0.025 * H * math.sin(ang + sgn * 0.45))], 1.0, 2.2)
            _txt(d, s, cx - 0.12 * H, cy - b_ - 0.075 * H, "Molniya:  a ≈ 26 600 km   e ≈ 0.74", 30, 1.0, "DejaVuSerif-Italic")
            _txt(d, s, tip[0] - 0.05 * H, tip[1] - 0.07 * H, "v", 46, 1.0, nota)
            _txt(d, s, fx - 0.03 * H, cy + 0.07 * H, "Tierra", 38, 1.0, nota)
            _txt(d, s, cx + a_ - 0.05 * H, cy + 0.02 * H, "periapsis", 34, 0.9, nota)
        tinta_sobre(cap(dibujo), tinta, 0.85)
        tinta_sobre(cap(lambda d, s: (_txt(d, s, 1.02 * H, 0.08 * H, "v² = μ (2/r − 1/a)", 46, 1.0, "DejaVuSerif-Italic"),
                                      _txt(d, s, 1.02 * H, 0.145 * H, "vis-viva", 40, 1.0, nota))), roja, 0.85)
        return fin(img, BASE, tipo, zona, 0.12)
    if tipo == "seccion":
        cx, cy = 1.36 * H, 0.52 * H
        r1, r2 = 0.16 * H, 0.36 * H
        t = np.linspace(0, 2 * np.pi, 240)
        a_ = (r1 + r2) / 2
        ce = cx - (r2 - r1) / 2

        def dibujo(d, s):
            _l(d, s, _boceto(list(zip(cx + r1 * np.cos(t), cy + r1 * np.sin(t))), rng), 1.0, 2.2)
            _l(d, s, _boceto(list(zip(cx + r2 * np.cos(t), cy + r2 * np.sin(t))), rng), 1.0, 2.2)
            th = np.linspace(0, np.pi, 160)
            bb = math.sqrt(r1 * r2)
            _punteada(d, s, list(zip(ce - a_ * np.cos(th) * -1, cy - bb * np.sin(th))), 1.0, 2.2, 14, 9)
            _c(d, s, cx, cy, 0.04 * H, 1.0, 2.2)
            _txt(d, s, cx + r1 + 0.012 * H, cy - 0.03 * H, "Δv₁", 36, 1.0, "DejaVuSerif-Italic")
            _txt(d, s, cx - r2 - 0.10 * H, cy - 0.03 * H, "Δv₂", 36, 1.0, "DejaVuSerif-Italic")
            _txt(d, s, cx - 0.18 * H, cy + r2 + 0.02 * H, "transferencia de Hohmann", 38, 1.0, nota)
        tinta_sobre(cap(dibujo), tinta, 0.85)
        return fin(img, BASE, tipo, zona, 0.12)
    # contenido / video: boceto chico en la esquina
    cx, cy = W - 0.16 * H, H - 0.14 * H
    t = np.linspace(0, 2 * np.pi, 160)

    def dibujo(d, s):
        _l(d, s, _boceto(list(zip(cx + 0.11 * H * np.cos(t), cy + 0.06 * H * np.sin(t))), rng), 1.0, 1.8)
        _c(d, s, cx + 0.05 * H, cy, 0.018 * H, 1.0, 1.8)
    tinta_sobre(cap(dibujo), tinta, 0.35)
    return fin(img, BASE, tipo, zona, 0.10)


# ---------------------------------------------------------------- registro
GENERADORES_TEMATICOS_2 = {"espectro": espectro, "neuronal": neuronal, "caos": caos, "aerodinamica": aerodinamica,
                           "solar": solar, "cuaderno": cuaderno}
for _n, _f in GENERADORES_TEMATICOS_2.items():
    F.registrar_generador(_n, _f)


if __name__ == "__main__":
    import sys
    print(hoja_contacto(sys.argv[1:] or list(GENERADORES_TEMATICOS_2)))
