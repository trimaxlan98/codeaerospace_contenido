"""Apuntamiento y seguimiento de satelites: vista polar, TLE, Doppler y lazo.

Pensado para el curso "Apuntar a un satelite: el arte del seguimiento". Todo
el calculo es numpy puro y determinista (`np.random.default_rng(semilla)` si
alguna pieza necesitara azar; hoy ninguna lo necesita): mismo script -> mismo
render, condicion necesaria para trabajar con `--disable_caching`. Nada de
red, nada de disco.

La regla de color del curso: el SATELITE es ambar, la ANTENA cian, el CIELO
violeta, lo que FALLA rojo, lo LOGRADO verde; los anillos, ejes y mascaras en
el gris azulado `COLOR_EJE`. No mezclar roles.

Piezas:
    boveda      vista polar (az/el), mascara de elevacion, traza de pase,
                cono del keyhole
    montura     icono de antena Az/El orientable y aguja de velocidad
    TLE         tarjeta con las dos lineas y sus campos resaltables
    Doppler     la S del pase con su linea f0
    lazo        curvas de referencia y de antena con su rezago

Las piezas que exponen localizadores (`.punto`, `.punto_en`, `.brecha_en`,
`.pivote`) los calculan sobre la geometria ACTUAL del mobject: siguen siendo
validos despues de mover o escalar. Asi los clips cuelgan flechas, tags y
puntos sin adivinar coordenadas.

El mapa raster se REUSA de `satelites.py` (`imagen_mapa`, `puntos_en_mapa`,
`traza_terrestre`): en las escenas va siempre dentro de un `Group`, nunca de
un `VGroup`.

Tope duro para no castigar el VPS (2 vCPU / 2 GB por render): `MUESTRAS_MAX`
levanta ValueError (a diferencia de fractales.py, que recorta en silencio:
aqui pasarse cambia lo que se ve, y es mejor enterarse).

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from apuntado import vista_polar, traza_pase, antena

    vista = vista_polar(radio=2.3)
    traza = traza_pase(vista, el_max=70, az_culminacion=25)
    ant = antena(escala=0.9).to_edge(RIGHT)
    self.add(vista, traza, ant)
    ant.orientar(traza.el_en(0.5))
"""

import numpy as np

from manim import (Annulus, Arc, AnnularSector, Circle, DashedVMobject, Dot,
                   Line, Polygon, RoundedRectangle, Text, VGroup, VMobject)

from code_brand import CODE_INK, CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limite duro: pasarse levanta ValueError (ver docstring del modulo).
MUESTRAS_MAX = 400      # muestras maximas de una curva parametrica

# Paleta propia de la libreria (coincide con la del curso).
COLOR_SAT = "#f59e0b"       # EL SATELITE: su traza, su señal, su Doppler
COLOR_ANTENA = "#22d3ee"    # LA ANTENA: la montura y lo que la antena hace
COLOR_CIELO = "#a78bfa"     # EL CIELO: vista polar, mapa, referencias
COLOR_PELIGRO = "#f43f5e"   # keyhole, error de apuntamiento, saturacion
COLOR_OK = "#34d399"        # enganche, ventana util, pase logrado
COLOR_EJE = "#31414f"       # mobiliario: anillos, ejes, mascaras

# Alias cortos con los nombres de la tabla de paleta del curso, para que el
# style_block de los clips pueda escribir `color=C_SAT` tal cual.
C_SAT, C_ANTENA, C_CIELO = COLOR_SAT, COLOR_ANTENA, COLOR_CIELO
C_PELIGRO, C_OK, C_EJE = COLOR_PELIGRO, COLOR_OK, COLOR_EJE

_EPS = 1e-9

# Las dos lineas TLE de la leccion (valores didacticos de la ISS: 51.64° de
# inclinacion y 15.5 vueltas al dia). Las columnas son las del formato real,
# de ahi que los campos se recorten por numero de columna.
TLE_NOMBRE = "ISS (ZARYA)"
TLE_LINEA_1 = ("1 25544U 98067A   26210.54791667  .00016717  "
               "00000-0  10270-3 0  9007")
TLE_LINEA_2 = ("2 25544  51.6416 247.4627 0006703 130.5360 "
               "325.0288 15.50000000 12345")

