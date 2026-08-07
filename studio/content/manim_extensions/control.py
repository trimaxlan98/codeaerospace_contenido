"""Control automatico animable: masa-resorte, plano s, 2o orden, lazo y windup.

Pensado para el curso "Control: domar sistemas que se resisten". Todo el
calculo es numpy puro y determinista (no hay azar en ninguna pieza): mismo
script -> mismo render, condicion necesaria para trabajar con
`--disable_caching`. Nada de red, nada de disco.

La regla de color del curso: la REFERENCIA (lo que se ordena) es ambar, el
SISTEMA y su respuesta cian, el CONTROLADOR y sus señales violeta, lo
INESTABLE / saturado / errado rojo, lo LOGRADO verde; ejes, cajas y demas
mobiliario en el gris azulado `COLOR_EJE`. No mezclar roles.

Piezas:
    masa_resorte        el sistema de segundo orden hecho objeto: pared,
                        resorte en zigzag, amortiguador en paralelo y masa
    plano_s + polo      el mapa del destino, con sus dos semiplanos
    respuesta_escalon   la curva de 2o orden para un zeta / wn dados
    lazo_cerrado        el diagrama de bloques r -> +/- -> C -> P -> y
    rampa_con_rezago    el error de arrastre: dos rectas paralelas
    curva_windup        la memoria que se emborracha (y su remedio)
    barras_metricas     tres metricas de sintonizacion, comparables

Las piezas que exponen localizadores (`.punto`, `.punto_en`, `.brecha_en`,
`.centro`, `.re` / `.im`) los calculan sobre la geometria ACTUAL del mobject:
siguen siendo validos despues de mover o escalar. Asi los clips cuelgan
flechas, tags y puntos sin adivinar coordenadas. `masa_resorte.estirar()` va
mas lejos: redibuja el resorte y el amortiguador leyendo la pared, asi que
tambien funciona despues de un `move_to` o un `scale`.

Todo el texto se crea con el nombre GLOBAL `Text`, nunca con una referencia
capturada en un local: el style_block de los clips inyecta su propia version
(`_control.Text = Text`) y necesita que la busqueda sea global.

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render):
`MUESTRAS_MAX` y `POLOS_MAX` levantan ValueError (a diferencia de
fractales.py, que recorta en silencio: aqui pasarse cambia lo que se ve, y es
mejor enterarse).

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from control import masa_resorte, plano_s, polo, respuesta_escalon

    mr = masa_resorte(ancho=2.8)
    self.add(mr)
    self.play(mr.animate.estirar(0.9), run_time=0.8)

    plano = plano_s().to_edge(LEFT)
    p = polo(plano, -1.2, 0.9)
    self.add(plano, p)
"""

import numpy as np

from manim import (Arrow, Circle, DashedVMobject, Dot, Line, Polygon,
                   Rectangle, RoundedRectangle, Text, VGroup, VMobject)

from code_brand import CODE_INK, CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
MUESTRAS_MAX = 400      # muestras maximas de una curva parametrica
POLOS_MAX = 8           # polos maximos colgados de un mismo plano s

# Paleta propia de la libreria (coincide con la del curso).
COLOR_REF = "#f59e0b"       # LA REFERENCIA: lo que se ordena, el escalon
COLOR_SIS = "#22d3ee"       # EL SISTEMA: la planta y su respuesta
COLOR_CTRL = "#a78bfa"      # EL CONTROLADOR: resorte, amortiguador, mando
COLOR_MAL = "#f43f5e"       # inestabilidad, error, saturacion, exceso
COLOR_OK = "#34d399"        # estable, amortiguado, meta alcanzada
COLOR_EJE = "#31414f"       # mobiliario: ejes, cajas, pared

# Alias cortos con los nombres de la tabla de paleta del curso, para que el
# style_block de los clips pueda escribir `color=C_REF` tal cual.
C_REF, C_SIS, C_CTRL = COLOR_REF, COLOR_SIS, COLOR_CTRL
C_MAL, C_OK, C_EJE = COLOR_MAL, COLOR_OK, COLOR_EJE

_EPS = 1e-9

# Muestras por curva de respuesta. Con 241 puntos una oscilacion de 3.5
# ciclos en 4.8 unidades de ancho sale lisa sin inflar la cuenta de beziers.
_MUESTRAS_CURVA = 241

# Todas las respuestas al escalon comparten esta escala vertical: el valor 0
# cae en el eje del tiempo y el valor `_VALOR_MAX` en el borde superior de la
# caja. 1.9 deja entrar entera la peor curva del curso (zeta = 0.056, con su
# 84% de sobreimpulso: pico 1.839) sin que ninguna se salga del `alto`
# declarado. Es una constante y no un parametro a proposito: es lo que
# permite comparar dos zetas distintas de un vistazo, y lo que hace que un
# ReplacementTransform entre ellas no deforme los ejes.
_VALOR_MAX = 1.9

# La curva de windup se pasa mas todavia (pico ~1.77) y se compara consigo
# misma, no con las respuestas al escalon: escala propia.
_VALOR_MAX_WINDUP = 2.0

# El "exceso" del windup empieza donde la curva supera este multiplo de la
# referencia: por debajo es sobreimpulso normal, por encima es la memoria
# emborrachada.
_UMBRAL_EXCESO = 1.15


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


def _ejes_minimos(ancho, alto, color=COLOR_EJE, etiqueta_x="t", etiqueta_y="y",
                  font_size=15):
    """Eje horizontal + eje vertical en L, centrados en ORIGIN, con rotulos.

    Devuelve (ejes, eje_x, eje_y, etiquetas, origen): `origen` es la esquina
    inferior izquierda, que es el (0, 0) logico de todas las curvas de la
    libreria.
    """
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    origen = np.array([-ancho / 2.0, -alto / 2.0, 0.0])

    eje_x = Line(origen, origen + np.array([ancho, 0.0, 0.0]),
                 stroke_width=2.4, color=color)
    eje_y = Line(origen, origen + np.array([0.0, alto, 0.0]),
                 stroke_width=2.4, color=color)
    ejes = VGroup(eje_x, eje_y)

    et_x = _texto_hud(etiqueta_x, font_size=font_size, color=color)
    et_x.move_to(origen + np.array([ancho + 0.04, -0.24, 0.0]))
    et_y = _texto_hud(etiqueta_y, font_size=font_size, color=color)
    et_y.move_to(origen + np.array([-0.28, alto - 0.02, 0.0]))
    etiquetas = VGroup(et_x, et_y)

    return ejes, eje_x, eje_y, etiquetas, origen


