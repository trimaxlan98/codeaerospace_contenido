"""El espectro radioelectrico: mapa de bandas, propagacion, orbitas y arbitro.

Pensado para el curso "El espectro: la guerra invisible por las ondas". Todo
el calculo es numpy puro y determinista (`np.random.default_rng(semilla)`
donde hace falta azar, hoy solo el campo de gotas): mismo script -> mismo
render, condicion necesaria para trabajar con `--disable_caching`. Nada de
red, nada de disco.

La regla de color del curso: la ONDA/banda es ambar, el GSO cian, el NGSO
violeta, la PERDIDA (lluvia, absorcion, interferencia) roja, la VENTANA (o la
coexistencia lograda) verde; ejes, anillos y mobiliario en el gris azulado
`COLOR_EJE`. No mezclar roles.

Piezas:
    barra_bandas        el mapa de UHF a Q/V en escala log de frecuencia
    curva_gases         absorcion gaseosa: pico de H2O en 22, muro de O2 en 60
    curva_lluvia        atenuacion especifica por lluvia a dos intensidades
    gotas_y_onda        onda contra un campo de gotas (larga vs comparable)
    tierra_y_anillos    disco terrestre + anillo GSO + anillo NGSO poblados
    haz                 cono translucido estacion -> satelite
    patron_antena       diagrama polar con lobulo principal y laterales
    linea_tiempo        hitos regulatorios rotulados sin encimarse

Las piezas que exponen localizadores (`.centro_de`, `.punto_de`, `.pos_gso`,
`.pos_ngso`, `.estacion`, `.direccion`, `.muesca`) los calculan sobre la
geometria ACTUAL del mobject: siguen siendo validos despues de mover o
escalar. Asi los clips cuelgan flechas, tags y puntos sin adivinar
coordenadas.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`BANDAS_MAX`, `SATS_MAX`, `HITOS_MAX` y `MUESTRAS_MAX` levantan ValueError (a
diferencia de fractales.py, que recorta en silencio: aqui pasarse cambia lo
que se ve, y es mejor enterarse).

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from espectro import barra_bandas, curva_gases, tierra_y_anillos

    barra = barra_bandas(ancho=6.8).move_to(UP * 1.3)
    self.play(Indicate(barra.segmento("Ka"), color=COLOR_ONDA))

    gases = curva_gases().move_to(DOWN * 0.2)
    self.add(Dot(gases.punto_de(60.0)))
    self.play(*gases.abrir_ventanas())
"""

import numpy as np

from manim import (Circle, DashedVMobject, Dot, Ellipse, Line, Polygon,
                   Rectangle, Text, VGroup, VMobject)

from code_brand import CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
BANDAS_MAX = 10         # segmentos en la barra del mapa de bandas
SATS_MAX = 48           # puntos de satelite por anillo
HITOS_MAX = 6           # muescas de la linea de tiempo
MUESTRAS_MAX = 400      # muestras maximas de una curva parametrica

# Paleta propia de la libreria (coincide con la del curso).
COLOR_ONDA = "#f59e0b"      # LA ONDA: el espectro util, las bandas
COLOR_GSO = "#22d3ee"       # EL GSO: lo establecido, la victima protegida
COLOR_NGSO = "#a78bfa"      # EL NGSO: las constelaciones, lo nuevo que llega
COLOR_PERDIDA = "#f43f5e"   # lluvia, absorcion, interferencia
COLOR_OK = "#34d399"        # ventana atmosferica, coexistencia lograda
COLOR_EJE = "#31414f"       # mobiliario: ejes, anillos, muescas

# Alias cortos con los nombres de la tabla de paleta del curso, para que el
# style_block de los clips pueda escribir `color=C_ONDA` tal cual.
C_ONDA, C_GSO, C_NGSO = COLOR_ONDA, COLOR_GSO, COLOR_NGSO
C_PERDIDA, C_OK, C_EJE = COLOR_PERDIDA, COLOR_OK, COLOR_EJE

# Colores de apoyo que no son roles narrativos.
COLOR_TIERRA = "#0b2038"    # relleno del disco terrestre (azul-gris oscuro)
COLOR_GOTA = "#7d93a8"      # las gotas de lluvia: azul-gris neutro

_EPS = 1e-9

# --- el mapa de bandas -------------------------------------------------
# Nombre y rango NOMINAL en GHz de las ocho bandas satelitales. Dos avisos
# sobre la tabla, porque la realidad no es una barra limpia:
#   * entre Ku (hasta 18) y Ka (desde 26.5) queda el hueco de la banda K,
#     inutilizable por la resonancia del vapor de agua en 22 GHz: la barra lo
#     dibuja como un tramo gris tenue SIN etiqueta, que es justamente lo que
#     hay que contar.
#   * Q/V arranca en 33 GHz en la realidad, o sea que Q SOLAPA a Ka. En una
#     barra segmentada dos tramos encimados se leen como un error de dibujo,
#     asi que el segmento se DIBUJA desde donde termina Ka (40 GHz) mientras
#     que su etiqueta conserva el rango nominal 33-75.
_BANDAS = (
    ("UHF", 0.3, 1.0),
    ("L", 1.0, 2.0),
    ("S", 2.0, 4.0),
    ("C", 4.0, 8.0),
    ("X", 8.0, 12.0),
    ("Ku", 12.0, 18.0),
    ("Ka", 26.5, 40.0),
    ("Q/V", 33.0, 75.0),
)

# --- atenuacion por lluvia --------------------------------------------
# Coeficientes k y alpha de la ley de potencia de la UIT (Rec. P.838,
# polarizacion horizontal) muestreados en frecuencia. Entre muestras se
# interpola log10(k) linealmente en log10(f) y alpha linealmente en log10(f):
# la curva resultante reproduce los valores de manual (a 60 mm/h da ~3 dB/km
# en 12 GHz y ~7 dB/km en 20 GHz) sin arrastrar la tabla completa.
_LLUVIA_F = np.array([1.0, 2.0, 4.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0, 25.0,
                      30.0, 35.0, 40.0, 50.0, 60.0, 80.0, 100.0])
_LLUVIA_K = np.array([2.59e-5, 8.47e-5, 1.071e-4, 6.50e-4, 4.115e-3, 1.217e-2,
                      2.386e-2, 4.481e-2, 9.164e-2, 1.571e-1, 2.403e-1,
                      3.374e-1, 4.431e-1, 6.433e-1, 8.206e-1, 1.0473,
                      1.1442])
