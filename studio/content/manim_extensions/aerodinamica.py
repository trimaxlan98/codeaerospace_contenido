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
    razon_temperatura       T0/T = 1 + (gamma-1)/2 M^2
    fraccion_cinetica       que parte de la entalpia total es V^2/2
    razon_presion           p0/p = (1 + (gamma-1)/2 M^2)^3.5
    razon_area              A/A*, la cuarta columna de la tabla
    criticas                T*/T0, p*/p0, rho*/rho0 y a*/a0 (numeros fijos)

Piezas (leccion 1.1):
    curva_compresibilidad   el error del modelo incompresible frente a M
    balanza_energias        movimiento contra agitacion termica, en reparto
    banda_regimenes         la regla de los cuatro regimenes de vuelo
    frentes_moviles         las ondas que emite una fuente en movimiento

Piezas (leccion 1.2, termodinamica):
    piston_gas              p V = m R T con un embolo y sus particulas
    barras_calores          cp = cv + R como una suma de dos trozos
    volumen_control         la caja imaginaria y lo que cruza sus paredes
    diagrama_ts             el plano T-s: donde se ve la entropia

Piezas (leccion 1.3, la velocidad del sonido):
    pulso_conducto          un escalon de presion recorriendo un tubo
    curva_sonido            a frente a la temperatura
    perfil_isa              a frente a la altitud, con su tropopausa
    curva_mu                como se cierra el cono al subir de Mach

Piezas (leccion 1.4, conservacion):
    conducto                tubo de area variable (recto/conv/div/De Laval)
    barras_entalpia         h + V^2/2 = h0: una barra de altura fija

Piezas (leccion 1.5, estancamiento):
    remanso                 la corriente que se para contra un cuerpo romo
    curvas_isentropicas     T/T0, rho/rho0 y p/p0 cayendo con el Mach
    tabla_isentropica       la tabla de NACA 1135, generada y no transcrita

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

from manim import (AnimationGroup, Arrow, Circle, DashedLine, DashedVMobject,
                   Dot, Line, Rectangle, Text, Transform, VGroup, VMobject,
                   DOWN, LEFT, ORIGIN, RIGHT, UP, UR)

from code_brand import (CODE_BG, CODE_MUTED, FUENTE_DISPLAY,
                        FUENTE_HUD, registrar_fuentes)

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


def _escalador(origen, rango_x, rango_y, ancho, alto):
    """Traductor de coordenadas de DATO a coordenadas de escena.

    Se usa DURANTE la construccion, cuando la pieza aun no existe como
    mobject y por tanto no puede preguntarse por su propio centro. Una vez
    construida, la pieza usa `_Cartesiano._en`, que ademas suma el
    desplazamiento acumulado.
    """
    o = np.asarray(origen, dtype=np.float64)
    x0, x1 = float(rango_x[0]), float(rango_x[1])
    y0, y1 = float(rango_y[0]), float(rango_y[1])

    def en(x, y):
        fx = (np.asarray(x, dtype=np.float64) - x0) / max(x1 - x0, _EPS)
        fy = (np.asarray(y, dtype=np.float64) - y0) / max(y1 - y0, _EPS)
        fx = np.clip(fx, 0.0, 1.0)
        fy = np.clip(fy, 0.0, 1.0)
        if np.ndim(fx) == 0 and np.ndim(fy) == 0:
            return o + np.array([fx * ancho, fy * alto, 0.0])
        fx, fy = np.broadcast_arrays(fx, fy)
        return o + np.column_stack([fx * ancho, fy * alto, np.zeros(fx.size)])

    return en