def _linea_punteada(p0, p1, color, num_dashes=30, grosor=2.0, opacidad=0.9):
    """Segmento punteado con un numero FIJO de guiones.

    Fijar `num_dashes` es lo que permite que dos variantes de la misma pieza
    (dos zetas, con y sin anti-windup) se transformen una en otra sin que la
    linea de referencia parpadee.
    """
    linea = DashedVMobject(Line(p0, p1, stroke_width=grosor, color=color),
                           num_dashes=int(num_dashes))
    linea.set_stroke(opacity=float(opacidad))
    return linea


# --- el sistema de segundo orden hecho objeto -------------------------
class MasaResorte(VGroup):
    """Masa sobre resorte y amortiguador en paralelo (la crea `masa_resorte`).

    Es el dibujo literal de la ecuacion m x'' + b x' + k x = F: el resorte es
    el termino proporcional (tira mas cuanto mas lejos esta la masa) y el
    amortiguador el derivativo (se opone a la velocidad). En el curso hace de
    analogo fisico del PID.

    `.estirar(dx)` deja la masa a `dx` unidades de su reposo y REDIBUJA el
    zigzag del resorte y el piston del amortiguador entre la pared y la masa.
    Es ABSOLUTO, no incremental: llamarlo dos veces con el mismo valor no
    mueve nada y un updater puede llamarlo en cada frame sin acumular error.

    Toda la geometria se reconstruye a partir de la PARED (su cara derecha y
    su altura), no de la caja del grupo: la pieza se puede mover y escalar
    antes o despues de estirarla y el resorte sigue naciendo donde debe. Y el
    numero de puntos del resorte es constante para cualquier `dx`, de modo
    que `self.play(mr.animate.estirar(0.9))` interpola limpio.
    """

    @property
    def escala(self):
        """Factor de escala actual del conjunto, leido de la pared (float)."""
        return float(self.pared_linea.height) / max(_EPS, self._alto_pared)

    @property
    def anclaje(self):
        """Centro de la cara derecha de la pared, en coordenadas de escena.

        Es el (0, 0) local: de aqui cuelgan el resorte, el cilindro del
        amortiguador y la posicion de reposo de la masa.
        """
        return np.asarray(self.pared_linea.get_right(), dtype=np.float64)

    def centro_masa(self):
        """Centro de la caja "m" en coordenadas de escena (np.array)."""
        return np.asarray(self.masa.get_center(), dtype=np.float64)

    def _a_escena(self, x, y):
        """Punto local (x, y) -> coordenadas de escena, con la escala actual."""
        return self.anclaje + self.escala * np.array([float(x), float(y), 0.0])

    def estirar(self, dx=0.0):
        """Lleva la masa a `dx` del reposo y redibuja resorte y amortiguador.

        `dx` va en unidades LOCALES (las mismas que `ancho`), positivo hacia
        la derecha. Se recorta para que el resorte nunca se colapse del todo
        (minimo el 35% de su largo de reposo): mas comprimido que eso el
        zigzag se convierte en un borron ilegible.
        """
        dx = float(dx)
        largo0 = self._largo
        largo = float(np.clip(largo0 + dx, 0.35 * largo0, 3.0 * largo0))
        self.x = largo - largo0          # el dx efectivo tras el recorte

        # --- la masa ---
        self.masa.move_to(self._a_escena(largo + self._lado / 2.0, 0.0))

        # --- el resorte: zigzag de `_dientes` dientes entre pared y masa ---
        # La amplitud se encoge al estirar y crece al comprimir (el alambre
        # no se estira: se abre el paso), y el ancho del diente sale solo del
        # largo disponible. Los dos tramos rectos de los extremos son las
        # patas de anclaje.
        lead = self._lead
        util = max(0.06, largo - 2.0 * lead)
        amp = self._amp * float(np.clip(largo0 / max(_EPS, largo), 0.55, 1.6))
        n = self._dientes
        y0 = self._y_resorte

        locales = [(0.0, y0), (lead, y0)]
        for i in range(2 * n):
            x = lead + util * (i + 0.5) / (2.0 * n)
            locales.append((x, y0 + (amp if i % 2 == 0 else -amp)))
        locales.append((lead + util, y0))
        locales.append((largo, y0))
        self.resorte.set_points_as_corners(
            [self._a_escena(x, y) for x, y in locales])

        # --- el amortiguador: cilindro anclado a la pared + piston + vastago ---
        ya = self._y_amort
        h = self._alto_cil
        largo_cil = self._largo_cil
        self.cilindro.set_points_as_corners([
            self._a_escena(largo_cil, ya + h), self._a_escena(0.0, ya + h),
            self._a_escena(0.0, ya - h), self._a_escena(largo_cil, ya - h)])

        # El piston viaja con la masa pero se queda DENTRO del cilindro: al
        # tope sigue siendo un amortiguador, no un dibujo roto. Ocupa casi
        # todo el hueco (0.88 de la semialtura) para que se lea como el
        # embolo que es y no como una marca suelta sobre el vastago.
        xp = float(np.clip(self._piston0 + self.x, 0.15 * largo_cil,
                           0.85 * largo_cil))
        self.piston.set_points_as_corners([
            self._a_escena(xp, ya + h * 0.88), self._a_escena(xp, ya - h * 0.88)])
        self.vastago.set_points_as_corners([
            self._a_escena(xp, ya), self._a_escena(largo, ya)])
        return self


