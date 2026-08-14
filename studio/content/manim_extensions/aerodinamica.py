"""Aerodinamica de alta velocidad: compresibilidad, energias, regimenes y el
cono de Mach.

Pensado para la familia de cursos "Aerodinamica" (leccion 1.1 en adelante).
Todo el calculo es numpy puro y determinista — sin red, sin disco, sin azar —
condicion necesaria para trabajar con `--disable_caching`: mismo script, mismo
render.

La regla de color del curso, que es tambien la de esta libreria: **el color
dice a que velocidad se vuela**. Cuanto mas rapido, mas caliente.

    subsonico   verde    el aire aun se aparta a tiempo
    transonico  ambar    conviven zonas sub y supersonicas
    supersonico rojo     la informacion ya no llega antes que el vehiculo
    hipersonico violeta  la quimica y el calor mandan sobre la aerodinamica

Ademas: cian para lo que se CALCULA (umbrales, resultados, energia termica) y
el gris azulado `COLOR_EJE` para el mobiliario (ejes, guias, muescas). No
mezclar roles: una banda de regimenes debe poder leerse sin narracion.

Funciones (los numeros que el clip rotula salen de aqui, nunca a mano):
    velocidad_sonido        a = sqrt(gamma R T)
    isa                     atmosfera estandar hasta 20 km -> (T, p, rho, a)
    razon_densidad          rho0/rho = (1 + 0.2 M^2)^2.5
    error_incompresible     cuanto miente suponer densidad constante
    mach_de_error           el Mach al que ese error alcanza un porcentaje
    razon_energias          (V^2/2)/e = gamma(gamma-1)/2 M^2
    angulo_mach             mu = arcsen(1/M), en grados

Piezas:
    curva_compresibilidad   el error del modelo incompresible frente a M
    balanza_energias        movimiento contra agitacion termica, en reparto
    banda_regimenes         la regla de los cuatro regimenes de vuelo
    frentes_moviles         las ondas que emite una fuente en movimiento

Las piezas exponen localizadores (`.punto_de`, `.fuente`, `.centro_zona`)
que se recalculan sobre la posicion ACTUAL del mobject: siguen siendo validos
tras un `move_to` o un `shift`, asi que los clips cuelgan flechas, llaves y
tags sin adivinar coordenadas. Lo que NO siguen es un `scale` — la escala se
elige al construir (`ancho`, `alto`) y no se toca despues; es la misma regla
que en `enlace.py` y `espectro.py`. Y exponen los NUMEROS que dibujan
(`.error`, `.razon`, `.mu`): el rotulo del clip debe salir de la misma fuente
que el trazo.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`MUESTRAS_MAX`, `ONDAS_MAX` y `ZONAS_MAX` levantan ValueError; pasarse cambia
lo que se ve y es mejor enterarse.

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from aerodinamica import banda_regimenes, frentes_moviles

    banda = banda_regimenes()
    self.add(Dot(banda.punto_de(2.02)))          # y banda.zona_de(2.02)

    ondas = frentes_moviles(0.0)
    self.play(Transform(ondas, ondas.con_mach(2.0)))   # y ondas.mu() -> 30.0
"""

import numpy as np

from manim import (AnimationGroup, Circle, DashedLine, Dot, Line, Rectangle,
                   Text, Transform, VGroup, VMobject, DOWN, LEFT, ORIGIN, UP)

from code_brand import FUENTE_DISPLAY, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
MUESTRAS_MAX = 400      # muestras de una curva parametrica
ONDAS_MAX = 12          # frentes de onda de una fuente movil
ZONAS_MAX = 6           # zonas de la banda de regimenes

# Paleta propia de la libreria (coincide con la del curso): el color ES el
# regimen. Ver la nota del docstring — cuanto mas rapido, mas caliente.
COLOR_SUBSONICO = "#34d399"    # verde: el aire se aparta a tiempo
COLOR_TRANSONICO = "#f59e0b"   # ambar: conviven zonas sub y supersonicas
COLOR_SUPERSONICO = "#f43f5e"  # rojo: choques, el vehiculo llega sin avisar
COLOR_HIPERSONICO = "#a78bfa"  # violeta: calor y quimica
COLOR_CALCULO = "#22d3ee"      # cian: umbrales, resultados, energia termica
COLOR_EJE = "#31414f"          # mobiliario: ejes, guias, muescas

