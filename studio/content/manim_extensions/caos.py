"""Caos: mapa logistico, bifurcacion, Lorenz, Lyapunov y pendulo doble.

Pensado para el curso "Caos: el orden escondido". Todo el calculo es numpy
puro y determinista (integracion RK4 con paso fijo; el unico azar es
`ruido_uniforme`, con semilla): mismo script -> mismo render, condicion
necesaria para trabajar con `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: el SISTEMA
es ambar, su GEMELO casi identico (y lo que se mide: delta, lambda) cian,
el ERROR que crece entre ambos rojo, el ORDEN (equilibrios, ciclos,
ventanas) verde y el ESPACIO DE FASES (el atractor como objeto, el ruido)
violeta. Mobiliario en el gris azulado `COLOR_EJE`.

Piezas:
    orbita_logistica    nucleo: x_{k+1} = r x_k (1 - x_k)
    cobweb              parabola + diagonal + telarana, por segmentos
    imagen_bifurcacion  EL diagrama, como imagen por densidad (log)
    feigenbaum_cocientes  los cocientes que convergen a delta = 4.669
    trayectoria_lorenz  nucleo RK4 del sistema de Lorenz (sigma/rho/beta)
    curva_lorenz        la proyeccion 2D del atractor, lista para Create
    par_lorenz          dos trayectorias a eps y su separacion por paso
    curva_separacion    log10(d) contra t; mide su propio Lyapunov
    pendulo_doble       nucleo RK4 del pendulo doble (energia validable)
    PenduloDoble        brazos + bolas + traza, reproducible por alpha
    abanico_pendulos    N pendulos casi identicos que revientan juntos
    mapa_retorno        (x_k, x_{k+1}): el caos se delata, el ruido no
    ruido_uniforme      azar de verdad, determinista por semilla

Las piezas exponen localizadores sobre la geometria ACTUAL (`.en`,
`.punto`, `.punto_de`, anclas invisibles inmunes a move_to) y los NUMEROS
que dibujan (`.lyapunov()`, `.punto_fijo()`, `.divergencia(alpha)`,
`feigenbaum_cocientes()`): en un curso sobre medir la impredecibilidad,
el rotulo sale de la misma fuente que el dibujo, nunca a mano.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`PASOS_MAX`, `RES_BIF_MAX`, `PENDULOS_MAX`, `MUESTRAS_MAX` y
`PUNTOS_NUBE_MAX` levantan ValueError; pasarse cambia lo que se ve y es
mejor enterarse.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from caos import cobweb, imagen_bifurcacion, par_lorenz

    tela = cobweb(2.9)
    self.play(Create(tela.parabola))
    self.play(Transform(tela, tela.con_r(3.9)))
"""

import math

import numpy as np

from manim import (Dot, ImageMobject, Line, Text, VGroup, VMobject,
                   DOWN, LEFT, ORIGIN, RIGHT, UP)

from code_brand import FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
PASOS_MAX = 60_000          # pasos de una integracion RK4
RES_BIF_MAX = 1600          # lado mayor (px) del diagrama de bifurcacion
PENDULOS_MAX = 40
MUESTRAS_MAX = 600          # muestras de una curva parametrica
PUNTOS_NUBE_MAX = 400       # puntos de un mapa de retorno

# Paleta propia de la libreria (coincide con la del curso).
COLOR_SISTEMA = "#f59e0b"    # el sistema: trayectoria, parabola, pendulo
COLOR_GEMELO = "#22d3ee"     # el gemelo casi identico; lo medido (delta,
                             # lambda)
COLOR_ERROR = "#f43f5e"      # el error que crece, la divergencia
COLOR_ORDEN = "#34d399"      # el orden: equilibrios, ciclos, ventanas
COLOR_FASE = "#a78bfa"       # el espacio de fases, el atractor, el ruido
COLOR_EJE = "#31414f"        # mobiliario: ejes, cajas, diagonales

C_SISTEMA, C_GEMELO, C_ERROR = COLOR_SISTEMA, COLOR_GEMELO, COLOR_ERROR
C_ORDEN, C_FASE, C_EJE = COLOR_ORDEN, COLOR_FASE, COLOR_EJE