_LLUVIA_A = np.array([0.9691, 1.0664, 1.6009, 1.4098, 1.3905, 1.2571, 1.1825,
                      1.1233, 1.0568, 0.9991, 0.9485, 0.9047, 0.8673, 0.8016,
                      0.7515, 0.6859, 0.6466])


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


def _punto(objeto):
    """Coordenada de escena de un punto o del centro de un mobject.

    Deja que los clips escriban `haz(estacion_dot, sat_dot)` sin desempaquetar
    a mano: cualquier cosa con `get_center()` vale como extremo.
    """
    if hasattr(objeto, "get_center"):
        return np.asarray(objeto.get_center(), dtype=np.float64)
    pt = np.asarray(objeto, dtype=np.float64).flatten()
    if pt.size == 2:
        pt = np.array([pt[0], pt[1], 0.0])
    return pt[:3].astype(np.float64)


def _unitario(deg):
    """Vector unitario de escena para `deg` (0 = derecha, antihorario)."""
    a = np.deg2rad(float(deg))
    return np.array([np.cos(a), np.sin(a), 0.0])


def _fmt_ghz(f):
    """Numero de frecuencia como se rotula en la barra: sin ceros de adorno."""
    return f"{f:g}"


# --- el mapa de bandas ------------------------------------------------
class BarraBandas(VGroup):
    """Mapa de bandas satelitales en escala log (la crea `barra_bandas`).

    Cada banda es un rectangulo que nace en una linea base comun y crece hacia
    ARRIBA con una altura proporcional (en log suave) a su ancho de banda
    tipico: la lectura instantanea es "subir en frecuencia ofrece mas sitio".

    `.segmento(nombre)` devuelve el VGroup del tramo (rectangulo + sus dos
    etiquetas) listo para `Indicate` o `set_color`, y `.centro_de(nombre)` /
    `.tope_de(nombre)` leen la geometria ACTUAL del rectangulo, asi que
    siguen valiendo despues de mover o escalar la barra.
    """

    def _buscar(self, nombre):
        clave = str(nombre).strip().upper()
        if clave not in self._indice:
            disponibles = ", ".join(self.nombres)
            raise ValueError(f"barra_bandas: banda '{nombre}' desconocida "
                             f"(hay: {disponibles})")
        return self._indice[clave]

    def segmento(self, nombre):
        """VGroup de la banda (rectangulo + etiquetas) para resaltar."""
        return self._buscar(nombre)["grupo"]

    def barra_de(self, nombre):
        """Solo el rectangulo de la banda, sin sus etiquetas."""
        return self._buscar(nombre)["barra"]

    def centro_de(self, nombre):
        """Centro de escena del rectangulo de la banda (np.array)."""
        return np.asarray(self._buscar(nombre)["barra"].get_center(),
                          dtype=np.float64)

    def tope_de(self, nombre):
        """Borde superior del rectangulo: de donde colgar una guia o un tag."""
        return np.asarray(self._buscar(nombre)["barra"].get_top(),
                          dtype=np.float64)


def _colocar_rangos(etiquetas, y_fila, salto, buff=0.07):
    """Baja a una segunda fila las etiquetas de rango que se encimarian.

    Recorre de izquierda a derecha con un tope por fila: la etiqueta que no
    entra despues de la anterior de su fila cae a la fila de abajo. Con la
    tabla por defecto no baja ninguna (todas caben), pero un `bandas`
    personalizado o un `font_size` grande no rompen la lectura.
    """
    derecho = {0: -1e9, 1: -1e9}
    for etiqueta in sorted(etiquetas, key=lambda m: float(m.get_x())):
        fila = 0 if float(etiqueta.get_left()[0]) >= derecho[0] + buff else 1
        etiqueta.set_y(y_fila - fila * salto)
        derecho[fila] = float(etiqueta.get_right()[0])