# Alias cortos, para que el style_block de los clips escriba `color=C_CHOQUE`.
C_SUB, C_TRANS = COLOR_SUBSONICO, COLOR_TRANSONICO
C_SUPER, C_HIPER = COLOR_SUPERSONICO, COLOR_HIPERSONICO
C_CALCULO, C_EJE = COLOR_CALCULO, COLOR_EJE
C_CHOQUE = COLOR_SUPERSONICO   # una onda de choque es, por definicion, super

# Constantes fisicas del aire (las del curso, en un solo sitio).
GAMMA = 1.4              # razon de calores especificos del aire
R_AIRE = 287.05          # constante del gas, J/(kg K)
T0_ISA = 288.15          # temperatura al nivel del mar, K
P0_ISA = 101325.0        # presion al nivel del mar, Pa
LAPSE = 0.0065           # gradiente termico de la troposfera, K/m
H_TROPOPAUSA = 11000.0   # techo de la troposfera ISA, m
T_TROPOPAUSA = 216.65    # temperatura de la estratosfera baja ISA, K
P_TROPOPAUSA = 22632.06  # presion en la tropopausa, Pa
G0 = 9.80665             # gravedad estandar, m/s^2

# Fronteras de los regimenes de vuelo, tal y como las usa el curso:
# (nombre, M inicial, M final, color). El limite subsonico/transonico en 0.8 y
# el transonico/supersonico en 1.2 son convenciones de ingenieria (el flujo
# local ya es supersonico bastante antes de M = 1), no numeros exactos.
REGIMENES = (("Subsónico", 0.0, 0.8, COLOR_SUBSONICO),
             ("Transónico", 0.8, 1.2, COLOR_TRANSONICO),
             ("Supersónico", 1.2, 5.0, COLOR_SUPERSONICO),
             ("Hipersónico", 5.0, 30.0, COLOR_HIPERSONICO))

_EPS = 1e-9


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Etiqueta tecnica en la tipografia de telemetria de la marca.

    SOLO ASCII: Space Mono no trae superindices ni acentos fiables (un "M²"
    sale renderizado como "M'"). Lo que lleve acento o exponente va en
    `_texto_display` o en un MathTex del clip.
    """
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _texto_display(texto, font_size=18, color=COLOR_EJE):
    """Etiqueta con palabras de verdad (acentos incluidos), en Rajdhani."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_DISPLAY, font_size=font_size,
                color=color)


def _curva(puntos, color, grosor=2.8):
    """VMobject suave a partir de un array (n, 2) o (n, 3) de escena."""
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly(pts)
    return curva


def _validar_muestras(nombre, muestras):
    """Tope duro comun a todas las curvas parametricas de la libreria."""
    n = int(muestras)
    if n > MUESTRAS_MAX:
        raise ValueError(
            f"{nombre}: muestras={n} supera MUESTRAS_MAX={MUESTRAS_MAX}")
    return max(8, n)


def _ejes_xy(ancho, alto, color=COLOR_EJE):
    """Par de ejes en L con origen en la esquina inferior izquierda, centrados
    en ORIGIN. Devuelve (VGroup, origen) con el origen ya en coordenadas de
    escena para que quien llama situe sus curvas."""
    x0, y0 = -ancho / 2, -alto / 2
    eje_x = Line((x0, y0, 0), (x0 + ancho, y0, 0), stroke_width=2.0,
                 color=color)
    eje_y = Line((x0, y0, 0), (x0, y0 + alto, 0), stroke_width=2.0,
                 color=color)
    return VGroup(eje_x, eje_y), np.array([x0, y0, 0.0])


# --- los numeros del aire ----------------------------------------------
def velocidad_sonido(t_kelvin):
    """a = sqrt(gamma R T) en m/s. Acepta escalares o arrays.

    Es LA razon por la que el numero de Mach depende de la altitud y no solo
    de la velocidad: a solo depende de la temperatura.
    """
    t = np.maximum(np.asarray(t_kelvin, dtype=np.float64), _EPS)
    return np.sqrt(GAMMA * R_AIRE * t)


