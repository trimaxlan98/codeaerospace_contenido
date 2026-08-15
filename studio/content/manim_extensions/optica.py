"""Metrologia optica: la luz como regla (modulos 1 y 2 de la familia).

Pensado para el curso "Metrologia optica". Todo el calculo es
python/numpy/scipy puro y determinista (el unico azar iria con semilla):
mismo script -> mismo render, condicion necesaria para `--disable_caching`.
Nada de red, nada de disco.

La regla de color del curso, que es tambien la de esta libreria: la FUENTE
de luz (laser, haz, pulso) es roja, la ONDA y su fase son ambar, lo que la
luz DIBUJA (franjas, disco de Airy, manchas) es violeta, lo que se MIDE o
se calcula (cifras, detector, curvas de resultado) es cian, y el OBJETO
medido o el otro extremo (espejo, pieza, satelite) es verde. El gris
(`COLOR_EJE`) es mobiliario: ejes, marcos, monturas.

Nucleo (numeros, todos verificados en el contenedor):
    frecuencia_de              c/lam: HeNe 632.8 nm -> 473.76 THz
    paso_franja                lam/2 por franja de Michelson: 316.4 nm
    franjas_por_desplazamiento 2 d / lam
    longitud_coherencia        lam^2/dlam: LED 20 nm -> 20 um; HeNe 1 pm -> 0.40 m
    intensidad_dos_haces       (1 + V cos fase)/2
    visibilidad                (Imax - Imin)/(Imax + Imin)
    franjas_indice             2 L (n-1)/lam: 10 cm de aire -> 85.3 franjas
    rendija_intensidad         sinc^2 de la rendija unica
    airy_intensidad            (2 J1(x)/x)^2 (scipy.special.j1)
    angulo_rayleigh            1.22 lam/D: Hubble 0.28 urad, ojo 224 urad
    divergencia_gauss          lam/(pi w0): 1550 nm, w0 5 cm -> 9.87 urad
    radio_haz                  w0 sqrt(1 + (z/zR)^2)
    huella                     2 theta R: 9.87 urad a 5000 km -> 98.7 m
    tiempo_vuelo               2 d/c: Luna 2.564 s, LAGEOS 39.4 ms
    distancia_por_tiempo       1 mm <-> 6.67 ps
    ambiguedad_fase            c/(2 f): 10 MHz -> 15 m
    fotones_retorno            ley 1/R^4 del retrorreflector (cifra RELATIVA)
    fase_4_pasos               atan2(I4-I2, I1-I3), vectorizado
    desenvolver                np.unwrap 1-D y 2-D (filas y luego columnas)
    altura_de_fase             z = fase lam / (4 pi sin theta)
    zernike                    polinomios NORMALIZADOS (RMS 1 en el circulo)
    strehl                     exp(-(2 pi sigma)^2); lam/14 -> 0.818
    strehl_lineal              1 - (2 pi sigma)^2 (Marechal); lam/14 -> 0.799
    pendientes_locales         gradiente del frente (Shack-Hartmann)

Piezas (VGroup, salvo las que llevan imagen: ver mas abajo):
    # 1.1
    onda_regla          senoide con su lambda acotada; .a_fase(f), .cresta(i)
    reloj_luz           el metro definido por la luz; .a_t(t)
    tren_coherencia     tren de ondas de longitud finita; .con_longitud(L)
    suma_ondas          a, b y a+b; .a_fase(f)
    # 1.2
    michelson           el interferometro completo; .a_desplazamiento(d_nm)
    patron_franjas      franjas rectas; .a_fase(f), .con_visibilidad(V)
    contador_franjas    I(d) + contador; .a_desplazamiento(d_nm)
    celda_gas           celda que se llena; .a_indice(n-1) -> franjas
    # 1.3
    rendija_patron      rendija + sinc^2; .con_ancho(a_rel)
    disco_airy      *   imagen del disco + perfil; .con_diametro(d_rel)
    dos_fuentes_rayleigh *  dos Airy que se acercan; .resuelto()
    haz_gaussiano       cintura + hiperbolas; .radio_en(z), .a_distancia(z)
    # 2.1
    pulso_ida_vuelta    ida y vuelta con cronometro; .a_t(frac)
    tierra_luna_laser   Tierra-Luna a escala de DISTANCIA; .a_t(frac)
    satelite_slr        estacion + LAGEOS; .a_t(frac)
    regla_ambiguedad    la regla que da vueltas; .con_frecuencia(f)
    # 2.2
    objeto_franjas  *   franjas deformadas por una semiesfera; .con_fase0(f)
    cuatro_pasos    *   4 desfases + la fase calculada; .fase()
    mapa_fase           fase envuelta y desenvuelta; .envuelta, .desenvuelta
    perfil_superficie   medido vs ideal; .error_lambda(), .error_nm()
    # 2.3
    frente_onda         rejilla deformada por Zernike; .rms_ondas()
    shack_hartmann      microlentes + manchas; .mancha(i,j), .con_frente(c)
    tarjetas_zernike *  4 tarjetas con su mapa; .tarjeta(nombre)
    espejo_deformable   actuadores que corrigen; .a_correccion(k), .strehl()

(*) Las piezas marcadas llevan `ImageMobject` y por eso son `Group`, no
`VGroup`: manim no admite mobjects no vectoriales dentro de un VGroup. Un
`ImageMobject` NO se colorea con `set_color` ni se anima con `Transform`:
se anima con `FadeIn`/`FadeOut` o `FadeTransform` hacia la GEMELA que
devuelve su `.con_*()`. Cada una de esas piezas expone ademas `.vectorial`
(un VGroup con sus rotulos y curvas) por si el clip quiere animar solo esa
parte.

Convenio de los metodos:
    `.con_*(x)`  devuelve una pieza GEMELA, ya escalada y colocada donde
                 esta la original (lista para `Transform`/`FadeTransform`).
    `.a_*(x)`    MUTA la pieza en el sitio y devuelve self (para updaters,
                 ValueTracker y estados iniciales).
    localizadores (`.cresta`, `.mancha`, `.primer_cero`, ...) se calculan
    sobre la geometria ACTUAL: sobreviven a `.shift`/`.move_to`/`.scale`
    (no a `.rotate`).

Topes duros para no castigar el VPS: `PUNTOS_MAX`, `CELDAS_MAX`,
`PIXELES_MAX`, `FRANJAS_MAX`, `ACTUADORES_MAX` levantan ValueError.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from optica import michelson, paso_franja

    m = michelson()
    self.add(m)
    self.play(m.animate.scale(0.9))
    m.a_desplazamiento(949.2)      # 3 franjas
"""

import math

import numpy as np
from scipy.special import j1 as _j1

from manim import (Arc, ArcBetweenPoints, Arrow, Brace, Circle, DashedLine,
                   DashedVMobject, Dot, DoubleArrow, Group, ImageMobject,
                   Line, Polygon, Rectangle, RoundedRectangle,
                   Square, Text, VGroup, VMobject, DOWN, LEFT, ORIGIN, PI,
                   RIGHT, TAU, UP)

from code_brand import CODE_BG, CODE_INK, CODE_MUTED, FUENTE_HUD, registrar_fuentes

# --- Constantes fisicas del curso -------------------------------------
C_LUZ = 299_792_458.0        # m/s, EXACTA por definicion del metro (1983)
LAMBDA_HENE = 632.8e-9       # m, laser de helio-neon (el rojo del taller)
LAMBDA_ISL = 1550e-9         # m, banda telecom de los enlaces opticos
LAMBDA_VERDE = 532e-9        # m, el verde doblado de los telemetros laser
H_PLANCK = 6.62607015e-34    # J s, exacta desde 2019

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
PUNTOS_MAX = 4000            # muestras de una curva
CELDAS_MAX = 64              # lado de una rejilla de celdas/microlentes
PIXELES_MAX = 512            # lado de una imagen sintetica
FRANJAS_MAX = 40             # franjas dibujadas en un patron
ACTUADORES_MAX = 21          # actuadores de un espejo deformable

# Paleta propia de la libreria (coincide con la del curso).
COLOR_HAZ = "#f43f5e"        # rojo: la fuente, el laser, el pulso que sale
COLOR_ONDA = "#f59e0b"       # ambar: la onda y su fase, los frentes
COLOR_FRANJA = "#a78bfa"     # violeta: lo que la luz dibuja (franjas, Airy)
COLOR_MEDIDA = "#22d3ee"     # cian: lo que se mide (cifras, detector, curvas)
COLOR_OBJETO = "#34d399"     # verde: el objeto medido / el otro extremo
COLOR_EJE = "#31414f"        # mobiliario: ejes, marcos, monturas

C_HAZ, C_ONDA, C_FRANJA = COLOR_HAZ, COLOR_ONDA, COLOR_FRANJA
C_MEDIDA, C_OBJETO, C_EJE = COLOR_MEDIDA, COLOR_OBJETO, COLOR_EJE

# Modos de Zernike que el curso nombra: nombre -> (n, m).
MODOS_ZERNIKE = {
    "inclinacion_x": (1, 1),
    "inclinacion_y": (1, -1),
    "desenfoque": (2, 0),
    "astigmatismo": (2, 2),
    "astigmatismo_45": (2, -2),
    "coma": (3, 1),
    "coma_y": (3, -1),
    "esferica": (4, 0),
}

_EPS = 1e-12

# Caracteres que la fuente HUD (Space Mono, ASCII puro) no tiene.
_NO_ASCII = {"µ": "u", "μ": "u", "°": " grados", "±": "+/-",
             "á": "a", "é": "e", "í": "i", "ó": "o",
             "ú": "u", "ñ": "n", "Á": "A", "É": "E",
             "Í": "I", "Ó": "O", "Ú": "U", "Ñ": "N",
             "→": "->", "λ": "lambda", "σ": "sigma",
             "θ": "theta"}


# =====================================================================
# Utilidades internas
# =====================================================================
def _validar(nombre, valor, tope):
    """Entero en 1..tope o ValueError."""
    valor = int(valor)
    if valor < 1 or valor > tope:
        raise ValueError(f"{nombre}: {valor} fuera de rango (1..{tope})")
    return valor


def _ascii(texto):
    """ASCII puro para la fuente HUD: 'µrad' -> 'urad', tildes fuera."""
    salida = []
    for ch in str(texto):
        salida.append(_NO_ASCII.get(ch, ch))
    txt = "".join(salida)
    return txt.encode("ascii", "ignore").decode("ascii")


def _texto_hud(texto, font_size=15, color=CODE_MUTED):
    """Texto de telemetria: Space Mono, ASCII puro (sin tildes, sin µ: la
    fuente HUD no los tiene; los exponentes van en MathTex)."""
    registrar_fuentes()
    return Text(_ascii(texto), font=FUENTE_HUD, font_size=font_size,
                color=color)


def _ancla(punto=ORIGIN):
    """Dot invisible que viaja con la pieza: localizador inmune a move_to,
    shift y scale."""
    p = np.asarray(punto, dtype=np.float64)
    if p.shape == (2,):
        p = np.append(p, 0.0)
    return Dot(p, radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)


def _xyz(pts):
    """(n,2) o (n,3) -> (n,3) float."""
    pts = np.asarray(pts, dtype=np.float64)
    if pts.ndim == 1:
        pts = pts[None, :]
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    return pts


def _poligonal(puntos, color, grosor=2.6, opacidad=1.0):
    """VMobject por segmentos a partir de (n,2)/(n,3): barato de recalcular
    (es lo que usan los `.a_*` que corren en un updater)."""
    linea = VMobject(color=color, stroke_width=grosor)
    linea.set_points_as_corners(_xyz(puntos))
    linea.set_stroke(opacity=opacidad)
    linea.set_fill(opacity=0.0)
    return linea


def _fijar(mob, puntos):
    """Reescribe los puntos de una poligonal EN SITIO."""
    mob.set_points_as_corners(_xyz(puntos))
    return mob


def _hex_a_rgb(hexcolor):
    h = str(hexcolor).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)],
                    dtype=np.float64)


def _mezcla(color_a, color_b, t):
    """Interpolacion lineal entre dos hex; t escalar o array."""
    a, b = _hex_a_rgb(color_a), _hex_a_rgb(color_b)
    t = np.clip(np.asarray(t, dtype=np.float64), 0.0, 1.0)
    return a + (b - a) * t[..., None]


def _imagen(rgba, alto=None, ancho=None):
    """ImageMobject desde un array uint8 (h, w, 4). OJO: un ImageMobject no
    acepta `set_color` ni entra en un VGroup."""
    img = ImageMobject(np.ascontiguousarray(rgba))
    img.set_resampling_algorithm(3)          # BICUBIC
    if alto is not None:
        img.height = float(alto)
    if ancho is not None:
        img.width = float(ancho)
    return img