def masa_resorte(ancho=2.8, color_masa=COLOR_SIS, color_resorte=COLOR_CTRL,
                 color_amortiguador=COLOR_CTRL):
    """Pared + resorte en zigzag + amortiguador en paralelo + masa "m".

    `ancho` es el ancho NOMINAL del conjunto en reposo, de la cara de la
    pared al borde derecho de la masa (el rayado de la pared asoma un poco
    mas a la izquierda). El resorte va arriba y el amortiguador debajo, en
    paralelo, que es la disposicion canonica del sistema de segundo orden.

    Nace en reposo (`.x` = 0) y centrado en ORIGIN. Para deformarlo,
    `.estirar(dx)`.
    """
    ancho = float(max(1.0, ancho))
    lado = max(0.42, 0.29 * ancho)          # arista de la caja "m"
    largo = max(0.5, ancho - lado)          # resorte en reposo, pared -> masa
    alto_pared = lado * 2.05
    y_resorte = lado * 0.31
    y_amort = -lado * 0.32
    alto_cil = lado * 0.36                  # semialtura interior del cilindro
    largo_cil = largo * 0.68

    # --- pared: trazo vertical grueso + rayado de empotramiento ---
    pared_linea = Line((0.0, -alto_pared / 2.0, 0.0), (0.0, alto_pared / 2.0, 0.0),
                       stroke_width=5.0, color=COLOR_EJE)
    rayas = VGroup()
    paso = alto_pared / 7.0
    for k in range(7):
        y = -alto_pared / 2.0 + paso * (k + 0.5)
        rayas.add(Line((0.0, y, 0.0), (-0.19, y - 0.15, 0.0),
                       stroke_width=2.2, color=COLOR_EJE))
    pared = VGroup(pared_linea, rayas)

    # --- masa: caja redondeada con su letra ---
    caja = RoundedRectangle(corner_radius=lado * 0.14, width=lado, height=lado,
                            stroke_width=3.0, color=color_masa)
    caja.set_fill(color=color_masa, opacity=0.18)
    letra = _texto_hud("m", font_size=max(13, int(lado * 26)), color=color_masa)
    letra.move_to(caja.get_center())
    masa = VGroup(caja, letra)

    resorte = VMobject(color=color_resorte, stroke_width=3.2)
    cilindro = VMobject(color=color_amortiguador, stroke_width=4.0)
    piston = VMobject(color=color_amortiguador, stroke_width=5.4)
    vastago = VMobject(color=color_amortiguador, stroke_width=2.8)
    amortiguador = VGroup(cilindro, piston, vastago)

    mr = MasaResorte(pared, resorte, amortiguador, masa)
    mr.pared, mr.pared_linea, mr.rayas = pared, pared_linea, rayas
    mr.masa, mr.caja, mr.letra = masa, caja, letra
    mr.resorte, mr.amortiguador = resorte, amortiguador
    mr.cilindro, mr.piston, mr.vastago = cilindro, piston, vastago
    mr._alto_pared = alto_pared
    mr._lado, mr._largo = lado, largo
    mr._y_resorte, mr._y_amort = y_resorte, y_amort
    mr._alto_cil, mr._largo_cil = alto_cil, largo_cil
    mr._piston0 = largo_cil * 0.50
    mr._amp = lado * 0.26
    mr._dientes = 8
    mr._lead = min(0.16, largo * 0.09)
    mr.x = 0.0
    mr.estirar(0.0)
    mr.move_to((0.0, 0.0, 0.0))
    return mr


# --- el plano s -------------------------------------------------------
class PlanoS(VGroup):
    """Plano complejo con sus dos semiplanos (lo crea `plano_s`).

    `.unidad`, `.centro()` y `.punto()` se leen de la geometria ACTUAL, asi
    que siguen valiendo despues de mover o escalar el plano: un polo colgado
    con `.punto()` cae en el mismo sitio logico pase lo que pase.
    """

    @property
    def unidad(self):
        """Unidades de escena que vale 1 en el plano (un cuarto del semiancho)."""
        return float(self.eje_re.width) / 8.0

    def centro(self):
        """Origen del plano (el cruce de los ejes) en coordenadas de escena.

        NO es `get_center()`: las etiquetas "estable" / "inestable" no son
        simetricas y desplazarian la caja del grupo. Se lee del eje
        imaginario, que siempre esta centrado en el origen.
        """
        return np.asarray(self.eje_im.get_center(), dtype=np.float64)

    def punto(self, re, im=0.0):
        """Coordenada de escena del punto s = re + j*im del plano."""
        u = self.unidad
        return self.centro() + np.array([float(re) * u, float(im) * u, 0.0])


def plano_s(ancho=4.6, alto=3.2, color=COLOR_EJE, font_size=15):
    """Ejes Re/Im con el semiplano izquierdo verde y el derecho rojo.

    Los dos sombreados van a `fill_opacity` 0.10: se leen como una tincion
    del fondo, no como dos rectangulos de color, y dejan pasar cualquier
    curva o polo que se dibuje encima. Las etiquetas HUD "estable" e
    "inestable" van chicas y al 0.7 de opacidad en la parte alta de cada
    mitad, lejos del eje imaginario donde viven los polos.

    La escala es 1 unidad = un cuarto del semiancho (`.unidad`), asi que con
    el ancho por defecto el plano cubre s de -4 a +4 en la parte real. El
    grupo se centra en ORIGIN.
    """
    ancho, alto = float(max(1.0, ancho)), float(max(1.0, alto))
    medio = ancho / 2.0

    zona_estable = Rectangle(width=medio, height=alto, stroke_width=0)
    zona_estable.set_fill(color=COLOR_OK, opacity=0.10)
    zona_estable.move_to((-medio / 2.0, 0.0, 0.0))
    zona_inestable = Rectangle(width=medio, height=alto, stroke_width=0)
    zona_inestable.set_fill(color=COLOR_MAL, opacity=0.10)
    zona_inestable.move_to((medio / 2.0, 0.0, 0.0))
    for zona in (zona_estable, zona_inestable):
        zona.set_z_index(-2)

    eje_re = Line((-medio, 0.0, 0.0), (medio, 0.0, 0.0), stroke_width=2.4,
                  color=color)
    eje_im = Line((0.0, -alto / 2.0, 0.0), (0.0, alto / 2.0, 0.0),
                  stroke_width=2.6, color=color)

    # Los rotulos de los ejes van FUERA del rectangulo sombreado, sobre el
    # fondo limpio: dentro competian con "estable" / "inestable" (que viven
    # en la misma franja alta) y las dos palabras se tocaban.
    et_re = _texto_hud("Re", font_size=font_size, color=CODE_MUTED)
    et_re.set_opacity(0.75)
    et_re.move_to((medio + 0.28, -0.24, 0.0))
    et_im = _texto_hud("Im", font_size=font_size, color=CODE_MUTED)
    et_im.set_opacity(0.75)
    et_im.move_to((0.30, alto / 2.0 + 0.22, 0.0))
    ejes = VGroup(eje_re, eje_im)
    etiquetas = VGroup(et_re, et_im)

    et_estable = _texto_hud("estable", font_size=font_size - 1, color=COLOR_OK)
    et_estable.set_opacity(0.7)
    et_estable.move_to((-medio / 2.0, alto / 2.0 - 0.28, 0.0))
    et_inestable = _texto_hud("inestable", font_size=font_size - 1,
                              color=COLOR_MAL)
    et_inestable.set_opacity(0.7)
    et_inestable.move_to((medio / 2.0, alto / 2.0 - 0.28, 0.0))
    zonas = VGroup(zona_estable, zona_inestable, et_estable, et_inestable)

    plano = PlanoS(zonas, ejes, etiquetas)
    plano.zona_estable, plano.zona_inestable = zona_estable, zona_inestable
    plano.eje_re, plano.eje_im = eje_re, eje_im
    plano.ejes, plano.etiquetas = ejes, etiquetas
    plano.et_estable, plano.et_inestable = et_estable, et_inestable
    plano.polos = []
    return plano