def barra_bandas(ancho=6.8, alto=0.8, font_size=15, bandas=None):
    """Barra segmentada con las 8 bandas satelitales en escala log.

    El eje horizontal es log10(f) de 0.3 a 75 GHz, asi que UHF (media decada)
    ocupa mas ancho que Ka pese a tener treinta veces menos espectro: es
    exactamente la asimetria que hay que contar. Las alturas van al reves
    (proporcionales al ancho de banda), de modo que la barra sube en escalera
    hacia la derecha.

    El hueco de la banda K (18-26.5 GHz, arruinada por el vapor de agua) se
    dibuja como un tramo gris tenue sin etiqueta. Los nombres van ENCIMA de
    cada tramo y el rango en GHz DEBAJO de la linea base, en un cuerpo menor y
    bajando a una segunda fila si alguno se encimaria con su vecino.

    `bandas` permite pasar una tabla propia de tuplas (nombre, f_ini, f_fin);
    por defecto usa las ocho del curso. Tope `BANDAS_MAX`. El grupo se centra
    en ORIGIN.
    """
    tabla = tuple(_BANDAS if bandas is None else bandas)
    if len(tabla) > BANDAS_MAX:
        raise ValueError(
            f"barra_bandas: {len(tabla)} bandas supera "
            f"BANDAS_MAX={BANDAS_MAX}")
    if not tabla:
        raise ValueError("barra_bandas: hace falta al menos una banda")

    ancho, alto = float(max(0.5, ancho)), float(max(0.2, alto))
    tabla = tuple(sorted(((str(n), float(a), float(b)) for n, a, b in tabla),
                         key=lambda t: t[1]))
    f_min = tabla[0][1]
    f_max = max(b for _, _, b in tabla)
    if f_min <= 0.0 or f_max <= f_min:
        raise ValueError("barra_bandas: rangos de frecuencia invalidos")

    u_min, u_max = np.log10(f_min), np.log10(f_max)
    escala_x = ancho / (u_max - u_min)

    def x_de(f):
        return (np.log10(float(f)) - u_min) * escala_x - ancho / 2.0

    # Alturas: log del ancho de banda nominal, remapeado a [0.42, 1.0] del
    # alto. El piso de 0.42 existe para que UHF (0.7 GHz contra los 42 de
    # Q/V) siga siendo un bloque legible y no una raya.
    anchos_banda = np.array([max(_EPS, b - a) for _, a, b in tabla])
    logs = np.log10(anchos_banda)
    span = float(logs.max() - logs.min())
    rel = (np.full(len(tabla), 1.0) if span < _EPS
           else 0.42 + 0.58 * (logs - logs.min()) / span)

    barras, huecos, nombres_txt, rangos_txt = VGroup(), VGroup(), [], []
    indice, orden = {}, []
    grupos = VGroup()
    dibujo_previo = None

    for (nombre, f_ini, f_fin), h_rel in zip(tabla, rel):
        ini = f_ini if dibujo_previo is None else max(f_ini, dibujo_previo)
        if ini >= f_fin:
            raise ValueError(f"barra_bandas: la banda '{nombre}' queda tapada "
                             f"por la anterior")
        # Hueco sin adjudicar (el caso real es la banda K): tramo gris tenue,
        # bajito y sin rotulo. Es el unico sitio de la barra que no se vende.
        if dibujo_previo is not None and ini > dibujo_previo + _EPS:
            x0, x1 = x_de(dibujo_previo), x_de(ini)
            hueco = Rectangle(width=x1 - x0, height=alto * 0.28,
                              stroke_width=1.0, color=COLOR_EJE)
            hueco.set_fill(color=COLOR_EJE, opacity=0.35)
            hueco.set_stroke(color=COLOR_EJE, opacity=0.6)
            hueco.move_to(np.array([(x0 + x1) / 2.0, alto * 0.14, 0.0]))
            huecos.add(hueco)

        x0, x1 = x_de(ini), x_de(f_fin)
        h = alto * float(h_rel)
        rect = Rectangle(width=x1 - x0, height=h, stroke_width=1.8,
                         color=COLOR_ONDA)
        rect.set_fill(color=COLOR_ONDA,
                      opacity=0.16 + 0.26 * (float(h_rel) - 0.42) / 0.58)
        rect.set_stroke(color=COLOR_ONDA, opacity=0.9)
        rect.move_to(np.array([(x0 + x1) / 2.0, h / 2.0, 0.0]))
        barras.add(rect)

        etiqueta = _texto_hud(nombre, font_size=font_size, color=COLOR_ONDA)
        etiqueta.move_to(np.array([(x0 + x1) / 2.0, h + 0.20, 0.0]))
        nombres_txt.append(etiqueta)

        rango = _texto_hud(f"{_fmt_ghz(f_ini)}-{_fmt_ghz(f_fin)}",
                           font_size=max(8, font_size - 4), color=CODE_MUTED)
        rango.set_opacity(0.9)
        rango.set_x((x0 + x1) / 2.0)
        rangos_txt.append(rango)

        grupo = VGroup(rect, etiqueta, rango)
        grupos.add(grupo)
        indice[nombre.upper()] = {"barra": rect, "grupo": grupo,
                                  "rango": (f_ini, f_fin)}
        orden.append(nombre)
        dibujo_previo = f_fin

    alto_rango = float(max(m.height for m in rangos_txt))
    _colocar_rangos(rangos_txt, -0.20 - alto_rango / 2.0, alto_rango + 0.09)

    base = Line(np.array([-ancho / 2.0, 0.0, 0.0]),
                np.array([ancho / 2.0, 0.0, 0.0]),
                stroke_width=2.2, color=COLOR_EJE)
    unidad = _texto_hud("GHz", font_size=max(8, font_size - 3),
                        color=CODE_MUTED)
    unidad.set_opacity(0.85)
    unidad.move_to(np.array([ancho / 2.0 + 0.30, -0.20 - alto_rango / 2.0,
                             0.0]))

    mapa = BarraBandas(base, huecos, grupos, unidad)
    mapa.base, mapa.huecos, mapa.barras = base, huecos, barras
    mapa.grupos, mapa.unidad = grupos, unidad
    mapa.nombres_txt = VGroup(*nombres_txt)
    mapa.rangos_txt = VGroup(*rangos_txt)
    mapa.nombres = tuple(orden)
    mapa._indice = indice
    # Centrado en la BARRA, no en la caja: el rotulo "GHz" cuelga por fuera
    # a la derecha y si contara para el centro dejaria la barra corrida.
    mapa.move_to(np.array([0.0, 0.0, 0.0]))
    mapa.shift(np.array([-float(base.get_center()[0]), 0.0, 0.0]))
    return mapa


# --- propagacion: los gases -------------------------------------------
class CurvaGases(VGroup):
    """Absorcion atmosferica contra frecuencia (la crea `curva_gases`).

    El eje x es log10(f) entre `f_min` y `f_max` GHz. El eje y es
    CUALITATIVO: la atenuacion real va de centesimas de dB/km en 1 GHz a 15
    dB/km en 60, cinco ordenes de magnitud que en escala lineal borrarian el
    pico de 22. La altura dibujada es la suma de un continuo que crece con la
    frecuencia mas dos resonancias gaussianas (H2O en 22.2 GHz, O2 en 60), o
    sea la forma que se lee en cualquier grafica log de la UIT.

    `.punto_de()` cae SOBRE la curva dibujada y se calcula con el origen y el
    tamaño ACTUALES de los ejes: sirve igual antes y despues de mover o
    escalar el grupo.
    """

    def _y_rel(self, f_ghz):
        """Altura normalizada [0, 1] de la curva en `f_ghz`."""
        u = np.log10(np.clip(float(f_ghz), self.f_min, self.f_max))
        continuo = 0.06 + 0.150 * (u - np.log10(self.f_min))
        h2o = 0.30 * np.exp(-((u - np.log10(22.2)) / 0.045) ** 2)
        o2 = 0.62 * np.exp(-((u - np.log10(60.0)) / 0.050) ** 2)
        return float(np.clip(continuo + h2o + o2, 0.0, 1.0))

    def _x_rel(self, f_ghz):
        """Posicion normalizada [0, 1] de `f_ghz` sobre el eje log."""
        u = np.log10(np.clip(float(f_ghz), self.f_min, self.f_max))
        return float((u - np.log10(self.f_min)) /
                     (np.log10(self.f_max) - np.log10(self.f_min)))

    def _en(self, x_rel, y_rel):
        origen = np.asarray(self.eje_x.get_start(), dtype=np.float64)
        return origen + np.array([float(x_rel) * float(self.eje_x.width),
                                  float(y_rel) * float(self.eje_y.height),
                                  0.0])

    def punto_de(self, f_ghz):
        """Coordenada de escena del punto de la curva en `f_ghz`."""
        return self._en(self._x_rel(f_ghz), self._y_rel(f_ghz))

    def base_de(self, f_ghz):
        """Coordenada de escena sobre el eje x (y = 0) en `f_ghz`."""
        return self._en(self._x_rel(f_ghz), 0.0)

    def abrir_ventanas(self):
        """Lista de animaciones que encienden las ventanas verdes.

        Las ventanas nacen en opacidad 0 y viven DENTRO del grupo (asi
        acompañan a la curva si el clip la mueve o la escala). Sobre un
        mobject ya invisible `FadeIn` no tiene nada que interpolar, de modo
        que el encendido va por `.animate`:

            self.play(*gases.abrir_ventanas(), run_time=0.8)
        """
        return [v.animate.set_fill(opacity=v.opacidad_llena)
                .set_stroke(opacity=v.opacidad_llena * 1.6)
                for v in self.ventanas]