# Campos resaltables: (linea, columna inicial, columna final), ambas
# inclusivas y 1-based, tal cual las define el formato TLE.
_CAMPOS_TLE = {
    "epoca": (1, 19, 32),
    "inclinacion": (2, 9, 16),
    "raan": (2, 18, 25),
    "excentricidad": (2, 27, 33),
    "movimiento_medio": (2, 53, 63),
}


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=15, color=COLOR_EJE):
    """Etiqueta tecnica corta en la tipografia de telemetria de la marca."""
    registrar_fuentes()
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=color)


def _curva(puntos, color, grosor=3.0):
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


def _glifos(mobjeto):
    """Submobjects con trazo de un Text: un glifo por caracter NO espacio.

    El style_block de los cursos sombrea `Text` para tirar los glifos vacios
    (los espacios, que en Manim 0.20.1 se quedan anclados donde nacio el
    texto e inflan la caja). Filtrando aqui por `has_points()` la cuenta sale
    igual con la sombra y sin ella: la lista siempre corresponde, en orden, a
    los caracteres no-espacio de la cadena.
    """
    return [s for s in mobjeto.submobjects if s.has_points()]


def _rango_columnas(cadena, mobjeto, col_ini, col_fin):
    """VGroup con los glifos de `cadena` entre dos columnas (1-based, incl.).

    Los espacios del rango no aportan glifo (ni en el borde ni dentro), asi
    que un campo TLE declarado con su columna oficial resalta exactamente sus
    digitos, ni uno mas ni uno menos.
    """
    glifos = _glifos(mobjeto)
    inicio = sum(1 for c in cadena[:col_ini - 1] if not c.isspace())
    cuantos = sum(1 for c in cadena[col_ini - 1:col_fin] if not c.isspace())
    return VGroup(*glifos[inicio:inicio + cuantos])


# --- la boveda del cielo ----------------------------------------------
class VistaPolar(VGroup):
    """Boveda celeste en proyeccion polar equidistante (la crea `vista_polar`).

    El centro es el CENIT (el = 90) y el anillo exterior el HORIZONTE
    (el = 0): la distancia al centro es lineal en la elevacion, que es la
    convencion de cualquier carta de pases. El norte va arriba y el este a la
    derecha, con el acimut creciendo en sentido HORARIO (N -> E -> S -> W).

    `.radio_u` y `.punto()` leen la geometria ACTUAL, asi que siguen siendo
    validos despues de mover o escalar la vista.
    """

    @property
    def radio_u(self):
        """Radio del horizonte en unidades de escena (float)."""
        return float(self.horizonte.width) / 2.0

    def centro(self):
        """Cenit de la vista en coordenadas de escena.

        NO es `get_center()`: las etiquetas de los puntos cardinales
        desbalancean la caja del grupo. Se lee del anillo del horizonte, que
        siempre esta centrado en el cenit.
        """
        return np.asarray(self.horizonte.get_center(), dtype=np.float64)

    def punto(self, az_deg, el_deg):
        """Coordenada de escena del punto (acimut, elevacion), en grados.

        Proyeccion equidistante: r = radio_u * (90 - el) / 90 y direccion de
        escena 90 - az (asi az=0 cae arriba/N y az=90 a la derecha/E).
        """
        el = float(np.clip(el_deg, 0.0, 90.0))
        r = self.radio_u * (90.0 - el) / 90.0
        ang = np.deg2rad(90.0 - float(az_deg))
        return self.centro() + np.array([r * np.cos(ang), r * np.sin(ang), 0.0])