# --- Los numeros del curso -------------------------------------------
# Puntos de duplicacion del mapa logistico (Feigenbaum 1978): 1->2, 2->4,
# 4->8, 8->16, 16->32. Sus cocientes convergen a delta.
R_BIFURCACIONES = (3.0, 3.449490, 3.544090, 3.564407, 3.568759)
FEIGENBAUM_DELTA = 4.669201609
LORENZ_SIGMA, LORENZ_RHO, LORENZ_BETA = 10.0, 28.0, 8.0 / 3.0
VENTANA_P3 = (3.8284, 3.8415)     # la isla de periodo 3 dentro del caos

_EPS = 1e-12


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _hex_a_rgb(hexcolor):
    h = str(hexcolor).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)],
                    dtype=np.float64)


def _mezcla_hex(color_a, color_b, t):
    a, b = _hex_a_rgb(color_a), _hex_a_rgb(color_b)
    rgb = np.clip(a + (b - a) * float(t), 0, 255)
    return "#%02x%02x%02x" % tuple(int(round(v)) for v in rgb)


def _poligonal(puntos, color, grosor=2.0):
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


def _ancla(punto=ORIGIN):
    """Dot invisible que viaja con la pieza: localizador inmune a move_to."""
    p = np.asarray(punto, dtype=np.float64)
    if p.shape == (2,):
        p = np.append(p, 0.0)
    return Dot(p, radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)


def _validar(nombre, valor, tope):
    valor = int(valor)
    if valor < 1 or valor > tope:
        raise ValueError(f"{nombre}: {valor} fuera de rango (1..{tope})")
    return valor


def _imagen(rgba, alto_escena):
    img = ImageMobject(rgba)
    img.set_resampling_algorithm(3)   # BICUBIC
    if alto_escena is not None:
        img.height = alto_escena
    return img


# =====================================================================
# El mapa logistico y su telarana
# =====================================================================
def orbita_logistica(r, x0=0.2, n=60):
    """Orbita x_{k+1} = r x_k (1 - x_k), incluida la semilla."""
    n = _validar("orbita_logistica.n", n, PASOS_MAX)
    x = np.empty(n)
    x[0] = float(x0)
    r = float(r)
    for k in range(n - 1):
        x[k + 1] = r * x[k] * (1.0 - x[k])
    return x


class Cobweb(VGroup):
    """Parabola r x(1-x), diagonal y=x y la telarana de la orbita."""

    def __init__(self, ancla, caja, parabola, diagonal, telarana, params,
                 **kwargs):
        super().__init__(ancla, caja, parabola, diagonal, telarana,
                         **kwargs)
        self._ancla = ancla            # esquina inferior izquierda
        self.caja = caja
        self.parabola = parabola
        self.diagonal = diagonal
        self.telarana = telarana
        self._params = params
        self.r = params["r"]

    def en(self, x, y):
        """Punto de escena para (x, y) en [0,1]^2, geometria ACTUAL."""
        lado = self._params["lado"] * self._escala_actual()
        return self._ancla.get_center() + RIGHT * x * lado + UP * y * lado

    def _escala_actual(self):
        return self.caja.width / max(self._params["lado"], _EPS)

    def punto_fijo(self):
        """El equilibrio no trivial 1 - 1/r (el numero del clip 2)."""
        return 1.0 - 1.0 / self.r

    def con_r(self, r):
        """La misma caja con otra r, anclada por la esquina (Transform)."""
        params = dict(self._params, r=float(r))
        otro = cobweb(**params)
        otro.shift(self._ancla.get_center() - otro._ancla.get_center())
        return otro