def _ejes_xy(ancho, alto, color_ejes):
    """Par de ejes en L con el origen en la esquina inferior izquierda."""
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])
    eje_x = Line(origen, origen + np.array([ancho, 0.0, 0.0]),
                 stroke_width=2.4, color=color_ejes)
    eje_y = Line(origen, origen + np.array([0.0, alto, 0.0]),
                 stroke_width=2.4, color=color_ejes)
    return origen, eje_x, eje_y, VGroup(eje_x, eje_y)


def curva_gases(ancho=6.0, alto=2.6, color=COLOR_PERDIDA, color_ejes=COLOR_EJE,
                font_size=14, muestras=220):
    """Ejes log + curva de absorcion gaseosa + las dos ventanas atmosfericas.

    La curva sube despacio desde 1 GHz, levanta el pico moderado del vapor de
    agua en 22 GHz, cae a un valle en la treintena y choca contra el muro del
    oxigeno en 60 GHz, que domina toda la grafica; despues del muro vuelve a
    un nivel intermedio. `.ventanas` son las dos zonas verdes translucidas
    bajo la curva (10-20 y 26-50 GHz), donde viven las bandas comerciales:
    nacen invisibles y se encienden con `.abrir_ventanas()`.

    El grupo se centra en ORIGIN.
    """
    muestras = _validar_muestras("curva_gases", muestras)
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    origen, eje_x, eje_y, ejes = _ejes_xy(ancho, alto, color_ejes)

    g = CurvaGases(ejes)
    g.ejes, g.eje_x, g.eje_y = ejes, eje_x, eje_y
    g.f_min, g.f_max = 1.0, 100.0

    # Marcas de decada (con las intermedias en 2, 5, 20 y 50 sin rotulo: dan
    # la sensacion de escala log sin llenar el eje de cifras).
    marcas, rotulos = VGroup(), VGroup()
    for f, rotular in ((1.0, True), (2.0, False), (5.0, False), (10.0, True),
                       (20.0, False), (50.0, False), (100.0, True)):
        base = g.base_de(f)
        largo = 0.13 if rotular else 0.08
        marcas.add(Line(base, base + np.array([0.0, -largo, 0.0]),
                        stroke_width=1.8, color=color_ejes))
        if rotular:
            t = _texto_hud(_fmt_ghz(f), font_size=font_size, color=CODE_MUTED)
            t.set_opacity(0.9)
            t.move_to(base + np.array([0.0, -0.30, 0.0]))
            rotulos.add(t)

    # La unidad va a la DERECHA del ultimo rotulo, no a una distancia fija del
    # eje: con "100" en la ultima decada las dos cifras se tocarian.
    etiqueta_x = _texto_hud("GHz", font_size=font_size, color=CODE_MUTED)
    etiqueta_x.set_opacity(0.9)
    etiqueta_x.next_to(rotulos[-1], np.array([1.0, 0.0, 0.0]), buff=0.16)
    etiqueta_y = _texto_hud("dB/km", font_size=font_size, color=CODE_MUTED)
    etiqueta_y.set_opacity(0.9)
    etiqueta_y.move_to(origen + np.array([0.46, alto + 0.02, 0.0]))
    etiquetas = VGroup(rotulos, etiqueta_x, etiqueta_y)

    fs = np.logspace(np.log10(g.f_min), np.log10(g.f_max), muestras)
    curva = _curva(np.array([g.punto_de(f) for f in fs]), color, grosor=3.4)

    # Las ventanas se recortan CONTRA la curva (el borde superior es la propia
    # absorcion), no contra un rectangulo: asi se lee que la ventana es el
    # hueco que dejan las dos resonancias.
    ventanas = VGroup()
    for f_a, f_b in ((10.0, 20.0), (26.0, 50.0)):
        techo = np.logspace(np.log10(f_a), np.log10(f_b), 34)
        vertices = ([g.base_de(f_a)] + [g.punto_de(f) for f in techo] +
                    [g.base_de(f_b)])
        zona = Polygon(*vertices, color=COLOR_OK, stroke_width=1.4)
        zona.opacidad_llena = 0.24
        zona.set_fill(color=COLOR_OK, opacity=0.0)
        zona.set_stroke(color=COLOR_OK, opacity=0.0)
        ventanas.add(zona)

    g.add(marcas, etiquetas, ventanas, curva)
    g.marcas, g.rotulos, g.etiquetas = marcas, rotulos, etiquetas
    g.curva, g.ventanas = curva, ventanas
    return g


# --- propagacion: la lluvia -------------------------------------------
def _gamma_lluvia(f_ghz, tasa_mm_h):
    """Atenuacion especifica (dB/km) por la ley de potencia de la UIT."""
    u = np.log10(np.clip(float(f_ghz), _LLUVIA_F[0], _LLUVIA_F[-1]))
    us = np.log10(_LLUVIA_F)
    k = 10.0 ** float(np.interp(u, us, np.log10(_LLUVIA_K)))
    a = float(np.interp(u, us, _LLUVIA_A))
    return float(k * max(_EPS, float(tasa_mm_h)) ** a)


class CurvaLluvia(VGroup):
    """Atenuacion especifica por lluvia a dos intensidades (`curva_lluvia`).

    El eje x es LINEAL en GHz (a diferencia de `curva_gases`): lo que hay que
    ver es que la penalizacion se dispara al subir de banda, y en log-log las
    dos curvas se aplanarian en rectas paralelas sin dramatismo.

    `.punto_de(f, intensa=)` lee el origen y el tamaño ACTUALES de los ejes.
    """

    def _en(self, f_ghz, gamma):
        origen = np.asarray(self.eje_x.get_start(), dtype=np.float64)
        x = ((np.clip(float(f_ghz), self.f_min, self.f_max) - self.f_min) /
             (self.f_max - self.f_min))
        y = np.clip(float(gamma) / self.gamma_max, 0.0, 1.0)
        return origen + np.array([x * float(self.eje_x.width),
                                  y * float(self.eje_y.height), 0.0])

    def punto_de(self, f_ghz, intensa=True):
        """Coordenada de escena sobre la curva pedida en `f_ghz`."""
        tasa = self.tasa_intensa if intensa else self.tasa_suave
        return self._en(f_ghz, _gamma_lluvia(f_ghz, tasa))

    def db_km(self, f_ghz, intensa=True):
        """Valor de la curva en dB/km (para rotular sin inventar cifras)."""
        tasa = self.tasa_intensa if intensa else self.tasa_suave
        return _gamma_lluvia(f_ghz, tasa)