def vista_polar(radio=2.5, color=COLOR_EJE, font_size=15):
    """Carta polar del cielo: horizonte, 30°, 60°, cenit y los cardinales.

    Tres anillos concentricos (el = 0, 30 y 60) con las cruces N/E/S/W. Las
    etiquetas de grados van sobre la diagonal NE, que es la unica direccion
    libre de cruces, para que nunca se encimen con los cardinales. Las
    etiquetas usan el gris de telemetria de la marca (el gris de `color` es
    demasiado oscuro para leerse sobre el fondo casi negro).

    El grupo se centra en ORIGIN: para colocarlo, `.move_to(...)` normal.
    """
    radio = float(max(0.4, radio))

    def r_de(el):
        return radio * (90.0 - el) / 90.0

    horizonte = Circle(radius=radio, stroke_width=2.6, color=color)
    anillo_30 = Circle(radius=r_de(30.0), stroke_width=1.8, color=color)
    anillo_60 = Circle(radius=r_de(60.0), stroke_width=1.8, color=color)
    for anillo in (anillo_30, anillo_60):
        anillo.set_stroke(opacity=0.75)
    anillos = VGroup(horizonte, anillo_30, anillo_60)

    cruces = VGroup()
    for az in (0.0, 90.0, 180.0, 270.0):
        ang = np.deg2rad(90.0 - az)
        fuera = np.array([radio * np.cos(ang), radio * np.sin(ang), 0.0])
        cruces.add(Line((0, 0, 0), fuera, stroke_width=1.6, color=color)
                   .set_stroke(opacity=0.55))

    cardinales = VGroup()
    for az, nombre in ((0.0, "N"), (90.0, "E"), (180.0, "S"), (270.0, "W")):
        ang = np.deg2rad(90.0 - az)
        fuera = np.array([np.cos(ang), np.sin(ang), 0.0])
        etiqueta = _texto_hud(nombre, font_size=font_size + 1, color=CODE_MUTED)
        etiqueta.move_to(fuera * (radio + 0.24))
        cardinales.add(etiqueta)

    grados = VGroup()
    for el in (30.0, 60.0):
        ang = np.deg2rad(90.0 - 45.0)          # diagonal NE, libre de cruces
        # Un pelo por fuera del anillo: encima del trazo la cifra se lee mal.
        pos = np.array([np.cos(ang), np.sin(ang), 0.0]) * (r_de(el) + 0.16)
        etiqueta = _texto_hud(f"{int(el)}°", font_size=font_size - 1,
                              color=CODE_MUTED)
        etiqueta.set_opacity(0.8)
        etiqueta.move_to(pos)
        grados.add(etiqueta)

    vista = VistaPolar(anillos, cruces, cardinales, grados)
    vista.anillos, vista.cruces = anillos, cruces
    vista.horizonte = horizonte
    vista.anillo_30, vista.anillo_60 = anillo_30, anillo_60
    vista.cardinales, vista.grados = cardinales, grados
    return vista


def mascara_elevacion(vista, el_min=8.0, color=COLOR_EJE):
    """Anillo sombreado entre el horizonte y `el_min` sobre `vista`.

    Es la franja donde la estacion NO declara visibilidad: arboles,
    edificios y demasiada atmosfera. Translucido (0.25) para que la traza de
    un pase se siga leyendo por debajo.
    """
    radio_u = vista.radio_u
    el_min = float(np.clip(el_min, 0.0, 89.0))
    interior = radio_u * (90.0 - el_min) / 90.0

    mascara = Annulus(inner_radius=interior, outer_radius=radio_u,
                      color=color, stroke_width=1.2)
    mascara.set_fill(color=color, opacity=0.25)
    mascara.set_stroke(color=color, opacity=0.7)
    mascara.move_to(vista.centro())
    return mascara


class TrazaPase(VMobject):
    """Pase LEO sobre la vista polar (lo crea `traza_pase`).

    En proyeccion equidistante un pase real es casi una CUERDA RECTA: entra
    por el horizonte, culmina a `el_max` sobre `az_culminacion` y sale por el
    punto simetrico. Basta y es estable (nada de propagar SGP4 en un clip).

    `t` recorre la cuerda de forma UNIFORME en [0, 1], y `.el_en()` /
    `.az_en()` se derivan de la posicion leyendo la geometria ACTUAL de la
    traza y de su vista: si ambas se mueven juntas, los angulos no cambian.
    """

    def punto_en(self, t):
        """Coordenada de escena del punto de la traza en `t` de [0, 1]."""
        t = float(np.clip(t, 0.0, 1.0))
        inicio = np.asarray(self.get_start(), dtype=np.float64)
        fin = np.asarray(self.get_end(), dtype=np.float64)
        return inicio + (fin - inicio) * t

    def el_en(self, t):
        """Elevacion (grados) del punto de la traza en `t`."""
        d = np.linalg.norm(self.punto_en(t) - self.vista.centro())
        radio_u = max(_EPS, self.vista.radio_u)
        return float(np.clip(90.0 * (1.0 - d / radio_u), 0.0, 90.0))

    def az_en(self, t):
        """Acimut (grados, 0 = N, 90 = E) del punto de la traza en `t`."""
        d = self.punto_en(t) - self.vista.centro()
        if float(np.linalg.norm(d)) < _EPS:
            return 0.0
        return float(np.rad2deg(np.arctan2(d[0], d[1])) % 360.0)