def cobweb(r, x0=0.2, pasos=14, lado=4.2, color=COLOR_SISTEMA,
           color_tela=None, color_ejes=COLOR_EJE, muestras=160):
    """Telarana del mapa logistico en una caja [0,1]^2 de `lado` en escena.

    `.telarana` es un VGroup con un segmento por rebote (vertical a la
    parabola, horizontal a la diagonal): LaggedStart(*telarana) la dibuja
    rebote a rebote. La esquina inferior izquierda queda en ORIGIN - lado/2.
    """
    pasos = _validar("cobweb.pasos", pasos, 200)
    muestras = _validar("cobweb.muestras", muestras, MUESTRAS_MAX)
    r, lado = float(r), float(lado)
    esquina = np.array([-lado / 2.0, -lado / 2.0, 0.0])

    def punto(x, y):
        return esquina + RIGHT * x * lado + UP * y * lado

    caja = VGroup(
        Line(punto(0, 0), punto(1, 0), stroke_width=2.0, color=color_ejes),
        Line(punto(0, 0), punto(0, 1), stroke_width=2.0, color=color_ejes))

    xs = np.linspace(0.0, 1.0, muestras)
    parab = _poligonal([punto(x, r * x * (1 - x)) for x in xs], color, 3.0)
    diag = Line(punto(0, 0), punto(1, 1), stroke_width=1.6, color=color_ejes)
    diag.set_stroke(opacity=0.8)

    tela_color = color_tela if color_tela else color
    orbita = orbita_logistica(r, x0, pasos + 1)
    telarana = VGroup()
    y_prev = 0.0
    for k in range(pasos):
        x_k, x_sig = orbita[k], orbita[k + 1]
        seg = VGroup(
            Line(punto(x_k, y_prev), punto(x_k, x_sig), stroke_width=1.8,
                 color=tela_color),
            Line(punto(x_k, x_sig), punto(x_sig, x_sig), stroke_width=1.8,
                 color=tela_color))
        seg.set_stroke(opacity=0.85)
        telarana.add(seg)
        y_prev = x_sig

    params = {"r": r, "x0": float(x0), "pasos": pasos, "lado": lado,
              "color": color, "color_tela": color_tela,
              "color_ejes": color_ejes, "muestras": muestras}
    return Cobweb(_ancla(esquina), caja, parab, diag, telarana, params)


# =====================================================================
# El diagrama de bifurcacion (imagen por densidad)
# =====================================================================
def imagen_bifurcacion(r=(2.8, 4.0), res=(1400, 800), burn=400,
                       muestra=260, color=COLOR_SISTEMA, alto_escena=5.2,
                       gamma=0.65):
    """EL diagrama: histograma 2D de las orbitas por columna de r.

    Devuelve un ImageMobject con `.punto_de(r, x)` (escena, geometria
    ACTUAL: cierra sobre el propio mobject) y `.rango = (r_min, r_max)`.
    Con r=(3.82, 3.87) es el zoom a la ventana de periodo 3.
    """
    res_x, res_y = int(res[0]), int(res[1])
    if max(res_x, res_y) > RES_BIF_MAX:
        raise ValueError(f"imagen_bifurcacion: res {res} > {RES_BIF_MAX}")
    burn = _validar("imagen_bifurcacion.burn", burn, 2000)
    muestra = _validar("imagen_bifurcacion.muestra", muestra, 2000)
    r0, r1 = float(r[0]), float(r[1])

    rs = np.linspace(r0, r1, res_x)
    x = np.full(res_x, 0.5)
    for _ in range(burn):
        x = rs * x * (1.0 - x)
    hist = np.zeros((res_y, res_x), dtype=np.float64)
    cols = np.arange(res_x)
    for _ in range(muestra):
        x = rs * x * (1.0 - x)
        filas = np.clip((x * res_y).astype(np.int64), 0, res_y - 1)
        np.add.at(hist, (filas, cols), 1.0)

    dens = np.log1p(hist[::-1])           # fila 0 = x alto (imagen)
    if dens.max() > 0:
        dens = (dens / dens.max()) ** float(gamma)
    tinta = _hex_a_rgb(color)
    rgba = np.zeros((res_y, res_x, 4), dtype=np.uint8)
    rgba[..., :3] = np.clip(tinta * dens[..., None], 0, 255).astype(np.uint8)
    rgba[..., 3] = np.clip(dens * 255 * 1.5, 0, 255).astype(np.uint8)

    img = _imagen(rgba, alto_escena)
    img.rango = (r0, r1)

    def punto_de(r_val, x_val, _img=img, _r0=r0, _r1=r1):
        """Escena para (r, x): lee centro y tamaño ACTUALES de la imagen."""
        fx = (float(r_val) - _r0) / max(_r1 - _r0, _EPS) - 0.5
        fy = float(x_val) - 0.5
        return (_img.get_center() + RIGHT * fx * _img.width
                + UP * fy * _img.height)

    img.punto_de = punto_de
    return img