def isa(altitud_m):
    """Atmosfera estandar internacional hasta 20 km -> (T, p, rho, a).

    Dos tramos, que es lo que el curso usa: troposfera con gradiente lineal
    hasta 11 km y estratosfera isoterma por encima. Mas arriba de 20 km el
    modelo de dos tramos ya no vale y levanta ValueError en vez de devolver
    un numero silenciosamente equivocado.
    """
    h = float(altitud_m)
    if not -1000.0 <= h <= 20000.0:
        raise ValueError(f"isa: altitud {h} m fuera del rango -1000..20000")
    if h <= H_TROPOPAUSA:
        t = T0_ISA - LAPSE * h
        p = P0_ISA * (t / T0_ISA) ** (G0 / (LAPSE * R_AIRE))
    else:
        t = T_TROPOPAUSA
        p = P_TROPOPAUSA * np.exp(-G0 * (h - H_TROPOPAUSA)
                                  / (R_AIRE * T_TROPOPAUSA))
    rho = p / (R_AIRE * t)
    return float(t), float(p), float(rho), float(velocidad_sonido(t))


def razon_densidad(mach):
    """rho0/rho = (1 + (gamma-1)/2 M^2)^(1/(gamma-1)).

    La densidad de estancamiento frente a la de la corriente: cuanto se
    comprime el aire al frenarlo isentropicamente hasta el reposo. Con
    gamma = 1.4 el exponente es 2.5.
    """
    m = np.asarray(mach, dtype=np.float64)
    return (1 + (GAMMA - 1) / 2 * m ** 2) ** (1 / (GAMMA - 1))


def error_incompresible(mach):
    """Cuanto miente suponer densidad constante, en fraccion (0.046 = 4.6 %).

    Es `razon_densidad(M) - 1`: el cambio relativo de densidad que el modelo
    incompresible tira a la basura. El criterio M < 0.3 del curso sale de
    aqui — a M = 0.3 vale un 4.6 %, todavia por debajo del 5 % que se admite
    como error tolerable.
    """
    return razon_densidad(mach) - 1.0


def mach_de_error(fraccion=0.05):
    """El Mach al que `error_incompresible` alcanza esa fraccion.

    Invierte la relacion en forma cerrada (no busca a ciegas): de
    (1 + 0.2 M^2)^2.5 = 1 + f sale M = sqrt(((1+f)^0.4 - 1)/0.2). Con f = 0.05
    da 0.313, que es de donde viene la regla de oro del 0.3.
    """
    f = float(fraccion)
    if f <= 0:
        raise ValueError("mach_de_error: la fraccion debe ser positiva")
    interior = (1 + f) ** (GAMMA - 1) - 1
    return float(np.sqrt(interior / ((GAMMA - 1) / 2)))


def razon_energias(mach):
    """(energia cinetica)/(energia interna) = gamma(gamma-1)/2 M^2.

    La lectura fisica del numero de Mach: no es "una velocidad", es cuanta
    energia ordenada de movimiento lleva el flujo frente a la energia
    desordenada de agitacion termica que ya tenia. Con gamma = 1.4 el factor
    es 0.28, asi que a M = 1 el movimiento aporta un 28 % de lo que aporta el
    calor, y a M = 5 lo septuplica.
    """
    m = np.asarray(mach, dtype=np.float64)
    return GAMMA * (GAMMA - 1) / 2 * m ** 2


def angulo_mach(mach):
    """mu = arcsen(1/M) en GRADOS. Solo tiene sentido con M >= 1.

    Por debajo de 1 no hay cono (las ondas se adelantan al vehiculo) y
    devuelve 90 grados, que es el limite continuo desde M = 1: el "cono" es
    entonces el propio frente plano que envuelve a la fuente.
    """
    m = float(mach)
    if m <= 1.0:
        return 90.0
    return float(np.degrees(np.arcsin(1.0 / m)))