class _Cartesiano(VGroup):
    """Base de las piezas con ejes: recuerda la caja de datos y traduce.

    Las subclases llaman a `_calibrar` DESPUES de haber añadido todos sus
    submobjects — ahi se congela el centro, y de la diferencia con el centro
    actual salen los localizadores validos tras un `move_to`.
    """

    def _calibrar(self, rango_x, rango_y, ancho, alto, origen):
        self._rx = (float(rango_x[0]), float(rango_x[1]))
        self._ry = (float(rango_y[0]), float(rango_y[1]))
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        self._centro_original = self.get_center()

    def _en(self, x, y):
        """Punto de escena del dato (x, y), recortado a la caja."""
        fx = float(np.clip((float(x) - self._rx[0])
                           / max(self._rx[1] - self._rx[0], _EPS), 0.0, 1.0))
        fy = float(np.clip((float(y) - self._ry[0])
                           / max(self._ry[1] - self._ry[0], _EPS), 0.0, 1.0))
        return (self._origen
                + np.array([fx * self._ancho, fy * self._alto, 0.0])
                + (self.get_center() - self._centro_original))


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
class CurvaCompresibilidad(_Cartesiano):
    """Cuanto miente la densidad constante, y hasta donde se le perdona."""

    def __init__(self, ejes, curva, banda, umbral, etiquetas, rango_m,
                 rango_err, ancho, alto, origen, **kwargs):
        super().__init__(ejes, banda, umbral, curva, etiquetas, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.banda = banda
        self.umbral = umbral
        self.etiquetas = etiquetas
        self._calibrar(rango_m, rango_err, ancho, alto, origen)

    def error(self, mach):
        """El valor que el clip rotula, en fraccion. Misma fuente que el trazo."""
        return float(error_incompresible(mach))

    def punto_de(self, mach):
        """Punto de escena sobre la curva a ese Mach."""
        return self._en(mach, self.error(mach))


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


# --- 1.2.1 el gas ideal: p V = m R T -----------------------------------
class PistonGas(VGroup):
    """Cilindro con embolo: la mitad de volumen es el doble de presion.

    Las particulas no son azar decorativo — sus posiciones relativas se fijan
    una sola vez y despues se ESCALAN con el volumen, asi que al comprimir se
    ve a las MISMAS particulas juntarse. Con posiciones nuevas cada vez, la
    lectura seria "otro gas" en lugar de "el mismo gas apretado".
    """

    def __init__(self, cilindro, particulas, embolo, barra, rotulo, fraccion,
                 unidades, geom, **kwargs):
        super().__init__(cilindro, particulas, embolo, barra, rotulo,
                         **kwargs)
        self.cilindro = cilindro
        self.particulas = particulas
        self.embolo = embolo
        self.barra = barra
        self.rotulo = rotulo
        self.fraccion = float(fraccion)
        self._u = unidades           # posiciones relativas, en [0,1]x[0,1]
        self._g = geom               # dict con izq, largo, alto, colores...
        # Ancla para las piezas que se reconstruyen: el CILINDRO, que ni se
        # mueve ni cambia de tamaño dentro del grupo. No sirve el centro del
        # grupo (crece y encoge con la barra de presion) ni las coordenadas
        # de construccion (tras un `move_to` del grupo, las piezas nuevas
        # apareceran donde el grupo estaba, no donde esta).
        self._ancla = cilindro.get_center().copy()

    def presion_rel(self):
        """Presion relativa a la del estado inicial (isotermo: p ~ 1/V)."""
        return 1.0 / max(self.fraccion, _EPS)

    def _piezas_para(self, fraccion):
        g = self._g
        d = self.cilindro.get_center() - self._ancla
        f = float(np.clip(fraccion, 0.08, 1.0))
        x_embolo = g["izq"] + f * g["largo"]

        puntos = VGroup(*[
            Dot(d + np.array([g["izq"] + ux * f * g["largo"],
                              g["abajo"] + uy * g["alto"], 0.0]),
                radius=0.036, color=g["color_gas"]).set_opacity(0.85)
            for ux, uy in self._u])

        embolo = Line(d + np.array([x_embolo, g["abajo"] - 0.06, 0]),
                      d + np.array([x_embolo, g["abajo"] + g["alto"] + 0.06,
                                    0]),
                      stroke_width=6.0, color=g["color_embolo"])

        p = 1.0 / f
        h = min(p / g["p_max"], 1.0) * g["alto"]
        barra = Rectangle(width=g["ancho_barra"], height=max(h, 0.03),
                          stroke_width=0, fill_color=g["color_presion"],
                          fill_opacity=0.85)
        barra.move_to(d + np.array([g["x_barra"], g["abajo"] + h / 2, 0]))

        rotulo = _texto_hud(f"p x{p:.1f}", font_size=g["font_size"],
                            color=g["color_presion"])
        rotulo.move_to(d + np.array([g["x_barra"], g["abajo"] - 0.30, 0]))
        return puntos, embolo, barra, rotulo

    def a_fraccion(self, fraccion):
        """Animacion unica: embolo, gas, barra y cifra se mueven a la vez.

        Van juntas a proposito: separadas, durante medio segundo el numero
        dice una presion que el dibujo todavia no tiene.
        """
        puntos, embolo, barra, rotulo = self._piezas_para(fraccion)
        self.fraccion = float(np.clip(fraccion, 0.08, 1.0))
        return AnimationGroup(Transform(self.particulas, puntos),
                              Transform(self.embolo, embolo),
                              Transform(self.barra, barra),
                              Transform(self.rotulo, rotulo))


def piston_gas(fraccion=1.0, n_particulas=44, largo=3.6, alto=2.0,
               p_max=3.2, semilla=17, color_gas=COLOR_CALCULO,
               color_embolo=COLOR_EJE, color_presion=COLOR_TRANSONICO,
               font_size=15):
    """Cilindro de gas con embolo movil y su barra de presion.

    A temperatura constante, apretar el gas a la mitad de volumen dobla su
    presion: es `p V = m R T` puesta a la vista. `p_max` acota la barra para
    que una compresion fuerte no se salga del encuadre.
    """
    n = int(n_particulas)
    if n > MUESTRAS_MAX:
        raise ValueError(f"piston_gas: n_particulas={n} supera "
                         f"MUESTRAS_MAX={MUESTRAS_MAX}")
    rng = np.random.default_rng(int(semilla))
    # Margenes para que ninguna particula nazca pegada a la pared.
    u = np.column_stack([rng.uniform(0.04, 0.96, n),
                         rng.uniform(0.06, 0.94, n)])

    izq, abajo = -largo / 2, -alto / 2
    ancho_barra = 0.34
    x_barra = izq + largo + 0.72

    cilindro = Rectangle(width=largo, height=alto, stroke_width=2.0,
                         color=COLOR_EJE)
    cilindro.move_to((izq + largo / 2, abajo + alto / 2, 0))
    riel = Line((x_barra - ancho_barra / 2 - 0.16, abajo, 0),
                (x_barra + ancho_barra / 2 + 0.16, abajo, 0),
                stroke_width=1.6, color=COLOR_EJE)

    geom = {"izq": izq, "abajo": abajo, "largo": largo, "alto": alto,
            "p_max": float(p_max), "ancho_barra": ancho_barra,
            "x_barra": x_barra, "color_gas": color_gas,
            "color_embolo": color_embolo, "color_presion": color_presion,
            "font_size": font_size}

    pistola = PistonGas(cilindro, VGroup(), Line(), Rectangle(), VGroup(),
                        fraccion, u, geom)
    puntos, embolo, barra, rotulo = pistola._piezas_para(fraccion)
    # Se reconstruye el grupo con las piezas de verdad: el constructor recibe
    # placeholders porque `_piezas_para` necesita la geometria ya guardada.
    pistola.remove(*pistola.submobjects)
    pistola.particulas, pistola.embolo = puntos, embolo
    pistola.barra, pistola.rotulo = barra, rotulo
    pistola.add(cilindro, riel, puntos, embolo, barra, rotulo)
    return pistola


# --- 1.2.2 calores especificos: cp = cv + R ----------------------------
class BarrasCalores(VGroup):
    """cp = cv + R dibujado como lo que es: una suma de dos trozos."""

    def __init__(self, barras, etiquetas, valores, **kwargs):
        super().__init__(barras, etiquetas, **kwargs)
        self.barras = barras
        self.etiquetas = etiquetas
        self._v = dict(valores)

    def valor(self, nombre):
        """cv, R, cp en J/(kg K), o gamma adimensional. La cifra que rotula
        el clip sale de aqui, no de la memoria de nadie."""
        if nombre not in self._v:
            raise KeyError(f"barras_calores: no hay '{nombre}' "
                           f"({', '.join(self._v)})")
        return self._v[nombre]

    def barra(self, i):
        """0 = cv, 1 = R, 2 = cp (la fila de abajo, que suma las dos)."""
        return self.barras[i % len(self.barras)]


def barras_calores(ancho=6.4, alto=0.46, separacion=0.62, font_size=16,
                   color_cv=COLOR_CALCULO, color_r=COLOR_SUBSONICO,
                   color_cp=COLOR_TRANSONICO):
    """Dos filas: arriba cv y R pegados, abajo cp con la misma longitud total.

    Las longitudes son PROPORCIONALES a los valores reales del aire
    (cv = 717.6, R = 287.1, cp = 1004.7 J/kg K), asi que la fila de arriba y
    la de abajo miden lo mismo porque los numeros lo dicen, no porque se haya
    dibujado asi. De ahi sale gamma = cp/cv = 1.4 sin postularlo.
    """
    cv = R_AIRE / (GAMMA - 1)
    cp = GAMMA * R_AIRE / (GAMMA - 1)
    escala = ancho / cp
    x0 = -ancho / 2
    y_sup = separacion / 2
    y_inf = -separacion / 2

    def _tramo(x_ini, valor, color, y):
        largo = valor * escala
        caja = Rectangle(width=largo, height=alto, stroke_width=0,
                         fill_color=color, fill_opacity=0.85)
        caja.move_to((x_ini + largo / 2, y, 0))
        return caja, x_ini + largo

    caja_cv, x_medio = _tramo(x0, cv, color_cv, y_sup)
    caja_r, _ = _tramo(x_medio, R_AIRE, color_r, y_sup)
    caja_cp, _ = _tramo(x0, cp, color_cp, y_inf)
    barras = VGroup(caja_cv, caja_r, caja_cp)

    etiquetas = VGroup()
    # Los rotulos van SIEMPRE fuera de su tramo: dentro, un texto del mismo
    # color que el relleno se pierde (cian sobre cian no se lee), y pintarlo
    # del color del fondo lo ataria a un tema concreto. Fuera, cada uno cae
    # sobre negro y se lee igual de bien.
    for caja, texto, color, lado in ((caja_cv, f"cv = {cv:.0f}", color_cv, UP),
                                     (caja_r, f"R = {R_AIRE:.0f}", color_r,
                                      UP),
                                     (caja_cp, f"cp = {cp:.0f}", color_cp,
                                      DOWN)):
        tag = _texto_hud(texto, font_size=font_size, color=color)
        tag.next_to(caja, lado, buff=0.12)
        etiquetas.add(tag)

    valores = {"cv": float(cv), "R": float(R_AIRE), "cp": float(cp),
               "gamma": float(GAMMA)}
    return BarrasCalores(barras, etiquetas, valores)


# --- 1.2.3 / 1.4 el volumen de control ---------------------------------
class VolumenControl(VGroup):
    """La caja imaginaria: lo que entra, lo que sale y lo que cruza la pared."""

    def __init__(self, superficie, entrada, salida, calor, trabajo, geom,
                 **kwargs):
        super().__init__(superficie, entrada, salida, **kwargs)
        self.superficie = superficie
        self.entrada = entrada
        self.salida = salida
        self.calor = calor
        self.trabajo = trabajo
        self._g = geom
        for extra in (calor, trabajo):
            if len(extra):
                self.add(extra)

    def punto_entrada(self):
        """Donde el flujo cruza la cara de entrada (para colgar rotulos)."""
        return self.superficie.get_left() + np.array([0.0, 0.0, 0.0])

    def punto_salida(self):
        return self.superficie.get_right() + np.array([0.0, 0.0, 0.0])

    def dentro(self, dx=0.0, dy=0.0):
        """Punto interior de la caja, en unidades de escena desde su centro."""
        return self.superficie.get_center() + np.array([dx, dy, 0.0])


def volumen_control(ancho=3.6, alto=2.2, etiquetas=("1", "2"),
                    con_calor=True, con_trabajo=True, font_size=17,
                    color=COLOR_EJE, color_flujo=COLOR_TRANSONICO,
                    color_calor=COLOR_SUPERSONICO,
                    color_trabajo=COLOR_SUBSONICO):
    """Superficie de control punteada con sus flujos de entrada y salida.

    La superficie va PUNTEADA y los flujos en linea continua a proposito: la
    caja es una eleccion del ingeniero (no existe en el aire), y lo que si
    existe es lo que la cruza.
    """
    caja = Rectangle(width=ancho, height=alto, stroke_width=2.0, color=color)
    superficie = DashedVMobject(caja, num_dashes=44)

    largo = 1.0
    entrada = VGroup(Arrow(start=(-ancho / 2 - largo, 0, 0),
                           end=(-ancho / 2 + 0.06, 0, 0), buff=0,
                           stroke_width=3.4, color=color_flujo,
                           max_tip_length_to_length_ratio=0.18))
    salida = VGroup(Arrow(start=(ancho / 2 - 0.06, 0, 0),
                          end=(ancho / 2 + largo, 0, 0), buff=0,
                          stroke_width=3.4, color=color_flujo,
                          max_tip_length_to_length_ratio=0.18))
    for grupo, texto, lado in ((entrada, etiquetas[0], UP),
                               (salida, etiquetas[1], UP)):
        tag = _texto_hud(texto, font_size=font_size, color=color_flujo)
        tag.next_to(grupo[0], lado, buff=0.12)
        grupo.add(tag)

    calor = VGroup()
    if con_calor:
        flecha = Arrow(start=(-ancho / 4, -alto / 2 - 0.85, 0),
                       end=(-ancho / 4, -alto / 2 + 0.06, 0), buff=0,
                       stroke_width=3.0, color=color_calor,
                       max_tip_length_to_length_ratio=0.22)
        tag = _texto_hud("Q", font_size=font_size, color=color_calor)
        tag.next_to(flecha, DOWN, buff=0.10)
        calor.add(flecha, tag)

    trabajo = VGroup()
    if con_trabajo:
        flecha = Arrow(start=(ancho / 4, alto / 2 - 0.06, 0),
                       end=(ancho / 4, alto / 2 + 0.85, 0), buff=0,
                       stroke_width=3.0, color=color_trabajo,
                       max_tip_length_to_length_ratio=0.22)
        tag = _texto_hud("W", font_size=font_size, color=color_trabajo)
        tag.next_to(flecha, UP, buff=0.10)
        trabajo.add(flecha, tag)

    geom = {"ancho": float(ancho), "alto": float(alto)}
    return VolumenControl(superficie, entrada, salida, calor, trabajo, geom)


# --- 1.2.4 la segunda ley: el plano T-s --------------------------------
class DiagramaTS(_Cartesiano):
    """El plano donde se ve lo que la primera ley no distingue: la entropia.

    Las coordenadas son RELATIVAS (0-1 en cada eje) y los ejes van sin
    numeros. Es deliberado: en este punto del curso la entropia se lee como
    direccion (a la derecha, nunca a la izquierda), no como cifra.
    """

    def __init__(self, ejes, ancho, alto, origen, **kwargs):
        super().__init__(ejes, **kwargs)
        self.ejes = ejes
        self._calibrar((0.0, 1.0), (0.0, 1.0), ancho, alto, origen)

    def punto_de(self, s, t):
        """Punto de escena de un estado (s, T) en coordenadas relativas."""
        return self._en(s, t)

    def estado(self, s, t, etiqueta=None, color=COLOR_TRANSONICO,
               font_size=16, direccion=None):
        """Punto marcado, con su etiqueta si se pide."""
        punto = Dot(self.punto_de(s, t), radius=0.068, color=color)
        if etiqueta is None:
            return VGroup(punto)
        tag = _texto_hud(etiqueta, font_size=font_size, color=color)
        tag.next_to(punto, UP if direccion is None else direccion, buff=0.12)
        return VGroup(punto, tag)

    def trayecto(self, estados, color=COLOR_TRANSONICO, grosor=2.8,
                 punteado=False):
        """Camino por una lista de estados (s, T) relativos."""
        pts = np.array([self.punto_de(s, t) for s, t in estados])
        if len(pts) < 2:
            raise ValueError("diagrama_ts: un trayecto necesita 2 estados")
        linea = VMobject(color=color, stroke_width=grosor)
        linea.set_points_as_corners(pts) if len(pts) == 2 else \
            linea.set_points_smoothly(pts)
        return DashedVMobject(linea, num_dashes=26) if punteado else linea


def diagrama_ts(ancho=5.2, alto=3.0, color_ejes=COLOR_EJE, font_size=15):
    """Ejes (entropia s ->, temperatura T ^) sin numeros, para leer procesos."""
    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    tag_x = _texto_hud("ENTROPIA  s", font_size=font_size)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_hud("T", font_size=font_size + 3)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)
    return DiagramaTS(ejes, ancho, alto, origen)


# --- 1.3.1 la perturbacion infinitesimal -------------------------------
class PulsoConducto(VGroup):
    """Un escalon de presion recorriendo un tubo: eso es el sonido.

    La zona ya alcanzada por el pulso queda teñida y el trazo de presion de
    arriba sube un escalon: el aire de detras "ya se ha enterado", el de
    delante no. La velocidad del frente es, por definicion, a.
    """

    def __init__(self, tubo, tenido, frente, traza, geom, avance, **kwargs):
        super().__init__(tubo, tenido, traza, frente, **kwargs)
        self.tubo = tubo
        self.tenido = tenido
        self.frente = frente
        self.traza = traza
        self.rotulo = VGroup()   # lo rellena `pulso_conducto` al construir
        self._g = geom
        self.avance = float(avance)
        # Ancla de las piezas que se reconstruyen: el TUBO, que no cambia
        # nunca. Ver la nota de PistonGas — sin esto, tras un `move_to` del
        # grupo el frente reaparece donde el tubo estaba antes.
        self._ancla = tubo.get_center().copy()

    def _desfase(self):
        return self.tubo.get_center() - self._ancla

    def x_frente(self, avance=None):
        """x de escena del frente para ese avance (0-1)."""
        g = self._g
        a = self.avance if avance is None else float(avance)
        return (g["izq"] + float(np.clip(a, 0.0, 1.0)) * g["largo"]
                + self._desfase()[0])

    def _piezas_para(self, avance):
        g = self._g
        d = self._desfase()
        a = float(np.clip(avance, 0.0, 1.0))
        x = g["izq"] + a * g["largo"]

        tenido = Rectangle(width=max(x - g["izq"], 0.02), height=g["alto"],
                           stroke_width=0, fill_color=g["color_pulso"],
                           fill_opacity=0.22)
        tenido.move_to(d + np.array([(g["izq"] + x) / 2, g["y"], 0]))

        frente = Line(d + np.array([x, g["y"] - g["alto"] / 2, 0]),
                      d + np.array([x, g["y"] + g["alto"] / 2, 0]),
                      stroke_width=3.0, color=g["color_pulso"])

        # Trazo de presion: escalon alto detras del frente, base delante.
        y_base = g["y_traza"]
        y_alto = y_base + g["salto"]
        traza = VMobject(color=g["color_pulso"], stroke_width=2.4)
        traza.set_points_as_corners([
            d + np.array([g["izq"], y_alto, 0]),
            d + np.array([x, y_alto, 0]),
            d + np.array([x, y_base, 0]),
            d + np.array([g["izq"] + g["largo"], y_base, 0])])
        return tenido, frente, traza

    def a_avance(self, avance):
        """Animacion unica: teñido, frente y trazo van SIEMPRE juntos."""
        tenido, frente, traza = self._piezas_para(avance)
        self.avance = float(np.clip(avance, 0.0, 1.0))
        return AnimationGroup(Transform(self.tenido, tenido),
                              Transform(self.frente, frente),
                              Transform(self.traza, traza))