def _imagen_escalar(v, color, alto=None, ancho=None, fondo=CODE_BG,
                    alfa=None):
    """Campo v en [0,1] -> imagen del degradado fondo->color.

    La fila 0 del array es y MINIMO (se invierte al pasar a pixeles, que
    van de arriba a abajo). `alfa` opcional (mismo shape) para recortar.
    """
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    if max(v.shape) > PIXELES_MAX:
        raise ValueError(f"_imagen_escalar: {v.shape} pasa de {PIXELES_MAX}")
    rgba = np.empty(v.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = np.clip(_mezcla(fondo, color, v), 0, 255).astype(np.uint8)
    if alfa is None:
        rgba[..., 3] = 255
    else:
        rgba[..., 3] = np.clip(np.asarray(alfa) * 255.0, 0,
                               255).astype(np.uint8)
    return _imagen(rgba[::-1], alto=alto, ancho=ancho)


def _imagen_divergente(v, color_neg=C_MEDIDA, color_pos=C_ONDA, alto=None,
                       ancho=None, fondo=CODE_BG, alfa=None):
    """Campo v en [-1,1] -> cian (negativo) - fondo - ambar (positivo)."""
    v = np.clip(np.asarray(v, dtype=np.float64), -1.0, 1.0)
    if max(v.shape) > PIXELES_MAX:
        raise ValueError(f"_imagen_divergente: {v.shape} pasa de {PIXELES_MAX}")
    rgb = np.where((v < 0)[..., None],
                   _mezcla(fondo, color_neg, -v),
                   _mezcla(fondo, color_pos, v))
    rgba = np.empty(v.shape + (4,), dtype=np.uint8)
    rgba[..., :3] = np.clip(rgb, 0, 255).astype(np.uint8)
    if alfa is None:
        rgba[..., 3] = 255
    else:
        rgba[..., 3] = np.clip(np.asarray(alfa) * 255.0, 0,
                               255).astype(np.uint8)
    return _imagen(rgba[::-1], alto=alto, ancho=ancho)


def _malla(res, extension=1.0):
    """Malla cuadrada res x res en [-extension, extension]^2.

    Devuelve (X, Y) con la FILA 0 en y minimo (convenio del modulo: las
    filas suben; `_imagen_*` ya invierte al dibujar)."""
    res = _validar("_malla.res", res, PIXELES_MAX)
    t = np.linspace(-float(extension), float(extension), res)
    return np.meshgrid(t, t)


class _Geometria:
    """Mixin de los localizadores: mapea coordenadas LOCALES (las del
    constructor) a coordenadas de ESCENA usando dos anclas invisibles, asi
    que sobrevive a `.shift`, `.move_to` y `.scale`.

    Requiere que la pieza fije `_ancla_a`, `_ancla_b`, `_largo_ref` (la
    distancia local entre las dos anclas) y `_p0` (la posicion local del
    ancla a).
    """

    _p0 = (0.0, 0.0, 0.0)

    def _escala_actual(self):
        d = float(np.linalg.norm(self._ancla_b.get_center()
                                 - self._ancla_a.get_center()))
        return d / max(self._largo_ref, _EPS)

    def _origen(self):
        return self._ancla_a.get_center()

    def _a_escena(self, puntos):
        """(n,2)/(n,3) locales -> (n,3) de escena, con la escala y la
        posicion ACTUALES de la pieza."""
        p0 = np.asarray(self._p0, dtype=np.float64)
        if p0.shape == (2,):
            p0 = np.append(p0, 0.0)
        return self._origen() + (_xyz(puntos) - p0) * self._escala_actual()

    def _punto(self, xy):
        """Un solo punto local -> escena."""
        return self._a_escena(np.asarray(xy, dtype=np.float64).reshape(1, -1))[0]

    def _alinear(self, otra):
        """Escala y coloca una pieza GEMELA sobre esta (para Transform)."""
        otra.scale(self._escala_actual())
        otra.shift(self._origen() - otra._ancla_a.get_center())
        return otra

    def _relectura(self, viejo, texto, font_size=16, color=C_MEDIDA,
                   contenedor=None, borde=LEFT):
        """Sustituye un rotulo HUD conservando su borde `borde` (por
        omision el izquierdo: asi los numeros no bailan) y su escala."""
        nuevo = _texto_hud(texto, font_size=font_size, color=color)
        nuevo.scale(self._escala_actual())
        if borde is LEFT:
            nuevo.move_to(viejo.get_left(), aligned_edge=LEFT)
        elif borde is RIGHT:
            nuevo.move_to(viejo.get_right(), aligned_edge=RIGHT)
        else:
            nuevo.move_to(viejo.get_center())
        destino = self if contenedor is None else contenedor
        destino.remove(viejo)
        destino.add(nuevo)
        return nuevo


class _Pieza(_Geometria, VGroup):
    """Pieza vectorial con localizadores (el caso normal)."""


class _PiezaImg(_Geometria, Group):
    """Pieza con `ImageMobject`: `Group`, no `VGroup`. Se anima con
    `FadeIn`/`FadeOut`/`FadeTransform`, nunca con `Transform`, y su imagen
    no se puede recolorear."""


# =====================================================================
# Nucleo: la onda como regla
# =====================================================================
def frecuencia_de(lam):
    """Frecuencia de una onda de longitud `lam` (m): f = c/lam.

    El HeNe de 632.8 nm oscila a 4.7376e14 Hz = 473.76 THz: 473 billones
    de veces por segundo. Ningun contador electronico llega ahi; por eso
    la luz se mide por interferencia y no contando ciclos.
    """
    lam = float(lam)
    if lam <= 0:
        raise ValueError(f"frecuencia_de: lam={lam} <= 0")
    return C_LUZ / lam


def paso_franja(lam=LAMBDA_HENE):
    """Cuanto avanza el espejo movil de un Michelson por cada franja que
    pasa: lam/2, porque la luz recorre el brazo DOS veces.

    Con el HeNe: 632.8/2 = 316.4 nm por franja.
    """
    lam = float(lam)
    if lam <= 0:
        raise ValueError(f"paso_franja: lam={lam} <= 0")
    return lam / 2.0


def franjas_por_desplazamiento(d, lam=LAMBDA_HENE):
    """Franjas que pasan cuando el espejo se mueve `d` metros: N = 2 d/lam.

    949.2 nm -> 3.00 franjas exactas con el HeNe. Contar franjas ES medir:
    la regla la pone la longitud de onda.
    """
    lam = float(lam)
    if lam <= 0:
        raise ValueError(f"franjas_por_desplazamiento: lam={lam} <= 0")
    return 2.0 * np.asarray(d, dtype=np.float64) / lam


def longitud_coherencia(lam, dlam):
    """Longitud de coherencia: Lc = lam^2/dlam (aproximacion habitual).

    Es hasta donde sirve la regla: mas alla de Lc las franjas se lavan.
    LED rojo (dlam = 20 nm @ 633 nm) -> 20.0 um. HeNe estabilizado
    (dlam = 1 pm) -> 0.40 m: 20 000 veces mas largo.
    """
    lam, dlam = float(lam), float(dlam)
    if lam <= 0 or dlam <= 0:
        raise ValueError(f"longitud_coherencia: lam={lam}, dlam={dlam}")
    return lam * lam / dlam


def intensidad_dos_haces(fase, V=1.0):
    """Intensidad NORMALIZADA de dos haces que interfieren:
    I = (1 + V cos(fase))/2, con V la visibilidad.

    Vale 1 en la franja brillante y 0 en la oscura cuando V = 1. Acepta
    escalares o arrays de numpy.
    """
    fase = np.asarray(fase, dtype=np.float64)
    return (1.0 + float(V) * np.cos(fase)) / 2.0


def visibilidad(imax, imin):
    """Visibilidad (contraste) de un patron: (Imax - Imin)/(Imax + Imin).

    Es la salud de la medida: 1 son franjas limpias, 0.3 franjas lavadas,
    0 ya no hay franjas que contar.
    """
    imax, imin = float(imax), float(imin)
    s = imax + imin
    if abs(s) < _EPS:
        raise ValueError("visibilidad: Imax + Imin = 0")
    return (imax - imin) / s


def franjas_indice(L, n_menos_1, lam=LAMBDA_HENE):
    """Franjas que pasan al llenar una celda de largo `L` con un gas de
    indice n: N = 2 L (n-1)/lam (la luz cruza la celda dos veces).

    10 cm de aire (n-1 = 2.7e-4) con el HeNe: 85.3 franjas. Contarlas es
    medir el indice del aire con un laser y una regla de 316 nm.
    """
    lam = float(lam)
    if lam <= 0:
        raise ValueError(f"franjas_indice: lam={lam} <= 0")
    return 2.0 * float(L) * float(n_menos_1) / lam


# =====================================================================
# Nucleo: difraccion
# =====================================================================
def rendija_intensidad(theta, a, lam=LAMBDA_HENE):
    """Difraccion por una rendija de ancho `a`: I(theta) = sinc^2(a sin/lam)
    con la sinc NORMALIZADA de numpy (sin(pi u)/(pi u)).

    Los ceros caen en sin(theta) = k lam/a: cuanto MAS angosta la rendija,
    MAS ancho el patron. Ahi empieza el limite de la regla.
    """
    a, lam = float(a), float(lam)
    if a <= 0 or lam <= 0:
        raise ValueError(f"rendija_intensidad: a={a}, lam={lam}")
    u = a * np.sin(np.asarray(theta, dtype=np.float64)) / lam
    return np.sinc(u) ** 2


def airy_intensidad(x):
    """Patron de Airy (apertura circular): I(x) = (2 J1(x)/x)^2, con
    x = pi D sin(theta)/lam. Vale 1 en el centro (limite x->0).

    El primer cero es el primer cero de J1, x = 3.8317, o sea
    sin(theta) = 1.2197 lam/D: de ahi sale el 1.22 de Rayleigh.
    """
    x = np.asarray(x, dtype=np.float64)
    seguro = np.where(np.abs(x) < 1e-9, 1e-9, x)
    val = (2.0 * _j1(seguro) / seguro) ** 2
    return np.where(np.abs(x) < 1e-9, 1.0, val)


def angulo_rayleigh(lam, D):
    """Criterio de Rayleigh: dos puntos se distinguen si los separa al
    menos 1.22 lam/D (el maximo de uno cae en el primer cero del otro).

    Hubble (D = 2.4 m, 550 nm) -> 2.80e-7 rad = 0.28 urad. El ojo
    (D = 3 mm) -> 2.24e-4 rad = 224 urad. Es un CRITERIO, no una ley: con
    mucha senal y buen modelo se puede afinar mas.
    """
    lam, D = float(lam), float(D)
    if lam <= 0 or D <= 0:
        raise ValueError(f"angulo_rayleigh: lam={lam}, D={D}")
    return 1.22 * lam / D


def divergencia_gauss(lam, w0):
    """Semiangulo de divergencia de un haz gaussiano: theta = lam/(pi w0).

    1550 nm con cintura w0 = 5 cm -> 9.868e-6 rad = 9.87 urad. Ni el laser
    es una recta: todo haz se abre, y el que se abre poco necesita una
    apertura grande.
    """
    lam, w0 = float(lam), float(w0)
    if lam <= 0 or w0 <= 0:
        raise ValueError(f"divergencia_gauss: lam={lam}, w0={w0}")
    return lam / (PI * w0)


def rango_rayleigh(lam, w0):
    """Distancia de Rayleigh zR = pi w0^2/lam: hasta ahi el haz casi no se
    abre. Con w0 = 5 cm a 1550 nm son 5066 m."""
    lam, w0 = float(lam), float(w0)
    if lam <= 0 or w0 <= 0:
        raise ValueError(f"rango_rayleigh: lam={lam}, w0={w0}")
    return PI * w0 * w0 / lam


def radio_haz(z, lam, w0):
    """Radio del haz gaussiano a distancia z: w = w0 sqrt(1 + (z/zR)^2).

    Muy lejos vale w -> theta z, con theta = lam/(pi w0): la hiperbola se
    vuelve recta. A 5000 km con w0 = 5 cm y 1550 nm, w = 49.3 m.
    """
    zr = rango_rayleigh(lam, w0)
    z = np.asarray(z, dtype=np.float64)
    return float(w0) * np.sqrt(1.0 + (z / zr) ** 2)


def huella(theta, R):
    """Diametro de la huella de un haz de semiangulo `theta` a distancia
    `R`: 2 theta R.

    9.87 urad a 5000 km -> 98.7 m. Ese es el problema del enlace optico:
    hay que meter una mancha de 99 m sobre un satelite de 2 m.
    """
    return 2.0 * float(theta) * float(R)


# =====================================================================
# Nucleo: tiempo de vuelo
# =====================================================================
def tiempo_vuelo(d):
    """Tiempo de ida y vuelta de un pulso hasta `d` metros: t = 2 d/c.

    Luna (384 400 km) -> 2.5644 s. LAGEOS (5900 km) -> 39.36 ms. Medir
    distancia es, aqui, medir tiempo.
    """
    d = float(d)
    if d < 0:
        raise ValueError(f"tiempo_vuelo: d={d} < 0")
    return 2.0 * d / C_LUZ


def distancia_por_tiempo(dt):
    """Distancia que corresponde a un tiempo de ida y vuelta: d = c dt/2.

    1 ps -> 0.15 mm. Al reves: 1 mm de distancia son 6.67 ps. Por eso los
    telemetros buenos se pelean por los picosegundos.
    """
    return C_LUZ * float(dt) / 2.0


def ambiguedad_fase(f_mod):
    """Distancia en la que la fase de una modulacion de `f_mod` da una
    vuelta entera: c/(2 f_mod).

    10 MHz -> 14.99 m; 100 MHz -> 1.499 m. La fase mide fino pero no sabe
    cuantas vueltas lleva: por eso se combinan varias frecuencias.
    """
    f_mod = float(f_mod)
    if f_mod <= 0:
        raise ValueError(f"ambiguedad_fase: f_mod={f_mod} <= 0")
    return C_LUZ / (2.0 * f_mod)


def fotones_retorno(energia_j, area_rx_m2, theta_tx, R, lam=LAMBDA_VERDE,
                    seccion_m2=7.0e6, eficiencia=0.05):
    """Fotones que vuelven de un retrorreflector (enlace SLR SIMPLIFICADO).

    n = N_emitidos * eficiencia * G_tx * (sigma/(4 pi R^2)) * (A_rx/(4 pi R^2))
    con N_emitidos = E lam/(h c) y G_tx = 8/theta^2 (haz gaussiano). Los
    dos factores 1/(4 pi R^2) son la ida y la vuelta: de ahi la ley 1/R^4
    que hace tan dificil el telemetro lunar.

    Es una cifra RELATIVA (de juguete): sirve para comparar distancias o
    aperturas, no para predecir el retorno absoluto de una estacion real
    (faltan atmosfera, optica, eficiencia cuantica del detector). Con
    100 mJ, telescopio de 0.5 m2, 50 urad y LAGEOS a 5900 km da ~780
    fotones; cuadruplicar la distancia divide el retorno por 256.
    """
    energia_j, theta_tx, R = float(energia_j), float(theta_tx), float(R)
    if energia_j <= 0 or theta_tx <= 0 or R <= 0:
        raise ValueError("fotones_retorno: energia, theta y R deben ser > 0")
    n_emit = energia_j * float(lam) / (H_PLANCK * C_LUZ)
    g_tx = 8.0 / (theta_tx ** 2)
    esfera = 4.0 * PI * R * R
    return (n_emit * float(eficiencia) * g_tx
            * (float(seccion_m2) / esfera)
            * (float(area_rx_m2) / esfera))


# =====================================================================
# Nucleo: fase, desenvoltura y forma
# =====================================================================
def fase_4_pasos(i1, i2, i3, i4):
    """Fase por el algoritmo de los cuatro pasos:
    fase = atan2(I4 - I2, I1 - I3), pixel a pixel (vectorizado).

    Con I_k = I0 (1 + V cos(fase + (k-1) 90 grados)) sale
    I4 - I2 = 2 I0 V sin(fase) y I1 - I3 = 2 I0 V cos(fase): la fase
    aparece sin saber ni I0 ni V. Devuelve la fase ENVUELTA, en (-pi, pi].
    """
    i1 = np.asarray(i1, dtype=np.float64)
    i2 = np.asarray(i2, dtype=np.float64)
    i3 = np.asarray(i3, dtype=np.float64)
    i4 = np.asarray(i4, dtype=np.float64)
    return np.arctan2(i4 - i2, i1 - i3)


def desenvolver(fase):
    """Quita los saltos de 2 pi: `np.unwrap` en 1-D; en 2-D, primero por
    filas y luego por columnas (el metodo simple, suficiente para un mapa
    sin ruido ni islas).

    Los dientes de sierra vuelven a ser una rampa continua: ahi esta la
    forma de la pieza.
    """
    a = np.asarray(fase, dtype=np.float64)
    if a.ndim == 1:
        return np.unwrap(a)
    if a.ndim == 2:
        return np.unwrap(np.unwrap(a, axis=1), axis=0)
    raise ValueError(f"desenvolver: se esperaba 1-D o 2-D, no {a.ndim}-D")


def altura_de_fase(fase, lam=LAMBDA_HENE, theta=PI / 4.0):
    """Altura del objeto a partir de la fase de unas franjas PROYECTADAS:
    z = fase lam/(4 pi sin theta), con `theta` el angulo entre la
    proyeccion y la observacion.

    Con 45 grados y el HeNe, 2 pi de fase (una franja entera) son 447.5 nm
    de altura. La forma no se toca: se lee en las franjas.
    """
    theta = float(theta)
    s = math.sin(theta)
    if abs(s) < _EPS:
        raise ValueError(f"altura_de_fase: sin(theta)={s} ~ 0")
    return np.asarray(fase, dtype=np.float64) * float(lam) / (4.0 * PI * s)


def _radial_zernike(n, m, rho):
    """Polinomio radial R_n^m(rho) (m ya en valor absoluto)."""
    n, m = int(n), abs(int(m))
    s = np.zeros_like(np.asarray(rho, dtype=np.float64))
    for k in range((n - m) // 2 + 1):
        c = ((-1) ** k * math.factorial(n - k)
             / (math.factorial(k) * math.factorial((n + m) // 2 - k)
                * math.factorial((n - m) // 2 - k)))
        s = s + c * np.asarray(rho, dtype=np.float64) ** (n - 2 * k)
    return s


def zernike(n, m, rho, phi):
    """Polinomio de Zernike NORMALIZADO (convenio de Noll): su RMS sobre el
    circulo unidad vale 1, asi que un coeficiente en ondas ES su RMS.

    m > 0 lleva cos(m phi), m < 0 lleva sin(|m| phi), m = 0 no depende del
    angulo. El curso usa desenfoque (2,0), astigmatismo (2,+-2), coma
    (3,+-1) y esferica (4,0). Fuera del circulo (rho > 1) la formula sigue
    devolviendo numeros: el que llama recorta con una mascara.

    Ejemplo: zernike(2, 0, 1.0, 0.0) = sqrt(3) (2 - 1) = 1.732.
    """
    n, m = int(n), int(m)
    if n < 0 or abs(m) > n or (n - abs(m)) % 2 != 0:
        raise ValueError(f"zernike: (n, m) = ({n}, {m}) no es un modo valido")
    rho = np.asarray(rho, dtype=np.float64)
    phi = np.asarray(phi, dtype=np.float64)
    radial = _radial_zernike(n, m, rho)
    if m == 0:
        norma = math.sqrt(n + 1.0)
        return norma * radial
    norma = math.sqrt(2.0 * (n + 1.0))
    if m > 0:
        return norma * radial * np.cos(m * phi)
    return norma * radial * np.sin(abs(m) * phi)


def strehl(sigma_ondas):
    """Razon de Strehl a partir del RMS del frente en ONDAS (Marechal
    extendido): S = exp(-(2 pi sigma)^2).

    sigma = lam/14 -> 0.8176. El clasico "S = 0.8 con lam/14" viene de la
    version LINEAL de la misma formula (`strehl_lineal`, 0.7986): son la
    misma fisica con y sin la aproximacion exp(x) ~ 1 + x.
    """
    s = np.asarray(sigma_ondas, dtype=np.float64)
    return np.exp(-((2.0 * PI * s) ** 2))


def strehl_lineal(sigma_ondas):
    """Aproximacion clasica de Marechal: S ~ 1 - (2 pi sigma)^2.

    Es la que da el numero redondo del criterio: sigma = lam/14 -> 0.799.
    Solo vale para aberraciones pequenas (se vuelve negativa pasado
    sigma = 0.159 ondas)."""
    s = np.asarray(sigma_ondas, dtype=np.float64)
    return 1.0 - (2.0 * PI * s) ** 2


def sigma_de_strehl(S):
    """El RMS (en ondas) que da esa razon de Strehl: sqrt(-ln S)/(2 pi).

    S = 0.30 -> 0.1746 ondas = lam/5.7. Sirve para arrancar el espejo
    deformable en un Strehl dado."""
    S = float(S)
    if not 0.0 < S <= 1.0:
        raise ValueError(f"sigma_de_strehl: S={S} fuera de (0, 1]")
    return math.sqrt(-math.log(S)) / (2.0 * PI)


def pendientes_locales(frente, paso=1.0):
    """Pendientes locales de un frente de onda: el gradiente (gx, gy) con
    `np.gradient` y separacion `paso` entre muestras.

    Es LO QUE MIDE un Shack-Hartmann: cada microlente no ve la fase, ve la
    inclinacion, y la mancha se corre proporcionalmente. Convenio del
    modulo: `frente[i, j]` con i = fila creciendo hacia y POSITIVO, asi que
    `gy` es la derivada respecto de y y `gx` respecto de x.
    """
    a = np.asarray(frente, dtype=np.float64)
    if a.ndim != 2:
        raise ValueError(f"pendientes_locales: se esperaba 2-D, no {a.ndim}-D")
    gy, gx = np.gradient(a, float(paso))
    return gx, gy


def frente_de_coeficientes(coefs, res=64, extension=1.0, recortar=True):
    """Mapa del frente W(rho, phi) = suma c_i Z_i en ONDAS sobre
    [-extension, extension]^2.

    `coefs` es un dict {nombre: coeficiente} con los nombres de
    `MODOS_ZERNIKE`, o {(n, m): coeficiente}. Devuelve (X, Y, W, dentro)
    con `dentro` la mascara booleana (rho <= 1). Con `recortar` (por
    omision) W vale 0 fuera de la pupila; con `recortar=False` se deja el
    polinomio extrapolado, que es lo que hay que usar para DERIVAR (si no,
    el borde de la mascara mete un acantilado falso en el gradiente).
    Como los Zernike van normalizados, el RMS del frente es
    sqrt(suma c_i^2) — se comprueba midiendolo sobre la malla.
    """
    X, Y = _malla(res, extension)
    rho = np.hypot(X, Y)
    phi = np.arctan2(Y, X)
    dentro = rho <= 1.0
    W = np.zeros_like(X)
    for clave, c in dict(coefs).items():
        if isinstance(clave, str):
            if clave not in MODOS_ZERNIKE:
                raise ValueError(f"frente_de_coeficientes: modo '{clave}' "
                                 f"desconocido ({sorted(MODOS_ZERNIKE)})")
            n, m = MODOS_ZERNIKE[clave]
        else:
            n, m = clave
        W = W + float(c) * zernike(n, m, rho, phi)
    if recortar:
        W = np.where(dentro, W, 0.0)
    return X, Y, W, dentro


# =====================================================================
# 1.1 — La onda como regla
# =====================================================================
class OndaRegla(_Pieza):
    """Senoide ambar con su longitud de onda acotada por una llave.

    Atributos: `.curva`, `.eje`, `.llave_lambda` (Brace + rotulo, o None),
    `.lambda_local` (la lambda DIBUJADA, en unidades de escena),
    `.fase` (rad).
    """

    def __init__(self, ancla_a, ancla_b, eje, curva, llave, params, **kwargs):
        hijos = [ancla_a, ancla_b, eje, curva]
        if llave is not None:
            hijos.append(llave)
        super().__init__(*hijos, **kwargs)
        self._ancla_a = ancla_a             # extremo izquierdo del eje
        self._ancla_b = ancla_b             # extremo derecho del eje
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.eje = eje
        self.curva = curva
        self.llave_lambda = llave
        self._params = params
        self.fase = params["fase"]
        self.lambda_local = params["lam_local"]

    def _puntos(self, fase):
        p = self._params
        x = np.linspace(-p["ancho"] / 2.0, p["ancho"] / 2.0, p["muestras"])
        u = x + p["ancho"] / 2.0
        y = p["amplitud"] * np.cos(p["k"] * u - fase)
        return np.column_stack([x, y])

    def a_fase(self, fase):
        """MUTA la onda: la corre a esa fase (rad). La onda viaja hacia la
        DERECHA cuando la fase crece. Devuelve self (sirve en un updater:
        `onda.add_updater(lambda o: o.a_fase(t.get_value()))`).

        OJO: la llave de lambda NO se mueve (marca un periodo fijo del
        dibujo, que es lo que se quiere rotular).
        """
        self.fase = float(fase)
        _fijar(self.curva, self._a_escena(self._puntos(self.fase)))
        return self

    def cresta(self, i):
        """Punto de escena de la cresta i (i = 0 es la primera cresta a la
        derecha del borde izquierdo con fase 0). Puede caer fuera de la
        pieza si la fase la saco: es un localizador, no un recorte."""
        p = self._params
        u = float(i) * p["lam_local"] + self.fase / p["k"]
        return self._punto((u - p["ancho"] / 2.0, p["amplitud"]))

    def valle(self, i):
        """Punto de escena del valle i (medio periodo despues de la cresta
        i)."""
        p = self._params
        u = (float(i) + 0.5) * p["lam_local"] + self.fase / p["k"]
        return self._punto((u - p["ancho"] / 2.0, -p["amplitud"]))


def onda_regla(n_periodos=4, ancho=5.2, amplitud=0.62, fase=0.0,
               color=C_ONDA, etiqueta="lambda", con_llave=True,
               muestras=241):
    """La onda como regla: cada cresta es una marca.

    `n_periodos` lambdas caben en `ancho` unidades de escena, asi que la
    lambda dibujada vale ancho/n_periodos (esta en `.lambda_local`). El
    dibujo NO esta a escala real — 632.8 nm no se dibujan: lo que se rotula
    es la cifra, y la llave dice cual es el tramo que vale una lambda.
    """
    n_periodos = _validar("onda_regla.n_periodos", n_periodos, FRANJAS_MAX)
    muestras = _validar("onda_regla.muestras", muestras, PUNTOS_MAX)
    ancho, amplitud = float(ancho), float(amplitud)
    lam_local = ancho / n_periodos
    k = TAU / lam_local

    eje = Line(np.array([-ancho / 2.0, 0.0, 0.0]),
               np.array([ancho / 2.0, 0.0, 0.0]),
               stroke_width=1.4, color=C_EJE)

    params = {"ancho": ancho, "amplitud": amplitud, "k": k,
              "lam_local": lam_local, "n_periodos": n_periodos,
              "muestras": muestras, "fase": float(fase), "color": color,
              "etiqueta": etiqueta, "con_llave": con_llave}

    x = np.linspace(-ancho / 2.0, ancho / 2.0, muestras)
    y = amplitud * np.cos(k * (x + ancho / 2.0) - float(fase))
    curva = _poligonal(np.column_stack([x, y]), color, 3.2)

    llave = None
    if con_llave:
        y_llave = -amplitud - 0.22
        guia = Line(np.array([-ancho / 2.0, y_llave, 0.0]),
                    np.array([-ancho / 2.0 + lam_local, y_llave, 0.0]),
                    stroke_width=0.1)
        brace = Brace(guia, DOWN, buff=0.05, color=C_EJE)
        rot = _texto_hud(etiqueta, font_size=19, color=color)
        rot.next_to(brace, DOWN, buff=0.10)
        llave = VGroup(brace, rot)

    return OndaRegla(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                     _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                     eje, curva, llave, params)


class RelojLuz(_Pieza):
    """La definicion del metro: la barra de 1 m y el pulso que la recorre.

    Atributos: `.barra`, `.pulso`, `.halo`, `.lectura` (Text HUD),
    `.definicion` (el rotulo "1 m = c x 1/299 792 458 s"), `.t` (el valor
    actual)."""

    def __init__(self, ancla_a, ancla_b, barra, topes, llave, definicion,
                 halo, pulso, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, barra, topes, llave, definicion,
                         halo, pulso, lectura, **kwargs)
        self._ancla_a = ancla_a            # extremo izquierdo de la barra
        self._ancla_b = ancla_b            # extremo derecho de la barra
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.barra = barra
        self.topes = topes
        self.llave = llave
        self.definicion = definicion
        self.halo = halo
        self.pulso = pulso
        self.lectura = lectura
        self._params = params
        self.t = 0.0

    def a_t(self, t):
        """MUTA la pieza: pone el pulso donde esta la luz en el instante t.

        `t` va en unidades de 1/c segundos, o sea que t ES la distancia
        recorrida en METROS: t = 1 es el metro completo, que la luz tarda
        1/299 792 458 s = 3.336 ns. Fuera de [0, 1] se recorta.
        """
        self.t = float(np.clip(float(t), 0.0, 1.0))
        p = self._params
        x = -p["ancho"] / 2.0 + p["ancho"] * self.t
        destino = self._punto((x, 0.0))
        self.pulso.move_to(destino)
        self.halo.move_to(destino)
        ns = self.t / C_LUZ * 1e9
        self.lectura = self._relectura(
            self.lectura, f"t = {ns:5.3f} ns    d = {self.t:4.3f} m",
            font_size=17, color=C_MEDIDA)
        return self


def reloj_luz(ancho=5.4, color_pulso=C_HAZ, color_barra=C_OBJETO):
    """El metro que define la luz: una barra de 1 m y el pulso que la
    recorre en 1/299 792 458 s.

    Desde 1983 la velocidad de la luz es un numero EXACTO por definicion y
    el metro es lo que se deduce: la distancia que recorre la luz en ese
    tiempo. La barra mide `ancho` unidades de escena y representa 1 m; el
    pulso tarda 3.336 ns reales en cruzarla.
    """
    ancho = float(ancho)
    y0 = 0.0
    barra = Line(np.array([-ancho / 2.0, y0, 0.0]),
                 np.array([ancho / 2.0, y0, 0.0]),
                 stroke_width=4.0, color=color_barra)
    barra.set_stroke(opacity=0.55)
    topes = VGroup(*[
        Line(np.array([s * ancho / 2.0, y0 - 0.16, 0.0]),
             np.array([s * ancho / 2.0, y0 + 0.16, 0.0]),
             stroke_width=3.0, color=color_barra)
        for s in (-1, 1)])

    guia = Line(np.array([-ancho / 2.0, y0 - 0.30, 0.0]),
                np.array([ancho / 2.0, y0 - 0.30, 0.0]), stroke_width=0.1)
    brace = Brace(guia, DOWN, buff=0.04, color=C_EJE)
    rot = _texto_hud("1 m", font_size=20, color=color_barra)
    rot.next_to(brace, DOWN, buff=0.10)
    llave = VGroup(brace, rot)

    definicion = _texto_hud("1 m = c x 1 / 299 792 458 s", font_size=17,
                            color=CODE_MUTED)
    definicion.move_to(np.array([0.0, y0 + 0.98, 0.0]))

    halo = Dot(np.array([-ancho / 2.0, y0, 0.0]), radius=0.17,
               color=color_pulso)
    halo.set_fill(color_pulso, opacity=0.22)
    halo.set_stroke(width=0)
    pulso = Dot(np.array([-ancho / 2.0, y0, 0.0]), radius=0.075,
                color=color_pulso)

    lectura = _texto_hud("t = 0.000 ns    d = 0.000 m", font_size=17,
                         color=C_MEDIDA)
    lectura.move_to(np.array([0.0, y0 + 0.52, 0.0]))

    params = {"ancho": ancho, "color_pulso": color_pulso}
    return RelojLuz(_ancla(np.array([-ancho / 2.0, y0, 0.0])),
                    _ancla(np.array([ancho / 2.0, y0, 0.0])),
                    barra, topes, llave, definicion, halo, pulso, lectura,
                    params)


class TrenCoherencia(_Pieza):
    """Tren de ondas de longitud finita: la senoide por su envolvente.

    Atributos: `.curva`, `.envolvente` (las dos gaussianas punteadas),
    `.etiqueta`, `.lc_rel` (la longitud del tren como fraccion del ancho
    dibujado)."""

    def __init__(self, ancla_a, ancla_b, eje, envolvente, curva, etiqueta,
                 params, **kwargs):
        hijos = [ancla_a, ancla_b, eje, envolvente, curva]
        if etiqueta is not None:
            hijos.append(etiqueta)
        super().__init__(*hijos, **kwargs)
        self._ancla_a = ancla_a
        self._ancla_b = ancla_b
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.eje = eje
        self.envolvente = envolvente
        self.curva = curva
        self.etiqueta = etiqueta
        self._params = params
        self.lc_rel = params["lc_rel"]

    def con_longitud(self, lc_rel, etiqueta=None):
        """Pieza GEMELA con otra longitud de coherencia, ya escalada y
        colocada encima de esta (para `Transform`): asi se pasa del LED
        (tren corto) al HeNe (tren largo) sin que salte el dibujo."""
        p = self._params
        otra = tren_coherencia(lc_rel, ancho=p["ancho"],
                               n_periodos=p["n_periodos"],
                               amplitud=p["amplitud"], color=p["color"],
                               etiqueta=(p["etiqueta"] if etiqueta is None
                                         else etiqueta),
                               muestras=p["muestras"])
        return self._alinear(otra)


def tren_coherencia(lc_rel=0.35, ancho=5.2, n_periodos=11, amplitud=0.6,
                    color=C_ONDA, etiqueta=None, muestras=321):
    """Un tren de ondas de longitud finita: la regla no es infinita.

    La envolvente es exp(-(2 x/(lc_rel*ancho))^2), asi que `lc_rel` es la
    longitud de coherencia expresada como FRACCION del ancho dibujado
    (lc_rel = 1 -> el tren ocupa toda la pieza). La cifra fisica la pone
    `longitud_coherencia`: el LED (20 um) y el HeNe (0.40 m) se diferencian
    en 20 000 veces, que no cabe en una pantalla — por eso el dibujo es
    cualitativo y el numero va rotulado.
    """
    muestras = _validar("tren_coherencia.muestras", muestras, PUNTOS_MAX)
    n_periodos = _validar("tren_coherencia.n_periodos", n_periodos,
                          FRANJAS_MAX)
    ancho, amplitud = float(ancho), float(amplitud)
    lc_rel = float(np.clip(float(lc_rel), 0.02, 2.0))
    k = TAU * n_periodos / ancho
    sigma = max(lc_rel * ancho / 2.0, 1e-3)

    x = np.linspace(-ancho / 2.0, ancho / 2.0, muestras)
    env = np.exp(-((x / sigma) ** 2))
    y = amplitud * env * np.cos(k * x)

    eje = Line(np.array([-ancho / 2.0, 0.0, 0.0]),
               np.array([ancho / 2.0, 0.0, 0.0]),
               stroke_width=1.2, color=C_EJE)
    curva = _poligonal(np.column_stack([x, y]), color, 3.0)
    sup = _poligonal(np.column_stack([x, amplitud * env]), color, 1.6, 0.45)
    inf = _poligonal(np.column_stack([x, -amplitud * env]), color, 1.6, 0.45)
    envolvente = VGroup(DashedVMobject(sup, num_dashes=44),
                        DashedVMobject(inf, num_dashes=44))

    rot = None
    if etiqueta is not None:
        rot = _texto_hud(etiqueta, font_size=18, color=C_MEDIDA)
        rot.move_to(np.array([0.0, -amplitud - 0.34, 0.0]))

    params = {"lc_rel": lc_rel, "ancho": ancho, "n_periodos": n_periodos,
              "amplitud": amplitud, "color": color, "etiqueta": etiqueta,
              "muestras": muestras}
    return TrenCoherencia(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                          _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                          eje, envolvente, curva, rot, params)


class SumaOndas(_Pieza):
    """Tres senoides apiladas: a, b y su suma.

    Atributos: `.onda_a`, `.onda_b`, `.suma`, `.lectura`, `.fase` (rad, la
    de b respecto de a)."""

    def __init__(self, ancla_a, ancla_b, ejes, onda_a, onda_b, suma,
                 rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, ejes, onda_a, onda_b, suma,
                         rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a
        self._ancla_b = ancla_b
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, params["y_a"], 0.0)
        self.ejes = ejes
        self.onda_a = onda_a
        self.onda_b = onda_b
        self.suma = suma
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.fase = params["fase"]

    def _perfiles(self, fase):
        p = self._params
        x = np.linspace(-p["ancho"] / 2.0, p["ancho"] / 2.0, p["muestras"])
        a = p["amplitud"] * np.cos(p["k"] * x)
        b = p["amplitud"] * np.cos(p["k"] * x - fase)
        return x, a, b

    def amplitud_suma(self):
        """Amplitud RELATIVA de la suma (1 = la de una sola onda): vale
        2|cos(fase/2)|, o sea 2 en constructiva y 0 en destructiva."""
        return 2.0 * abs(math.cos(self.fase / 2.0))

    def a_fase(self, fase):
        """MUTA la pieza: cambia la fase de b (rad) y recalcula la suma y
        la lectura. Devuelve self."""
        self.fase = float(fase)
        p = self._params
        x, a, b = self._perfiles(self.fase)
        _fijar(self.onda_b,
               self._a_escena(np.column_stack([x, b + p["y_b"]])))
        _fijar(self.suma,
               self._a_escena(np.column_stack([x, a + b + p["y_s"]])))
        grados = math.degrees(self.fase) % 360.0
        self.lectura = self._relectura(
            self.lectura,
            f"fase = {grados:5.1f} grados   amplitud = "
            f"{self.amplitud_suma():.2f}",
            font_size=17, color=C_MEDIDA, borde=LEFT)
        return self


def suma_ondas(fase=0.0, ancho=5.2, n_periodos=3, amplitud=0.34,
               color_a=C_ONDA, color_b=C_HAZ, color_suma=C_FRANJA,
               muestras=241):
    """Dos ondas y su suma: la interferencia se ve en la tercera linea.

    Arriba la onda a (ambar), en medio la b (roja, la que corre), abajo
    a + b (violeta: lo que la luz DIBUJA). Con fase 0 la suma vale el
    doble; con 180 grados se cancela. La escala vertical de la suma es la
    MISMA que la de a y b, para que el doble se vea doble.
    """
    muestras = _validar("suma_ondas.muestras", muestras, PUNTOS_MAX)
    n_periodos = _validar("suma_ondas.n_periodos", n_periodos, FRANJAS_MAX)
    ancho, amplitud = float(ancho), float(amplitud)
    k = TAU * n_periodos / ancho
    y_a, y_b, y_s = 1.28, 0.35, -1.05

    x = np.linspace(-ancho / 2.0, ancho / 2.0, muestras)
    a = amplitud * np.cos(k * x)
    b = amplitud * np.cos(k * x - float(fase))

    ejes = VGroup(*[
        Line(np.array([-ancho / 2.0, y, 0.0]),
             np.array([ancho / 2.0, y, 0.0]), stroke_width=1.1, color=C_EJE)
        for y in (y_a, y_b, y_s)])

    onda_a = _poligonal(np.column_stack([x, a + y_a]), color_a, 2.8)
    onda_b = _poligonal(np.column_stack([x, b + y_b]), color_b, 2.8)
    suma = _poligonal(np.column_stack([x, a + b + y_s]), color_suma, 3.2)

    rotulos = VGroup()
    for texto, y, col in (("onda a", y_a, color_a), ("onda b", y_b, color_b),
                          ("a + b", y_s, color_suma)):
        t = _texto_hud(texto, font_size=16, color=col)
        t.move_to(np.array([-ancho / 2.0 - 0.62, y, 0.0]))
        rotulos.add(t)

    grados = math.degrees(float(fase)) % 360.0
    amp = 2.0 * abs(math.cos(float(fase) / 2.0))
    lectura = _texto_hud(f"fase = {grados:5.1f} grados   amplitud = "
                         f"{amp:.2f}", font_size=17, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, y_s - 0.92, 0.0]), aligned_edge=ORIGIN)

    params = {"ancho": ancho, "amplitud": amplitud, "k": k,
              "muestras": muestras, "fase": float(fase),
              "y_a": y_a, "y_b": y_b, "y_s": y_s}
    return SumaOndas(_ancla(np.array([-ancho / 2.0, y_a, 0.0])),
                     _ancla(np.array([ancho / 2.0, y_a, 0.0])),
                     ejes, onda_a, onda_b, suma, rotulos, lectura, params)


# =====================================================================
# 1.2 — La interferencia: contar franjas
# =====================================================================
class PatronFranjas(_Pieza):
    """Franjas rectas: una fila de barras verticales cuya opacidad sigue
    `intensidad_dos_haces`.

    Se hace con barras (no con una imagen) a proposito: asi `.a_fase()`
    solo cambia opacidades y se puede animar con un updater, y `Transform`
    hacia la gemela de `.con_visibilidad()` funciona.

    Atributos: `.barras`, `.marco`, `.fase`, `.V`, `.n_franjas`.
    """

    def __init__(self, ancla_a, ancla_b, marco, barras, params, **kwargs):
        super().__init__(ancla_a, ancla_b, marco, barras, **kwargs)
        self._ancla_a = ancla_a            # borde izquierdo del patron
        self._ancla_b = ancla_b            # borde derecho
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.marco = marco
        self.barras = barras
        self._params = params
        self.fase = params["fase"]
        self.V = params["V"]
        self.n_franjas = params["n_franjas"]

    def intensidades(self, fase=None, V=None):
        """El perfil I(x) de las barras, en [0, 1]."""
        p = self._params
        f = self.fase if fase is None else float(fase)
        v = self.V if V is None else float(V)
        return intensidad_dos_haces(f + TAU * p["n_franjas"] * p["u"], v)

    def a_fase(self, fase):
        """MUTA el patron: corre las franjas a esa fase (rad). 2 pi es una
        franja entera. Devuelve self."""
        self.fase = float(fase)
        for barra, i in zip(self.barras, self.intensidades()):
            barra.set_fill(self._params["color"],
                           opacity=0.05 + 0.95 * float(i))
        return self

    def a_visibilidad(self, V):
        """MUTA el patron: cambia la visibilidad sin rehacerlo."""
        self.V = float(np.clip(float(V), 0.0, 1.0))
        return self.a_fase(self.fase)

    def con_visibilidad(self, V):
        """Pieza GEMELA con otra visibilidad, ya escalada y colocada encima
        (para `Transform`): franjas nitidas (V = 1) contra franjas lavadas
        (V = 0.3)."""
        p = self._params
        otra = patron_franjas(self.fase, V, n_franjas=p["n_franjas"],
                              ancho=p["ancho"], alto=p["alto"],
                              n_barras=p["n_barras"], color=p["color"],
                              marco=p["con_marco"])
        return self._alinear(otra)


def patron_franjas(fase0=0.0, V=1.0, n_franjas=6, ancho=3.2, alto=1.3,
                   n_barras=96, color=C_FRANJA, marco=True):
    """Las franjas que pinta la interferencia: I = (1 + V cos fase)/2.

    `n_franjas` franjas caben en el ancho; `fase0` las corre (2 pi = una
    franja) y `V` es la visibilidad. Es lo que se ve en el detector de un
    Michelson y lo que hay que CONTAR para medir.
    """
    n_barras = _validar("patron_franjas.n_barras", n_barras, 4 * CELDAS_MAX)
    n_franjas = _validar("patron_franjas.n_franjas", n_franjas, FRANJAS_MAX)
    ancho, alto = float(ancho), float(alto)
    V = float(np.clip(float(V), 0.0, 1.0))

    u = (np.arange(n_barras) + 0.5) / n_barras           # 0..1
    x = -ancho / 2.0 + u * ancho
    inten = intensidad_dos_haces(float(fase0) + TAU * n_franjas * u, V)

    paso = ancho / n_barras
    barras = VGroup()
    for xi, ii in zip(x, inten):
        b = Rectangle(width=paso * 1.02, height=alto, stroke_width=0.0,
                      color=color)
        b.set_fill(color, opacity=0.05 + 0.95 * float(ii))
        b.move_to(np.array([xi, 0.0, 0.0]))
        barras.add(b)

    m = Rectangle(width=ancho, height=alto, stroke_width=1.6, color=C_EJE)
    m.set_fill(opacity=0.0)
    if not marco:
        m.set_stroke(opacity=0.0)

    params = {"ancho": ancho, "alto": alto, "n_franjas": n_franjas,
              "n_barras": n_barras, "color": color, "fase": float(fase0),
              "V": V, "u": u, "con_marco": marco}
    return PatronFranjas(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                         _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                         m, barras, params)


class Michelson(_Pieza):
    """El interferometro de Michelson en planta.

    Atributos: `.fuente`, `.divisor`, `.espejo_fijo`, `.espejo_movil`,
    `.detector`, `.franjas` (un `patron_franjas`), `.lectura`,
    `.desplazamiento_nm` (el estado actual).
    """

    def __init__(self, ancla_a, ancla_b, mobiliario, haces, fuente, divisor,
                 espejo_fijo, espejo_movil, flecha, detector, franjas,
                 rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, mobiliario, haces, fuente,
                         divisor, espejo_fijo, espejo_movil, flecha,
                         detector, franjas, rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a           # extremo izquierdo del esquema
        self._ancla_b = ancla_b           # extremo derecho
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.mobiliario = mobiliario
        self.haces = haces                # VGroup(izq, arriba, der, abajo)
        self.brazo_movil = haces[2]
        self.fuente = fuente
        self.divisor = divisor
        self.espejo_fijo = espejo_fijo
        self.espejo_movil = espejo_movil
        self.flecha = flecha
        self.detector = detector
        self.franjas = franjas
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.desplazamiento_nm = 0.0

    def franjas_contadas(self, d_nm=None):
        """Franjas que han pasado para ese desplazamiento (en nm): usa
        `franjas_por_desplazamiento`. 949.2 nm -> 3.00 franjas."""
        d = self.desplazamiento_nm if d_nm is None else float(d_nm)
        return franjas_por_desplazamiento(d * 1e-9, self._params["lam"])

    def a_desplazamiento(self, d_nm):
        """MUTA la pieza: mueve el espejo movil `d_nm` NANOMETROS y corre
        las franjas del detector la fase que toca (2 pi por franja).

        El movimiento esta EXAGERADO: `nm_por_unidad` nanometros reales se
        dibujan como 1 unidad de escena (por omision 2400, o sea que las
        3 franjas de 949 nm se ven como 0.40 unidades), y ademas se recorta
        a +-`tope_local` unidades para que el espejo no se salga del
        esquema. La FISICA (la cuenta de franjas) no se toca: sale de
        `franjas_por_desplazamiento`.
        """
        p = self._params
        self.desplazamiento_nm = float(d_nm)
        dx = float(d_nm) / p["nm_por_unidad"]
        dx = float(np.clip(dx, -p["tope_local"], p["tope_local"]))
        x_m = p["x_movil"] + dx

        self.espejo_movil.move_to(self._punto((x_m, 0.0)))
        _fijar(self.brazo_movil,
               self._a_escena([(p["x_divisor"] + 0.30, 0.0),
                               (x_m - 0.05, 0.0)]))
        self.flecha.move_to(self._punto((x_m, -0.62)))

        n = self.franjas_contadas()
        self.franjas.a_fase(p["fase0"] + TAU * n)
        self.lectura = self._relectura(
            self.lectura,
            f"d = {float(d_nm):7.1f} nm    N = {n:5.2f} franjas",
            font_size=17, color=C_MEDIDA)
        return self


def michelson(lam=LAMBDA_HENE, ancho=6.6, nm_por_unidad=2400.0,
              n_franjas=5, fase0=0.0):
    """El interferometro de Michelson: fuente, divisor, dos espejos y un
    detector que ve franjas.

    La luz roja sale de la fuente, el divisor la parte en dos, cada mitad
    va a un espejo y vuelve, y las dos se juntan en el detector. Si un
    espejo se mueve lam/2 (`paso_franja`), la franja se corre entera: por
    eso contar franjas es medir con una regla de 316 nm.

    El esquema mide `ancho` unidades de escena (por omision 6.6 de ancho y
    unas 4.7 de alto). El desplazamiento del espejo va EXAGERADO: ver
    `.a_desplazamiento`.
    """
    ancho = float(ancho)
    esc = ancho / 6.6                       # el dibujo canonico mide 6.6
    x_fuente, x_divisor, x_movil = -2.55, 0.0, 2.05
    y_fijo, y_det = 1.72, -1.72

    # --- mobiliario ---------------------------------------------------
    divisor = Line(np.array([-0.30, -0.30, 0.0]),
                   np.array([0.30, 0.30, 0.0]),
                   stroke_width=4.0, color=CODE_MUTED)
    divisor.set_stroke(opacity=0.8)

    cuerpo_fuente = RoundedRectangle(width=0.62, height=0.40,
                                     corner_radius=0.08, stroke_width=2.2,
                                     color=C_HAZ)
    cuerpo_fuente.set_fill(C_HAZ, opacity=0.16)
    cuerpo_fuente.move_to(np.array([x_fuente, 0.0, 0.0]))
    fuente = VGroup(cuerpo_fuente)

    espejo_fijo = Rectangle(width=1.05, height=0.11, stroke_width=1.6,
                            color=C_OBJETO)
    espejo_fijo.set_fill(C_OBJETO, opacity=0.85)
    espejo_fijo.move_to(np.array([x_divisor, y_fijo, 0.0]))

    espejo_movil = Rectangle(width=0.11, height=1.05, stroke_width=1.6,
                             color=C_OBJETO)
    espejo_movil.set_fill(C_OBJETO, opacity=0.85)
    espejo_movil.move_to(np.array([x_movil, 0.0, 0.0]))

    flecha = DoubleArrow(np.array([-0.30, 0.0, 0.0]),
                         np.array([0.30, 0.0, 0.0]), buff=0.0,
                         stroke_width=2.0, color=C_MEDIDA, tip_length=0.11)
    flecha.move_to(np.array([x_movil, -0.62, 0.0]))

    marco_det = Rectangle(width=1.72, height=1.02, stroke_width=2.0,
                          color=C_MEDIDA)
    marco_det.set_fill(C_MEDIDA, opacity=0.05)
    marco_det.move_to(np.array([x_divisor, y_det, 0.0]))
    franjas = patron_franjas(fase0, 1.0, n_franjas=n_franjas, ancho=1.46,
                             alto=0.72, n_barras=72, marco=False)
    franjas.move_to(np.array([x_divisor, y_det, 0.0]))
    detector = VGroup(marco_det)

    # --- los haces ----------------------------------------------------
    haz_izq = _poligonal([(x_fuente + 0.34, 0.0), (x_divisor - 0.30, 0.0)],
                         C_HAZ, 3.0)
    haz_arr = _poligonal([(x_divisor, 0.30), (x_divisor, y_fijo - 0.09)],
                         C_HAZ, 3.0)
    haz_der = _poligonal([(x_divisor + 0.30, 0.0), (x_movil - 0.05, 0.0)],
                         C_HAZ, 3.0)
    haz_aba = _poligonal([(x_divisor, -0.30), (x_divisor, y_det + 0.52)],
                         C_HAZ, 3.0)
    haces = VGroup(haz_izq, haz_arr, haz_der, haz_aba)

    # --- rotulos ------------------------------------------------------
    rotulos = VGroup()
    for texto, pos, col, direccion in (
            ("laser", (x_fuente, -0.42), C_HAZ, DOWN),
            ("divisor", (-0.98, 0.66), CODE_MUTED, ORIGIN),
            ("espejo fijo", (x_divisor, y_fijo + 0.30), C_OBJETO, ORIGIN),
            ("espejo movil", (x_movil + 0.06, 1.02), C_OBJETO, ORIGIN),
            ("detector", (x_divisor, y_det - 0.72), C_MEDIDA, ORIGIN)):
        t = _texto_hud(texto, font_size=16, color=col)
        t.move_to(np.array([pos[0], pos[1], 0.0]))
        rotulos.add(t)

    lectura = _texto_hud("d =     0.0 nm    N =  0.00 franjas",
                         font_size=17, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, y_det - 1.06, 0.0]))

    mobiliario = VGroup(divisor)
    params = {"ancho": ancho, "lam": float(lam), "x_movil": x_movil,
              "x_divisor": x_divisor, "nm_por_unidad": float(nm_por_unidad),
              "tope_local": 0.62, "fase0": float(fase0),
              "n_franjas": n_franjas}
    pieza = Michelson(_ancla(np.array([-3.3, 0.0, 0.0])),
                      _ancla(np.array([3.3, 0.0, 0.0])),
                      mobiliario, haces, fuente, divisor, espejo_fijo,
                      espejo_movil, flecha, detector, franjas, rotulos,
                      lectura, params)
    if abs(esc - 1.0) > 1e-9:
        pieza.scale(esc)
    return pieza


class ContadorFranjas(_Pieza):
    """La curva I(d) con un punto que avanza y el contador de franjas.

    Atributos: `.curva`, `.punto`, `.guia`, `.lectura_d`, `.lectura_n`,
    `.d_nm` (estado)."""

    def __init__(self, ancla_a, ancla_b, ejes, ticks, etiquetas, curva,
                 guia, punto, lectura_d, lectura_n, params, **kwargs):
        super().__init__(ancla_a, ancla_b, ejes, ticks, etiquetas, curva,
                         guia, punto, lectura_d, lectura_n, **kwargs)
        self._ancla_a = ancla_a           # origen de los ejes
        self._ancla_b = ancla_b           # extremo derecho del eje x
        self._largo_ref = params["ancho"]
        self._p0 = (0.0, 0.0, 0.0)
        self.ejes = ejes
        self.ticks = ticks
        self.etiquetas = etiquetas
        self.curva = curva
        self.guia = guia
        self.punto = punto
        self.lectura_d = lectura_d
        self.lectura_n = lectura_n
        self._params = params
        self.d_nm = 0.0

    def punto_en(self, d_nm):
        """Punto de escena de la curva para ese desplazamiento (nm)."""
        p = self._params
        d = float(np.clip(float(d_nm), 0.0, p["d_max_nm"]))
        x = d / p["d_max_nm"] * p["ancho"]
        n = franjas_por_desplazamiento(d * 1e-9, p["lam"])
        y = float(intensidad_dos_haces(TAU * n)) * p["alto"]
        return self._punto((x, y))

    def a_desplazamiento(self, d_nm):
        """MUTA la pieza: lleva el punto a ese desplazamiento (nm) y
        actualiza el contador. Devuelve self."""
        p = self._params
        self.d_nm = float(np.clip(float(d_nm), 0.0, p["d_max_nm"]))
        destino = self.punto_en(self.d_nm)
        self.punto.move_to(destino)
        base = self._punto((self.d_nm / p["d_max_nm"] * p["ancho"], 0.0))
        _fijar(self.guia, np.array([base, destino]))
        n = franjas_por_desplazamiento(self.d_nm * 1e-9, p["lam"])
        self.lectura_d = self._relectura(
            self.lectura_d, f"d = {self.d_nm:7.1f} nm", font_size=18,
            color=C_MEDIDA)
        self.lectura_n = self._relectura(
            self.lectura_n, f"N = {n:5.2f} franjas", font_size=18,
            color=C_MEDIDA)
        return self


def contador_franjas(lam=LAMBDA_HENE, d_max_nm=1600.0, ancho=5.4, alto=1.9):
    """La intensidad contra el desplazamiento del espejo: cada maximo es
    una franja, cada franja vale `paso_franja` = lam/2 = 316.4 nm.

    Los ticks del eje x caen justo en los multiplos de lam/2, asi que el
    dibujo DEMUESTRA la cifra en vez de afirmarla. El origen de los ejes es
    el ancla: la curva ocupa `ancho` x `alto` unidades hacia arriba y a la
    derecha.
    """
    ancho, alto, d_max_nm = float(ancho), float(alto), float(d_max_nm)
    lam = float(lam)
    paso_nm = paso_franja(lam) * 1e9

    ejes = VGroup(
        Line(ORIGIN, np.array([ancho, 0.0, 0.0]), stroke_width=2.0,
             color=C_EJE),
        Line(ORIGIN, np.array([0.0, alto * 1.12, 0.0]), stroke_width=2.0,
             color=C_EJE))

    d = np.linspace(0.0, d_max_nm, 361)
    n = franjas_por_desplazamiento(d * 1e-9, lam)
    y = intensidad_dos_haces(TAU * n) * alto
    curva = _poligonal(np.column_stack([d / d_max_nm * ancho, y]),
                       C_FRANJA, 3.0)

    ticks, etiquetas = VGroup(), VGroup()
    k = 0
    while k * paso_nm <= d_max_nm + 1e-9:
        x = k * paso_nm / d_max_nm * ancho
        ticks.add(Line(np.array([x, 0.0, 0.0]), np.array([x, -0.13, 0.0]),
                       stroke_width=1.8, color=C_EJE))
        if k % 2 == 0:
            t = _texto_hud(f"{k * paso_nm:.0f}", font_size=13,
                           color=CODE_MUTED)
            t.move_to(np.array([x, -0.30, 0.0]))
            etiquetas.add(t)
        k += 1
    t_eje = _texto_hud("d del espejo (nm)", font_size=14, color=CODE_MUTED)
    t_eje.move_to(np.array([ancho * 0.5, -0.58, 0.0]))
    etiquetas.add(t_eje)
    t_i = _texto_hud("I", font_size=15, color=CODE_MUTED)
    t_i.move_to(np.array([-0.24, alto * 1.06, 0.0]))
    etiquetas.add(t_i)

    guia = _poligonal([(0.0, 0.0), (0.0, alto)], C_MEDIDA, 1.4, 0.5)
    punto = Dot(np.array([0.0, alto, 0.0]), radius=0.075, color=C_MEDIDA)

    lectura_d = _texto_hud("d =     0.0 nm", font_size=18, color=C_MEDIDA)
    lectura_d.move_to(np.array([ancho * 0.02, alto + 0.80, 0.0]),
                      aligned_edge=LEFT)
    lectura_n = _texto_hud("N =  0.00 franjas", font_size=18, color=C_MEDIDA)
    lectura_n.move_to(np.array([ancho * 0.52, alto + 0.80, 0.0]),
                      aligned_edge=LEFT)

    params = {"ancho": ancho, "alto": alto, "d_max_nm": d_max_nm,
              "lam": lam}
    return ContadorFranjas(_ancla(ORIGIN), _ancla(np.array([ancho, 0.0, 0.0])),
                           ejes, ticks, etiquetas, curva, guia, punto,
                           lectura_d, lectura_n, params)


class CeldaGas(_Pieza):
    """La celda que se llena de gas en un brazo del interferometro.

    Atributos: `.marco`, `.relleno`, `.haz`, `.lectura_n`, `.lectura_f`,
    `.n_menos_1` (estado), `.franjas_actuales`."""

    def __init__(self, ancla_a, ancla_b, haz, marco, relleno, titulo,
                 lectura_n, lectura_f, params, **kwargs):
        super().__init__(ancla_a, ancla_b, haz, relleno, marco, titulo,
                         lectura_n, lectura_f, **kwargs)
        self._ancla_a = ancla_a          # borde izquierdo de la celda
        self._ancla_b = ancla_b          # borde derecho
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.haz = haz
        self.marco = marco
        self.relleno = relleno
        self.titulo = titulo
        self.lectura_n = lectura_n
        self.lectura_f = lectura_f
        self._params = params
        self.n_menos_1 = 0.0
        self.franjas_actuales = 0.0

    def a_indice(self, n_menos_1):
        """MUTA la pieza: llena la celda hasta ese (n - 1) y DEVUELVE las
        franjas acumuladas (`franjas_indice`), que es el numero que se
        rotula. Con 10 cm de aire (n - 1 = 2.7e-4) salen 85.3 franjas.

        El nivel de llenado es proporcional a (n-1)/`n_max`: es una barra
        de progreso, no una densidad fisica.
        """
        p = self._params
        self.n_menos_1 = float(n_menos_1)
        frac = float(np.clip(self.n_menos_1 / p["n_max"], 0.0, 1.0))
        esc = self._escala_actual()
        h_local = max(frac * p["alto_int"], 1e-3)
        self.relleno.stretch_to_fit_height(h_local * esc)
        self.relleno.stretch_to_fit_width(p["ancho_int"] * esc)
        self.relleno.move_to(self._punto((0.0, -p["alto_int"] / 2.0
                                          + h_local / 2.0)))
        self.franjas_actuales = franjas_indice(p["L"], self.n_menos_1,
                                               p["lam"])
        self.lectura_n = self._relectura(
            self.lectura_n, f"n - 1 = {self.n_menos_1:.2e}", font_size=18,
            color=C_OBJETO)
        self.lectura_f = self._relectura(
            self.lectura_f, f"{self.franjas_actuales:5.1f} franjas",
            font_size=18, color=C_MEDIDA)
        return self.franjas_actuales


def celda_gas(L=0.10, lam=LAMBDA_HENE, n_max=2.7e-4, ancho=2.9, alto=1.35):
    """Una celda de `L` metros en un brazo del interferometro: al llenarla
    de aire pasan `franjas_indice(L, n-1, lam)` franjas.

    Es el truco de medir el indice del aire con luz: no se toca el gas, se
    cuentan las franjas que pasan mientras entra. 10 cm y n - 1 = 2.7e-4
    dan 85.3 franjas con el HeNe.
    """
    ancho, alto = float(ancho), float(alto)
    ancho_int, alto_int = ancho - 0.16, alto - 0.16

    haz = _poligonal([(-ancho / 2.0 - 0.55, 0.0), (ancho / 2.0 + 0.55, 0.0)],
                     C_HAZ, 3.0)
    marco = Rectangle(width=ancho, height=alto, stroke_width=2.4,
                      color=C_OBJETO)
    marco.set_fill(opacity=0.0)
    relleno = Rectangle(width=ancho_int, height=0.001, stroke_width=0.0,
                        color=C_OBJETO)
    relleno.set_fill(C_OBJETO, opacity=0.30)
    relleno.move_to(np.array([0.0, -alto_int / 2.0, 0.0]))

    titulo = _texto_hud(f"celda {L * 100:.0f} cm", font_size=17,
                        color=C_OBJETO)
    titulo.move_to(np.array([0.0, alto / 2.0 + 0.26, 0.0]))
    lectura_n = _texto_hud("n - 1 = 0.00e+00", font_size=18, color=C_OBJETO)
    lectura_n.move_to(np.array([ancho / 2.0 + 0.75, 0.26, 0.0]),
                      aligned_edge=LEFT)
    lectura_f = _texto_hud("  0.0 franjas", font_size=18, color=C_MEDIDA)
    lectura_f.move_to(np.array([ancho / 2.0 + 0.75, -0.14, 0.0]),
                      aligned_edge=LEFT)

    params = {"ancho": ancho, "alto": alto, "ancho_int": ancho_int,
              "alto_int": alto_int, "L": float(L), "lam": float(lam),
              "n_max": float(n_max)}
    return CeldaGas(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                    _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                    haz, marco, relleno, titulo, lectura_n, lectura_f,
                    params)


# =====================================================================
# 1.3 — La difraccion: el limite de la regla
# =====================================================================
class RendijaPatron(_Pieza):
    """La rendija y su patron sinc^2.

    Atributos: `.rendija` (las dos mordazas), `.curva`, `.ceros` (las
    lineas punteadas del primer cero), `.a_rel` (ancho de la rendija en
    longitudes de onda), `.sin_primer_cero`."""

    def __init__(self, ancla_a, ancla_b, entrada, rendija, ejes, curva,
                 ceros, rotulos, params, **kwargs):
        super().__init__(ancla_a, ancla_b, entrada, rendija, ejes, curva,
                         ceros, rotulos, **kwargs)
        self._ancla_a = ancla_a          # extremo izquierdo del eje x
        self._ancla_b = ancla_b          # extremo derecho
        self._largo_ref = params["ancho_grafica"]
        self._p0 = (params["x0"], params["y0"], 0.0)
        self.entrada = entrada
        self.rendija = rendija
        self.ejes = ejes
        self.curva = curva
        self.ceros = ceros
        self.rotulos = rotulos
        self._params = params
        self.a_rel = params["a_rel"]
        self.sin_primer_cero = 1.0 / params["a_rel"]

    def primer_cero(self, signo=1):
        """Punto de escena donde el patron toca cero por primera vez."""
        p = self._params
        s = float(signo) * self.sin_primer_cero
        x = p["x0"] + (s / p["s_max"] + 1.0) / 2.0 * p["ancho_grafica"]
        return self._punto((x, p["y0"]))

    def con_ancho(self, a_rel):
        """Pieza GEMELA con otra rendija, ya escalada y colocada encima
        (para `Transform`): a la mitad de ancho, el doble de patron."""
        p = self._params
        otra = rendija_patron(a_rel, lam=p["lam"], ancho=p["ancho"],
                              alto=p["alto"], muestras=p["muestras"])
        return self._alinear(otra)


def rendija_patron(a_rel=8.0, lam=LAMBDA_HENE, ancho=6.4, alto=1.9,
                   muestras=401):
    """Una rendija de ancho a = `a_rel` x lam y el patron que produce.

    A la izquierda las dos mordazas con el hueco (el hueco DIBUJADO es
    proporcional a `a_rel`, no esta a escala con el resto); a la derecha
    la curva I(sin theta) = sinc^2(a sin/lam) con los primeros ceros
    marcados en sin(theta) = +-lam/a. Cuanto MAS angosta la rendija, MAS
    ancho el patron: ahi empieza el limite de la regla.

    El eje de angulos es FIJO (+-`s_max` en sin theta), asi que al cambiar
    `a_rel` con `.con_ancho()` lo que se ve moverse es la curva.
    """
    muestras = _validar("rendija_patron.muestras", muestras, PUNTOS_MAX)
    a_rel = float(a_rel)
    if a_rel <= 0.5:
        raise ValueError(f"rendija_patron: a_rel={a_rel} <= 0.5 lam")
    ancho, alto = float(ancho), float(alto)
    s_max = 0.36
    x_rendija = -ancho / 2.0 + 0.95
    x0 = x_rendija + 0.90
    ancho_grafica = ancho / 2.0 - 0.05 - x0
    y0 = -alto / 2.0

    # --- la rendija ---------------------------------------------------
    hueco = float(np.clip(0.42 * a_rel / 8.0, 0.05, 0.95))
    alto_mordaza = 1.7
    mordazas = VGroup()
    for s in (-1, 1):
        m = Rectangle(width=0.34, height=alto_mordaza, stroke_width=1.4,
                      color=C_EJE)
        m.set_fill(C_EJE, opacity=0.85)
        m.move_to(np.array([x_rendija + s * (hueco / 2.0 + 0.17), 0.0, 0.0]))
        mordazas.add(m)

    x_mordaza = x_rendija - hueco / 2.0 - 0.34
    entrada = VGroup()
    for y in (-0.5, 0.0, 0.5):
        entrada.add(Arrow(np.array([x_mordaza - 0.72, y, 0.0]),
                          np.array([x_mordaza - 0.12, y, 0.0]), buff=0.0,
                          stroke_width=3.0, color=C_HAZ,
                          max_tip_length_to_length_ratio=0.26))

    # --- la grafica ---------------------------------------------------
    ejes = VGroup(
        Line(np.array([x0, y0, 0.0]),
             np.array([x0 + ancho_grafica, y0, 0.0]), stroke_width=2.0,
             color=C_EJE),
        Line(np.array([x0 + ancho_grafica / 2.0, y0, 0.0]),
             np.array([x0 + ancho_grafica / 2.0, y0 + alto * 1.10, 0.0]),
             stroke_width=1.6, color=C_EJE))

    s = np.linspace(-s_max, s_max, muestras)
    theta = np.arcsin(np.clip(s, -1.0, 1.0))
    inten = rendija_intensidad(theta, a_rel * lam, lam)
    x = x0 + (s / s_max + 1.0) / 2.0 * ancho_grafica
    curva = _poligonal(np.column_stack([x, y0 + inten * alto]), C_FRANJA, 3.0)

    ceros = VGroup()
    for signo in (-1, 1):
        sc = signo / a_rel
        if abs(sc) <= s_max:
            xc = x0 + (sc / s_max + 1.0) / 2.0 * ancho_grafica
            ceros.add(DashedLine(np.array([xc, y0, 0.0]),
                                 np.array([xc, y0 + alto * 0.95, 0.0]),
                                 stroke_width=1.6, color=C_MEDIDA,
                                 dash_length=0.09))

    rotulos = VGroup()
    t = _texto_hud(f"a = {a_rel:.0f} lambda", font_size=16, color=CODE_MUTED)
    t.move_to(np.array([x_rendija, -alto_mordaza / 2.0 - 0.26, 0.0]))
    rotulos.add(t)
    t2 = _texto_hud("sin theta = lambda / a", font_size=16, color=C_MEDIDA)
    t2.move_to(np.array([x0 + ancho_grafica / 2.0, y0 + alto * 1.24, 0.0]))
    rotulos.add(t2)
    t3 = _texto_hud("sin theta", font_size=14, color=CODE_MUTED)
    t3.move_to(np.array([x0 + ancho_grafica - 0.05, y0 - 0.28, 0.0]),
               aligned_edge=RIGHT)
    rotulos.add(t3)

    params = {"a_rel": a_rel, "lam": float(lam), "ancho": ancho,
              "alto": alto, "muestras": muestras, "s_max": s_max,
              "x0": x0, "y0": y0, "ancho_grafica": ancho_grafica}
    return RendijaPatron(_ancla(np.array([x0, y0, 0.0])),
                         _ancla(np.array([x0 + ancho_grafica, y0, 0.0])),
                         entrada, mordazas, ejes, curva, ceros, rotulos,
                         params)


def _campo_airy(d_rel, res, s_max):
    """Intensidad de Airy en una malla de senos de angulo (res x res)."""
    S, T = _malla(res, s_max)
    r = np.hypot(S, T)
    return airy_intensidad(PI * float(d_rel) * r)


def _estirado_log(v, ganancia=320.0):
    """Estirado logaritmico: saca los anillos, que en lineal no se ven."""
    v = np.clip(np.asarray(v, dtype=np.float64), 0.0, 1.0)
    return np.log1p(float(ganancia) * v) / math.log1p(float(ganancia))


class DiscoAiry(_PiezaImg):
    """El disco de Airy: imagen 2-D (con estirado logaritmico) y perfil.

    Es un `Group` porque lleva `ImageMobject`: se anima con
    `FadeIn`/`FadeTransform`, NUNCA con `Transform`, y la imagen no se
    puede recolorear. `.vectorial` es el VGroup con el perfil y los
    rotulos, por si el clip quiere animar solo esa parte.

    Atributos: `.imagen`, `.curva`, `.marca_cero`, `.vectorial`,
    `.angulo_primer_cero` (rad), `.d_rel` (D/lam)."""

    def __init__(self, ancla_a, ancla_b, imagen, marco, vectorial, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, imagen, marco, vectorial,
                         **kwargs)
        self._ancla_a = ancla_a          # extremo izquierdo del eje del perfil
        self._ancla_b = ancla_b          # extremo derecho
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, params["y0"], 0.0)
        self.imagen = imagen
        self.marco = marco
        self.vectorial = vectorial
        self.curva = params["curva"]
        self.marca_cero = params["marca_cero"]
        self._params = params
        self.d_rel = params["d_rel"]
        self.angulo_primer_cero = math.asin(min(1.2197 / params["d_rel"],
                                                1.0))

    @property
    def primer_cero(self):
        """Punto de escena del primer cero, sobre el eje del perfil."""
        p = self._params
        s = 1.2197 / p["d_rel"]
        x = s / p["s_max"] * (p["ancho"] / 2.0)
        return self._punto((x, p["y0"]))

    def con_diametro(self, d_rel):
        """Pieza GEMELA con otra apertura, ya escalada y colocada encima:
        el doble de apertura, la mitad de disco. Animala con
        `FadeTransform` (lleva imagen)."""
        p = self._params
        otra = disco_airy(d_rel, lam=p["lam"], ancho=p["ancho"],
                          alto_perfil=p["alto_perfil"], res=p["res"],
                          lado_imagen=p["lado_imagen"])
        return self._alinear(otra)


def disco_airy(d_rel=12.0, lam=LAMBDA_HENE, ancho=5.6, alto_perfil=1.25,
               res=220, lado_imagen=2.4):
    """El disco de Airy de una apertura circular de diametro D = `d_rel`
    lam, con su perfil debajo y el primer cero marcado.

    Arriba, la imagen 2-D con ESTIRADO LOGARITMICO (si no, los anillos no
    se ven: el primero lleva el 1.7 % de la luz del centro). Abajo, el
    perfil I(sin theta) en lineal, donde el primer cero se ve tocar el
    suelo en sin(theta) = 1.22 lam/D. El eje de angulos es fijo, asi que
    cambiar D con `.con_diametro()` encoge o agranda el disco.
    """
    res = _validar("disco_airy.res", res, PIXELES_MAX)
    d_rel = float(d_rel)
    if d_rel < 2.0:
        raise ValueError(f"disco_airy: d_rel={d_rel} < 2 lam")
    ancho, alto_perfil = float(ancho), float(alto_perfil)
    s_max = 0.36
    y0 = -1.85
    y_img = 1.25

    campo = _estirado_log(_campo_airy(d_rel, res, s_max))
    imagen = _imagen_escalar(campo, C_FRANJA, ancho=lado_imagen)
    imagen.move_to(np.array([0.0, y_img, 0.0]))
    marco = Square(side_length=float(lado_imagen), stroke_width=1.4,
                   color=C_EJE)
    marco.set_fill(opacity=0.0)
    marco.move_to(imagen.get_center())

    s = np.linspace(-s_max, s_max, 481)
    inten = airy_intensidad(PI * d_rel * np.abs(s))
    x = s / s_max * (ancho / 2.0)
    curva = _poligonal(np.column_stack([x, y0 + inten * alto_perfil]),
                       C_FRANJA, 3.0)
    eje = Line(np.array([-ancho / 2.0, y0, 0.0]),
               np.array([ancho / 2.0, y0, 0.0]), stroke_width=2.0,
               color=C_EJE)

    s_cero = 1.2197 / d_rel
    marca_cero = VGroup()
    for signo in (-1, 1):
        xc = signo * s_cero / s_max * (ancho / 2.0)
        if abs(xc) <= ancho / 2.0:
            marca_cero.add(DashedLine(
                np.array([xc, y0, 0.0]),
                np.array([xc, y0 + alto_perfil * 1.02, 0.0]),
                stroke_width=1.6, color=C_MEDIDA, dash_length=0.09))

    rot = _texto_hud("primer cero:  1.22 lambda / D", font_size=17,
                     color=C_MEDIDA)
    rot.move_to(np.array([0.0, y0 - 0.36, 0.0]))
    rot2 = _texto_hud(f"D = {d_rel:.0f} lambda", font_size=16,
                      color=CODE_MUTED)
    rot2.move_to(np.array([0.0, y_img + float(lado_imagen) / 2.0 + 0.24,
                           0.0]))
    rot3 = _texto_hud("estirado logaritmico", font_size=13,
                      color=CODE_MUTED)
    rot3.move_to(np.array([0.0, y_img - float(lado_imagen) / 2.0 - 0.24,
                           0.0]))

    vectorial = VGroup(eje, curva, marca_cero, rot, rot2, rot3)

    params = {"d_rel": d_rel, "lam": float(lam), "ancho": ancho,
              "alto_perfil": alto_perfil, "res": res, "s_max": s_max,
              "y0": y0, "lado_imagen": float(lado_imagen), "curva": curva,
              "marca_cero": marca_cero}
    return DiscoAiry(_ancla(np.array([-ancho / 2.0, y0, 0.0])),
                     _ancla(np.array([ancho / 2.0, y0, 0.0])),
                     imagen, marco, vectorial, params)


class DosFuentesRayleigh(_PiezaImg):
    """Dos fuentes puntuales que se acercan hasta confundirse.

    `Group` (lleva imagen): `FadeIn`/`FadeTransform`, no `Transform`.
    Atributos: `.imagen`, `.curva`, `.picos`, `.vectorial`, `.sep_rel`
    (separacion en unidades de lam/D; Rayleigh es 1.22)."""

    def __init__(self, ancla_a, ancla_b, imagen, marco, vectorial, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, imagen, marco, vectorial,
                         **kwargs)
        self._ancla_a = ancla_a
        self._ancla_b = ancla_b
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, params["y0"], 0.0)
        self.imagen = imagen
        self.marco = marco
        self.vectorial = vectorial
        self.curva = params["curva"]
        self.picos = params["picos"]
        self.lectura = params["lectura"]
        self._params = params
        self.sep_rel = params["sep_rel"]

    def resuelto(self):
        """True si la separacion llega al criterio de Rayleigh (1.22 lam/D).
        Es un CRITERIO, no una ley: por debajo aun hay informacion, pero ya
        no se ve el valle."""
        return bool(self.sep_rel >= 1.22)

    def hundimiento(self):
        """Hundimiento MEDIDO del valle central: (Imax - Icentro)/Imax.

        En el criterio de Rayleigh exacto vale ~0.265 (el famoso 26.5 % de
        caida); a la mitad de separacion casi no hay valle."""
        p = self._params
        i = p["perfil"]
        centro = float(i[len(i) // 2])
        return (float(i.max()) - centro) / max(float(i.max()), _EPS)

    def con_separacion(self, sep_rel):
        """Pieza GEMELA con otra separacion, ya escalada y encima (usar
        `FadeTransform`)."""
        p = self._params
        otra = dos_fuentes_rayleigh(sep_rel, d_rel=p["d_rel"],
                                    ancho=p["ancho"], alto=p["alto"],
                                    res=p["res"],
                                    lado_imagen=p["lado_imagen"])
        return self._alinear(otra)


def dos_fuentes_rayleigh(sep_rel=1.22, d_rel=12.0, ancho=5.4, alto=1.30,
                         res=180, lado_imagen=2.4):
    """Dos fuentes puntuales separadas `sep_rel` x (lam/D): el criterio de
    Rayleigh dice que se distinguen si sep_rel >= 1.22.

    Arriba la imagen 2-D (suma de dos discos de Airy, estirado
    logaritmico), abajo el perfil sumado donde se ve —o no— el valle. La
    cifra fisica que rotula el clip sale de `angulo_rayleigh`: Hubble
    0.28 urad, el ojo 224 urad.
    """
    res = _validar("dos_fuentes_rayleigh.res", res, PIXELES_MAX)
    sep_rel, d_rel = float(sep_rel), float(d_rel)
    ancho, alto = float(ancho), float(alto)
    s_max = 0.36
    y0 = -1.90
    y_img = 1.25
    sep = sep_rel / d_rel                       # en sin(theta)

    S, T = _malla(res, s_max)
    r1 = np.hypot(S - sep / 2.0, T)
    r2 = np.hypot(S + sep / 2.0, T)
    campo = (airy_intensidad(PI * d_rel * r1)
             + airy_intensidad(PI * d_rel * r2))
    campo = campo / max(float(campo.max()), _EPS)
    imagen = _imagen_escalar(_estirado_log(campo, 220.0), C_FRANJA,
                             ancho=lado_imagen)
    imagen.move_to(np.array([0.0, y_img, 0.0]))
    marco = Rectangle(width=float(lado_imagen), height=float(lado_imagen),
                      stroke_width=1.4, color=C_EJE)
    marco.set_fill(opacity=0.0)
    marco.move_to(imagen.get_center())

    s = np.linspace(-s_max, s_max, 481)
    perfil = (airy_intensidad(PI * d_rel * np.abs(s - sep / 2.0))
              + airy_intensidad(PI * d_rel * np.abs(s + sep / 2.0)))
    perfil = perfil / max(float(perfil.max()), _EPS)
    x = s / s_max * (ancho / 2.0)
    curva = _poligonal(np.column_stack([x, y0 + perfil * alto]),
                       C_FRANJA, 3.0)
    eje = Line(np.array([-ancho / 2.0, y0, 0.0]),
               np.array([ancho / 2.0, y0, 0.0]), stroke_width=2.0,
               color=C_EJE)

    picos = VGroup()
    for signo in (-1, 1):
        xc = signo * (sep / 2.0) / s_max * (ancho / 2.0)
        picos.add(DashedLine(np.array([xc, y0, 0.0]),
                             np.array([xc, y0 + alto * 1.06, 0.0]),
                             stroke_width=1.4, color=C_OBJETO,
                             dash_length=0.08))

    estado = "resuelto" if sep_rel >= 1.22 else "sin resolver"
    lectura = _texto_hud(f"separacion = {sep_rel:.2f} lambda/D    {estado}",
                         font_size=17, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, y0 - 0.36, 0.0]))

    vectorial = VGroup(eje, curva, picos, lectura)
    params = {"sep_rel": sep_rel, "d_rel": d_rel, "ancho": ancho,
              "alto": alto, "res": res, "y0": y0, "perfil": perfil,
              "lado_imagen": float(lado_imagen), "curva": curva,
              "picos": picos, "lectura": lectura}
    return DosFuentesRayleigh(_ancla(np.array([-ancho / 2.0, y0, 0.0])),
                              _ancla(np.array([ancho / 2.0, y0, 0.0])),
                              imagen, marco, vectorial, params)


class HazGaussiano(_Pieza):
    """La cintura del haz y las dos hiperbolas w(z).

    Atributos: `.superior`, `.inferior`, `.asintota`, `.cintura`,
    `.marcador` (el plano movil), `.lectura`, `.theta` (rad),
    `.w0`, `.z_max`."""

    def __init__(self, ancla_a, ancla_b, eje, asintota, superior, inferior,
                 relleno, cintura, marcador, rotulos, lectura, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, eje, asintota, relleno, superior,
                         inferior, cintura, marcador, rotulos, lectura,
                         **kwargs)
        self._ancla_a = ancla_a          # la cintura (z = 0)
        self._ancla_b = ancla_b          # el extremo derecho (z = z_max)
        self._largo_ref = params["ancho"]
        self._p0 = (0.0, 0.0, 0.0)
        self.eje = eje
        self.asintota = asintota
        self.superior = superior
        self.inferior = inferior
        self.relleno = relleno
        self.cintura = cintura
        self.marcador = marcador
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.theta = params["theta"]
        self.w0 = params["w0"]
        self.z_max = params["z_max"]

    def radio_en(self, z):
        """Radio FISICO del haz a distancia z (metros), con `radio_haz`.
        A 5000 km con w0 = 5 cm y 1550 nm: 49.3 m."""
        return float(radio_haz(float(z), self._params["lam"],
                               self._params["w0"]))

    def huella_en(self, z):
        """Diametro de la huella a distancia z (metros) = 2 w(z). A
        5000 km son 98.7 m, lo mismo que da `huella(theta, R)` en campo
        lejano."""
        return 2.0 * self.radio_en(z)

    def punto_borde(self, z, signo=1):
        """Punto de escena del borde del haz a distancia z."""
        p = self._params
        z = float(np.clip(float(z), 0.0, p["z_max"]))
        x = z / p["z_max"] * p["ancho"]
        y = float(signo) * self.radio_en(z) * p["escala_w"]
        return self._punto((x, y))

    def a_distancia(self, z):
        """MUTA la pieza: lleva el plano marcador a esa distancia z
        (metros) y actualiza la lectura. Devuelve self."""
        p = self._params
        z = float(np.clip(float(z), 0.0, p["z_max"]))
        x = z / p["z_max"] * p["ancho"]
        w = self.radio_en(z)
        h = max(w * p["escala_w"], 0.05)
        _fijar(self.marcador, self._a_escena([(x, -h), (x, h)]))
        self.lectura = self._relectura(
            self.lectura,
            f"z = {z / 1000.0:7.0f} km    huella 2w = {2.0 * w:6.1f} m",
            font_size=17, color=C_MEDIDA)
        return self


def haz_gaussiano(w0=0.05, lam=LAMBDA_ISL, z_max=5.0e6, ancho=5.8,
                  alto=2.4, muestras=161):
    """El haz que se abre: la cintura w0 y las dos ramas de w(z).

    Ni el laser es una recta. Con w0 = 5 cm a 1550 nm el semiangulo es
    `divergencia_gauss` = 9.87 urad y a 5000 km la huella mide 98.7 m.

    ESCALAS: el eje horizontal es lineal en z (0..z_max) y el vertical es
    lineal en w, pero con factores COMPLETAMENTE distintos (5000 km contra
    50 m): la apertura del haz esta exagerada unos 10^5. El dibujo dice la
    forma —una hiperbola que arranca en una cintura y acaba en una recta—,
    no la proporcion.
    """
    muestras = _validar("haz_gaussiano.muestras", muestras, PUNTOS_MAX)
    w0, lam, z_max = float(w0), float(lam), float(z_max)
    ancho, alto = float(ancho), float(alto)
    theta = divergencia_gauss(lam, w0)
    w_max = float(radio_haz(z_max, lam, w0))
    escala_w = (alto / 2.0) * 0.90 / max(w_max, _EPS)

    z = np.linspace(0.0, z_max, muestras)
    w = radio_haz(z, lam, w0)
    x = z / z_max * ancho
    y = w * escala_w

    eje = Line(ORIGIN, np.array([ancho, 0.0, 0.0]), stroke_width=1.4,
               color=C_EJE)
    superior = _poligonal(np.column_stack([x, y]), C_HAZ, 3.0)
    inferior = _poligonal(np.column_stack([x, -y]), C_HAZ, 3.0)
    relleno = Polygon(*[np.array([xi, yi, 0.0]) for xi, yi in zip(x, y)],
                      *[np.array([xi, -yi, 0.0])
                        for xi, yi in zip(x[::-1], y[::-1])],
                      stroke_width=0.0, color=C_HAZ)
    relleno.set_fill(C_HAZ, opacity=0.10)

    recta = _poligonal([(0.0, 0.0), (ancho, theta * z_max * escala_w)],
                       C_MEDIDA, 1.4, 0.6)
    asintota = DashedVMobject(recta, num_dashes=28)

    cintura = Line(np.array([0.0, -w0 * escala_w - 0.18, 0.0]),
                   np.array([0.0, w0 * escala_w + 0.18, 0.0]),
                   stroke_width=3.0, color=C_ONDA)
    marcador = _poligonal([(ancho, -alto / 2.0 * 0.9),
                           (ancho, alto / 2.0 * 0.9)], C_OBJETO, 2.4)

    rotulos = VGroup()
    t0 = _texto_hud(f"w0 = {w0 * 100:.0f} cm", font_size=16, color=C_ONDA)
    t0.move_to(np.array([0.10, w0 * escala_w + 0.42, 0.0]),
               aligned_edge=LEFT)
    rotulos.add(t0)
    t1 = _texto_hud(f"theta = {theta * 1e6:.2f} urad", font_size=17,
                    color=C_MEDIDA)
    t1.move_to(np.array([ancho * 0.50, (alto / 2.0) * 0.90 * 0.34, 0.0]),
               aligned_edge=LEFT)
    rotulos.add(t1)
    t2 = _texto_hud("escala transversal exagerada", font_size=13,
                    color=CODE_MUTED)
    t2.move_to(np.array([ancho * 0.5, -alto / 2.0 - 0.30, 0.0]))
    rotulos.add(t2)

    lectura = _texto_hud(f"z = {z_max / 1000.0:7.0f} km    huella 2w = "
                         f"{2.0 * w_max:6.1f} m", font_size=17,
                         color=C_MEDIDA)
    lectura.move_to(np.array([ancho, alto / 2.0 + 0.32, 0.0]),
                    aligned_edge=RIGHT)

    params = {"w0": w0, "lam": lam, "z_max": z_max, "ancho": ancho,
              "alto": alto, "escala_w": escala_w, "theta": theta,
              "muestras": muestras}
    return HazGaussiano(_ancla(ORIGIN), _ancla(np.array([ancho, 0.0, 0.0])),
                        eje, asintota, superior, inferior, relleno, cintura,
                        marcador, rotulos, lectura, params)


# =====================================================================
# 2.1 — Medir con el tiempo de vuelo
# =====================================================================
class PulsoIdaVuelta(_Pieza):
    """Emisor, blanco y un pulso que va y vuelve con su cronometro.

    Atributos: `.emisor`, `.blanco`, `.pulso`, `.halo`, `.lectura`,
    `.tiempo_total` (s, de `tiempo_vuelo`), `.frac` (estado)."""

    def __init__(self, ancla_a, ancla_b, camino, medida, emisor, blanco,
                 halo, pulso, rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, camino, medida, emisor, blanco,
                         halo, pulso, rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a          # el emisor
        self._ancla_b = ancla_b          # el blanco
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.camino = camino
        self.medida = medida
        self.emisor = emisor
        self.blanco = blanco
        self.halo = halo
        self.pulso = pulso
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.tiempo_total = tiempo_vuelo(params["d"])
        self.frac = 0.0

    def a_t(self, frac):
        """MUTA la pieza: `frac` en [0, 1] es la fraccion del viaje COMPLETO
        (ida y vuelta). 0.5 es el instante en que el pulso toca el blanco.

        La lectura muestra el tiempo real transcurrido (frac x
        `tiempo_vuelo(d)`) y la distancia que se deduce, c t/2.
        """
        p = self._params
        self.frac = float(np.clip(float(frac), 0.0, 1.0))
        u = 2.0 * self.frac if self.frac <= 0.5 else 2.0 - 2.0 * self.frac
        x = -p["ancho"] / 2.0 + u * p["ancho"]
        destino = self._punto((x, 0.0))
        self.pulso.move_to(destino)
        self.halo.move_to(destino)
        t = self.frac * self.tiempo_total
        d = distancia_por_tiempo(t)
        self.lectura = self._relectura(
            self.lectura,
            f"t = {t * 1e9:7.2f} ns    c t / 2 = {d * 100:6.2f} cm",
            font_size=17, color=C_MEDIDA)
        return self


def pulso_ida_vuelta(d=1.5, ancho=5.6, color_emisor=C_HAZ,
                     color_blanco=C_OBJETO):
    """Un pulso y un cronometro: la medida de distancia mas directa que
    hay.

    El pulso sale del emisor (rojo), rebota en el blanco (verde) y vuelve;
    el reloj mide t y la distancia es c t/2 (`distancia_por_tiempo`). Con
    1.5 m el viaje dura 10.0 ns, y 1 mm de diferencia son 6.67 ps: por eso
    los telemetros se pelean por los picosegundos.
    """
    ancho, d = float(ancho), float(d)
    x_e, x_b = -ancho / 2.0, ancho / 2.0

    camino = _poligonal([(x_e, 0.0), (x_b, 0.0)], C_EJE, 1.6)
    medida = VGroup(
        DoubleArrow(np.array([x_e, -0.85, 0.0]), np.array([x_b, -0.85, 0.0]),
                    buff=0.0, stroke_width=2.0, color=CODE_MUTED,
                    tip_length=0.14))
    t_d = _texto_hud(f"d = {d:.2f} m", font_size=17, color=CODE_MUTED)
    t_d.move_to(np.array([0.0, -1.16, 0.0]))
    medida.add(t_d)

    cuerpo_e = RoundedRectangle(width=0.66, height=0.86, corner_radius=0.09,
                                stroke_width=2.4, color=color_emisor)
    cuerpo_e.set_fill(color_emisor, opacity=0.14)
    cuerpo_e.move_to(np.array([x_e, 0.0, 0.0]))
    emisor = VGroup(cuerpo_e)

    cuerpo_b = Rectangle(width=0.20, height=1.10, stroke_width=2.4,
                         color=color_blanco)
    cuerpo_b.set_fill(color_blanco, opacity=0.55)
    cuerpo_b.move_to(np.array([x_b, 0.0, 0.0]))
    blanco = VGroup(cuerpo_b)

    halo = Dot(np.array([x_e, 0.0, 0.0]), radius=0.17, color=C_HAZ)
    halo.set_fill(C_HAZ, opacity=0.20)
    halo.set_stroke(width=0)
    pulso = Dot(np.array([x_e, 0.0, 0.0]), radius=0.08, color=C_HAZ)

    rotulos = VGroup()
    t_e = _texto_hud("emisor", font_size=16, color=color_emisor)
    t_e.move_to(np.array([x_e, 0.66, 0.0]))
    rotulos.add(t_e)
    t_b = _texto_hud("blanco", font_size=16, color=color_blanco)
    t_b.move_to(np.array([x_b, 0.78, 0.0]))
    rotulos.add(t_b)

    lectura = _texto_hud("t =    0.00 ns    c t / 2 =   0.00 cm",
                         font_size=17, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, 1.28, 0.0]))

    params = {"ancho": ancho, "d": d}
    return PulsoIdaVuelta(_ancla(np.array([x_e, 0.0, 0.0])),
                          _ancla(np.array([x_b, 0.0, 0.0])),
                          camino, medida, emisor, blanco, halo, pulso,
                          rotulos, lectura, params)


