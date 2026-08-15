"""Enlaces opticos entre satelites (ISL): apuntar, adquirir, seguir y medirse.

Modulo 3 de la familia "Metrologia optica". Todo el calculo es
python/numpy/scipy puro y determinista (el unico azar va con semilla en
`mapa_gravedad`): mismo script -> mismo render, condicion necesaria para
`--disable_caching`. Nada de red, nada de disco.

La regla de color de la familia, que es tambien la de esta libreria: el
ROJO es la FUENTE (el laser, el haz, el pulso que sale), el AMBAR la onda
y su fase, el VIOLETA lo que la luz DIBUJA (la huella, la mancha, las
franjas), el CIAN lo que se MIDE (cifras, curvas de resultado, el
detector) y el VERDE el otro extremo: el satelite receptor, la nave, la
masa que se mide. El gris `COLOR_EJE` es mobiliario.

Piezas:
    dos_satelites           arco de orbita + dos satelites; `.enlace()`, `.a_separacion(km)`
    cono_haz                el cono de microradianes y su huella; `.con_divergencia(t)`
    barra_enlace            cascada Pt +Gt -FSPL +Gr = Pr; `.paso(i)`, `.pr_dbm`
    comparador_rf_optico    antena RF 1 m vs telescopio 10 cm; `.fila(nombre)`
    punteria                huella contra el receptor; `.con_error(urad)`, `.acierta()`
    adelanto_apuntado       apuntar adonde ESTARA; `.a_t(frac)`
    espiral_adquisicion     la busqueda hasta ver el faro; `.a_paso(k)`, `.k_encuentro`
    detector_cuadrantes     4 cuadrantes + mancha + barras; `.con_mancha(x, y)`, `.senales()`
    grace_par               GRACE-FO: la masa que los separa; `.a_t(frac)`, `.delta_nm()`
    interferometro_espacial esquema LRI con la senal de fase; `.a_fase(f)`, `.senal`
    mapa_gravedad           mapa de anomalias (ImageMobject); `.region(nombre)`
    triangulo_lisa          tres naves y un brazo que se estira; `.a_estiramiento(h)`

Los NUMEROS que se rotulan salen de funciones (`ganancia_apertura`,
`fspl_db`, `potencia_recibida_dbm`, `energia_foton`, `fotones_por_bit`,
`divergencia_gauss`, `huella`, `angulo_adelanto`, `doppler_optico`,
`desplazamiento_por_jitter`, `tiempo_luz`, `espiral_busqueda`,
`error_cuadrante`, `sensibilidad_relativa`), nunca a mano. El paso en que
la espiral encuentra el faro (`.k_encuentro`) se MIDE recorriendola.

Convenciones (las mismas de `cripto.py`):
    - cada pieza es un `VGroup` con atributos publicos y localizadores
      sobre la geometria ACTUAL (sobreviven a `.shift/.move_to/.scale`);
    - `.con_*()` devuelve una pieza GEMELA ya escalada y colocada encima
      de la original, lista para `Transform`;
    - `.a_*()` MUTA la pieza en sitio y devuelve `self`, lista para
      updaters y `ValueTracker`.
    EXCEPCIONES documentadas: `punteria.con_error` y
    `detector_cuadrantes.con_mancha` MUTAN (asi lo pide el contrato del
    curso); tienen alias `a_error` / `a_mancha` con el mismo efecto.

`mapa_gravedad` es la unica pieza que NO es un VGroup: lleva dentro un
`ImageMobject` y por eso es un `Group`. Un ImageMobject NO acepta
`set_color` ni `set_stroke`: se anima con `FadeIn`/`FadeOut` o
transformando a una gemela.

Topes duros para no castigar el VPS: `PUNTOS_MAX`, `CELDAS_MAX`,
`PIXELES_MAX`, `VUELTAS_MAX` levantan ValueError.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from isl import cono_haz, huella

    cono = cono_haz(9.87, 5000.0)
    self.play(FadeIn(cono))
    self.play(Transform(cono, cono.con_divergencia(20.0)))
"""

import math

import numpy as np
from scipy.special import erf

from manim import (Arc, Circle, DashedLine, DashedVMobject, Dot, Ellipse,
                   Group, ImageMobject, Line, Polygon, Rectangle,
                   RoundedRectangle, Text, VGroup, VMobject, DOWN, LEFT,
                   ORIGIN, PI, RIGHT, TAU, UP)

from code_brand import CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
PUNTOS_MAX = 4000       # puntos de una polilinea / de la espiral
CELDAS_MAX = 64         # celdas de una rejilla o de una tira de franjas
PIXELES_MAX = 900       # lado mayor (px) de una imagen sintetica
VUELTAS_MAX = 12        # vueltas de la espiral de adquisicion

# --- Constantes fisicas y del curso ----------------------------------
C_LUZ = 299_792_458.0        # m/s, EXACTA por definicion del metro (1983)
LAMBDA_ISL = 1550e-9         # m, la banda de telecom que usan los ISL
H_PLANCK = 6.626e-34         # J s (valor redondeado que rotula el curso)
R_TIERRA_KM = 6371.0         # km, radio medio
V_LEO_KMS = 7.6              # km/s, velocidad tipica en orbita baja
SEP_GRACE_KM = 220.0         # km, separacion nominal del par GRACE-FO
BRAZO_LISA_KM = 2.5e6        # km, brazo de LISA (2.5 millones de km)

# Paleta propia de la libreria (coincide con la de la familia).
COLOR_HAZ = "#f43f5e"      # rojo: la fuente, el laser, el haz, el pulso
COLOR_ONDA = "#f59e0b"     # ambar: la onda y su fase
COLOR_FRANJA = "#a78bfa"   # violeta: lo que la luz DIBUJA (huella, mancha)
COLOR_MEDIDA = "#22d3ee"   # cian: lo que se mide (cifras, curvas, detector)
COLOR_OBJETO = "#34d399"   # verde: el otro extremo (satelite, nave, masa)
COLOR_EJE = "#31414f"      # mobiliario

C_HAZ, C_ONDA, C_FRANJA = COLOR_HAZ, COLOR_ONDA, COLOR_FRANJA
C_MEDIDA, C_OBJETO, C_EJE = COLOR_MEDIDA, COLOR_OBJETO, COLOR_EJE

_EPS = 1e-12


# =====================================================================
# Utilidades internas
# =====================================================================
def _validar(nombre, valor, tope, minimo=1):
    """Entero en [minimo, tope] o ValueError."""
    valor = int(valor)
    if valor < minimo or valor > tope:
        raise ValueError(f"{nombre}: {valor} fuera de rango "
                         f"({minimo}..{tope})")
    return valor


def _positivo(nombre, valor):
    """Float estrictamente positivo o ValueError."""
    valor = float(valor)
    if not np.isfinite(valor) or valor <= 0.0:
        raise ValueError(f"{nombre}: {valor} no es un positivo finito")
    return valor