def pulso_conducto(avance=0.15, largo=6.2, alto=1.1, salto=0.42,
                   color_pulso=COLOR_CALCULO, color_tubo=COLOR_EJE,
                   font_size=14):
    """Tubo horizontal con un frente de presion que lo recorre, y su trazo.

    El escalon es pequeño a proposito (`salto` es un delta, no una montaña):
    la deduccion de a = sqrt(gamma R T) vale para una perturbacion
    INFINITESIMAL, y un dibujo con una ola gigante contaria otra cosa (esa
    seria una onda de choque, que llega en el modulo 2).
    """
    izq = -largo / 2
    y = -0.55
    tubo = Rectangle(width=largo, height=alto, stroke_width=2.0,
                     color=color_tubo)
    tubo.move_to((0, y, 0))

    geom = {"izq": izq, "largo": float(largo), "alto": float(alto), "y": y,
            "y_traza": y + alto / 2 + 0.45, "salto": float(salto),
            "color_pulso": color_pulso}

    pulso = PulsoConducto(tubo, Rectangle(), Line(), VMobject(), geom, avance)
    tenido, frente, traza = pulso._piezas_para(avance)
    pulso.remove(*pulso.submobjects)
    pulso.tenido, pulso.frente, pulso.traza = tenido, frente, traza
    # El rotulo comparte color con el tubo: los dos son mobiliario, y quien
    # aclare el tubo para que se vea la zona aun sin perturbar quiere que el
    # rotulo se aclare con el.
    tag = _texto_hud("PRESION", font_size=font_size, color=color_tubo)
    tag.next_to((izq, geom["y_traza"] + salto, 0), UP, buff=0.10)
    # Se expone como `.rotulo` y no solo dentro del grupo: los clips encienden
    # las piezas una a una (`FadeIn(pulso.tubo)`, `FadeIn(pulso.traza)`...) y
    # una pieza sin nombre propio no llega nunca a la escena.
    pulso.rotulo = tag
    pulso.add(tubo, tenido, traza, frente, tag)
    return pulso


