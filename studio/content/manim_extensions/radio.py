"""Radio definida por software animable: IQ, espectro, waterfall y bits.

Pensado para el curso "SDR: la radio hecha software". Todo el calculo es
numpy puro y determinista (`np.random.default_rng(semilla)`, nunca el
`random` global): mismo script -> mismo render, condicion necesaria para
trabajar con `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso: la SEÑAL es ambar, la componente I cian, la Q
violeta, el RUIDO y sus fantasmas rojos, lo RECUPERADO verde; los ejes y el
mobiliario en el gris azulado `COLOR_EJE`. No mezclar roles.

Piezas:
    plano IQ + fasor        el numero complejo como flecha que gira
    ondas                   senoidal, AM (con envolvente), FM, flujo cortado
    espectro                ventana con sintonia, pico gaussiano, barras
    waterfall               ImageMobject sintetico con 4 firmas reales
    digital                 constelacion BPSK, curva de acantilado, ojo

El waterfall es RASTER (`ImageMobject`): en las escenas va siempre dentro de
un `Group`, nunca de un `VGroup`. Expone `.pos_de(f_rel, t_rel)` para colgar
recuadros y tags sobre una firma concreta sin adivinar coordenadas.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render): `TRAZAS_MAX`
y `PUNTOS_MAX` levantan ValueError (a diferencia de fractales.py, que
recorta en silencio: aqui pasarse cambia lo que se ve, y es mejor enterarse).

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from radio import (plano_iq, fasor, girar_fasor, ventana_espectro,
                       pico_espectral, waterfall_imagen, constelacion_bpsk,
                       diagrama_ojo)

    plano = plano_iq(radio=1.7)
    f = fasor(plano, angulo=0.6)
    self.add(plano, f)
    self.play(girar_fasor(f, 2 * np.pi + 0.6))
"""

import numpy as np

from manim import (Animation, Circle, DashedVMobject, Dot, ImageMobject,
                   Line, Rectangle, Text, VGroup, VMobject, linear)

from code_brand import FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
TRAZAS_MAX = 60         # trazas maximas de un diagrama de ojo
PUNTOS_MAX = 80         # puntos maximos de una constelacion

# Paleta propia de la libreria (coincide con la del curso).
COLOR_SENAL = "#f59e0b"     # LA SEÑAL: ondas, picos, trazas, fasor
COLOR_I = "#22d3ee"         # componente I, envolvente, el "uno" digital
COLOR_Q = "#a78bfa"         # componente Q, FM, el "cero" digital
COLOR_RUIDO = "#f43f5e"     # ruido, alias fantasma, bits errados
COLOR_OK = "#34d399"        # mensaje recuperado, enlace vivo
COLOR_EJE = "#31414f"       # mobiliario: ejes, ventanas, cortes

# Alias cortos con los nombres de la tabla de paleta del curso, para que el
# style_block de los clips pueda escribir `color=C_SENAL` tal cual.
C_SENAL, C_I, C_Q = COLOR_SENAL, COLOR_I, COLOR_Q
C_RUIDO, C_OK, C_EJE = COLOR_RUIDO, COLOR_OK, COLOR_EJE

_EPS = 1e-9

# Muestras por curva: suficientes para que una senoidal de 26 ciclos no se
# aliasee en pantalla, sin inflar el numero de beziers de la escena.
_MUESTRAS_CURVA = 420


# --- utilidades internas ----------------------------------------------
def _hex_a_rgb(hexcolor):
    h = str(hexcolor).lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float64)


def _curva(puntos, color, grosor=3.0):
    """VMobject suave a partir de un array (n, 2) o (n, 3) de escena."""
    pts = np.asarray(puntos, dtype=np.float64)
    if pts.shape[1] == 2:
        pts = np.column_stack([pts, np.zeros(len(pts))])
    curva = VMobject(color=color, stroke_width=grosor)
    curva.set_points_smoothly(pts)
    return curva


def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Etiqueta tecnica corta en la tipografia de telemetria de la marca."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _centro_plano(plano):
    """Origen de un PlanoIQ (o de cualquier mobject que haga de plano)."""
    obtener = getattr(plano, "centro", None)
    return np.asarray(obtener() if callable(obtener) else plano.get_center(),
                      dtype=np.float64)


def _suave(ruido, ventana):
    """Media movil circular sobre el ultimo eje: ruido sin picos de un pixel."""
    ventana = int(max(1, ventana))
    if ventana <= 1:
        return ruido
    nucleo = np.ones(ventana) / ventana
    return np.apply_along_axis(
        lambda fila: np.convolve(np.r_[fila[-ventana:], fila, fila[:ventana]],
                                 nucleo, mode="same")[ventana:-ventana],
        -1, ruido)