class Polo(VGroup):
    """Marca "x" de un polo sobre un plano s (la crea `polo`).

    `.re` y `.im` son PROPIEDADES: se recalculan del centro actual de la
    marca contra el origen del plano. Un polo que se anima con
    `.animate.move_to(plano.punto(-0.1, 0.9))` sigue diciendo la verdad sobre
    donde esta, que es justo lo que el clip necesita para rotularlo.
    """

    @property
    def re(self):
        """Parte real del polo, leida de su posicion actual (float)."""
        d = np.asarray(self.get_center(), dtype=np.float64) - self.plano.centro()
        return float(d[0] / max(_EPS, self.plano.unidad))

    @property
    def im(self):
        """Parte imaginaria del polo, leida de su posicion actual (float)."""
        d = np.asarray(self.get_center(), dtype=np.float64) - self.plano.centro()
        return float(d[1] / max(_EPS, self.plano.unidad))

    @property
    def estable(self):
        """¿El polo esta en el semiplano izquierdo ahora mismo? (bool)."""
        return bool(self.re < 0.0)


def polo(plano, re, im=0.0, color=COLOR_SIS):
    """Marca "x" en `plano.punto(re, im)`, del tamaño del plano.

    Cada plano lleva la cuenta de sus polos en `plano.polos`: pasado
    `POLOS_MAX` la funcion levanta ValueError. Un mapa con nueve polos no es
    un mapa, es una mancha, y ademas cada marca son dos trazos que el render
    del VPS acaba pagando.
    """
    ya = len(getattr(plano, "polos", []))
    if ya >= POLOS_MAX:
        raise ValueError(
            f"polo: el plano ya tiene {ya} polos y POLOS_MAX={POLOS_MAX}")

    centro = plano.punto(re, im)
    brazo = plano.unidad * 0.22
    trazos = [Line(centro + np.array([-brazo, -s * brazo, 0.0]),
                   centro + np.array([brazo, s * brazo, 0.0]),
                   stroke_width=4.2, color=color) for s in (1.0, -1.0)]

    p = Polo(*trazos)
    p.plano = plano
    p.trazos = VGroup(*trazos)
    p.set_z_index(3)
    if hasattr(plano, "polos"):
        plano.polos.append(p)
    return p


# --- la respuesta al escalon ------------------------------------------
def _valor_segundo_orden(t, zeta, wn):
    """y(t) de un 2o orden canonico ante escalon unitario (array o escalar).

    Subamortiguado (zeta < 1):
        y = 1 - exp(-z wn t) / sqrt(1 - z^2) * sin(wd t + acos(z))
    Criticamente amortiguado (zeta = 1):
        y = 1 - (1 + wn t) exp(-wn t)
    Sobreamortiguado (zeta > 1), con s1,2 = -wn (z -+ sqrt(z^2 - 1)):
        y = 1 - (s2 exp(s1 t) - s1 exp(s2 t)) / (s2 - s1)
    Las tres arrancan en y(0) = 0 y tienden a 1, que es lo que hace que las
    curvas de distintos zeta se puedan superponer y transformar entre si.
    """
    t = np.asarray(t, dtype=np.float64)
    z = float(max(0.0, zeta))
    w = float(max(_EPS, wn))

    if z < 1.0 - 1e-6:
        wd = w * np.sqrt(1.0 - z * z)
        fase = np.arccos(z)
        return 1.0 - np.exp(-z * w * t) / np.sqrt(1.0 - z * z) * \
            np.sin(wd * t + fase)
    if z <= 1.0 + 1e-6:
        return 1.0 - (1.0 + w * t) * np.exp(-w * t)

    raiz = np.sqrt(z * z - 1.0)
    s1, s2 = -w * (z - raiz), -w * (z + raiz)
    return 1.0 - (s2 * np.exp(s1 * t) - s1 * np.exp(s2 * t)) / (s2 - s1)


