"""Relatividad y el GPS: dilatacion del tiempo, orbitas y trilateracion.

Pensado para el curso "Relatividad y el GPS". Todo el calculo es numpy
puro y determinista: mismo script -> mismo render, condicion necesaria
para trabajar con `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: la LUZ
(pulsos, fotones) es ambar, el SATELITE y sus relojes (lo medido) cian,
la TIERRA y el receptor verde, el ERROR que se acumula rojo, la GRAVEDAD
(el pozo, la relatividad general) violeta. Mobiliario en `COLOR_EJE`.

Piezas:
    reloj_luz          espejos + zigzag del foton; la hipotenusa SE MIDE
    curva_gamma        gamma contra beta, con localizador `.en(beta)`
    orbita_gps         Tierra + orbita A ESCALA + satelite reposicionable
    trilateracion      3 circulos por el receptor; `.con_sesgo` los infla
                       y `.triangulo_error()` mide donde dejan de cortarse
    curvas_muones      supervivencia clasica vs relativista por altura
    pozo_potencial     el pozo -1/r con la Tierra al fondo
    curva_deriva       deriva neta us/dia contra altura (log); cruza cero
    carita_reloj       esfera + manecilla, reproducible por fase
    mapa_error         pin + circulo de error que crece con las horas
    fila_pulsos        tren de pulsos (fabrica vs orbita) con desfase

Los NUMEROS que se rotulan salen de funciones (`derivas_gps()`,
`altura_empate()`, `gamma()`, `frac_muones()`, `frecuencia_fabrica()`,
`error_metros()`, `metros_por_us()`), nunca a mano: en un curso sobre
relojes que no mienten, el rotulo sale de la misma fuente que el dibujo.
`altura_empate()` y `.longitud_camino()` se MIDEN (biseccion, geometria
en pantalla), no se citan.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`MUESTRAS_MAX`, `TICS_MAX`, `PULSOS_MAX` levantan ValueError.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from relatividad import reloj_luz, derivas_gps

    reloj = reloj_luz(beta=0.5)
    self.play(Create(reloj.espejos))
"""

import math

import numpy as np

from manim import (Circle, DashedVMobject, Dot, Line, Polygon,
                   RoundedRectangle, Text, VGroup, VMobject,
                   DOWN, LEFT, ORIGIN, RIGHT, TAU, UP)

from code_brand import FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
MUESTRAS_MAX = 600     # muestras de una curva parametrica
TICS_MAX = 12          # rebotes del reloj de luz
PULSOS_MAX = 60        # pulsos de un tren
CALLES_MAX = 12        # calles del mapa

# Paleta propia de la libreria (coincide con la del curso).
COLOR_LUZ = "#f59e0b"       # la luz: pulsos, el foton del reloj
COLOR_SATELITE = "#22d3ee"  # el satelite, sus relojes, lo medido
COLOR_TIERRA = "#34d399"    # la Tierra, el receptor, lo de abajo
COLOR_ERROR = "#f43f5e"     # el error que se acumula
COLOR_GRAVEDAD = "#a78bfa"  # la gravedad, el pozo, la relatividad general
COLOR_EJE = "#31414f"       # mobiliario: ejes, cajas, espejos

C_LUZ, C_SATELITE, C_TIERRA = COLOR_LUZ, COLOR_SATELITE, COLOR_TIERRA
C_ERROR, C_GRAVEDAD, C_EJE = COLOR_ERROR, COLOR_GRAVEDAD, COLOR_EJE

# --- Los numeros del mundo -------------------------------------------
# GM y radio medio terrestre (WGS-84 / IERS), semieje de la constelacion
# GPS, frecuencia base de sus relojes, y el muon de rayos cosmicos tipico.
GM_TIERRA = 3.986004418e14        # m^3/s^2
RADIO_TIERRA = 6.371e6            # m (radio medio)
C = 299792458.0                   # m/s, exacta por definicion
RADIO_GPS = 26_560e3              # m (semieje real de la constelacion)
ALTURA_ISS = 420e3                # m
FREQ_GPS = 10.23e6                # Hz (reloj base de los satelites)
TAU_MUON = 2.2e-6                 # s (vida media en reposo)
BETA_MUON = 0.995                 # v/c tipica -> gamma ~ 10
ALTURA_MUON = 15e3                # m (donde nacen)
SEGUNDOS_DIA = 86400.0

_EPS = 1e-12


# --- nucleo: los numeros ----------------------------------------------
def gamma(beta):
    """Factor de Lorentz 1/sqrt(1 - beta^2)."""
    beta = float(beta)
    if not -1.0 < beta < 1.0:
        raise ValueError(f"gamma: |beta| = {abs(beta)} >= 1")
    return 1.0 / math.sqrt(1.0 - beta * beta)


def velocidad_orbital(radio=RADIO_GPS):
    """v = sqrt(GM/r) de una orbita circular, en m/s."""
    return math.sqrt(GM_TIERRA / float(radio))