# --- plano IQ y fasor -------------------------------------------------
class PlanoIQ(VGroup):
    """Ejes I/Q con circulo unitario punteado (lo devuelve `plano_iq`).

    `.radio_u` y `.punto()` se calculan sobre la geometria ACTUAL, asi que
    siguen siendo validos despues de mover o escalar el plano.
    """

    @property
    def radio_u(self):
        """Radio del circulo unitario en unidades de escena (float)."""
        return float(self.circulo.width) / 2.0

    def centro(self):
        """Origen del plano (el cruce de los ejes) en coordenadas de escena.

        NO es `get_center()`: las etiquetas "I" y "Q" desbalancean la caja
        del grupo y la desplazarian unas centesimas. Se lee del circulo, que
        siempre esta centrado en el origen del plano.
        """
        return np.asarray(self.circulo.get_center(), dtype=np.float64)

    def punto(self, angulo, r=1.0):
        """Coordenada de escena del punto (r, angulo) del plano complejo."""
        radio = self.radio_u * float(r)
        return self.centro() + np.array(
            [radio * np.cos(float(angulo)), radio * np.sin(float(angulo)), 0.0])


def plano_iq(radio=1.7, color=COLOR_EJE, font_size=16):
    """Plano complejo I (horizontal) / Q (vertical) con circulo unitario.

    Los ejes sobresalen un poco del circulo para que las etiquetas "I" y "Q"
    no se apoyen sobre el trazo punteado. El grupo se centra en ORIGIN: para
    colocarlo, `.move_to(...)` normal.
    """
    radio = float(max(0.2, radio))
    largo = radio * 1.22

    eje_i = Line((-largo, 0, 0), (largo, 0, 0), stroke_width=2.4, color=color)
    eje_q = Line((0, -largo, 0), (0, largo, 0), stroke_width=2.4, color=color)
    circulo = DashedVMobject(
        Circle(radius=radio, stroke_width=2.0, color=color), num_dashes=52)
    circulo.set_stroke(opacity=0.75)

    etiqueta_i = _texto_hud("I", font_size=font_size, color=color)
    etiqueta_i.next_to(eje_i.get_end(), 0.5 * np.array([0.0, -1.0, 0.0]),
                       buff=0.16)
    etiqueta_q = _texto_hud("Q", font_size=font_size, color=color)
    etiqueta_q.next_to(eje_q.get_end(), np.array([1.0, 0.0, 0.0]), buff=0.16)
    for etiqueta in (etiqueta_i, etiqueta_q):
        etiqueta.set_opacity(0.9)

    plano = PlanoIQ(eje_i, eje_q, circulo, etiqueta_i, etiqueta_q)
    plano.eje_i, plano.eje_q, plano.circulo = eje_i, eje_q, circulo
    plano.etiqueta_i, plano.etiqueta_q = etiqueta_i, etiqueta_q
    return plano


class Fasor(VGroup):
    """Flecha desde el centro del plano + punto brillante en la punta."""

    def punta(self):
        """Coordenada de escena de la punta, leida del propio mobject."""
        return self.brillo.get_center()


def fasor(plano, angulo=0.0, r=1.0, color=COLOR_SENAL):
    """Flecha del centro de `plano` al punto (r, angulo) del plano complejo.

    La cabeza se dibuja a mano (dos segmentos) en vez de con Arrow: al girar
    el fasor con `girar_fasor` la punta rota rigidamente con el resto, sin
    los reajustes de tamaño que Arrow hace en cada transformacion.
    """
    angulo = float(angulo)
    origen = _centro_plano(plano)
    destino = plano.punto(angulo, r)
    largo = float(np.linalg.norm(destino - origen))

    tallo = Line(origen, destino, stroke_width=4.0, color=color)
    cabeza = VGroup()
    if largo > 1e-6:
        u = (destino - origen) / largo
        n = np.array([-u[1], u[0], 0.0])
        lado = min(0.22, largo * 0.32)
        for signo in (1.0, -1.0):
            base = destino - u * lado + n * signo * lado * 0.45
            cabeza.add(Line(base, destino, stroke_width=4.0, color=color))
    brillo = Dot(destino, radius=0.06, color=color, fill_opacity=1.0)

    f = Fasor(tallo, cabeza, brillo)
    f.tallo, f.cabeza, f.brillo = tallo, cabeza, brillo
    f.plano = plano
    f.angulo = angulo
    f.r = float(r)
    return f