class Respuesta(VGroup):
    """Respuesta al escalon de un 2o orden (la crea `respuesta_escalon`).

    La escala vertical es FIJA (el valor `_VALOR_MAX` = 1.9 en el borde
    superior): la curva de zeta = 0.056, con su 84% de sobreimpulso, cabe
    entera dentro del `alto` declarado, y dos respuestas de distinto zeta se
    leen sobre la misma regla. Es la razon de que un ReplacementTransform
    entre ellas mueva la curva sin mover los ejes.

    `.punto_en(t_rel)` cae SOBRE la curva dibujada y se calcula con el origen
    y el tamaño ACTUALES de los ejes: sirve igual antes y despues de mover o
    escalar el grupo.
    """

    def valor_en(self, t_rel):
        """Valor y(t) de la respuesta en `t_rel` de [0, 1] (1 = `t_max`)."""
        t = float(np.clip(t_rel, 0.0, 1.0)) * self.t_max
        return float(_valor_segundo_orden(t, self.zeta, self.wn))

    def punto_en(self, t_rel):
        """Coordenada de escena del punto de la curva en `t_rel` de [0, 1]."""
        origen = np.asarray(self.eje_t.get_start(), dtype=np.float64)
        v = float(np.clip(self.valor_en(t_rel), 0.0, _VALOR_MAX))
        return origen + np.array([
            float(np.clip(t_rel, 0.0, 1.0)) * float(self.eje_t.width),
            v / _VALOR_MAX * float(self.eje_y.height),
            0.0])


def respuesta_escalon(zeta=0.056, wn=2.24, ancho=4.8, alto=2.3,
                      color=COLOR_SIS, color_ref=COLOR_REF, t_max=10.0):
    """Ejes minimos + referencia punteada en 1.0 + curva de 2o orden.

    Con `zeta` < 1 la curva se pasa y oscila (con 0.056 y wn 2.24, los
    numeros del curso: 84% de sobreimpulso y 32 s de establecimiento); con
    `zeta` >= 1 sube suave y no se pasa nunca.

    El valor 1.0 (la referencia) queda a 1/1.9 del alto, o sea algo por
    debajo de la mitad de la caja: el hueco de arriba es exactamente el que
    hace falta para que el sobreimpulso mas bruto del curso entre completo.
    El grupo se centra en ORIGIN.
    """
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    ejes, eje_t, eje_y, etiquetas, origen = _ejes_minimos(
        ancho, alto, etiqueta_x="t", etiqueta_y="y")

    r = Respuesta(ejes)
    r.ejes, r.eje_t, r.eje_y = ejes, eje_t, eje_y
    r.zeta, r.wn, r.t_max = float(zeta), float(wn), float(max(_EPS, t_max))

    y_ref = alto / _VALOR_MAX
    linea_ref = _linea_punteada(origen + np.array([0.0, y_ref, 0.0]),
                                origen + np.array([ancho, y_ref, 0.0]),
                                color_ref, num_dashes=30, opacidad=0.85)

    n = _validar_muestras("respuesta_escalon", _MUESTRAS_CURVA)
    ts = np.linspace(0.0, 1.0, n)
    curva = _curva(np.array([r.punto_en(t) for t in ts]), color, grosor=3.4)

    r.add(linea_ref, curva, etiquetas)
    r.linea_ref, r.curva, r.etiquetas = linea_ref, curva, etiquetas
    return r


# --- el lazo cerrado --------------------------------------------------
def _bloque(texto, ancho, alto, color, font_size):
    """Caja redondeada con su rotulo centrado (bloque propio de esta libreria).

    Deliberadamente NO se importa `bloques.py`: aquel modulo es de proposito
    general y sus colores y proporciones responden a otros diagramas. Aqui el
    bloque es parte del lazo y sigue la paleta del curso.
    """
    caja = RoundedRectangle(corner_radius=alto * 0.16, width=ancho, height=alto,
                            stroke_width=2.8, color=color)
    caja.set_fill(color=color, opacity=0.14)
    registrar_fuentes()
    etiqueta = Text(str(texto), font=FUENTE_HUD, font_size=font_size,
                    color=color)
    if float(etiqueta.width) > ancho * 0.82:
        etiqueta.scale_to_fit_width(ancho * 0.82)
    etiqueta.move_to(caja.get_center())
    b = VGroup(caja, etiqueta)
    b.caja, b.etiqueta = caja, etiqueta
    return b


def _flecha(p0, p1, color, punta=0.17, grosor=3.4):
    """Flecha recta con la punta ACOTADA en tamaño absoluto.

    Un `Arrow` normal dimensiona la punta como fraccion del largo, asi que en
    un diagrama con tramos de 0.4 y de 1.3 unidades las cabezas salen de
    tamaños muy distintos y el tramo largo parece un cartel. Aqui la punta
    mide `punta` salvo que el tramo sea tan corto que no quepa (entonces
    manda el 30% del largo).
    """
    return Arrow(np.asarray(p0, dtype=np.float64),
                 np.asarray(p1, dtype=np.float64), buff=0.0, color=color,
                 stroke_width=grosor, tip_length=float(punta),
                 max_tip_length_to_length_ratio=0.30)


class LazoCerrado(VGroup):
    """Diagrama de bloques del lazo realimentado (lo crea `lazo_cerrado`)."""

    def camino(self):
        """Los tramos del recorrido de la señal, EN ORDEN.

        r -> sumador -> CONTROL -> PLANTA -> y -> retro -> sumador: cinco
        VMobjects listos para `ShowPassingFlash` encadenados en `Succession`.
        El ultimo es el TRAZO de la rama de realimentacion (la polilinea sin
        su punta): un solo VMobject continuo hace un destello mucho mas
        limpio que un VGroup, en el que todos los tramos brillarian a la vez.
        """
        return [self.flecha_r, self.flecha_control, self.flecha_planta,
                self.flecha_y, self.trazo_retro]