class TierraLunaLaser(_Pieza):
    """La Tierra, la Luna y el pulso que tarda 2.564 s en ir y volver.

    Atributos: `.tierra`, `.luna`, `.retrorreflector`, `.pulso`,
    `.lectura`, `.frac`."""

    def __init__(self, ancla_a, ancla_b, camino, tierra, luna, retro,
                 estacion, halo, pulso, rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, camino, tierra, luna, retro,
                         estacion, halo, pulso, rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a          # centro de la Tierra
        self._ancla_b = ancla_b          # centro de la Luna
        self._largo_ref = params["separacion"]
        self._p0 = (-params["separacion"] / 2.0, 0.0, 0.0)
        self.camino = camino
        self.tierra = tierra
        self.luna = luna
        self.retrorreflector = retro
        self.estacion = estacion
        self.halo = halo
        self.pulso = pulso
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.tiempo_total = tiempo_vuelo(params["d_m"])
        self.frac = 0.0

    def a_t(self, frac):
        """MUTA la pieza: `frac` en [0, 1] del viaje COMPLETO (2.564 s
        reales). 0.5 es el rebote en el retrorreflector."""
        p = self._params
        self.frac = float(np.clip(float(frac), 0.0, 1.0))
        u = 2.0 * self.frac if self.frac <= 0.5 else 2.0 - 2.0 * self.frac
        x = p["x_tierra"] + u * (p["x_luna"] - p["x_tierra"])
        destino = self._punto((x, 0.0))
        self.pulso.move_to(destino)
        self.halo.move_to(destino)
        t = self.frac * self.tiempo_total
        self.lectura = self._relectura(
            self.lectura, f"t = {t:5.3f} s  de  {self.tiempo_total:5.3f} s",
            font_size=18, color=C_MEDIDA)
        return self


def tierra_luna_laser(ancho=8.6, r_tierra=0.115, r_luna=0.070):
    """Tierra y Luna a escala de DISTANCIA: 30 diametros terrestres.

    La separacion dibujada vale exactamente 30 veces el diametro dibujado
    de la Tierra, que es la proporcion real (384 400 / 12 742 = 30.2). Los
    TAMANOS no estan a escala entre si: la Luna real mide 0.27 diametros
    terrestres y aqui se dibuja mas grande para que se vea el
    retrorreflector. El pulso tarda 2.564 s en ir y volver
    (`tiempo_vuelo`), y con el se mide la distancia al milimetro.
    """
    ancho = float(ancho)
    r_tierra = float(r_tierra)
    separacion = 30.2 * (2.0 * r_tierra)
    esc = ancho / separacion
    x_t, x_l = -separacion / 2.0, separacion / 2.0

    camino = _poligonal([(x_t, 0.0), (x_l, 0.0)], C_EJE, 1.2)

    tierra = Circle(radius=r_tierra, stroke_width=2.2, color=C_MEDIDA)
    tierra.set_fill(C_MEDIDA, opacity=0.14)
    tierra.move_to(np.array([x_t, 0.0, 0.0]))

    estacion = VGroup(
        Line(np.array([x_t, r_tierra, 0.0]),
             np.array([x_t + 0.10, r_tierra + 0.20, 0.0]),
             stroke_width=3.0, color=C_HAZ))

    luna = Circle(radius=float(r_luna), stroke_width=2.2, color=C_OBJETO)
    luna.set_fill(C_OBJETO, opacity=0.16)
    luna.move_to(np.array([x_l, 0.0, 0.0]))

    lado = float(r_luna) * 0.95
    retro = Square(side_length=lado, stroke_width=1.8, color=C_OBJETO)
    retro.set_fill(C_OBJETO, opacity=0.55)
    retro.move_to(np.array([x_l - float(r_luna) - lado * 0.75, 0.0, 0.0]))

    halo = Dot(np.array([x_t, 0.0, 0.0]), radius=0.13, color=C_HAZ)
    halo.set_fill(C_HAZ, opacity=0.20)
    halo.set_stroke(width=0)
    pulso = Dot(np.array([x_t, 0.0, 0.0]), radius=0.06, color=C_HAZ)

    rotulos = VGroup()
    t_t = _texto_hud("Tierra", font_size=16, color=C_MEDIDA)
    t_t.move_to(np.array([x_t, -r_tierra - 0.30, 0.0]))
    rotulos.add(t_t)
    t_l = _texto_hud("Luna", font_size=16, color=C_OBJETO)
    t_l.move_to(np.array([x_l, -float(r_luna) - 0.30, 0.0]))
    rotulos.add(t_l)
    t_r = _texto_hud("retrorreflector", font_size=13, color=C_OBJETO)
    t_r.move_to(np.array([x_l - 0.30, float(r_luna) + 0.32, 0.0]))
    rotulos.add(t_r)
    t_d = _texto_hud("384 400 km   (30 diametros terrestres)",
                     font_size=16, color=CODE_MUTED)
    t_d.move_to(np.array([0.0, -0.62, 0.0]))
    rotulos.add(t_d)

    d_m = 384_400_000.0
    lectura = _texto_hud(f"t = 0.000 s  de  {tiempo_vuelo(d_m):5.3f} s",
                         font_size=18, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, 0.62, 0.0]))

    params = {"separacion": separacion, "x_tierra": x_t, "x_luna": x_l,
              "d_m": d_m, "r_tierra": r_tierra}
    pieza = TierraLunaLaser(_ancla(np.array([x_t, 0.0, 0.0])),
                            _ancla(np.array([x_l, 0.0, 0.0])),
                            camino, tierra, luna, retro, estacion, halo,
                            pulso, rotulos, lectura, params)
    if abs(esc - 1.0) > 1e-9:
        pieza.scale(esc)
    return pieza