class GirarFasor(Animation):
    """Gira un `Fasor` alrededor del centro de su plano (ver `girar_fasor`).

    Rota el grupo entero por incrementos alrededor del centro del plano
    capturado al empezar: el tallo nunca se despega del origen. Al terminar
    deja `.angulo` exactamente en `hasta`.
    """

    def __init__(self, fasor_, hasta, **kwargs):
        self.hasta = float(hasta)
        kwargs.setdefault("rate_func", linear)
        super().__init__(fasor_, **kwargs)

    def begin(self):
        plano = getattr(self.mobject, "plano", None)
        self.centro = (_centro_plano(plano) if plano is not None
                       else np.asarray(self.mobject.get_start()))
        self.desde = float(getattr(self.mobject, "angulo", 0.0))
        self._actual = self.desde
        super().begin()

    def interpolate_mobject(self, alpha):
        objetivo = self.desde + (self.hasta - self.desde) * self.rate_func(alpha)
        delta = objetivo - self._actual
        if abs(delta) > 1e-12:
            self.mobject.rotate(delta, about_point=self.centro)
            self._actual = objetivo
        self.mobject.angulo = objetivo

    def finish(self):
        super().finish()
        self.mobject.angulo = self.hasta


def girar_fasor(fasor_, hasta, run_time=2.0):
    """Animation que lleva el fasor de su angulo actual a `hasta` (radianes).

    El signo de la diferencia da el sentido: `hasta` mayor gira antihorario
    (frecuencia positiva, encima de la sintonia) y menor, horario.
    """
    return GirarFasor(fasor_, hasta, run_time=float(run_time))


# --- ondas ------------------------------------------------------------
def onda_senoidal(ancho=4.4, alto=0.5, ciclos=3.0, fase=0.0,
                  color=COLOR_SENAL, muestras=0):
    """Senoidal centrada en ORIGIN, con puntitos de muestreo opcionales.

    `alto` es el pico a pico: la onda va de -alto/2 a +alto/2. Con
    `muestras>0` se añaden esa cantidad de Dots equiespaciados EN LA CURVA
    (el clip del muestreo IQ los usa para contar).
    """
    ancho, alto = float(ancho), float(alto)
    ciclos, fase = float(ciclos), float(fase)

    def y(t):
        return (alto / 2.0) * np.sin(2.0 * np.pi * ciclos * t + fase)

    t = np.linspace(0.0, 1.0, _MUESTRAS_CURVA)
    xs = (t - 0.5) * ancho
    curva = _curva(np.column_stack([xs, y(t)]), color)

    puntos = VGroup()
    n = int(max(0, muestras))
    if n > 0:
        tm = np.linspace(0.0, 1.0, n)
        for tk in tm:
            puntos.add(Dot(np.array([(tk - 0.5) * ancho, y(tk), 0.0]),
                           radius=0.045, color=color, fill_opacity=1.0))

    onda = VGroup(curva, puntos)
    onda.curva, onda.puntos = curva, puntos
    return onda


def onda_am(ancho=5.6, alto=1.1, ciclos_portadora=26.0, ciclos_mensaje=2.0,
            indice=0.55, color=COLOR_SENAL, color_envolvente=COLOR_I):
    """Portadora modulada en amplitud + su envolvente superior.

    La envolvente (el mensaje) es cian porque es lo que se quiere recuperar;
    la portadora es ambar como toda señal. `indice` es el indice de
    modulacion clasico: 0 no modula, 1 llega a tocar el cero.
    """
    ancho, alto = float(ancho), float(alto)
    indice = float(np.clip(indice, 0.0, 1.0))
    pico = alto / 2.0

    t = np.linspace(0.0, 1.0, _MUESTRAS_CURVA)
    xs = (t - 0.5) * ancho
    mensaje = np.sin(2.0 * np.pi * float(ciclos_mensaje) * t)
    env = pico * (1.0 + indice * mensaje) / (1.0 + indice)
    portadora_y = env * np.sin(2.0 * np.pi * float(ciclos_portadora) * t)

    portadora = _curva(np.column_stack([xs, portadora_y]), color, grosor=2.4)
    envolvente = _curva(np.column_stack([xs, env]), color_envolvente,
                        grosor=3.0)

    onda = VGroup(portadora, envolvente)
    onda.portadora, onda.envolvente = portadora, envolvente
    return onda