def feigenbaum_cocientes():
    """(4.751, 4.656, 4.668): los cocientes (r_n - r_{n-1})/(r_{n+1} - r_n)
    de R_BIFURCACIONES — la escalera que converge a delta = 4.669."""
    r = R_BIFURCACIONES
    return tuple((r[i] - r[i - 1]) / (r[i + 1] - r[i])
                 for i in range(1, len(r) - 1))


# =====================================================================
# Lorenz
# =====================================================================
def _lorenz_derivada(estado):
    x, y, z = estado
    return np.array([LORENZ_SIGMA * (y - x),
                     x * (LORENZ_RHO - z) - y,
                     x * y - LORENZ_BETA * z])


def trayectoria_lorenz(x0=(1.0, 1.0, 20.0), n=9000, dt=0.005):
    """(n, 3) puntos del sistema de Lorenz por RK4 de paso fijo."""
    n = _validar("trayectoria_lorenz.n", n, PASOS_MAX)
    dt = float(dt)
    pts = np.empty((n, 3))
    s = np.array(x0, dtype=np.float64)
    for k in range(n):
        pts[k] = s
        k1 = _lorenz_derivada(s)
        k2 = _lorenz_derivada(s + 0.5 * dt * k1)
        k3 = _lorenz_derivada(s + 0.5 * dt * k2)
        k4 = _lorenz_derivada(s + dt * k3)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return pts


def par_lorenz(eps=1e-6, x0=(1.0, 1.0, 20.0), n=9000, dt=0.005):
    """(pts_a, pts_b, d): el gemelo arranca a `eps` en x, y `d` es la
    distancia euclidea por paso — TODO de la misma integracion."""
    a = trayectoria_lorenz(x0, n, dt)
    b = trayectoria_lorenz((x0[0] + float(eps), x0[1], x0[2]), n, dt)
    d = np.linalg.norm(a - b, axis=1)
    return a, b, d


class CurvaLorenz(VMobject):
    """Proyeccion 2D del atractor; `.punto(frac)` sobre geometria actual."""

    def punto(self, frac):
        return self.point_from_proportion(float(np.clip(frac, 0.0, 1.0)))


def curva_lorenz(pts, plano="xz", alto=5.0, color=COLOR_SISTEMA,
                 grosor=2.0, maximo=4000, como=None):
    """La trayectoria proyectada, centrada en ORIGIN con altura `alto`.

    `maximo` submuestrea la trayectoria para que el VMobject no pese; el
    trazo sigue siendo la MISMA orbita (se toman puntos equiespaciados).
    Con `como=<otra CurvaLorenz>` reutiliza SU centro y escala: dos
    trayectorias gemelas comparten encuadre y la separacion que se ve es
    la fisica, no un artefacto del centrado individual.
    """
    pts = np.asarray(pts, dtype=np.float64)
    ejes = {"xz": (0, 2), "xy": (0, 1), "yz": (1, 2)}[plano]
    p2 = pts[:, ejes]
    if len(p2) > int(maximo):
        idx = np.linspace(0, len(p2) - 1, int(maximo)).astype(int)
        p2 = p2[idx]
    if como is not None:
        centro, escala = como.centro_usado, como.escala_usada
    else:
        lo, hi = p2.min(axis=0), p2.max(axis=0)
        centro = (lo + hi) / 2.0
        escala = float(alto) / max((hi - lo)[1], _EPS)
    p2 = (p2 - centro) * escala
    curva = CurvaLorenz(color=color, stroke_width=grosor)
    curva.set_points_as_corners(np.column_stack([p2, np.zeros(len(p2))]))
    curva.escala_usada = escala
    curva.centro_usado = centro
    return curva