def periodo_orbital(radio=RADIO_GPS):
    """T = 2 pi sqrt(r^3/GM), en segundos (GPS: ~11 h 58 m)."""
    r = float(radio)
    return TAU * math.sqrt(r ** 3 / GM_TIERRA)


def tasa_sr(radio=RADIO_GPS):
    """Dilatacion especial -v^2/2c^2 (adimensional; negativa: atrasa)."""
    v = velocidad_orbital(radio)
    return -v * v / (2.0 * C * C)


def tasa_gr(radio=RADIO_GPS):
    """Dilatacion gravitatoria (GM/c^2)(1/R - 1/r): positiva en orbita.

    Modelo simple (potencial newtoniano, sin geoide ni rotacion): eso es
    lo que se rotula, no el valor citado con geoide (+45.9).
    """
    r = float(radio)
    return GM_TIERRA / (C * C) * (1.0 / RADIO_TIERRA - 1.0 / r)


def deriva_us_dia(radio=RADIO_GPS):
    """Deriva NETA del reloj orbital en microsegundos por dia."""
    return (tasa_sr(radio) + tasa_gr(radio)) * SEGUNDOS_DIA * 1e6


def derivas_gps(radio=RADIO_GPS):
    """(sr, gr, neta) en us/dia: (-7.21, +45.72, +38.50) para el GPS."""
    sr = tasa_sr(radio) * SEGUNDOS_DIA * 1e6
    gr = tasa_gr(radio) * SEGUNDOS_DIA * 1e6
    return (sr, gr, sr + gr)


def altura_empate():
    """Altura (m) donde SR y GR se cancelan, MEDIDA por biseccion.

    Sale ~3.186e6 m (r = 1.5 radios terrestres, el resultado analitico):
    por debajo (ISS) el reloj orbital atrasa, por encima (GPS) adelanta.
    """
    lo, hi = RADIO_TIERRA + 1e3, RADIO_GPS
    for _ in range(200):
        medio = 0.5 * (lo + hi)
        if deriva_us_dia(medio) < 0.0:
            lo = medio
        else:
            hi = medio
    return 0.5 * (lo + hi) - RADIO_TIERRA


def metros_por_us(microsegundos=1.0):
    """c por microsegundo: ~300 m. El precio de 1 us de reloj."""
    return C * float(microsegundos) * 1e-6


def error_metros(horas, radio=RADIO_GPS):
    """Error de pseudodistancia c*deriva acumulado en `horas`, en metros.

    ~481 m/hora, ~11.5 km/dia si nadie corrigiera la deriva neta.
    """
    tasa = tasa_sr(radio) + tasa_gr(radio)
    return abs(C * tasa * float(horas) * 3600.0)


def frecuencia_fabrica(radio=RADIO_GPS):
    """Frecuencia (Hz) a la que se desafina el reloj antes de lanzarlo:
    10.23 MHz * (1 - deriva) = 10.22999999544 MHz, para latir exacto
    EN orbita."""
    return FREQ_GPS * (1.0 - (tasa_sr(radio) + tasa_gr(radio)))


def supervivencia_muones(altura, factor_gamma=1.0):
    """Fraccion de muones viva al descender de ALTURA_MUON a `altura` (m).

    exp(-t/(gamma tau)) con t el tiempo de vuelo a BETA_MUON*c. Acepta
    arrays de altura (numpy).
    """
    h = np.asarray(altura, dtype=np.float64)
    t_vuelo = (ALTURA_MUON - h) / (BETA_MUON * C)
    return np.exp(-t_vuelo / (float(factor_gamma) * TAU_MUON))


def frac_muones():
    """(clasica, relativista) que llegan al suelo: (~1e-10, ~0.102)."""
    clasica = float(supervivencia_muones(0.0, 1.0))
    relativista = float(supervivencia_muones(0.0, gamma(BETA_MUON)))
    return (clasica, relativista)


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


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


# =====================================================================
# El reloj de luz
# =====================================================================
class RelojLuz(VGroup):
    """Dos espejos y el camino del foton; la hipotenusa se mide aqui."""

    def __init__(self, ancla, espejos, camino, foton, params, **kwargs):
        super().__init__(ancla, espejos, camino, foton, **kwargs)
        self._ancla = ancla            # arranque del foton (espejo de abajo)
        self.espejos = espejos         # VGroup(abajo, arriba)
        self.camino = camino           # VGroup: un Line por tramo
        self.foton = foton
        self._params = params
        self.beta = params["beta"]

    def _alto_actual(self):
        abajo, arriba = self.espejos
        return abs(arriba.get_center()[1] - abajo.get_center()[1])

    def longitud_camino(self):
        """Tramo medio MEDIDO / separacion de espejos = gamma(beta).

        Se mide sobre la geometria actual: escala la pieza y sigue dando
        lo mismo. Es el numero que el clip 3 rotula como gamma.
        """
        largos = [np.linalg.norm(t.get_end() - t.get_start())
                  for t in self.camino]
        return float(np.mean(largos)) / max(self._alto_actual(), _EPS)

    def punto_camino(self, alpha):
        """Punto de escena a fraccion `alpha` del camino total (para
        UpdateFromAlphaFunc del foton), geometria ACTUAL."""
        largos = np.array([np.linalg.norm(t.get_end() - t.get_start())
                           for t in self.camino])
        total = float(largos.sum())
        objetivo = float(np.clip(alpha, 0.0, 1.0)) * total
        acum = 0.0
        for tramo, largo in zip(self.camino, largos):
            if acum + largo >= objetivo - _EPS:
                f = (objetivo - acum) / max(largo, _EPS)
                return tramo.get_start() + f * (tramo.get_end()
                                                - tramo.get_start())
            acum += largo
        return self.camino[-1].get_end()

    def con_beta(self, beta):
        """El mismo reloj con otra beta, anclado por el arranque del
        foton (para Transform)."""
        params = dict(self._params, beta=float(beta))
        otro = reloj_luz(**params)
        otro.shift(self._ancla.get_center() - otro._ancla.get_center())
        return otro