def curva_lluvia(ancho=5.6, alto=2.4, color=COLOR_PERDIDA,
                 color_ejes=COLOR_EJE, font_size=14, muestras=140):
    """Ejes + dos curvas de atenuacion por lluvia (20 y 60 mm/h).

    La tenue es una lluvia normal (20 mm/h) y la plena un aguacero tropical
    (60 mm/h); ambas siguen la ley de potencia de la UIT con los coeficientes
    tabulados del modulo, asi que los valores que un clip rotule sobre la
    curva (`.db_km`) son los de manual, no adornos. El grupo se centra en
    ORIGIN.
    """
    muestras = _validar_muestras("curva_lluvia", muestras)
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    origen, eje_x, eje_y, ejes = _ejes_xy(ancho, alto, color_ejes)

    c = CurvaLluvia(ejes)
    c.ejes, c.eje_x, c.eje_y = ejes, eje_x, eje_y
    c.f_min, c.f_max = 1.0, 50.0
    c.tasa_suave, c.tasa_intensa = 20.0, 60.0
    # Techo con un 8% de aire: la curva intensa no debe tocar el borde
    # superior, que si no se lee como recortada.
    c.gamma_max = _gamma_lluvia(c.f_max, c.tasa_intensa) * 1.08

    marcas, rotulos = VGroup(), VGroup()
    for f in (10.0, 20.0, 30.0, 40.0, 50.0):
        base = c._en(f, 0.0)
        marcas.add(Line(base, base + np.array([0.0, -0.12, 0.0]),
                        stroke_width=1.8, color=color_ejes))
        t = _texto_hud(_fmt_ghz(f), font_size=font_size, color=CODE_MUTED)
        t.set_opacity(0.9)
        t.move_to(base + np.array([0.0, -0.30, 0.0]))
        rotulos.add(t)

    etiqueta_x = _texto_hud("GHz", font_size=font_size, color=CODE_MUTED)
    etiqueta_x.set_opacity(0.9)
    etiqueta_x.next_to(rotulos[-1], np.array([1.0, 0.0, 0.0]), buff=0.16)
    etiqueta_y = _texto_hud("dB/km", font_size=font_size, color=CODE_MUTED)
    etiqueta_y.set_opacity(0.9)
    etiqueta_y.move_to(origen + np.array([0.46, alto + 0.02, 0.0]))
    etiquetas = VGroup(rotulos, etiqueta_x, etiqueta_y)

    fs = np.linspace(c.f_min, c.f_max, muestras)
    suave = _curva(np.array([c.punto_de(f, intensa=False) for f in fs]),
                   color, grosor=2.6)
    suave.set_stroke(opacity=0.45)
    intensa = _curva(np.array([c.punto_de(f, intensa=True) for f in fs]),
                     color, grosor=3.4)

    tag_suave = _texto_hud("20 mm/h", font_size=font_size, color=color)
    tag_suave.set_opacity(0.6)
    tag_suave.next_to(c.punto_de(c.f_max, intensa=False),
                      np.array([0.0, -1.0, 0.0]), buff=0.10)
    tag_intensa = _texto_hud("60 mm/h", font_size=font_size, color=color)
    tag_intensa.next_to(c.punto_de(c.f_max, intensa=True),
                        np.array([0.0, 1.0, 0.0]), buff=0.10)
    tags = VGroup(tag_suave, tag_intensa)

    c.add(marcas, etiquetas, suave, intensa, tags)
    c.marcas, c.rotulos, c.etiquetas = marcas, rotulos, etiquetas
    c.suave, c.intensa, c.tags = suave, intensa, tags
    return c


# --- propagacion: la gota contra la onda ------------------------------
def gotas_y_onda(lambda_rel=1.0, ancho=3.0, alto=1.6, color=COLOR_ONDA,
                 semilla=5):
    """Senoidal atravesando un campo de gotas deterministas.

    `lambda_rel` es la longitud de onda RELATIVA al recuadro: con 1.0 la onda
    mide media caja y las gotas son motas que no la perturban (banda L); con
    0.15 la onda mide como una gota y el dibujo se llena de choques (banda
    Ka). Esa comparacion de tamaños es todo el argumento del clip.

    El campo de gotas es el MISMO con la misma `semilla` para las dos
    llamadas, de modo que solo cambia la onda. Atributos `.onda` y `.gotas`.
    El grupo se centra en ORIGIN.
    """
    ancho, alto = float(max(0.5, ancho)), float(max(0.3, alto))
    lam = max(0.02, float(lambda_rel)) * ancho * 0.5
    periodos = ancho / lam
    muestras = _validar_muestras("gotas_y_onda",
                                 int(np.clip(24 * periodos, 120, 400)))

    rng = np.random.default_rng(int(semilla))
    n_gotas = 14
    xs = rng.uniform(-ancho / 2.0 + 0.10, ancho / 2.0 - 0.10, n_gotas)
    ys = rng.uniform(-alto / 2.0 + 0.10, alto / 2.0 - 0.10, n_gotas)
    radios = rng.uniform(0.055, 0.095, n_gotas)

    gotas = VGroup()
    for x, y, r in zip(xs, ys, radios):
        gota = Dot(np.array([x, y, 0.0]), radius=float(r), color=COLOR_GOTA)
        gota.set_fill(color=COLOR_GOTA, opacity=0.55)
        gota.set_stroke(color=COLOR_GOTA, width=1.2, opacity=0.85)
        gotas.add(gota)

    t = np.linspace(-ancho / 2.0, ancho / 2.0, muestras)
    amplitud = alto * 0.22
    pts = np.column_stack([t, amplitud * np.sin(2.0 * np.pi * t / lam),
                           np.zeros(muestras)])
    onda = _curva(pts, color, grosor=3.0)
    onda.set_z_index(4)

    grupo = VGroup(gotas, onda)
    grupo.gotas, grupo.onda = gotas, onda
    grupo.lam = lam
    grupo.move_to(np.array([0.0, 0.0, 0.0]))
    return grupo