class CurvaSeparacion(VGroup):
    """log10(d) contra t; su pendiente ln es el exponente de Lyapunov."""

    def __init__(self, ejes, traza, params, **kwargs):
        super().__init__(ejes, traza, **kwargs)
        self.ejes = ejes
        self.traza = traza
        self._params = params

    def lyapunov(self):
        """Pendiente de ln d(t) ajustada sobre el tramo de crecimiento
        (antes de saturar al tamaño del atractor). Es el numero que el
        clip 5 rotula: MEDIDO, no citado."""
        d, dt = self._params["d"], self._params["dt"]
        t = np.arange(len(d)) * dt
        techo = d.max() * 0.05          # satura ~ al 5 % del diametro
        usar = (t > 1.0) & (d < techo) & (d > 0)
        if usar.sum() < 10:
            usar = (t > 0.5) & (d > 0)
        pend, _ = np.polyfit(t[usar], np.log(d[usar]), 1)
        return float(pend)

    def recta_ajuste(self, color=COLOR_GEMELO):
        """La recta del ajuste sobre la MISMA caja (geometria actual)."""
        d, dt = self._params["d"], self._params["dt"]
        lam = self.lyapunov()
        t = np.arange(len(d)) * dt
        t0 = 1.0
        ln0 = float(np.interp(t0, t, np.log(d)))
        t_fin = min(t.max(), t0 + (np.log(d.max() * 0.05) - ln0) / lam)
        p0 = self._a_escena(t0, ln0 / math.log(10.0))
        p1 = self._a_escena(t_fin, (ln0 + lam * (t_fin - t0))
                            / math.log(10.0))
        return Line(p0, p1, stroke_width=2.6, color=color)

    def _a_escena(self, t, log10_d):
        p = self._params
        origen = self.ejes[0].get_start()
        fx = t / p["t_max"]
        fy = ((log10_d - p["log_min"])
              / max(p["log_max"] - p["log_min"], _EPS))
        dx = (self.ejes[0].get_end() - origen) * fx
        dy = (self.ejes[1].get_end() - self.ejes[1].get_start()) * fy
        return origen + dx + dy


def curva_separacion(d, dt=0.005, ancho=5.6, alto=2.6, color=COLOR_ERROR,
                     color_ejes=COLOR_EJE, maximo=500):
    """Ejes (t ->, log10 d ^) con la curva de separacion, esquina en
    ORIGIN - (ancho, alto)/2. En log, el crecimiento exponencial es una
    recta: esa lectura ES el clip 5."""
    d = np.asarray(d, dtype=np.float64)
    d = np.maximum(d, 1e-16)
    log_d = np.log10(d)
    t = np.arange(len(d)) * float(dt)
    log_min, log_max = float(log_d.min()) - 0.3, float(log_d.max()) + 0.3

    esquina = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    eje_x = Line(esquina, esquina + RIGHT * ancho, stroke_width=2.0,
                 color=color_ejes)
    eje_y = Line(esquina, esquina + UP * alto, stroke_width=2.0,
                 color=color_ejes)
    ejes = VGroup(eje_x, eje_y)

    if len(d) > int(maximo):
        idx = np.linspace(0, len(d) - 1, int(maximo)).astype(int)
    else:
        idx = np.arange(len(d))
    fx = t[idx] / t.max()
    fy = (log_d[idx] - log_min) / max(log_max - log_min, _EPS)
    pts = esquina + np.column_stack([fx * ancho, fy * alto,
                                     np.zeros(len(idx))])
    traza = _poligonal(pts, color, 2.6)

    params = {"d": d, "dt": float(dt), "t_max": float(t.max()),
              "log_min": log_min, "log_max": log_max}
    return CurvaSeparacion(ejes, traza, params)


# =====================================================================
# El pendulo doble
# =====================================================================
_G, _L, _M = 9.8, 1.0, 1.0


def _pendulo_derivada(s):
    """s = (th1, w1, th2, w2), cada uno array (k,) o escalar."""
    th1, w1, th2, w2 = s
    delta = th1 - th2
    den = 2.0 * _M + _M - _M * np.cos(2.0 * delta)
    dw1 = (-_G * (2 * _M + _M) * np.sin(th1)
           - _M * _G * np.sin(th1 - 2 * th2)
           - 2 * np.sin(delta) * _M
           * (w2 * w2 * _L + w1 * w1 * _L * np.cos(delta))) / (_L * den)
    dw2 = (2 * np.sin(delta)
           * (w1 * w1 * _L * (_M + _M) + _G * (_M + _M) * np.cos(th1)
              + w2 * w2 * _L * _M * np.cos(delta))) / (_L * den)
    return np.array([w1, dw1, w2, dw2])


