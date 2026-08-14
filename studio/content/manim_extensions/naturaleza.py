"""Matematicas en la naturaleza: filotaxis, phi, fractales biologicos,
Turing, meandros, e y hexagonos.

Pensado para el curso "Matematicas en la naturaleza". Todo el calculo es
numpy puro y determinista (`np.random.default_rng(semilla)` donde hace falta
azar: el chaos game del helecho, el ruido inicial de Turing, el micelio y el
basalto): mismo script -> mismo render, condicion necesaria para trabajar
con `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: la REGLA
matematica es ambar, lo VIVO verde, la CONSTANTE que la regla produce (phi,
pi, e, 137.5 grados) cian, el MITO y el desperdicio rojos, la QUIMICA que
calcula violeta. Mobiliario en el gris azulado `COLOR_EJE`.

Piezas:
    filotaxis             el girasol: semillas en r=c*sqrt(k), un giro fijo
    rectangulos_fibonacci los cuadrados 1,1,2,3,5,8 con su espiral de arcos
    espiral_log           r = a*e^(b*theta); escalar es girar (autosemejanza)
    gato_dormido          silueta de gato enroscado (mobiliario narrativo)
    imagen_helecho        el helecho de Barnsley como imagen por densidad
    mapas_helecho_marcos  las 4 reglas afines dibujadas como marcos fantasma
    arbol_fractal         arbol binario por niveles, para crecerlo en escena
    red_micelio           hifas que se ramifican desde un punto (los hongos)
    campo_turing          Gray-Scott: la quimica que pinta manchas y rayas
    secuencia_turing      el mismo campo a tiempos crecientes, para animarlo
    imagen_turing         el campo como imagen, opcionalmente DENTRO de una
                          silueta (un gato con el pelaje recien calculado)
    gato_sentado          silueta de gato sentado, contorno y mascara
    rio_meandro           curva sine-generated de Langbein-Leopold; mide su
                          propia sinuosidad (camino / recta)
    onda_circular         anillos concentricos (una gota en el agua)
    curva_crecimiento     ejes + e^(tasa*t); con tasa negativa, decae
    escalera_compuesta    capitalizar en n saltos sobre la misma caja
    panal                 reticula hexagonal; con jitter, basalto
    tesela_unidad         triangulo/cuadrado/hexagono de AREA exacta 1

Las piezas exponen localizadores calculados sobre la geometria ACTUAL del
mobject (`.semilla`, `.polo`, `.punto_en`, `.extremos`, `.celda`, ...):
siguen validos despues de mover o escalar. Y exponen los NUMEROS que
dibujan (`.sinuosidad()`, `.cociente(i)`, `.valor_final()`,
`perimetro_por_area(n)`): en un curso sobre el codigo de la naturaleza, el
rotulo del clip sale de la misma fuente que el dibujo, nunca a mano.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`SEMILLAS_MAX`, `HELECHO_PUNTOS_MAX`, `RES_CAMPO_MAX`, `PASOS_TURING_MAX`,
`CUADROS_TURING_MAX`, `NIVELES_ARBOL_MAX` y `MUESTRAS_MAX` levantan
ValueError; pasarse cambia lo que se ve y es mejor enterarse.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from naturaleza import filotaxis, campo_turing, imagen_turing

    disco = filotaxis(600, 137.5077)
    self.play(disco.aparecer())
    self.play(Transform(disco, disco.con_angulo(90.0)))

    campo = campo_turing(*TURING_MANCHAS)
    self.add(imagen_turing(campo, alto_escena=5.0))
"""

import math

import numpy as np

from manim import (Arc, Circle, DashedVMobject, Dot, FadeIn, GrowFromCenter,
                   ImageMobject, LaggedStart, Line, Polygon, Text, VGroup,
                   VMobject, DOWN, LEFT, ORIGIN, RIGHT, UP)

from code_brand import FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
SEMILLAS_MAX = 900          # semillas de un disco de filotaxis
HELECHO_PUNTOS_MAX = 400_000
RES_CAMPO_MAX = 360         # lado mayor (px) de un campo de Turing
PASOS_TURING_MAX = 12_000
CUADROS_TURING_MAX = 12
NIVELES_ARBOL_MAX = 8
MUESTRAS_MAX = 600          # muestras de una curva parametrica
CUADROS_FIB_MAX = 9

# Paleta propia de la libreria (coincide con la del curso).
COLOR_REGLA = "#f59e0b"      # la regla matematica: curvas, angulos, teselas
COLOR_VIDA = "#34d399"       # lo vivo: semillas, helecho, ramas, micelio
COLOR_CONSTANTE = "#22d3ee"  # la constante que la regla produce: phi, pi, e
COLOR_MITO = "#f43f5e"       # el desperdicio, el error, el mito
COLOR_QUIMICA = "#a78bfa"    # la quimica que calcula: morfogenos, decaer
COLOR_EJE = "#31414f"        # mobiliario: ejes, guias, marcos

C_REGLA, C_VIDA, C_CONSTANTE = COLOR_REGLA, COLOR_VIDA, COLOR_CONSTANTE
C_MITO, C_QUIMICA, C_EJE = COLOR_MITO, COLOR_QUIMICA, COLOR_EJE

# --- Los numeros del curso -------------------------------------------
PHI = (1.0 + math.sqrt(5.0)) / 2.0            # 1.6180339887...
ANGULO_AUREO_DEG = 360.0 / PHI ** 2           # 137.5077640...
FIB = (1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144)
E = math.e                                    # 2.7182818284...
B_AUREA = math.log(PHI) / (math.pi / 2.0)     # 0.3063: la espiral aurea
B_NAUTILUS = 0.18                             # el nautilus real (~3.1/vuelta)
TURING_MANCHAS = (0.0367, 0.0649)             # (F, k): leopardo
TURING_RAYAS = (0.0460, 0.0630)               # (F, k): cebra / gato atigrado
OMEGA_PI_DEG = 109.4                          # el meandro cuya sinuosidad ~ pi

_EPS = 1e-9


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Etiqueta tecnica corta en la tipografia de telemetria de la marca."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _hex_a_rgb(hexcolor):
    h = str(hexcolor).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)],
                    dtype=np.float64)


def _mezcla(color_a, color_b, t):
    """Interpolacion lineal entre dos hex; t escalar o array (n,)."""
    a, b = _hex_a_rgb(color_a), _hex_a_rgb(color_b)
    t = np.clip(np.asarray(t, dtype=np.float64), 0.0, 1.0)
    return a + (b - a) * t[..., None]


def _a_hex(rgb):
    r, g, b = (int(round(v)) for v in np.clip(rgb, 0, 255))
    return f"#{r:02x}{g:02x}{b:02x}"


def _curva(puntos, color, grosor=3.0, cerrada=False):
    """VMobject suave a partir de un array (n, 2) o (n, 3) de escena."""
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly(pts)
    if cerrada:
        curva.close_path()
    return curva