class SateliteSLR(_Pieza):
    """Estacion en la superficie, satelite arriba y el pulso entre los dos.

    Atributos: `.superficie`, `.estacion`, `.satelite`, `.pulso`,
    `.lectura`, `.tiempo_total` (s), `.frac`."""

    def __init__(self, ancla_a, ancla_b, superficie, vista, estacion,
                 satelite, halo, pulso, rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, superficie, vista, estacion,
                         satelite, halo, pulso, rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a          # la estacion
        self._ancla_b = ancla_b          # el satelite
        self._largo_ref = params["largo"]
        self._p0 = params["p_estacion"]
        self.superficie = superficie
        self.vista = vista
        self.estacion = estacion
        self.satelite = satelite
        self.halo = halo
        self.pulso = pulso
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.tiempo_total = tiempo_vuelo(params["h_km"] * 1000.0)
        self.frac = 0.0

    def a_t(self, frac):
        """MUTA la pieza: `frac` en [0, 1] del viaje COMPLETO (39.4 ms para
        LAGEOS a 5900 km)."""
        p = self._params
        self.frac = float(np.clip(float(frac), 0.0, 1.0))
        u = 2.0 * self.frac if self.frac <= 0.5 else 2.0 - 2.0 * self.frac
        a = np.asarray(p["p_estacion"], dtype=np.float64)
        b = np.asarray(p["p_satelite"], dtype=np.float64)
        destino = self._punto(a + u * (b - a))
        self.pulso.move_to(destino)
        self.halo.move_to(destino)
        t = self.frac * self.tiempo_total
        self.lectura = self._relectura(
            self.lectura,
            f"t = {t * 1000.0:6.2f} ms  de  "
            f"{self.tiempo_total * 1000.0:5.1f} ms",
            font_size=18, color=C_MEDIDA)
        return self


def satelite_slr(h_km=5900.0, ancho=6.4, r_satelite=0.26):
    """Telemetria laser a satelite (SLR): la estacion dispara, el satelite
    devuelve y la orbita queda medida al milimetro.

    LAGEOS a 5900 km: 39.4 ms de ida y vuelta (`tiempo_vuelo`). El retorno
    cae como 1/R^4 (`fotones_retorno`), asi que de cada disparo vuelven
    unos pocos fotones: se acumulan miles de disparos.

    La superficie es un arco (no una recta) para que se lea "planeta"; la
    altura del satelite en el dibujo NO esta a escala con el radio
    terrestre.
    """
    ancho = float(ancho)
    r_curv = 7.2
    y_centro = -r_curv - 0.9
    x_est, y_est = -1.35, math.sqrt(max(r_curv ** 2 - 1.35 ** 2, 0.0)) + y_centro
    p_sat = (1.55, 1.95)

    ang = math.asin(min(ancho / 2.0 / r_curv, 1.0))
    superficie = Arc(radius=r_curv, start_angle=PI / 2.0 - ang,
                     angle=2.0 * ang, stroke_width=2.6, color=C_EJE)
    superficie.move_arc_center_to(np.array([0.0, y_centro, 0.0]))
    superficie.set_stroke(opacity=0.9)

    vista = DashedLine(np.array([x_est, y_est + 0.18, 0.0]),
                       np.array([p_sat[0], p_sat[1], 0.0]),
                       stroke_width=1.4, color=C_EJE, dash_length=0.10)

    estacion = VGroup(
        Polygon(np.array([x_est - 0.20, y_est, 0.0]),
                np.array([x_est + 0.20, y_est, 0.0]),
                np.array([x_est, y_est + 0.34, 0.0]),
                stroke_width=2.0, color=C_MEDIDA))
    estacion[0].set_fill(C_MEDIDA, opacity=0.18)

    cuerpo = Circle(radius=float(r_satelite), stroke_width=2.2,
                    color=C_OBJETO)
    cuerpo.set_fill(C_OBJETO, opacity=0.18)
    cuerpo.move_to(np.array([p_sat[0], p_sat[1], 0.0]))
    facetas = VGroup(*[
        Line(cuerpo.get_center()
             + float(r_satelite) * 0.45 * np.array([math.cos(a),
                                                    math.sin(a), 0.0]),
             cuerpo.get_center()
             + float(r_satelite) * 0.92 * np.array([math.cos(a),
                                                    math.sin(a), 0.0]),
             stroke_width=1.4, color=C_OBJETO)
        for a in np.linspace(0.0, TAU, 9)[:-1]])
    satelite = VGroup(cuerpo, facetas)

    halo = Dot(np.array([x_est, y_est + 0.18, 0.0]), radius=0.14,
               color=C_HAZ)
    halo.set_fill(C_HAZ, opacity=0.20)
    halo.set_stroke(width=0)
    pulso = Dot(np.array([x_est, y_est + 0.18, 0.0]), radius=0.07,
                color=C_HAZ)

    rotulos = VGroup()
    t_e = _texto_hud("estacion SLR", font_size=15, color=C_MEDIDA)
    t_e.move_to(np.array([x_est - 0.05, y_est - 0.34, 0.0]))
    rotulos.add(t_e)
    t_s = _texto_hud("LAGEOS", font_size=16, color=C_OBJETO)
    t_s.move_to(np.array([p_sat[0] + float(r_satelite) + 0.22, p_sat[1],
                          0.0]), aligned_edge=LEFT)
    rotulos.add(t_s)
    t_h = _texto_hud(f"{h_km:.0f} km", font_size=17, color=CODE_MUTED)
    t_h.move_to(np.array([p_sat[0] + 0.95, (p_sat[1] + y_est) / 2.0, 0.0]))
    rotulos.add(t_h)

    lectura = _texto_hud(f"t =   0.00 ms  de  "
                         f"{tiempo_vuelo(float(h_km) * 1000.0) * 1000.0:5.1f}"
                         f" ms", font_size=18, color=C_MEDIDA)
    lectura.move_to(np.array([-3.05, 2.62, 0.0]), aligned_edge=LEFT)

    p_est = (x_est, y_est + 0.18)
    largo = float(np.hypot(p_sat[0] - p_est[0], p_sat[1] - p_est[1]))
    params = {"h_km": float(h_km), "p_estacion": p_est, "p_satelite": p_sat,
              "largo": largo}
    return SateliteSLR(_ancla(np.array([p_est[0], p_est[1], 0.0])),
                       _ancla(np.array([p_sat[0], p_sat[1], 0.0])),
                       superficie, vista, estacion, satelite, halo, pulso,
                       rotulos, lectura, params)


class ReglaAmbiguedad(_Pieza):
    """La onda de modulacion como regla que da vueltas.

    Atributos: `.onda`, `.marcas` (una por vuelta), `.llave`, `.lectura`,
    `.ambiguedad_m`, `.f_mod` (Hz), `.n_vueltas`."""

    def __init__(self, ancla_a, ancla_b, eje, onda, marcas, llave, lectura,
                 rotulos, params, **kwargs):
        super().__init__(ancla_a, ancla_b, eje, onda, marcas, llave,
                         lectura, rotulos, **kwargs)
        self._ancla_a = ancla_a          # origen del eje de distancia
        self._ancla_b = ancla_b          # extremo derecho
        self._largo_ref = params["ancho"]
        self._p0 = (0.0, 0.0, 0.0)
        self.eje = eje
        self.onda = onda
        self.marcas = marcas
        self.llave = llave
        self.lectura = lectura
        self.rotulos = rotulos
        self._params = params
        self.f_mod = params["f_mod"]
        self.ambiguedad_m = params["ambiguedad_m"]
        self.n_vueltas = params["n_vueltas"]

    def con_frecuencia(self, f_mod):
        """Pieza GEMELA con otra frecuencia de modulacion, ya escalada y
        encima (para `Transform`): a 10 veces la frecuencia, 10 veces mas
        vueltas en el mismo rango y una regla 10 veces mas fina."""
        p = self._params
        otra = regla_ambiguedad(f_mod, rango_m=p["rango_m"],
                                ancho=p["ancho"], alto=p["alto"])
        return self._alinear(otra)


def regla_ambiguedad(f_mod=10e6, rango_m=45.0, ancho=6.0, alto=0.72,
                     muestras=481):
    """La regla que da vueltas: la fase de una modulacion mide fino pero no
    sabe cuantas vueltas lleva.

    Cada periodo de la onda dibujada vale `ambiguedad_fase(f_mod)` metros
    de distancia: 15.0 m a 10 MHz, 1.5 m a 100 MHz. El eje horizontal es
    la distancia real (0..`rango_m`) y las marcas son las "vueltas": dos
    distancias separadas una vuelta entera dan la MISMA fase. Por eso se
    combinan varias frecuencias: la baja quita la ambiguedad, la alta pone
    la resolucion.
    """
    muestras = _validar("regla_ambiguedad.muestras", muestras, PUNTOS_MAX)
    f_mod, rango_m = float(f_mod), float(rango_m)
    ancho, alto = float(ancho), float(alto)
    amb = ambiguedad_fase(f_mod)
    n_vueltas = rango_m / amb
    if n_vueltas > FRANJAS_MAX:
        raise ValueError(f"regla_ambiguedad: {n_vueltas:.1f} vueltas pasan "
                         f"de {FRANJAS_MAX} (baja f_mod o el rango)")

    d = np.linspace(0.0, rango_m, muestras)
    x = d / rango_m * ancho
    y = alto * np.cos(TAU * d / amb)
    eje = Line(ORIGIN, np.array([ancho, 0.0, 0.0]), stroke_width=1.6,
               color=C_EJE)
    onda = _poligonal(np.column_stack([x, y]), C_ONDA, 3.0)

    marcas = VGroup()
    k = 0
    while k * amb <= rango_m + 1e-9:
        xm = k * amb / rango_m * ancho
        marcas.add(DashedLine(np.array([xm, -alto - 0.14, 0.0]),
                              np.array([xm, alto + 0.14, 0.0]),
                              stroke_width=1.4, color=C_MEDIDA,
                              dash_length=0.08))
        k += 1

    guia = Line(np.array([0.0, -alto - 0.30, 0.0]),
                np.array([amb / rango_m * ancho, -alto - 0.30, 0.0]),
                stroke_width=0.1)
    brace = Brace(guia, DOWN, buff=0.04, color=C_EJE)
    t_amb = _texto_hud(f"{amb:.2f} m", font_size=17, color=C_MEDIDA)
    t_amb.next_to(brace, DOWN, buff=0.08)
    llave = VGroup(brace, t_amb)

    rotulos = VGroup()
    t_r = _texto_hud(f"distancia (0 a {rango_m:.0f} m)", font_size=14,
                     color=CODE_MUTED)
    t_r.move_to(np.array([ancho, -alto - 0.52, 0.0]), aligned_edge=RIGHT)
    rotulos.add(t_r)

    lectura = _texto_hud(f"f = {f_mod / 1e6:5.1f} MHz    ambiguedad "
                         f"{amb:.2f} m", font_size=18, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, alto + 0.44, 0.0]), aligned_edge=LEFT)

    params = {"f_mod": f_mod, "rango_m": rango_m, "ancho": ancho,
              "alto": alto, "ambiguedad_m": amb, "n_vueltas": n_vueltas,
              "muestras": muestras}
    return ReglaAmbiguedad(_ancla(ORIGIN),
                           _ancla(np.array([ancho, 0.0, 0.0])),
                           eje, onda, marcas, llave, lectura, rotulos,
                           params)