def reloj_luz(beta=0.0, alto=2.2, tics=4, color=COLOR_LUZ,
              color_espejo=COLOR_EJE, margen=0.35):
    """Reloj de luz: espejos arriba/abajo y el zigzag del foton.

    En reposo (beta=0) el foton rebota vertical; en movimiento cada
    tramo es la hipotenusa alto*gamma con avance horizontal
    alto*beta*gamma (la cinematica real, no un dibujo). `.camino` trae
    un Line por tramo: LaggedStart(*[Create(t) for t in camino]) lo
    dibuja rebote a rebote. El foton arranca en el espejo de abajo.
    """
    tics = _validar("reloj_luz.tics", tics, TICS_MAX)
    beta, alto = float(beta), float(alto)
    g = gamma(beta)
    dx = alto * beta * g                 # avance del espejo por tramo

    puntos = [np.array([0.0, 0.0, 0.0])]
    for k in range(tics):
        x = (k + 1) * dx
        y = alto if k % 2 == 0 else 0.0
        puntos.append(np.array([x, y, 0.0]))

    ancho = max(tics * dx, 0.0) + 2.0 * margen
    x_med = 0.5 * tics * dx
    espejo_abajo = Line([x_med - ancho / 2, 0, 0], [x_med + ancho / 2, 0, 0],
                        stroke_width=4.0, color=color_espejo)
    espejo_arriba = espejo_abajo.copy().shift(UP * alto)
    espejos = VGroup(espejo_abajo, espejo_arriba)

    camino = VGroup(*[
        Line(puntos[k], puntos[k + 1], stroke_width=2.6, color=color)
        for k in range(tics)])
    camino.set_stroke(opacity=0.9)

    foton = Dot(puntos[0], radius=0.07, color=color)

    params = {"beta": beta, "alto": alto, "tics": tics, "color": color,
              "color_espejo": color_espejo, "margen": margen}
    return RelojLuz(_ancla(puntos[0]), espejos, camino, foton, params)


# =====================================================================
# La curva gamma
# =====================================================================
class CurvaGamma(VGroup):
    """Ejes + gamma(beta); localizador `.en(beta)` sobre geometria actual."""

    def __init__(self, ancla, ejes, curva, params, **kwargs):
        super().__init__(ancla, ejes, curva, **kwargs)
        self._ancla = ancla            # origen de los ejes
        self.ejes = ejes
        self.curva = curva
        self._params = params

    def _escala_actual(self):
        return self.ejes[0].get_length() / max(self._params["ancho"], _EPS)

    def en(self, beta):
        """Punto de escena sobre la curva para `beta` (geometria ACTUAL)."""
        p = self._params
        esc = self._escala_actual()
        fx = float(beta) / p["beta_max"]
        fy = gamma(beta) / p["gamma_max"]
        return (self._ancla.get_center() + RIGHT * fx * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)


def curva_gamma(beta_max=0.95, ancho=4.8, alto=2.6,
                color=COLOR_SATELITE, color_ejes=COLOR_EJE, muestras=220):
    """gamma contra beta, con el origen de los ejes en ORIGIN - (a/2, a/2).

    El eje y va de 0 a gamma(beta_max) (~3.2): la zona plana del arranque
    —a velocidades humanas gamma es 1— es parte del argumento.
    """
    muestras = _validar("curva_gamma.muestras", muestras, MUESTRAS_MAX)
    beta_max, ancho, alto = float(beta_max), float(ancho), float(alto)
    g_max = gamma(beta_max)
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    ejes = VGroup(
        Line(origen, origen + RIGHT * ancho, stroke_width=2.0,
             color=color_ejes),
        Line(origen, origen + UP * alto, stroke_width=2.0,
             color=color_ejes))

    betas = np.linspace(0.0, beta_max, muestras)
    gs = 1.0 / np.sqrt(1.0 - betas ** 2)
    pts = [origen + RIGHT * (b / beta_max) * ancho + UP * (g / g_max) * alto
           for b, g in zip(betas, gs)]
    curva = _poligonal(pts, color, 3.0)

    params = {"beta_max": beta_max, "ancho": ancho, "alto": alto,
              "gamma_max": g_max}
    return CurvaGamma(_ancla(origen), ejes, curva, params)