def onda_fm(ancho=5.6, alto=1.1, ciclos_base=18.0, desviacion=0.65,
            ciclos_mensaje=1.5, color=COLOR_Q):
    """Onda de frecuencia instantanea variable: apretada donde el mensaje sube.

    La fase es la integral de la frecuencia instantanea
    f(t) = ciclos_base * (1 + desviacion * sin(2 pi ciclos_mensaje t)), asi
    que la onda es continua (nada de saltos de fase en los cambios).
    """
    ancho, alto = float(ancho), float(alto)
    base = float(ciclos_base)
    desv = float(desviacion)
    cm = max(_EPS, float(ciclos_mensaje))

    t = np.linspace(0.0, 1.0, _MUESTRAS_CURVA)
    xs = (t - 0.5) * ancho
    # integral de sin(2 pi cm t) dt = (1 - cos(2 pi cm t)) / (2 pi cm)
    integral = (1.0 - np.cos(2.0 * np.pi * cm * t)) / (2.0 * np.pi * cm)
    fase = 2.0 * np.pi * base * (t + desv * integral)
    ys = (alto / 2.0) * np.sin(fase)

    curva = _curva(np.column_stack([xs, ys]), color, grosor=2.6)
    onda = VGroup(curva)
    onda.onda = curva
    return onda


def flujo_en_bloques(ancho=6.6, alto=0.65, bloques=5, ciclos=11.0,
                     color=COLOR_SENAL, color_corte=COLOR_EJE):
    """Onda continua cortada en `bloques` por lineas verticales punteadas.

    Es el flujo de muestras que la FFT trocea: cada tramo entre cortes es un
    bloque de N muestras.
    """
    ancho, alto = float(ancho), float(alto)
    n = int(max(1, bloques))

    onda_v = onda_senoidal(ancho=ancho, alto=alto, ciclos=float(ciclos),
                           color=color)
    curva = onda_v.curva

    cortes = VGroup()
    medio = alto * 0.85
    for k in range(1, n):
        x = (k / n - 0.5) * ancho
        corte = DashedVMobject(
            Line((x, -medio, 0), (x, medio, 0), stroke_width=2.0,
                 color=color_corte), num_dashes=9)
        cortes.add(corte)

    flujo = VGroup(curva, cortes)
    flujo.onda, flujo.cortes = curva, cortes
    return flujo


# --- espectro ---------------------------------------------------------
class VentanaEspectro(VGroup):
    """Ventana de frecuencia con sintonia al centro (la crea
    `ventana_espectro`). `.x_de()` y `.base_y` leen la geometria ACTUAL."""

    @property
    def base_y(self):
        """Altura (y de escena) del eje de frecuencia, en float."""
        return float(self.eje.get_center()[1])

    def x_de(self, f_rel):
        """x de escena de la frecuencia relativa `f_rel` en [-1, 1]."""
        izquierda = float(self.eje.get_left()[0])
        return izquierda + (float(f_rel) + 1.0) / 2.0 * float(self.eje.width)


def ventana_espectro(ancho=6.8, alto=2.3, color=COLOR_EJE, font_size=15):
    """Eje de frecuencia con la banda [-fs/2, +fs/2] sombreada y rotulada.

    f_rel = -1 es -fs/2, 0 la sintonia (marca punteada) y +1 el +fs/2. Todo
    lo que se dibuje dentro se coloca con `.x_de()` y `.base_y`.
    """
    ancho, alto = float(ancho), float(alto)
    medio = ancho / 2.0
    base = -alto / 2.0

    zona = Rectangle(width=ancho, height=alto, stroke_width=0)
    zona.set_fill(color=color, opacity=0.16)
    zona.move_to((0, 0, 0))

    eje = Line((-medio, base, 0), (medio, base, 0), stroke_width=2.6,
               color=color)
    bordes = VGroup(*[
        Line((s * medio, base, 0), (s * medio, alto / 2.0, 0),
             stroke_width=2.0, color=color).set_stroke(opacity=0.65)
        for s in (-1.0, 1.0)])
    sintonia = DashedVMobject(
        Line((0, base, 0), (0, alto / 2.0, 0), stroke_width=2.0, color=color),
        num_dashes=11)
    sintonia.set_stroke(opacity=0.85)

    etiquetas = VGroup()
    for f_rel, texto in ((-1.0, "-fs/2"), (0.0, "sintonia"), (1.0, "+fs/2")):
        t = _texto_hud(texto, font_size=font_size, color=color)
        t.set_opacity(0.95)
        t.move_to((f_rel * medio, base - 0.26, 0))
        etiquetas.add(t)
    # Las de los extremos se meten hacia dentro para no salirse del cuadro.
    etiquetas[0].shift(np.array([0.30, 0.0, 0.0]))
    etiquetas[2].shift(np.array([-0.30, 0.0, 0.0]))

    v = VentanaEspectro(zona, eje, bordes, sintonia, etiquetas)
    v.zona, v.eje, v.bordes = zona, eje, bordes
    v.sintonia, v.etiquetas = sintonia, etiquetas
    return v