# =====================================================================
# 2.2 — Medir la forma con franjas
# =====================================================================
def campo_objeto(res=200, n_franjas=7, fase0=0.0, sag_ondas=6.0,
                 radio_rel=0.72):
    """Campo sintetico del objeto medido: una semiesfera bajo unas franjas
    rectas proyectadas.

    Devuelve (fase, intensidad, altura) en mallas (res, res) sobre
    [-1, 1]^2, con la FILA 0 en y minimo. La fase es
    fase0 + 2 pi n x_norm + 2 pi sag_ondas z(x, y), con z la semiesfera
    normalizada (1 en el polo, 0 fuera del radio): las franjas salen
    rectas donde no hay objeto y curvadas encima. `sag_ondas` es la altura
    del polo medida en franjas.
    """
    res = _validar("campo_objeto.res", res, PIXELES_MAX)
    n_franjas = _validar("campo_objeto.n_franjas", n_franjas, FRANJAS_MAX)
    X, Y = _malla(res, 1.0)
    rr = np.hypot(X, Y) / float(radio_rel)
    altura = np.where(rr <= 1.0, np.sqrt(np.clip(1.0 - rr ** 2, 0.0, 1.0)),
                      0.0)
    fase = (float(fase0) + TAU * n_franjas * (X + 1.0) / 2.0
            + TAU * float(sag_ondas) * altura)
    return fase, intensidad_dos_haces(fase), altura