# --- la geometria orbital ---------------------------------------------
class TierraAnillos(VGroup):
    """Tierra con los anillos GSO y NGSO poblados (`tierra_y_anillos`).

    Los localizadores no leen los anillos punteados (un `DashedVMobject` puede
    terminar en hueco y su caja miente por unas milesimas): leen el DISCO
    terrestre, que es un circulo entero, y le aplican la razon de radios fija
    de construccion. Asi `.pos_gso()`, `.pos_ngso()` y `.estacion()` siguen
    siendo exactos despues de mover o escalar el grupo.

    Convencion angular: 0 grados a la derecha, sentido antihorario.
    """

    @property
    def centro(self):
        """Centro de la Tierra en coordenadas de escena (np.array)."""
        return np.asarray(self.disco.get_center(), dtype=np.float64)

    @property
    def radio_u(self):
        """Radio terrestre actual en unidades de escena (float)."""
        return float(self.disco.width) / 2.0

    def estacion(self, deg):
        """Punto sobre la SUPERFICIE terrestre en `deg` grados."""
        return self.centro + self.radio_u * _unitario(deg)

    def pos_gso(self, deg):
        """Punto del anillo GSO en `deg` grados."""
        return self.centro + self.radio_u * self.razon_gso * _unitario(deg)

    def pos_ngso(self, deg):
        """Punto del anillo NGSO en `deg` grados."""
        return self.centro + self.radio_u * self.razon_ngso * _unitario(deg)

    def sat_gso_mas_cercano(self, punto):
        """El Dot GSO mas proximo a `punto` (para colgarle un haz)."""
        objetivo = _punto(punto)
        return min(self.sats_gso,
                   key=lambda d: float(np.linalg.norm(d.get_center() -
                                                      objetivo)))


def tierra_y_anillos(radio_tierra=0.85, radio_gso=2.75, radio_ngso=1.55,
                     sats_gso=14, sats_ngso=10, font_size=14):
    """Disco terrestre con meridianos + anillo GSO + anillo NGSO poblados.

    La Tierra es un circulo azul-gris muy oscuro con tres elipses de trazo
    tenue que sugieren meridianos y ecuador (no es un globo texturizado: a
    este tamaño basta la insinuacion). Los dos anillos son circulos punteados
    con sus satelites como puntos equiespaciados, cian el GSO y violeta el
    NGSO, cada uno con su rotulo HUD arriba.

    Los NGSO van en un VGroup propio para poder rotarlo entero
    (`Rotate(t.sats_ngso, ...)` alrededor de `t.centro`) mientras el GSO se
    queda quieto: esa es la escena del conflicto. Topes `SATS_MAX` por anillo.
    El grupo se centra en ORIGIN.
    """
    for nombre, n in (("sats_gso", sats_gso), ("sats_ngso", sats_ngso)):
        if int(n) > SATS_MAX:
            raise ValueError(
                f"tierra_y_anillos: {nombre}={int(n)} supera "
                f"SATS_MAX={SATS_MAX}")
        if int(n) < 0:
            raise ValueError(f"tierra_y_anillos: {nombre} no puede ser < 0")

    rt = float(max(0.1, radio_tierra))
    r_gso = float(max(rt * 1.15, radio_gso))
    r_ngso = float(np.clip(radio_ngso, rt * 1.05, r_gso * 0.95))

    disco = Circle(radius=rt, stroke_width=1.8, color="#3f6f9c")
    disco.set_fill(color=COLOR_TIERRA, opacity=1.0)
    disco.set_stroke(color="#3f6f9c", opacity=0.75)

    # Un meridiano visto de frente es una elipse de altura completa y anchura
    # menor; el ecuador, una elipse ancha y aplastada. Con tres basta para que
    # el disco se lea como un globo sin cargar un raster.
    meridianos = VGroup()
    for ancho_rel, alto_rel in ((0.42, 2.0), (0.86, 2.0), (2.0, 0.44)):
        elipse = Ellipse(width=rt * ancho_rel, height=rt * alto_rel,
                         stroke_width=1.2, color="#3f6f9c")
        elipse.set_stroke(color="#3f6f9c", opacity=0.32)
        elipse.set_fill(opacity=0.0)
        meridianos.add(elipse)
    tierra = VGroup(disco, meridianos)

    def anillo(radio, color):
        return DashedVMobject(
            Circle(radius=radio, stroke_width=2.0, color=color),
            num_dashes=64, dashed_ratio=0.55).set_stroke(color=color,
                                                         opacity=0.75)

    anillo_gso = anillo(r_gso, COLOR_GSO)
    anillo_ngso = anillo(r_ngso, COLOR_NGSO)

    def puntos(n, radio, color, radio_punto):
        grupo = VGroup()
        for k in range(int(n)):
            ang = 360.0 * k / max(1, int(n))
            d = Dot(radio * _unitario(ang), radius=radio_punto, color=color)
            d.set_fill(color=color, opacity=1.0)
            d.set_z_index(5)
            grupo.add(d)
        return grupo

    sats_gso_g = puntos(sats_gso, r_gso, COLOR_GSO, 0.062)
    sats_ngso_g = puntos(sats_ngso, r_ngso, COLOR_NGSO, 0.055)

    rot_gso = _texto_hud("GSO", font_size=font_size, color=COLOR_GSO)
    rot_gso.set_opacity(0.9)
    rot_gso.move_to(np.array([0.0, r_gso + 0.24, 0.0]))
    rot_ngso = _texto_hud("NGSO", font_size=font_size, color=COLOR_NGSO)
    rot_ngso.set_opacity(0.9)
    rot_ngso.move_to(np.array([0.0, r_ngso + 0.24, 0.0]))
    rotulos = VGroup(rot_gso, rot_ngso)

    t = TierraAnillos(anillo_gso, anillo_ngso, tierra, sats_ngso_g,
                      sats_gso_g, rotulos)
    t.tierra, t.disco, t.meridianos = tierra, disco, meridianos
    t.anillo_gso, t.anillo_ngso = anillo_gso, anillo_ngso
    t.sats_gso, t.sats_ngso = sats_gso_g, sats_ngso_g
    t.rotulos = rotulos
    t.razon_gso, t.razon_ngso = r_gso / rt, r_ngso / rt
    return t


class Haz(Polygon):
    """Cono translucido de un enlace (lo crea `haz`).

    `.contiene()` prueba el punto contra los TRES vertices actuales, asi que
    responde bien despues de mover, escalar o rotar el haz: es como el clip 6
    decide si el satelite NGSO que orbita ya se metio en el enlace.
    """

    @property
    def origen(self):
        """Vertice de origen (la punta del cono) en coordenadas de escena."""
        return np.asarray(self.get_vertices()[0], dtype=np.float64)

    @property
    def destino(self):
        """Punto medio del extremo ancho del cono."""
        v = self.get_vertices()
        return np.asarray((v[1] + v[2]) / 2.0, dtype=np.float64)

    def contiene(self, punto):
        """¿El punto cae dentro del triangulo del haz?"""
        p = _punto(punto)[:2]
        a, b, c = [np.asarray(v[:2], dtype=np.float64)
                   for v in self.get_vertices()[:3]]

        def cruz(u, v, w):
            return float((v[0] - u[0]) * (w[1] - u[1]) -
                         (v[1] - u[1]) * (w[0] - u[0]))

        d1, d2, d3 = cruz(a, b, p), cruz(b, c, p), cruz(c, a, p)
        neg = (d1 < 0.0) or (d2 < 0.0) or (d3 < 0.0)
        pos = (d1 > 0.0) or (d2 > 0.0) or (d3 > 0.0)
        return not (neg and pos)