def traza_pase(vista, el_max=45.0, az_culminacion=20.0, muestras=120,
               color=COLOR_SAT):
    """Traza de un pase sobre `vista`: horizonte -> culminacion -> horizonte.

    La cuerda pasa a r_min = radio_u * (90 - el_max) / 90 del cenit sobre el
    acimut `az_culminacion` y corta el horizonte en los dos extremos. El
    sentido del recorrido (t creciente) es el que deja la culminacion a mano
    derecha del avance, o sea el pase "de izquierda a derecha" visto desde el
    lado de la culminacion.
    """
    muestras = _validar_muestras("traza_pase", muestras)
    radio_u = vista.radio_u
    el_max = float(np.clip(el_max, 1.0, 89.5))
    r_min = radio_u * (90.0 - el_max) / 90.0
    semicuerda = float(np.sqrt(max(_EPS, radio_u ** 2 - r_min ** 2)))

    ang = np.deg2rad(90.0 - float(az_culminacion))
    normal = np.array([np.cos(ang), np.sin(ang), 0.0])       # hacia la culminacion
    avance = np.array([-normal[1], normal[0], 0.0])          # perpendicular

    centro = vista.centro()
    t = np.linspace(0.0, 1.0, muestras)[:, None]
    puntos = (centro + r_min * normal) + (2.0 * t - 1.0) * semicuerda * avance

    traza = TrazaPase(color=color, stroke_width=3.4)
    traza.set_points_smoothly(puntos)
    traza.vista = vista
    traza.el_max = el_max
    traza.az_culminacion = float(az_culminacion)
    return traza


def cono_keyhole(vista, radio_deg=8.0, color=COLOR_PELIGRO):
    """Circulo translucido en el cenit de `vista`: la zona ciega de la montura.

    `radio_deg` es el semiangulo del cono medido desde el cenit, asi que en
    la carta polar es un circulo de radio radio_u * radio_deg / 90.
    """
    radio_deg = float(np.clip(radio_deg, 0.5, 89.0))
    cono = Circle(radius=vista.radio_u * radio_deg / 90.0, color=color,
                  stroke_width=1.6)
    cono.set_fill(color=color, opacity=0.25)
    cono.set_stroke(color=color, opacity=0.85)
    cono.move_to(vista.centro())
    return cono


# --- la montura -------------------------------------------------------
class Antena(VGroup):
    """Icono 2D de montura Az/El orientable (la crea `antena`).

    `.orientar(deg)` gira SOLO el plato alrededor del pivote (la punta del
    mastil): 0 = mirando al horizonte derecho, 90 = cenit. El pivote se lee
    de la geometria ACTUAL, asi que la antena se puede mover o escalar y el
    plato sigue girando sobre su montura.
    """

    @property
    def pivote(self):
        """Punto de giro del plato (punta del mastil) en coordenadas de escena."""
        return np.asarray(self.mastil.get_top(), dtype=np.float64)

    def orientar(self, deg):
        """Deja el plato apuntando a `deg` grados de elevacion (0 = horizonte).

        Gira por la DIFERENCIA con el angulo actual, no en absoluto: llamarla
        dos veces con el mismo valor no mueve nada, y un updater puede
        llamarla en cada frame sin acumular error.
        """
        objetivo = float(deg)
        delta = objetivo - float(self.angulo)
        if abs(delta) > 1e-9:
            self.plato.rotate(np.deg2rad(delta), about_point=self.pivote)
        self.angulo = objetivo
        return self