def _poligonal(puntos, color, grosor=2.0):
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


def _ancla(punto):
    """Dot invisible que viaja con la pieza: localizador inmune a move_to.

    Un atributo numpy cacheado se queda mudo cuando el grupo se mueve; un
    submobject de radio infimo siempre reporta su posicion ACTUAL.
    """
    return Dot(np.append(np.asarray(punto, dtype=np.float64), 0.0)
               if len(np.ravel(punto)) == 2 else punto,
               radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)


def _validar(nombre, valor, tope):
    valor = int(valor)
    if valor < 1 or valor > tope:
        raise ValueError(f"{nombre}: {valor} fuera de rango (1..{tope})")
    return valor


def _imagen(rgba, alto_escena):
    img = ImageMobject(rgba)
    img.set_resampling_algorithm(3)  # BICUBIC: escala sin pixelado duro
    if alto_escena is not None:
        img.height = alto_escena
    return img


def _spline_cerrada(control, filos=(), por_tramo=14):
    """Catmull-Rom cerrada por los puntos de control; tangente nula en los
    indices `filos` (puntas de oreja, punta de cola). Devuelve (n, 2)."""
    P = np.asarray(control, dtype=np.float64)
    n = len(P)
    filos = set(int(i) % n for i in filos)

    def tangente(i):
        if i in filos:
            return np.zeros(2)
        return (P[(i + 1) % n] - P[(i - 1) % n]) * 0.5

    t = np.linspace(0.0, 1.0, por_tramo, endpoint=False)
    h00 = 2 * t ** 3 - 3 * t ** 2 + 1
    h10 = t ** 3 - 2 * t ** 2 + t
    h01 = -2 * t ** 3 + 3 * t ** 2
    h11 = t ** 3 - t ** 2
    tramos = []
    for i in range(n):
        p0, p1 = P[i], P[(i + 1) % n]
        m0, m1 = tangente(i), tangente((i + 1) % n)
        tramos.append(h00[:, None] * p0 + h10[:, None] * m0
                      + h01[:, None] * p1 + h11[:, None] * m1)
    pts = np.vstack(tramos)
    return np.vstack([pts, pts[:1]])


def _mascara_poligono(poligono, res_x, res_y):
    """Mascara booleana (res_y, res_x) del interior de un poligono en
    coordenadas [0,1]x[0,1] (par-impar, ray casting vectorizado)."""
    P = np.asarray(poligono, dtype=np.float64)
    xs = (np.arange(res_x) + 0.5) / res_x
    ys = (np.arange(res_y) + 0.5) / res_y
    X, Y = np.meshgrid(xs, ys)
    dentro = np.zeros(X.shape, dtype=bool)
    n = len(P)
    for i in range(n):
        x1, y1 = P[i]
        x2, y2 = P[(i + 1) % n]
        if abs(y2 - y1) < _EPS:
            continue
        corta = (y1 > Y) != (y2 > Y)
        x_corte = (x2 - x1) * (Y - y1) / (y2 - y1) + x1
        dentro ^= corta & (X < x_corte)
    return dentro


# =====================================================================
# Filotaxis: el reparto del girasol
# =====================================================================
def _puntos_filotaxis(n, angulo_deg, escala):
    """(n, 2): semilla k en r = escala*sqrt(k/(n-1)), theta = k*angulo."""
    k = np.arange(n, dtype=np.float64)
    r = escala * np.sqrt(k / max(n - 1, 1))
    th = np.deg2rad(angulo_deg) * k
    return np.column_stack([r * np.cos(th), r * np.sin(th)])


class Filotaxis(VGroup):
    """Disco de semillas nacidas con un giro fijo; el angulo es la pieza."""

    def __init__(self, ancla, puntos_mob, params, **kwargs):
        super().__init__(ancla, puntos_mob, **kwargs)
        self._ancla = ancla
        self.puntos = puntos_mob
        self._params = params
        self.angulo = params["angulo_deg"]
        self.n = params["n"]

    def polo(self):
        """Centro real del disco (el punto donde nacen las semillas)."""
        return self._ancla.get_center()

    def semilla(self, k):
        """Posicion ACTUAL de la semilla k (0-based)."""
        return self.puntos[int(k)].get_center()

    def aparecer(self, run_time=3.0, lag_ratio=None):
        """Las semillas nacen del centro hacia afuera, una a una."""
        dots = list(self.puntos)
        lag = lag_ratio if lag_ratio is not None else 3.0 / max(len(dots), 1)
        return LaggedStart(*[GrowFromCenter(d) for d in dots],
                           lag_ratio=lag, run_time=run_time)

    def con_angulo(self, angulo_deg):
        """El mismo disco con otro giro por semilla, anclado en el polo:
        Transform semilla a semilla (mismo numero de puntos)."""
        params = dict(self._params, angulo_deg=float(angulo_deg))
        otro = filotaxis(**params)
        otro.shift(self.polo() - otro.polo())
        return otro

    def parastica(self, m, color=COLOR_CONSTANTE, grosor=3.0, desde=None):
        """Curva que une las semillas k, k+m, k+2m...: una espiral visible.

        Se calcula sobre la geometria ACTUAL de los puntos, asi que vale
        despues de mover o escalar el disco.
        """
        m = int(m)
        desde = m if desde is None else int(desde)
        idx = list(range(desde, self.n, m))
        if len(idx) < 3:
            raise ValueError(f"parastica({m}): solo {len(idx)} semillas")
        pts = np.array([self.semilla(k) for k in idx])
        return _curva(pts, color, grosor).set_stroke(opacity=0.9)

    def rayos_vacios(self, color=COLOR_MITO):
        """Con un angulo racional (90, 120...) las semillas caen en rayos;
        esto devuelve las cuñas VACIAS entre rayos, teñidas: el desperdicio.
        Solo tiene sentido con angulos que dividen 360 exacto."""
        paso = float(self._params["angulo_deg"]) % 360.0
        brazos = int(round(360.0 / paso)) if paso > _EPS else 1
        if abs(brazos * paso - 360.0) > 1.0:
            raise ValueError("rayos_vacios: el angulo no forma rayos")
        escala = self._params["escala"]
        polo = self.polo()
        cunas = VGroup()
        for i in range(brazos):
            a0 = math.radians(paso * i + paso * 0.16)
            a1 = math.radians(paso * (i + 1) - paso * 0.16)
            th = np.linspace(a0, a1, 14)
            borde = np.column_stack([np.cos(th), np.sin(th)]) * escala * 1.02
            pts = np.vstack([[0.0, 0.0], borde]) + polo[:2]
            cuna = Polygon(*[np.append(p, 0.0) for p in pts],
                           stroke_width=0, fill_color=color, fill_opacity=0.22)
            cunas.add(cuna)
        return cunas