# --- 1.3.2 a = sqrt(gamma R T) -----------------------------------------
class CurvaSonido(_Cartesiano):
    """La velocidad del sonido solo depende de la temperatura."""

    def __init__(self, ejes, curva, rango_t, rango_a, ancho, alto, origen,
                 **kwargs):
        super().__init__(ejes, curva, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self._calibrar(rango_t, rango_a, ancho, alto, origen)

    def a(self, t_kelvin):
        """m/s a esa temperatura. Misma fuente que el trazo."""
        return float(velocidad_sonido(t_kelvin))

    def punto_de(self, t_kelvin):
        return self._en(t_kelvin, self.a(t_kelvin))


def curva_sonido(t_rango=(200.0, 320.0), ancho=5.4, alto=2.6,
                 color=COLOR_CALCULO, color_ejes=COLOR_EJE, font_size=14,
                 muestras=120):
    """Ejes (temperatura K ->, velocidad del sonido m/s ^) con a = sqrt(gRT).

    El rango arranca en 200 K y no en 0: entre 0 y 200 K no vuela nadie, y
    empezar en cero aplastaria en un rincon justo el tramo que importa (la
    troposfera va de 288 a 217 K).
    """
    muestras = _validar_muestras("curva_sonido", muestras)
    t0, t1 = float(t_rango[0]), float(t_rango[1])
    ts = np.linspace(t0, t1, muestras)
    aes = np.asarray(velocidad_sonido(ts), dtype=np.float64)
    a0, a1 = float(aes.min()) - 6.0, float(aes.max()) + 6.0

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (t0, t1), (a0, a1), ancho, alto)
    curva = _curva(en(ts, aes), color, grosor=3.0)

    tag_x = _texto_hud("TEMPERATURA  K", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_hud("a   m/s", font_size=font_size)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaSonido(ejes, curva, (t0, t1), (a0, a1), ancho, alto, origen)


# --- 1.3.3 la atmosfera estandar ---------------------------------------
class PerfilISA(_Cartesiano):
    """Como cae la velocidad del sonido al subir, y donde deja de caer."""

    def __init__(self, ejes, curva, tropopausa, rango_a, rango_h, ancho, alto,
                 origen, **kwargs):
        super().__init__(ejes, tropopausa, curva, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.tropopausa = tropopausa
        self._calibrar(rango_a, rango_h, ancho, alto, origen)

    def a(self, altitud_m):
        """m/s a esa altitud (ISA). La cifra que rotula el clip."""
        return isa(altitud_m)[3]

    def temperatura(self, altitud_m):
        return isa(altitud_m)[0]

    def punto_de(self, altitud_m):
        """Punto sobre el perfil a esa altitud (eje vertical = altitud)."""
        return self._en(self.a(altitud_m), float(altitud_m))


def perfil_isa(h_max=20000.0, ancho=4.6, alto=3.0, color=COLOR_CALCULO,
               color_ejes=COLOR_EJE, color_tropopausa=COLOR_SUBSONICO,
               font_size=14, muestras=140):
    """Perfil de la velocidad del sonido con la altitud (altitud en vertical).

    La altitud va en el eje VERTICAL aunque sea la variable independiente:
    es un perfil atmosferico, y dibujarlo tumbado obliga al espectador a
    girar la cabeza para leer "arriba hace mas frio". La linea verde marca la
    tropopausa, donde la temperatura deja de caer y el sonido se estanca.
    """
    muestras = _validar_muestras("perfil_isa", muestras)
    hs = np.linspace(0.0, float(h_max), muestras)
    aes = np.array([isa(float(h))[3] for h in hs])
    a0, a1 = float(aes.min()) - 4.0, float(aes.max()) + 4.0

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (a0, a1), (0.0, float(h_max)), ancho, alto)
    curva = _curva(en(aes, hs), color, grosor=3.0)

    y_trop = en(a0, H_TROPOPAUSA)[1]
    tropopausa = VGroup(
        DashedLine((origen[0], y_trop, 0), (origen[0] + ancho, y_trop, 0),
                   stroke_width=1.5, color=color_tropopausa, dash_length=0.08))
    tag = _texto_hud("TROPOPAUSA  11 km", font_size=font_size - 2,
                     color=color_tropopausa)
    tag.next_to(tropopausa[0].get_end(), UP, buff=0.08).shift(LEFT * 0.30)
    tropopausa.add(tag)

    tag_x = _texto_hud("a   m/s", font_size=font_size)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_hud("ALTITUD", font_size=font_size - 1)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return PerfilISA(ejes, curva, tropopausa, (a0, a1), (0.0, float(h_max)),
                     ancho, alto, origen)


# --- 1.3.4 el angulo del cono ------------------------------------------
class CurvaMu(_Cartesiano):
    """Como se cierra el cono de Mach al subir la velocidad."""

    def __init__(self, ejes, curva, rango_m, rango_mu, ancho, alto, origen,
                 **kwargs):
        super().__init__(ejes, curva, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self._calibrar(rango_m, rango_mu, ancho, alto, origen)

    def mu(self, mach):
        """Semiangulo en grados. Misma fuente que el trazo."""
        return angulo_mach(mach)

    def punto_de(self, mach):
        return self._en(mach, self.mu(mach))


def curva_mu(m_rango=(1.0, 6.0), ancho=5.0, alto=2.6, color=COLOR_SUPERSONICO,
             color_ejes=COLOR_EJE, font_size=14, muestras=140):
    """Ejes (Mach ->, mu grados ^) con mu = arcsen(1/M), de M = 1 a M = 6."""
    muestras = _validar_muestras("curva_mu", muestras)
    m0, m1 = float(m_rango[0]), float(m_rango[1])
    if m0 < 1.0:
        raise ValueError("curva_mu: por debajo de M = 1 no hay cono")
    ms = np.linspace(m0, m1, muestras)
    mus = np.array([angulo_mach(float(m)) for m in ms])

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (m0, m1), (0.0, 90.0), ancho, alto)
    curva = _curva(en(ms, mus), color, grosor=3.0)

    tag_x = _texto_hud("MACH", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_hud("mu   grados", font_size=font_size)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaMu(ejes, curva, (m0, m1), (0.0, 90.0), ancho, alto, origen)


# --- 1.4 el conducto de area variable ----------------------------------
_PERFILES = {
    "recto": lambda x, ag: np.ones_like(x),
    "convergente": lambda x, ag: 1.0 - (1.0 - ag) * x,
    "divergente": lambda x, ag: ag + (1.0 - ag) * x,
    # De Laval: parabola con el minimo exacto en x = 0.5 y area 1 en los dos
    # extremos, para que la garganta sea inequivoca sin ajustar nada a ojo.
    "delaval": lambda x, ag: ag + (1.0 - ag) * (2.0 * x - 1.0) ** 2,
}


class Conducto(VGroup):
    """Tubo de area variable: la geometria sobre la que se escribe el modulo 2.

    El area se maneja NORMALIZADA (1.0 = area de referencia del perfil) y el
    dibujo la reparte simetricamente arriba y abajo del eje, que es como se
    dibuja un conducto cuasi-unidimensional: lo unico que importa es A(x).
    """

    def __init__(self, paredes, eje, perfil, area_garganta, largo, alto,
                 izq, y, **kwargs):
        super().__init__(eje, paredes, **kwargs)
        self.paredes = paredes
        self.eje = eje
        self._perfil = perfil
        self._ag = float(area_garganta)
        self._largo = float(largo)
        self._alto = float(alto)
        self._izq = float(izq)
        self._y = float(y)
        self._centro_original = self.get_center()

    def area(self, x):
        """Area normalizada en la estacion x (0 = entrada, 1 = salida)."""
        f = float(np.clip(x, 0.0, 1.0))
        return float(_PERFILES[self._perfil](np.array([f]), self._ag)[0])

    def punto_de(self, x, y_rel=0.0):
        """Punto del conducto en la estacion x. `y_rel` va de -1 (pared de
        abajo) a +1 (pared de arriba); 0 es el eje."""
        f = float(np.clip(x, 0.0, 1.0))
        media = self.area(f) * self._alto / 2
        desplazamiento = self.get_center() - self._centro_original
        return (np.array([self._izq + f * self._largo,
                          self._y + float(np.clip(y_rel, -1.0, 1.0)) * media,
                          0.0]) + desplazamiento)

    def garganta(self):
        """Punto del eje en la seccion de area minima."""
        xs = np.linspace(0.0, 1.0, 201)
        areas = _PERFILES[self._perfil](xs, self._ag)
        return self.punto_de(float(xs[int(np.argmin(areas))]))


def conducto(perfil="delaval", area_garganta=0.42, largo=6.0, alto=2.2,
             y=0.0, color=COLOR_EJE, muestras=120, grosor=2.6):
    """Paredes de un conducto de area variable, con su eje punteado.

    `perfil` es 'recto', 'convergente', 'divergente' o 'delaval'.
    `area_garganta` es el area minima relativa a la de referencia.
    """
    if perfil not in _PERFILES:
        raise ValueError(f"conducto: perfil '{perfil}' desconocido "
                         f"({', '.join(sorted(_PERFILES))})")
    muestras = _validar_muestras("conducto", muestras)
    ag = float(np.clip(area_garganta, 0.06, 1.0))
    izq = -largo / 2

    xs = np.linspace(0.0, 1.0, muestras)
    areas = _PERFILES[perfil](xs, ag)
    x_esc = izq + xs * largo
    media = areas * alto / 2

    arriba = _curva(np.column_stack([x_esc, y + media, np.zeros_like(xs)]),
                    color, grosor)
    abajo = _curva(np.column_stack([x_esc, y - media, np.zeros_like(xs)]),
                   color, grosor)
    eje = DashedLine((izq, y, 0), (izq + largo, y, 0), stroke_width=1.2,
                     color=color, dash_length=0.10)
    eje.set_opacity(0.6)

    return Conducto(VGroup(arriba, abajo), eje, perfil, ag, largo, alto, izq,
                    y)


# --- 1.4.3 la entalpia total se conserva -------------------------------
def razon_temperatura(mach):
    """T0/T = 1 + (gamma-1)/2 M^2. El termometro del flujo compresible."""
    m = np.asarray(mach, dtype=np.float64)
    return 1 + (GAMMA - 1) / 2 * m ** 2


def fraccion_cinetica(mach):
    """Que parte de la entalpia TOTAL es energia cinetica: 1 - T/T0.

    Es la lectura de la ecuacion de la energia: h + V^2/2 = h0 constante, asi
    que acelerar el flujo es gastarse su temperatura. A M = 1 va un 17 %; a
    M = 3, un 64 %.
    """
    return 1.0 - 1.0 / razon_temperatura(mach)


class BarrasEntalpia(VGroup):
    """h + V^2/2 = h0: una barra de altura FIJA que se reparte.

    Que el total no cambie nunca es el mensaje entero del clip — por eso es
    una barra apilada y no dos barras sueltas: si la suma pudiera crecer, la
    conservacion dejaria de leerse.
    """

    def __init__(self, marco, termica, cinetica, rotulo, mach, geom, **kwargs):
        super().__init__(marco, termica, cinetica, rotulo, **kwargs)
        self.marco = marco
        self.termica = termica
        self.cinetica = cinetica
        self.rotulo = rotulo
        self.mach = float(mach)
        self._g = geom

    def fraccion(self, mach=None):
        """Fraccion cinetica al Mach actual, o al que se le pase."""
        return float(fraccion_cinetica(self.mach if mach is None else mach))

    def _piezas_para(self, mach):
        g = self._g
        f = self.fraccion(mach)
        y0 = self.marco.get_bottom()[1]
        h_term = max(g["alto"] * (1 - f), 0.02)
        h_cin = max(g["alto"] * f, 0.02)
        x = self.marco.get_center()[0]

        termica = Rectangle(width=g["ancho"], height=h_term, stroke_width=0,
                            fill_color=g["color_termica"], fill_opacity=0.85)
        termica.move_to((x, y0 + h_term / 2, 0))
        cinetica = Rectangle(width=g["ancho"], height=h_cin, stroke_width=0,
                             fill_color=g["color_cinetica"], fill_opacity=0.85)
        cinetica.move_to((x, y0 + h_term + h_cin / 2, 0))

        rotulo = _texto_hud(f"M = {float(mach):g}   {f * 100:.0f} % cinetica",
                            font_size=g["font_size"],
                            color=g["color_cinetica"])
        rotulo.move_to((x, y0 + g["alto"] + 0.34, 0))
        return termica, cinetica, rotulo

    def a_mach(self, mach):
        """Animacion unica: los dos tramos y la cifra, siempre a la vez."""
        termica, cinetica, rotulo = self._piezas_para(mach)
        self.mach = float(mach)
        return AnimationGroup(Transform(self.termica, termica),
                              Transform(self.cinetica, cinetica),
                              Transform(self.rotulo, rotulo))


def barras_entalpia(mach=0.0, alto=2.6, ancho=0.9, font_size=15,
                    color_termica=COLOR_CALCULO,
                    color_cinetica=COLOR_TRANSONICO, color_eje=COLOR_EJE):
    """Barra apilada de altura constante: entalpia estatica + energia cinetica.

    El marco dibuja el TOTAL (h0) y no se mueve nunca; lo unico que cambia es
    donde esta la frontera entre los dos tramos.
    """
    marco = Rectangle(width=ancho, height=alto, stroke_width=1.8,
                      color=color_eje)
    geom = {"alto": float(alto), "ancho": float(ancho),
            "color_termica": color_termica, "color_cinetica": color_cinetica,
            "font_size": font_size}

    barras = BarrasEntalpia(marco, Rectangle(), Rectangle(), VGroup(), mach,
                            geom)
    termica, cinetica, rotulo = barras._piezas_para(mach)
    barras.remove(*barras.submobjects)
    barras.termica, barras.cinetica, barras.rotulo = termica, cinetica, rotulo
    tag = _texto_hud("h0", font_size=font_size, color=color_eje)
    tag.next_to(marco, LEFT, buff=0.14)
    barras.add(marco, termica, cinetica, rotulo, tag)
    return barras


# --- 1.5.1 el punto de remanso -----------------------------------------
class Remanso(VGroup):
    """La corriente llega a un cuerpo romo y en la punta se para del todo.

    Las lineas se integran sobre el campo de velocidad del flujo potencial
    alrededor de un cilindro. Es el patron INCOMPRESIBLE, y aqui solo cumple
    una funcion: localizar el punto de remanso y hacer ver que la linea
    central muere en el. A Mach supersonico habria delante una onda de
    choque desprendida — eso llega en el modulo 3, y por eso el clip que usa
    esta pieza habla de la definicion de T0, no del campo real.
    """

    def __init__(self, cuerpo, lineas, radio, **kwargs):
        super().__init__(lineas, cuerpo, **kwargs)
        self.cuerpo = cuerpo
        self.lineas = lineas
        self._radio = float(radio)
        self._centro_original = self.get_center()

    def linea(self, i):
        return self.lineas[i % len(self.lineas)]

    def centro_cuerpo(self):
        """Centro actual del obstaculo."""
        return self.cuerpo.get_center()

    def punto(self):
        """El punto de remanso: el morro del cuerpo, donde muere la linea
        central. Se lee del cuerpo, asi que sigue valiendo tras un move_to."""
        return self.centro_cuerpo() + np.array([-self._radio, 0.0, 0.0])


def _corriente(y0, radio, x_ini, x_fin, ds, pasos):
    """Traza una linea de corriente sobre el campo del cilindro.

    Se avanza por LONGITUD DE ARCO y no en x: cerca del cuerpo la linea se
    pone casi vertical y un paso en x la mandaria al infinito. El campo es
    tangente a la superficie, asi que las lineas que no son la central
    rodean el cilindro por si solas; la central se para en el morro, que es
    justo lo que hay que ver.
    """
    pts = []
    x, y = float(x_ini), float(y0)
    r2_min = (radio * 1.015) ** 2
    for _ in range(int(pasos)):
        pts.append((x, y))
        r2 = x * x + y * y
        if r2 < r2_min or x > x_fin:
            break
        u = 1.0 - radio ** 2 * (x * x - y * y) / (r2 * r2)
        v = -2.0 * radio ** 2 * x * y / (r2 * r2)
        norma = float(np.hypot(u, v))
        if norma < 1e-7:
            break
        x += ds * u / norma
        y += ds * v / norma
    return pts


def remanso(radio=0.85, n_lineas=7, separacion=0.42, largo=3.4, ds=0.05,
            color=COLOR_TRANSONICO, color_cuerpo=COLOR_EJE, grosor=2.0,
            pasos=260):
    """Lineas de corriente llegando a un cuerpo romo, con su punto de remanso.

    `n_lineas` se fuerza a impar: la linea CENTRAL es la que muere en el
    punto de remanso y sin ella el dibujo pierde su unico mensaje.
    """
    n = int(n_lineas)
    if n > ONDAS_MAX * 2:
        raise ValueError(f"remanso: n_lineas={n} es demasiado para un render")
    n = max(3, n if n % 2 else n + 1)
    r = float(radio)

    lineas = VGroup()
    mitad = n // 2
    for k in range(-mitad, mitad + 1):
        y0 = k * float(separacion)
        pts = _corriente(y0, r, -largo, largo, float(ds), pasos)
        if len(pts) < 3:
            continue
        traza = _curva(np.array(pts), color, grosor)
        # La central es la protagonista: las demas la acompañan.
        traza.set_stroke(opacity=1.0 if k == 0 else 0.55)
        lineas.add(traza)

    cuerpo = Circle(radius=r, color=color_cuerpo, stroke_width=2.4)
    cuerpo.set_fill(COLOR_EJE, opacity=0.35)
    return Remanso(cuerpo, lineas, r)


# --- 1.5.2 / 1.5.3 las relaciones isentropicas -------------------------
def razon_presion(mach):
    """p0/p = (1 + (gamma-1)/2 M^2)^(gamma/(gamma-1)).

    El exponente 3.5 no es un numero suelto: sale de exigir que el frenado
    sea isentropico (p/rho^gamma constante) sobre la razon de temperaturas.
    """
    return razon_temperatura(mach) ** (GAMMA / (GAMMA - 1))


def razon_area(mach):
    """A/A* = (1/M) [ (2/(gamma+1)) (1 + (gamma-1)/2 M^2) ]^((gamma+1)/(2(gamma-1))).

    Vive ya aqui, aunque su leccion sea la 2.4, porque es la cuarta columna
    de la tabla de flujo isentropico y la tabla se presenta en la 1.5.
    """
    m = np.maximum(np.asarray(mach, dtype=np.float64), _EPS)
    base = 2 / (GAMMA + 1) * razon_temperatura(m)
    return base ** ((GAMMA + 1) / (2 * (GAMMA - 1))) / m


# Razones ESTATICA/ESTANCAMIENTO, que es como las dan las tablas: valen 1 en
# reposo y caen al subir M. (nombre, funcion M -> valor, color).
RAZONES = (("T/T0", lambda m: 1.0 / razon_temperatura(m), COLOR_CALCULO),
           ("RHO/RHO0", lambda m: 1.0 / razon_densidad(m), COLOR_SUBSONICO),
           ("p/p0", lambda m: 1.0 / razon_presion(m), COLOR_TRANSONICO))


def criticas():
    """Las condiciones criticas (M = 1) frente a las de estancamiento.

    Son numeros FIJOS para un gamma dado —0.8333, 0.6339, 0.5283 y 0.9129—
    y por eso sirven de referencia universal en todo el curso.
    """
    return {"T*/T0": float(1.0 / razon_temperatura(1.0)),
            "RHO*/RHO0": float(1.0 / razon_densidad(1.0)),
            "p*/p0": float(1.0 / razon_presion(1.0)),
            "a*/a0": float(np.sqrt(1.0 / razon_temperatura(1.0)))}


class CurvasIsentropicas(_Cartesiano):
    """Las tres razones cayendo con el Mach, cada una a su ritmo."""

    def __init__(self, ejes, curvas, etiquetas, m_max, ancho, alto, origen,
                 **kwargs):
        super().__init__(ejes, curvas, etiquetas, **kwargs)
        self.ejes = ejes
        self.curvas = curvas
        self.etiquetas = etiquetas
        self._calibrar((0.0, m_max), (0.0, 1.0), ancho, alto, origen)

    def nombre(self, i):
        return RAZONES[i % len(RAZONES)][0]

    def valor(self, i, mach):
        """La razon i a ese Mach. Misma fuente que la curva dibujada."""
        return float(RAZONES[i % len(RAZONES)][1](float(mach)))

    def color_de(self, i):
        """El color de la razon i. Se llama `color_de` y no `color` porque
        `color` ya es un atributo de todo Mobject: definirlo como metodo lo
        sombrea y el clip acaba llamando a un ManimColor."""
        return RAZONES[i % len(RAZONES)][2]

    def curva(self, i):
        return self.curvas[i % len(self.curvas)]

    def punto_de(self, i, mach):
        """Punto sobre la curva i a ese Mach."""
        return self._en(mach, self.valor(i, mach))

    def vertical_en(self, mach, color=None, grosor=1.5):
        """Linea punteada de eje a eje en ese Mach, para leer las tres a la
        vez. La construye la pieza y no el clip porque las coordenadas de la
        caja son suyas."""
        return DashedLine(self._en(mach, 0.0), self._en(mach, 1.0),
                          stroke_width=grosor,
                          color=COLOR_EJE if color is None else color,
                          dash_length=0.08)


def curvas_isentropicas(m_max=3.0, ancho=5.4, alto=2.9, color_ejes=COLOR_EJE,
                        font_size=15, muestras=160, hueco_etiquetas=0.72):
    """Ejes (Mach ->, razon 0-1 ^) con T/T0, rho/rho0 y p/p0.

    Las etiquetas van en una COLUMNA a la derecha, a alturas repartidas, y
    cada una se ata al final de su curva con una guia punteada. Colgadas del
    propio final de curva se encimarian: p/p0 y rho/rho0 solo se diferencian
    en un exponente y a Mach alto acaban a menos de un renglon la una de la
    otra.
    """
    muestras = _validar_muestras("curvas_isentropicas", muestras)
    m1 = float(m_max)
    if m1 <= 0:
        raise ValueError("curvas_isentropicas: m_max debe ser positivo")
    ms = np.linspace(0.0, m1, muestras)

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (0.0, m1), (0.0, 1.0), ancho, alto)

    curvas = VGroup()
    etiquetas = VGroup()
    x_tag = origen[0] + ancho + float(hueco_etiquetas)
    alturas = (0.86, 0.54, 0.22)   # repartidas, no las de las curvas
    for i, (nombre, funcion, color) in enumerate(RAZONES):
        ys = np.asarray([float(funcion(m)) for m in ms], dtype=np.float64)
        curvas.add(_curva(en(ms, ys), color, grosor=2.8))

        fin = en(m1, ys[-1])
        tag = _texto_hud(nombre, font_size=font_size, color=color)
        tag.move_to((x_tag + tag.width / 2, origen[1] + alturas[i] * alto, 0))
        guia = DashedLine(fin + RIGHT * 0.08, tag.get_left() + LEFT * 0.10,
                          stroke_width=1.2, color=color, dash_length=0.07)
        guia.set_stroke(opacity=0.55)
        etiquetas.add(VGroup(guia, tag))

    # Marcas de Mach en los dos extremos: sin ellas el eje no dice a que
    # velocidad esta cada cosa, y el clip habla de "a Mach 3" señalando un
    # sitio que el espectador no puede situar.
    marcas = VGroup()
    for valor in (0.0, m1):
        muesca = Line(en(valor, 0.0) + DOWN * 0.08, en(valor, 0.0),
                      stroke_width=1.6, color=color_ejes)
        num = _texto_hud(f"{valor:g}", font_size=font_size - 2,
                         color=color_ejes)
        num.next_to(muesca, DOWN, buff=0.08)
        marcas.add(muesca, num)

    tag_x = _texto_hud("MACH", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.44)
    tag_y = _texto_hud("1.0", font_size=font_size - 2)
    tag_y.next_to(ejes[1].get_end(), LEFT, buff=0.12)
    ejes.add(marcas, tag_x, tag_y)

    return CurvasIsentropicas(ejes, curvas, etiquetas, m1, ancho, alto,
                              origen)


# --- 1.5.4 la tabla de flujo isentropico -------------------------------
# Columnas de la tabla, en el orden de NACA 1135: (cabecera ASCII, funcion,
# decimales). La cabecera es ASCII a proposito — Space Mono no trae
# subindices ni griegas fiables.
COLUMNAS_ISENTROPICAS = (
    ("M", lambda m: m, 2),
    ("T/T0", lambda m: 1.0 / razon_temperatura(m), 4),
    ("p/p0", lambda m: 1.0 / razon_presion(m), 4),
    ("RHO/RHO0", lambda m: 1.0 / razon_densidad(m), 4),
    ("A/A*", lambda m: razon_area(m), 4),
)

FILAS_MAX = 8   # filas de una tabla; mas no se leen en pantalla


class TablaIsentropica(VGroup):
    """La tabla de siempre, generada — no transcrita.

    Cada celda se evalua con las mismas funciones que dibujan las curvas, asi
    que la tabla no puede discrepar de la grafica ni traer una errata de
    copia.
    """

    def __init__(self, cabecera, filas, regla, machs, **kwargs):
        super().__init__(cabecera, regla, filas, **kwargs)
        self.cabecera = cabecera
        self.filas = filas
        self.regla = regla
        self._machs = list(machs)

    def fila(self, i):
        return self.filas[i % len(self.filas)]

    def celda(self, i, j):
        return self.fila(i)[j % len(self.fila(i))]

    def columna(self, j):
        """La columna j entera, cabecera incluida (para Indicate)."""
        return VGroup(self.cabecera[j % len(self.cabecera)],
                      *[f[j % len(f)] for f in self.filas])

    def valor(self, i, j):
        """El numero de la celda (i, j), de la misma funcion que lo escribio."""
        return float(COLUMNAS_ISENTROPICAS[j % len(COLUMNAS_ISENTROPICAS)][1](
            self._machs[i % len(self._machs)]))

    def resaltar(self, i, color=COLOR_TRANSONICO, opacidad=0.16, buff=0.10):
        """Rectangulo detras de la fila i. Se devuelve sin añadir al grupo:
        el clip decide cuando entra y cuando sale."""
        objetivo = self.fila(i)
        caja = Rectangle(width=objetivo.width + 2 * buff,
                         height=objetivo.height + 2 * buff, stroke_width=0,
                         fill_color=color, fill_opacity=opacidad)
        caja.move_to(objetivo.get_center())
        return caja


def tabla_isentropica(machs=(0.5, 1.0, 1.5, 2.0, 3.0), ancho_col=1.42,
                      alto_fila=0.46, font_size=17, color=CODE_MUTED,
                      color_cabecera=COLOR_CALCULO, color_eje=COLOR_EJE):
    """Tabla de flujo isentropico: M, T/T0, p/p0, rho/rho0 y A/A*.

    Las celdas se alinean por columna con una malla de posiciones fija (y no
    con `arrange`): en Space Mono los numeros son de ancho constante, pero
    `arrange` centra cada fila por su propio ancho y bastaria una cifra de
    mas en una celda para desalinear la columna entera.
    """
    ms = [float(m) for m in machs]
    if not ms:
        raise ValueError("tabla_isentropica: hace falta al menos un Mach")
    if len(ms) > FILAS_MAX:
        raise ValueError(f"tabla_isentropica: {len(ms)} filas supera "
                         f"FILAS_MAX={FILAS_MAX}")

    n_col = len(COLUMNAS_ISENTROPICAS)
    xs = [(j - (n_col - 1) / 2) * float(ancho_col) for j in range(n_col)]
    y_cabecera = 0.0

    cabecera = VGroup()
    for j, (nombre, _f, _d) in enumerate(COLUMNAS_ISENTROPICAS):
        tag = _texto_hud(nombre, font_size=font_size - 1,
                         color=color_cabecera)
        tag.move_to((xs[j], y_cabecera, 0))
        cabecera.add(tag)

    ancho_total = (n_col - 1) * ancho_col + ancho_col
    regla = Line((-ancho_total / 2, y_cabecera - alto_fila * 0.52, 0),
                 (ancho_total / 2, y_cabecera - alto_fila * 0.52, 0),
                 stroke_width=1.6, color=color_eje)

    filas = VGroup()
    for i, m in enumerate(ms):
        y = y_cabecera - (i + 1) * float(alto_fila) - 0.10
        fila = VGroup()
        for j, (_n, funcion, decimales) in enumerate(COLUMNAS_ISENTROPICAS):
            # La columna del Mach en el color de cabecera: es la que se
            # busca al leer la tabla, no un resultado.
            col = color_cabecera if j == 0 else color
            celda = _texto_hud(f"{float(funcion(m)):.{decimales}f}",
                               font_size=font_size, color=col)
            celda.move_to((xs[j], y, 0))
            fila.add(celda)
        filas.add(fila)

    return TablaIsentropica(cabecera, filas, regla, ms)


# =======================================================================
# MODULO 2 — ondas de choque normales y flujo cuasi-unidimensional
# =======================================================================

# --- 2.2 las relaciones del choque normal ------------------------------
def choque_normal(mach1):
    """Salto de propiedades a traves de una onda de choque normal.

    Devuelve un dict con M2, p2/p1, T2/T1, rho2/rho1 y p02/p01, todos en
    funcion del Mach de entrada. Son las relaciones de Rankine-Hugoniot
    resueltas para gas ideal calorificamente perfecto — las mismas que
    tabula NACA 1135.

    Con M1 < 1 levanta ValueError en vez de devolver numeros: un choque de
    expansion violaria la segunda ley, y ese es justamente el mensaje del
    clip 3 de la leccion 2.1. Devolver algo aqui lo dejaria pasar callando.
    """
    m1 = float(mach1)
    if m1 < 1.0:
        raise ValueError(f"choque_normal: M1={m1} < 1; un choque de "
                         "expansion violaria la segunda ley")
    g = GAMMA
    m1c = m1 * m1
    m2c = (1 + (g - 1) / 2 * m1c) / (g * m1c - (g - 1) / 2)
    p21 = 1 + 2 * g / (g + 1) * (m1c - 1)
    r21 = (g + 1) * m1c / (2 + (g - 1) * m1c)
    t21 = p21 / r21
    # p02/p01 se escribe con las dos razones y no como exp(-Ds/R) para que
    # el numero salga de las MISMAS expresiones que se dibujan al lado.
    p0201 = (r21 ** (g / (g - 1))
             * ((g + 1) / (2 * g * m1c - (g - 1))) ** (1 / (g - 1)))
    return {"M2": float(np.sqrt(m2c)), "p2/p1": float(p21),
            "T2/T1": float(t21), "rho2/rho1": float(r21),
            "p02/p01": float(p0201)}


# Curvas del choque normal, en el orden en que las cuenta el clip:
# (nombre ASCII, funcion M1 -> valor, color, si crece sin techo).
SALTOS_CHOQUE = (
    ("p2/p1", lambda m: choque_normal(m)["p2/p1"], COLOR_SUPERSONICO, True),
    ("T2/T1", lambda m: choque_normal(m)["T2/T1"], COLOR_TRANSONICO, True),
    ("rho2/rho1", lambda m: choque_normal(m)["rho2/rho1"], COLOR_SUBSONICO,
     False),
    ("M2", lambda m: choque_normal(m)["M2"], COLOR_CALCULO, False),
)

# Tope asintotico de rho2/rho1 cuando M1 -> infinito: (gamma+1)/(gamma-1).
COMPRESION_MAXIMA = (GAMMA + 1) / (GAMMA - 1)   # 6.0 para el aire


# --- 2.3 medir la velocidad --------------------------------------------
def rayleigh_pitot(mach1):
    """p02/p1 de la formula de Rayleigh: Pitot en flujo supersonico.

    Un Pitot supersonico NO mide p0 de la corriente: delante de su boca se
    forma un choque desprendido, asi que lo que lee es la presion de
    estancamiento DETRAS del choque. La formula lo tiene en cuenta de una
    vez, y por eso no es la isentropica.
    """
    m1 = float(mach1)
    if m1 < 1.0:
        raise ValueError(f"rayleigh_pitot: M1={m1} < 1; en subsonico no hay "
                         "choque delante del Pitot (usa razon_presion)")
    g = GAMMA
    m1c = m1 * m1
    primero = ((g + 1) ** 2 * m1c / (4 * g * m1c - 2 * (g - 1))) ** (g / (g - 1))
    segundo = (1 - g + 2 * g * m1c) / (g + 1)
    return float(primero * segundo)


def error_anemometro(mach):
    """Cuanto se equivoca un anemometro que use la formula incompresible.

    Un tubo de Pitot mide p0 - p. El instrumento incompresible supone que
    eso vale (1/2) rho V^2; de verdad vale p[(1+0.2M^2)^3.5 - 1]. El
    cociente menos uno es el error relativo de la presion dinamica, y a
    M = 0 vale cero por continuidad (el limite del cociente es 1).
    """
    m = np.asarray(mach, dtype=np.float64)
    seguro = np.where(m < 1e-4, 1e-4, m)
    exacto = razon_presion(seguro) - 1.0
    incompresible = GAMMA / 2 * seguro ** 2
    return np.where(m < 1e-4, 0.0, exacto / incompresible - 1.0)


# --- 2.4 la relacion area-Mach -----------------------------------------
def mach_de_area(area_rel, rama="sub"):
    """Invierte A/A* -> M por biseccion, en la rama que se pida.

    A/A* vale 1 en M = 1 y crece a los dos lados: para un area dada hay DOS
    Machs posibles, uno subsonico y otro supersonico. Cual de los dos ocurre
    no lo decide la geometria sino la presion de salida — ese es el asunto de
    la leccion 2.5. Aqui solo hace falta poder pedir cualquiera de los dos.

    Biseccion y no Newton: la derivada se anula justo en M = 1, que es el
    borde de los dos intervalos y el caso que mas se pide.
    """
    objetivo = float(area_rel)
    if objetivo < 1.0 - 1e-9:
        raise ValueError(f"mach_de_area: A/A* = {objetivo} < 1 no existe")
    if rama not in ("sub", "super"):
        raise ValueError("mach_de_area: rama debe ser 'sub' o 'super'")
    if objetivo <= 1.0:
        return 1.0
    lo, hi = (1e-6, 1.0) if rama == "sub" else (1.0, 60.0)
    # 60 bisecciones dejan el intervalo en ~1e-17: de sobra, y el numero
    # importa porque `perfil_tobera` llama a esto cientos de veces por
    # render (con 200 el clip tardaba segundos solo en resolver Machs).
    for _ in range(60):
        medio = (lo + hi) / 2
        valor = float(razon_area(medio))
        # En la rama subsonica A/A* DECRECE con M; en la supersonica crece.
        if (valor > objetivo) == (rama == "sub"):
            lo = medio
        else:
            hi = medio
    return float((lo + hi) / 2)


# --- 2.1.1 la coalescencia, en el plano x-t ----------------------------
class DiagramaXT(_Cartesiano):
    """Ondas de compresion en el plano x-t: la de detras siempre alcanza.

    Cada pulso viaja sobre el gas que ya movio y calento el anterior, asi
    que va mas rapido. En el plano x-t eso son rectas cada vez MENOS
    inclinadas, y rectas que se cierran acaban cortandose: ahi nace el
    choque. La coalescencia no se postula, se ve.
    """

    def __init__(self, ejes, caracteristicas, choque, corte, t_max, x_max,
                 ancho, alto, origen, **kwargs):
        super().__init__(ejes, caracteristicas, choque, **kwargs)
        self.ejes = ejes
        self.caracteristicas = caracteristicas
        self.choque = choque
        self._corte = corte
        self._calibrar((0.0, x_max), (0.0, t_max), ancho, alto, origen)

    def caracteristica(self, i):
        return self.caracteristicas[i % len(self.caracteristicas)]

    def coalescencia(self):
        """Punto (x, t) donde las dos primeras rectas se cortan: el instante
        y el sitio en que el frente pasa a ser una discontinuidad."""
        return self._en(*self._corte)


def diagrama_xt(n_ondas=6, c0=1.0, refuerzo=0.16, t_max=1.0, ancho=5.0,
                alto=2.9, color=COLOR_CALCULO, color_choque=COLOR_SUPERSONICO,
                color_ejes=COLOR_EJE, font_size=14):
    """Familia de caracteristicas que convergen, y el choque que forman.

    La onda i sale en t_i y viaja a c0(1 + refuerzo*i): cada una sobre un gas
    algo mas caliente y ya en movimiento. El corte de las DOS PRIMERAS es el
    primero en ocurrir, y desde el se dibuja el frente unico.
    """
    n = int(n_ondas)
    if n > ONDAS_MAX:
        raise ValueError(f"diagrama_xt: n_ondas={n} supera ONDAS_MAX={ONDAS_MAX}")
    n = max(2, n)
    t_max = float(t_max)
    # Instantes de emision y velocidades: la de detras siempre mas rapida.
    ts = np.linspace(0.0, t_max * 0.42, n)
    cs = float(c0) * (1 + float(refuerzo) * np.arange(n))

    # Corte de las dos primeras: c0(t-t0) = c1(t-t1)  ->  t y luego x.
    t_corte = (cs[1] * ts[1] - cs[0] * ts[0]) / (cs[1] - cs[0])
    x_corte = cs[0] * (t_corte - ts[0])
    x_max = max(x_corte * 1.9, cs[-1] * (t_max - ts[-1]))

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (0.0, x_max), (0.0, t_max), ancho, alto)

    caracteristicas = VGroup()
    for t0, c in zip(ts, cs):
        # Cada recta se corta al llegar al frente ya formado, no antes: mas
        # alla de la coalescencia ya no hay ondas sueltas que dibujar.
        t_fin = min(t_max, t_corte)
        pts = np.array([en(0.0, t0), en(c * (t_fin - t0), t_fin)])
        recta = Line(pts[0], pts[1], stroke_width=2.0, color=color)
        recta.set_stroke(opacity=0.75)
        caracteristicas.add(recta)

    # El frente unico, desde la coalescencia hacia arriba y algo mas rapido
    # que la ultima onda suelta (un choque adelanta al sonido de delante).
    v_choque = cs[-1] * 1.06
    choque = Line(en(x_corte, t_corte),
                  en(x_corte + v_choque * (t_max - t_corte), t_max),
                  stroke_width=4.0, color=color_choque)

    tag_x = _texto_hud("POSICION  x", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_hud("t", font_size=font_size + 3)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return DiagramaXT(ejes, caracteristicas, choque, (x_corte, t_corte),
                      t_max, x_max, ancho, alto, origen)


# --- 2.1.2 el espesor real ---------------------------------------------
class PerfilChoque(VGroup):
    """El escalon, visto de cerca: ni vertical ni ancho — unas micras."""

    def __init__(self, ejes, curva, escala, salto, ancho, **kwargs):
        super().__init__(ejes, curva, escala, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.escala = escala
        self.salto = float(salto)
        self._ancho = float(ancho)


def perfil_choque(salto=4.5, espesor_rel=0.055, ancho=5.2, alto=2.4,
                  color=COLOR_SUPERSONICO, color_ejes=COLOR_EJE,
                  font_size=14, muestras=200, etiqueta="200 nm"):
    """Perfil real de presion a traves del choque: una tanh muy apretada.

    `espesor_rel` es la fraccion del ancho que ocupa la transicion. Se deja
    VISIBLE a proposito aunque en la realidad sea invisible: el clip cuenta
    justamente que el escalon tiene grosor, y un salto pintado vertical
    diria lo contrario. La barra de escala pone el numero de verdad.
    """
    muestras = _validar_muestras("perfil_choque", muestras)
    s = float(salto)
    x = np.linspace(-0.5, 0.5, muestras)
    y = (1 + (s - 1) * (np.tanh(x / max(float(espesor_rel), 1e-3)) + 1) / 2)

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (-0.5, 0.5), (0.0, s * 1.12), ancho, alto)
    curva = _curva(en(x, y), color, grosor=3.0)

    # Barra de escala bajo la transicion, del ancho real del salto.
    medio = origen[0] + ancho / 2
    semi = espesor_rel * ancho * 1.6
    barra = VGroup(
        Line((medio - semi, origen[1] - 0.30, 0),
             (medio + semi, origen[1] - 0.30, 0), stroke_width=2.0,
             color=color),
        Line((medio - semi, origen[1] - 0.40, 0),
             (medio - semi, origen[1] - 0.20, 0), stroke_width=1.6,
             color=color),
        Line((medio + semi, origen[1] - 0.40, 0),
             (medio + semi, origen[1] - 0.20, 0), stroke_width=1.6,
             color=color))
    tag = _texto_hud(etiqueta, font_size=font_size, color=color)
    tag.next_to(barra, DOWN, buff=0.10)
    escala = VGroup(barra, tag)

    tag_y = _texto_hud("p/p1", font_size=font_size)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_y)

    return PerfilChoque(ejes, curva, escala, s, ancho)