# =====================================================================
# La orbita GPS (a escala)
# =====================================================================
class OrbitaGPS(VGroup):
    """Tierra + orbita a escala + satelite reposicionable por angulo."""

    def __init__(self, ancla, tierra, orbita, satelite, params, **kwargs):
        super().__init__(ancla, tierra, orbita, satelite, **kwargs)
        self._ancla = ancla            # centro de la Tierra
        self.tierra = tierra
        self.orbita = orbita
        self.satelite = satelite       # VGroup(panel, cuerpo)
        self._params = params

    def _radio_actual(self):
        return 0.5 * self.orbita.width

    def punto_orbita(self, alpha):
        """Punto de escena a fraccion `alpha` de vuelta (geometria ACTUAL,
        arranca a las 3 en punto, antihorario)."""
        ang = TAU * float(alpha)
        return (self._ancla.get_center()
                + self._radio_actual() * np.array([math.cos(ang),
                                                   math.sin(ang), 0.0]))

    def en(self, alpha):
        """Coloca el satelite (cuerpo Y panel tangente) en `alpha`; para
        UpdateFromAlphaFunc. Devuelve el propio grupo."""
        pos = self.punto_orbita(alpha)
        ang = TAU * float(alpha)
        tangente = np.array([-math.sin(ang), math.cos(ang), 0.0])
        panel, cuerpo = self.satelite
        cuerpo.move_to(pos)
        medio = 0.5 * self._params["panel"] * self._radio_actual() \
            / max(self._params["radio_escena"], _EPS)
        panel.put_start_and_end_on(pos - tangente * medio,
                                   pos + tangente * medio)
        return self


def orbita_gps(radio_escena=2.5, alpha0=0.125, color_orbita=COLOR_EJE,
               color_tierra=COLOR_TIERRA, color_sat=COLOR_SATELITE):
    """Tierra y orbita GPS A ESCALA (R_tierra/r_gps = 0.24: cabe y se ve).

    El satelite es cuerpo + panel tangente; `orb.en(alpha)` lo recoloca
    sobre la geometria actual (UpdateFromAlphaFunc(orb, lambda m, a:
    m.en(a)) le da la vuelta).
    """
    radio_escena = float(radio_escena)
    radio_tierra = radio_escena * RADIO_TIERRA / RADIO_GPS

    tierra = Circle(radius=radio_tierra, color=color_tierra,
                    stroke_width=2.5, fill_color=color_tierra,
                    fill_opacity=0.25)
    orbita = DashedVMobject(Circle(radius=radio_escena, stroke_width=1.8,
                                   color=color_orbita), num_dashes=80)
    orbita.set_stroke(opacity=0.85)

    cuerpo = Dot(ORIGIN, radius=0.085, color=color_sat)
    panel = Line(ORIGIN, RIGHT * 0.001, stroke_width=3.2, color=color_sat)
    satelite = VGroup(panel, cuerpo)

    params = {"radio_escena": radio_escena, "panel": 0.42}
    pieza = OrbitaGPS(_ancla(ORIGIN), tierra, orbita, satelite, params)
    return pieza.en(alpha0)


# =====================================================================
# Trilateracion (en el plano, y se dice)
# =====================================================================
class Trilateracion(VGroup):
    """Receptor + 3 satelites + 3 circulos de distancia."""

    def __init__(self, ancla, receptor, satelites, circulos, params,
                 **kwargs):
        super().__init__(ancla, receptor, satelites, circulos, **kwargs)
        self._ancla = ancla            # el receptor (la verdad)
        self.receptor = receptor
        self.satelites = satelites
        self.circulos = circulos
        self._params = params
        self.sesgo = params["sesgo"]

    def _escala_actual(self):
        d0 = np.linalg.norm(self.satelites[0].get_center()
                            - self._ancla.get_center())
        return d0 / max(self._params["dists"][0], _EPS)

    def con_sesgo(self, sesgo):
        """La misma escena con TODOS los radios inflados `sesgo` (unidades
        locales): el error de reloj comun. Anclada por el receptor."""
        params = dict(self._params, sesgo=float(sesgo))
        otro = trilateracion(**{k: params[k] for k in
                                ("angulos", "dists", "sesgo", "escala",
                                 "color_circulo", "color_sat",
                                 "color_receptor")})
        otro.shift(self._ancla.get_center() - otro._ancla.get_center())
        return otro

    def triangulo_error(self, color=COLOR_ERROR):
        """Poligono de los cortes por pares mas cercanos al receptor,
        MEDIDO sobre la geometria actual. Con sesgo 0 degenera al punto."""
        esc = self._escala_actual()
        centro = self._ancla.get_center()
        centros = [s.get_center() for s in self.satelites]
        radios = [(d + self.sesgo) * esc for d in self._params["dists"]]
        vertices = []
        n = len(centros)
        for i in range(n):
            j = (i + 1) % n
            corte = _corte_circulos(centros[i], radios[i],
                                    centros[j], radios[j], centro)
            vertices.append(corte)
        tri = Polygon(*vertices, stroke_width=2.6, color=color)
        tri.set_fill(color, opacity=0.18)
        tri.lado_medio = float(np.mean([
            np.linalg.norm(vertices[i] - vertices[(i + 1) % n])
            for i in range(n)]))
        return tri