def _integra_pendulos(th1s, th2s, n, dt):
    """(n, 4, k): RK4 vectorizado sobre k pendulos a la vez."""
    n = _validar("pendulo.n", n, PASOS_MAX)
    dt = float(dt)
    th1s = np.atleast_1d(np.asarray(th1s, dtype=np.float64))
    th2s = np.atleast_1d(np.asarray(th2s, dtype=np.float64))
    k = len(th1s)
    s = np.zeros((4, k))
    s[0], s[2] = th1s, th2s
    salida = np.empty((n, 4, k))
    for paso in range(n):
        salida[paso] = s
        k1 = _pendulo_derivada(s)
        k2 = _pendulo_derivada(s + 0.5 * dt * k1)
        k3 = _pendulo_derivada(s + 0.5 * dt * k2)
        k4 = _pendulo_derivada(s + dt * k3)
        s = s + dt / 6.0 * (k1 + 2 * k2 + 2 * k3 + k4)
    return salida


def pendulo_doble(th1, th2, n=6000, dt=0.004):
    """(n, 4) estados de UN pendulo doble (th1, w1, th2, w2)."""
    return _integra_pendulos([float(th1)], [float(th2)], n, dt)[:, :, 0]


def energia_pendulo(estados):
    """Energia total por paso (para validar la integracion: deriva ~0)."""
    th1, w1, th2, w2 = (estados[:, i] for i in range(4))
    ep = -(2 * _M) * _G * _L * np.cos(th1) - _M * _G * _L * np.cos(th2)
    ec = (_M * _L * _L * w1 * w1
          + 0.5 * _M * _L * _L * w2 * w2
          + _M * _L * _L * w1 * w2 * np.cos(th1 - th2))
    return ep + ec


def _extremos(th1, th2, escala):
    """(codo, punta) en el plano, colgando de ORIGIN, en unidades escena."""
    codo = np.array([np.sin(th1), -np.cos(th1), 0.0]) * escala
    punta = codo + np.array([np.sin(th2), -np.cos(th2), 0.0]) * escala
    return codo, punta


class PenduloDoble(VGroup):
    """Dos brazos y dos bolas que reproducen una simulacion por alpha.

    `.en(alpha)` coloca los brazos en la fraccion `alpha` de la
    trayectoria (para UpdateFromAlphaFunc) y, si hay traza, la revela
    hasta ese punto. El pivote es el ancla del grupo.
    """

    def __init__(self, estados, escala=1.1, color=COLOR_SISTEMA,
                 con_traza=True, color_traza=COLOR_FASE, **kwargs):
        self._estados = np.asarray(estados, dtype=np.float64)
        self._escala = float(escala)
        pivote = _ancla(ORIGIN)
        th1, th2 = self._estados[0, 0], self._estados[0, 2]
        codo, punta = _extremos(th1, th2, self._escala)
        self.brazo1 = Line(ORIGIN, codo, stroke_width=4.0, color=color)
        self.brazo2 = Line(codo, punta, stroke_width=4.0, color=color)
        self.bola1 = Dot(codo, radius=0.055, color=color)
        self.bola2 = Dot(punta, radius=0.075, color=color)
        piezas = [pivote, self.brazo1, self.brazo2, self.bola1, self.bola2]

        self.traza = None
        if con_traza:
            puntas = np.array([_extremos(e[0], e[2], self._escala)[1]
                               for e in self._estados[::4]])
            self._traza_pts = puntas
            self.traza = VMobject(color=color_traza, stroke_width=1.6)
            self.traza.set_points_as_corners(puntas[:2])
            self.traza.set_stroke(opacity=0.55)
            piezas.insert(1, self.traza)

        super().__init__(*piezas, **kwargs)
        self._pivote = pivote

    def pivote(self):
        return self._pivote.get_center()

    def en(self, alpha):
        """Coloca brazos y bolas en la fraccion `alpha` de la simulacion."""
        alpha = float(np.clip(alpha, 0.0, 1.0))
        i = int(alpha * (len(self._estados) - 1))
        th1, th2 = self._estados[i, 0], self._estados[i, 2]
        base = self.pivote()
        codo, punta = _extremos(th1, th2, self._escala)
        self.brazo1.put_start_and_end_on(base, base + codo)
        self.brazo2.put_start_and_end_on(base + codo, base + punta)
        self.bola1.move_to(base + codo)
        self.bola2.move_to(base + punta)
        if self.traza is not None:
            j = max(int(alpha * (len(self._traza_pts) - 1)), 1)
            self.traza.set_points_as_corners(self._traza_pts[:j + 1] + base)
        return self