# --- 2.1.4 como se fotografia una onda ---------------------------------
class EsquemaSchlieren(VGroup):
    """Por que una onda de choque sale en una foto: la luz se dobla.

    Donde la densidad cambia de golpe, el indice de refraccion tambien, y el
    rayo que la cruza sale desviado. La cuchilla corta justo esos rayos, y
    en la pantalla queda la sombra de la onda. Es todo el truco.
    """

    def __init__(self, rayos, seccion, onda, cuchilla, pantalla, banda,
                 **kwargs):
        super().__init__(rayos, seccion, onda, cuchilla, pantalla, banda,
                         **kwargs)
        self.rayos = rayos
        self.seccion = seccion
        self.onda = onda
        self.cuchilla = cuchilla
        self.pantalla = pantalla
        self.banda = banda


def esquema_schlieren(n_rayos=9, ancho=8.4, alto=3.0, desviados=(3, 4),
                      color_luz=COLOR_TRANSONICO, color_onda=COLOR_SUPERSONICO,
                      color_eje=COLOR_EJE, font_size=13):
    """Banco Schlieren esquematico: rayos, seccion de ensayo, cuchilla y
    pantalla. `desviados` son los indices de los rayos que cruzan la onda."""
    n = max(3, int(n_rayos))
    if n > ONDAS_MAX * 2:
        raise ValueError(f"esquema_schlieren: n_rayos={n} es demasiado")

    x0, x_sec, x_cuchilla, x_pant = -ancho / 2, -ancho / 6, ancho / 4, ancho / 2
    ys = np.linspace(alto / 2, -alto / 2, n)
    idx = set(int(i) % n for i in desviados)

    rayos = VGroup()
    for i, y in enumerate(ys):
        if i in idx:
            # El rayo que cruza la onda sale con un angulo y se estampa en
            # la cuchilla: por eso ese trozo de imagen queda oscuro.
            y_desvio = y - 0.42
            pts = [(x0, y, 0), (x_sec, y, 0), (x_cuchilla, y_desvio, 0)]
            color = color_onda
        else:
            pts = [(x0, y, 0), (x_pant, y, 0)]
            color = color_luz
        rayo = VMobject(color=color, stroke_width=1.8)
        rayo.set_points_as_corners([np.array(p) for p in pts])
        rayo.set_stroke(opacity=0.9 if i in idx else 0.55)
        rayos.add(rayo)

    seccion = VGroup(DashedVMobject(
        Rectangle(width=ancho / 4, height=alto * 1.12, stroke_width=1.8,
                  color=color_eje).move_to((x_sec + ancho / 12, 0, 0)),
        num_dashes=36))
    onda = Line((x_sec, alto / 2 + 0.2, 0), (x_sec, -alto / 2 - 0.2, 0),
                stroke_width=3.4, color=color_onda)

    hoja = Rectangle(width=0.22, height=alto / 2 + 0.5, stroke_width=0,
                     fill_color=color_eje, fill_opacity=1.0)
    hoja.move_to((x_cuchilla, -alto / 2 - 0.25 + hoja.height / 2, 0))
    cuchilla = VGroup(hoja)
    # La pantalla se pinta ILUMINADA (una franja de luz), no como una linea:
    # la banda de la onda es un HUECO en esa luz, y un hueco solo se ve si
    # hay algo alrededor de lo que faltar.
    pantalla = VGroup(Rectangle(width=0.20, height=alto + 0.70,
                                stroke_width=0, fill_color=color_luz,
                                fill_opacity=0.55)
                      .move_to((x_pant, 0, 0)))

    # La franja oscura: donde faltan los rayos que la cuchilla se comio. Se
    # pinta del color del FONDO —es ausencia de luz, no una marca— con un
    # filo tenue del color de la onda para que se lea de que es la sombra.
    y_altos = [ys[i] for i in sorted(idx)]
    banda = Rectangle(width=0.21,
                      height=abs(max(y_altos) - min(y_altos)) + 0.34,
                      stroke_width=1.4, color=color_onda,
                      fill_color=CODE_BG, fill_opacity=1.0)
    banda.move_to((x_pant, (max(y_altos) + min(y_altos)) / 2, 0))

    # Cada rotulo se pega a SU pieza para que entre y salga con ella: en un
    # esquema que se enciende por partes, un rotulo suelto aparece antes que
    # lo que nombra.
    for mob, texto, lado in ((seccion, "SECCION", UP),
                             (cuchilla, "CUCHILLA", DOWN),
                             (pantalla, "PANTALLA", UP)):
        tag = _texto_hud(texto, font_size=font_size, color=color_eje)
        tag.next_to(mob, lado, buff=0.14)
        mob.add(tag)

    return EsquemaSchlieren(rayos, seccion, onda, cuchilla, pantalla, banda)