def lazo_cerrado(ancho=6.4, font_size=16):
    """r -> (+/-) -> [CONTROL] -> [PLANTA] -> y, con realimentacion negativa.

    Las cuatro flechas de ida arrancan y mueren EXACTAMENTE en los bordes de
    lo que unen (nada de `buff` que las deje cortas ni de puntas metidas
    dentro de una caja), y la rama de retorno baja bien por debajo de los
    bloques antes de volver: ninguna linea cruza ninguna caja.

    El sumador es un circulo chico con "+" en el cuadrante por donde entra la
    referencia (arriba a la izquierda) y "-" en el cuadrante por donde vuelve
    la medida (abajo a la izquierda), que es la convencion de cualquier
    diagrama de control. El grupo se centra en ORIGIN.
    """
    k = float(max(0.3, ancho)) / 6.4          # escala respecto del nominal

    x_r, x_sum, x_ctrl, x_planta, x_y = (-3.12 * k, -2.30 * k, -0.845 * k,
                                         1.005 * k, 2.92 * k)
    w_bloque, h_bloque = 1.35 * k, 0.78 * k
    r_sum = 0.28 * k
    punta = 0.17 * k
    x_nodo, y_retro = 2.35 * k, -1.20 * k

    control = _bloque("CONTROL", w_bloque, h_bloque, COLOR_CTRL, font_size)
    control.move_to((x_ctrl, 0.0, 0.0))
    planta = _bloque("PLANTA", w_bloque, h_bloque, COLOR_SIS, font_size)
    planta.move_to((x_planta, 0.0, 0.0))

    circulo = Circle(radius=r_sum, stroke_width=2.8, color=CODE_MUTED)
    circulo.set_fill(color="#0a1119", opacity=0.95)
    circulo.move_to((x_sum, 0.0, 0.0))
    # Los signos van FUERA del circulo, cada uno en el cuadrante por el que
    # entra su señal. En Space Mono el "+" y el "-" son glifos pequeños
    # dentro de su caja, asi que van varios puntos por encima del cuerpo del
    # diagrama para pesar lo mismo en pantalla.
    signo_mas = _texto_hud("+", font_size=font_size + 8, color=COLOR_REF)
    signo_mas.move_to((x_sum - 0.36 * k, 0.36 * k, 0.0))
    signo_menos = _texto_hud("-", font_size=font_size + 12, color=COLOR_SIS)
    signo_menos.move_to((x_sum - 0.36 * k, -0.36 * k, 0.0))
    sumador = VGroup(circulo, signo_mas, signo_menos)
    sumador.circulo = circulo
    sumador.signo_mas, sumador.signo_menos = signo_mas, signo_menos

    eti_r = _texto_hud("r", font_size=font_size + 2, color=COLOR_REF)
    eti_r.move_to((x_r, 0.0, 0.0))
    eti_y = _texto_hud("y", font_size=font_size + 2, color=COLOR_SIS)
    eti_y.move_to((x_y, 0.0, 0.0))
    etiquetas = VGroup(eti_r, eti_y)

    flecha_r = _flecha((x_r + 0.14 * k, 0.0, 0.0), (x_sum - r_sum, 0.0, 0.0),
                       CODE_MUTED, punta)
    flecha_control = _flecha((x_sum + r_sum, 0.0, 0.0),
                             (x_ctrl - w_bloque / 2.0, 0.0, 0.0), CODE_MUTED,
                             punta)
    flecha_planta = _flecha((x_ctrl + w_bloque / 2.0, 0.0, 0.0),
                            (x_planta - w_bloque / 2.0, 0.0, 0.0), CODE_MUTED,
                            punta)
    flecha_y = _flecha((x_planta + w_bloque / 2.0, 0.0, 0.0),
                       (x_y - 0.16 * k, 0.0, 0.0), CODE_MUTED, punta)

    # Rama de retorno: nodo sobre la linea de salida, bajada, tramo largo por
    # debajo de todo y subida al sumador. La punta se dibuja a mano porque un
    # Arrow no sabe seguir una polilinea.
    nodo = Dot((x_nodo, 0.0, 0.0), radius=0.055 * max(0.5, k), color=COLOR_SIS)
    trazo_retro = VMobject(color=COLOR_SIS, stroke_width=3.0)
    trazo_retro.set_points_as_corners([
        np.array([x_nodo, 0.0, 0.0]), np.array([x_nodo, y_retro, 0.0]),
        np.array([x_sum, y_retro, 0.0]),
        np.array([x_sum, -r_sum - 0.11 * k, 0.0])])
    lado = 0.11 * k
    punta_retro = Polygon(np.array([x_sum, -r_sum, 0.0]),
                          np.array([x_sum - lado, -r_sum - 2.0 * lado, 0.0]),
                          np.array([x_sum + lado, -r_sum - 2.0 * lado, 0.0]),
                          stroke_width=0, color=COLOR_SIS)
    punta_retro.set_fill(color=COLOR_SIS, opacity=1.0)
    rama_retro = VGroup(nodo, trazo_retro, punta_retro)
    rama_retro.nodo, rama_retro.trazo = nodo, trazo_retro
    rama_retro.punta = punta_retro

    flechas = VGroup(flecha_r, flecha_control, flecha_planta, flecha_y,
                     rama_retro)

    lazo = LazoCerrado(etiquetas, flechas, sumador, control, planta)
    lazo.sumador, lazo.circulo = sumador, circulo
    lazo.signo_mas, lazo.signo_menos = signo_mas, signo_menos
    lazo.control, lazo.planta = control, planta
    lazo.flechas, lazo.rama_retro = flechas, rama_retro
    lazo.trazo_retro, lazo.punta_retro, lazo.nodo = trazo_retro, punta_retro, nodo
    lazo.flecha_r, lazo.flecha_control = flecha_r, flecha_control
    lazo.flecha_planta, lazo.flecha_y = flecha_planta, flecha_y
    lazo.etiquetas, lazo.eti_r, lazo.eti_y = etiquetas, eti_r, eti_y
    return lazo


# --- la rampa y el error de arrastre ----------------------------------
class Rampa(VGroup):
    """Referencia rampa y respuesta rezagada (la crea `rampa_con_rezago`).

    El rezago se modela como un RETARDO en t, que sobre una rampa equivale
    exactamente a un error constante en valor: las dos rectas salen
    paralelas y la brecha vertical entre ellas vale lo mismo en todo el
    recorrido. Es el error de arrastre e_ss = v*b/kp del curso.

    Antes de `rezago` la respuesta se queda pegada al cero (una montura que
    todavia no arranco), asi que la curva nunca se sale por abajo.

    `.brecha_en()` lee la geometria ACTUAL de los ejes: con `rezago` 0 los
    dos puntos que devuelve son identicos.
    """

    def _punto(self, t_rel, valor):
        origen = np.asarray(self.eje_t.get_start(), dtype=np.float64)
        return origen + np.array([
            float(np.clip(t_rel, 0.0, 1.0)) * float(self.eje_t.width),
            (self.base_rel + self.span_rel * float(np.clip(valor, 0.0, 1.0))) *
            float(self.eje_y.height),
            0.0])

    def punto_ref(self, t_rel):
        """Punto de escena de la REFERENCIA (la rampa ordenada) en `t_rel`."""
        return self._punto(t_rel, float(np.clip(t_rel, 0.0, 1.0)))

    def punto_sis(self, t_rel):
        """Punto de escena de la RESPUESTA del sistema en `t_rel`."""
        t = float(np.clip(t_rel, 0.0, 1.0))
        return self._punto(t, max(0.0, t - self.rezago))

    def brecha_en(self, t_rel):
        """(p_ref, p_sis) en `t_rel`: los dos extremos del error de arrastre."""
        return self.punto_ref(t_rel), self.punto_sis(t_rel)