class ObjetoFranjas(_PiezaImg):
    """Franjas proyectadas que se curvan sobre una semiesfera.

    `Group` (lleva imagen): `FadeIn`/`FadeTransform`, no `Transform`.
    Atributos: `.imagen`, `.contornos` (curvas de nivel verdes), `.marco`,
    `.vectorial`, `.fase0`, `.sag_ondas`."""

    def __init__(self, ancla_a, ancla_b, imagen, vectorial, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, imagen, vectorial, **kwargs)
        self._ancla_a = ancla_a          # esquina izquierda del marco
        self._ancla_b = ancla_b          # esquina derecha
        self._largo_ref = params["lado"]
        self._p0 = (-params["lado"] / 2.0, 0.0, 0.0)
        self.imagen = imagen
        self.vectorial = vectorial
        self.marco = params["marco"]
        self.contornos = params["contornos"]
        self._params = params
        self.fase0 = params["fase0"]
        self.sag_ondas = params["sag_ondas"]

    def campo_fase(self):
        """La fase (res, res) con la que se pinto: es lo que `cuatro_pasos`
        vuelve a sacar de las intensidades."""
        return self._params["fase"]

    def con_fase0(self, fase0):
        """Pieza GEMELA con otra fase inicial, ya escalada y encima: es lo
        que se anima para "correr" las franjas sobre el objeto (usar
        `FadeTransform`)."""
        p = self._params
        otra = objeto_franjas(fase0, n_franjas=p["n_franjas"],
                              sag_ondas=p["sag_ondas"], lado=p["lado"],
                              res=p["res"], radio_rel=p["radio_rel"])
        return self._alinear(otra)