# --- 2.2 / 2.4 las curvas del choque y del area ------------------------
# (nombre ASCII, funcion M1 -> valor, color) por grupo. Se separan porque
# p2/p1 llega a 10 y M2 no pasa de 1: en un mismo eje, el segundo grupo
# quedaria pegado al suelo y no se leeria nada.
GRUPOS_CHOQUE = {
    "saltos": (("p2/p1", lambda m: choque_normal(m)["p2/p1"],
                COLOR_SUPERSONICO),
               ("T2/T1", lambda m: choque_normal(m)["T2/T1"],
                COLOR_TRANSONICO),
               ("rho2/rho1", lambda m: choque_normal(m)["rho2/rho1"],
                COLOR_SUBSONICO)),
    "perdidas": (("M2", lambda m: choque_normal(m)["M2"], COLOR_CALCULO),
                 ("p02/p01", lambda m: choque_normal(m)["p02/p01"],
                  COLOR_SUPERSONICO)),
}


class CurvasChoque(_Cartesiano):
    """Que le hace un choque normal al flujo, en funcion del Mach de entrada."""

    def __init__(self, ejes, curvas, etiquetas, grupo, rango_m, rango_y,
                 ancho, alto, origen, **kwargs):
        super().__init__(ejes, curvas, etiquetas, **kwargs)
        self.ejes = ejes
        self.curvas = curvas
        self.etiquetas = etiquetas
        self.grupo = str(grupo)
        self._calibrar(rango_m, rango_y, ancho, alto, origen)

    def _entradas(self):
        return GRUPOS_CHOQUE[self.grupo]

    def nombre(self, i):
        return self._entradas()[i % len(self._entradas())][0]

    def valor(self, i, mach1):
        """El salto i para ese M1. Misma fuente que la curva dibujada."""
        return float(self._entradas()[i % len(self._entradas())][1](
            float(mach1)))

    def color_de(self, i):
        """Color de la curva i (no `color`: lo sombrearia el del Mobject)."""
        return self._entradas()[i % len(self._entradas())][2]

    def curva(self, i):
        return self.curvas[i % len(self.curvas)]

    def punto_de(self, i, mach1):
        return self._en(mach1, self.valor(i, mach1))

    def vertical_en(self, mach1, color=None, grosor=1.5):
        """Corte de eje a eje en ese M1, para leer las curvas a la vez."""
        return DashedLine(self._en(mach1, self._ry[0]),
                          self._en(mach1, self._ry[1]), stroke_width=grosor,
                          color=COLOR_EJE if color is None else color,
                          dash_length=0.08)

    def horizontal_en(self, valor, color=None, grosor=1.6):
        """Recta de valor constante a lo ancho del grafico: la asintota de
        rho2/rho1 es el uso previsto. La construye la pieza porque las
        coordenadas de la caja son suyas — armada en el clip a partir de una
        DashedLine degenerada, no se dibuja nada."""
        return DashedLine(self._en(self._rx[0], valor),
                          self._en(self._rx[1], valor), stroke_width=grosor,
                          color=COLOR_EJE if color is None else color,
                          dash_length=0.08)