def filotaxis(n=600, angulo_deg=ANGULO_AUREO_DEG, escala=2.6,
              color_centro=COLOR_REGLA, color_borde=COLOR_VIDA,
              radio_semilla=None):
    """Disco de filotaxis: n semillas, un giro fijo, degradado radial."""
    n = _validar("filotaxis.n", n, SEMILLAS_MAX)
    pts = _puntos_filotaxis(n, float(angulo_deg), float(escala))
    radio = (0.72 * escala / math.sqrt(n)) if radio_semilla is None \
        else float(radio_semilla)
    r_rel = np.linalg.norm(pts, axis=1) / max(float(escala), _EPS)
    colores = _mezcla(color_centro, color_borde, r_rel)
    dots = VGroup(*[
        Dot(np.append(p, 0.0), radius=radio, color=_a_hex(c))
        for p, c in zip(pts, colores)])
    params = {"n": n, "angulo_deg": float(angulo_deg),
              "escala": float(escala), "color_centro": color_centro,
              "color_borde": color_borde, "radio_semilla": radio}
    return Filotaxis(_ancla(ORIGIN), dots, params)


# =====================================================================
# Fibonacci y la espiral
# =====================================================================
class RectangulosFib(VGroup):
    """Cuadrados 1,1,2,3,5,8... en espiral, con su arco dentro de cada uno."""

    def __init__(self, cuadros, arcos, params, **kwargs):
        super().__init__(cuadros, arcos, **kwargs)
        self.cuadros = cuadros
        self.arcos = arcos
        self._params = params

    def cuadro(self, i):
        return self.cuadros[int(i)]

    def arco(self, i):
        return self.arcos[int(i)]

    def aparecer(self, i, run_time=0.5):
        """El cuadrado i y su arco, juntos (para armar la espiral por beats)."""
        return FadeIn(VGroup(self.cuadros[int(i)], self.arcos[int(i)]),
                      run_time=run_time)

    @staticmethod
    def cociente(i):
        """F(i+1)/F(i): la sucesion de cocientes que se acerca a phi."""
        return FIB[int(i) + 1] / FIB[int(i)]


def rectangulos_fibonacci(n=7, lado=0.32, color=COLOR_EJE,
                          color_arco=COLOR_REGLA):
    """Los primeros n cuadrados de Fibonacci con su espiral de arcos.

    `lado` es el tamaño en escena del cuadrado unidad. El conjunto se centra
    en ORIGIN. Direcciones: derecha, arriba, izquierda, abajo, girando en
    contra de las agujas (la espiral crece hacia afuera).
    """
    n = _validar("rectangulos_fibonacci.n", n, CUADROS_FIB_MAX)
    # Cajas [x0, x1, y0, y1] en unidades de Fibonacci.
    cajas = [(0.0, 1.0, 0.0, 1.0)]
    bx0, bx1, by0, by1 = 0.0, 1.0, 0.0, 1.0
    # (arco: centro, angulo inicial) por direccion de anexado.
    arcos_spec = [((0.0, 1.0), -math.pi / 2)]  # cuadro 1: centro arriba-izq
    for i in range(1, n):
        f = float(FIB[i])
        rumbo = (i - 1) % 4  # 0 der, 1 arriba, 2 izq, 3 abajo
        if rumbo == 0:
            caja = (bx1, bx1 + f, by0, by0 + f)
            centro, a0 = (caja[0], caja[3]), -math.pi / 2
        elif rumbo == 1:
            caja = (bx0, bx0 + f, by1, by1 + f)
            centro, a0 = (caja[0], caja[2]), 0.0
        elif rumbo == 2:
            caja = (bx0 - f, bx0, by0, by0 + f)
            centro, a0 = (caja[1], caja[2]), math.pi / 2
        else:
            caja = (bx0, bx0 + f, by0 - f, by0)
            centro, a0 = (caja[1], caja[3]), math.pi
        cajas.append(caja)
        arcos_spec.append((centro, a0))
        bx0, bx1 = min(bx0, caja[0]), max(bx1, caja[1])
        by0, by1 = min(by0, caja[2]), max(by1, caja[3])

    despl = np.array([(bx0 + bx1) / 2.0, (by0 + by1) / 2.0])
    cuadros, arcos = VGroup(), VGroup()
    for i, ((x0, x1, y0, y1), (centro, a0)) in enumerate(zip(cajas,
                                                             arcos_spec)):
        f = float(FIB[i])
        esquinas = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        cuadros.add(Polygon(
            *[np.append((np.array(e) - despl) * lado, 0.0) for e in esquinas],
            stroke_width=1.8, stroke_color=color, fill_opacity=0.0))
        c = (np.array(centro) - despl) * lado
        arcos.add(Arc(radius=f * lado, start_angle=a0, angle=math.pi / 2,
                      arc_center=np.append(c, 0.0), color=color_arco,
                      stroke_width=3.0))
    params = {"n": n, "lado": lado}
    return RectangulosFib(cuadros, arcos, params)


class EspiralLog(VGroup):
    """r = a*e^(b*theta): la espiral del crecimiento autosemejante."""

    def __init__(self, ancla, curva, params, **kwargs):
        super().__init__(ancla, curva, **kwargs)
        self._ancla = ancla
        self.curva = curva
        self._params = params
        self.b = params["b"]

    def polo(self):
        """El polo ACTUAL de la espiral (no esta sobre la curva)."""
        return self._ancla.get_center()

    def punto_en(self, theta):
        """Punto de la curva en el angulo `theta` (radianes), geometria
        actual: se interpola sobre los puntos ya dibujados."""
        t0, t1 = 0.0, self._params["vueltas"] * 2.0 * math.pi
        alpha = float(np.clip((theta - t0) / max(t1 - t0, _EPS), 0.0, 1.0))
        return self.curva.point_from_proportion(alpha)

    def autosemejante(self, factor=PHI):
        """(copia escalada, angulo): escalar la espiral por `factor` desde
        el polo produce LA MISMA espiral girada. La copia se devuelve YA
        escalada; girarla `angulo` radianes sobre el polo
        (`copia.rotate(angulo, about_point=esp.polo())`) la calza sobre la
        original — esa es la demostracion de la autosemejanza."""
        angulo = math.log(float(factor)) / self.b
        copia = self.copy()
        copia.scale(float(factor), about_point=self.polo())
        return copia, angulo


def espiral_log(b=B_AUREA, vueltas=3.0, escala=1.0, color=COLOR_REGLA,
                grosor=3.4, muestras=360):
    """Espiral logaritmica con el radio exterior igual a `escala`."""
    muestras = _validar("espiral_log.muestras", muestras, MUESTRAS_MAX)
    b = float(b)
    th_max = float(vueltas) * 2.0 * math.pi
    a = float(escala) / math.exp(b * th_max)
    th = np.linspace(0.0, th_max, muestras)
    r = a * np.exp(b * th)
    pts = np.column_stack([r * np.cos(th), r * np.sin(th)])
    curva = _curva(pts, color, grosor)
    params = {"b": b, "vueltas": float(vueltas), "escala": float(escala)}
    return EspiralLog(_ancla(ORIGIN), curva, params)