def pico_espectral(ventana, f_rel=0.0, altura=1.5, ancho_rel=0.06,
                   color=COLOR_SENAL):
    """Campana gaussiana apoyada en el eje de `ventana`, centrada en `f_rel`.

    `ancho_rel` es la sigma medida en unidades de f_rel. Al moverse con
    `.move_to([ventana.x_de(f), pico.get_center()[1], 0])` conserva la
    altura, que es lo que se anima en el clip del aliasing.
    """
    altura = float(altura)
    sigma_f = max(1e-3, float(ancho_rel))
    escala = float(ventana.eje.width) / 2.0     # unidades de escena por f_rel

    u = np.linspace(-3.4, 3.4, 121)
    ys = altura * np.exp(-0.5 * u * u)
    xs = ventana.x_de(f_rel) + u * sigma_f * escala
    base_y = ventana.base_y

    pico = VMobject(color=color, stroke_width=3.0)
    pico.set_points_smoothly(
        [np.array([x, base_y + y, 0.0]) for x, y in zip(xs, ys)])
    pico.add_line_to(np.array([xs[-1], base_y, 0.0]))
    pico.add_line_to(np.array([xs[0], base_y, 0.0]))
    pico.set_fill(color=color, opacity=0.22)
    return pico


def barras_espectro(alturas, ancho=2.9, alto=1.8, color=COLOR_SENAL,
                    separacion_rel=0.25):
    """Espectro de barras: linea base + una barra por valor de `alturas`.

    `alturas` son valores en [0, 1] (se recortan). `separacion_rel` es el
    hueco entre barras como fraccion del paso, asi que 5 barras salen anchas
    y 20 finas sin tocar ningun otro parametro.
    """
    valores = np.clip(np.asarray(list(alturas), dtype=np.float64).ravel(),
                      0.0, 1.0)
    ancho, alto = float(ancho), float(alto)
    n = max(1, valores.size)
    paso = ancho / n
    ancho_barra = paso * (1.0 - float(np.clip(separacion_rel, 0.0, 0.9)))
    base = -alto / 2.0

    linea = Line((-ancho / 2.0, base, 0), (ancho / 2.0, base, 0),
                 stroke_width=2.4, color=COLOR_EJE)

    barras = VGroup()
    for k, v in enumerate(valores):
        h = max(0.012, float(v) * alto)
        x = -ancho / 2.0 + paso * (k + 0.5)
        barra = Rectangle(width=ancho_barra, height=h, stroke_width=0)
        barra.set_fill(color=color, opacity=0.9)
        barra.move_to((x, base + h / 2.0, 0))
        barras.add(barra)

    grupo = VGroup(linea, barras)
    grupo.linea, grupo.barras = linea, barras
    return grupo


# --- waterfall (raster) -----------------------------------------------
# Colormap del waterfall: negro de marca -> azul de fondo -> violeta ->
# ambar -> blanco. Los dos primeros tramos se comen todo el ruido de fondo
# (que vive en ~0.10-0.30), asi que el fondo queda azul oscuro y solo las
# señales entran en el tramo caliente.
_PARADAS_WATERFALL = ((0.00, "#05070a"), (0.30, "#0b2038"),
                      (0.55, "#6d3f8f"), (0.80, "#f59e0b"), (1.00, "#ffffff"))


def _colormap(p):
    """Malla de potencia en [0, 1] -> RGB uint8 (filas, columnas, 3)."""
    puntos = np.array([x for x, _ in _PARADAS_WATERFALL])
    colores = np.stack([_hex_a_rgb(c) for _, c in _PARADAS_WATERFALL])
    p = np.clip(p, 0.0, 1.0)
    rgb = np.stack([np.interp(p, puntos, colores[:, k]) for k in range(3)],
                   axis=-1)
    return np.clip(rgb, 0, 255).astype(np.uint8)