def curvas_choque(grupo="saltos", m_max=3.0, ancho=5.2, alto=2.8,
                  color_ejes=COLOR_EJE, font_size=15, muestras=140,
                  hueco_etiquetas=0.72):
    """Ejes (M1 ->, salto ^) con las curvas del choque normal.

    `grupo` es 'saltos' (p2/p1, T2/T1, rho2/rho1) o 'perdidas' (M2 y
    p02/p01). Arranca en M1 = 1 y no en 0: por debajo no hay choque, y
    dibujar el tramo vacio insinuaria que si.
    """
    if grupo not in GRUPOS_CHOQUE:
        raise ValueError(f"curvas_choque: grupo '{grupo}' desconocido "
                         f"({', '.join(sorted(GRUPOS_CHOQUE))})")
    muestras = _validar_muestras("curvas_choque", muestras)
    m1 = float(m_max)
    if m1 <= 1.0:
        raise ValueError("curvas_choque: m_max debe ser mayor que 1")
    ms = np.linspace(1.0, m1, muestras)

    entradas = GRUPOS_CHOQUE[grupo]
    series = [np.array([float(f(m)) for m in ms]) for _n, f, _c in entradas]
    y_lo = 0.0 if grupo == "perdidas" else 1.0
    y_hi = max(float(s.max()) for s in series) * 1.08

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (1.0, m1), (y_lo, y_hi), ancho, alto)

    curvas = VGroup()
    etiquetas = VGroup()
    x_tag = origen[0] + ancho + float(hueco_etiquetas)
    n = len(entradas)
    alturas = [0.86 - 0.32 * i for i in range(n)]
    for i, ((nombre, _f, color), ys) in enumerate(zip(entradas, series)):
        curvas.add(_curva(en(ms, ys), color, grosor=2.8))
        fin = en(m1, ys[-1])
        tag = _texto_hud(nombre, font_size=font_size, color=color)
        tag.move_to((x_tag + tag.width / 2, origen[1] + alturas[i] * alto, 0))
        guia = DashedLine(fin + RIGHT * 0.08, tag.get_left() + LEFT * 0.10,
                          stroke_width=1.2, color=color, dash_length=0.07)
        guia.set_stroke(opacity=0.55)
        etiquetas.add(VGroup(guia, tag))

    marcas = VGroup()
    for valor in (1.0, m1):
        muesca = Line(en(valor, y_lo) + DOWN * 0.08, en(valor, y_lo),
                      stroke_width=1.6, color=color_ejes)
        num = _texto_hud(f"{valor:g}", font_size=font_size - 3,
                         color=color_ejes)
        num.next_to(muesca, DOWN, buff=0.08)
        marcas.add(muesca, num)

    tag_x = _texto_hud("MACH ANTES DEL CHOQUE", font_size=font_size - 2)
    tag_x.next_to(ejes[0], DOWN, buff=0.44)
    ejes.add(marcas, tag_x)

    return CurvasChoque(ejes, curvas, etiquetas, grupo, (1.0, m1),
                        (y_lo, y_hi), ancho, alto, origen)


class CurvaAnemometro(_Cartesiano):
    """Cuanto miente medir la velocidad con la formula incompresible."""

    def __init__(self, ejes, curva, umbral, etiquetas, m_max, err_max, ancho,
                 alto, origen, **kwargs):
        super().__init__(ejes, umbral, curva, etiquetas, **kwargs)
        self.ejes = ejes
        self.curva = curva
        self.umbral = umbral
        self.etiquetas = etiquetas
        self._calibrar((0.0, m_max), (0.0, err_max), ancho, alto, origen)

    def error(self, mach):
        """Error relativo en fraccion. Misma fuente que el trazo."""
        return float(error_anemometro(mach))

    def punto_de(self, mach):
        return self._en(mach, self.error(mach))