# =====================================================================
# Gatos (mobiliario narrativo: silueta cerrada + mascara)
# =====================================================================
def _gato_sentado_control():
    """Puntos de control (x, y) de un gato sentado de perfil, mirando a la
    IZQUIERDA, en una caja de ~1.6 x 2.3 centrada en (0, 0). Los indices
    filosos son las puntas y muescas de las orejas."""
    control = [
        (-0.62, 0.42),    # 0 mejilla / mandibula
        (-0.72, 0.66),    # 1 hocico
        (-0.68, 0.90),    # 2 frente
        (-0.74, 1.16),    # 3 punta oreja izquierda  [filo]
        (-0.46, 1.02),    # 4 muesca entre orejas    [filo]
        (-0.26, 1.18),    # 5 punta oreja derecha    [filo]
        (-0.08, 0.94),    # 6 nuca
        (0.05, 0.60),     # 7 cuello
        (0.32, 0.18),     # 8 lomo
        (0.62, -0.34),    # 9 anca (la joroba de sentado)
        (0.66, -0.80),    # 10 grupa
        (0.42, -1.04),    # 11 base trasera
        (-0.06, -1.08),   # 12 suelo
        (-0.50, -1.08),   # 13 patas delanteras (suelo)
        (-0.86, -1.02),   # 14 cola por delante
        (-1.02, -0.86),   # 15 punta de cola        [filo]
        (-0.84, -0.76),   # 16 cola, lomo superior
        (-0.56, -0.74),   # 17 cola contra la pata
        (-0.50, -0.40),   # 18 pata delantera
        (-0.56, 0.02),    # 19 pecho
    ]
    return control, (3, 4, 5, 15)


def _gato_dormido_control():
    """Gato enroscado (dormido): un ovillo con la cabeza recostada a la
    derecha (orejas bien salidas) y la cola envolviendo por abajo. Caja
    ~2.4 x 1.9 centrada en (0, 0)."""
    control = [
        (1.06, 0.20),     # 0 mejilla derecha
        (1.10, 0.48),     # 1 frente
        (1.24, 0.86),     # 2 punta oreja derecha  [filo]
        (0.88, 0.66),     # 3 muesca               [filo]
        (0.74, 1.00),     # 4 punta oreja izquierda [filo]
        (0.48, 0.74),     # 5 nuca (hendidura cabeza-lomo)
        (0.10, 0.92),     # 6 lomo alto
        (-0.52, 0.84),    # 7 lomo
        (-0.96, 0.46),    # 8 costado
        (-1.12, -0.02),   # 9 flanco izquierdo
        (-0.96, -0.52),   # 10 curva baja
        (-0.50, -0.86),   # 11 vientre
        (0.08, -0.96),    # 12 cola envolviendo
        (0.66, -0.84),    # 13 cola
        (1.08, -0.52),    # 14 punta de cola frente al hocico [filo]
        (1.14, -0.16),    # 15 mejilla baja
    ]
    return control, (2, 3, 4, 5, 14)


def _silueta(control, filos, escala, color, relleno):
    pts2 = _spline_cerrada(control, filos)
    mob = VMobject(stroke_color=color, stroke_width=2.6,
                   fill_color=relleno, fill_opacity=0.92)
    pts3 = np.column_stack([pts2, np.zeros(len(pts2))]) * float(escala)
    mob.set_points_as_corners(pts3)
    mob.puntos_poligono = pts2 * float(escala)   # locales, para la mascara
    mob._ancho_original = mob.width
    return mob


def gato_sentado(escala=1.0, color="#0d1420", relleno="#0d1420"):
    """Silueta cerrada de gato sentado (mira a la izquierda). Atributo
    `.puntos_poligono` para `imagen_turing(silueta=...)`."""
    control, filos = _gato_sentado_control()
    return _silueta(control, filos, escala, color, relleno)


def gato_dormido(escala=1.0, color="#5a6b80", relleno="#131d2b",
                 color_detalle="#5a6b80"):
    """Gato enroscado: VGroup(silueta, detalle). El detalle (curva de la
    cabeza recostada y trazo de la cola envolviendo) hace legible el ovillo
    sobre el relleno oscuro. Su enrollado sigue una espiral logaritmica:
    anclar una `espiral_log(b~0.35, ~1.8 vueltas)` en su centro la abraza
    (la comprobacion del clip 3). Atributos `.silueta` y `.detalle`."""
    control, filos = _gato_dormido_control()
    cuerpo = _silueta(control, filos, escala, color, relleno)
    e = float(escala)
    # La cabeza recostada: arco de la mejilla a la nuca.
    cabeza = _curva(np.array([(1.02, -0.14), (0.72, 0.10), (0.52, 0.44),
                              (0.50, 0.72)]) * e,
                    color_detalle, 2.2)
    # La cola que envuelve: paralela al borde inferior, hasta su punta.
    cola = _curva(np.array([(-0.42, -0.66), (0.10, -0.78), (0.62, -0.68),
                            (0.94, -0.44)]) * e,
                  color_detalle, 2.2)
    for trazo in (cabeza, cola):
        trazo.set_stroke(opacity=0.75)
    grupo = VGroup(cuerpo, cabeza, cola)
    grupo.silueta = cuerpo
    grupo.detalle = VGroup(cabeza, cola)
    grupo.puntos_poligono = cuerpo.puntos_poligono
    return grupo


# =====================================================================
# El helecho de Barnsley (IFS) y los fractales que crecen
# =====================================================================
# (matriz 2x2 aplanada por filas, traslacion, probabilidad) — Barnsley 1988.
MAPAS_HELECHO = (
    ((0.00, 0.00, 0.00, 0.16), (0.0, 0.00), 0.01),
    ((0.85, 0.04, -0.04, 0.85), (0.0, 1.60), 0.85),
    ((0.20, -0.26, 0.23, 0.22), (0.0, 1.60), 0.07),
    ((-0.15, 0.28, 0.26, 0.24), (0.0, 0.44), 0.07),
)


def _puntos_helecho(n, semilla=2):
    """(n, 2) puntos del chaos game, SIEMPRE el mismo prefijo: pedir 300 y
    pedir 250 000 comparten los primeros 300 (la acumulacion del clip 4).

    Enjambre vectorizado: 500 particulas avanzan juntas; el orden de emision
    es (paso, particula), asi que el prefijo es estable para una semilla.
    """
    n = _validar("helecho.puntos", n, HELECHO_PUNTOS_MAX)
    rng = np.random.default_rng(int(semilla))
    enjambre = 500
    mats = np.array([m for m, _, _ in MAPAS_HELECHO]).reshape(4, 2, 2)
    tras = np.array([t for _, t, _ in MAPAS_HELECHO])
    probs = np.array([p for _, _, p in MAPAS_HELECHO])
    probs = probs / probs.sum()

    pts = np.zeros((enjambre, 2))
    # Burn-in: 15 pasos para caer en el atractor antes de emitir.
    total_pasos = 15 + math.ceil(n / enjambre)
    emitidos = []
    for paso in range(total_pasos):
        eleccion = rng.choice(4, size=enjambre, p=probs)
        nuevo = np.einsum("kij,kj->ki", mats[eleccion], pts) + tras[eleccion]
        pts = nuevo
        if paso >= 15:
            emitidos.append(pts.copy())
    salida = np.vstack(emitidos)[:n]
    return salida