def objeto_franjas(fase0=0.0, n_franjas=7, sag_ondas=6.0, lado=4.2, res=200,
                   radio_rel=0.72, niveles=5):
    """Franjas rectas proyectadas sobre una semiesfera: la forma esta en la
    fase.

    Donde no hay objeto las franjas salen rectas; sobre la semiesfera se
    curvan tanto como alto sea el objeto (`sag_ondas` franjas en el polo).
    Las curvas de nivel verdes recuerdan que el objeto es un casquete. La
    altura se recupera de la fase con `altura_de_fase`.
    """
    lado = float(lado)
    fase, inten, altura = campo_objeto(res, n_franjas, fase0, sag_ondas,
                                       radio_rel)
    imagen = _imagen_escalar(inten, C_FRANJA, ancho=lado)
    imagen.move_to(ORIGIN)

    marco = Square(side_length=lado, stroke_width=1.6, color=C_EJE)
    marco.set_fill(opacity=0.0)

    niveles = _validar("objeto_franjas.niveles", niveles, 12)
    contornos = VGroup()
    for k in range(1, niveles + 1):
        z = k / (niveles + 1.0)
        r = float(radio_rel) * math.sqrt(max(1.0 - z * z, 0.0)) * lado / 2.0
        c = Circle(radius=r, stroke_width=2.0, color=C_OBJETO)
        c.set_fill(opacity=0.0)
        c.set_stroke(opacity=0.85)
        contornos.add(c)

    rot = _texto_hud(f"semiesfera:  {sag_ondas:.0f} franjas de altura",
                     font_size=16, color=C_OBJETO)
    rot.move_to(np.array([0.0, -lado / 2.0 - 0.30, 0.0]))

    vectorial = VGroup(contornos, marco, rot)
    params = {"lado": lado, "res": res, "n_franjas": n_franjas,
              "sag_ondas": float(sag_ondas), "fase0": float(fase0),
              "radio_rel": float(radio_rel), "fase": fase, "marco": marco,
              "contornos": contornos}
    return ObjetoFranjas(_ancla(np.array([-lado / 2.0, 0.0, 0.0])),
                         _ancla(np.array([lado / 2.0, 0.0, 0.0])),
                         imagen, vectorial, params)


class CuatroPasos(_PiezaImg):
    """Las cuatro imagenes desfasadas 90 grados y la fase que sale de
    ellas.

    `Group` (lleva imagenes). Atributos: `.miniaturas` (lista de
    ImageMobject), `.mapa` (la quinta, la fase), `.vectorial`."""

    def __init__(self, ancla_a, ancla_b, imagenes, vectorial, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, *imagenes, vectorial, **kwargs)
        self._ancla_a = ancla_a          # centro de la primera miniatura
        self._ancla_b = ancla_b          # centro de la quinta
        self._largo_ref = params["largo_ref"]
        self._p0 = (params["x0"], 0.0, 0.0)
        self.miniaturas = list(imagenes[:4])
        self.mapa = imagenes[4]
        self.vectorial = vectorial
        self._params = params

    def intensidades(self):
        """Las cuatro imagenes como arrays (res, res), en el orden
        I1, I2, I3, I4 (0, 90, 180, 270 grados)."""
        return self._params["I"]

    def fase(self):
        """La fase ENVUELTA calculada con `fase_4_pasos` a partir de las
        cuatro intensidades: array (res, res) en (-pi, pi].

        Es la demostracion del clip: la fase sale de las imagenes, no de la
        formula con la que se pintaron (aunque coincidan, que es el
        punto)."""
        i1, i2, i3, i4 = self._params["I"]
        return fase_4_pasos(i1, i2, i3, i4)

    def miniatura(self, i):
        """La i-esima imagen (0..3), o la 4 para el mapa de fase."""
        i = int(i)
        return self.mapa if i == 4 else self.miniaturas[i]


def cuatro_pasos(n_franjas=5, sag_ondas=4.0, res=140, lado=1.45, sep=0.26,
                 radio_rel=0.72):
    """Cuatro imagenes desfasadas 90 grados y la fase que sale de ellas.

    fase = atan2(I4 - I2, I1 - I3) pixel a pixel (`fase_4_pasos`): no hace
    falta saber ni la iluminacion ni el contraste, solo cuatro fotos con
    el desfase controlado. La quinta miniatura es la fase ENVUELTA, en
    cian (negativa) y ambar (positiva).
    """
    lado, sep = float(lado), float(sep)
    fase, _, _ = campo_objeto(res, n_franjas, 0.0, sag_ondas, radio_rel)
    intens = [intensidad_dos_haces(fase + k * PI / 2.0) for k in range(4)]
    envuelta = fase_4_pasos(*intens)

    paso = lado + sep
    x0 = -2.0 * paso
    imagenes = []
    for k, I in enumerate(intens):
        img = _imagen_escalar(I, C_FRANJA, ancho=lado)
        img.move_to(np.array([x0 + k * paso, 0.0, 0.0]))
        imagenes.append(img)
    mapa = _imagen_divergente(envuelta / PI, C_MEDIDA, C_ONDA, ancho=lado)
    mapa.move_to(np.array([x0 + 4 * paso, 0.0, 0.0]))
    imagenes.append(mapa)

    vectorial = VGroup()
    for k, texto in enumerate(("0", "90", "180", "270")):  # grados
        m = Square(side_length=lado, stroke_width=1.2, color=C_EJE)
        m.set_fill(opacity=0.0)
        m.move_to(np.array([x0 + k * paso, 0.0, 0.0]))
        t = _texto_hud(texto, font_size=15, color=CODE_MUTED)
        t.move_to(np.array([x0 + k * paso, -lado / 2.0 - 0.26, 0.0]))
        vectorial.add(m, t)
    m5 = Square(side_length=lado, stroke_width=1.6, color=C_MEDIDA)
    m5.set_fill(opacity=0.0)
    m5.move_to(np.array([x0 + 4 * paso, 0.0, 0.0]))
    t5 = _texto_hud("fase", font_size=15, color=C_MEDIDA)
    t5.move_to(np.array([x0 + 4 * paso, -lado / 2.0 - 0.26, 0.0]))
    vectorial.add(m5, t5)
    t6 = _texto_hud("cuatro tomas desfasadas 90 grados:   "
                    "fase = atan2(I4 - I2, I1 - I3)", font_size=17,
                    color=C_MEDIDA)
    t6.move_to(np.array([0.0, lado / 2.0 + 0.34, 0.0]))
    vectorial.add(t6)

    params = {"res": res, "lado": lado, "sep": sep, "x0": x0,
              "largo_ref": 4.0 * paso, "I": intens, "fase": fase,
              "n_franjas": n_franjas, "sag_ondas": float(sag_ondas)}
    return CuatroPasos(_ancla(np.array([x0, 0.0, 0.0])),
                       _ancla(np.array([x0 + 4 * paso, 0.0, 0.0])),
                       imagenes, vectorial, params)


class MapaFase(_Pieza):
    """Dos paneles: la fase envuelta (dientes de sierra) y la desenvuelta.

    Atributos: `.envuelta` y `.desenvuelta` (los dos paneles, VGroup),
    `.datos_envuelta` y `.datos_desenvuelta` (los arrays 1-D),
    `.sag_ondas`."""

    def __init__(self, ancla_a, ancla_b, envuelta, desenvuelta, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, envuelta, desenvuelta, **kwargs)
        self._ancla_a = ancla_a          # origen del panel izquierdo
        self._ancla_b = ancla_b          # origen del panel derecho
        self._largo_ref = params["sep_paneles"]
        self._p0 = (params["x_izq"], 0.0, 0.0)
        self.envuelta = envuelta
        self.desenvuelta = desenvuelta
        self._params = params
        self.datos_envuelta = params["envuelta"]
        self.datos_desenvuelta = params["desenvuelta"]
        self.sag_ondas = params["sag_ondas"]

    def saltos(self):
        """Cuantos saltos de 2 pi tiene la fase envuelta: son los dientes
        que hay que quitar (CONTADOS sobre los datos)."""
        d = np.diff(self.datos_envuelta)
        return int(np.count_nonzero(np.abs(d) > PI))


def mapa_fase(sag_ondas=3.0, ancho_panel=2.7, alto=1.7, sep=0.85,
              muestras=401):
    """La fase envuelta y la desenvuelta, sobre una superficie sintetica.

    La superficie es una parabola de flecha `sag_ondas` longitudes de onda,
    asi que la fase verdadera va de 0 a 2 pi x sag_ondas. El detector solo
    puede dar la fase MODULO 2 pi: eso son los dientes de sierra del panel
    izquierdo. `desenvolver` (np.unwrap) devuelve la rampa continua del
    panel derecho, que ya es la forma de la pieza.
    """
    muestras = _validar("mapa_fase.muestras", muestras, PUNTOS_MAX)
    ancho_panel, alto, sep = float(ancho_panel), float(alto), float(sep)
    sag_ondas = float(sag_ondas)

    x = np.linspace(-1.0, 1.0, muestras)
    verdadera = TAU * sag_ondas * (x ** 2)
    envuelta = np.angle(np.exp(1j * verdadera))
    desenvuelta = desenvolver(envuelta)

    x_izq = -(ancho_panel + sep / 2.0)
    x_der = sep / 2.0

    def panel(x0, datos, titulo, color, y_min, y_max):
        g = VGroup()
        y_cero = -alto / 2.0 - (y_min / max(y_max - y_min, _EPS)) * 0.0
        g.add(Line(np.array([x0, -alto / 2.0, 0.0]),
                   np.array([x0 + ancho_panel, -alto / 2.0, 0.0]),
                   stroke_width=1.8, color=C_EJE))
        g.add(Line(np.array([x0, -alto / 2.0, 0.0]),
                   np.array([x0, alto / 2.0, 0.0]),
                   stroke_width=1.8, color=C_EJE))
        u = (x + 1.0) / 2.0 * ancho_panel + x0
        v = (-alto / 2.0
             + (datos - y_min) / max(y_max - y_min, _EPS) * alto)
        g.add(_poligonal(np.column_stack([u, v]), color, 3.0))
        t = _texto_hud(titulo, font_size=17, color=color)
        t.move_to(np.array([x0 + ancho_panel / 2.0, alto / 2.0 + 0.30, 0.0]))
        g.add(t)
        del y_cero
        return g

    p_env = panel(x_izq, envuelta, "fase envuelta", C_FRANJA, -PI, PI)
    p_des = panel(x_der, desenvuelta, "fase desenvuelta", C_MEDIDA,
                  float(desenvuelta.min()), float(desenvuelta.max()))

    t_env = _texto_hud("+pi / -pi", font_size=13, color=CODE_MUTED)
    t_env.move_to(np.array([x_izq - 0.14, 0.0, 0.0]), aligned_edge=RIGHT)
    p_env.add(t_env)
    t_des = _texto_hud(f"0 a {sag_ondas:.0f} x 2 pi", font_size=13,
                       color=CODE_MUTED)
    t_des.move_to(np.array([x_der + ancho_panel + 0.14, 0.0, 0.0]),
                  aligned_edge=LEFT)
    p_des.add(t_des)

    params = {"sag_ondas": sag_ondas, "ancho_panel": ancho_panel,
              "alto": alto, "sep": sep, "x_izq": x_izq, "x_der": x_der,
              "sep_paneles": x_der - x_izq, "envuelta": envuelta,
              "desenvuelta": desenvuelta, "verdadera": verdadera}
    return MapaFase(_ancla(np.array([x_izq, 0.0, 0.0])),
                    _ancla(np.array([x_der, 0.0, 0.0])),
                    p_env, p_des, params)