def antena(escala=1.0, color=COLOR_ANTENA):
    """Montura Az/El de perfil: base trapezoidal, mastil, plato y alimentador.

    Dibujada para leerse pequeña (en los clips va a ~0.9): trazos gruesos,
    pocas piezas y el plato como arco ABIERTO con su alimentador, que es lo
    que da la lectura instantanea de "antena". Nace apuntando al horizonte
    derecho (`.angulo` = 0); usar `.orientar()` para elevarla.
    """
    escala = float(max(0.05, escala))

    base = Polygon((-0.45, 0.0, 0.0), (0.45, 0.0, 0.0),
                   (0.26, 0.30, 0.0), (-0.26, 0.30, 0.0),
                   color=color, stroke_width=3.0)
    base.set_fill(color=color, opacity=0.18)

    # El mastil termina EXACTAMENTE en el pivote (y = 1.0): `.pivote` lo lee
    # con get_top(), asi que el plato gira sobre su vertice sin desviarse.
    mastil = Line((0.0, 0.28, 0.0), (0.0, 1.00, 0.0), stroke_width=5.0,
                  color=color)
    # La horquilla va un pelo por DEBAJO del pivote: asi sostiene el plato sin
    # asomar por delante cuando el plato esta elevado.
    horquilla = Line((-0.11, 0.94, 0.0), (0.11, 0.94, 0.0), stroke_width=4.0,
                     color=color)

    # El plato se construye centrado en su foco y se corre para que su VERTICE
    # (el fondo del arco) quede sobre el pivote. Montado por detras, el plato
    # gira de 0 a 90 grados sin que el mastil le cruce nunca la boca; el
    # alimentador sale siempre hacia donde apunta.
    radio_plato = 0.55
    apertura = 122.0                       # el arco va de 122° a 238°
    arco = Arc(radius=radio_plato, start_angle=np.deg2rad(apertura),
               angle=np.deg2rad(2.0 * (180.0 - apertura)), color=color,
               stroke_width=4.4)
    alimentador = Line((-radio_plato, 0.0, 0.0), (0.0, 0.0, 0.0),
                       stroke_width=2.6, color=color)
    foco = Dot((0.0, 0.0, 0.0), radius=0.045, color=color, fill_opacity=1.0)
    plato = VGroup(arco, alimentador, foco)
    plato.shift(np.array([radio_plato, 1.00, 0.0]))

    ant = Antena(base, mastil, horquilla, plato)
    ant.base, ant.mastil, ant.plato = base, mastil, plato
    ant.horquilla = horquilla
    ant.arco, ant.alimentador, ant.foco = arco, alimentador, foco
    ant.angulo = 0.0
    ant.scale(escala, about_point=np.array([0.0, 0.0, 0.0]))
    ant.move_to((0, 0, 0))
    return ant


class AgujaVelocidad(VGroup):
    """Indicador semicircular de velocidad de giro (lo crea `aguja_velocidad`).

    Convencion angular: el valor 0 esta a la IZQUIERDA (pi radianes) y el
    maximo a la DERECHA (0 radianes), como cualquier tacometro. `.a_valor()`
    devuelve el angulo ABSOLUTO al que debe quedar la aguja, y `.angulo` el
    que tiene ahora, de modo que animar es siempre:

        medidor.play(Rotate(medidor.aguja,
                            medidor.a_valor(9.0) - medidor.angulo,
                            about_point=medidor.pivote))

    `.pivote`, `.angulo` y `.valor` se leen de la geometria ACTUAL: valen
    despues de mover, escalar o rotar la aguja con cualquier animacion.
    """

    @property
    def pivote(self):
        """Centro de giro de la aguja en coordenadas de escena (np.array)."""
        return np.asarray(self.arco.get_arc_center(), dtype=np.float64)

    @property
    def angulo(self):
        """Angulo actual de la aguja en radianes (0 = maximo, pi = cero)."""
        d = np.asarray(self.aguja.get_end(), dtype=np.float64) - self.pivote
        return float(np.arctan2(d[1], d[0]))

    @property
    def valor(self):
        """Valor que marca la aguja ahora mismo, leido de su angulo."""
        return float(np.clip(self.maximo * (1.0 - self.angulo / np.pi),
                             0.0, self.maximo))

    def a_valor(self, v):
        """Angulo absoluto (radianes) al que debe quedar la aguja para `v`."""
        frac = float(np.clip(float(v) / max(_EPS, self.maximo), 0.0, 1.0))
        return float(np.pi * (1.0 - frac))

    def en_peligro(self, v=None):
        """¿El valor (o el actual) cae en la zona roja del indicador?"""
        actual = self.valor if v is None else float(v)
        return bool(actual >= self.umbral_peligro * self.maximo)