def _corte_circulos(c1, r1, c2, r2, cerca_de):
    """Interseccion de dos circulos mas cercana a `cerca_de` (2D en z=0)."""
    c1, c2 = np.asarray(c1, float), np.asarray(c2, float)
    d = np.linalg.norm(c2[:2] - c1[:2])
    d = max(d, _EPS)
    a = (r1 * r1 - r2 * r2 + d * d) / (2.0 * d)
    h2 = r1 * r1 - a * a
    h = math.sqrt(max(h2, 0.0))
    ux, uy = (c2[:2] - c1[:2]) / d
    base = c1[:2] + a * np.array([ux, uy])
    p1 = np.array([base[0] - h * uy, base[1] + h * ux, 0.0])
    p2 = np.array([base[0] + h * uy, base[1] - h * ux, 0.0])
    if (np.linalg.norm(p1 - cerca_de) <= np.linalg.norm(p2 - cerca_de)):
        return p1
    return p2


def trilateracion(angulos=(104.0, 214.0, 338.0), dists=(2.05, 1.65, 2.35),
                  sesgo=0.0, escala=1.0, color_circulo=COLOR_TIERRA,
                  color_sat=COLOR_SATELITE, color_receptor=COLOR_TIERRA):
    """Tres satelites y sus circulos de distancia al receptor (ORIGIN).

    Con sesgo=0 los tres circulos pasan por el receptor; con sesgo>0
    todos los radios crecen lo mismo (el reloj barato del telefono) y
    `.triangulo_error()` mide donde dejan de cortarse. EN EL PLANO: la
    honestidad 3D (esferas, 4o satelite) va en el pie del clip.
    """
    escala, sesgo = float(escala), float(sesgo)
    receptor = Dot(ORIGIN, radius=0.075, color=color_receptor)

    satelites, circulos = VGroup(), VGroup()
    for ang_deg, d in zip(angulos, dists):
        ang = math.radians(float(ang_deg))
        pos = escala * float(d) * np.array([math.cos(ang), math.sin(ang),
                                            0.0])
        sat = Dot(pos, radius=0.07, color=color_sat)
        circ = Circle(radius=escala * (float(d) + sesgo), stroke_width=2.2,
                      color=color_circulo)
        circ.move_to(pos)
        circ.set_stroke(opacity=0.85)
        satelites.add(sat)
        circulos.add(circ)

    params = {"angulos": tuple(float(a) for a in angulos),
              "dists": tuple(float(d) for d in dists), "sesgo": sesgo,
              "escala": escala, "color_circulo": color_circulo,
              "color_sat": color_sat, "color_receptor": color_receptor}
    return Trilateracion(_ancla(ORIGIN), receptor, satelites, circulos,
                         params)


# =====================================================================
# Los muones
# =====================================================================
class CurvasMuones(VGroup):
    """Supervivencia contra altura: la clasica muere, la relativista llega."""

    def __init__(self, ancla, ejes, suelo, clasica, relativista, params,
                 **kwargs):
        super().__init__(ancla, ejes, suelo, clasica, relativista, **kwargs)
        self._ancla = ancla            # esquina inferior izquierda
        self.ejes = ejes
        self.suelo = suelo
        self.clasica = clasica
        self.relativista = relativista
        self._params = params

    def _escala_actual(self):
        return self.suelo.get_length() / max(self._params["ancho"], _EPS)

    def en(self, frac, altura_m):
        """Punto de escena para (fraccion viva, altura en m), geometria
        ACTUAL."""
        p = self._params
        esc = self._escala_actual()
        fy = float(altura_m) / ALTURA_MUON
        return (self._ancla.get_center()
                + RIGHT * float(frac) * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)