class PerfilSuperficie(_Pieza):
    """El perfil medido contra el ideal, con su banda de error.

    Atributos: `.ideal`, `.medido`, `.banda`, `.lectura`, `.lam`."""

    def __init__(self, ancla_a, ancla_b, ejes, banda, ideal, medido,
                 rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, ejes, banda, ideal, medido,
                         rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a
        self._ancla_b = ancla_b
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.ejes = ejes
        self.banda = banda
        self.ideal = ideal
        self.medido = medido
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.lam = params["lam"]

    def error_lambda(self):
        """Error MEDIDO sobre los datos, en fraccion de lambda: es el
        pico-valle de (medido - ideal). Con el valor por omision sale
        0.0500 ondas, o sea lambda/20."""
        e = self._params["error_perfil"]
        return float(e.max() - e.min())

    def error_nm(self):
        """El mismo error en nanometros: lambda/20 con el HeNe son
        31.6 nm."""
        return self.error_lambda() * self.lam * 1e9

    def error_rms(self):
        """RMS del error medido, en ondas (menor que el pico-valle)."""
        e = self._params["error_perfil"]
        return float(np.sqrt(np.mean((e - e.mean()) ** 2)))


def perfil_superficie(error_ondas=0.05, lam=LAMBDA_HENE, ancho=5.6,
                      alto=1.9, span_ondas=0.22, muestras=321):
    """El perfil de un espejo: lo medido contra lo ideal.

    `error_ondas` es el pico-valle del error (0.05 = lambda/20, que con el
    HeNe son 31.6 nm). La escala vertical esta EXAGERADA y documentada:
    todo el alto del panel son `span_ondas` longitudes de onda, o sea
    140 nm — un espejo de telescopio de un metro dibujado asi seria una
    montana.

    El perfil medido es determinista (dos cosenos incomensurables), no
    aleatorio: mismo render siempre.
    """
    muestras = _validar("perfil_superficie.muestras", muestras, PUNTOS_MAX)
    ancho, alto = float(ancho), float(alto)
    error_ondas, span_ondas = float(error_ondas), float(span_ondas)
    lam = float(lam)

    x = np.linspace(-1.0, 1.0, muestras)
    forma = (0.62 * np.cos(2.3 * PI * x + 0.7)
             + 0.38 * np.cos(5.1 * PI * x - 1.3))
    forma = forma - forma.mean()
    pv = float(forma.max() - forma.min())
    err = forma / max(pv, _EPS) * error_ondas          # ondas, PV exacto

    esc = alto / max(span_ondas, _EPS)                  # unidades por onda
    xs = x * (ancho / 2.0)

    ejes = VGroup(
        Line(np.array([-ancho / 2.0, -alto / 2.0, 0.0]),
             np.array([ancho / 2.0, -alto / 2.0, 0.0]), stroke_width=1.6,
             color=C_EJE))

    banda = Rectangle(width=ancho, height=error_ondas * esc,
                      stroke_width=0.0, color=C_FRANJA)
    banda.set_fill(C_FRANJA, opacity=0.14)
    banda.move_to(ORIGIN)

    linea_ideal = _poligonal(np.column_stack([xs, np.zeros_like(xs)]),
                             C_OBJETO, 2.4)
    ideal = DashedVMobject(linea_ideal, num_dashes=42)
    medido = _poligonal(np.column_stack([xs, err * esc]), C_MEDIDA, 3.0)

    rotulos = VGroup()
    t_i = _texto_hud("ideal", font_size=15, color=C_OBJETO)
    t_i.move_to(np.array([-ancho / 2.0 - 0.62, 0.0, 0.0]))
    rotulos.add(t_i)
    t_m = _texto_hud("medido", font_size=15, color=C_MEDIDA)
    t_m.move_to(np.array([ancho / 2.0 + 0.68, err[-1] * esc, 0.0]))
    rotulos.add(t_m)
    t_e = _texto_hud(f"escala vertical: todo el alto = {span_ondas:.2f} "
                     f"lambda", font_size=13, color=CODE_MUTED)
    t_e.move_to(np.array([0.0, -alto / 2.0 - 0.30, 0.0]))
    rotulos.add(t_e)

    denom = 1.0 / max(error_ondas, _EPS)
    lectura = _texto_hud(f"PV = lambda/{denom:.0f} = "
                         f"{error_ondas * lam * 1e9:.1f} nm", font_size=19,
                         color=C_MEDIDA)
    lectura.move_to(np.array([0.0, alto / 2.0 + 0.34, 0.0]))

    params = {"ancho": ancho, "alto": alto, "lam": lam,
              "error_ondas": error_ondas, "span_ondas": span_ondas,
              "error_perfil": err, "muestras": muestras}
    return PerfilSuperficie(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                            _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                            ejes, banda, ideal, medido, rotulos, lectura,
                            params)


# =====================================================================
# 2.3 — Medir el frente de onda
# =====================================================================
class FrenteOnda(_Pieza):
    """El frente de onda como una rejilla deformada dentro de la pupila.

    Plano = lineas rectas; aberrado = lineas onduladas. Atributos:
    `.lineas`, `.pupila`, `.lectura`, `.coefs` (dict), `.radio`.
    """

    def __init__(self, ancla_a, ancla_b, pupila, lineas, lectura, params,
                 **kwargs):
        super().__init__(ancla_a, ancla_b, pupila, lineas, lectura,
                         **kwargs)
        self._ancla_a = ancla_a          # borde izquierdo de la pupila
        self._ancla_b = ancla_b          # borde derecho
        self._largo_ref = 2.0 * params["radio"]
        self._p0 = (-params["radio"], 0.0, 0.0)
        self.pupila = pupila
        self.lineas = lineas
        self.lectura = lectura
        self._params = params
        self.coefs = dict(params["coefs"])
        self.radio = params["radio"]

    def rms_ondas(self):
        """RMS del frente en ONDAS, MEDIDO sobre la pupila muestreada.

        Como los Zernike de `zernike()` van normalizados, coincide con
        sqrt(suma c_i^2) salvo el error de muestreo (< 1 % con res 96)."""
        p = self._params
        W, dentro = p["W"], p["dentro"]
        v = W[dentro]
        return float(np.sqrt(np.mean((v - v.mean()) ** 2)))

    def pv_ondas(self):
        """Pico-valle del frente en ondas, MEDIDO sobre la pupila."""
        p = self._params
        v = p["W"][p["dentro"]]
        return float(v.max() - v.min())

    def strehl(self):
        """Razon de Strehl del frente medido (`strehl` con el RMS)."""
        return float(strehl(self.rms_ondas()))

    def con_coeficientes(self, coefs):
        """Pieza GEMELA con otros Zernike, ya escalada y colocada encima
        (para `Transform`: la rejilla se deforma sin saltos)."""
        p = self._params
        otra = frente_onda(coefs, radio=p["radio"], n_lineas=p["n_lineas"],
                           muestras=p["muestras"],
                           escala_ondas=p["escala_ondas"],
                           color=p["color"], res=p["res"])
        return self._alinear(otra)

    def plano(self):
        """La GEMELA sin aberracion (todas las lineas rectas): el "antes"
        del clip."""
        return self.con_coeficientes({})


def frente_onda(coefs=None, radio=1.5, n_lineas=11, muestras=61,
                escala_ondas=0.09, color=C_ONDA, res=96):
    """El frente de onda W(rho, phi) = suma c_i Z_i, dibujado como una
    rejilla deformada dentro de la pupila.

    `coefs` es un dict {nombre: ondas} con los nombres de `MODOS_ZERNIKE`
    ("desenfoque", "astigmatismo", "coma", "esferica"...) o {(n, m): c}.
    Cada linea horizontal se levanta `escala_ondas` unidades normalizadas
    por cada onda de frente: la deformacion esta EXAGERADA (una onda son
    633 nm y la pupila, metros).

    Como los Zernike estan normalizados, el RMS del frente es
    sqrt(suma c^2) — y `.rms_ondas()` lo MIDE sobre la pupila para
    comprobarlo.
    """
    coefs = {} if coefs is None else dict(coefs)
    n_lineas = _validar("frente_onda.n_lineas", n_lineas, CELDAS_MAX)
    muestras = _validar("frente_onda.muestras", muestras, PUNTOS_MAX)
    radio = float(radio)

    _, _, W, dentro = frente_de_coeficientes(coefs, res=res)

    def w_en(xs, ys):
        rho = np.hypot(xs, ys)
        phi = np.arctan2(ys, xs)
        out = np.zeros_like(xs)
        for clave, c in coefs.items():
            n, m = (MODOS_ZERNIKE[clave] if isinstance(clave, str)
                    else clave)
            out = out + float(c) * zernike(n, m, rho, phi)
        return out

    pupila = Circle(radius=radio, stroke_width=1.8, color=C_EJE)
    pupila.set_fill(opacity=0.0)

    lineas = VGroup()
    for k in range(n_lineas):
        y = -1.0 + 2.0 * (k + 0.5) / n_lineas
        semi = math.sqrt(max(1.0 - y * y, 0.0))
        if semi < 0.05:
            continue
        xs = np.linspace(-semi, semi, muestras)
        ys = np.full_like(xs, y)
        dy = float(escala_ondas) * w_en(xs, ys)
        pts = np.column_stack([xs * radio, (ys + dy) * radio])
        lineas.add(_poligonal(pts, color, 2.4))

    v = W[dentro]
    rms = float(np.sqrt(np.mean((v - v.mean()) ** 2)))
    lectura = _texto_hud(f"RMS = {rms:.3f} ondas", font_size=18,
                         color=C_MEDIDA)
    lectura.move_to(np.array([0.0, radio + 0.34, 0.0]))

    params = {"coefs": coefs, "radio": radio, "n_lineas": n_lineas,
              "muestras": muestras, "escala_ondas": float(escala_ondas),
              "color": color, "res": res, "W": W, "dentro": dentro}
    return FrenteOnda(_ancla(np.array([-radio, 0.0, 0.0])),
                      _ancla(np.array([radio, 0.0, 0.0])),
                      pupila, lineas, lectura, params)


class ShackHartmann(_Pieza):
    """La rejilla de microlentes y sus manchas desplazadas.

    Atributos: `.rejilla` (los cuadros), `.referencias` (los centros
    ideales), `.manchas` (los Dots violeta), `.pupila`, `.lectura`,
    `.desplazamientos` (dict (i,j) -> (dx, dy) en unidades de escena
    LOCALES)."""

    def __init__(self, ancla_a, ancla_b, pupila, rejilla, referencias,
                 manchas, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, pupila, rejilla, referencias,
                         manchas, lectura, **kwargs)
        self._ancla_a = ancla_a
        self._ancla_b = ancla_b
        self._largo_ref = 2.0 * params["radio"]
        self._p0 = (-params["radio"], 0.0, 0.0)
        self.pupila = pupila
        self.rejilla = rejilla
        self.referencias = referencias
        self.manchas = manchas
        self.lectura = lectura
        self._params = params
        self.desplazamientos = params["desplazamientos"]
        self.n = params["n"]

    def mancha(self, i, j):
        """El Dot de la microlente (i, j), i = fila (0 abajo), j = columna
        (0 a la izquierda). KeyError si esa lente cae fuera de la pupila."""
        return self._params["mapa"][(int(i), int(j))]

    def con_frente(self, coefs):
        """Pieza GEMELA con otro frente, ya escalada y encima (para
        `Transform`: las manchas se corren)."""
        p = self._params
        otra = shack_hartmann(coefs, n=p["n"], radio=p["radio"],
                              ganancia=p["ganancia"])
        return self._alinear(otra)


def shack_hartmann(coefs=None, n=8, radio=1.5, ganancia=0.10):
    """Shack-Hartmann: una rejilla de microlentes y una mancha por lente.

    Cada microlente no ve la fase, ve la PENDIENTE local del frente
    (`pendientes_locales`), y su mancha se corre proporcionalmente. Con el
    frente plano las manchas caen en el centro de su cuadro; con
    aberracion se descolocan, y de esos desplazamientos se reconstruye el
    frente.

    `ganancia` es la fraccion del PASO de la rejilla que se corre una
    mancha por cada onda de pendiente (ondas por radio de pupila): escala
    de DIBUJO, y ademas se recorta a 0.45 del paso para que ninguna mancha
    invada la celda vecina. Con el valor por omision, un desenfoque de
    0.5 ondas corre las manchas del borde ~0.35 celdas.
    """
    n = _validar("shack_hartmann.n", n, CELDAS_MAX)
    coefs = {} if coefs is None else dict(coefs)
    radio = float(radio)

    X, Y, W, dentro = frente_de_coeficientes(coefs, res=n, recortar=False)
    paso_norm = 2.0 / (n - 1) if n > 1 else 2.0
    # El gradiente se toma del polinomio SIN recortar: recortarlo antes
    # de derivar mete un escalon falso en las lentes del borde.
    gx, gy = pendientes_locales(W, paso_norm)

    pupila = Circle(radius=radio, stroke_width=1.8, color=C_EJE)
    pupila.set_fill(opacity=0.0)

    lado = paso_norm * radio * 0.92
    rejilla, referencias, manchas = VGroup(), VGroup(), VGroup()
    mapa, desplazamientos = {}, {}
    tope = 0.45 * paso_norm * radio
    k_esc = float(ganancia) * paso_norm * radio
    for i in range(n):
        for j in range(n):
            if not dentro[i, j]:
                continue
            cx, cy = X[i, j] * radio, Y[i, j] * radio
            q = Square(side_length=lado, stroke_width=1.2, color=C_EJE)
            q.set_fill(opacity=0.0)
            q.set_stroke(opacity=0.9)
            q.move_to(np.array([cx, cy, 0.0]))
            rejilla.add(q)
            r = Dot(np.array([cx, cy, 0.0]), radius=0.020, color=CODE_MUTED)
            r.set_opacity(0.75)
            referencias.add(r)
            dx = float(np.clip(-k_esc * gx[i, j], -tope, tope))
            dy = float(np.clip(-k_esc * gy[i, j], -tope, tope))
            d = Dot(np.array([cx + dx, cy + dy, 0.0]), radius=0.046,
                    color=C_FRANJA)
            manchas.add(d)
            mapa[(i, j)] = d
            desplazamientos[(i, j)] = (dx, dy)

    _, _, W_fino, dentro_fino = frente_de_coeficientes(coefs, res=96)
    v = W_fino[dentro_fino]
    rms = float(np.sqrt(np.mean((v - v.mean()) ** 2)))
    lectura = _texto_hud(f"{len(mapa)} microlentes    RMS = {rms:.3f} ondas",
                         font_size=17, color=C_MEDIDA)
    lectura.move_to(np.array([0.0, radio + 0.34, 0.0]))

    params = {"coefs": coefs, "n": n, "radio": radio,
              "ganancia": float(ganancia), "mapa": mapa,
              "desplazamientos": desplazamientos, "W": W, "dentro": dentro}
    return ShackHartmann(_ancla(np.array([-radio, 0.0, 0.0])),
                         _ancla(np.array([radio, 0.0, 0.0])),
                         pupila, rejilla, referencias, manchas, lectura,
                         params)


class TarjetasZernike(_PiezaImg):
    """Cuatro tarjetas con los modos que el curso nombra.

    `Group` (llevan imagen): `FadeIn`/`FadeTransform`, no `Transform`.
    Atributos: `.nombres`, `.vectorial`; `.tarjeta(nombre)` devuelve el
    Group de una tarjeta (imagen + marco + rotulo)."""

    def __init__(self, ancla_a, ancla_b, tarjetas, params, **kwargs):
        super().__init__(ancla_a, ancla_b, *tarjetas, **kwargs)
        self._ancla_a = ancla_a          # centro de la primera tarjeta
        self._ancla_b = ancla_b          # centro de la ultima
        self._largo_ref = params["largo_ref"]
        self._p0 = (params["x0"], 0.0, 0.0)
        self.tarjetas = list(tarjetas)
        self.vectorial = params["vectorial"]
        self._params = params
        self.nombres = params["nombres"]

    def tarjeta(self, nombre):
        """La tarjeta de ese modo ('desenfoque', 'astigmatismo', 'coma',
        'esferica')."""
        clave = _ascii(str(nombre)).lower()
        if clave not in self._params["mapa"]:
            raise ValueError(f"tarjeta: '{nombre}' no esta en "
                             f"{self.nombres}")
        return self._params["mapa"][clave]


def tarjetas_zernike(nombres=("desenfoque", "astigmatismo", "coma",
                              "esferica"), lado=2.0, sep=0.34, res=140,
                     coeficiente=1.0):
    """Las cuatro aberraciones que el curso nombra, como tarjetas.

    Cada tarjeta lleva el mapa del modo sobre la pupila (cian negativo,
    ambar positivo, fondo en el cero) y su nombre. Nombrar la aberracion
    es el primer paso para corregirla: el Shack-Hartmann da el mapa y
    Zernike le pone apellido.
    """
    lado, sep = float(lado), float(sep)
    nombres = [_ascii(str(x)).lower() for x in nombres]
    for nb in nombres:
        if nb not in MODOS_ZERNIKE:
            raise ValueError(f"tarjetas_zernike: modo '{nb}' desconocido "
                             f"({sorted(MODOS_ZERNIKE)})")

    X, Y = _malla(res, 1.0)
    rho, phi = np.hypot(X, Y), np.arctan2(Y, X)
    dentro = rho <= 1.0

    paso = lado + sep
    x0 = -(len(nombres) - 1) * paso / 2.0
    tarjetas, mapa = [], {}
    vectorial = VGroup()
    for k, nb in enumerate(nombres):
        n, m = MODOS_ZERNIKE[nb]
        Z = float(coeficiente) * zernike(n, m, rho, phi)
        Z = np.where(dentro, Z, 0.0)
        Z = Z / max(float(np.abs(Z).max()), _EPS)
        img = _imagen_divergente(Z, C_MEDIDA, C_ONDA, ancho=lado,
                                 alfa=dentro.astype(np.float64))
        cx = x0 + k * paso
        img.move_to(np.array([cx, 0.16, 0.0]))
        marco = RoundedRectangle(width=lado + 0.16, height=lado + 0.72,
                                 corner_radius=0.10, stroke_width=1.6,
                                 color=C_EJE)
        marco.set_fill(opacity=0.0)
        marco.move_to(np.array([cx, 0.0, 0.0]))
        aro = Circle(radius=lado / 2.0, stroke_width=1.2, color=C_EJE)
        aro.set_fill(opacity=0.0)
        aro.move_to(np.array([cx, 0.16, 0.0]))
        rot = _texto_hud(nb, font_size=16, color=CODE_INK)
        rot.move_to(np.array([cx, -lado / 2.0 - 0.16, 0.0]))
        vectorial.add(marco, aro, rot)
        t = Group(img, marco, aro, rot)
        tarjetas.append(t)
        mapa[nb] = t

    params = {"nombres": nombres, "lado": lado, "sep": sep, "x0": x0,
              "largo_ref": max((len(nombres) - 1) * paso, paso),
              "mapa": mapa, "vectorial": vectorial, "res": res}
    return TarjetasZernike(_ancla(np.array([x0, 0.0, 0.0])),
                           _ancla(np.array([x0 + (len(nombres) - 1) * paso,
                                            0.0, 0.0])),
                           tarjetas, params)


class EspejoDeformable(_Pieza):
    """El espejo deformable y el frente residual que deja.

    Atributos: `.espejo` (el arco), `.actuadores`, `.residual` (la curva
    de arriba), `.lectura`, `.k` (correccion en [0, 1]), `.sigma_ondas`."""

    def __init__(self, ancla_a, ancla_b, base, espejo, actuadores, eje,
                 residual, rotulos, lectura, params, **kwargs):
        super().__init__(ancla_a, ancla_b, base, actuadores, espejo, eje,
                         residual, rotulos, lectura, **kwargs)
        self._ancla_a = ancla_a
        self._ancla_b = ancla_b
        self._largo_ref = params["ancho"]
        self._p0 = (-params["ancho"] / 2.0, 0.0, 0.0)
        self.base = base
        self.espejo = espejo
        self.actuadores = actuadores
        self.eje = eje
        self.residual = residual
        self.rotulos = rotulos
        self.lectura = lectura
        self._params = params
        self.k = 0.0
        self.sigma_ondas = params["sigma0"]

    def _perfil(self, k):
        p = self._params
        sigma = p["sigma0"] + (p["sigma1"] - p["sigma0"]) * float(k)
        return sigma, p["forma"] * sigma * p["escala"]

    def strehl(self):
        """Razon de Strehl del estado actual, con `strehl(sigma)`.

        Arranca en 0.30 (sigma = lambda/5.7) y llega a 0.818 con
        sigma = lambda/14. El 0.80 clasico del criterio de Marechal sale de
        `strehl_lineal` (0.799): son la misma formula con y sin
        aproximacion."""
        return float(strehl(self.sigma_ondas))

    def a_correccion(self, k):
        """MUTA la pieza: `k` en [0, 1] es cuanto corrige el espejo. 0 deja
        el residual entero (Strehl 0.30) y 1 lo baja a lambda/14
        (Strehl 0.818). Devuelve self."""
        p = self._params
        self.k = float(np.clip(float(k), 0.0, 1.0))
        sigma, y = self._perfil(self.k)
        self.sigma_ondas = sigma
        _fijar(self.residual,
               self._a_escena(np.column_stack([p["x"], p["y_res"] + y])))
        for act, forma in zip(self.actuadores, p["forma_act"]):
            h = max(p["alto_act"] * (0.5 + 0.5 * self.k * forma), 0.05)
            esc = self._escala_actual()
            act.stretch_to_fit_height(h * esc)
            act.move_to(self._punto((float(act._x_local),
                                     p["y_act"] + h / 2.0)))
        denom = 1.0 / max(sigma, _EPS)
        self.lectura = self._relectura(
            self.lectura,
            f"RMS = lambda/{denom:4.1f}    Strehl = {self.strehl():.2f}",
            font_size=18, color=C_MEDIDA)
        return self


def espejo_deformable(n_act=7, ancho=5.2, strehl_inicial=0.30,
                      sigma_final=1.0 / 14.0, muestras=241):
    """El espejo deformable: actuadores que empujan la superficie hasta
    aplanar el frente.

    Arriba, el frente residual (ambar) que queda despues de corregir;
    abajo, el espejo (verde) y sus actuadores (cian). `.a_correccion(k)`
    lleva el RMS de `sigma_de_strehl(strehl_inicial)` = lambda/5.7 (Strehl
    0.30) hasta `sigma_final` = lambda/14 (Strehl 0.818 con `strehl`, el
    0.80 redondo del criterio de Marechal con `strehl_lineal`).

    La forma del residual es determinista (dos cosenos incomensurables) y
    esta normalizada a RMS 1, asi que la amplitud dibujada ES proporcional
    al sigma que se rotula. La escala vertical va exagerada.
    """
    n_act = _validar("espejo_deformable.n_act", n_act, ACTUADORES_MAX)
    muestras = _validar("espejo_deformable.muestras", muestras, PUNTOS_MAX)
    ancho = float(ancho)
    sigma0 = sigma_de_strehl(strehl_inicial)
    sigma1 = float(sigma_final)

    x = np.linspace(-ancho / 2.0, ancho / 2.0, muestras)
    u = x / (ancho / 2.0)
    forma = 0.72 * np.cos(2.1 * PI * u + 0.4) + 0.42 * np.cos(4.7 * PI * u
                                                              - 1.1)
    forma = forma - forma.mean()
    forma = forma / max(float(np.sqrt(np.mean(forma ** 2))), _EPS)
    escala = 0.62 / max(sigma0, _EPS)          # unidades de escena por onda
    y_res = 1.35

    eje = Line(np.array([-ancho / 2.0, y_res, 0.0]),
               np.array([ancho / 2.0, y_res, 0.0]), stroke_width=1.2,
               color=C_EJE)
    residual = _poligonal(np.column_stack([x, y_res + forma * sigma0
                                           * escala]), C_ONDA, 3.0)

    arco = ArcBetweenPoints(np.array([-ancho / 2.0, -0.30, 0.0]),
                            np.array([ancho / 2.0, -0.30, 0.0]),
                            angle=-0.55, stroke_width=5.0, color=C_OBJETO)
    espejo = VGroup(arco)

    y_act = -1.55
    alto_act = 0.62
    xs_act = np.linspace(-ancho / 2.0 * 0.82, ancho / 2.0 * 0.82, n_act)
    forma_act = np.cos(2.1 * PI * (xs_act / (ancho / 2.0)) + 0.4)
    actuadores = VGroup()
    for xa, fa in zip(xs_act, forma_act):
        h = alto_act * 0.5
        a = Rectangle(width=0.16, height=h, stroke_width=1.4,
                      color=C_MEDIDA)
        a.set_fill(C_MEDIDA, opacity=0.35)
        a.move_to(np.array([xa, y_act + h / 2.0, 0.0]))
        a._x_local = float(xa)
        actuadores.add(a)
    conectores = VGroup(*[
        Line(np.array([xa, y_act + alto_act * 0.5, 0.0]),
             np.array([xa, -0.42, 0.0]), stroke_width=1.2, color=C_EJE)
        for xa in xs_act])
    espejo.add(conectores)
    base = Line(np.array([-ancho / 2.0 * 0.92, y_act, 0.0]),
                np.array([ancho / 2.0 * 0.92, y_act, 0.0]),
                stroke_width=3.0, color=C_EJE)

    rotulos = VGroup()
    t_r = _texto_hud("frente residual", font_size=16, color=C_ONDA)
    t_r.move_to(np.array([0.0, y_res + 1.05, 0.0]))
    rotulos.add(t_r)
    t_e = _texto_hud("espejo deformable", font_size=16, color=C_OBJETO)
    t_e.move_to(np.array([0.0, 0.34, 0.0]))
    rotulos.add(t_e)
    t_a = _texto_hud(f"{n_act} actuadores", font_size=15, color=C_MEDIDA)
    t_a.move_to(np.array([0.0, y_act - 0.30, 0.0]))
    rotulos.add(t_a)

    lectura = _texto_hud(f"RMS = lambda/{1.0 / sigma0:4.1f}    Strehl = "
                         f"{float(strehl(sigma0)):.2f}", font_size=18,
                         color=C_MEDIDA)
    lectura.move_to(np.array([0.0, y_res + 1.42, 0.0]))

    params = {"ancho": ancho, "sigma0": sigma0, "sigma1": sigma1,
              "forma": forma, "escala": escala, "x": x, "y_res": y_res,
              "y_act": y_act, "alto_act": alto_act,
              "forma_act": forma_act, "n_act": n_act,
              "muestras": muestras}
    return EspejoDeformable(_ancla(np.array([-ancho / 2.0, 0.0, 0.0])),
                            _ancla(np.array([ancho / 2.0, 0.0, 0.0])),
                            base, espejo, actuadores, eje, residual,
                            rotulos, lectura, params)