def aguja_velocidad(maximo=10.0, valor=0.5, ancho=2.4, color=COLOR_ANTENA,
                    color_peligro=COLOR_PELIGRO):
    """Tacometro semicircular "grados/s" con zona roja sobre el 75%.

    Es el indicador del keyhole: cerca del cenit la demanda de acimut se
    dispara y la aguja se va al sector rojo, donde la montura ya no puede
    seguir. El grupo se centra en ORIGIN.
    """
    maximo = float(max(_EPS, maximo))
    radio = float(max(0.4, ancho)) / 2.0
    umbral = 0.75

    arco = Arc(radius=radio, start_angle=0.0, angle=np.pi, color=COLOR_EJE,
               stroke_width=3.0)
    base = Line((-radio, 0.0, 0.0), (radio, 0.0, 0.0), stroke_width=2.4,
                color=COLOR_EJE)

    zona = AnnularSector(inner_radius=radio * 0.78, outer_radius=radio,
                         angle=np.pi * (1.0 - umbral), start_angle=0.0,
                         color=color_peligro, stroke_width=0)
    zona.set_fill(color=color_peligro, opacity=0.32)

    marcas = VGroup()
    for k in range(6):
        ang = np.pi * (1.0 - k / 5.0)
        u = np.array([np.cos(ang), np.sin(ang), 0.0])
        marcas.add(Line(u * radio * 0.86, u * radio, stroke_width=2.2,
                        color=COLOR_EJE))

    etiquetas = VGroup()
    for texto, ang in (("0", np.pi), (f"{maximo:g}", 0.0)):
        u = np.array([np.cos(ang), np.sin(ang), 0.0])
        t = _texto_hud(texto, font_size=14, color=CODE_MUTED)
        t.set_opacity(0.85)
        t.move_to(u * (radio + 0.22))
        etiquetas.add(t)
    unidad = _texto_hud("°/s", font_size=14, color=CODE_MUTED)
    unidad.set_opacity(0.85)
    unidad.move_to(np.array([0.0, radio * 0.30, 0.0]))
    etiquetas.add(unidad)

    ang0 = np.pi * (1.0 - float(np.clip(valor / maximo, 0.0, 1.0)))
    # La aguja llega hasta dentro del anillo de marcas (0.78 R): asi, en la
    # zona roja, la punta queda claramente DENTRO del sector, no rozandolo.
    aguja = Line((0.0, 0.0, 0.0),
                 np.array([np.cos(ang0), np.sin(ang0), 0.0]) * radio * 0.90,
                 stroke_width=4.4, color=color)
    eje = Dot((0.0, 0.0, 0.0), radius=0.055, color=color, fill_opacity=1.0)

    medidor = AgujaVelocidad(arco, base, zona, marcas, etiquetas, aguja, eje)
    medidor.arco, medidor.base, medidor.zona = arco, base, zona
    medidor.marcas, medidor.etiquetas = marcas, etiquetas
    medidor.aguja, medidor.eje = aguja, eje
    medidor.maximo = maximo
    medidor.umbral_peligro = umbral
    return medidor


# --- el TLE -----------------------------------------------------------
def tarjeta_tle(font_size=15):
    """Caja oscura con las tres lineas del TLE de la ISS y sus campos.

    `.campos` es un dict de VGroups de glifos listos para `Indicate` o
    `set_color`: "epoca", "inclinacion", "raan", "excentricidad" y
    "movimiento_medio". Cada uno se recorta por las COLUMNAS oficiales del
    formato TLE, de modo que resalta el numero completo y nada mas.
    """
    registrar_fuentes()
    cuerpo = [TLE_LINEA_1, TLE_LINEA_2]

    nombre = Text(TLE_NOMBRE, font=FUENTE_HUD, font_size=font_size + 1,
                  color=COLOR_SAT)
    lineas = [Text(txt, font=FUENTE_HUD, font_size=font_size, color=CODE_INK)
              for txt in cuerpo]
    for linea in lineas:
        linea.set_opacity(0.92)

    texto = VGroup(nombre, *lineas)
    texto.arrange(np.array([0.0, -1.0, 0.0]), buff=0.18, aligned_edge=
                  np.array([-1.0, 0.0, 0.0]))

    caja = RoundedRectangle(corner_radius=0.12,
                            width=float(texto.width) + 0.52,
                            height=float(texto.height) + 0.46,
                            stroke_width=1.8, color=COLOR_EJE)
    caja.set_fill(color="#0a1119", opacity=0.92)
    caja.move_to(texto.get_center())

    campos = {}
    for nombre_campo, (num_linea, col_ini, col_fin) in _CAMPOS_TLE.items():
        campos[nombre_campo] = _rango_columnas(
            cuerpo[num_linea - 1], lineas[num_linea - 1], col_ini, col_fin)

    tarjeta = VGroup(caja, texto)
    tarjeta.caja, tarjeta.texto = caja, texto
    tarjeta.nombre, tarjeta.lineas = nombre, VGroup(*lineas)
    tarjeta.campos = campos
    return tarjeta