def rampa_con_rezago(ancho=5.4, alto=2.4, rezago=0.14, muestras=120,
                     color_ref=COLOR_REF, color_sis=COLOR_SIS):
    """Ejes minimos + rampa de referencia + respuesta paralela rezagada.

    `rezago` va en unidades de t (el eje completo es 1.0), asi que 0.14 es un
    14% de retraso: la respuesta persigue a distancia constante y no alcanza
    jamas. Con `rezago=0` las dos curvas coinciden punto por punto.

    Los ejes, la escala y la posicion NO dependen de `rezago`: dos variantes
    de la misma rampa se transforman una en otra sin que el cuadro se mueva
    un pixel. El grupo se centra en ORIGIN.
    """
    muestras = _validar_muestras("rampa_con_rezago", muestras)
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    ejes, eje_t, eje_y, etiquetas, _ = _ejes_minimos(
        ancho, alto, etiqueta_x="t", etiqueta_y="ang")

    rampa = Rampa(ejes)
    rampa.ejes, rampa.eje_t, rampa.eje_y = ejes, eje_t, eje_y
    rampa.rezago = float(np.clip(rezago, 0.0, 0.9))
    # La rampa arranca despegada del eje del tiempo y muere despegada del
    # borde de arriba: pegada a cualquiera de los dos se lee como recortada.
    rampa.base_rel, rampa.span_rel = 0.05, 0.88

    ts = np.linspace(0.0, 1.0, muestras)
    ref = _curva(np.array([rampa.punto_ref(t) for t in ts]), color_ref,
                 grosor=3.4)
    sis = _curva(np.array([rampa.punto_sis(t) for t in ts]), color_sis,
                 grosor=3.4)

    rampa.add(ref, sis, etiquetas)
    rampa.ref, rampa.sis, rampa.etiquetas = ref, sis, etiquetas
    return rampa


# --- windup y anti-windup ---------------------------------------------
class Windup(VGroup):
    """Respuesta con integrador saturado (la crea `curva_windup`).

    Sin anti-windup el mando satura, la antena deja de acelerar y el
    integrador SIGUE acumulando: cuando por fin llega, trae encima toda esa
    memoria y se pasa muchisimo, tarde. Se modela como una subida rapida
    (saturada) mas un pulso grande y lento que decae:

        y(t) = 1 - exp(-t/tau) + Mp * (t/tp)^p * exp(p (1 - t/tp))

    El pulso vale 1 justo en t = tp y se apaga solo, asi que la curva tiende
    a la referencia sin trucos. Con anti-windup la SUBIDA es la misma (el
    actuador satura igual: eso no lo arregla nadie) y lo unico que cambia es
    el pulso, que baja de 0.80 a 0.06: llega y se queda.

    Los ejes, la escala y la posicion son los MISMOS en los dos modos: es lo
    que permite el `ReplacementTransform` del clip 7.
    """

    def valor_en(self, t_rel):
        """Valor de la respuesta en `t_rel` de [0, 1] (1.0 = la referencia)."""
        t = float(np.clip(t_rel, 0.0, 1.0))
        base = 1.0 - np.exp(-t / self.tau)
        u = t / self.tp
        pulso = (u ** self.potencia) * np.exp(self.potencia * (1.0 - u))
        return float(base + self.exceso_max * pulso)

    def punto_en(self, t_rel):
        """Coordenada de escena del punto de la curva en `t_rel` de [0, 1]."""
        origen = np.asarray(self.eje_t.get_start(), dtype=np.float64)
        v = float(np.clip(self.valor_en(t_rel), 0.0, _VALOR_MAX_WINDUP))
        return origen + np.array([
            float(np.clip(t_rel, 0.0, 1.0)) * float(self.eje_t.width),
            v / _VALOR_MAX_WINDUP * float(self.eje_y.height),
            0.0])