def curvas_muones(ancho=4.6, alto=3.0, color_clasica=COLOR_ERROR,
                  color_relativista=COLOR_SATELITE, color_ejes=COLOR_EJE,
                  muestras=200):
    """x = fraccion viva (0..1), y = altura (15 km arriba, suelo abajo).

    Ambas curvas nacen arriba con fraccion 1; la clasica se pega al eje
    en ~2 km de caida (vida 660 m), la relativista (gamma 10) toca el
    suelo con ~10 %. Los numeros: `frac_muones()`.
    """
    muestras = _validar("curvas_muones.muestras", muestras, MUESTRAS_MAX)
    ancho, alto = float(ancho), float(alto)
    esquina = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    def punto(frac, h):
        return esquina + RIGHT * frac * ancho + UP * (h / ALTURA_MUON) * alto

    suelo = Line(esquina, esquina + RIGHT * ancho, stroke_width=3.0,
                 color=color_ejes)
    ejes = VGroup(Line(esquina, esquina + UP * alto, stroke_width=2.0,
                       color=color_ejes))

    alturas = np.linspace(ALTURA_MUON, 0.0, muestras)
    cla = supervivencia_muones(alturas, 1.0)
    rel = supervivencia_muones(alturas, gamma(BETA_MUON))
    clasica = _poligonal([punto(f, h) for f, h in zip(cla, alturas)],
                         color_clasica, 3.0)
    relativista = _poligonal([punto(f, h) for f, h in zip(rel, alturas)],
                             color_relativista, 3.0)

    params = {"ancho": ancho, "alto": alto}
    return CurvasMuones(_ancla(esquina), ejes, suelo, clasica, relativista,
                        params)


# =====================================================================
# El pozo de potencial
# =====================================================================
class PozoPotencial(VGroup):
    """Phi = -R/|x| con la Tierra al fondo; relojes a distintas alturas."""

    def __init__(self, ancla, curva, tierra, params, **kwargs):
        super().__init__(ancla, curva, tierra, **kwargs)
        self._ancla = ancla            # el fondo del pozo (x=R, phi=-1)
        self.curva = curva
        self.tierra = tierra
        self._params = params

    def _escala_actual(self):
        return self.tierra.width / max(2.0 * self._params["radio_tierra"],
                                       _EPS)

    def en(self, radios):
        """Punto de escena sobre la rama derecha del pozo para r en
        radios terrestres (>= 1), geometria ACTUAL."""
        p = self._params
        r = max(float(radios), 1.0)
        esc = self._escala_actual()
        x = p["medio_ancho"] * (r / p["r_max"])
        y = p["profundo"] * (1.0 - 1.0 / r)     # -R/r remontado a 0 abajo
        return (self._ancla.get_center() + RIGHT * x * esc + UP * y * esc)


def pozo_potencial(ancho=5.4, profundo=2.4, r_max=5.0,
                   color=COLOR_GRAVEDAD, color_tierra=COLOR_TIERRA,
                   muestras=180):
    """El pozo -R/r en las dos ramas, fondo en ORIGIN + DOWN*profundo/2.

    El eje x es r en radios terrestres (fondo r=1, borde r_max); el
    fondo del pozo esta 1 - 1/r por debajo del infinito. `.en(r)` da el
    punto para colgar relojes.
    """
    muestras = _validar("pozo_potencial.muestras", muestras, MUESTRAS_MAX)
    ancho, profundo, r_max = float(ancho), float(profundo), float(r_max)
    medio = ancho / 2.0
    fondo = np.array([0.0, -profundo / 2.0, 0.0])

    def punto(r, lado):
        x = lado * medio * (r / r_max)
        y = profundo * (1.0 - 1.0 / r)
        return fondo + RIGHT * x + UP * y

    rs = np.linspace(1.0, r_max, muestras)
    rama_der = _poligonal([punto(r, +1.0) for r in rs], color, 3.0)
    rama_izq = _poligonal([punto(r, -1.0) for r in rs], color, 3.0)
    curva = VGroup(rama_izq, rama_der)

    radio_tierra = medio / r_max
    tierra = Circle(radius=radio_tierra, color=color_tierra,
                    stroke_width=2.5, fill_color=color_tierra,
                    fill_opacity=0.25)
    tierra.move_to(fondo)

    params = {"medio_ancho": medio, "profundo": profundo, "r_max": r_max,
              "radio_tierra": radio_tierra}
    return PozoPotencial(_ancla(fondo), curva, tierra, params)


# =====================================================================
# La curva de deriva contra altura (la curva estrella)
# =====================================================================
class CurvaDeriva(VGroup):
    """Deriva neta us/dia contra altura (x log); cruza cero en el empate."""

    def __init__(self, ancla, ejes, cero, curva, params, **kwargs):
        super().__init__(ancla, ejes, cero, curva, **kwargs)
        self._ancla = ancla            # esquina inferior izquierda
        self.ejes = ejes               # eje y (izquierda)
        self.cero = cero               # la linea horizontal deriva = 0
        self.curva = curva
        self._params = params
        self.rango = (params["h_min"], params["h_max"])

    def _escala_actual(self):
        return self.cero.get_length() / max(self._params["ancho"], _EPS)

    def en(self, altura_m):
        """Punto de escena SOBRE la curva para una altura en m
        (geometria ACTUAL)."""
        p = self._params
        h = float(np.clip(altura_m, p["h_min"], p["h_max"]))
        esc = self._escala_actual()
        fx = ((math.log10(h) - math.log10(p["h_min"]))
              / (math.log10(p["h_max"]) - math.log10(p["h_min"])))
        d = deriva_us_dia(RADIO_TIERRA + h)
        fy = (d - p["d_min"]) / (p["d_max"] - p["d_min"])
        return (self._ancla.get_center() + RIGHT * fx * p["ancho"] * esc
                + UP * fy * p["alto"] * esc)

    def altura_cero(self):
        """La altura del empate SR = GR, medida por biseccion: ~3186 km."""
        return altura_empate()