# --- el Doppler -------------------------------------------------------
class CurvaS(VGroup):
    """La S del Doppler de un pase (la crea `curva_s_doppler`).

    `.punto_en()` cae SOBRE la curva dibujada y se calcula con el origen y el
    tamaño ACTUALES de los ejes: sirve igual antes y despues de mover o
    escalar el grupo.
    """

    def _y_rel(self, t_rel):
        """Altura normalizada de la curva en `t_rel` de [0, 1].

        Va de 0.94 (AOS) a 0.06 (LOS) y no de 1 a 0: los extremos de la S se
        despegan del eje del tiempo y del borde superior, que si no se leen
        como si la curva estuviera recortada.
        """
        u = 2.0 * float(np.clip(t_rel, 0.0, 1.0)) - 1.0
        amplitud = 0.44
        return float(0.5 - amplitud * np.tanh(self.dureza * u) /
                     np.tanh(self.dureza))

    def punto_en(self, t_rel):
        """Coordenada de escena del punto de la S en `t_rel` de [0, 1]."""
        origen = np.asarray(self.eje_t.get_start(), dtype=np.float64)
        return origen + np.array([
            float(np.clip(t_rel, 0.0, 1.0)) * float(self.eje_t.width),
            self._y_rel(t_rel) * float(self.eje_f.height),
            0.0])


def curva_s_doppler(ancho=5.4, alto=2.6, color=COLOR_SAT,
                    color_ejes=COLOR_EJE, font_size=15):
    """Ejes minimos + linea f0 punteada + la S del Doppler del pase.

    Alta en el AOS (el satelite se acerca y la frecuencia llega comprimida),
    cruza f0 en la maxima aproximacion y cae en el LOS: una tanh invertida.
    El grupo se centra en ORIGIN.
    """
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    eje_t = Line(origen, origen + np.array([ancho, 0.0, 0.0]),
                 stroke_width=2.4, color=color_ejes)
    eje_f = Line(origen, origen + np.array([0.0, alto, 0.0]),
                 stroke_width=2.4, color=color_ejes)
    ejes = VGroup(eje_t, eje_f)

    s = CurvaS(ejes)
    s.ejes, s.eje_t, s.eje_f = ejes, eje_t, eje_f
    s.dureza = 2.2

    linea_f0 = DashedVMobject(
        Line(origen + np.array([0.0, alto / 2.0, 0.0]),
             origen + np.array([ancho, alto / 2.0, 0.0]),
             stroke_width=2.0, color=color_ejes), num_dashes=26)
    linea_f0.set_stroke(opacity=0.85)

    ts = np.linspace(0.0, 1.0, 121)
    curva = _curva(np.array([s.punto_en(t) for t in ts]), color, grosor=3.4)

    etiqueta_f0 = _texto_hud("f0", font_size=font_size, color=color_ejes)
    etiqueta_f0.set_opacity(0.95)
    etiqueta_f0.move_to(origen + np.array([ancho - 0.22, alto / 2.0 + 0.22,
                                           0.0]))
    etiqueta_t = _texto_hud("t", font_size=font_size, color=color_ejes)
    etiqueta_t.move_to(origen + np.array([ancho + 0.02, -0.24, 0.0]))
    etiqueta_f = _texto_hud("f", font_size=font_size, color=color_ejes)
    etiqueta_f.move_to(origen + np.array([-0.26, alto - 0.02, 0.0]))
    etiquetas = VGroup(etiqueta_f0, etiqueta_t, etiqueta_f)

    s.add(linea_f0, curva, etiquetas)
    s.linea_f0, s.curva, s.etiquetas = linea_f0, curva, etiquetas
    return s