def imagen_helecho(puntos=250_000, res=(560, 840), color=COLOR_VIDA,
                   alto_escena=6.0, semilla=2, fondo=None):
    """El helecho de Barnsley como imagen por densidad (brillo log).

    Con `puntos` chico (300, 3000) la nube rala del mismo prefijo: relevar
    imagenes con puntos crecientes ES la animacion de la acumulacion.
    `fondo=None` deja el exterior transparente (alpha 0).
    """
    res_x, res_y = int(res[0]), int(res[1])
    if max(res_x, res_y) > 2200:
        raise ValueError(f"imagen_helecho: res {res} demasiado grande")
    pts = _puntos_helecho(puntos, semilla)
    # Caja fija del atractor (no la de los puntos pedidos): asi la imagen de
    # 300 puntos y la de 250 000 comparten encuadre y el relevo no salta.
    x0, x1, y0, y1 = -2.75, 2.75, -0.10, 10.10
    hist, _, _ = np.histogram2d(
        pts[:, 0], pts[:, 1], bins=[res_x, res_y],
        range=[[x0, x1], [y0, y1]])
    dens = np.log1p(hist.T[::-1])            # filas = y invertida (imagen)
    if dens.max() > 0:
        dens = dens / dens.max()
    # Con pocos puntos el log aplasta: garantiza que un pixel tocado se vea.
    dens = np.where(dens > 0, np.maximum(dens, 0.55), 0.0)
    tinta = _hex_a_rgb(color)
    rgba = np.zeros((res_y, res_x, 4), dtype=np.uint8)
    if fondo is None:
        rgba[..., :3] = np.clip(tinta * dens[..., None] * 1.35, 0,
                                255).astype(np.uint8)
        rgba[..., 3] = np.clip(dens * 255 * 1.6, 0, 255).astype(np.uint8)
    else:
        base = _hex_a_rgb(fondo)
        rgb = base + (tinta - base) * dens[..., None]
        rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        rgba[..., 3] = 255
    return _imagen(rgba, alto_escena)


def mapas_helecho_marcos(alto_escena=6.0, colores=(COLOR_REGLA,
                                                   COLOR_CONSTANTE,
                                                   COLOR_QUIMICA,
                                                   COLOR_MITO)):
    """Las 4 reglas afines como marcos: cada una dibuja DONDE ese mapa mete
    una copia entera del helecho (la caja del atractor transformada).

    Escalado igual que `imagen_helecho(alto_escena=...)`: superponer ambos
    con el mismo centro alinea marcos e imagen.
    """
    x0, x1, y0, y1 = -2.75, 2.75, -0.10, 10.10
    esquinas = np.array([[x0, y0], [x1, y0], [x1, y1], [x0, y1]])
    escala = float(alto_escena) / (y1 - y0)
    centro = np.array([(x0 + x1) / 2.0, (y0 + y1) / 2.0])
    marcos = VGroup()
    for (m, t, _), col in zip(MAPAS_HELECHO, colores):
        M = np.array(m).reshape(2, 2)
        trans = (esquinas @ M.T) + np.array(t)
        pts = (trans - centro) * escala
        marcos.add(Polygon(*[np.append(p, 0.0) for p in pts],
                           stroke_width=2.2, stroke_color=col,
                           fill_opacity=0.0).set_stroke(opacity=0.85))
    return marcos


class ArbolFractal(VGroup):
    """Arbol binario: una rama que se repite mas chica y girada."""

    def __init__(self, niveles_vg, params, **kwargs):
        super().__init__(*niveles_vg, **kwargs)
        self.niveles = list(niveles_vg)
        self._params = params

    def nivel(self, i):
        """VGroup de las ramas de la generacion i (0 = tronco)."""
        return self.niveles[int(i)]

    def raiz(self):
        """Base ACTUAL del tronco (donde el arbol toca el suelo)."""
        return self.niveles[0][0].get_start()

    def con_angulo(self, angulo_deg):
        """El mismo arbol con otro angulo de ramificacion, anclado por la
        base del tronco (el bounding box cambia con el angulo y move_to
        haria 'saltar' el suelo)."""
        params = dict(self._params, angulo_deg=float(angulo_deg))
        otro = arbol_fractal(**params)
        otro.shift(self.raiz() - otro.raiz())
        return otro


def arbol_fractal(niveles=7, angulo_deg=27.0, razon=0.72, escala=1.0,
                  color=COLOR_EJE, color_puntas=COLOR_VIDA):
    """Arbol fractal binario, tronco abajo (crece hacia arriba).

    El color pasa del tronco (`color`) a las puntas (`color_puntas`), y el
    grosor decae con el nivel: se lee la generacion sin contar ramas.
    """
    niveles = _validar("arbol_fractal.niveles", niveles, NIVELES_ARBOL_MAX)
    ang = math.radians(float(angulo_deg))
    razon = float(razon)
    largo0 = 1.05 * float(escala)
    grupos = []
    frentes = [(np.array([0.0, -1.3 * escala]), math.pi / 2, largo0)]
    for nivel in range(niveles):
        t = nivel / max(niveles - 1, 1)
        col = _a_hex(_mezcla(color, color_puntas, t))
        grosor = max(1.2, 4.6 * (0.78 ** nivel))
        capa = VGroup()
        siguientes = []
        for origen, rumbo, largo in frentes:
            destino = origen + largo * np.array([math.cos(rumbo),
                                                 math.sin(rumbo)])
            capa.add(Line(np.append(origen, 0.0), np.append(destino, 0.0),
                          stroke_width=grosor, color=col))
            siguientes.append((destino, rumbo + ang, largo * razon))
            siguientes.append((destino, rumbo - ang, largo * razon))
        grupos.append(capa)
        frentes = siguientes
    params = {"niveles": niveles, "angulo_deg": float(angulo_deg),
              "razon": razon, "escala": float(escala), "color": color,
              "color_puntas": color_puntas}
    return ArbolFractal(grupos, params)


class RedMicelio(VGroup):
    """Hifas que crecen desde un punto, ramificandose: la red del hongo."""

    def __init__(self, anillos_vg, params, **kwargs):
        super().__init__(*anillos_vg, **kwargs)
        self.anillos = list(anillos_vg)
        self._params = params

    def anillo(self, i):
        """VGroup de los segmentos de la generacion i."""
        return self.anillos[int(i)]