def _potencia_waterfall(columnas, filas, semilla):
    """Malla (filas, columnas) de potencia con las 4 firmas del curso.

    Fila 0 = arriba = lo mas reciente; la frecuencia cruza de -1 a +1. Las
    firmas son gaussianas en frecuencia con la amplitud modulada en tiempo,
    que es exactamente como se ven en un waterfall real.
    """
    rng = np.random.default_rng(int(semilla))
    f = np.linspace(-1.0, 1.0, columnas)[None, :]
    t = np.linspace(0.0, 1.0, filas)[:, None]

    # Ruido de fondo: gaussiano suavizado en frecuencia, con una ondulacion
    # lenta que imita el rizado del filtro de entrada.
    fondo = _suave(rng.normal(0.0, 1.0, (filas, columnas)), 5)
    p = 0.17 + 0.055 * fondo / (np.std(fondo) + _EPS) * 0.6
    p += 0.03 * np.sin(2.6 * f + 0.8) * np.ones_like(t)

    def gauss(centro, sigma):
        return np.exp(-0.5 * ((f - centro) / sigma) ** 2)

    # 1. CW: portadora fina e inmovil en -0.55, con centelleo minimo.
    p += (0.78 + 0.06 * rng.normal(0.0, 1.0, (filas, 1))) * gauss(-0.55, 0.012)

    # 2. FM ancha: banda plana en -0.12 +- 0.10 con textura interna.
    plana = np.exp(-((f + 0.12) / 0.10) ** 8)
    textura = _suave(rng.normal(0.0, 1.0, (filas, columnas)), 7)
    textura = textura / (np.std(textura) + _EPS)
    p += plana * (0.52 + 0.16 * textura + 0.06 * np.sin(9.0 * np.pi * t))

    # 3. AFSK: rafagas cortas e intermitentes en +0.32 (dos tonos juntos).
    rafaga = np.zeros((filas, 1))
    fila = 3
    while fila < filas:
        largo = int(rng.integers(3, 7))
        rafaga[fila:fila + largo, 0] = 1.0
        fila += largo + int(rng.integers(5, 12))
    tono = gauss(0.315, 0.011) + gauss(0.345, 0.011)
    p += 0.72 * rafaga * tono

    # 4. Doppler: traza inclinada de +0.72 (arriba) a +0.38 (abajo); a media
    #    altura pasa por +0.55, que es donde el clip la señala.
    centro = 0.72 + (0.38 - 0.72) * t
    p += 0.80 * np.exp(-0.5 * ((f - centro) / 0.014) ** 2)

    return np.clip(p, 0.0, 1.0)


class WaterfallImagen(ImageMobject):
    """Waterfall raster con localizador de firmas (lo crea `waterfall_imagen`).

    `.pos_de()` se calcula con el centro y el tamaño ACTUALES del mobject:
    si el waterfall se mueve o se escala, los recuadros que se cuelguen de el
    siguen cayendo sobre la firma correcta.
    """

    def pos_de(self, f_rel, t_rel):
        """Coordenada de escena de (f_rel en [-1,1], t_rel en [0,1] arriba->abajo)."""
        centro = self.get_center()
        return centro + np.array([
            float(np.clip(f_rel, -1.0, 1.0)) * float(self.width) / 2.0,
            (0.5 - float(np.clip(t_rel, 0.0, 1.0))) * float(self.height),
            0.0])


def waterfall_imagen(ancho=6.2, alto=3.3, columnas=220, filas=120, semilla=7):
    """Waterfall sintetico con portadora CW, FM ancha, rafagas AFSK y Doppler.

    Es un `ImageMobject`: en las escenas va en `Group`, JAMAS en `VGroup`.
    Firmas (f_rel, t_rel de 0 arriba a 1 abajo):
        CW       linea vertical fina en f_rel = -0.55
        FM       banda con textura centrada en -0.12, semiancho ~0.10
        AFSK     rafagas intermitentes cortas en +0.32
        Doppler  traza de (+0.72, 0) a (+0.38, 1), cruzando +0.55 a t=0.5
    """
    columnas = int(max(16, columnas))
    filas = int(max(16, filas))

    p = _potencia_waterfall(columnas, filas, semilla)
    rgba = np.empty((filas, columnas, 4), dtype=np.uint8)
    rgba[..., :3] = _colormap(p)
    rgba[..., 3] = 255

    img = WaterfallImagen(np.ascontiguousarray(rgba))
    img.stretch_to_fit_width(float(ancho))
    img.stretch_to_fit_height(float(alto))
    return img