def curva_windup(ancho=5.4, alto=2.4, con_antiwindup=False, color=COLOR_SIS,
                 color_ref=COLOR_REF, color_mal=COLOR_MAL):
    """Referencia escalon + respuesta con (o sin) la memoria emborrachada.

    Sin anti-windup la curva se va hasta ~1.77 veces la referencia y pasa
    medio recorrido (t de 0.15 a 0.66) por encima del umbral; ese tramo se
    repinta encima en rojo y se expone como `.exceso`. Con
    `con_antiwindup=True` la respuesta llega limpia (pico 1.04) y `.exceso`
    es un VMobject VACIO y transparente (`.has_points()` es False: los clips
    deben comprobarlo antes de animarlo, `Create` sobre un mobject sin puntos
    no dibuja nada).

    El grupo se centra en ORIGIN.
    """
    ancho, alto = float(max(0.5, ancho)), float(max(0.5, alto))
    ejes, eje_t, eje_y, etiquetas, origen = _ejes_minimos(
        ancho, alto, etiqueta_x="t", etiqueta_y="y")

    w = Windup(ejes)
    w.ejes, w.eje_t, w.eje_y = ejes, eje_t, eje_y
    w.con_antiwindup = bool(con_antiwindup)
    # tp = 0.30 pone el pico en el 30% del recorrido (bien despues de que la
    # referencia ya deberia estar alcanzada: el sobreimpulso es TARDIO) y la
    # potencia 4 hace que el tramo rojo ocupe algo mas de la mitad del cuadro
    # y no casi todo: con una cola mas lenta el cian desaparecia de la escena
    # y ya no se leia que la curva vuelve.
    w.tau, w.tp, w.potencia = 0.09, 0.30, 4.0
    w.exceso_max = 0.06 if w.con_antiwindup else 0.80

    y_ref = alto / _VALOR_MAX_WINDUP
    linea_ref = _linea_punteada(origen + np.array([0.0, y_ref, 0.0]),
                                origen + np.array([ancho, y_ref, 0.0]),
                                color_ref, num_dashes=30, opacidad=0.85)

    n = _validar_muestras("curva_windup", 181)
    ts = np.linspace(0.0, 1.0, n)
    puntos = np.array([w.punto_en(t) for t in ts])
    curva = _curva(puntos, color, grosor=3.4)

    # El exceso es el tramo contiguo por encima del umbral. Se recortan los
    # dos cruces por interpolacion lineal para que el rojo empiece y termine
    # exactamente en el umbral y no un par de muestras despues.
    valores = np.array([w.valor_en(t) for t in ts])
    dentro = np.flatnonzero(valores > _UMBRAL_EXCESO)
    exceso = VMobject(color=color_mal, stroke_width=5.4)
    if dentro.size >= 2:
        i0, i1 = int(dentro[0]), int(dentro[-1])
        tramo = [puntos[k] for k in range(i0, i1 + 1)]
        if i0 > 0:
            f = ((_UMBRAL_EXCESO - valores[i0 - 1]) /
                 (valores[i0] - valores[i0 - 1]))
            tramo.insert(0, puntos[i0 - 1] + f * (puntos[i0] - puntos[i0 - 1]))
        if i1 + 1 < n:
            f = ((_UMBRAL_EXCESO - valores[i1]) /
                 (valores[i1 + 1] - valores[i1]))
            tramo.append(puntos[i1] + f * (puntos[i1 + 1] - puntos[i1]))
        exceso.set_points_smoothly(np.array(tramo))
    else:
        # Sin exceso el mobject se queda SIN puntos y ademas con el trazo
        # transparente. Lo segundo es lo que evita el fantasma del clip 7: en
        # un ReplacementTransform, Manim le inventa un punto al mobject vacio
        # para poder alinearlo, y sin esto el tramo rojo del windup se
        # encogia hasta un puntito rojo que se quedaba clavado en la escena.
        exceso.set_stroke(opacity=0.0)
    exceso.set_z_index(2)

    w.add(linea_ref, curva, exceso, etiquetas)
    w.linea_ref, w.curva, w.exceso = linea_ref, curva, exceso
    w.etiquetas = etiquetas
    return w


# --- las metricas de sintonizacion ------------------------------------
def barras_metricas(valores, etiquetas=("RMS", "SOBREIMPULSO", "T. EST."),
                    ancho=3.6, alto=1.9, color=COLOR_SIS):
    """Barras verticales con rotulo HUD debajo, para comparar sintonizaciones.

    `valores` van en [0, 1] (se recortan) y son "lo malo": 1 es una metrica
    por las nubes y 0 una metrica perfecta, asi que sintonizar bien se ve
    como barras que se hunden. Detras de cada barra queda su marco al 0.14 de
    opacidad, que da la referencia del 100% sin la cual una barra suelta no
    dice nada.

    La estructura (marco, barra y rotulo por metrica) no depende de los
    valores: dos juegos de barras se transforman uno en otro directamente.
    El grupo se centra en ORIGIN.
    """
    vals = np.clip(np.asarray(list(valores), dtype=np.float64).ravel(), 0.0, 1.0)
    ancho, alto = float(max(0.5, ancho)), float(max(0.3, alto))
    n = max(1, vals.size)
    paso = ancho / n
    ancho_barra = paso * 0.46
    base = -alto / 2.0

    linea = Line((-ancho / 2.0, base, 0.0), (ancho / 2.0, base, 0.0),
                 stroke_width=2.4, color=COLOR_EJE)

    marcos, barras, rotulos = VGroup(), VGroup(), VGroup()
    nombres = list(etiquetas) + [""] * max(0, n - len(list(etiquetas)))
    for k in range(n):
        x = -ancho / 2.0 + paso * (k + 0.5)

        marco = Rectangle(width=ancho_barra, height=alto, stroke_width=1.4,
                          color=COLOR_EJE)
        marco.set_fill(color=COLOR_EJE, opacity=0.14)
        marco.set_stroke(opacity=0.6)
        marco.move_to((x, base + alto / 2.0, 0.0))
        marcos.add(marco)

        h = max(0.02, float(vals[k]) * alto)
        barra = Rectangle(width=ancho_barra, height=h, stroke_width=0)
        barra.set_fill(color=color, opacity=0.9)
        barra.move_to((x, base + h / 2.0, 0.0))
        barras.add(barra)

        rotulo = _texto_hud(nombres[k], font_size=13, color=CODE_MUTED)
        rotulo.set_opacity(0.85)
        if float(rotulo.width) > paso * 0.94:
            rotulo.scale_to_fit_width(paso * 0.94)
        rotulo.move_to((x, base - 0.22, 0.0))
        rotulos.add(rotulo)

    grupo = VGroup(marcos, linea, barras, rotulos)
    grupo.marcos, grupo.linea = marcos, linea
    grupo.barras, grupo.rotulos = barras, rotulos
    grupo.valores = [float(v) for v in vals]
    return grupo


__all__ = ["MUESTRAS_MAX", "POLOS_MAX", "COLOR_REF", "COLOR_SIS", "COLOR_CTRL",
           "COLOR_MAL", "COLOR_OK", "COLOR_EJE", "C_REF", "C_SIS", "C_CTRL",
           "C_MAL", "C_OK", "C_EJE", "MasaResorte", "masa_resorte", "PlanoS",
           "plano_s", "Polo", "polo", "Respuesta", "respuesta_escalon",
           "LazoCerrado", "lazo_cerrado", "Rampa", "rampa_con_rezago",
           "Windup", "curva_windup", "barras_metricas"]