def curva_deriva(h_min=200e3, h_max=40_000e3, ancho=5.6, alto=3.0,
                 color=COLOR_SATELITE, color_ejes=COLOR_EJE, muestras=240):
    """LA curva del curso: deriva neta del reloj orbital contra altura.

    x en log10 de la altura (200 km a 40 000 km), y lineal en us/dia.
    Por debajo de 3186 km (ISS) es negativa: gana la velocidad. Por
    encima (GPS) positiva: gana la gravedad. `.en(h)` localiza puntos
    sobre la geometria actual; `.cero` es la linea de deriva nula.
    """
    muestras = _validar("curva_deriva.muestras", muestras, MUESTRAS_MAX)
    h_min, h_max = float(h_min), float(h_max)
    ancho, alto = float(ancho), float(alto)

    hs = np.logspace(math.log10(h_min), math.log10(h_max), muestras)
    ds = np.array([deriva_us_dia(RADIO_TIERRA + h) for h in hs])
    margen = 0.06 * (ds.max() - ds.min())
    d_min, d_max = ds.min() - margen, ds.max() + margen

    esquina = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    def punto(h, d):
        fx = ((math.log10(h) - math.log10(h_min))
              / (math.log10(h_max) - math.log10(h_min)))
        fy = (d - d_min) / (d_max - d_min)
        return esquina + RIGHT * fx * ancho + UP * fy * alto

    y_cero = punto(h_min, 0.0)[1]
    cero = Line([esquina[0], y_cero, 0.0],
                [esquina[0] + ancho, y_cero, 0.0],
                stroke_width=2.0, color=color_ejes)
    ejes = VGroup(Line(esquina, esquina + UP * alto, stroke_width=2.0,
                       color=color_ejes))
    curva = _poligonal([punto(h, d) for h, d in zip(hs, ds)], color, 3.0)

    params = {"h_min": h_min, "h_max": h_max, "ancho": ancho, "alto": alto,
              "d_min": float(d_min), "d_max": float(d_max)}
    return CurvaDeriva(_ancla(esquina), ejes, cero, curva, params)


# =====================================================================
# La carita de reloj
# =====================================================================
class CaritaReloj(VGroup):
    """Esfera + 12 marcas + manecilla, reproducible por fase."""

    def __init__(self, ancla, esfera, marcas, manecilla, params, **kwargs):
        super().__init__(ancla, esfera, marcas, manecilla, **kwargs)
        self._ancla = ancla            # el centro
        self.esfera = esfera
        self.marcas = marcas
        self.manecilla = manecilla
        self._params = params

    def en(self, fase):
        """Pone la manecilla a `fase` vueltas (horario, 12 arriba) sobre
        la geometria ACTUAL; para UpdateFromAlphaFunc. Devuelve self."""
        centro = self._ancla.get_center()
        radio = 0.5 * self.esfera.width * self._params["frac_manecilla"]
        ang = 0.25 * TAU - TAU * float(fase)
        punta = centro + radio * np.array([math.cos(ang), math.sin(ang),
                                           0.0])
        self.manecilla.put_start_and_end_on(centro, punta)
        return self


def carita_reloj(radio=0.55, color=COLOR_SATELITE, color_esfera=COLOR_EJE):
    """Reloj analogico minimo; `reloj.en(fase)` mueve la manecilla
    (fase en vueltas). La cifra en us/dia va SIEMPRE al lado en el clip:
    la exageracion visual se confiesa."""
    radio = float(radio)
    esfera = Circle(radius=radio, stroke_width=2.6, color=color_esfera)
    marcas = VGroup()
    for k in range(12):
        ang = TAU * k / 12.0
        u = np.array([math.cos(ang), math.sin(ang), 0.0])
        marcas.add(Line(u * radio * 0.86, u * radio * 0.97,
                        stroke_width=2.0, color=color_esfera))
    marcas.set_stroke(opacity=0.8)
    manecilla = Line(ORIGIN, UP * radio * 0.72, stroke_width=3.2,
                     color=color)
    params = {"frac_manecilla": 0.72}
    pieza = CaritaReloj(_ancla(ORIGIN), esfera, marcas, manecilla, params)
    return pieza.en(0.0)