# --- digital ----------------------------------------------------------
# El ruido de la constelacion se expresa RELATIVO a la separacion: sigma =
# ruido * separacion * _ESCALA_RUIDO. Calibrado para que con los valores del
# curso (separacion 1.05, puntos 26) ruido=0.06 de dos nubes limpias sin un
# solo error, y ruido=0.28 deje unas pocas muestras del otro lado de la
# frontera (3 con semilla=3), que es lo que el clip necesita señalar.
_ESCALA_RUIDO = 2.0
# Las colas gaussianas se truncan a esta cantidad de sigmas: sin el truncado
# una muestra suelta se va a media pantalla y rompe la composicion del clip.
# 2.2 sigma sigue dejando cruzar la frontera (hace falta 1.79 sigma), asi que
# no cambia la cuenta de errados.
_SIGMAS_MAX = 2.2
# Radio maximo (en unidades del plano) al que puede quedar una muestra:
# apenas mas alla de donde llega la frontera de decision dibujada (1.15),
# para que todo punto se lea como parte de la constelacion y no como
# basura suelta en la escena.
_RADIO_MAX = 1.38


def constelacion_bpsk(plano, separacion=1.05, ruido=0.06, puntos=26,
                      semilla=3, color_uno=COLOR_I, color_cero=COLOR_Q):
    """Dos nubes BPSK sobre `plano`, en +I (uno) y -I (cero).

    `separacion` va en unidades del plano (1 = radio del circulo unitario).
    `.errados` son los Dots cuya componente I quedo del lado contrario a su
    nube: los bits que el receptor decide mal.
    """
    n = int(puntos)
    if n > PUNTOS_MAX:
        raise ValueError(
            f"constelacion_bpsk: puntos={n} supera PUNTOS_MAX={PUNTOS_MAX}")
    n = max(2, n)

    separacion = float(separacion)
    sigma = abs(float(ruido)) * abs(separacion) * _ESCALA_RUIDO
    rng = np.random.default_rng(int(semilla))

    n_uno = n // 2
    n_cero = n - n_uno
    centro = _centro_plano(plano)
    radio_u = plano.radio_u

    nube_uno, nube_cero, errados = VGroup(), VGroup(), []
    for signo, cuantos, grupo, color in ((1.0, n_uno, nube_uno, color_uno),
                                         (-1.0, n_cero, nube_cero, color_cero)):
        tope = sigma * _SIGMAS_MAX
        ruido_i = np.clip(rng.normal(0.0, sigma, cuantos), -tope, tope)
        ruido_q = np.clip(rng.normal(0.0, sigma, cuantos), -tope, tope)
        iq = np.column_stack([signo * separacion + ruido_i, ruido_q])
        # Recorte radial: el clip por sigma acota el ruido, pero el punto
        # final (centro de nube + ruido) aun podia caer a >2 radios del
        # plano y se veia flotando en el vacio. Se reescala hacia el
        # centro conservando el signo de I (los .errados no cambian).
        radios = np.linalg.norm(iq, axis=1)
        exceso = radios > _RADIO_MAX
        iq[exceso] *= (_RADIO_MAX / radios[exceso])[:, None]
        for i_val, q_val in iq:
            pos = centro + np.array([i_val * radio_u, q_val * radio_u, 0.0])
            d = Dot(pos, radius=0.055, color=color, fill_opacity=1.0)
            d.set_z_index(3)
            grupo.add(d)
            if i_val * signo <= 0.0:      # cruzo la frontera I = 0
                errados.append(d)

    c = VGroup(nube_uno, nube_cero)
    c.nube_uno, c.nube_cero = nube_uno, nube_cero
    c.errados = errados
    c.plano = plano
    return c


class CurvaAcantilado(VGroup):
    """Curva de errores contra SNR (la crea `curva_acantilado`)."""

    def _y_rel(self, x_rel):
        """Errores normalizados en [0, 1] para la SNR relativa `x_rel`."""
        x = float(np.clip(x_rel, 0.0, 1.0))
        return float(1.0 / (1.0 + np.exp((x - self.umbral_rel) * self.dureza)))

    def punto_en(self, x_rel):
        """Coordenada de escena del punto de la curva en `x_rel` de [0, 1]."""
        origen = self.eje_x.get_start()
        return np.asarray(origen, dtype=np.float64) + np.array([
            float(np.clip(x_rel, 0.0, 1.0)) * float(self.eje_x.width),
            self._y_rel(x_rel) * float(self.eje_y.height),
            0.0])