def red_micelio(radios=5, brotes=26, semilla=5, escala=1.0,
                color=COLOR_VIDA):
    """Red de micelio: `brotes` hifas radiales que avanzan y se ramifican
    (azar determinista). La opacidad cae hacia afuera: la red se difumina."""
    radios = _validar("red_micelio.radios", radios, 7)
    brotes = _validar("red_micelio.brotes", brotes, 40)
    rng = np.random.default_rng(int(semilla))
    paso0 = 0.34 * float(escala)
    anillos = []
    frentes = [(np.array([0.0, 0.0]),
                2 * math.pi * i / brotes + rng.normal(0, 0.12))
               for i in range(brotes)]
    for gen in range(radios):
        capa = VGroup()
        siguientes = []
        largo = paso0 * (0.88 ** gen)
        opacidad = 0.95 * (0.82 ** gen)
        grosor = max(1.0, 2.6 * (0.85 ** gen))
        for origen, rumbo in frentes:
            rumbo2 = rumbo + rng.normal(0.0, 0.22)
            destino = origen + largo * np.array([math.cos(rumbo2),
                                                 math.sin(rumbo2)])
            capa.add(Line(np.append(origen, 0.0), np.append(destino, 0.0),
                          stroke_width=grosor, color=color,
                          stroke_opacity=opacidad))
            siguientes.append((destino, rumbo2))
            if rng.random() < 0.42 and gen < radios - 1:
                siguientes.append((destino,
                                   rumbo2 + rng.choice([-1, 1])
                                   * rng.uniform(0.5, 0.9)))
        anillos.append(capa)
        frentes = siguientes
        if len(frentes) > 220:              # la red no explota
            frentes = frentes[:220]
    params = {"radios": radios, "brotes": brotes, "semilla": semilla,
              "escala": float(escala)}
    return RedMicelio(anillos, params)


# =====================================================================
# Turing: Gray-Scott, la quimica que pinta
# =====================================================================
def _validar_campo(res, pasos):
    res_x, res_y = int(res[0]), int(res[1])
    if max(res_x, res_y) > RES_CAMPO_MAX:
        raise ValueError(f"campo_turing: res {res} > {RES_CAMPO_MAX}")
    pasos = int(pasos)
    if pasos > PASOS_TURING_MAX:
        raise ValueError(f"campo_turing: {pasos} pasos > {PASOS_TURING_MAX}")
    return res_x, res_y, pasos


def _laplaciano(Z):
    return (np.roll(Z, 1, 0) + np.roll(Z, -1, 0)
            + np.roll(Z, 1, 1) + np.roll(Z, -1, 1) - 4.0 * Z)


def _turing_inicial(res_x, res_y, semilla):
    rng = np.random.default_rng(int(semilla))
    U = np.ones((res_y, res_x))
    V = np.zeros((res_y, res_x))
    # Parches sembrados por todo el dominio: el patron llena el lienzo en
    # vez de crecer solo desde el centro.
    for _ in range(24):
        cy = rng.integers(4, res_y - 4)
        cx = rng.integers(4, res_x - 4)
        r = int(rng.integers(2, 5))
        U[cy - r:cy + r, cx - r:cx + r] = 0.50
        V[cy - r:cy + r, cx - r:cx + r] = 0.25
    U += rng.normal(0, 0.02, U.shape)
    V += rng.normal(0, 0.02, V.shape)
    return np.clip(U, 0, 1.2), np.clip(V, 0, 1.0)


def _turing_avanza(U, V, f, k, pasos):
    Du, Dv, dt = 0.2097, 0.1050, 1.0     # Pearson 1993 en unidades de malla
    for _ in range(int(pasos)):
        UVV = U * V * V
        U = U + dt * (Du * _laplaciano(U) - UVV + f * (1.0 - U))
        V = V + dt * (Dv * _laplaciano(V) + UVV - (f + k) * V)
    return U, V


def campo_turing(f, k, pasos=7000, res=(288, 162), semilla=7):
    """Campo V de Gray-Scott tras `pasos` (frontera periodica), en [0, 1].

    Presets del curso: `TURING_MANCHAS` (leopardo) y `TURING_RAYAS` (cebra,
    gato atigrado). El campo es (res_y, res_x): filas = alto.
    """
    res_x, res_y, pasos = _validar_campo(res, pasos)
    U, V = _turing_inicial(res_x, res_y, semilla)
    _, V = _turing_avanza(U, V, float(f), float(k), pasos)
    return np.clip(V / 0.40, 0.0, 1.0)


def secuencia_turing(f, k, cuadros=7, pasos=7000, res=(288, 162), semilla=7):
    """`cuadros` campos a tiempos crecientes del MISMO proceso (mismo estado
    inicial): relevarlos en escena es ver a la quimica calcular. El
    espaciado es cuadratico: al principio pasa todo, al final se asienta."""
    res_x, res_y, pasos = _validar_campo(res, pasos)
    cuadros = _validar("secuencia_turing.cuadros", cuadros,
                       CUADROS_TURING_MAX)
    U, V = _turing_inicial(res_x, res_y, semilla)
    cortes = [int(pasos * ((i + 1) / cuadros) ** 2) for i in range(cuadros)]
    salida, hechos = [], 0
    for corte in cortes:
        U, V = _turing_avanza(U, V, float(f), float(k), corte - hechos)
        hechos = corte
        salida.append(np.clip(V / 0.40, 0.0, 1.0))
    return salida