def haz(origen, destino, semiancho=0.16, color=COLOR_GSO):
    """Cono translucido desde `origen` (puntual) hasta `destino` (ancho).

    `semiancho` es RELATIVO al largo del enlace: 0.16 abre unos 9 grados a
    cada lado, que es lo que se lee como "haz" sin tapar media escena. Los dos
    extremos aceptan un punto o cualquier mobject (se usa su centro).
    """
    a, b = _punto(origen), _punto(destino)
    d = b - a
    largo = float(np.linalg.norm(d))
    if largo < _EPS:
        raise ValueError("haz: origen y destino coinciden")
    u = d / largo
    perp = np.array([-u[1], u[0], 0.0]) * largo * float(max(0.01, semiancho))

    cono = Haz(a, b + perp, b - perp, color=color, stroke_width=1.4)
    cono.set_fill(color=color, opacity=0.18)
    cono.set_stroke(color=color, opacity=0.55)
    return cono


# --- el patron de antena ----------------------------------------------
# Lobulos del diagrama polar: (amplitud, angulo en grados, sigma en grados).
# El principal apunta a 0 (a la derecha) con semiancho ~18 grados; los cuatro
# laterales son la quinta parte de alto y viven en +-40 y +-75.
_LOBULOS = ((1.00, 0.0, 15.3), (0.22, 40.0, 9.0), (0.22, -40.0, 9.0),
            (0.22, 75.0, 9.0), (0.22, -75.0, 9.0))
_PISO_LOBULO = 0.06     # radio de fondo: cierra la curva sin colapsarla

# Tramos angulares (en grados) en que se parte la curva cerrada. Cada tramo es
# un VMobject propio que comparte extremos con sus vecinos, de modo que la
# curva se ve continua pero `.principal` y `.laterales` son piezas reales que
# un clip puede resaltar por separado.
_TRAMOS = (("principal", -28.0, 28.0), ("lateral", 28.0, 55.0),
           ("resto", 55.0, 62.0), ("lateral", 62.0, 92.0),
           ("resto", 92.0, 268.0), ("lateral", -92.0, -62.0),
           ("resto", -62.0, -55.0), ("lateral", -55.0, -28.0))


class PatronAntena(VGroup):
    """Diagrama polar de una parabolica que mira a la derecha.

    Lo crea `patron_antena`.

    El eje del lobulo principal se lee de dos puntos guia INVISIBLES (el
    vertice y la punta) que viajan dentro del grupo: por eso `.direccion()` y
    `.punto_de()` siguen siendo correctos despues de mover, escalar o ROTAR el
    patron, que es lo que hace el clip cuando cambia el angulo de llegada de
    la interferencia.

    Angulos en grados, 0 = eje del lobulo principal, positivo antihorario.
    """

    @property
    def origen(self):
        """Vertice del patron (la antena) en coordenadas de escena."""
        return np.asarray(self._vertice.get_center(), dtype=np.float64)

    @property
    def escala_u(self):
        """Unidades de escena por unidad de radio normalizado (float)."""
        punta = np.asarray(self._punta.get_center(), dtype=np.float64)
        return float(np.linalg.norm(punta - self.origen)) / self._r(0.0)

    def direccion(self, deg=0.0):
        """Vector unitario a `deg` grados del eje del lobulo principal."""
        punta = np.asarray(self._punta.get_center(), dtype=np.float64)
        d = punta - self.origen
        n = float(np.linalg.norm(d))
        if n < _EPS:
            return np.array([1.0, 0.0, 0.0])
        eje = d / n
        a = np.deg2rad(float(deg))
        cos, sin = np.cos(a), np.sin(a)
        return np.array([eje[0] * cos - eje[1] * sin,
                         eje[0] * sin + eje[1] * cos, 0.0])

    def _r(self, deg):
        """Radio normalizado del patron en `deg` grados."""
        d = (float(deg) + 180.0) % 360.0 - 180.0
        r = _PISO_LOBULO
        for amp, centro, sigma in _LOBULOS:
            delta = (d - centro + 180.0) % 360.0 - 180.0
            r += amp * np.exp(-(delta / sigma) ** 2)
        return float(r)

    def punto_de(self, deg):
        """Punto del contorno del patron en `deg` grados (de escena)."""
        return self.origen + self.escala_u * self._r(deg) * self.direccion(deg)