def curva_acantilado(ancho=3.2, alto=2.2, umbral_rel=0.45, color=COLOR_SENAL):
    """Ejes minimos (SNR ->, errores ^) + curva que se desploma en el umbral.

    La curva es una logistica decreciente: casi plana arriba a la izquierda
    (todo son errores), caida brusca alrededor de `umbral_rel` y suelo casi
    perfecto a la derecha. El efecto acantilado del enlace digital.
    """
    ancho, alto = float(ancho), float(alto)
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    eje_x = Line(origen, origen + np.array([ancho, 0.0, 0.0]),
                 stroke_width=2.4, color=COLOR_EJE)
    eje_y = Line(origen, origen + np.array([0.0, alto, 0.0]),
                 stroke_width=2.4, color=COLOR_EJE)
    ejes = VGroup(eje_x, eje_y)

    c = CurvaAcantilado(ejes)
    c.ejes, c.eje_x, c.eje_y = ejes, eje_x, eje_y
    c.umbral_rel = float(np.clip(umbral_rel, 0.05, 0.95))
    c.dureza = 15.0

    xs = np.linspace(0.0, 1.0, 121)
    curva = _curva(np.array([c.punto_en(x)[:2] for x in xs]), color,
                   grosor=3.2)
    c.add(curva)
    c.curva = curva
    return c


def diagrama_ojo(ancho=4.8, alto=2.5, trazas=22, ruido=0.05, semilla=5,
                 color=COLOR_SENAL):
    """Trazas de 2 simbolos superpuestas: el ojo del enlace digital.

    Cada traza es una secuencia de bits pseudoaleatorios con transiciones de
    coseno alzado, mas ruido de amplitud suave y jitter de reloj, ambos
    proporcionales a `ruido`. Con ruido~0.05 el ojo esta abierto de par en
    par; con ~0.30 se cierra (el ruido tapa la abertura y el jitter come el
    ancho). Determinista via `semilla`.
    """
    n = int(trazas)
    if n > TRAZAS_MAX:
        raise ValueError(
            f"diagrama_ojo: trazas={n} supera TRAZAS_MAX={TRAZAS_MAX}")
    n = max(1, n)

    ancho, alto = float(ancho), float(alto)
    ruido = abs(float(ruido))
    rng = np.random.default_rng(int(semilla))

    t = np.linspace(0.0, 2.0, 121)          # dos simbolos de ancho
    ancho_transicion = 0.34                 # coseno alzado entre simbolos
    escala_y = (alto / 2.0) * 0.86

    grupo_trazas = VGroup()
    for _ in range(n):
        # bits del simbolo anterior, los dos visibles y el siguiente
        bits = rng.integers(0, 2, 4) * 2.0 - 1.0
        jitter = rng.normal(0.0, ruido * 0.55, 3)   # reloj de cada frontera

        # bits[0] es el simbolo anterior a la ventana y bits[3] el siguiente:
        # por eso las transiciones de los bordes (t=0 y t=2) se ven a medias,
        # como en un ojo real.
        centros = np.array([0.0, 1.0, 2.0]) + jitter
        v = np.where(t < centros[1], bits[1], bits[2]).astype(np.float64)
        v[t < centros[0] - ancho_transicion] = bits[0]
        v[t > centros[2] + ancho_transicion] = bits[3]
        for k, c0 in enumerate(centros):
            anterior, siguiente = bits[k], bits[k + 1]
            if anterior == siguiente:
                continue
            u = (t - c0) / ancho_transicion
            dentro = np.abs(u) <= 1.0
            suave = 0.5 * (1.0 - np.cos(np.pi * (u[dentro] + 1.0) / 2.0))
            v[dentro] = anterior + (siguiente - anterior) * suave

        # ruido de amplitud SUAVE: gaussiano grueso interpolado, para que la
        # traza ondule como una señal analogica y no tiemble pixel a pixel.
        grueso = rng.normal(0.0, 1.0, 14)
        v = v + ruido * 1.5 * np.interp(t, np.linspace(0.0, 2.0, 14), grueso)

        # El recorte mantiene el diagrama dentro del `alto` declarado: sin el,
        # con ruido 0.30 alguna traza se sale un 40% y pisa lo que tenga al
        # lado en la escena.
        xs = (t / 2.0 - 0.5) * ancho
        traza = _curva(np.column_stack([xs, np.clip(v, -1.35, 1.35) * escala_y]),
                       color, grosor=1.8)
        traza.set_stroke(opacity=0.55)
        grupo_trazas.add(traza)

    ojo = VGroup(grupo_trazas)
    ojo.trazas = grupo_trazas
    return ojo