def zona_de(mach):
    """Nombre del regimen al que pertenece ese Mach ('Transónico', ...)."""
    m = float(mach)
    for nombre, m0, m1, _ in REGIMENES:
        if m0 <= m < m1:
            return nombre
    return REGIMENES[-1][0]


# --- 1.1.1 el error del modelo incompresible ---------------------------
class CurvaCompresibilidad(VGroup):
    """Cuanto miente la densidad constante, y hasta donde se le perdona."""

    def __init__(self, ejes, curva, banda, umbral, etiquetas, rango_m,
                 rango_err, ancho, alto, origen, **kwargs):
        super().__init__(ejes, banda, umbral, curva, etiquetas, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.banda = banda
        self.umbral = umbral
        self.etiquetas = etiquetas
        self._m = rango_m
        self._err = rango_err
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        # Centro al construir: `punto_de` le suma el desplazamiento acumulado
        # y por eso sigue valiendo tras un move_to. Se congela AQUI y no la
        # primera vez que se pide, o el primer uso tras mover fijaria el
        # centro ya desplazado y el localizador quedaria mudo.
        self._centro_original = self.get_center()

    def error(self, mach):
        """El valor que el clip rotula, en fraccion. Misma fuente que el trazo."""
        return float(error_incompresible(mach))

    def punto_de(self, mach):
        """Punto de escena sobre la curva a ese Mach."""
        m0, m1 = self._m
        e0, e1 = self._err
        x = (float(np.clip(mach, m0, m1)) - m0) / (m1 - m0)
        y = (self.error(mach) - e0) / (e1 - e0)
        desplazamiento = self.get_center() - self._centro_original
        return (self._origen
                + np.array([x * self._ancho,
                            float(np.clip(y, 0.0, 1.0)) * self._alto, 0.0])
                + desplazamiento)


def curva_compresibilidad(m_max=1.0, umbral=0.05, ancho=5.8, alto=2.7,
                          color=COLOR_TRANSONICO, color_banda=COLOR_SUBSONICO,
                          color_umbral=COLOR_CALCULO, color_ejes=COLOR_EJE,
                          font_size=14, muestras=160):
    """Ejes (Mach ->, error de densidad % ^) con la curva del error y la banda
    verde donde el modelo incompresible aun se sostiene.

    La banda NO llega hasta 0.3 redondo sino hasta `mach_de_error(umbral)`,
    que con el 5 % vale 0.313: el 0.3 de los libros es ese numero redondeado
    a la baja, y la libreria dibuja el de verdad. La linea de umbral cruza
    todo el ancho para que se lea como un criterio, no como un punto.
    """
    muestras = _validar_muestras("curva_compresibilidad", muestras)
    m1 = float(m_max)
    if m1 <= 0:
        raise ValueError("curva_compresibilidad: m_max debe ser positivo")
    m_umbral = mach_de_error(umbral)

    ms = np.linspace(0.0, m1, muestras)
    errs = np.asarray(error_incompresible(ms), dtype=np.float64)
    e_hi = float(errs.max()) * 1.08

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    x = ms / m1
    y = errs / e_hi
    pts = origen + np.column_stack([x * ancho, y * alto, np.zeros_like(x)])
    curva = _curva(pts, color, grosor=3.0)

    # Banda verde: la region de Mach donde el error se queda bajo el umbral.
    x_umbral = float(np.clip(m_umbral / m1, 0.0, 1.0)) * ancho
    banda = Rectangle(width=max(x_umbral, 0.02), height=alto, stroke_width=0,
                      fill_color=color_banda, fill_opacity=0.14)
    banda.move_to(origen + np.array([x_umbral / 2, alto / 2, 0.0]))

    # Linea de umbral: el 5 % que la ingenieria admite, de lado a lado.
    y_umbral = float(np.clip(umbral / e_hi, 0.0, 1.0)) * alto
    linea = DashedLine(origen + np.array([0.0, y_umbral, 0.0]),
                       origen + np.array([ancho, y_umbral, 0.0]),
                       stroke_width=1.6, color=color_umbral, dash_length=0.08)

    etiquetas = VGroup()
    tag_umbral = _texto_hud(f"{umbral * 100:.0f} %", font_size=font_size,
                            color=color_umbral)
    tag_umbral.next_to(linea.get_end(), UP, buff=0.08).shift(LEFT * 0.16)
    # El Mach de corte va BAJO el eje, no dentro de la banda: dentro compite
    # con la curva justo donde esta mas tumbada y las dos se tocan.
    tag_m = _texto_hud(f"M = {m_umbral:.2f}", font_size=font_size,
                       color=color_banda)
    tag_m.move_to(origen + np.array([x_umbral, -0.28, 0.0]))
    etiquetas.add(tag_umbral, tag_m)

    tag_x = _texto_hud("MACH", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.52)
    tag_y = _texto_display("error de densidad", font_size=font_size + 2)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaCompresibilidad(ejes, curva, banda, linea, etiquetas,
                                (0.0, m1), (0.0, e_hi), ancho, alto, origen)


# --- 1.1.2 el Mach como razon de energias ------------------------------
class BalanzaEnergias(VGroup):
    """Movimiento contra agitacion termica: quien manda en el flujo.

    Las barras muestran el REPARTO (cada una sobre el total), no el cociente
    crudo: a M = 5 el movimiento septuplica al calor y una barra proporcional
    se saldria del encuadre siete veces. El cociente exacto va en el rotulo,
    que es donde un numero grande no rompe nada.
    """

    def __init__(self, marco, barras, rotulo, mach, alto, ancho, font_size,
                 colores, **kwargs):
        super().__init__(marco, barras, rotulo, **kwargs)
        self.marco = marco
        self.barras = barras
        self.rotulo = rotulo
        self.mach = float(mach)
        self._alto = float(alto)
        self._ancho = float(ancho)
        self._font_size = font_size
        self._colores = colores

    def razon(self, mach=None):
        """(cinetica)/(interna) al Mach actual, o al que se le pase."""
        return float(razon_energias(self.mach if mach is None else mach))

    def reparto(self, mach=None):
        """Fraccion del total que aporta el MOVIMIENTO (0-1)."""
        r = self.razon(mach)
        return r / (1.0 + r)

    def _columna(self, i, frac):
        """Rectangulo de la barra i con esa fraccion de altura, apoyado en el
        suelo del marco (no centrado: una barra crece desde abajo)."""
        base = self.barras[i][0]
        alto = max(self._alto * float(np.clip(frac, 0.0, 1.0)), 0.03)
        col = Rectangle(width=self._ancho, height=alto, stroke_width=0,
                        fill_color=self._colores[i], fill_opacity=0.85)
        col.move_to(np.array([base.get_center()[0],
                              self.marco.get_bottom()[1] + alto / 2, 0.0]))
        return col

    def a_mach(self, mach):
        """Animacion unica que reescala las DOS barras y reescribe el rotulo.

        Van juntas a proposito: en animaciones separadas el numero y las
        barras se desincronizan medio segundo, y una balanza que miente medio
        segundo es peor que no ponerla.
        """
        m = float(mach)
        frac = self.reparto(m)
        nuevo_rotulo = _texto_hud(f"M = {m:g}   ratio {self.razon(m):.2f}",
                                  font_size=self._font_size,
                                  color=self._colores[0])
        nuevo_rotulo.move_to(self.rotulo.get_center())
        self.mach = m
        return AnimationGroup(
            Transform(self.barras[0][0], self._columna(0, frac)),
            Transform(self.barras[1][0], self._columna(1, 1.0 - frac)),
            Transform(self.rotulo, nuevo_rotulo))


def balanza_energias(mach=0.3, alto=2.4, ancho=0.68, separacion=1.5,
                     color_movimiento=COLOR_TRANSONICO,
                     color_termica=COLOR_CALCULO, color_eje=COLOR_EJE,
                     font_size=16):
    """Dos columnas apoyadas en el mismo suelo: movimiento y agitacion termica.

    Es la lectura fisica del numero de Mach — no una velocidad, un reparto de
    energia. Al subir M la columna del movimiento se come a la termica.
    """
    # El suelo sobresale media columna a cada lado de las barras (que estan
    # en +-separacion/2), lo justo para que se lea como un apoyo comun y no
    # como un eje suelto que las desborda.
    medio = separacion / 2 + ancho
    marco = Line((-medio, 0, 0), (medio, 0, 0), stroke_width=2.0,
                 color=color_eje)
    colores = (color_movimiento, color_termica)
    nombres = ("movimiento", "térmica")

    r = float(razon_energias(mach))
    fracs = (r / (1 + r), 1 / (1 + r))

    barras = VGroup()
    for i, (frac, color, nombre) in enumerate(zip(fracs, colores, nombres)):
        x = (-separacion / 2 if i == 0 else separacion / 2)
        col = Rectangle(width=ancho, height=max(alto * frac, 0.03),
                        stroke_width=0, fill_color=color, fill_opacity=0.85)
        col.move_to((x, col.height / 2, 0))
        tag = _texto_display(nombre, font_size=font_size + 1, color=color)
        tag.move_to((x, -0.30, 0))
        barras.add(VGroup(col, tag))

    rotulo = _texto_hud(f"M = {mach:g}   ratio {r:.2f}", font_size=font_size,
                        color=color_movimiento)
    rotulo.move_to((0, alto + 0.34, 0))

    balanza = BalanzaEnergias(marco, barras, rotulo, mach, alto, ancho,
                              font_size, colores)
    # El marco se dibujo en y = 0 y las barras crecen hacia arriba: se recentra
    # el conjunto para que `move_to` del clip sitúe el centro visual.
    balanza.shift(DOWN * alto / 2)
    return balanza


# --- 1.1.3 la regla de los regimenes -----------------------------------
class BandaRegimenes(VGroup):
    """Los cuatro regimenes de vuelo, cada uno con el mismo ancho en pantalla.

    OJO, y es deliberado: el eje NO es lineal en Mach. El regimen supersonico
    abarca de 1.2 a 5 y el hipersonico de 5 a 25; en un eje lineal el
    transonico — que es donde ocurre casi todo lo interesante — seria una
    rendija de dos pixeles. Cada zona ocupa lo mismo y dentro de ella la
    interpolacion si es lineal, asi que `punto_de` es continuo y monotono: se
    puede colgar un avion en su Mach real sin mentir sobre el ORDEN, solo
    sobre la escala. Las fronteras van rotuladas con su numero justamente para
    que el espectador vea que los tramos no son comparables.
    """

    def __init__(self, eje, zonas, nombres, fronteras, ancho, alto, origen,
                 **kwargs):
        super().__init__(zonas, eje, nombres, fronteras, **kwargs)
        self.eje = eje
        self.zonas = zonas
        self.nombres = nombres
        self.fronteras = fronteras
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        self._n = len(REGIMENES)
        # Ver la nota de CurvaCompresibilidad.
        self._centro_original = self.get_center()

    def _x_relativa(self, mach):
        """Fraccion 0-1 del ancho para ese Mach, zona a zona."""
        m = float(mach)
        paso = 1.0 / self._n
        for i, (_, m0, m1, _c) in enumerate(REGIMENES):
            if m < m1 or i == self._n - 1:
                dentro = (np.clip(m, m0, m1) - m0) / max(m1 - m0, _EPS)
                return float(np.clip((i + dentro) * paso, 0.0, 1.0))
        return 1.0

    def punto_de(self, mach, altura=0.0):
        """Punto sobre la regla a ese Mach (`altura` en unidades de escena
        para colgar marcadores por encima o por debajo sin recalcular nada)."""
        desplazamiento = self.get_center() - self._centro_original
        return (self._origen
                + np.array([self._x_relativa(mach) * self._ancho,
                            self._alto / 2 + float(altura), 0.0])
                + desplazamiento)

    def zona(self, i):
        """El rectangulo de la zona i (para Indicate o para cambiar opacidad)."""
        return self.zonas[i % len(self.zonas)]

    def centro_zona(self, i):
        """Centro actual de la zona i."""
        return self.zona(i).get_center()

    def indice_de(self, mach):
        """Indice de la zona a la que pertenece ese Mach."""
        m = float(mach)
        for i, (_, m0, m1, _c) in enumerate(REGIMENES):
            if m0 <= m < m1:
                return i
        return len(REGIMENES) - 1

    def zona_de(self, mach):
        """Nombre del regimen de ese Mach ('Supersónico', ...)."""
        return REGIMENES[self.indice_de(mach)][0]

    def color_de(self, mach):
        """Color del regimen de ese Mach: el clip pinta su marcador con el."""
        return REGIMENES[self.indice_de(mach)][3]


def banda_regimenes(ancho=9.4, alto=0.62, font_size=18, color_eje=COLOR_EJE,
                    opacidad=0.30):
    """Regla horizontal de los cuatro regimenes, con las fronteras rotuladas.

    Los nombres van DENTRO de su zona y los numeros de frontera DEBAJO de la
    regla: en la misma linea, el nombre del transonico (la zona mas estrecha
    en Mach y aqui igual de ancha que las demas) chocaria con los dos numeros
    que la limitan.
    """
    if len(REGIMENES) > ZONAS_MAX:
        raise ValueError(f"banda_regimenes: {len(REGIMENES)} zonas supera "
                         f"ZONAS_MAX={ZONAS_MAX}")
    n = len(REGIMENES)
    paso = ancho / n
    x0 = -ancho / 2
    origen = np.array([x0, -alto / 2, 0.0])

    zonas = VGroup()
    nombres = VGroup()
    fronteras = VGroup()
    for i, (nombre, m0, _m1, color) in enumerate(REGIMENES):
        x = x0 + (i + 0.5) * paso
        caja = Rectangle(width=paso, height=alto, stroke_width=1.2,
                         color=color, fill_color=color, fill_opacity=opacidad)
        caja.move_to((x, 0, 0))
        zonas.add(caja)

        tag = _texto_display(nombre, font_size=font_size, color=color)
        if tag.width > paso - 0.16:
            tag.scale_to_fit_width(paso - 0.16)
        tag.move_to((x, 0, 0))
        nombres.add(tag)

        if i > 0:
            num = _texto_hud(f"{m0:g}", font_size=font_size - 3, color=color)
            num.move_to((x0 + i * paso, -alto / 2 - 0.26, 0))
            fronteras.add(num)

    eje = Line((x0, -alto / 2, 0), (x0 + ancho, -alto / 2, 0),
               stroke_width=2.0, color=color_eje)
    tag_eje = _texto_hud("MACH", font_size=font_size - 4, color=color_eje)
    tag_eje.next_to(eje, LEFT, buff=0.18)
    eje = VGroup(eje, tag_eje)

    return BandaRegimenes(eje, zonas, nombres, fronteras, ancho, alto, origen)


# --- 1.1.3 / 1.3.4 las ondas de una fuente en movimiento ---------------
class FrentesMoviles(VGroup):
    """Los frentes que emite una fuente que se mueve, y el cono que forman.

    Cada circunferencia es el sonido emitido k intervalos atras: nacio en
    x = -M k d (la fuente ya no esta alli) y ha crecido hasta un radio k d.
    Con M < 1 los frentes se adelantan y el aire "se entera" antes de que el
    vehiculo llegue; a M = 1 todos son tangentes en la propia fuente — la
    pared; con M > 1 la envolvente es el cono de Mach de semiangulo
    mu = arcsen(1/M).
    """

    def __init__(self, ondas, cono, fuente, estela, mach, params, **kwargs):
        super().__init__(ondas, cono, estela, fuente, **kwargs)
        self.ondas = ondas
        self.cono = cono
        self.punto_fuente = fuente
        self.estela = estela
        self.mach = float(mach)
        self._params = params
        # Vector del centro del bounding box al PUNTO FUENTE. Se guarda porque
        # el dibujo es asimetrico: su centro geometrico no es donde esta la
        # fuente, y sin esto un `move_to` deja el cono colgando de un sitio
        # que no es el vehiculo.
        self._al_origen = fuente.get_center() - self.get_center()

    def fuente(self):
        """Donde esta AHORA el emisor (no el centro del dibujo)."""
        return self.get_center() + self._al_origen

    def mu(self):
        """Semiangulo del cono de Mach en grados (90 si aun no hay cono)."""
        return angulo_mach(self.mach)

    def onda(self, k):
        """La circunferencia k-esima (0 = la mas vieja y por tanto la mayor)."""
        return self.ondas[k % len(self.ondas)]

    def con_mach(self, mach):
        """El mismo dibujo a otro Mach, con la FUENTE en el mismo sitio: el
        argumento natural de un Transform.

        Se ancla por la fuente y no por el centro a proposito — al abrirse o
        cerrarse el cono, centro y fuente se separan, y anclar por centro
        haria que el vehiculo se deslizara solo durante la animacion.
        """
        otro = frentes_moviles(mach=mach, **self._params)
        otro.shift(self.fuente() - otro.fuente())
        return otro


def frentes_moviles(mach=0.0, n_ondas=5, paso=0.58, color=COLOR_CALCULO,
                    color_cono=COLOR_SUPERSONICO, color_fuente=None,
                    grosor=1.8):
    """Frentes de onda de una fuente que avanza hacia la DERECHA, mas su cono.

    `paso` es el radio que gana una onda por intervalo (y tambien lo que
    avanza la fuente por intervalo a M = 1), asi que la geometria a M = 1 sale
    exactamente tangente sin ajustar nada a ojo.

    El cono se construye SIEMPRE con dos lineas, aunque a M <= 1 sean de
    longitud cero y opacidad cero: asi un Transform entre dos Mach interpola
    submobject a submobject en vez de aparearlos al azar.
    """
    m = float(mach)
    if m < 0:
        raise ValueError("frentes_moviles: el Mach no puede ser negativo")
    n = int(n_ondas)
    if n > ONDAS_MAX:
        raise ValueError(f"frentes_moviles: n_ondas={n} supera "
                         f"ONDAS_MAX={ONDAS_MAX}")
    n = max(2, n)
    d = float(paso)
    col_fuente = color_cono if color_fuente is None else color_fuente

    # k = n es la onda mas vieja (radio mayor); k = 1 la recien emitida.
    ondas = VGroup()
    for k in range(n, 0, -1):
        radio = k * d
        centro = np.array([-m * k * d, 0.0, 0.0])
        aro = Circle(radius=radio, color=color, stroke_width=grosor)
        aro.move_to(centro)
        # Las viejas se ven mas tenues: dan profundidad temporal sin robarle
        # contraste al frente reciente, que es el que define el cono.
        aro.set_stroke(opacity=float(np.clip(0.30 + 0.55 * (1 - k / n), 0.25,
                                             0.9)))
        ondas.add(aro)

    # Envolvente: desde la fuente hacia atras, a +-mu de la direccion de
    # marcha. La longitud es la distancia exacta al punto de tangencia con la
    # onda mas vieja, n*d*sqrt(M^2-1), para que el cono acabe justo ahi.
    # Longitud minima no nula: una Line de longitud cero rompe el calculo de
    # su direccion en manim, asi que las lineas invisibles siguen siendo
    # segmentos de verdad — solo que a opacidad cero.
    largo = max(n * d * np.sqrt(max(m ** 2 - 1.0, 0.0)), 0.02)
    mu = np.deg2rad(angulo_mach(m))
    dx, dy = -np.cos(mu) * largo, np.sin(mu) * largo
    cono = VGroup(
        Line(ORIGIN, (dx, dy, 0), stroke_width=2.6, color=color_cono),
        Line(ORIGIN, (dx, -dy, 0), stroke_width=2.6, color=color_cono))
    cono.set_stroke(opacity=1.0 if m > 1.0 else 0.0)

    # Estela: por donde ha venido la fuente. Marca la direccion de marcha, que
    # de otro modo solo se adivina por la asimetria de los aros.
    estela = DashedLine((-max(m, 0.02) * n * d, 0, 0), ORIGIN,
                        stroke_width=1.4, color=COLOR_EJE, dash_length=0.09)
    estela.set_stroke(opacity=0.0 if m <= _EPS else 0.7)

    punto = Dot(ORIGIN, radius=0.075, color=col_fuente)

    params = {"n_ondas": n, "paso": d, "color": color,
              "color_cono": color_cono, "color_fuente": color_fuente,
              "grosor": grosor}
    return FrentesMoviles(ondas, cono, punto, estela, m, params)