def patron_antena(ancho=3.4, color=COLOR_GSO, font_size=14):
    """Patron polar estilizado: lobulo principal + 4 laterales, a la derecha.

    La curva es una suma de gaussianas angulares sobre un piso constante, o
    sea la caricatura honesta de un diagrama de radiacion: casi toda la
    ganancia en un cono estrecho y unas orejas pequeñas donde igual se cuela
    (o se escapa) energia. Ese contraste es lo que la epfd mide.

    `.principal` es el tramo del lobulo mayor y `.laterales` los cuatro
    pequeños; el resto del contorno va en `.resto`. Todos comparten color y
    grosor, asi que a simple vista es una sola curva cerrada.

    `ancho` es el ancho del CONTORNO polar (`.contorno.width`), no el de la
    caja del grupo: el rotulo "0°" cuelga por fuera de la punta, igual que los
    cardinales cuelgan por fuera del radio en la vista polar de apuntado.py.
    El grupo se centra en ORIGIN.
    """
    ancho = float(max(0.4, ancho))

    guia = PatronAntena()

    def tramo(a, b):
        # Muestras IMPAR: asi el punto medio del tramo cae siempre en una
        # muestra y el lobulo principal (que va de -28 a +28) toca de verdad
        # su punta en 0, que es lo que `.punto_de(0)` promete.
        n = _validar_muestras("patron_antena", int(max(13, abs(b - a) / 1.4)))
        angs = np.linspace(a, b, n | 1)
        pts = np.array([guia._r(g) * _unitario(g) for g in angs])
        return _curva(pts, color, grosor=3.0)

    principal, laterales, resto = None, VGroup(), VGroup()
    contorno = VGroup()
    for papel, a, b in _TRAMOS:
        pieza = tramo(a, b)
        contorno.add(pieza)
        if papel == "principal":
            principal = pieza
        elif papel == "lateral":
            laterales.add(pieza)
        else:
            resto.add(pieza)

    eje = DashedVMobject(
        Line(np.array([0.0, 0.0, 0.0]),
             guia._r(0.0) * np.array([1.0, 0.0, 0.0]),
             stroke_width=1.6, color=COLOR_EJE), num_dashes=16)
    eje.set_stroke(opacity=0.8)

    # Puntos guia: radio minusculo y sin relleno para que no aporten a la caja
    # ni se vean, pero si viajen con el grupo en cualquier transformacion.
    vertice = Dot(np.array([0.0, 0.0, 0.0]), radius=0.001, color=color)
    punta = Dot(guia._r(0.0) * np.array([1.0, 0.0, 0.0]), radius=0.001,
                color=color)
    for guia_dot in (vertice, punta):
        guia_dot.set_fill(opacity=0.0)
        guia_dot.set_stroke(opacity=0.0)

    guia.add(eje, contorno, vertice, punta)
    guia.contorno, guia.principal = contorno, principal
    guia.laterales, guia.resto = laterales, resto
    guia.eje = eje
    guia._vertice, guia._punta = vertice, punta
    guia.scale(ancho / max(_EPS, float(contorno.width)))

    # El rotulo se añade DESPUES de escalar: asi el cuerpo de letra es el
    # pedido y no una consecuencia del tamaño del patron. Va FUERA del
    # contorno y por debajo del eje: el clip mete una flecha por el eje desde
    # la derecha y no debe encontrarse un texto en el camino.
    rotulo = _texto_hud("0°", font_size=font_size, color=CODE_MUTED)
    rotulo.set_opacity(0.85)
    rotulo.move_to(guia.punto_de(0.0) + guia.direccion(0.0) * 0.12 +
                   guia.direccion(-90.0) * 0.30)
    guia.add(rotulo)
    guia.rotulo = rotulo
    guia.move_to(np.array([0.0, 0.0, 0.0]))
    return guia


# --- regulacion: la linea de tiempo -----------------------------------
class LineaTiempo(VGroup):
    """Hitos regulatorios sobre una linea (la crea `linea_tiempo`).

    `.muesca(i)` lee el centro ACTUAL de la muesca i-esima, asi que un punto
    que recorra la linea (o una flecha que señale un hito) sigue cayendo bien
    despues de mover o escalar el grupo.
    """

    def muesca(self, i):
        """Centro de escena de la muesca `i` (np.array)."""
        n = len(self.muescas)
        k = int(i)
        if not -n <= k < n:
            raise ValueError(f"linea_tiempo: no hay hito {i} (hay {n})")
        return np.asarray(self.muescas[k].get_center(), dtype=np.float64)

    def rotulo(self, i):
        """VGroup del rotulo (etiqueta + sub-etiqueta) del hito `i`."""
        return self.rotulos[int(i)]


def linea_tiempo(hitos, ancho=6.4, color=COLOR_ONDA, font_size=16):
    """Linea horizontal con muescas rotuladas alternando arriba y abajo.

    `hitos` es una lista de `(etiqueta_corta, sub_etiqueta)`; tambien acepta
    cadenas sueltas si el hito no lleva sub-etiqueta. El alternado es lo que
    permite rotular cuatro o cinco hitos en 6.4 unidades sin que dos textos se
    toquen, aunque uno sea largo. La sub-etiqueta va en cuerpo menor y SIEMPRE
    mas lejos de la linea que su etiqueta, para que el par se lea como bloque.

    Tope `HITOS_MAX`. El grupo se centra en ORIGIN.
    """
    lista = list(hitos)
    if not lista:
        raise ValueError("linea_tiempo: hace falta al menos un hito")
    if len(lista) > HITOS_MAX:
        raise ValueError(
            f"linea_tiempo: {len(lista)} hitos supera HITOS_MAX={HITOS_MAX}")

    ancho = float(max(0.5, ancho))
    normalizados = []
    for h in lista:
        if isinstance(h, str):
            normalizados.append((h, ""))
        else:
            par = tuple(h)
            normalizados.append((str(par[0]),
                                 str(par[1]) if len(par) > 1 else ""))

    linea = Line(np.array([-ancho / 2.0, 0.0, 0.0]),
                 np.array([ancho / 2.0, 0.0, 0.0]),
                 stroke_width=2.6, color=COLOR_EJE)
    # Margen para que el primer y el ultimo rotulo no se salgan de la linea.
    margen = ancho * 0.10
    util = ancho - 2.0 * margen
    n = len(normalizados)
    xs = ([0.0] if n == 1
          else np.linspace(-util / 2.0, util / 2.0, n))

    muescas, rotulos = VGroup(), VGroup()
    for i, (etiqueta, sub) in enumerate(normalizados):
        x = float(xs[i])
        muesca = Line(np.array([x, -0.11, 0.0]), np.array([x, 0.11, 0.0]),
                      stroke_width=2.8, color=color)
        muescas.add(muesca)
        punto = Dot(np.array([x, 0.0, 0.0]), radius=0.045, color=color)
        punto.set_z_index(3)
        muescas.add(punto)

        arriba = (i % 2 == 0)
        signo = 1.0 if arriba else -1.0
        principal = _texto_hud(etiqueta, font_size=font_size, color=color)
        principal.move_to(np.array([x, signo * (0.20 + principal.height / 2.0),
                                    0.0]))
        bloque = VGroup(principal)
        if sub:
            secundaria = _texto_hud(sub, font_size=max(8, font_size - 4),
                                    color=CODE_MUTED)
            secundaria.set_opacity(0.9)
            secundaria.move_to(np.array(
                [x, float(principal.get_y()) +
                 signo * (principal.height / 2.0 + 0.07 +
                          secundaria.height / 2.0), 0.0]))
            bloque.add(secundaria)
        rotulos.add(bloque)

    # `.muesca(i)` indexa las rayas, no los puntos: se guardan aparte.
    rayas = VGroup(*[m for k, m in enumerate(muescas) if k % 2 == 0])
    puntos = VGroup(*[m for k, m in enumerate(muescas) if k % 2 == 1])

    lt = LineaTiempo(linea, muescas, rotulos)
    lt.linea, lt.rotulos = linea, rotulos
    lt.muescas, lt.puntos = rayas, puntos
    lt.hitos = tuple(normalizados)
    lt.move_to(np.array([0.0, 0.0, 0.0]))
    return lt