def curva_anemometro(m_max=1.0, umbral=0.05, ancho=5.2, alto=2.6,
                     color=COLOR_TRANSONICO, color_umbral=COLOR_CALCULO,
                     color_ejes=COLOR_EJE, font_size=14, muestras=140):
    """Ejes (Mach ->, error % ^) del anemometro incompresible, con su umbral.

    Es el hermano de `curva_compresibilidad` y cuenta lo mismo desde el otro
    lado: alli la densidad, aqui el instrumento que la ignora.
    """
    muestras = _validar_muestras("curva_anemometro", muestras)
    m1 = float(m_max)
    ms = np.linspace(0.0, m1, muestras)
    errs = np.asarray(error_anemometro(ms), dtype=np.float64)
    e_hi = float(errs.max()) * 1.10

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (0.0, m1), (0.0, e_hi), ancho, alto)
    curva = _curva(en(ms, errs), color, grosor=3.0)

    y_u = float(np.clip(umbral / e_hi, 0.0, 1.0)) * alto
    linea = DashedLine(origen + np.array([0.0, y_u, 0.0]),
                       origen + np.array([ancho, y_u, 0.0]),
                       stroke_width=1.6, color=color_umbral, dash_length=0.08)
    tag_u = _texto_hud(f"{umbral * 100:.0f} %", font_size=font_size,
                       color=color_umbral)
    tag_u.next_to(linea.get_end(), UP, buff=0.08).shift(LEFT * 0.18)

    tag_x = _texto_hud("MACH", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_display("error del anemómetro", font_size=font_size + 2)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaAnemometro(ejes, curva, linea, VGroup(tag_u), m1, e_hi, ancho,
                           alto, origen)


class EscaleraVelocidades(VGroup):
    """IAS, CAS, EAS y TAS: cuatro numeros para la misma velocidad."""

    def __init__(self, barras, valores, nombres, **kwargs):
        super().__init__(barras, **kwargs)
        self.barras = barras
        self._v = list(valores)
        self._n = list(nombres)

    def barra(self, i):
        return self.barras[i % len(self.barras)]

    def valor(self, i):
        """m/s de la lectura i, en el orden IAS, CAS, EAS, TAS."""
        return self._v[i % len(self._v)]

    def nombre(self, i):
        return self._n[i % len(self._n)]


def escalera_velocidades(tas=250.0, altitud=11000.0, error_posicion=2.0,
                         ancho=6.0, alto=0.40, separacion=0.30,
                         font_size=16, color_eje=COLOR_EJE):
    """Las cuatro velocidades de un anemometro, a escala entre si.

    EAS sale de TAS por la raiz del cociente de densidades — es la unica
    relacion exacta del grupo y la que explica el salto grande. CAS y IAS se
    separan de EAS por la compresibilidad y por el error de posicion de la
    toma, que aqui entra como un dato del avion (`error_posicion`).
    """
    tas = float(tas)
    rho = isa(float(altitud))[2]
    rho0 = isa(0.0)[2]
    eas = tas * float(np.sqrt(rho / rho0))
    # La correccion de compresibilidad va de CAS a EAS y siempre resta:
    # se estima con el mismo error del anemometro, a mitad de efecto sobre
    # la velocidad (la presion dinamica va como V^2).
    mach = tas / isa(float(altitud))[3]
    cas = eas * (1 + float(error_anemometro(mach)) / 2)
    ias = cas - float(error_posicion)

    valores = [ias, cas, eas, tas]
    nombres = ["IAS", "CAS", "EAS", "TAS"]
    colores = [COLOR_SUBSONICO, COLOR_SUBSONICO, COLOR_CALCULO,
               COLOR_TRANSONICO]
    escala = ancho / max(valores)

    barras = VGroup()
    for i, (v, nombre, color) in enumerate(zip(valores, nombres, colores)):
        y = -i * (alto + separacion)
        caja = Rectangle(width=v * escala, height=alto, stroke_width=0,
                         fill_color=color, fill_opacity=0.85)
        caja.move_to((-ancho / 2 + v * escala / 2, y, 0))
        etiqueta = _texto_hud(nombre, font_size=font_size, color=color)
        etiqueta.next_to(caja, LEFT, buff=0.22)
        cifra = _texto_hud(f"{v:.0f} m/s", font_size=font_size - 1,
                           color=color)
        cifra.next_to(caja, RIGHT, buff=0.18)
        barras.add(VGroup(caja, etiqueta, cifra))

    return EscaleraVelocidades(barras, valores, nombres)


class CurvaAreaMach(_Cartesiano):
    """A/A* con sus DOS ramas: la misma area, dos Machs posibles."""

    def __init__(self, ejes, rama_sub, rama_super, garganta, etiquetas,
                 m_max, a_max, ancho, alto, origen, **kwargs):
        super().__init__(ejes, rama_sub, rama_super, garganta, etiquetas,
                         **kwargs)
        self.ejes = ejes
        self.rama_sub = rama_sub
        self.rama_super = rama_super
        self.garganta = garganta
        self.etiquetas = etiquetas
        self._calibrar((0.0, m_max), (0.0, a_max), ancho, alto, origen)

    def area(self, mach):
        return float(razon_area(mach))

    def punto_de(self, mach):
        return self._en(mach, self.area(mach))

    def mach_de(self, area_rel, rama="sub"):
        """El Mach que da esa area en la rama pedida (la libreria invierte)."""
        return mach_de_area(area_rel, rama)

    def horizontal_en(self, area_rel, color=None, grosor=1.5):
        """Recta de area constante: corta a las DOS ramas, y ese es el punto
        del clip — una relacion de areas no basta para decidir el Mach."""
        return DashedLine(self._en(0.0, area_rel), self._en(self._rx[1],
                                                            area_rel),
                          stroke_width=grosor,
                          color=COLOR_EJE if color is None else color,
                          dash_length=0.08)


def curva_area_mach(m_max=3.2, ancho=5.4, alto=2.9, color_sub=COLOR_SUBSONICO,
                    color_super=COLOR_SUPERSONICO, color_ejes=COLOR_EJE,
                    font_size=14, muestras=180):
    """A/A* frente al Mach, con la rama subsonica y la supersonica en
    colores distintos y la garganta marcada en M = 1.

    Las dos ramas son la MISMA funcion: se pintan distinto porque el clip
    necesita que se vea que una relacion de areas admite dos soluciones.
    """
    muestras = _validar_muestras("curva_area_mach", muestras)
    m1 = float(m_max)
    # Se arranca en M = 0.12 y no en 0: A/A* diverge en M -> 0 y el trazo se
    # iria al infinito arrastrando toda la escala vertical.
    ms_sub = np.linspace(0.12, 1.0, muestras // 2)
    ms_sup = np.linspace(1.0, m1, muestras // 2)
    a_sub = np.array([float(razon_area(m)) for m in ms_sub])
    a_sup = np.array([float(razon_area(m)) for m in ms_sup])
    a_hi = max(float(a_sub.max()), float(a_sup.max())) * 1.06

    ejes, origen = _ejes_xy(ancho, alto, color_ejes)
    en = _escalador(origen, (0.0, m1), (0.0, a_hi), ancho, alto)
    rama_sub = _curva(en(ms_sub, a_sub), color_sub, grosor=3.0)
    rama_super = _curva(en(ms_sup, a_sup), color_super, grosor=3.0)

    punto = en(1.0, 1.0)
    garganta = VGroup(Dot(punto, radius=0.07, color=COLOR_CALCULO),
                      DashedLine(en(1.0, 0.0), punto, stroke_width=1.3,
                                 color=COLOR_EJE, dash_length=0.07))

    etiquetas = VGroup()
    for texto, color, m_ref in (("subsónico", color_sub, 0.30),
                                ("supersónico", color_super, 2.4)):
        tag = _texto_display(texto, font_size=font_size + 3, color=color)
        tag.next_to(en(m_ref, float(razon_area(m_ref))), UR, buff=0.10)
        etiquetas.add(tag)
    tag_g = _texto_hud("A/A* = 1", font_size=font_size, color=COLOR_CALCULO)
    tag_g.next_to(punto, DOWN, buff=0.30)
    etiquetas.add(tag_g)

    tag_x = _texto_hud("MACH", font_size=font_size - 1)
    tag_x.next_to(ejes[0], DOWN, buff=0.18)
    tag_y = _texto_hud("A/A*", font_size=font_size + 1)
    tag_y.next_to(ejes[1], UP, buff=0.14)
    ejes.add(tag_x, tag_y)

    return CurvaAreaMach(ejes, rama_sub, rama_super, garganta, etiquetas, m1,
                         a_hi, ancho, alto, origen)


# --- 2.5 la tobera, regimen a regimen ----------------------------------
# El orden es el de la subida de presion de salida: de la tobera adaptada a
# la que ni siquiera se bloquea. (clave, etiqueta, color).
REGIMENES_TOBERA = (
    ("diseno", "adaptada", COLOR_SUPERSONICO),
    ("choque", "choque interno", COLOR_TRANSONICO),
    ("bloqueo", "bloqueada", COLOR_CALCULO),
    ("venturi", "sin bloquear", COLOR_SUBSONICO),
)


def _solucion_tobera(xs, areas, regimen, m_garganta, x_choque):
    """(machs, presiones/p01) a lo largo del conducto para ese regimen.

    `areas` es A(x)/A_garganta. Todo sale de invertir A/A* y de aplicar
    p/p0 = 1/razon_presion(M); el unico caso con dos tramos es el del
    choque, y su segundo tramo usa el A* NUEVO que impone la perdida de
    presion de estancamiento (A*2 = A*1 * p01/p02).
    """
    machs = np.empty_like(xs)
    presiones = np.empty_like(xs)

    if regimen == "choque":
        salto = choque_normal(mach_de_area(
            float(np.interp(x_choque, xs, areas)), "super"))
        factor = salto["p02/p01"]
    else:
        salto, factor = None, 1.0

    for k, (x, a) in enumerate(zip(xs, areas)):
        if regimen == "venturi":
            m = mach_de_area(a * float(razon_area(m_garganta)), "sub")
            p0_local = 1.0
        elif regimen == "bloqueo":
            m = mach_de_area(a, "sub")
            p0_local = 1.0
        elif regimen == "diseno":
            m = mach_de_area(a, "super" if x > 0.5 else "sub")
            p0_local = 1.0
        elif regimen == "choque":
            if x <= x_choque:
                m = mach_de_area(a, "super" if x > 0.5 else "sub")
                p0_local = 1.0
            else:
                m = mach_de_area(a * factor, "sub")
                p0_local = factor
        else:
            raise ValueError(f"perfil_tobera: regimen '{regimen}' desconocido")
        machs[k] = m
        presiones[k] = p0_local / float(razon_presion(m))
    return machs, presiones


class PerfilTobera(VGroup):
    """La figura del modulo 2: la tobera arriba, p/p0 abajo, por regimenes.

    Cada curva es una presion de salida distinta sobre la MISMA geometria.
    Todas comparten el tramo convergente —el bloqueo hace que aguas arriba
    de la garganta no se entere nadie de lo que pasa detras— y se separan
    en el divergente. Ese es el mensaje entero de la leccion 2.5.
    """

    def __init__(self, tubo, ejes, curvas, choques, datos, ancho, alto,
                 origen, **kwargs):
        # `choques` es un DICT (clave -> marca) para poder consultarlo por
        # nombre; al VGroup van sus valores. Y entran AQUI, antes de congelar
        # el centro: añadir un submobject despues cambiaria el bounding box
        # y `punto_de` empezaria a mentir.
        super().__init__(tubo, ejes, curvas, VGroup(*choques.values()),
                         **kwargs)
        self.tubo = tubo
        self.ejes = ejes
        self.curvas = curvas
        self.choques = choques
        self._d = datos           # clave -> (xs, machs, presiones, color)
        self._ancho = float(ancho)
        self._alto = float(alto)
        self._origen = np.asarray(origen, dtype=np.float64)
        self._centro_original = self.get_center()

    def _clave(self, nombre):
        if nombre not in self._d:
            raise KeyError(f"perfil_tobera: no se pidio el regimen "
                           f"'{nombre}' ({', '.join(self._d)})")
        return nombre

    def curva(self, nombre):
        """La traza de p/p0 de ese regimen."""
        return self.curvas[list(self._d).index(self._clave(nombre))]

    def choque(self, nombre):
        """La marca vertical del choque interno, o None si ese regimen no
        tiene ninguno."""
        return self.choques.get(self._clave(nombre))

    def mach(self, nombre, x):
        """Mach en la estacion x (0 = entrada, 1 = salida)."""
        xs, machs, _p, _c = self._d[self._clave(nombre)]
        return float(np.interp(float(np.clip(x, 0, 1)), xs, machs))

    def presion(self, nombre, x):
        """p/p0 en la estacion x. Misma fuente que la curva dibujada."""
        xs, _m, ps, _c = self._d[self._clave(nombre)]
        return float(np.interp(float(np.clip(x, 0, 1)), xs, ps))

    def salida(self, nombre):
        """p_salida/p0: el numero que distingue un regimen de otro."""
        return self.presion(nombre, 1.0)

    def color_de(self, nombre):
        return self._d[self._clave(nombre)][3]

    def punto_de(self, nombre, x):
        """Punto de escena sobre la curva de ese regimen."""
        p = self.presion(nombre, x)
        desplazamiento = self.get_center() - self._centro_original
        return (self._origen
                + np.array([float(np.clip(x, 0, 1)) * self._ancho,
                            float(np.clip(p, 0.0, 1.0)) * self._alto, 0.0])
                + desplazamiento)


def perfil_tobera(area_garganta=0.42, regimenes=("diseno", "choque",
                                                 "bloqueo", "venturi"),
                  m_garganta_venturi=0.55, x_choque=0.74, ancho=6.4,
                  alto_tubo=1.7, alto_grafico=2.3, hueco=0.55,
                  color_tubo=CODE_MUTED, color_ejes=COLOR_EJE, font_size=14,
                  muestras=90):
    """Tobera De Laval con su grafico de p/p0, una curva por regimen.

    Comparten el eje x con el conducto de arriba, asi que cada punto de la
    curva cae bajo la seccion que le corresponde. `muestras` se queda corto
    a proposito (90): cada punto exige invertir A/A* por biseccion.
    """
    claves = [str(r) for r in regimenes]
    validos = {k for k, _e, _c in REGIMENES_TOBERA}
    for k in claves:
        if k not in validos:
            raise ValueError(f"perfil_tobera: regimen '{k}' desconocido "
                             f"({', '.join(sorted(validos))})")
    # Impar a la fuerza: con un numero par de muestras la rejilla no cae
    # nunca en x = 0.5 y la garganta —el punto entero de la leccion— se lee
    # interpolada, dando M = 0.986 donde tiene que dar 1.
    muestras = _validar_muestras("perfil_tobera", muestras)
    muestras = muestras if muestras % 2 else muestras + 1

    tubo = conducto("delaval", area_garganta=area_garganta, largo=ancho,
                    alto=alto_tubo, color=color_tubo)
    tubo.shift(UP * (alto_grafico / 2 + hueco + alto_tubo / 2))

    xs = np.linspace(0.0, 1.0, muestras)
    areas = np.array([tubo.area(x) for x in xs]) / float(area_garganta)

    # El grafico se queda centrado en ORIGIN y es el TUBO el que sube: asi
    # el origen que devuelve `_ejes_xy` sigue siendo el bueno y `punto_de`
    # no necesita corregir nada.
    ejes, origen = _ejes_xy(ancho, alto_grafico, color_ejes)
    en = _escalador(origen, (0.0, 1.0), (0.0, 1.0), ancho, alto_grafico)

    colores = {k: c for k, _e, c in REGIMENES_TOBERA}
    curvas = VGroup()
    choques = {}
    datos = {}
    for clave in claves:
        machs, presiones = _solucion_tobera(xs, areas, clave,
                                            m_garganta_venturi, x_choque)
        color = colores[clave]
        curvas.add(_curva(en(xs, presiones), color, grosor=2.6))
        datos[clave] = (xs, machs, presiones, color)
        if clave == "choque":
            # El choque se marca en el TUBO, no en el grafico: es un sitio
            # del conducto, y en la curva ya se ve solo como un escalon.
            marca = Line(tubo.punto_de(x_choque, -1.0),
                         tubo.punto_de(x_choque, 1.0), stroke_width=3.0,
                         color=COLOR_SUPERSONICO)
            choques[clave] = marca

    tag_y = _texto_hud("p/p0", font_size=font_size + 1)
    tag_y.next_to(ejes[1], UP, buff=0.12)
    tag_g = _texto_hud("GARGANTA", font_size=font_size - 2)
    tag_g.move_to((0.0, origen[1] - 0.28, 0))
    guia = DashedLine(en(0.5, 0.0), en(0.5, 1.0), stroke_width=1.2,
                      color=color_ejes, dash_length=0.08)
    guia.set_stroke(opacity=0.6)
    ejes.add(guia, tag_y, tag_g)

    return PerfilTobera(tubo, ejes, curvas, choques, datos, ancho,
                        alto_grafico, origen)