class Abanico(VGroup):
    """N pendulos casi identicos colgando del mismo pivote."""

    def __init__(self, pendulos, estados, **kwargs):
        super().__init__(*pendulos, **kwargs)
        self.pendulos = list(pendulos)
        self._estados = estados        # (n, 4, k)

    def en(self, alpha):
        for p in self.pendulos:
            p.en(alpha)
        return self

    def divergencia(self, alpha):
        """Dispersion (grados) de la punta: el numero que se rotula.
        Se mide sobre el angulo th2 SIN envolver, como salio del RK4."""
        alpha = float(np.clip(alpha, 0.0, 1.0))
        i = int(alpha * (len(self._estados) - 1))
        th2 = self._estados[i, 2, :]
        return float(np.degrees(th2.std()))


def abanico_pendulos(cuantos=25, eps_deg=0.01, th1_deg=120.0,
                     th2_deg=-10.0, n=5000, dt=0.004, escala=1.1,
                     color_a=COLOR_SISTEMA, color_b=COLOR_GEMELO):
    """`cuantos` pendulos con th2 separados `eps_deg` grados, degradado
    color_a -> color_b, sin trazas (la nube de brazos ES la imagen)."""
    cuantos = _validar("abanico_pendulos.cuantos", cuantos, PENDULOS_MAX)
    th1 = math.radians(float(th1_deg))
    th2s = np.radians(th2_deg + np.arange(cuantos) * float(eps_deg))
    estados = _integra_pendulos(np.full(cuantos, th1), th2s, n, dt)
    pendulos = []
    for j in range(cuantos):
        col = _mezcla_hex(color_a, color_b, j / max(cuantos - 1, 1))
        p = PenduloDoble(estados[:, :, j], escala=escala, color=col,
                         con_traza=False)
        p.brazo1.set_stroke(width=2.2, opacity=0.8)
        p.brazo2.set_stroke(width=2.2, opacity=0.8)
        p.bola1.scale(0.6)
        p.bola2.scale(0.8)
        pendulos.append(p)
    return Abanico(pendulos, estados)


# =====================================================================
# Caos no es azar
# =====================================================================
def ruido_uniforme(n, semilla=9):
    """Azar de verdad (uniforme [0,1]), determinista por semilla."""
    n = _validar("ruido_uniforme.n", n, PASOS_MAX)
    return np.random.default_rng(int(semilla)).uniform(0.0, 1.0, n)


class MapaRetorno(VGroup):
    """Nube (x_k, x_{k+1}) sobre una caja con diagonal tenue."""

    def __init__(self, ancla, caja, nube, params, **kwargs):
        super().__init__(ancla, caja, nube, **kwargs)
        self._ancla = ancla
        self.caja = caja
        self.nube = nube
        self._params = params


def mapa_retorno(serie, lado=3.4, color=COLOR_SISTEMA, radio=0.028,
                 color_ejes=COLOR_EJE):
    """El detector de reglas: el caos dibuja su curva, el ruido llena."""
    serie = np.asarray(serie, dtype=np.float64)
    if len(serie) - 1 > PUNTOS_NUBE_MAX:
        raise ValueError(f"mapa_retorno: {len(serie) - 1} puntos "
                         f"> {PUNTOS_NUBE_MAX}")
    lado = float(lado)
    esquina = np.array([-lado / 2.0, -lado / 2.0, 0.0])
    caja = VGroup(
        Line(esquina, esquina + RIGHT * lado, stroke_width=2.0,
             color=color_ejes),
        Line(esquina, esquina + UP * lado, stroke_width=2.0,
             color=color_ejes),
        Line(esquina, esquina + (RIGHT + UP) * lado, stroke_width=1.2,
             color=color_ejes).set_stroke(opacity=0.5))
    nube = VGroup(*[
        Dot(esquina + RIGHT * serie[k] * lado + UP * serie[k + 1] * lado,
            radius=float(radio), color=color)
        for k in range(len(serie) - 1)])
    params = {"lado": lado}
    return MapaRetorno(_ancla(esquina), caja, nube, params)