# =====================================================================
# El mapa del error
# =====================================================================
class MapaError(VGroup):
    """Mapa con pin; el circulo rojo crece con las horas sin correccion."""

    def __init__(self, ancla, caja, calles, pin, circulo, params, **kwargs):
        super().__init__(ancla, caja, calles, pin, circulo, **kwargs)
        self._ancla = ancla            # el pin (tu posicion verdadera)
        self.caja = caja
        self.calles = calles
        self.pin = pin
        self.circulo = circulo
        self._params = params

    def _escala_actual(self):
        # unidades de escena por km, sobre la geometria actual
        return self.caja.width / max(self._params["km_lado"], _EPS)

    def radio_km(self, horas):
        """El radio del error a las `horas`, en km (c * deriva neta)."""
        return error_metros(horas) / 1000.0

    def en(self, horas):
        """Escala el circulo de error al radio de `horas` (geometria
        ACTUAL, tope el lado del mapa); para UpdateFromAlphaFunc."""
        r_esc = self.radio_km(horas) * self._escala_actual()
        r_esc = float(np.clip(r_esc, 0.012,
                              0.75 * self.caja.width))
        self.circulo.scale_to_fit_width(2.0 * r_esc)
        self.circulo.move_to(self._ancla.get_center())
        return self


def mapa_error(lado=3.6, km_lado=30.0, calles=9, color_pin=COLOR_TIERRA,
               color_error=COLOR_ERROR, color_caja=COLOR_EJE, semilla=7):
    """Mapa cuadrado (lado = `km_lado` km) con calles tenues, pin verde y
    circulo de error rojo. `mapa.en(horas)` pone el circulo al error real
    c*deriva (481 m/hora); `.radio_km(horas)` expone el numero."""
    calles = _validar("mapa_error.calles", calles, CALLES_MAX)
    lado, km_lado = float(lado), float(km_lado)
    rng = np.random.default_rng(int(semilla))

    caja = RoundedRectangle(width=lado, height=lado, corner_radius=0.12,
                            stroke_width=2.2, color=color_caja)
    grupo_calles = VGroup()
    for _ in range(calles):
        if rng.random() < 0.5:
            y = (rng.random() - 0.5) * lado * 0.86
            linea = Line([-lado / 2, y, 0], [lado / 2, y, 0],
                         stroke_width=1.4, color=color_caja)
        else:
            x = (rng.random() - 0.5) * lado * 0.86
            linea = Line([x, -lado / 2, 0], [x, lado / 2, 0],
                         stroke_width=1.4, color=color_caja)
        linea.set_stroke(opacity=0.45)
        grupo_calles.add(linea)

    pin = Dot(ORIGIN, radius=0.08, color=color_pin)
    circulo = Circle(radius=0.012, stroke_width=2.4, color=color_error,
                     fill_color=color_error, fill_opacity=0.15)

    params = {"lado": lado, "km_lado": km_lado}
    pieza = MapaError(_ancla(ORIGIN), caja, grupo_calles, pin, circulo,
                      params)
    return pieza.en(0.0)


# =====================================================================
# El tren de pulsos
# =====================================================================
class FilaPulsos(VGroup):
    """Fila de pulsos equiespaciados; `.en(i)` localiza el pulso i."""

    def __init__(self, ancla, pulsos, params, **kwargs):
        super().__init__(ancla, pulsos, **kwargs)
        self._ancla = ancla            # el primer pulso, abajo
        self.pulsos = pulsos
        self._params = params

    def paso_actual(self):
        if len(self.pulsos) < 2:
            return 0.0
        return float(np.linalg.norm(
            self.pulsos[1].get_center() - self.pulsos[0].get_center()))

    def en(self, i):
        """Centro del pulso i (geometria ACTUAL)."""
        return self.pulsos[int(i)].get_center()

    def con_desfase(self, desfase):
        """La misma fila corrida `desfase` pasos (fraccion), anclada al
        arranque de esta (para Transform o comparacion)."""
        params = dict(self._params, desfase=float(desfase))
        otro = fila_pulsos(**params)
        otro.shift(self._ancla.get_center() - otro._ancla.get_center())
        return otro


def fila_pulsos(n=16, ancho=5.2, alto=0.42, desfase=0.0, color=COLOR_LUZ):
    """`n` pulsos verticales repartidos en `ancho`, corridos `desfase`
    pasos. Dos filas con desfases distintos son el reloj de fabrica y el
    reloj en orbita del clip 8 (exageracion confesada con su cifra)."""
    n = _validar("fila_pulsos.n", n, PULSOS_MAX)
    ancho, alto, desfase = float(ancho), float(alto), float(desfase)
    paso = ancho / (n - 1) if n > 1 else 0.0
    x0 = -ancho / 2.0 + desfase * paso

    pulsos = VGroup()
    for k in range(n):
        x = x0 + k * paso
        pulsos.add(Line([x, -alto / 2, 0], [x, alto / 2, 0],
                        stroke_width=2.6, color=color))
    pulsos.set_stroke(opacity=0.9)

    params = {"n": n, "ancho": ancho, "alto": alto, "desfase": desfase,
              "color": color}
    # El ancla es el MARCO (independiente del desfase): asi con_desfase
    # alinea marcos y el corrimiento de los pulsos se ve.
    base = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    return FilaPulsos(_ancla(base), pulsos, params)