def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Texto de telemetria: Space Mono, ASCII PURO.

    La fuente HUD no trae tildes ni el signo micro: se escribe "urad",
    "um", "lambda". Un texto no-ASCII levanta ValueError a proposito —
    en pantalla saldrian cuadros vacios.
    """
    registrar_fuentes()
    texto = str(texto)
    if not texto.isascii():
        raise ValueError(f"_texto_hud: '{texto}' no es ASCII puro "
                         "(usa 'urad', 'um', 'lambda', sin tildes)")
    return Text(texto, font=FUENTE_HUD, font_size=font_size, color=color)


def _v3(p):
    """(x, y) o (x, y, z) -> np.array de 3 componentes."""
    p = np.asarray(p, dtype=np.float64).ravel()
    if p.size == 2:
        p = np.append(p, 0.0)
    if p.size != 3:
        raise ValueError(f"_v3: {p} no es un punto 2-D ni 3-D")
    return p


def _ancla(punto=ORIGIN):
    """Dot invisible que viaja con la pieza: localizador inmune a
    `move_to`, `shift` y `scale`."""
    return Dot(_v3(punto), radius=0.001, fill_opacity=0.0,
               stroke_opacity=0.0)


def _poligonal(puntos, color, grosor=2.0):
    """Polilinea a partir de una lista de puntos 2-D o 3-D."""
    pts = np.asarray(puntos, dtype=np.float64)
    if len(pts) > PUNTOS_MAX:
        raise ValueError(f"_poligonal: {len(pts)} puntos > {PUNTOS_MAX}")
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(pts)
    return linea


class _Pieza(VGroup):
    """Base de todas las piezas: dos anclas invisibles (`_ancla_a` a la
    izquierda, `_ancla_b` a la derecha, separadas `_largo_ref` en el
    sistema LOCAL en que se construyo la pieza).

    De ahi salen dos servicios:
      - `_punto(p_local)`: lleva una coordenada del sistema local a la
        escena ACTUAL (sobrevive a `.shift/.move_to/.scale`);
      - `_alinear(otra)`: escala y coloca una pieza GEMELA encima de
        esta, que es lo que necesita `Transform`.
    """

    def _escala_actual(self):
        d = float(np.linalg.norm(self._ancla_b.get_center()
                                 - self._ancla_a.get_center()))
        return d / max(self._largo_ref, _EPS)

    def _punto(self, p_local):
        return (self._ancla_a.get_center()
                + (_v3(p_local) - self._p_a) * self._escala_actual())

    def _alinear(self, otra):
        otra.scale(self._escala_actual())
        otra.shift(self._ancla_a.get_center() - otra._ancla_a.get_center())
        return otra


def _anclas_de(largo_ref, y=0.0):
    """Par (ancla_a, ancla_b, p_a_local) centrado en el origen local."""
    a = np.array([-largo_ref / 2.0, y, 0.0])
    b = np.array([largo_ref / 2.0, y, 0.0])
    return _ancla(a), _ancla(b), a


def _satelite(escala=1.0, color=COLOR_OBJETO):
    """Icono de satelite: cuerpo + dos paneles. Mide ~0.9*escala de
    ancho y ~0.22*escala de alto."""
    e = float(escala)
    cuerpo = Rectangle(width=0.30 * e, height=0.22 * e, stroke_width=2.0,
                       color=color)
    cuerpo.set_fill(color, opacity=0.32)
    izq = Rectangle(width=0.26 * e, height=0.11 * e, stroke_width=1.3,
                    color=color)
    izq.set_fill(color, opacity=0.12)
    izq.next_to(cuerpo, LEFT, buff=0.07 * e)
    der = izq.copy()
    der.next_to(cuerpo, RIGHT, buff=0.07 * e)
    eje = Line(izq.get_right(), der.get_left(), stroke_width=1.2,
               color=color)
    return VGroup(eje, izq, der, cuerpo)


def _telescopio(escala=1.0, color=COLOR_HAZ):
    """Icono de telescopio/emisor: tubo + boca. Mide ~0.62*escala."""
    e = float(escala)
    tubo = Rectangle(width=0.40 * e, height=0.26 * e, stroke_width=2.0,
                     color=color)
    tubo.set_fill(color, opacity=0.18)
    boca = Rectangle(width=0.10 * e, height=0.34 * e, stroke_width=2.0,
                     color=color)
    boca.set_fill(color, opacity=0.30)
    boca.next_to(tubo, RIGHT, buff=0.0)
    return VGroup(tubo, boca)


# =====================================================================
# Nucleo: la ganancia de una apertura y el presupuesto de enlace
# =====================================================================
def ganancia_apertura(D, lam):
    """Ganancia LINEAL de una apertura circular ideal: (pi D / lam)^2.

    Es la misma formula para una antena de radio y para un telescopio —
    de ahi sale toda la ventaja del laser: la ganancia crece con el
    CUADRADO de D/lam, y a 1550 nm el cociente D/lam es enorme.

    Ejemplos: 10 cm a 1550 nm -> 4.108e10 (106.1 dBi);
    1 m a 30 GHz (lam = 9.993 mm) -> 9.883e4 (49.9 dBi).
    """
    D = _positivo("ganancia_apertura.D", D)
    lam = _positivo("ganancia_apertura.lam", lam)
    return (math.pi * D / lam) ** 2


def db10(x):
    """Potencia/ganancia lineal -> decibelios: 10 log10(x)."""
    x = _positivo("db10.x", x)
    return 10.0 * math.log10(x)


def ganancia_dbi(D, lam):
    """EXTRA (comodidad): `ganancia_apertura` ya en dBi.

    10 cm @1550 nm -> 106.14 dBi; 1 m @30 GHz -> 49.95 dBi.
    """
    return db10(ganancia_apertura(D, lam))


def longitud_de_onda_de(f):
    """EXTRA: c/f. 30 GHz -> 9.993 mm."""
    return C_LUZ / _positivo("longitud_de_onda_de.f", f)


def fspl_db(R, lam):
    """Perdida de espacio libre: 20 log10(4 pi R / lam), en dB.

    No es que el espacio "absorba": es que la esfera de la onda crece.
    5000 km a 1550 nm -> 272.16 dB. Con esos numeros el presupuesto solo
    cierra porque las dos aperturas regalan 106 dB cada una.
    """
    R = _positivo("fspl_db.R", R)
    lam = _positivo("fspl_db.lam", lam)
    return 20.0 * math.log10(4.0 * math.pi * R / lam)


def potencia_recibida_dbm(Pt_dbm, Gt, Gr, R, lam, perdidas_db=0.0):
    """Ecuacion de enlace en dB: Pt + Gt - FSPL + Gr - perdidas.

    `Pt_dbm` en dBm, `Gt`/`Gr` en dBi, `R` y `lam` en metros. Con 1 W
    (30 dBm), dos telescopios de 10 cm (106.14 dBi cada uno) y 5000 km:
    -29.88 dBm, es decir ~1.03 uW. Es un presupuesto IDEAL: sin perdidas
    opticas ni de apuntado (para eso esta `perdidas_db`).
    """
    return (float(Pt_dbm) + float(Gt) - fspl_db(R, lam) + float(Gr)
            - float(perdidas_db))


def dbm_a_w(p_dbm):
    """EXTRA: dBm -> watts. -30 dBm -> 1e-6 W."""
    return 10.0 ** (float(p_dbm) / 10.0) * 1e-3


def w_a_dbm(p_w):
    """EXTRA: watts -> dBm. 1 W -> 30 dBm."""
    return 10.0 * math.log10(_positivo("w_a_dbm.p_w", p_w) / 1e-3)


# =====================================================================
# Nucleo: fotones
# =====================================================================
def energia_foton(lam):
    """Energia de un foton: h c / lam, en julios.

    A 1550 nm son 1.282e-19 J. Es la moneda mas pequena del enlace: por
    debajo de unos cientos de fotones por bit no hay demodulacion que
    valga.
    """
    lam = _positivo("energia_foton.lam", lam)
    return H_PLANCK * C_LUZ / lam


def fotones_por_segundo(P, lam):
    """Fotones por segundo de una potencia optica: P / (h c / lam).

    1 uW a 1550 nm -> 7.80e12 fotones/s.
    """
    P = _positivo("fotones_por_segundo.P", P)
    return P / energia_foton(lam)


def fotones_por_bit(P, lam, tasa):
    """Fotones por bit: fotones/s dividido entre la tasa de bits.

    1 uW a 1550 nm y 10 Gbps -> 780.3 fotones por bit. Ese es el numero
    que de verdad decide si el enlace cierra.
    """
    tasa = _positivo("fotones_por_bit.tasa", tasa)
    return fotones_por_segundo(P, lam) / tasa


# =====================================================================
# Nucleo: el haz (duplicado de optica.py a proposito, ver contrato)
# =====================================================================
def divergencia_gauss(lam, w0):
    """Semiangulo de divergencia de un haz gaussiano: lam / (pi w0).

    Es el angulo del cono lejano medido desde el eje. Con 1550 nm y una
    cintura w0 = 5 cm (un telescopio de 10 cm) salen 9.868 urad. Ningun
    laser es una recta: todo haz se abre.
    """
    lam = _positivo("divergencia_gauss.lam", lam)
    w0 = _positivo("divergencia_gauss.w0", w0)
    return lam / (math.pi * w0)


def huella(theta, R):
    """DIAMETRO de la huella del haz a distancia R: 2 theta R.

    `theta` es el SEMIangulo (el de `divergencia_gauss`), asi que el
    diametro es el doble. 9.868 urad a 5000 km -> 98.68 m. Un haz que a
    5000 km mide 99 metros parece generoso hasta que uno recuerda que el
    satelite mide 1 metro.
    """
    return 2.0 * float(theta) * float(R)


def radio_haz_en(z, lam, w0):
    """EXTRA: radio del haz gaussiano a distancia z, w0 sqrt(1+(z/zR)^2)
    con zR = pi w0^2 / lam. A 5000 km con w0=5 cm da 49.34 m, o sea la
    mitad de la huella (coherente con `huella`)."""
    lam = _positivo("radio_haz_en.lam", lam)
    w0 = _positivo("radio_haz_en.w0", w0)
    zr = math.pi * w0 * w0 / lam
    return w0 * math.sqrt(1.0 + (float(z) / zr) ** 2)


# =====================================================================
# Nucleo: apuntar, seguir y el tiempo de luz
# =====================================================================
def angulo_adelanto(v_perp):
    """Angulo de adelanto de apuntado: 2 v / c, en radianes.

    Sale el DOBLE de v/c porque hay ida y vuelta: cuando la luz llega,
    el receptor ya se movio, y su respuesta encuentra al emisor tambien
    movido. A 7.6 km/s son 50.70 urad — mas de CINCO veces la
    divergencia de 9.87 urad: apuntar adonde esta el otro es fallar.
    """
    return 2.0 * float(v_perp) / C_LUZ


def doppler_optico(v, lam):
    """Corrimiento Doppler optico (primer orden): v / lam, en hertz.

    7.6 km/s a 1550 nm -> 4.903 GHz. El receptor tiene que buscar la
    portadora en varios GHz: por eso los ISL barren en frecuencia.
    """
    lam = _positivo("doppler_optico.lam", lam)
    return float(v) / lam


def desplazamiento_por_jitter(theta, R):
    """Cuanto se corre la huella por un error de apuntado: theta R.

    1 urad a 5000 km son 5 metros. Es el numero que explica por que un
    ISL necesita un sensor de cuadrantes y un espejo rapido.
    """
    return float(theta) * float(R)


def tiempo_luz(d):
    """Tiempo de vuelo de IDA: d / c, en segundos.

    220 km (GRACE-FO) -> 0.734 ms; un brazo de LISA (2.5e6 km) ->
    8.339 s. En LISA la "instantaneidad" no existe: el dato de hace 8
    segundos es el presente del otro extremo.
    """
    return float(d) / C_LUZ


def sensibilidad_relativa(dl, L):
    """Cuanto vale la medida en fraccion de la distancia: dl / L.

    1 nm en 220 km -> 4.545e-15. 1 pm en 2.5e6 km -> 4.0e-22. (OJO: el
    storyboard escribia 4e-25 para el caso de LISA; la cuenta honesta es
    1e-12 m / 2.5e9 m = 4e-22. Se rotula 4e-22.)
    """
    L = _positivo("sensibilidad_relativa.L", L)
    return float(dl) / L


# =====================================================================
# Nucleo: la espiral de busqueda y el detector de cuadrantes
# =====================================================================
def espiral_busqueda(paso, n_vueltas, por_vuelta=24):
    """Puntos (x, y) de una espiral de Arquimedes r = paso * theta/(2 pi).

    Es el barrido de adquisicion: el haz apunta a cada punto por turno,
    en circulos cada vez mas amplios, hasta cruzar el faro del otro
    satelite. `paso` es lo que crece el radio en UNA vuelta (en las
    unidades que use el clip: urad en el cielo, unidades de escena en el
    dibujo), y el muestreo es `por_vuelta` puntos por vuelta.

    Devuelve un array (N, 2) con N = n_vueltas * por_vuelta + 1, el
    primero en el centro. Determinista: no hay azar en una espiral.

    Ejemplo: `espiral_busqueda(0.78, 3)` -> 73 puntos, radio final 2.34.
    """
    paso = _positivo("espiral_busqueda.paso", paso)
    n_vueltas = _validar("espiral_busqueda.n_vueltas", n_vueltas,
                         VUELTAS_MAX)
    por_vuelta = _validar("espiral_busqueda.por_vuelta", por_vuelta, 240,
                          minimo=3)
    n = n_vueltas * por_vuelta + 1
    _validar("espiral_busqueda.puntos", n, PUNTOS_MAX)
    theta = np.arange(n, dtype=np.float64) * (TAU / por_vuelta)
    r = paso * theta / TAU
    return np.column_stack([r * np.cos(theta), r * np.sin(theta)])


def potencias_cuadrante(x, y, w):
    """EXTRA: fraccion de potencia en cada cuadrante (A, B, C, D).

    Mancha gaussiana I = exp(-2 r^2 / w^2) centrada en (x, y) sobre un
    detector partido por los ejes; A = arriba-izquierda, B =
    arriba-derecha, C = abajo-izquierda, D = abajo-derecha. Las cuatro
    suman 1 exactamente (el detector se supone mucho mayor que la
    mancha, que es el caso de trabajo). Analitico, sin integrar: la
    gaussiana es separable y cada mitad sale con `erf`.
    """
    w = _positivo("potencias_cuadrante.w", w)
    fx = 0.5 * (1.0 + erf(math.sqrt(2.0) * float(x) / w))   # fraccion x>0
    fy = 0.5 * (1.0 + erf(math.sqrt(2.0) * float(y) / w))   # fraccion y>0
    return ((1.0 - fx) * fy, fx * fy, (1.0 - fx) * (1.0 - fy),
            fx * (1.0 - fy))


def error_cuadrante(x, y, w):
    """Senales normalizadas del detector de 4 cuadrantes: (ex, ey).

    ex = (B + D - A - C) / (A+B+C+D) mide el error horizontal y
    ey = (A + B - C - D) / (A+B+C+D) el vertical. Con la mancha
    gaussiana de `potencias_cuadrante` las dos se reducen a
    erf(sqrt(2) x / w) y erf(sqrt(2) y / w): centrada da (0, 0),
    y a un radio w las senales valen ya +-0.954 (el detector se satura
    en cuanto la mancha se sale). Ese es el lazo que "sigue sin
    temblar": el error se lee como un voltaje, no como una imagen.
    """
    a, b, c, d = potencias_cuadrante(x, y, w)
    total = a + b + c + d
    if total <= 0.0:
        raise ValueError("error_cuadrante: potencia total nula")
    return ((b + d - a - c) / total, (a + b - c - d) / total)


# =====================================================================
# 3.1 — Dos satelites sobre una orbita
# =====================================================================
class DosSatelites(_Pieza):
    """Arco de orbita (gris) con dos satelites verdes separados.

    Publico: `.arco`, `.a`, `.b`, `.rotulo` (HUD con los km),
    `.sep_km`; `.centro_a` / `.centro_b` son PROPIEDADES que devuelven
    el punto de escena ACTUAL de cada satelite.
    """

    def __init__(self, ancla_a, ancla_b, arco, sat_a, sat_b, rotulo, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, arco, sat_a, sat_b, rotulo,
                         **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.arco = arco
        self.a = sat_a
        self.b = sat_b
        self.rotulo = rotulo
        self._params = params
        self.sep_km = params["sep_km"]

    @property
    def centro_a(self):
        """Punto de escena del satelite A, sobre la geometria ACTUAL."""
        return self.a.get_center()

    @property
    def centro_b(self):
        """Punto de escena del satelite B, sobre la geometria ACTUAL."""
        return self.b.get_center()

    def _en_orbita(self, sep_km):
        """Posiciones locales de los dos satelites para esa separacion."""
        p = self._params
        frac = float(sep_km) / p["span_km"]
        ang = 0.5 * frac * p["angulo"]
        centro = np.array([0.0, p["y_centro"], 0.0])
        r = p["radio"]
        return [centro + r * np.array([-math.sin(ang), math.cos(ang), 0.0]),
                centro + r * np.array([math.sin(ang), math.cos(ang), 0.0])]

    def enlace(self, color=COLOR_HAZ, grosor=2.0):
        """El enlace optico: Line roja fina de A a B, sobre la geometria
        ACTUAL. Es un mobject NUEVO (la pieza no lo contiene): el clip lo
        anima con `Create` y lo quita cuando quiere."""
        return Line(self.centro_a, self.centro_b, stroke_width=float(grosor),
                    color=color)

    def a_separacion(self, km):
        """MUTA: recoloca los dos satelites para esa separacion (km) y
        reescribe el rotulo. Devuelve `self`.

        La escala es angular: `span_km` (12 000 km por omision) ocupa el
        arco entero, asi que 5000 km son el 42 % del arco. Los tamanos de
        los satelites NO estan a escala (a 5000 km un satelite de 1 m
        seria invisible).
        """
        km = float(km)
        if km < 0.0 or km > self._params["span_km"]:
            raise ValueError(f"a_separacion: {km} km fuera de "
                             f"(0..{self._params['span_km']})")
        pa, pb = self._en_orbita(km)
        self.a.move_to(self._punto(pa))
        self.b.move_to(self._punto(pb))
        self.sep_km = km
        self._params["sep_km"] = km
        nuevo = _texto_hud(f"{km:.0f} km", font_size=17, color=COLOR_MEDIDA)
        nuevo.scale(self._escala_actual())
        nuevo.move_to(0.5 * (self.centro_a + self.centro_b)
                      + DOWN * 0.42 * self._escala_actual())
        self.remove(self.rotulo)
        self.add(nuevo)
        self.rotulo = nuevo
        return self


def dos_satelites(sep_km=5000.0, R_orb_rel=1.35, span_km=12000.0,
                  ancho=6.2, escala_sat=1.6):
    """Dos satelites verdes sobre un arco de orbita gris.

    El arco abarca `span_km` de arco util y mide `ancho` de punta a
    punta; `R_orb_rel` es el radio de la orbita en unidades del ancho (a
    mayor valor, arco mas plano). Los satelites se separan `sep_km`
    simetricamente respecto del vertice del arco.

    HONESTIDAD: la DISTANCIA esta a escala dentro del arco; los TAMANOS
    de los satelites no (son iconos). Ejemplo del curso: `sep_km=5000`.
    """
    ancho = _positivo("dos_satelites.ancho", ancho)
    span_km = _positivo("dos_satelites.span_km", span_km)
    sep_km = float(sep_km)
    if sep_km < 0.0 or sep_km > span_km:
        raise ValueError(f"dos_satelites: sep_km={sep_km} fuera de "
                         f"(0..{span_km})")
    radio = _positivo("dos_satelites.R_orb_rel", R_orb_rel) * ancho
    # Semiangulo del arco dibujado: el que hace que la cuerda mida `ancho`.
    semi = math.asin(min(ancho / (2.0 * radio), 0.999))
    y_centro = -radio * math.cos(semi)

    arco = Arc(radius=radio, start_angle=PI / 2 - semi, angle=2 * semi,
               stroke_width=2.0, color=COLOR_EJE)
    arco.move_arc_center_to(np.array([0.0, y_centro, 0.0]))

    params = {"ancho": ancho, "span_km": span_km, "sep_km": sep_km,
              "radio": radio, "angulo": 2 * semi, "y_centro": y_centro,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}

    sat_a = _satelite(escala_sat)
    sat_b = _satelite(escala_sat)
    rotulo = _texto_hud(f"{sep_km:.0f} km", font_size=17, color=COLOR_MEDIDA)

    a_a, a_b, p_a = _anclas_de(ancho)
    pieza = DosSatelites(a_a, a_b, arco, sat_a, sat_b, rotulo, params)
    pieza.a_separacion(sep_km)
    return pieza


# =====================================================================
# 3.1 — El cono del haz y su huella
# =====================================================================
class ConoHaz(_Pieza):
    """El cono de microradianes desde el emisor hasta la huella.

    Publico: `.emisor`, `.cono`, `.huella_elipse`, `.receptor`,
    `.rotulo`, `.theta_urad`, `.R_km`, `.huella_m`.
    """

    def __init__(self, ancla_a, ancla_b, cono, emisor, huella_elipse,
                 receptor, eje, rotulo, params, **kwargs):
        super().__init__(ancla_a, ancla_b, cono, eje, huella_elipse, emisor,
                         receptor, rotulo, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["largo"]
        self._p_a = params["p_a"]
        self.cono = cono
        self.eje = eje
        self.emisor = emisor
        self.huella_elipse = huella_elipse
        self.receptor = receptor
        self.rotulo = rotulo
        self._params = params
        self.theta_urad = params["theta_urad"]
        self.R_km = params["R_km"]
        self.huella_m = params["huella_m"]

    def punta(self):
        """Punto de escena del vertice del cono (el emisor)."""
        return self._punto(self._params["p_punta"])

    def centro_huella(self):
        """Punto de escena del centro de la huella (el receptor)."""
        return self._punto(self._params["p_huella"])

    def con_divergencia(self, theta_urad):
        """Pieza GEMELA con otra divergencia, ya escalada y colocada
        encima de esta: `Transform(cono, cono.con_divergencia(20))`.

        Conserva R_km y el largo, asi que las dos son comparables.
        """
        p = self._params
        otra = cono_haz(theta_urad, p["R_km"], largo=p["largo"],
                        theta_ref=p["theta_ref"], semi_ref=p["semi_ref"])
        return self._alinear(otra)


def cono_haz(theta_urad=9.87, R_km=5000.0, largo=5.0, theta_ref=9.87,
             semi_ref=0.52):
    """El cono del haz desde el emisor hasta la huella en el receptor.

    `theta_urad` es el SEMIangulo de divergencia en microradianes y
    `R_km` la distancia al receptor; el rotulo dice el DIAMETRO de la
    huella, calculado con `huella(theta, R)` (9.87 urad a 5000 km ->
    98.7 m).

    EXAGERACION (documentada): el semiancho en pantalla es
    `semi_ref * theta_urad / theta_ref`, o sea LINEAL en theta con
    9.87 urad -> 0.52 unidades. El cono real tiene una apertura de 1e-5
    radianes: a escala seria una recta.

    La huella se dibuja como una elipse violeta (el circulo visto de
    canto), porque violeta es "lo que la luz dibuja".
    """
    theta_urad = _positivo("cono_haz.theta_urad", theta_urad)
    R_km = _positivo("cono_haz.R_km", R_km)
    largo = _positivo("cono_haz.largo", largo)
    theta_ref = _positivo("cono_haz.theta_ref", theta_ref)
    semi_ref = _positivo("cono_haz.semi_ref", semi_ref)

    theta = theta_urad * 1e-6
    huella_m = huella(theta, R_km * 1e3)
    semi = semi_ref * theta_urad / theta_ref

    x0, x1 = -largo / 2.0, largo / 2.0
    p_punta = np.array([x0, 0.0, 0.0])
    p_huella = np.array([x1, 0.0, 0.0])

    cono = Polygon(p_punta,
                   np.array([x1, semi, 0.0]),
                   np.array([x1, -semi, 0.0]),
                   stroke_width=1.6, color=COLOR_HAZ)
    cono.set_fill(COLOR_HAZ, opacity=0.16)
    eje = DashedLine(p_punta, p_huella, stroke_width=1.2, color=COLOR_HAZ,
                     dash_length=0.09)
    eje.set_stroke(opacity=0.55)

    elipse = Ellipse(width=max(0.30 * semi, 0.06), height=2.0 * semi,
                     stroke_width=2.2, color=COLOR_FRANJA)
    elipse.set_fill(COLOR_FRANJA, opacity=0.22)
    elipse.move_to(p_huella)

    emisor = _telescopio(1.0, COLOR_HAZ)
    emisor.move_to(p_punta + LEFT * 0.20)
    receptor = _satelite(1.5, COLOR_OBJETO)
    receptor.move_to(p_huella + RIGHT * 0.52)

    rotulo = VGroup(
        _texto_hud(f"{theta_urad:.2f} urad", font_size=16, color=COLOR_HAZ),
        _texto_hud(f"huella {huella_m:.1f} m", font_size=16,
                   color=COLOR_MEDIDA),
        _texto_hud(f"a {R_km:.0f} km", font_size=14, color=CODE_MUTED))
    rotulo[0].move_to(np.array([x0 + 0.95, semi + 0.30, 0.0]),
                      aligned_edge=LEFT)
    rotulo[1].move_to(np.array([x1 - 0.10, -semi - 0.34, 0.0]),
                      aligned_edge=RIGHT)
    rotulo[2].next_to(rotulo[1], DOWN, buff=0.10)

    params = {"largo": largo, "theta_urad": theta_urad, "R_km": R_km,
              "huella_m": huella_m, "theta_ref": theta_ref,
              "semi_ref": semi_ref, "p_punta": p_punta,
              "p_huella": p_huella,
              "p_a": np.array([-largo / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(largo)
    return ConoHaz(a_a, a_b, cono, emisor, elipse, receptor, eje, rotulo,
                   params)


# =====================================================================
# 3.1 — El presupuesto de enlace en cascada
# =====================================================================
class BarraEnlace(_Pieza):
    """Cascada del presupuesto: Pt +Gt -FSPL +Gr = Pr, en barras de dB.

    Publico: `.barras` (VGroup de 5), `.nombres`, `.valores`, `.eje_cero`,
    `.pr_dbm`, `.pr_w`, `.acumulado` (lista de los 4 parciales).
    `.paso(i)` devuelve el VGroup (barra + nombre + valor) del paso i,
    con i en 0..4 (4 es la barra de resultado Pr).
    """

    def __init__(self, ancla_a, ancla_b, eje_cero, barras, nombres, valores,
                 nota, params, **kwargs):
        super().__init__(ancla_a, ancla_b, eje_cero, barras, nombres,
                         valores, nota, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.eje_cero = eje_cero
        self.barras = barras
        self.nombres = nombres
        self.valores = valores
        self.nota = nota
        self._params = params
        self.pr_dbm = params["pr_dbm"]
        self.pr_w = dbm_a_w(params["pr_dbm"])
        self.acumulado = params["acumulado"]

    def paso(self, i):
        """El paso i entero (barra + rotulos), para animarlo solo."""
        i = int(i)
        if i < 0 or i >= len(self.barras):
            raise ValueError(f"paso: {i} fuera de 0..{len(self.barras) - 1}")
        return VGroup(self.barras[i], self.nombres[i], self.valores[i])


def barra_enlace(Pt_dbm=30.0, Gt=None, fspl=None, Gr=None, perdidas_db=0.0,
                 ancho=6.4, alto=3.0, nota=True):
    """El presupuesto optico como cascada de barras (waterfall).

    Cada barra arranca donde acabo la anterior: Pt sube desde 0 dBm,
    +Gt sube, -FSPL se hunde y +Gr vuelve a subir; la quinta barra, en
    cian, es el resultado Pr medido desde 0. Por omision los valores son
    los del curso (`Gt=Gr=ganancia_dbi(0.10, 1550 nm)=106.14 dBi`,
    `fspl=fspl_db(5000 km, 1550 nm)=272.16 dB`), de modo que
    `barra_enlace()` da Pr = -29.88 dBm ~ 1.03 uW.

    Se rotula "presupuesto ideal" a proposito: no hay perdidas opticas
    ni de apuntado (van en `perdidas_db` si el clip las quiere).
    """
    ancho = _positivo("barra_enlace.ancho", ancho)
    alto = _positivo("barra_enlace.alto", alto)
    Gt = ganancia_dbi(0.10, LAMBDA_ISL) if Gt is None else float(Gt)
    Gr = ganancia_dbi(0.10, LAMBDA_ISL) if Gr is None else float(Gr)
    fspl = fspl_db(5000e3, LAMBDA_ISL) if fspl is None else float(fspl)
    Pt_dbm = float(Pt_dbm)
    perdidas_db = float(perdidas_db)

    incrementos = [Pt_dbm, Gt, -fspl, Gr]
    if perdidas_db:
        incrementos.append(-perdidas_db)
    acumulado, s = [], 0.0
    for inc in incrementos:
        s += inc
        acumulado.append(s)
    pr = s

    etiquetas = ["Pt", "+Gt", "-FSPL", "+Gr"]
    if perdidas_db:
        etiquetas.append("-perd")
    textos = [f"{Pt_dbm:.0f} dBm", f"{Gt:.1f} dB", f"{fspl:.1f} dB",
              f"{Gr:.1f} dB"]
    if perdidas_db:
        textos.append(f"{perdidas_db:.1f} dB")
    colores = [COLOR_HAZ, COLOR_OBJETO, COLOR_ONDA, COLOR_OBJETO]
    if perdidas_db:
        colores.append(COLOR_ONDA)

    y_max = max(max(acumulado), 0.0)
    y_min = min(min(acumulado), 0.0)
    escala = alto / max(y_max - y_min, _EPS)
    y0 = -(y_max + y_min) / 2.0 * escala      # y de escena del 0 dBm

    n = len(incrementos) + 1
    paso_x = ancho / n
    ancho_barra = paso_x * 0.60
    x0 = -ancho / 2.0

    eje_cero = DashedLine(np.array([x0, y0, 0.0]),
                          np.array([x0 + ancho, y0, 0.0]),
                          stroke_width=1.4, color=COLOR_EJE,
                          dash_length=0.10)

    barras, nombres, valores = VGroup(), VGroup(), VGroup()
    y_nom = alto / 2.0 + 0.34
    y_val = -alto / 2.0 - 0.34
    previo = 0.0
    for i, inc in enumerate(incrementos):
        x = x0 + (i + 0.5) * paso_x
        ya, yb = y0 + previo * escala, y0 + acumulado[i] * escala
        h = max(abs(yb - ya), 0.02)
        b = Rectangle(width=ancho_barra, height=h, stroke_width=1.2,
                      color=colores[i])
        b.set_fill(colores[i], opacity=0.80)
        b.move_to(np.array([x, (ya + yb) / 2.0, 0.0]))
        barras.add(b)
        nombres.add(_texto_hud(etiquetas[i], font_size=15,
                               color=colores[i]).move_to(
            np.array([x, y_nom, 0.0])))
        valores.add(_texto_hud(textos[i], font_size=13,
                               color=CODE_MUTED).move_to(
            np.array([x, y_val, 0.0])))
        previo = acumulado[i]

    # La quinta barra: el resultado, medido desde 0 dBm.
    x = x0 + (n - 0.5) * paso_x
    yb = y0 + pr * escala
    b = Rectangle(width=ancho_barra, height=max(abs(yb - y0), 0.02),
                  stroke_width=1.6, color=COLOR_MEDIDA)
    b.set_fill(COLOR_MEDIDA, opacity=0.85)
    b.move_to(np.array([x, (y0 + yb) / 2.0, 0.0]))
    barras.add(b)
    nombres.add(_texto_hud("= Pr", font_size=15,
                           color=COLOR_MEDIDA).move_to(
        np.array([x, y_nom, 0.0])))
    valores.add(_texto_hud(f"{pr:.1f} dBm", font_size=13,
                           color=COLOR_MEDIDA).move_to(
        np.array([x, y_val, 0.0])))

    nota_g = VGroup()
    if nota:
        t = _texto_hud("presupuesto ideal", font_size=12, color=CODE_MUTED)
        t.move_to(np.array([x0 + 0.05, y_val - 0.34, 0.0]),
                  aligned_edge=LEFT)
        nota_g.add(t)

    params = {"ancho": ancho, "alto": alto, "pr_dbm": pr,
              "acumulado": [float(v) for v in acumulado],
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    return BarraEnlace(a_a, a_b, eje_cero, barras, nombres, valores, nota_g,
                       params)


# =====================================================================
# 3.1 / 3.4 — Radio contra optico
# =====================================================================
class ComparadorRfOptico(_Pieza):
    """Dos columnas comparables: antena de radio y telescopio optico.

    Publico: `.columna_rf`, `.columna_optica`, `.etiquetas`, `.filas`
    (dict nombre -> VGroup de la fila), `.datos` (dict nombre -> (rf,
    optico) en texto). `.fila(nombre)` devuelve la fila entera.
    """

    def __init__(self, ancla_a, ancla_b, marco, etiquetas, columna_rf,
                 columna_optica, params, **kwargs):
        super().__init__(ancla_a, ancla_b, marco, etiquetas, columna_rf,
                         columna_optica, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.marco = marco
        self.etiquetas = etiquetas
        self.columna_rf = columna_rf
        self.columna_optica = columna_optica
        self._params = params
        self.filas = params["filas"]
        self.datos = params["datos"]

    def fila(self, nombre):
        """La fila entera (etiqueta + celda RF + celda optica)."""
        clave = str(nombre)
        if clave not in self.filas:
            raise ValueError(f"fila: '{clave}' no esta en "
                             f"{sorted(self.filas)}")
        return self.filas[clave]


def comparador_rf_optico(D_rf=1.0, f_rf=30e9, D_opt=0.10,
                         lam_opt=LAMBDA_ISL, R_km=5000.0, ancho=6.6,
                         alto=4.0):
    """Antena de radio de 1 m a 30 GHz contra telescopio de 10 cm a
    1550 nm, con la MISMA formula de apertura para las dos.

    Filas (claves de `.fila`): "apertura", "lambda", "ganancia",
    "ancho de haz", "huella". La ganancia sale de `ganancia_apertura`
    (49.9 dBi contra 106.1 dBi: 56 dB de regalo) y el ancho de haz de
    `divergencia_gauss(lam, D/2)` (6.36 mrad contra 9.87 urad), que a
    5000 km son 63.6 km de huella contra 98.7 m. Ese es el trato: el
    laser regala ganancia y la cobra en punteria.
    """
    ancho = _positivo("comparador_rf_optico.ancho", ancho)
    alto = _positivo("comparador_rf_optico.alto", alto)
    D_rf = _positivo("comparador_rf_optico.D_rf", D_rf)
    D_opt = _positivo("comparador_rf_optico.D_opt", D_opt)
    lam_rf = longitud_de_onda_de(f_rf)
    lam_opt = _positivo("comparador_rf_optico.lam_opt", lam_opt)
    R = _positivo("comparador_rf_optico.R_km", R_km) * 1e3

    g_rf, g_opt = ganancia_dbi(D_rf, lam_rf), ganancia_dbi(D_opt, lam_opt)
    th_rf = divergencia_gauss(lam_rf, D_rf / 2.0)
    th_opt = divergencia_gauss(lam_opt, D_opt / 2.0)
    h_rf, h_opt = huella(th_rf, R), huella(th_opt, R)

    datos = {
        "apertura": (f"{D_rf:.2f} m", f"{D_opt:.2f} m"),
        "lambda": (f"{lam_rf * 1e3:.2f} mm", f"{lam_opt * 1e9:.0f} nm"),
        "ganancia": (f"{g_rf:.1f} dBi", f"{g_opt:.1f} dBi"),
        "ancho de haz": (f"{th_rf * 1e3:.2f} mrad",
                         f"{th_opt * 1e6:.2f} urad"),
        "huella": (f"{h_rf / 1e3:.1f} km", f"{h_opt:.1f} m"),
    }
    orden = ["apertura", "lambda", "ganancia", "ancho de haz", "huella"]

    x_et = -ancho / 2.0 + 0.10
    x_rf = -0.30
    x_opt = ancho / 2.0 - 1.15
    y_icono = alto / 2.0 - 0.70
    y_cab = alto / 2.0 - 0.16
    y0 = y_icono - 1.05
    paso_y = 0.56

    marco = VGroup()
    sep = Line(np.array([x_et - 0.06, y0 + 0.34, 0.0]),
               np.array([ancho / 2.0 - 0.06, y0 + 0.34, 0.0]),
               stroke_width=1.4, color=COLOR_EJE)
    marco.add(sep)
    marco.add(Line(np.array([(x_rf + x_opt) / 2.0, y_cab + 0.16, 0.0]),
                   np.array([(x_rf + x_opt) / 2.0,
                             y0 - (len(orden) - 0.4) * paso_y, 0.0]),
                   stroke_width=1.2, color=COLOR_EJE).set_stroke(opacity=0.6))

    # Iconos: parabola verde (radio) y telescopio rojo (optico).
    foco = np.array([x_rf - 0.12, y_icono, 0.0])
    parabola = Arc(radius=0.42, start_angle=PI - 0.95, angle=1.90,
                   stroke_width=2.8, color=COLOR_OBJETO)
    parabola.move_arc_center_to(foco)
    feed = Line(foco, foco + RIGHT * 0.34, stroke_width=1.8,
                color=COLOR_OBJETO)
    icono_rf = VGroup(parabola, feed,
                      Dot(foco + RIGHT * 0.34, radius=0.055,
                          color=COLOR_OBJETO))
    icono_opt = _telescopio(1.25, COLOR_HAZ)
    icono_opt.move_to(np.array([x_opt, y_icono, 0.0]))

    cab_rf = _texto_hud("RADIO 30 GHz", font_size=16, color=COLOR_OBJETO)
    cab_rf.move_to(np.array([x_rf, y_cab, 0.0]))
    cab_opt = _texto_hud("OPTICO 1550 nm", font_size=16, color=COLOR_HAZ)
    cab_opt.move_to(np.array([x_opt, y_cab, 0.0]))

    etiquetas, celdas_rf, celdas_opt = VGroup(), VGroup(), VGroup()
    filas = {}
    for i, nombre in enumerate(orden):
        y = y0 - i * paso_y
        et = _texto_hud(nombre, font_size=14, color=CODE_MUTED)
        et.move_to(np.array([x_et, y, 0.0]), aligned_edge=LEFT)
        v_rf = _texto_hud(datos[nombre][0], font_size=17, color=COLOR_MEDIDA)
        v_rf.move_to(np.array([x_rf, y, 0.0]))
        v_opt = _texto_hud(datos[nombre][1], font_size=17, color=COLOR_MEDIDA)
        v_opt.move_to(np.array([x_opt, y, 0.0]))
        etiquetas.add(et)
        celdas_rf.add(v_rf)
        celdas_opt.add(v_opt)
        filas[nombre] = VGroup(et, v_rf, v_opt)

    columna_rf = VGroup(cab_rf, icono_rf, celdas_rf)
    columna_optica = VGroup(cab_opt, icono_opt, celdas_opt)

    params = {"ancho": ancho, "alto": alto, "filas": filas, "datos": datos,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    return ComparadorRfOptico(a_a, a_b, marco, etiquetas, columna_rf,
                              columna_optica, params)


# =====================================================================
# 3.2 — Punteria: un microradian son cinco metros
# =====================================================================
class Punteria(_Pieza):
    """El plano del receptor visto de frente: el satelite en el centro,
    su anillo de tolerancia y la huella del haz, que se corre con el
    error de apuntado.

    Publico: `.receptor`, `.anillo`, `.huella_circulo`, `.rotulo`,
    `.error_urad`, `.offset_m`, `.radio_huella_m`, `.escala_m`
    (unidades de escena por metro).
    """

    def __init__(self, ancla_a, ancla_b, anillo, huella_circulo, receptor,
                 rotulo, params, **kwargs):
        super().__init__(ancla_a, ancla_b, anillo, huella_circulo, receptor,
                         rotulo, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.anillo = anillo
        self.huella_circulo = huella_circulo
        self.receptor = receptor
        self.rotulo = rotulo
        self._params = params
        self.error_urad = params["error_urad"]
        self.offset_m = params["offset_m"]
        self.radio_huella_m = params["radio_huella_m"]
        self.escala_m = params["escala_m"]

    def centro(self):
        """Punto de escena del receptor (el centro del blanco)."""
        return self.receptor.get_center()

    def a_error(self, urad, direccion=(1.0, 0.35)):
        """MUTA: corre la huella el desplazamiento que produce ese error
        de apuntado y reescribe el rotulo. Devuelve `self`.

        El desplazamiento sale de `desplazamiento_por_jitter(theta, R)`:
        1 urad a 5000 km son 5.0 m. La escala del dibujo es
        `escala_m` unidades de escena por metro (fijada para que la
        huella de 98.7 m de diametro mida `ancho * 0.60`), asi que aqui
        SI hay proporcion: 10 urad se ven diez veces mas lejos que 1.
        `direccion` es hacia donde se corre (se normaliza).
        """
        urad = float(urad)
        if urad < 0.0:
            raise ValueError(f"a_error: {urad} urad < 0")
        p = self._params
        d_m = desplazamiento_por_jitter(urad * 1e-6, p["R_km"] * 1e3)
        u = _v3(direccion)
        norma = float(np.linalg.norm(u))
        if norma <= 0.0:
            raise ValueError("a_error: direccion nula")
        u = u / norma
        local = d_m * p["escala_m"] * u
        self.huella_circulo.move_to(self._punto(local))
        self.error_urad = urad
        self.offset_m = d_m
        p["error_urad"], p["offset_m"] = urad, d_m
        estado = "ACIERTA" if self.acierta() else "FALLA"
        color = COLOR_OBJETO if self.acierta() else COLOR_HAZ
        nuevo = VGroup(
            _texto_hud(f"error {urad:.1f} urad", font_size=16,
                       color=COLOR_MEDIDA),
            _texto_hud(f"= {d_m:.1f} m", font_size=16, color=COLOR_MEDIDA),
            _texto_hud(estado, font_size=15, color=color))
        nuevo.arrange(DOWN, buff=0.10, aligned_edge=LEFT)
        nuevo.scale(self._escala_actual())
        nuevo.move_to(self._punto(p["p_rotulo"]), aligned_edge=LEFT)
        self.remove(self.rotulo)
        self.add(nuevo)
        self.rotulo = nuevo
        return self

    def con_error(self, urad, direccion=(1.0, 0.35)):
        """Igual que `a_error` (MUTA y devuelve `self`).

        OJO, excepcion a la convencion del modulo: aqui `con_*` no
        fabrica una gemela — el contrato del curso pide que mueva la
        huella. Usa `a_error` si prefieres el nombre coherente.
        """
        return self.a_error(urad, direccion)

    def acierta(self):
        """True si el receptor sigue DENTRO de la huella, es decir si el
        desplazamiento no supera el radio del haz (49.34 m con 9.87 urad
        a 5000 km). 1 urad -> 5.0 m: acierta. 10 urad -> 50.0 m: falla
        por 66 centimetros."""
        return bool(self.offset_m <= self.radio_huella_m)


def punteria(R_km=5000.0, theta_urad=9.87, error_urad=1.0, ancho=5.2):
    """El blanco visto desde el haz: receptor verde al centro, anillo de
    tolerancia y la huella violeta que se corre con el error.

    El anillo de tolerancia ES el borde de la huella centrada: mientras
    el receptor quede dentro del circulo violeta, el enlace vive.

    ESCALA (esta si es proporcional): el diametro de la huella
    (`huella(theta, R)` = 98.7 m con los valores del curso) ocupa el
    60 % de `ancho`; de ahi sale `escala_m` en unidades de escena por
    metro. Con eso, 1 urad (5 m) es un empujon pequeno y 10 urad (50 m)
    se sale.
    """
    ancho = _positivo("punteria.ancho", ancho)
    R_km = _positivo("punteria.R_km", R_km)
    theta_urad = _positivo("punteria.theta_urad", theta_urad)

    huella_m = huella(theta_urad * 1e-6, R_km * 1e3)
    radio_huella_m = huella_m / 2.0
    radio_escena = 0.30 * ancho
    escala_m = radio_escena / radio_huella_m

    anillo = DashedVMobject(Circle(radius=radio_escena, stroke_width=2.0,
                                   color=COLOR_OBJETO), num_dashes=40)
    anillo.set_stroke(opacity=0.7)

    circulo = Circle(radius=radio_escena, stroke_width=2.4,
                     color=COLOR_FRANJA)
    circulo.set_fill(COLOR_FRANJA, opacity=0.18)

    receptor = _satelite(1.7, COLOR_OBJETO)

    p_rotulo = np.array([-ancho / 2.0 + 0.06, -0.42 * ancho, 0.0])
    params = {"ancho": ancho, "R_km": R_km, "theta_urad": theta_urad,
              "huella_m": huella_m, "radio_huella_m": radio_huella_m,
              "escala_m": escala_m, "error_urad": 0.0, "offset_m": 0.0,
              "p_rotulo": p_rotulo,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = Punteria(a_a, a_b, anillo, circulo, receptor, VGroup(), params)
    pieza.a_error(error_urad)
    return pieza


# =====================================================================
# 3.2 — Apuntar adonde ESTARA
# =====================================================================
class AdelantoApuntado(_Pieza):
    """Emisor a la izquierda, receptor a la derecha subiendo; el haz
    "ingenuo" apunta a donde el receptor SE VE y el adelantado a donde
    ESTARA cuando la luz llegue.

    Publico: `.emisor`, `.receptor`, `.fantasma`, `.haz_ingenuo`,
    `.haz_adelantado`, `.rotulo`, `.marcas` (los HUD "ahora"/"estara"),
    `.adelanto_urad`, `.offset_m`, `.t_luz_s`, `.frac`.
    """

    def __init__(self, ancla_a, ancla_b, carril, haz_ingenuo,
                 haz_adelantado, emisor, fantasma, receptor, rotulo, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, carril, haz_ingenuo,
                         haz_adelantado, fantasma, emisor, receptor, rotulo,
                         **kwargs)
        self.marcas = VGroup()
        self.add(self.marcas)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.carril = carril
        self.haz_ingenuo = haz_ingenuo
        self.haz_adelantado = haz_adelantado
        self.emisor = emisor
        self.fantasma = fantasma
        self.receptor = receptor
        self.rotulo = rotulo
        self._params = params
        self.adelanto_urad = params["adelanto_urad"]
        self.offset_m = params["offset_m"]
        self.t_luz_s = params["t_luz_s"]
        self.frac = params["frac"]

    def a_t(self, frac):
        """MUTA: coloca el receptor en `frac` de su recorrido (0..1) y
        rehace los dos haces. Devuelve `self`.

        `frac` es la fraccion del tramo vertical dibujado, no segundos:
        el movimiento real (7.6 km/s durante los 16.7 ms que tarda la
        luz en 5000 km) son 127 metros, invisibles al lado de 5000 km.
        """
        frac = float(frac)
        if frac < 0.0 or frac > 1.0:
            raise ValueError(f"a_t: frac={frac} fuera de 0..1")
        p = self._params
        y = p["y0"] + frac * (p["y1"] - p["y0"])
        p_ahora = np.array([p["x_rx"], y, 0.0])
        p_futuro = np.array([p["x_rx"], y + p["salto"], 0.0])
        self.receptor.move_to(self._punto(p_ahora))
        self.fantasma.move_to(self._punto(p_futuro))
        origen = self._punto(np.array([p["x_tx"], 0.0, 0.0]))
        # El haz ingenuo se REHACE (un DashedLine estirado con
        # put_start_and_end_on deja los guiones deformados).
        nuevo = DashedLine(origen, self._punto(p_ahora), stroke_width=2.0,
                           color=COLOR_HAZ,
                           dash_length=0.11 * self._escala_actual())
        nuevo.set_stroke(opacity=0.45)
        self.remove(self.haz_ingenuo)
        self.add_to_back(nuevo)
        self.haz_ingenuo = nuevo
        self.haz_adelantado.put_start_and_end_on(origen,
                                                 self._punto(p_futuro))
        esc = self._escala_actual()
        marcas = VGroup()
        for texto, mob, signo, color in (
                ("estara", self.fantasma, +1.0, COLOR_OBJETO),
                ("ahora", self.receptor, -1.0, CODE_MUTED)):
            t = _texto_hud(texto, font_size=13, color=color)
            t.scale(esc)
            t.move_to(mob.get_center()
                      + UP * signo * (mob.height / 2.0 + 0.20 * esc))
            marcas.add(t)
        self.remove(self.marcas)
        self.add(marcas)
        self.marcas = marcas
        self.frac = frac
        p["frac"] = frac
        return self


def adelanto_apuntado(v_kms=V_LEO_KMS, R_km=5000.0, ancho=6.4, alto=3.2,
                      salto=0.85, frac=0.35):
    """El receptor se mueve mientras la luz viaja: hay que apuntar
    adonde ESTARA.

    El angulo sale de `angulo_adelanto(v)` = 2 v / c: a 7.6 km/s son
    50.70 urad, que a 5000 km valen 253.5 m de desvio — CINCO veces la
    divergencia de 9.87 urad. Por eso el emisor no apunta a la imagen
    que ve (haz punteado) sino por delante (haz solido), hacia el
    fantasma verde.

    EXAGERACION (documentada): el desvio en pantalla es el `salto` fijo
    (0.85 unidades por omision), no proporcional — a escala real serian
    5e-5 unidades.
    """
    ancho = _positivo("adelanto_apuntado.ancho", ancho)
    alto = _positivo("adelanto_apuntado.alto", alto)
    v = _positivo("adelanto_apuntado.v_kms", v_kms) * 1e3
    R = _positivo("adelanto_apuntado.R_km", R_km) * 1e3
    salto = _positivo("adelanto_apuntado.salto", salto)

    adelanto = angulo_adelanto(v)
    offset_m = adelanto * R
    t_luz = tiempo_luz(R)

    x_tx, x_rx = -ancho / 2.0 + 0.35, ancho / 2.0 - 0.75
    y0, y1 = -alto / 2.0 + 0.25, alto / 2.0 - 0.85

    carril = DashedLine(np.array([x_rx, y0, 0.0]),
                        np.array([x_rx, y1 + salto, 0.0]),
                        stroke_width=1.2, color=COLOR_EJE, dash_length=0.09)

    emisor = _telescopio(1.3, COLOR_HAZ)
    emisor.move_to(np.array([x_tx - 0.28, 0.0, 0.0]))
    receptor = _satelite(1.6, COLOR_OBJETO)
    fantasma = _satelite(1.6, COLOR_OBJETO)
    fantasma.set_stroke(opacity=0.40)
    fantasma.set_fill(opacity=0.06)

    haz_ingenuo = DashedLine(ORIGIN, RIGHT, stroke_width=2.0,
                             color=COLOR_HAZ, dash_length=0.10)
    haz_ingenuo.set_stroke(opacity=0.45)
    haz_adelantado = Line(ORIGIN, RIGHT, stroke_width=2.6, color=COLOR_HAZ)

    rotulo = VGroup(
        _texto_hud(f"v = {v_kms:.1f} km/s", font_size=15, color=CODE_MUTED),
        _texto_hud(f"2v/c = {adelanto * 1e6:.2f} urad", font_size=17,
                   color=COLOR_MEDIDA),
        _texto_hud(f"= {offset_m:.1f} m a {R_km:.0f} km", font_size=15,
                   color=COLOR_MEDIDA),
        _texto_hud(f"luz: {t_luz * 1e3:.1f} ms", font_size=14,
                   color=CODE_MUTED))
    rotulo.arrange(DOWN, buff=0.11, aligned_edge=LEFT)
    rotulo.move_to(np.array([-ancho / 2.0 + 0.06, -alto / 2.0 - 0.40, 0.0]),
                   aligned_edge=LEFT)

    params = {"ancho": ancho, "alto": alto, "x_tx": x_tx, "x_rx": x_rx,
              "y0": y0, "y1": y1, "salto": salto, "frac": float(frac),
              "adelanto_urad": adelanto * 1e6, "offset_m": offset_m,
              "t_luz_s": t_luz,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = AdelantoApuntado(a_a, a_b, carril, haz_ingenuo, haz_adelantado,
                             emisor, fantasma, receptor, rotulo, params)
    pieza.a_t(frac)
    return pieza


# =====================================================================
# 3.2 — La espiral de adquisicion
# =====================================================================
class EspiralAdquisicion(_Pieza):
    """La busqueda: el haz barre en espiral la region de incertidumbre
    hasta cubrir el faro del otro satelite.

    Publico: `.region`, `.traza` (la polilinea), `.puntos_vista`
    (VGroup de Dots), `.faro`, `.haz` (circulo violeta del haz),
    `.rotulo`, `.puntos` (array (N,2) local), `.n_puntos`,
    `.k_encuentro` (indice MEDIDO del primer punto que cubre el faro, o
    None), `.paso_actual`.
    """

    def __init__(self, ancla_a, ancla_b, region, traza, puntos_vista, haz,
                 faro, rotulo, params, **kwargs):
        super().__init__(ancla_a, ancla_b, region, traza, puntos_vista, haz,
                         faro, rotulo, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.region = region
        self.traza = traza
        self.puntos_vista = puntos_vista
        self.haz = haz
        self.faro = faro
        self.rotulo = rotulo
        self._params = params
        self.puntos = params["puntos"]
        self.n_puntos = len(params["puntos"])
        self.k_encuentro = params["k_encuentro"]
        self.paso_actual = params["paso_actual"]

    def punto(self, k):
        """Punto de escena del paso k, sobre la geometria ACTUAL."""
        k = _validar("punto.k", int(k) + 1, self.n_puntos) - 1
        return self._punto(self.puntos[k])

    def a_paso(self, k):
        """MUTA: deja visibles solo los k primeros pasos (la traza se
        recorta y el circulo del haz se planta en el paso k). Devuelve
        `self`.

        k va de 0 (solo el centro) a `n_puntos - 1`.
        """
        k = int(k)
        if k < 0 or k >= self.n_puntos:
            raise ValueError(f"a_paso: {k} fuera de 0..{self.n_puntos - 1}")
        esc = self._escala_actual()
        pts = np.array([self._punto(p) for p in self.puntos[:k + 1]])
        if len(pts) == 1:
            pts = np.vstack([pts, pts])
        self.traza.set_points_as_corners(pts)
        for i, d in enumerate(self.puntos_vista):
            d.set_opacity(0.85 if i <= k else 0.0)
        self.haz.move_to(self._punto(self.puntos[k]))
        self.paso_actual = k
        self._params["paso_actual"] = k
        nuevo = _texto_hud(
            f"paso {k:d}/{self.n_puntos - 1:d}"
            + ("  FARO" if self.encontrado() else ""),
            font_size=16,
            color=COLOR_OBJETO if self.encontrado() else COLOR_MEDIDA)
        nuevo.scale(esc)
        nuevo.move_to(self._punto(self._params["p_rotulo"]))
        self.remove(self.rotulo)
        self.add(nuevo)
        self.rotulo = nuevo
        return self

    def encontrado(self):
        """True si el haz YA cubrio el faro, es decir si el paso actual
        alcanzo `k_encuentro`. Simulacion determinista: no hay ruido ni
        deriva, solo geometria."""
        return bool(self.k_encuentro is not None
                    and self.paso_actual >= self.k_encuentro)


def espiral_adquisicion(paso=0.78, n_vueltas=3, faro_xy=(1.404, -0.858),
                        radio_incert=2.5, por_vuelta=24, radio_haz=None):
    """La espiral de busqueda sobre la region de incertidumbre.

    `paso` es lo que crece el radio en una vuelta y `radio_haz` el radio
    del haz en ese plano (por omision `paso/2`, que es lo que hace que
    dos vueltas seguidas se toquen sin dejar hueco). El faro (Dot verde)
    esta en `faro_xy`; el primer paso cuyo haz lo cubre se MIDE
    recorriendo la espiral y queda en `.k_encuentro`.

    Con los valores por omision: 73 puntos, el faro a radio 1.645 y
    `k_encuentro = 46`. Todo en unidades de escena (la pieza mide
    2*`radio_incert` = 5.0 de ancho); en el cielo esas unidades serian
    microradianes.

    Se rotula "simulacion": la espiral es geometria pura, sin ruido de
    apuntado ni deriva orbital.
    """
    paso = _positivo("espiral_adquisicion.paso", paso)
    radio_incert = _positivo("espiral_adquisicion.radio_incert",
                             radio_incert)
    pts = espiral_busqueda(paso, n_vueltas, por_vuelta)
    r_haz = paso / 2.0 if radio_haz is None else _positivo(
        "espiral_adquisicion.radio_haz", radio_haz)
    faro = _v3(faro_xy)[:2]

    # MEDIDO: el primer paso cuyo haz cubre el faro.
    d = np.linalg.norm(pts - faro[None, :], axis=1)
    dentro = np.nonzero(d <= r_haz)[0]
    k_encuentro = int(dentro[0]) if len(dentro) else None

    ancho = 2.0 * radio_incert
    region = Circle(radius=radio_incert, stroke_width=1.6, color=COLOR_EJE)
    region.set_fill(COLOR_EJE, opacity=0.10)

    traza = VMobject(color=COLOR_HAZ, stroke_width=2.0)
    traza.set_points_as_corners(
        np.column_stack([pts, np.zeros(len(pts))]))

    puntos_vista = VGroup(*[
        Dot(np.array([p[0], p[1], 0.0]), radius=0.030, color=COLOR_HAZ)
        for p in pts])
    puntos_vista.set_opacity(0.85)

    haz = Circle(radius=r_haz, stroke_width=1.8, color=COLOR_FRANJA)
    haz.set_fill(COLOR_FRANJA, opacity=0.18)

    faro_dot = VGroup(
        Dot(np.array([faro[0], faro[1], 0.0]), radius=0.075,
            color=COLOR_OBJETO),
        Circle(radius=0.17, stroke_width=1.6,
               color=COLOR_OBJETO).move_to(
                   np.array([faro[0], faro[1], 0.0])).set_stroke(opacity=0.6))

    p_rotulo = np.array([0.0, -radio_incert - 0.30, 0.0])
    params = {"ancho": ancho, "puntos": pts, "k_encuentro": k_encuentro,
              "paso_actual": len(pts) - 1, "radio_haz": r_haz,
              "p_rotulo": p_rotulo,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = EspiralAdquisicion(a_a, a_b, region, traza, puntos_vista, haz,
                               faro_dot, VGroup(), params)
    pieza.a_paso(len(pts) - 1)
    return pieza


# =====================================================================
# 3.2 — El detector de cuadrantes
# =====================================================================
class DetectorCuadrantes(_Pieza):
    """Cuadrado partido en cuatro (A, B, C, D) con la mancha del haz y
    las dos barras de senal.

    Publico: `.cuadro`, `.cruz`, `.letras`, `.mancha`, `.barra_x`,
    `.barra_y`, `.lectura`, `.x`, `.y`, `.w`. OJO: las DOS barras son
    HORIZONTALES (apiladas a la derecha, ex arriba y ey abajo), asi que
    `barra_y.width` es la que mide la senal vertical.
    """

    def __init__(self, ancla_a, ancla_b, cuadro, cruz, letras, ejes_barra,
                 barra_x, barra_y, mancha, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, cuadro, cruz, letras, ejes_barra,
                         barra_x, barra_y, mancha, lectura, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.cuadro = cuadro
        self.cruz = cruz
        self.letras = letras
        self.ejes_barra = ejes_barra
        self.barra_x = barra_x
        self.barra_y = barra_y
        self.mancha = mancha
        self.lectura = lectura
        self._params = params
        self.x = params["x"]
        self.y = params["y"]
        self.w = params["w"]

    def senales(self):
        """(ex, ey) del detector con la mancha donde este AHORA, via
        `error_cuadrante`. Centrada da (0.0, 0.0); a un radio w en x da
        (0.954, 0.0)."""
        return error_cuadrante(self.x, self.y, self.w)

    def a_mancha(self, x, y):
        """MUTA: mueve la mancha a (x, y) —en unidades del detector, con
        el origen en el centro— y actualiza las dos barras y la lectura.
        Devuelve `self`."""
        p = self._params
        x, y = float(x), float(y)
        lim = p["lado"] / 2.0 + p["w"]
        if abs(x) > lim or abs(y) > lim:
            raise ValueError(f"a_mancha: ({x}, {y}) se sale del detector "
                             f"(+-{lim:.2f})")
        self.x, self.y = x, y
        p["x"], p["y"] = x, y
        self.mancha.move_to(self._punto(p["centro"]
                                        + np.array([x, y, 0.0])))
        ex, ey = self.senales()
        esc = self._escala_actual()

        def _barra(valor, y_eje):
            largo = valor * p["semi_barra"]
            r = Rectangle(width=max(abs(largo), 1e-3) * esc,
                          height=p["grosor_barra"] * esc, stroke_width=0.6,
                          color=COLOR_MEDIDA)
            r.set_fill(COLOR_MEDIDA, opacity=0.85)
            r.move_to(self._punto(np.array([p["x_barra"] + largo / 2.0,
                                            y_eje, 0.0])))
            return r

        nueva_x = _barra(ex, p["y_ex"])
        nueva_y = _barra(ey, p["y_ey"])
        nueva_lec = VGroup()
        for valor, y_eje, nombre in ((ex, p["y_ex"], "ex"),
                                     (ey, p["y_ey"], "ey")):
            t = _texto_hud(f"{nombre} {valor:+.2f}", font_size=15,
                           color=COLOR_MEDIDA)
            t.scale(esc)
            t.move_to(self._punto(np.array([p["x_barra"],
                                            y_eje + p["dy_lectura"], 0.0])))
            nueva_lec.add(t)

        for viejo, nuevo, campo in ((self.barra_x, nueva_x, "barra_x"),
                                    (self.barra_y, nueva_y, "barra_y"),
                                    (self.lectura, nueva_lec, "lectura")):
            self.remove(viejo)
            self.add(nuevo)
            setattr(self, campo, nuevo)
        return self

    def con_mancha(self, x, y):
        """Igual que `a_mancha` (MUTA y devuelve `self`).

        OJO, excepcion a la convencion del modulo: el contrato del curso
        pide que `con_mancha` MUEVA la mancha, no que fabrique una
        gemela."""
        return self.a_mancha(x, y)


def detector_cuadrantes(w=0.55, lado=2.6, x=0.0, y=0.0, ancho=6.4):
    """Los cuatro cuadrantes, la mancha del haz y las dos senales.

    `lado` es el lado del detector y `w` el radio 1/e^2 de la mancha
    gaussiana, ambos en unidades del propio detector. Los cuadrantes van
    A (arriba-izq), B (arriba-der), C (abajo-izq), D (abajo-der), que es
    el convenio de `error_cuadrante`: ex = (B+D-A-C)/total,
    ey = (A+B-C-D)/total.

    Las dos barras cian de la derecha (ex arriba, ey abajo) son esas
    senales a escala +-1, con su cifra encima. Es el lazo que "sigue sin
    temblar": la mancha se sale, el voltaje lo dice, el espejo rapido la
    devuelve al centro.
    """
    lado = _positivo("detector_cuadrantes.lado", lado)
    w = _positivo("detector_cuadrantes.w", w)
    ancho = _positivo("detector_cuadrantes.ancho", ancho)

    x_det = -ancho / 2.0 + lado / 2.0 + 0.15
    centro = np.array([x_det, 0.0, 0.0])

    cuadro = Rectangle(width=lado, height=lado, stroke_width=2.0,
                       color=COLOR_EJE)
    cuadro.set_fill(COLOR_EJE, opacity=0.12)
    cuadro.move_to(centro)
    cruz = VGroup(
        Line(centro + LEFT * lado / 2.0, centro + RIGHT * lado / 2.0,
             stroke_width=1.6, color=COLOR_EJE),
        Line(centro + DOWN * lado / 2.0, centro + UP * lado / 2.0,
             stroke_width=1.6, color=COLOR_EJE))

    letras = VGroup()
    for nombre, sx, sy in (("A", -1, 1), ("B", 1, 1), ("C", -1, -1),
                           ("D", 1, -1)):
        t = _texto_hud(nombre, font_size=18, color=CODE_MUTED)
        t.move_to(centro + np.array([sx * lado * 0.37, sy * lado * 0.37,
                                     0.0]))
        letras.add(t)

    mancha = VGroup(
        Circle(radius=w, stroke_width=1.6, color=COLOR_FRANJA).set_fill(
            COLOR_FRANJA, opacity=0.30),
        Circle(radius=w * 0.45, stroke_width=0.0,
               color=COLOR_FRANJA).set_fill(COLOR_FRANJA, opacity=0.55))

    # Las dos senales, en barras HORIZONTALES apiladas a la derecha del
    # detector: se leen de un vistazo y no pisan los cuadrantes.
    semi_barra = 0.95
    grosor = 0.22
    x_barra = x_det + lado / 2.0 + 1.45        # cero de las dos barras
    y_ex, y_ey = 0.62, -0.62
    dy_lectura = 0.34

    ejes_barra = VGroup()
    for y_eje, nombre in ((y_ex, "ex"), (y_ey, "ey")):
        ejes_barra.add(
            Line(np.array([x_barra - semi_barra, y_eje, 0.0]),
                 np.array([x_barra + semi_barra, y_eje, 0.0]),
                 stroke_width=1.2, color=COLOR_EJE),
            Line(np.array([x_barra, y_eje - grosor * 0.9, 0.0]),
                 np.array([x_barra, y_eje + grosor * 0.9, 0.0]),
                 stroke_width=1.6, color=COLOR_EJE),
            _texto_hud(nombre, font_size=14, color=CODE_MUTED).move_to(
                np.array([x_barra - semi_barra - 0.34, y_eje, 0.0])))

    params = {"ancho": ancho, "lado": lado, "w": w, "x": 0.0, "y": 0.0,
              "semi_barra": semi_barra, "grosor_barra": grosor,
              "x_barra": x_barra, "y_ex": y_ex, "y_ey": y_ey,
              "dy_lectura": dy_lectura, "centro": centro,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = DetectorCuadrantes(a_a, a_b, cuadro, cruz, letras, ejes_barra,
                               VGroup(), VGroup(), mancha, VGroup(), params)
    pieza.a_mancha(x, y)
    return pieza


# =====================================================================
# 3.3 — GRACE-FO: la masa que los separa
# =====================================================================
class GracePar(_Pieza):
    """Dos satelites en fila sobre un arco de Tierra con una masa que
    pasa por debajo y les cambia la distancia.

    Publico: `.tierra`, `.masa`, `.a`, `.b`, `.laser`, `.rotulo`,
    `.sep_km`, `.amplitud_nm`, `.frac`.
    """

    def __init__(self, ancla_a, ancla_b, tierra, masa, laser, sat_a, sat_b,
                 rotulo, params, **kwargs):
        super().__init__(ancla_a, ancla_b, tierra, masa, laser, sat_a,
                         sat_b, rotulo, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.tierra = tierra
        self.masa = masa
        self.laser = laser
        self.a = sat_a
        self.b = sat_b
        self.rotulo = rotulo
        self._params = params
        self.sep_km = params["sep_km"]
        self.amplitud_nm = params["amplitud_nm"]
        self.frac = params["frac"]

    def _delta_bruto(self, frac):
        """Senal cruda: g(u_a) - g(u_b) con g gaussiana. Antisimetrica en
        el tiempo, que es la firma clasica de GRACE."""
        p = self._params
        x_m = p["x_masa0"] + float(frac) * (p["x_masa1"] - p["x_masa0"])
        sig = p["sigma"]
        ua = (p["x_a"] - x_m) / sig
        ub = (p["x_b"] - x_m) / sig
        return math.exp(-0.5 * ua * ua) - math.exp(-0.5 * ub * ub), x_m

    def delta_nm(self):
        """Cambio de distancia entre los dos satelites, en nanometros,
        para el `frac` actual.

        MODELO (declarado): la masa tira mas del satelite que tiene mas
        cerca, asi que la senal es la DIFERENCIA de dos gaussianas
        centradas en cada satelite,
            delta(t) = A * [exp(-ua^2/2) - exp(-ub^2/2)],
        normalizada para que su maximo en el recorrido sea exactamente
        `amplitud_nm` (1 nm por omision, el orden de magnitud publicado
        del LRI de GRACE-FO). No es una simulacion de gravedad: es la
        FORMA de la senal, que es lo que cuenta el clip.
        """
        bruto, _ = self._delta_bruto(self.frac)
        return self._params["amplitud_nm"] * bruto / self._params["norma"]

    def distancia(self):
        """Distancia actual entre los satelites, en km.

        Es `sep_km` mas `delta_nm()` convertido a km: 220 km mas un
        nanometro. En un float de 64 bits ese nanometro sobrevive por los
        pelos (4.5e-15 relativo, ~20 veces el epsilon), pero para
        ROTULAR usa `delta_nm()`, que es el numero del que habla el clip.
        """
        return self.sep_km + self.delta_nm() * 1e-12

    def a_t(self, frac):
        """MUTA: mueve la masa por debajo, separa/acerca los satelites y
        reescribe el rotulo. Devuelve `self`.

        `frac` en [0, 1] recorre la pasada completa de la masa.
        EXAGERACION (documentada): en pantalla los satelites se mueven
        `escala_visual` (0.30 unidades) por nanometro; el factor real
        seria 3e14, asi que el temblor del dibujo es puro didactismo.
        """
        frac = float(frac)
        if frac < 0.0 or frac > 1.0:
            raise ValueError(f"a_t: frac={frac} fuera de 0..1")
        p = self._params
        self.frac = frac
        p["frac"] = frac
        _, x_m = self._delta_bruto(frac)
        d_nm = self.delta_nm()
        empuje = p["escala_visual"] * d_nm / max(p["amplitud_nm"], _EPS)

        # La masa cabalga el limbo terrestre: su y sale del arco.
        y_m = (p["y_centro_tierra"]
               + math.sqrt(max(p["radio_tierra"] ** 2 - x_m * x_m, 0.0))
               + p["alza_masa"])
        self.masa.move_to(self._punto(np.array([x_m, y_m, 0.0])))
        pa = np.array([p["x_a"] - empuje / 2.0, p["y_sat"], 0.0])
        pb = np.array([p["x_b"] + empuje / 2.0, p["y_sat"], 0.0])
        self.a.move_to(self._punto(pa))
        self.b.move_to(self._punto(pb))
        self.laser.put_start_and_end_on(
            self.a.get_center() + RIGHT * 0.24 * self._escala_actual(),
            self.b.get_center() + LEFT * 0.24 * self._escala_actual())

        esc = self._escala_actual()
        nuevo = VGroup(
            _texto_hud(f"{self.sep_km:.0f} km", font_size=17,
                       color=CODE_MUTED),
            _texto_hud(f"delta {d_nm:+.2f} nm", font_size=19,
                       color=COLOR_MEDIDA))
        nuevo.arrange(DOWN, buff=0.10)
        nuevo.scale(esc)
        nuevo.move_to(self._punto(p["p_rotulo"]))
        self.remove(self.rotulo)
        self.add(nuevo)
        self.rotulo = nuevo
        return self


def grace_par(sep_km=SEP_GRACE_KM, amplitud_nm=1.0, ancho=6.4, alto=3.6,
              escala_visual=0.30, frac=0.5):
    """GRACE-FO: dos satelites en fila, un laser rojo entre ellos y una
    masa que pasa por debajo cambiandoles la distancia.

    El arco gris de abajo es la Tierra; el bulto ambar es la anomalia de
    masa (mas agua, mas hielo, una cordillera). El rotulo cian da los
    `sep_km` nominales y el `delta` en nanometros de `delta_nm()`.

    Ni los tamanos ni el delta estan a escala (ver `a_t` y `delta_nm`);
    la FORMA de la senal si es la que se publica: dos lobulos de signo
    contrario segun cual de los dos satelites tiene la masa mas cerca.
    """
    ancho = _positivo("grace_par.ancho", ancho)
    alto = _positivo("grace_par.alto", alto)
    sep_km = _positivo("grace_par.sep_km", sep_km)
    amplitud_nm = _positivo("grace_par.amplitud_nm", amplitud_nm)

    x_a, x_b = -1.35, 1.35
    y_sat = alto / 2.0 - 0.85
    y_masa = -alto / 2.0 + 0.28
    sigma = 1.15
    x_masa0, x_masa1 = -ancho / 2.0 + 0.35, ancho / 2.0 - 0.35

    # Normalizacion MEDIDA: el maximo de |g(ua) - g(ub)| en el recorrido.
    fr = np.linspace(0.0, 1.0, 401)
    xm = x_masa0 + fr * (x_masa1 - x_masa0)
    bruto = (np.exp(-0.5 * ((x_a - xm) / sigma) ** 2)
             - np.exp(-0.5 * ((x_b - xm) / sigma) ** 2))
    norma = float(np.max(np.abs(bruto)))

    radio_tierra = 7.0
    y_centro_tierra = y_masa - radio_tierra
    tierra = Arc(radius=radio_tierra, start_angle=PI / 2 - 0.42,
                 angle=0.84, stroke_width=2.4, color=COLOR_EJE)
    tierra.move_arc_center_to(np.array([0.0, y_centro_tierra, 0.0]))

    masa = VGroup(
        Ellipse(width=1.15, height=0.50, stroke_width=2.0,
                color=COLOR_ONDA).set_fill(COLOR_ONDA, opacity=0.35),
        Ellipse(width=0.62, height=0.28, stroke_width=0.0,
                color=COLOR_ONDA).set_fill(COLOR_ONDA, opacity=0.55))

    sat_a = _satelite(1.6, COLOR_OBJETO)
    sat_b = _satelite(1.6, COLOR_OBJETO)
    laser = Line(ORIGIN, RIGHT, stroke_width=2.4, color=COLOR_HAZ)

    p_rotulo = np.array([0.0, y_sat + 0.72, 0.0])
    params = {"ancho": ancho, "alto": alto, "sep_km": sep_km,
              "amplitud_nm": amplitud_nm, "norma": norma, "sigma": sigma,
              "x_a": x_a, "x_b": x_b, "y_sat": y_sat, "y_masa": y_masa,
              "x_masa0": x_masa0, "x_masa1": x_masa1,
              "radio_tierra": radio_tierra,
              "y_centro_tierra": y_centro_tierra, "alza_masa": 0.16,
              "escala_visual": escala_visual, "frac": float(frac),
              "p_rotulo": p_rotulo,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = GracePar(a_a, a_b, tierra, masa, laser, sat_a, sat_b, VGroup(),
                     params)
    pieza.a_t(frac)
    return pieza


# =====================================================================
# 3.3 — El interferometro espacial (LRI)
# =====================================================================
class InterferometroEspacial(_Pieza):
    """Esquema del Laser Ranging Interferometer: laser en A, haz de ida,
    retorno, y en B el fotodetector con las franjas EN EL TIEMPO.

    Publico: `.a`, `.b`, `.ida`, `.vuelta`, `.detector`, `.franjas`,
    `.senal` (la curva), `.marcador`, `.ejes`, `.rotulo`, `.fase`.
    """

    def __init__(self, ancla_a, ancla_b, ejes, senal, marcador, ida, vuelta,
                 sat_a, sat_b, laser, detector, franjas, rotulo, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, ejes, senal, marcador, ida,
                         vuelta, sat_a, sat_b, laser, detector, franjas,
                         rotulo, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.ejes = ejes
        self.senal = senal
        self.marcador = marcador
        self.ida = ida
        self.vuelta = vuelta
        self.a = sat_a
        self.b = sat_b
        self.laser = laser
        self.detector = detector
        self.franjas = franjas
        self.rotulo = rotulo
        self._params = params
        self.fase = params["fase"]

    def _curva_local(self, fase):
        p = self._params
        t = np.linspace(0.0, 1.0, p["muestras"])
        i = 0.5 * (1.0 + np.cos(TAU * p["periodos"] * t + fase))
        x = p["x_curva0"] + t * p["ancho_curva"]
        y = p["y_curva"] + (i - 0.5) * p["alto_curva"]
        return np.column_stack([x, y, np.zeros_like(x)]), i

    def a_fase(self, fase):
        """MUTA: pone la senal de franjas en esa fase (radianes), mueve
        el marcador y repinta la tira de franjas del detector. Devuelve
        `self`.

        Una franja entera = lambda/2 de cambio en la distancia
        (775 nm a 1550 nm): la fase ES la regla.
        """
        fase = float(fase)
        pts, i = self._curva_local(fase)
        self.senal.set_points_as_corners(
            np.array([self._punto(p) for p in pts]))
        self.marcador.move_to(self._punto(pts[0]))
        n = len(self.franjas)
        for k, celda in enumerate(self.franjas):
            valor = 0.5 * (1.0 + math.cos(TAU * 1.5 * k / max(n - 1, 1)
                                          + fase))
            celda.set_fill(COLOR_FRANJA, opacity=0.10 + 0.80 * valor)
        self.fase = fase
        self._params["fase"] = fase
        return self


def interferometro_espacial(fase=0.0, ancho=6.6, alto=4.0, periodos=2.5,
                            muestras=220, n_franjas=12):
    """El LRI de GRACE-FO como esquema: A emite, B devuelve, y el
    fotodetector de B lee franjas EN EL TIEMPO.

    La senal de abajo es I(t) = (1 + cos(2 pi n t + fase)) / 2, la misma
    de cualquier interferometro; lo especial es la escala: cada franja
    vale lambda/2 = 775 nm, y contandolas se sigue una distancia de
    220 km al nanometro (`sensibilidad_relativa(1e-9, 220e3)` =
    4.5e-15).

    HONESTIDAD: es un esquema, no un modelo optico. Las cifras del LRI
    se rotulan como orden de magnitud publicado.
    """
    ancho = _positivo("interferometro_espacial.ancho", ancho)
    alto = _positivo("interferometro_espacial.alto", alto)
    muestras = _validar("interferometro_espacial.muestras", muestras,
                        PUNTOS_MAX, minimo=8)
    n_franjas = _validar("interferometro_espacial.n_franjas", n_franjas,
                         CELDAS_MAX, minimo=2)

    x_a, x_b = -ancho / 2.0 + 0.90, ancho / 2.0 - 0.90
    y_sat = alto / 2.0 - 0.45

    sat_a = _satelite(1.7, COLOR_OBJETO)
    sat_a.move_to(np.array([x_a, y_sat, 0.0]))
    sat_b = _satelite(1.7, COLOR_OBJETO)
    sat_b.move_to(np.array([x_b, y_sat, 0.0]))

    laser = _telescopio(1.1, COLOR_HAZ)
    laser.move_to(np.array([x_a, y_sat - 0.58, 0.0]))
    tallo = Line(laser.get_top(), sat_a.get_bottom(), stroke_width=1.2,
                 color=COLOR_EJE)

    # Los haces arrancan FUERA de los satelites (media anchura + aire).
    x0 = x_a + sat_a.width / 2.0 + 0.12
    x1 = x_b - sat_b.width / 2.0 - 0.12
    ida = Line(np.array([x0, y_sat + 0.11, 0.0]),
               np.array([x1, y_sat + 0.11, 0.0]),
               stroke_width=2.6, color=COLOR_HAZ)
    vuelta = DashedLine(np.array([x1, y_sat - 0.11, 0.0]),
                        np.array([x0, y_sat - 0.11, 0.0]),
                        stroke_width=2.0, color=COLOR_HAZ, dash_length=0.11)
    vuelta.set_stroke(opacity=0.55)

    detector = RoundedRectangle(width=1.15, height=0.62, corner_radius=0.08,
                                stroke_width=2.0, color=COLOR_MEDIDA)
    detector.set_fill(COLOR_MEDIDA, opacity=0.08)
    detector.move_to(np.array([x_b, y_sat - 0.95, 0.0]))
    cable = Line(sat_b.get_bottom(), detector.get_top(), stroke_width=1.2,
                 color=COLOR_EJE)

    ancho_franja = 0.90 / n_franjas
    franjas = VGroup()
    for k in range(n_franjas):
        celda = Rectangle(width=ancho_franja, height=0.34, stroke_width=0.0,
                          color=COLOR_FRANJA)
        celda.move_to(detector.get_center()
                      + RIGHT * ((k + 0.5) / n_franjas - 0.5) * 0.90)
        franjas.add(celda)

    ancho_curva = ancho - 1.5
    alto_curva = 0.95
    x_curva0 = -ancho_curva / 2.0
    y_curva = -alto / 2.0 + 0.78

    ejes = VGroup(
        Line(np.array([x_curva0, y_curva - alto_curva / 2.0 - 0.16, 0.0]),
             np.array([x_curva0 + ancho_curva,
                       y_curva - alto_curva / 2.0 - 0.16, 0.0]),
             stroke_width=1.6, color=COLOR_EJE),
        Line(np.array([x_curva0, y_curva - alto_curva / 2.0 - 0.16, 0.0]),
             np.array([x_curva0, y_curva + alto_curva / 2.0 + 0.16, 0.0]),
             stroke_width=1.6, color=COLOR_EJE),
        _texto_hud("I(t)", font_size=13, color=CODE_MUTED).move_to(
            np.array([x_curva0 - 0.42,
                      y_curva + alto_curva / 2.0 + 0.16, 0.0])),
        _texto_hud("t", font_size=13, color=CODE_MUTED).move_to(
            np.array([x_curva0 + ancho_curva + 0.22,
                      y_curva - alto_curva / 2.0 - 0.16, 0.0])))

    senal = VMobject(color=COLOR_MEDIDA, stroke_width=2.8)
    marcador = Dot(ORIGIN, radius=0.065, color=COLOR_MEDIDA)

    rotulo = VGroup(
        _texto_hud("1 franja = lambda/2 = 775 nm", font_size=15,
                   color=COLOR_FRANJA),
        _texto_hud("1 nm en 220 km = 4.5e-15", font_size=15,
                   color=COLOR_MEDIDA))
    rotulo.arrange(DOWN, buff=0.10, aligned_edge=LEFT)
    rotulo.move_to(np.array([-ancho / 2.0 + 0.30,
                             y_curva + alto_curva / 2.0 + 0.62, 0.0]),
                   aligned_edge=LEFT)

    params = {"ancho": ancho, "alto": alto, "periodos": float(periodos),
              "muestras": muestras, "x_curva0": x_curva0,
              "ancho_curva": ancho_curva, "y_curva": y_curva,
              "alto_curva": alto_curva, "fase": float(fase),
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = InterferometroEspacial(
        a_a, a_b, VGroup(ejes, cable, tallo), senal, marcador, ida, vuelta,
        sat_a,
        sat_b, laser, detector, franjas, rotulo, params)
    pieza.a_fase(fase)
    return pieza


# =====================================================================
# 3.3 — El mapa de anomalias de gravedad
# =====================================================================
_REGIONES_GRAVEDAD = {
    # nombre: (u, v en fracciones de (ancho, alto)), amplitud, sigma_u
    "acuifero": ((-0.30, 0.16), -1.00, 0.11),
    "hielo": ((0.33, -0.24), -0.85, 0.10),
    "cuenca": ((0.06, 0.31), +0.95, 0.12),
}


def _mapa_divergente(v):
    """v en [-1, 1] -> RGB uint8. Cian (negativo) -> fondo -> ambar
    (positivo). Nada de rojo/azul: la paleta de la familia manda."""
    neg = np.array([0x22, 0xd3, 0xee], dtype=np.float64)
    cero = np.array([0x05, 0x07, 0x0a], dtype=np.float64)
    pos = np.array([0xf5, 0x9e, 0x0b], dtype=np.float64)
    t = np.clip(np.abs(v), 0.0, 1.0)[..., None]
    destino = np.where((v >= 0.0)[..., None], pos[None, None, :],
                       neg[None, None, :])
    return np.clip(cero + (destino - cero) * t, 0, 255).astype(np.uint8)


class MapaGravedad(Group):
    """Mapa de anomalias de gravedad: la SENAL que sale de medir una
    distancia.

    OJO: es un `Group`, no un `VGroup`, porque lleva dentro un
    `ImageMobject`. Un ImageMobject NO acepta `set_color` ni
    `set_stroke`; se anima con `FadeIn`/`FadeOut` o transformando a una
    gemela (`Transform` sobre `Group` funciona pieza a pieza).

    Publico: `.imagen`, `.marco`, `.marcas`, `.rotulos`, `.campo`
    (array normalizado a [-1, 1]), `.nombres`. `.region(nombre)` da el
    PUNTO de escena de cada region sobre la geometria ACTUAL.
    """

    def __init__(self, ancla_a, ancla_b, imagen, marco, marcas, rotulos,
                 params, **kwargs):
        super().__init__(ancla_a, ancla_b, imagen, marco, marcas, rotulos,
                         **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.imagen = imagen
        self.marco = marco
        self.marcas = marcas
        self.rotulos = rotulos
        self._params = params
        self.campo = params["campo"]
        self.nombres = params["nombres"]

    def _escala_actual(self):
        d = float(np.linalg.norm(self._ancla_b.get_center()
                                 - self._ancla_a.get_center()))
        return d / max(self._largo_ref, _EPS)

    def _punto(self, p_local):
        return (self._ancla_a.get_center()
                + (_v3(p_local) - self._p_a) * self._escala_actual())

    def region(self, nombre):
        """Punto de escena (np.array de 3) de esa region, ACTUAL.

        Sirve tanto para `move_to(mapa.region("hielo"))` como para
        sumarle un vector: `mapa.region("hielo") + UP * 0.4`.
        """
        clave = str(nombre)
        if clave not in self._params["locales"]:
            raise ValueError(f"region: '{clave}' no esta en "
                             f"{sorted(self._params['locales'])}")
        return self._punto(self._params["locales"][clave])

    def valor(self, nombre):
        """EXTRA: la anomalia normalizada [-1, 1] MEDIDA en el pixel de
        esa region (negativa = falta masa, positiva = sobra)."""
        clave = str(nombre)
        i, j = self._params["pixeles"][clave]
        return float(self.campo[i, j])


def mapa_gravedad(semilla=3, ancho=6.0, alto=3.4, res_x=360, res_y=204,
                  n_fondo=9, rotular=True):
    """Mapa sintetico de anomalias de gravedad, sembrado y determinista.

    Es la suma de `n_fondo` gaussianas colocadas por
    `np.random.default_rng(semilla)` mas TRES anomalias fijas y
    nombradas: "acuifero" y "hielo" en negativo (cian: falta masa) y
    "cuenca" en positivo (ambar: sobra masa). El campo se normaliza a
    [-1, 1] y se pinta con un mapa divergente cian -> fondo -> ambar.

    Se dibuja con un `ImageMobject` (una imagen de 360x204 pesa lo que
    un mobject; 73 000 cuadrados matarian el render). `.region(nombre)`
    devuelve el punto de escena de cada anomalia y `.valor(nombre)` la
    anomalia MEDIDA ahi.

    HONESTIDAD: el mapa es sintetico. Lo real es el mecanismo — esa
    imagen sale de medir una distancia entre dos satelites.
    """
    ancho = _positivo("mapa_gravedad.ancho", ancho)
    alto = _positivo("mapa_gravedad.alto", alto)
    res_x = _validar("mapa_gravedad.res_x", res_x, PIXELES_MAX, minimo=16)
    res_y = _validar("mapa_gravedad.res_y", res_y, PIXELES_MAX, minimo=16)
    n_fondo = _validar("mapa_gravedad.n_fondo", n_fondo, 40, minimo=0) \
        if n_fondo else 0

    aspecto = ancho / alto
    u = np.linspace(-0.5, 0.5, res_x) * aspecto
    v = np.linspace(0.5, -0.5, res_y)          # fila 0 = arriba
    U, V = np.meshgrid(u, v)

    campo = np.zeros_like(U)
    rng = np.random.default_rng(int(semilla))
    for _ in range(n_fondo):
        cu = rng.uniform(-0.5, 0.5) * aspecto
        cv = rng.uniform(-0.45, 0.45)
        amp = rng.uniform(-0.55, 0.55)
        sig = rng.uniform(0.09, 0.20)
        campo += amp * np.exp(-((U - cu) ** 2 + (V - cv) ** 2)
                              / (2.0 * sig * sig))

    locales, pixeles = {}, {}
    for nombre, ((fu, fv), amp, sig) in _REGIONES_GRAVEDAD.items():
        cu, cv = fu * aspecto, fv
        campo += amp * np.exp(-((U - cu) ** 2 + (V - cv) ** 2)
                              / (2.0 * sig * sig))
        locales[nombre] = np.array([fu * ancho, fv * alto, 0.0])
        pixeles[nombre] = (int(round((0.5 - fv) * (res_y - 1))),
                           int(round((fu + 0.5) * (res_x - 1))))

    campo = campo / max(float(np.max(np.abs(campo))), _EPS)
    rgb = _mapa_divergente(campo)
    rgba = np.dstack([rgb, np.full(rgb.shape[:2], 255, dtype=np.uint8)])

    imagen = ImageMobject(rgba)
    imagen.set_resampling_algorithm(3)          # BICUBIC
    imagen.height = alto
    imagen.width = ancho

    marco = Rectangle(width=ancho, height=alto, stroke_width=1.8,
                      color=COLOR_EJE)
    marco.set_fill(opacity=0.0)

    marcas, rotulos = VGroup(), VGroup()
    if rotular:
        for nombre in _REGIONES_GRAVEDAD:
            p = locales[nombre]
            anillo = Circle(radius=0.24, stroke_width=1.8, color="#e8edf3")
            anillo.set_stroke(opacity=0.8)
            anillo.move_to(p)
            marcas.add(anillo)
            t = _texto_hud(nombre, font_size=14, color="#e8edf3")
            t.next_to(anillo, UP, buff=0.08)
            rotulos.add(t)

    params = {"ancho": ancho, "alto": alto, "campo": campo,
              "locales": locales, "pixeles": pixeles,
              "nombres": tuple(_REGIONES_GRAVEDAD),
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    return MapaGravedad(a_a, a_b, imagen, marco, marcas, rotulos, params)


# =====================================================================
# 3.3 — LISA: tres naves y un brazo que se estira
# =====================================================================
class TrianguloLisa(_Pieza):
    """El triangulo de LISA con los tres brazos laser y una onda
    gravitacional que llega desde fuera.

    Publico: `.naves` (VGroup de 3), `.brazos` (VGroup de 3), `.onda`,
    `.rotulo_brazo`, `.rotulo_delta`, `.h`, `.delta_pm()`.
    Brazos: 0 = nave0-nave1 (el que se estira), 1 = nave1-nave2,
    2 = nave2-nave0.
    """

    def __init__(self, ancla_a, ancla_b, onda, brazos, naves, rotulo_brazo,
                 rotulo_delta, params, **kwargs):
        super().__init__(ancla_a, ancla_b, onda, brazos, naves,
                         rotulo_brazo, rotulo_delta, **kwargs)
        self._ancla_a, self._ancla_b = ancla_a, ancla_b
        self._largo_ref = params["ancho"]
        self._p_a = params["p_a"]
        self.onda = onda
        self.brazos = brazos
        self.naves = naves
        self.rotulo_brazo = rotulo_brazo
        self.rotulo_delta = rotulo_delta
        self._params = params
        self.h = params["h"]

    def nave(self, i):
        """La nave i (0, 1, 2), donde este AHORA."""
        return self.naves[_validar("nave.i", int(i) + 1, 3) - 1]

    def brazo(self, i):
        """El brazo i: 0 = nave0-nave1, 1 = nave1-nave2, 2 = nave2-nave0."""
        return self.brazos[_validar("brazo.i", int(i) + 1, 3) - 1]

    def delta_pm(self):
        """Cambio de longitud del brazo para el `h` actual, en picometros:
        h * 2.5e6 km. Con h = 1e-21 salen 2.5 pm — de ahi la frase del
        clip: picometros entre tres naves."""
        return self.h * BRAZO_LISA_KM * 1e3 * 1e12

    def a_estiramiento(self, h):
        """MUTA: estira el brazo 0 segun la deformacion `h` (adimensional)
        y rehace los tres brazos y el rotulo. Devuelve `self`.

        La nave 1 se aleja de la nave 0 a lo largo del brazo 0; los
        brazos 0 y 1 cambian con ella.

        EXAGERACION (documentada): el desplazamiento en pantalla es
        `escala_visual` unidades por 1e-21 de h (0.32 por omision). El
        valor honesto —2.5 pm sobre 2.5e6 km— es 1e-21 de la figura: ni
        con un microscopio.
        """
        h = float(h)
        p = self._params
        base = p["vertices"]
        u = base[1] - base[0]
        u = u / max(float(np.linalg.norm(u)), _EPS)
        v1 = base[1] + u * (p["escala_visual"] * h / 1e-21)
        verts = [base[0], v1, base[2]]
        for i, nave in enumerate(self.naves):
            nave.move_to(self._punto(verts[i]))
        for i in range(3):
            pa, pb = verts[i], verts[(i + 1) % 3]
            d = pb - pa
            d = d / max(float(np.linalg.norm(d)), _EPS)
            self.brazos[i].put_start_and_end_on(
                self._punto(pa + d * p["retiro"]),
                self._punto(pb - d * p["retiro"]))
        self.h = h
        p["h"] = h
        esc = self._escala_actual()
        nuevo = _texto_hud(f"h = {h:.1e}   dL = {self.delta_pm():+.2f} pm",
                           font_size=16, color=COLOR_MEDIDA)
        nuevo.scale(esc)
        nuevo.move_to(self._punto(p["p_delta"]))
        self.remove(self.rotulo_delta)
        self.add(nuevo)
        self.rotulo_delta = nuevo
        return self


def triangulo_lisa(h=0.0, lado=4.2, escala_visual=0.32, ancho=6.4):
    """LISA: tres naves en triangulo equilatero de 2.5 millones de km,
    unidas por brazos laser, con una onda gravitacional que llega desde
    arriba a la izquierda.

    El rotulo del brazo dice "2.5 millones km" y "8.3 s de luz"
    (`tiempo_luz(2.5e9)` = 8.339 s); el otro rotulo da la `h` actual y
    el `dL` en picometros de `delta_pm()`.

    HONESTIDAD: LISA no ha volado (lanzamiento previsto ~2035); las
    cifras son las publicadas de la mision, no medidas aqui.
    """
    lado = _positivo("triangulo_lisa.lado", lado)
    ancho = _positivo("triangulo_lisa.ancho", ancho)
    r = lado / math.sqrt(3.0)                     # circunradio
    vertices = [r * np.array([math.cos(ang), math.sin(ang), 0.0])
                for ang in (PI / 2, PI / 2 - TAU / 3, PI / 2 + TAU / 3)]

    retiro = 0.26
    brazos = VGroup()
    for i in range(3):
        pa, pb = vertices[i], vertices[(i + 1) % 3]
        d = (pb - pa) / max(float(np.linalg.norm(pb - pa)), _EPS)
        brazos.add(Line(pa + d * retiro, pb - d * retiro, stroke_width=2.2,
                        color=COLOR_HAZ))

    naves = VGroup(*[_satelite(1.5, COLOR_OBJETO) for _ in range(3)])

    # La onda gravitacional: tres arcos ambar tenues que llegan desde
    # arriba a la izquierda, FUERA del triangulo (no cruzan los brazos).
    fuente = np.array([-0.72 * lado, 0.52 * lado, 0.0])
    hacia = -fuente / max(float(np.linalg.norm(fuente)), _EPS)
    ang0 = math.atan2(hacia[1], hacia[0])
    onda = VGroup()
    for k, rel in enumerate((0.15, 0.23, 0.31)):
        arco = Arc(radius=rel * lado, start_angle=ang0 - 0.45, angle=0.90,
                   stroke_width=1.8, color=COLOR_ONDA)
        arco.move_arc_center_to(fuente)
        arco.set_stroke(opacity=0.40 - 0.08 * k)
        onda.add(arco)

    medio = 0.5 * (vertices[0] + vertices[1])
    rotulo_brazo = VGroup(
        _texto_hud("2.5 millones km", font_size=16, color=COLOR_HAZ),
        _texto_hud("8.3 s de luz", font_size=14, color=CODE_MUTED))
    rotulo_brazo.arrange(DOWN, buff=0.08)
    rotulo_brazo.move_to(medio + np.array([1.20, 0.30, 0.0]))

    p_delta = np.array([0.0, vertices[1][1] - 0.72, 0.0])
    params = {"ancho": ancho, "lado": lado, "vertices": vertices,
              "retiro": retiro, "escala_visual": escala_visual,
              "h": float(h), "p_delta": p_delta,
              "p_a": np.array([-ancho / 2.0, 0.0, 0.0])}
    a_a, a_b, _ = _anclas_de(ancho)
    pieza = TrianguloLisa(a_a, a_b, onda, brazos, naves, rotulo_brazo,
                          VGroup(), params)
    pieza.a_estiramiento(h)
    return pieza