def imagen_turing(campo, color_fondo="#151a24", color_tinta=COLOR_QUIMICA,
                  alto_escena=5.0, silueta=None, umbral=(0.25, 0.75),
                  fuera_transparente=True):
    """El campo de Turing como imagen; con `silueta` (un VMobject de esta
    libreria con `.puntos_poligono`) el patron solo pinta DENTRO.

    `umbral` es la rampa (lo, hi) que pasa de fondo a tinta: aprieta el
    contraste del patron. Con silueta, la imagen queda del tamaño y en la
    posicion ACTUALES de la silueta (llamar DESPUES de colocarla).
    """
    campo = np.asarray(campo, dtype=np.float64)
    lo, hi = float(umbral[0]), float(umbral[1])
    t = np.clip((campo - lo) / max(hi - lo, _EPS), 0.0, 1.0)
    t = t * t * (3.0 - 2.0 * t)                      # smoothstep
    fondo, tinta = _hex_a_rgb(color_fondo), _hex_a_rgb(color_tinta)
    rgb = fondo + (tinta - fondo) * t[..., None]

    if silueta is None:
        rgba = np.empty(campo.shape + (4,), dtype=np.uint8)
        rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
        rgba[..., 3] = 255
        return _imagen(rgba, alto_escena)

    poli = np.asarray(silueta.puntos_poligono, dtype=np.float64)
    x0, y0 = poli.min(axis=0)
    x1, y1 = poli.max(axis=0)
    norm = (poli - [x0, y0]) / [max(x1 - x0, _EPS), max(y1 - y0, _EPS)]
    res_y, res_x = campo.shape
    # El campo se RECORTA (centrado) a la proporcion del poligono antes de
    # enmascarar: estirarlo despues a la caja de la silueta seria isotropo
    # y las rayas no se deformarian. Sin este recorte, un gato vertical
    # estira un campo apaisado ~3x y el patron se alarga.
    aspecto = (x1 - x0) / max(y1 - y0, _EPS)
    if res_x / res_y > aspecto:
        ancho_px = max(int(round(res_y * aspecto)), 8)
        margen = (res_x - ancho_px) // 2
        campo_c = campo[:, margen:margen + ancho_px]
        rgb_c = rgb[:, margen:margen + ancho_px]
    else:
        alto_px = max(int(round(res_x / aspecto)), 8)
        margen = (res_y - alto_px) // 2
        campo_c = campo[margen:margen + alto_px]
        rgb_c = rgb[margen:margen + alto_px]
    ry, rx = campo_c.shape
    mascara = _mascara_poligono(norm, rx, ry)[::-1]
    rgba = np.zeros(campo_c.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = np.clip(rgb_c, 0, 255).astype(np.uint8)
    rgba[..., 3] = np.where(mascara, 255, 0).astype(np.uint8)
    if not fuera_transparente:
        rgba[..., 3] = 255
    img = _imagen(rgba, None)
    img.width = silueta.width
    img.height = silueta.height
    img.move_to(silueta.get_center())
    return img


# =====================================================================
# pi baja por el rio: la curva sine-generated
# =====================================================================
def _puntos_meandro(omega_deg, muestras, periodos=2.5):
    """Curva de Langbein-Leopold: theta(s) = omega*sin(2*pi*s/L). Devuelve
    (n, 2) con la cuerda horizontal, SIN escalar."""
    om = math.radians(float(omega_deg))
    s = np.linspace(0.0, periodos, muestras)
    th = om * np.sin(2.0 * math.pi * s)
    ds = s[1] - s[0]
    x = np.concatenate([[0.0], np.cumsum(np.cos(th))[:-1]]) * ds
    y = np.concatenate([[0.0], np.cumsum(np.sin(th))[:-1]]) * ds
    pts = np.column_stack([x, y])
    cuerda = pts[-1] - pts[0]
    giro = -math.atan2(cuerda[1], cuerda[0])
    rot = np.array([[math.cos(giro), -math.sin(giro)],
                    [math.sin(giro), math.cos(giro)]])
    return pts @ rot.T


class RioMeandro(VMobject):
    """El rio que serpentea; mide su propia sinuosidad sobre la curva."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._params = {}

    def extremos(self):
        """(nacimiento, desembocadura) sobre la geometria ACTUAL."""
        return (np.array(self.points[0], dtype=np.float64),
                np.array(self.points[-1], dtype=np.float64))

    def sinuosidad(self):
        """Longitud del camino / distancia recta, MEDIDA sobre la curva
        dibujada: el numero que el clip rotula."""
        pts = np.asarray(self.get_anchors(), dtype=np.float64)
        camino = float(np.sum(np.linalg.norm(np.diff(pts, axis=0), axis=1)))
        a, b = self.extremos()
        recta = float(np.linalg.norm(b - a))
        return camino / max(recta, _EPS)

    def con_omega(self, omega_deg):
        """El mismo rio con otro angulo maximo, misma cuerda (Transform)."""
        params = dict(self._params, omega_deg=float(omega_deg))
        otro = rio_meandro(**params)
        otro.shift(self.get_center() - otro.get_center())
        return otro

    def arco_ajustado(self, indice=0, color=COLOR_EJE):
        """Circunferencia punteada ajustada (Kasa) a la curva del meandro
        `indice` (media onda): "cada curva es casi un arco". Se calcula
        sobre la geometria actual."""
        pts = np.asarray(self.get_anchors(), dtype=np.float64)[:, :2]
        n = len(pts)
        tramos = int(round(2 * self._params.get("periodos", 2.5)))
        i0 = int(n * indice / tramos)
        i1 = int(n * (indice + 1) / tramos)
        P = pts[i0:i1]
        A = np.column_stack([2 * P[:, 0], 2 * P[:, 1], np.ones(len(P))])
        b = (P ** 2).sum(axis=1)
        cx, cy, c = np.linalg.lstsq(A, b, rcond=None)[0]
        r = math.sqrt(max(c + cx * cx + cy * cy, _EPS))
        circ = Circle(radius=r, color=color, stroke_width=1.8)
        circ.move_to(np.array([cx, cy, 0.0]))
        return DashedVMobject(circ, num_dashes=48).set_stroke(opacity=0.7)


def rio_meandro(omega_deg=90.0, ancho=9.0, muestras=420, periodos=2.5,
                color=COLOR_REGLA, grosor=4.0):
    """Rio sine-generated con la cuerda horizontal de longitud `ancho`.

    `OMEGA_PI_DEG` (~110) da sinuosidad ~ pi; el numero que se rotula sale
    siempre de `.sinuosidad()`, medido, no de la teoria.
    """
    muestras = _validar("rio_meandro.muestras", muestras, MUESTRAS_MAX)
    pts = _puntos_meandro(omega_deg, muestras, periodos)
    cuerda = np.linalg.norm(pts[-1] - pts[0])
    pts = pts * (float(ancho) / max(cuerda, _EPS))
    pts = pts - (pts[0] + pts[-1]) / 2.0
    rio = RioMeandro(color=color, stroke_width=grosor)
    rio.set_points_smoothly(np.column_stack([pts, np.zeros(len(pts))]))
    rio._params = {"omega_deg": float(omega_deg), "ancho": float(ancho),
                   "muestras": muestras, "periodos": float(periodos),
                   "color": color, "grosor": grosor}
    return rio


def onda_circular(radios=(0.5, 1.0, 1.5), centro=ORIGIN,
                  color=COLOR_CONSTANTE):
    """Anillos concentricos punteados: la gota en el agua. La opacidad cae
    hacia afuera (la onda se apaga)."""
    grupo = VGroup()
    for i, r in enumerate(radios):
        anillo = DashedVMobject(Circle(radius=float(r), color=color,
                                       stroke_width=2.0), num_dashes=36)
        anillo.set_stroke(opacity=0.85 * (0.72 ** i))
        grupo.add(anillo)
    grupo.move_to(centro)
    return grupo


# =====================================================================
# e: el ritmo del crecimiento continuo
# =====================================================================
class CurvaCrecimiento(VGroup):
    """Ejes + e^(tasa*t); mapea (t, y) a escena para colgar escaleras."""

    def __init__(self, ejes, curva, params, **kwargs):
        super().__init__(ejes, curva, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self._params = params

    def valor(self, t):
        """e^(tasa*t): el numero, de la misma fuente que el dibujo."""
        return math.exp(self._params["tasa"] * float(t))

    def a_escena(self, t, y):
        """Punto de escena para (t, y) en las coordenadas de la caja,
        leido de la geometria ACTUAL de los ejes."""
        origen = self.ejes[0].get_start()
        p = self._params
        dx = (self.ejes[0].get_end() - origen) * (float(t) / p["t_max"])
        dy = (self.ejes[1].get_end() - self.ejes[1].get_start()) \
            * (float(y) / p["y_max"])
        return origen + dx + dy

    def punto_en(self, t):
        """Punto ACTUAL de la curva en el tiempo t."""
        return self.a_escena(t, self.valor(t))


def curva_crecimiento(tasa=1.0, t_max=1.0, ancho=5.6, alto=3.0,
                      color=COLOR_REGLA, color_ejes=COLOR_EJE,
                      muestras=140, y_max=None):
    """La exponencial e^(tasa*t) sobre ejes minimos, esquina en ORIGIN.

    Con `tasa` negativa decae (y_max lo fija el 1.0 inicial). `y_max`
    manual permite compartir caja entre curva y escaleras.
    """
    muestras = _validar("curva_crecimiento.muestras", muestras, MUESTRAS_MAX)
    tasa, t_max = float(tasa), float(t_max)
    tope = math.exp(max(tasa * t_max, 0.0)) * 1.10 if y_max is None \
        else float(y_max)
    eje_x = Line(ORIGIN, RIGHT * ancho, stroke_width=2.0, color=color_ejes)
    eje_y = Line(ORIGIN, UP * alto, stroke_width=2.0, color=color_ejes)
    ejes = VGroup(eje_x, eje_y)

    t = np.linspace(0.0, t_max, muestras)
    y = np.exp(tasa * t)
    pts = np.column_stack([t / t_max * ancho, y / tope * alto,
                           np.zeros(muestras)])
    curva = _curva(pts, color, 3.2)
    params = {"tasa": tasa, "t_max": t_max, "ancho": float(ancho),
              "alto": float(alto), "y_max": tope}
    grupo = CurvaCrecimiento(ejes, curva, params)
    grupo.shift(LEFT * ancho / 2 + DOWN * alto / 2)   # centrada en ORIGIN
    return grupo


class EscaleraCompuesta(VGroup):
    """Capitalizar en n saltos: la poligonal discreta bajo la curva."""

    def __init__(self, traza, params, **kwargs):
        super().__init__(traza, **kwargs)
        self.traza = traza
        self._params = params
        self.n = params["n"]

    def valor_final(self):
        """(1 + 1/n)^n: el numero que sube hacia e."""
        n = self.n
        return (1.0 + 1.0 / n) ** n


def escalera_compuesta(n, curva, color=COLOR_QUIMICA, grosor=3.0):
    """La poligonal de capitalizar en `n` saltos sobre la caja de `curva`
    (un CurvaCrecimiento con tasa=1, t_max=1): sube a (1+1/n)^i en saltos.
    Con n grande se pega a la curva continua: ese es el clip."""
    n = _validar("escalera_compuesta.n", n, 400)
    pts = [curva.a_escena(0.0, 1.0)]
    for i in range(1, n + 1):
        v_prev = (1.0 + 1.0 / n) ** (i - 1)
        v = (1.0 + 1.0 / n) ** i
        t = i / n
        pts.append(curva.a_escena(t, v_prev))    # tramo plano
        pts.append(curva.a_escena(t, v))         # el salto
    traza = VMobject(color=color, stroke_width=grosor)
    traza.set_points_as_corners(np.array(pts))
    return EscaleraCompuesta(traza, {"n": n})


# =====================================================================
# Hexagonos: el minimo material
# =====================================================================
def perimetro_por_area(n_lados, area=1.0):
    """Perimetro del poligono regular de `n_lados` con ese area:
    P = 2*sqrt(n*A*tan(pi/n)). 3 -> 4.559, 4 -> 4.000, 6 -> 3.722."""
    n = int(n_lados)
    return 2.0 * math.sqrt(n * float(area) * math.tan(math.pi / n))


def tesela_unidad(n_lados, area=1.0, color=COLOR_EJE, relleno=None):
    """Poligono regular de AREA exacta `area` (en unidades de escena al
    cuadrado), centrado en ORIGIN, apoyado sobre un lado horizontal."""
    n = int(n_lados)
    R = math.sqrt(2.0 * float(area) / (n * math.sin(2.0 * math.pi / n)))
    a0 = -math.pi / 2.0 + math.pi / n      # un lado horizontal abajo
    pts = [(R * math.cos(a0 + 2 * math.pi * i / n),
            R * math.sin(a0 + 2 * math.pi * i / n)) for i in range(n)]
    tesela = Polygon(*[np.array([x, y, 0.0]) for x, y in pts],
                     stroke_width=2.6, stroke_color=color,
                     fill_color=relleno if relleno else color,
                     fill_opacity=0.16 if relleno else 0.0)
    return tesela


class Panal(VGroup):
    """Reticula hexagonal; con jitter (semilla) se vuelve basalto."""

    def __init__(self, celdas, params, **kwargs):
        super().__init__(celdas, **kwargs)
        self.celdas = celdas
        self._params = params

    def celda(self, i):
        return self.celdas[int(i)]

    def aparecer(self, run_time=2.2):
        return LaggedStart(*[FadeIn(c, scale=0.6) for c in self.celdas],
                           lag_ratio=2.0 / max(len(self.celdas), 1),
                           run_time=run_time)


def panal(filas=4, columnas=6, lado=0.42, color=COLOR_REGLA,
          relleno=None, semilla=None):
    """Panal de `filas` x `columnas` hexagonos de lado `lado`, centrado.

    Con `semilla` las celdas se encogen y tuercen levemente al azar
    (determinista): columnas de basalto en vez de cera.
    """
    filas = _validar("panal.filas", filas, 12)
    columnas = _validar("panal.columnas", columnas, 16)
    lado = float(lado)
    rng = np.random.default_rng(int(semilla)) if semilla is not None else None
    celdas = VGroup()
    for col in range(columnas):
        for fila in range(filas):
            cx = col * 1.5 * lado
            cy = fila * math.sqrt(3.0) * lado \
                + (math.sqrt(3.0) / 2.0 * lado if col % 2 else 0.0)
            pts = [(cx + lado * math.cos(math.pi / 3.0 * i),
                    cy + lado * math.sin(math.pi / 3.0 * i))
                   for i in range(6)]
            celda = Polygon(*[np.array([x, y, 0.0]) for x, y in pts],
                            stroke_width=2.0, stroke_color=color,
                            fill_color=relleno if relleno else color,
                            fill_opacity=0.10 if relleno else 0.0)
            if rng is not None:
                celda.scale(rng.uniform(0.90, 0.97))
                celda.rotate(rng.normal(0.0, 0.05))
            celdas.add(celda)
    grupo = Panal(celdas, {"filas": filas, "columnas": columnas,
                           "lado": lado})
    grupo.move_to(ORIGIN)
    return grupo