# --- el lazo de seguimiento -------------------------------------------
class Seguimiento(VGroup):
    """Referencia y antena contra el tiempo (lo crea `curvas_seguimiento`).

    La referencia es la rampa de acimut de un pase (lenta, rapida al pasar
    por la culminacion, lenta otra vez) y la antena es la MISMA rampa
    evaluada `retraso` mas tarde: un rezago constante, que es lo que un lazo
    proporcional deja sin corregir. Con `retraso=0` las dos coinciden punto
    por punto.

    `.brecha_en()` devuelve las dos posiciones de escena leyendo la geometria
    ACTUAL de los ejes.
    """

    def _y_rel(self, t_rel):
        """Rampa suave (sigmoide de acimut del pase) normalizada.

        Va de 0.06 a 0.94 y no de 0 a 1: los extremos se despegan del eje del
        tiempo y del borde superior, que si no se leen como recortados.
        """
        t = float(np.clip(t_rel, 0.0, 1.0))
        k = self.dureza
        lo = 1.0 / (1.0 + np.exp(k * 0.5))
        hi = 1.0 / (1.0 + np.exp(-k * 0.5))
        s = (1.0 / (1.0 + np.exp(-k * (t - 0.5))) - lo) / (hi - lo)
        return float(0.06 + 0.88 * s)

    def _punto(self, t_rel, y_rel):
        origen = np.asarray(self.eje_t.get_start(), dtype=np.float64)
        return origen + np.array([
            float(np.clip(t_rel, 0.0, 1.0)) * float(self.eje_t.width),
            float(np.clip(y_rel, 0.0, 1.0)) * float(self.eje_a.height),
            0.0])

    def punto_ref(self, t_rel):
        """Punto de escena de la curva de REFERENCIA en `t_rel` de [0, 1]."""
        return self._punto(t_rel, self._y_rel(t_rel))

    def punto_ant(self, t_rel):
        """Punto de escena de la curva de la ANTENA en `t_rel` de [0, 1]."""
        return self._punto(t_rel, self._y_rel(float(t_rel) - self.retraso))

    def brecha_en(self, t_rel):
        """(punto_ref, punto_ant) en `t_rel`: los dos extremos del error."""
        return self.punto_ref(t_rel), self.punto_ant(t_rel)


def curvas_seguimiento(ancho=5.6, alto=2.4, retraso=0.16, muestras=140,
                       color_ref=COLOR_SAT, color_ant=COLOR_ANTENA):
    """Ejes minimos + rampa de referencia + rampa de la antena rezagada.

    `retraso` va en unidades de t (el eje completo es 1.0), asi que 0.16 es
    un rezago del 16% del pase. La curva de la antena se recorta al dominio:
    antes de `retraso` se queda en el valor inicial, que es exactamente lo
    que hace una montura que todavia no arranco. El grupo se centra en
    ORIGIN.
    """
    muestras = _validar_muestras("curvas_seguimiento", muestras)
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    eje_t = Line(origen, origen + np.array([ancho, 0.0, 0.0]),
                 stroke_width=2.4, color=COLOR_EJE)
    eje_a = Line(origen, origen + np.array([0.0, alto, 0.0]),
                 stroke_width=2.4, color=COLOR_EJE)
    ejes = VGroup(eje_t, eje_a)

    seg = Seguimiento(ejes)
    seg.ejes, seg.eje_t, seg.eje_a = ejes, eje_t, eje_a
    seg.dureza = 8.0
    seg.retraso = float(retraso)

    ts = np.linspace(0.0, 1.0, muestras)
    ref = _curva(np.array([seg.punto_ref(t) for t in ts]), color_ref,
                 grosor=3.4)
    ant = _curva(np.array([seg.punto_ant(t) for t in ts]), color_ant,
                 grosor=3.4)

    etiqueta_t = _texto_hud("t", font_size=15, color=COLOR_EJE)
    etiqueta_t.move_to(origen + np.array([ancho + 0.02, -0.24, 0.0]))
    etiqueta_a = _texto_hud("ang", font_size=15, color=COLOR_EJE)
    etiqueta_a.move_to(origen + np.array([-0.34, alto - 0.02, 0.0]))
    etiquetas = VGroup(etiqueta_t, etiqueta_a)

    seg.add(ref, ant, etiquetas)
    seg.ref, seg.ant, seg.etiquetas = ref, ant, etiquetas
    return seg
