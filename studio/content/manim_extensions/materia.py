"""Materia y materiales: del pozo de Lennard-Jones a la fatiga de un ala.

Pensado para el curso "Materiales que van al espacio". Todo el calculo es
numpy puro y determinista (`np.random.default_rng(semilla)` donde hace falta
azar, nunca el `random` global): mismo script -> mismo render, condicion
necesaria para trabajar con `--disable_caching`. Nada de red, nada de disco.

La regla de color del curso: el ATOMO y su enlace son ambar, el MATERIAL
protagonista cian, las FAMILIAS violeta, la FALLA roja, lo APTO verde; ejes y
mobiliario en el gris azulado `COLOR_EJE`. No mezclar roles.

Piezas:
    pozo LJ         curva U(r) con pared repulsiva, minimo y linea de r0
    atomos          par unido por un resorte, red 2D cizallable
    curva s-e       las cuatro familias sobre los MISMOS ejes
    Ashby           mapa log-log de densidad contra resistencia
    fatiga          curva S-N, grieta zigzag y placa con carga ciclica

Las piezas que exponen localizadores (`.punto_de`, `.fondo`, `.punto_en`,
`.burbuja`) los calculan sobre la geometria ACTUAL del mobject: siguen siendo
validos despues de mover o escalar. Asi los clips cuelgan puntos, tags y
flechas sin adivinar coordenadas.

Dos piezas cambian de forma despues de creadas (`ParAtomos.separar` y
`RedAtomica.cizallar`): las dos redibujan sus resortes leyendo la posicion
ACTUAL de los atomos, valen dentro de un updater y son idempotentes (volver
al valor inicial devuelve exactamente la figura inicial).

Topes duros para no castigar el VPS (2 vCPU / 2 GB por render): `ATOMOS_MAX`
y `MUESTRAS_MAX` levantan ValueError (a diferencia de fractales.py, que
recorta en silencio: aqui pasarse cambia lo que se ve, y es mejor enterarse).

Uso:
    import sys; sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from materia import pozo_lennard_jones, par_atomos, curva_esfuerzo

    pozo = pozo_lennard_jones(ancho=4.4, alto=2.0)
    punto = Dot(pozo.fondo(), radius=0.07, color="#22d3ee")
    self.add(pozo, punto)
    self.play(punto.animate.move_to(pozo.punto_de(1.35)))
"""

import numpy as np

from manim import (Circle, DashedVMobject, Dot, DoubleArrow, Ellipse, Line,
                   Polygon, RoundedRectangle, Text, VGroup, VMobject)

from code_brand import CODE_MUTED, FUENTE_HUD, registrar_fuentes

# Limites duros: pasarse levanta ValueError (ver docstring del modulo).
ATOMOS_MAX = 60         # atomos de una red (filas * columnas)
MUESTRAS_MAX = 400      # muestras maximas de una curva parametrica

# Paleta propia de la libreria (coincide con la del curso).
COLOR_ATOMO = "#f59e0b"     # EL ATOMO: enlaces, resortes, la curva del pozo
COLOR_MAT = "#22d3ee"       # EL MATERIAL protagonista, la propiedad destacada
COLOR_FAM = "#a78bfa"       # LAS FAMILIAS: alternativas, comparaciones
COLOR_FALLA = "#f43f5e"     # fractura, fatiga, degradacion
COLOR_OK = "#34d399"        # zona elastica, material apto
COLOR_EJE = "#31414f"       # mobiliario: ejes, rejillas, diagonales

# Alias cortos con los nombres de la tabla de paleta del curso, para que el
# style_block de los clips pueda escribir `color=C_ATOMO` tal cual.
C_ATOMO, C_MAT, C_FAM = COLOR_ATOMO, COLOR_MAT, COLOR_FAM
C_FALLA, C_OK, C_EJE = COLOR_FALLA, COLOR_OK, COLOR_EJE

_EPS = 1e-9
_X = np.array([1.0, 0.0, 0.0])
_Y = np.array([0.0, 1.0, 0.0])


# --- utilidades internas ----------------------------------------------
def _texto_hud(texto, font_size=14, color=COLOR_EJE):
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
    return max(16, n)


def _ejes_xy(ancho, alto, color_ejes, base_rel=0.0):
    """Par de ejes en L. `base_rel` sube el eje horizontal dentro de la caja.

    Con `base_rel=0` el eje x es el borde inferior de la caja (el caso normal
    de cualquier grafica); el pozo de Lennard-Jones lo sube a la altura de
    U = 0 para que la curva pueda hundirse POR DEBAJO del eje.
    """
    izq, abajo = -ancho / 2.0, -alto / 2.0
    y_eje = abajo + float(base_rel) * alto
    eje_x = Line((izq, y_eje, 0), (izq + ancho, y_eje, 0), stroke_width=2.4,
                 color=color_ejes)
    eje_y = Line((izq, abajo, 0), (izq, abajo + alto, 0), stroke_width=2.4,
                 color=color_ejes)
    return eje_x, eje_y, VGroup(eje_x, eje_y)


def _rotulos_ejes(eje_x, eje_y, texto_x, texto_y, color, font_size):
    """Nombres de los ejes: el de x centrado debajo, el de y girado a su lado.

    Girar el rotulo vertical (en vez de apilarlo horizontal) es lo unico que
    permite escribir "ESFUERZO" al lado de un eje de 2.6 unidades sin comerse
    media grafica.
    """
    rot_x = _texto_hud(texto_x, font_size=font_size - 2, color=color)
    rot_x.set_opacity(0.85)
    rot_x.move_to(np.array([float(eje_x.get_center()[0]),
                            float(eje_x.get_center()[1]) - 0.30, 0.0]))
    rot_y = _texto_hud(texto_y, font_size=font_size - 2, color=color)
    rot_y.set_opacity(0.85)
    rot_y.rotate(np.pi / 2.0)
    rot_y.move_to(np.array([float(eje_y.get_center()[0]) - 0.26,
                            float(eje_y.get_center()[1]), 0.0]))
    return VGroup(rot_x, rot_y)


def _puntos_zigzag(inicio, fin, picos=4, amplitud=0.10, cabo=0.14):
    """Vertices del resorte zigzag entre dos puntos de escena.

    Los `cabo` iniciales y finales son rectos (los "alambres" que entran al
    atomo) y el cuerpo alterna `2*picos` tramos a un lado y otro de la recta.
    Si el hueco es tan corto que no caben los cabos, estos se encogen: el
    resorte se comprime, nunca se da la vuelta.
    """
    p0 = np.asarray(inicio, dtype=np.float64)
    p1 = np.asarray(fin, dtype=np.float64)
    d = p1 - p0
    largo = float(np.linalg.norm(d))
    if largo < 1e-6:
        return [p0, p0 + np.array([1e-4, 0.0, 0.0])]

    u = d / largo
    n = np.array([-u[1], u[0], 0.0])
    c = min(float(cabo), largo * 0.30)
    a, b = p0 + u * c, p1 - u * c

    n_seg = 2 * int(max(1, picos))
    pts = [p0, a]
    for k in range(1, n_seg):
        signo = 1.0 if k % 2 else -1.0
        pts.append(a + (b - a) * (k / n_seg) + n * signo * float(amplitud))
    pts += [b, p1]
    return pts


def _redibujar_zigzag(resorte, inicio, fin, picos, amplitud, cabo):
    """Reescribe los vertices de un resorte YA existente, sin `become`.

    `become` sobre un VMobject vacio no copia los puntos: le cuelga el otro
    mobject como submobject (el alineado de familias mete un hijo nulo). Y
    aunque no lo hiciera, reescribir el array de puntos es lo unico barato
    cuando esto corre en cada frame de un updater.
    """
    resorte.set_points_as_corners(
        _puntos_zigzag(inicio, fin, picos=picos, amplitud=amplitud, cabo=cabo))
    return resorte


def _amplitud_resorte(largo, largo_ref, amplitud):
    """Amplitud del zigzag que se estrecha al estirar y se abre al comprimir.

    Un resorte real conserva el alambre: estirado se aplana. Sin esta
    correccion, al separar los atomos el zigzag se ve como una sierra suelta
    de la misma altura sobre un hueco tres veces mayor.
    """
    razon = float(largo_ref) / max(_EPS, float(largo))
    return float(amplitud) * float(np.clip(razon, 0.45, 1.35))


def _atomo(radio, color, brillo=True):
    """Nucleo solido + dos halos suaves: el atomo de todas las piezas."""
    radio = float(max(0.02, radio))
    piezas = []
    if brillo:
        for factor, opacidad in ((2.05, 0.09), (1.45, 0.18)):
            halo = Circle(radius=radio * factor, stroke_width=0)
            halo.set_fill(color=color, opacity=opacidad)
            piezas.append(halo)
    nucleo = Dot(radius=radio, color=color, fill_opacity=1.0)
    nucleo.set_stroke(width=0)
    piezas.append(nucleo)
    atomo = VGroup(*piezas)
    atomo.nucleo = nucleo
    atomo.radio_u = radio
    return atomo


# --- el pozo de Lennard-Jones -----------------------------------------
# Todo el pozo se calcula en unidades REDUCIDAS: rho = r / r0 (asi el minimo
# cae en rho = 1, que es lo que `.punto_de(1)` promete) y U en unidades de
# eps, de modo que U(rho) = rho^-12 - 2 rho^-6 y el fondo vale exactamente -1.
_U_ALTO = 1.9       # tope de la pared repulsiva (satura arriba de la caja)
_U_BAJO = -1.30     # suelo de la caja: deja aire debajo del minimo (-1)
_RHO_MAX = 1.95     # cola atractiva hasta casi tocar U = 0
# rho donde U vale _U_ALTO: raiz de x^2 - 2x - U = 0 con x = rho^-6.
_RHO_MIN = float((1.0 + np.sqrt(1.0 + _U_ALTO)) ** (-1.0 / 6.0))


def _u_lj(rho):
    """Potencial de Lennard-Jones reducido: minimo -1 exacto en rho = 1."""
    inv6 = np.asarray(rho, dtype=np.float64) ** -6.0
    return inv6 * inv6 - 2.0 * inv6


class PozoLJ(VGroup):
    """Pozo de Lennard-Jones con localizadores (lo crea `pozo_lennard_jones`).

    El eje horizontal es r (en unidades de r0, la distancia de equilibrio) y
    el vertical U. El eje de r esta a la altura de U = 0, asi que el pozo se
    hunde POR DEBAJO de el, como en cualquier figura del tema.

    `.punto_de()` y `.fondo()` leen la geometria ACTUAL (posicion y tamaño de
    los ejes), asi que siguen siendo validos despues de mover o escalar.
    """

    def _caja(self):
        """(x_izq, y_abajo, ancho, alto) de la caja del pozo, ahora mismo."""
        return (float(self.eje_u.get_center()[0]),
                float(self.eje_u.get_bottom()[1]),
                float(self.eje_r.width), float(self.eje_u.height))

    def punto_de(self, r_rel):
        """Coordenada de escena del punto de la curva a r = `r_rel` * r0.

        `r_rel` = 1 es el fondo del pozo; por debajo de ~0.85 la pared ya
        salio del cuadro, asi que el valor se recorta al dominio dibujado.
        """
        rho = float(np.clip(r_rel, _RHO_MIN, _RHO_MAX))
        u = float(np.clip(_u_lj(rho), _U_BAJO, _U_ALTO))
        x0, y0, ancho, alto = self._caja()
        fx = (rho - _RHO_MIN) / (_RHO_MAX - _RHO_MIN)
        fy = (u - _U_BAJO) / (_U_ALTO - _U_BAJO)
        return np.array([x0 + fx * ancho, y0 + fy * alto, 0.0])

    def fondo(self):
        """Coordenada de escena del minimo del pozo (r = r0, U = -eps)."""
        return self.punto_de(1.0)


def pozo_lennard_jones(ancho=4.8, alto=2.8, color=COLOR_ATOMO,
                       color_ejes=COLOR_EJE, font_size=14, muestras=240):
    """Ejes (r ->, U ^) + la curva 4eps[(s/r)^12 - (s/r)^6] + la linea de r0.

    La pared repulsiva es casi vertical: se RECORTA arriba (en U = 1.9 eps)
    para que quepa en el alto declarado, de modo que la curva entra por la
    esquina superior izquierda, cae al minimo y sale por la derecha con la
    cola atractiva pegada a U = 0. El muestreo se aprieta hacia la izquierda
    (t^1.4) porque ahi la curva gasta casi todo su desnivel.

    La linea punteada vertical marca r0 (el fondo). El grupo se centra en
    ORIGIN: para colocarlo, `.move_to(...)` normal.
    """
    muestras = _validar_muestras("pozo_lennard_jones", muestras)
    ancho, alto = float(max(0.6, ancho)), float(max(0.6, alto))
    base_rel = (0.0 - _U_BAJO) / (_U_ALTO - _U_BAJO)     # altura de U = 0

    eje_r, eje_u, ejes = _ejes_xy(ancho, alto, color_ejes, base_rel=base_rel)
    pozo = PozoLJ(ejes)
    pozo.ejes, pozo.eje_r, pozo.eje_u = ejes, eje_r, eje_u

    # rho = 1 va SIEMPRE en la malla: asi la curva dibujada pasa exactamente
    # por el punto que devuelve `.fondo()`, sin desfase de unas milesimas.
    t = np.linspace(0.0, 1.0, muestras) ** 1.4
    rhos = np.unique(np.append(_RHO_MIN + t * (_RHO_MAX - _RHO_MIN), 1.0))
    curva = _curva(np.array([pozo.punto_de(r)[:2] for r in rhos]), color,
                   grosor=3.4)

    fondo = pozo.fondo()
    r0_linea = DashedVMobject(
        Line(np.array([fondo[0], -alto / 2.0, 0.0]),
             np.array([fondo[0], -alto / 2.0 + base_rel * alto + 0.10, 0.0]),
             stroke_width=2.0, color=color_ejes), num_dashes=13)
    r0_linea.set_stroke(opacity=0.9)

    etiqueta_r0 = _texto_hud("r0", font_size=font_size, color=CODE_MUTED)
    etiqueta_r0.set_opacity(0.9)
    etiqueta_r0.next_to(r0_linea, np.array([1.0, 0.0, 0.0]), buff=0.08)
    etiqueta_r0.shift(np.array([0.0, -alto * 0.34, 0.0]))
    etiqueta_r = _texto_hud("r", font_size=font_size, color=color_ejes)
    etiqueta_r.move_to(np.array([ancho / 2.0 + 0.02,
                                 -alto / 2.0 + base_rel * alto - 0.26, 0.0]))
    etiqueta_u = _texto_hud("U", font_size=font_size, color=color_ejes)
    etiqueta_u.move_to(np.array([-ancho / 2.0 - 0.24, alto / 2.0 - 0.02, 0.0]))
    etiquetas = VGroup(etiqueta_r0, etiqueta_r, etiqueta_u)

    pozo.add(r0_linea, curva, etiquetas)
    pozo.curva, pozo.r0_linea, pozo.etiquetas = curva, r0_linea, etiquetas
    return pozo


# --- el par de atomos -------------------------------------------------
class ParAtomos(VGroup):
    """Dos atomos unidos por un resorte (lo crea `par_atomos`).

    El atomo IZQUIERDO es el ancla: `.separar(d)` solo mueve el derecho, a lo
    largo del eje que hoy une los dos centros (asi el par se puede rotar y
    seguir funcionando). El resorte se redibuja desde las posiciones ACTUALES
    de los atomos, de modo que llamarla en cada frame de un updater es lo
    esperado y volver a la separacion inicial devuelve la figura inicial.
    """

    def eje(self):
        """Vector unitario del atomo ancla al movil, leido de la geometria."""
        d = (np.asarray(self.b.nucleo.get_center(), dtype=np.float64) -
             np.asarray(self.a.nucleo.get_center(), dtype=np.float64))
        largo = float(np.linalg.norm(d))
        return d / largo if largo > _EPS else _X.copy()

    def _redibujar(self):
        ca = np.asarray(self.a.nucleo.get_center(), dtype=np.float64)
        cb = np.asarray(self.b.nucleo.get_center(), dtype=np.float64)
        u = self.eje()
        borde = self.radio * 1.25
        p0, p1 = ca + u * borde, cb - u * borde
        largo = max(_EPS, float(np.linalg.norm(p1 - p0)))
        _redibujar_zigzag(
            self.resorte, p0, p1, self.picos,
            _amplitud_resorte(largo, self.largo_ref, self.amplitud),
            self.radio * 0.5)
        return self

    def separar(self, d):
        """Deja los centros a `d` unidades de escena y redibuja el resorte.

        Se mueve por la DIFERENCIA con la separacion actual, no en absoluto:
        llamarla dos veces con el mismo valor no mueve nada.
        """
        objetivo = float(max(self.radio * 2.2, float(d)))
        u = self.eje()
        delta = objetivo - float(self.separacion)
        if abs(delta) > 1e-12:
            self.b.shift(u * delta)
        self.separacion = objetivo
        return self._redibujar()


def par_atomos(separacion=1.6, radio=0.28, color=COLOR_ATOMO,
               color_resorte=None):
    """Dos atomos con halo unidos por un resorte zigzag corto.

    Nace horizontal y centrado en ORIGIN. El resorte es del mismo ambar que
    los atomos (es el ENLACE, no mobiliario), salvo que se pida otro color.
    """
    separacion = float(max(0.2, separacion))
    radio = float(max(0.04, radio))

    a = _atomo(radio, color).shift(-_X * separacion / 2.0)
    b = _atomo(radio, color).shift(+_X * separacion / 2.0)
    resorte = VMobject(color=(color if color_resorte is None else color_resorte),
                       stroke_width=2.6)

    par = ParAtomos(resorte, a, b)      # el resorte va DEBAJO de los atomos
    par.a, par.b, par.resorte = a, b, resorte
    par.radio = radio
    par.separacion = separacion
    par.largo_ref = max(_EPS, separacion - 2.0 * radio * 1.25)
    par.amplitud = radio * 0.62
    par.picos = 4
    par.color_resorte = color if color_resorte is None else color_resorte
    return par._redibujar()


# --- la red atomica ---------------------------------------------------
class RedAtomica(VGroup):
    """Malla de atomos y resortes cizallable (la crea `red_atomica`).

    `.cizallar(dx)` desplaza cada fila en horizontal de forma proporcional a
    su ALTURA en la red (la fila de abajo no se mueve, la de arriba se mueve
    `dx` entero) y redibuja todos los resortes desde las posiciones ACTUALES
    de los atomos: es la deformacion elastica de cizalla de libro.

    Se mueve por la DIFERENCIA con la cizalla actual, asi que se puede llamar
    tantas veces como se quiera (tambien desde un updater, frame a frame) y
    `cizallar(0)` devuelve exactamente la red original.
    """

    def atomo(self, fila, columna):
        """Atomo (VGroup) de la fila `fila` (0 = la de arriba) y columna."""
        return self.filas_atomos[int(fila)][int(columna)]

    def _redibujar(self):
        for resorte, a, b, largo_ref in self._enlaces:
            ca = np.asarray(a.nucleo.get_center(), dtype=np.float64)
            cb = np.asarray(b.nucleo.get_center(), dtype=np.float64)
            d = cb - ca
            largo = float(np.linalg.norm(d))
            u = d / largo if largo > _EPS else _X.copy()
            borde = self.radio * 1.2
            p0, p1 = ca + u * borde, cb - u * borde
            hueco = max(_EPS, float(np.linalg.norm(p1 - p0)))
            _redibujar_zigzag(
                resorte, p0, p1, 3,
                _amplitud_resorte(hueco, largo_ref, self.amplitud),
                self.radio * 0.6)
        return self

    def cizallar(self, dx):
        """Cizalla la red: la fila superior se corre `dx` en horizontal."""
        objetivo = float(dx)
        delta = objetivo - float(self.cizalla)
        if abs(delta) > 1e-12:
            for fila, factor in zip(self.filas_atomos, self._factores):
                if factor > 0.0:
                    fila.shift(_X * delta * factor)
        self.cizalla = objetivo
        return self._redibujar()


def red_atomica(filas=4, columnas=6, paso=0.62, color=COLOR_ATOMO,
                color_resorte=COLOR_EJE):
    """Rejilla de atomos unidos por resortes horizontales y verticales.

    La fila 0 es la de ARRIBA (es la que mas se mueve al cizallar). Los
    resortes verticales son los que se inclinan con la cizalla; los
    horizontales solo se trasladan, igual que en el cristal real.

    El grupo se centra en ORIGIN. Tope: `filas * columnas <= ATOMOS_MAX`.
    """
    filas, columnas = int(max(1, filas)), int(max(1, columnas))
    total = filas * columnas
    if total > ATOMOS_MAX:
        raise ValueError(
            f"red_atomica: filas*columnas={total} supera "
            f"ATOMOS_MAX={ATOMOS_MAX}")
    paso = float(max(0.12, paso))
    radio = paso * 0.155

    ancho = (columnas - 1) * paso
    alto = (filas - 1) * paso

    filas_atomos = VGroup()
    for i in range(filas):
        fila = VGroup()
        for j in range(columnas):
            pos = np.array([-ancho / 2.0 + j * paso,
                            alto / 2.0 - i * paso, 0.0])
            fila.add(_atomo(radio, color).shift(pos))
        filas_atomos.add(fila)

    resortes = VGroup()
    enlaces = []
    largo_ref = max(_EPS, paso - 2.0 * radio * 1.2)
    for i in range(filas):
        for j in range(columnas):
            actual = filas_atomos[i][j]
            vecinos = []
            if j + 1 < columnas:
                vecinos.append(filas_atomos[i][j + 1])
            if i + 1 < filas:
                vecinos.append(filas_atomos[i + 1][j])
            for vecino in vecinos:
                resorte = VMobject(color=color_resorte, stroke_width=1.8)
                resortes.add(resorte)
                enlaces.append((resorte, actual, vecino, largo_ref))

    # Los resortes van DEBAJO de los atomos: al comprimirse, el zigzag nunca
    # asoma por encima de un nucleo.
    red = RedAtomica(resortes, filas_atomos)
    red.atomos, red.resortes = filas_atomos, resortes
    red.filas_atomos = filas_atomos
    red.filas, red.columnas, red.paso = filas, columnas, paso
    red.radio = radio
    red.amplitud = paso * 0.11
    red.color_resorte = color_resorte
    red.cizalla = 0.0
    red._enlaces = enlaces
    # Factor de arrastre por fila: 1 arriba, 0 abajo (proporcional a la altura).
    red._factores = [1.0 if filas == 1 else (filas - 1 - i) / (filas - 1)
                     for i in range(filas)]
    return red._redibujar()


# --- la curva esfuerzo-deformacion ------------------------------------
# Cada familia es una poligonal en coordenadas RELATIVAS (x = deformacion, y =
# esfuerzo, ambas en [0, 1] sobre la misma caja): asi las cuatro comparten
# ejes y escala y un ReplacementTransform entre dos de ellas se lee como una
# comparacion honesta, no como un cambio de zoom.
#
#   "elastico"  x_rel donde termina el tramo recto (la base de .zona_elastica)
#   "falla"     True si la familia se corta en seco (marca X roja al final)
_FAMILIAS = {
    "metal": {
        "puntos": [(0.000, 0.000), (0.085, 0.460), (0.108, 0.532),
                   (0.150, 0.575), (0.260, 0.630), (0.420, 0.700),
                   (0.545, 0.722), (0.635, 0.690), (0.712, 0.588)],
        "elastico": 0.085, "falla": False},
    "ceramico": {
        "puntos": [(0.000, 0.000), (0.130, 0.860)],
        "elastico": 0.130, "falla": True},
    "polimero": {
        "puntos": [(0.000, 0.000), (0.052, 0.150), (0.090, 0.196),
                   (0.260, 0.228), (0.520, 0.252), (0.760, 0.290),
                   (0.900, 0.352), (0.955, 0.400)],
        "elastico": 0.052, "falla": False},
    "compuesto": {
        "puntos": [(0.000, 0.000), (0.150, 0.500), (0.260, 0.856),
                   (0.302, 0.980)],
        "elastico": 0.260, "falla": True},
}


class CurvaSigmaEps(VGroup):
    """Curva esfuerzo-deformacion de una familia (la crea `curva_esfuerzo`).

    `.punto_en(t_rel)` recorre la curva DIBUJADA de principio (t=0, el
    origen) a fin (t=1, la rotura), leyendo el origen y el tamaño ACTUALES de
    los ejes: sirve igual antes y despues de mover o escalar el grupo.

    `.zona_elastica` nace INVISIBLE (opacity 0) y vive dentro del grupo, para
    que acompañe a la curva si el clip la mueve. Sobre un mobject ya invisible
    `FadeIn` no tiene nada que interpolar, asi que se enciende con
    `.abrir_zona()`.
    """

    def _origen(self):
        return np.asarray(self.eje_x.get_start(), dtype=np.float64)

    def punto_en(self, t_rel):
        """Coordenada de escena del punto de la curva en `t_rel` de [0, 1]."""
        t = float(np.clip(t_rel, 0.0, 1.0))
        x_rel = t * self.x_fin
        y_rel = float(np.interp(x_rel, self._xs, self._ys))
        return self._origen() + np.array([x_rel * float(self.eje_x.width),
                                          y_rel * float(self.eje_y.height),
                                          0.0])

    def abrir_zona(self):
        """Lista de animaciones que encienden la zona elastica verde.

            self.play(*curva.abrir_zona(), run_time=0.7)
        """
        return [self.zona_elastica.animate
                .set_fill(color=COLOR_OK, opacity=0.22)
                .set_stroke(color=COLOR_OK, opacity=0.55)]


def curva_esfuerzo(familia="metal", ancho=4.6, alto=2.6, color=COLOR_MAT,
                   color_ejes=COLOR_EJE, font_size=14, muestras=180):
    """Ejes (deformacion ->, esfuerzo ^) + la curva tipica de una familia.

    Las cuatro familias comparten caja y escala:
        "metal"      recta elastica, codo de fluencia, meseta ductil y caida
        "ceramico"   recta empinada que se corta en seco (X roja al final)
        "polimero"   curva baja y muy larga, con endurecimiento tardio
        "compuesto"  casi recta hasta arriba y corte seco (X roja)

    `.zona_elastica` es el triangulo verde bajo el tramo recto inicial, que
    nace invisible (ver `.abrir_zona`). `.marca_falla` es la X roja de las
    familias que revientan sin avisar, o None.

    El grupo se centra en ORIGIN.
    """
    clave = str(familia).lower().strip()
    if clave not in _FAMILIAS:
        raise ValueError(
            f"curva_esfuerzo: familia={familia!r} desconocida; use una de "
            f"{sorted(_FAMILIAS)}")
    muestras = _validar_muestras("curva_esfuerzo", muestras)
    ancho, alto = float(max(0.6, ancho)), float(max(0.6, alto))
    receta = _FAMILIAS[clave]

    eje_x, eje_y, ejes = _ejes_xy(ancho, alto, color_ejes)
    c = CurvaSigmaEps(ejes)
    c.ejes, c.eje_x, c.eje_y = ejes, eje_x, eje_y
    c.familia = clave

    quiebres = np.asarray(receta["puntos"], dtype=np.float64)
    c._xs, c._ys = quiebres[:, 0], quiebres[:, 1]
    c.x_fin = float(c._xs[-1])
    c.x_elastico = float(receta["elastico"])

    etiquetas = _rotulos_ejes(eje_x, eje_y, "DEFORMACION", "ESFUERZO",
                              color_ejes, font_size)

    # La zona elastica va ANTES que la curva en el grupo (queda por debajo).
    p_elastico = c.punto_en(c.x_elastico / c.x_fin)
    origen = c._origen()
    zona = Polygon(origen, np.array([p_elastico[0], origen[1], 0.0]),
                   p_elastico, stroke_width=1.6)
    zona.set_fill(color=COLOR_OK, opacity=0.0)
    zona.set_stroke(color=COLOR_OK, opacity=0.0)
    c.zona_elastica = zona
    c.opacidad_zona = 0.22

    # Los quiebres entran SIEMPRE en la malla de muestreo: el codo de fluencia
    # cae donde lo pone la receta, no donde lo deje el redondeo del linspace.
    xs = np.unique(np.append(np.linspace(0.0, c.x_fin, muestras), c._xs))
    curva = _curva(np.array([c.punto_en(x / c.x_fin)[:2] for x in xs]), color,
                   grosor=3.6)

    marca = None
    if receta["falla"]:
        fin = c.punto_en(1.0)
        brazo = 0.13
        marca = VGroup(*[
            Line(fin + np.array([-brazo * sx, -brazo, 0.0]),
                 fin + np.array([brazo * sx, brazo, 0.0]),
                 stroke_width=4.4, color=COLOR_FALLA)
            for sx in (1.0, -1.0)])
        marca.set_z_index(4)

    c.add(zona, curva, etiquetas)
    if marca is not None:
        c.add(marca)
    c.curva, c.etiquetas, c.marca_falla = curva, etiquetas, marca
    return c


# --- el mapa de Ashby -------------------------------------------------
# (x_rel, y_rel, ancho_rel, alto_rel, giro_deg) de cada barrio del mapa. Las
# posiciones son las del mapa real: los polimeros abajo a la izquierda
# (ligeros y flojos), los ceramicos arriba a la derecha (fuertes y pesados) y
# los compuestos ARRIBA A LA IZQUIERDA, el barrio dorado.
_BARRIOS = (
    ("POLIMEROS", 0.215, 0.200, 0.355, 0.215, -14.0, COLOR_FAM),
    ("METALES", 0.660, 0.510, 0.345, 0.205, 12.0, COLOR_FAM),
    ("CERAMICOS", 0.755, 0.830, 0.320, 0.190, -9.0, COLOR_FAM),
    ("COMPUESTOS", 0.290, 0.775, 0.360, 0.205, 15.0, COLOR_MAT),
)


class MapaAshby(VGroup):
    """Mapa densidad-resistencia con burbujas por familia (lo crea
    `mapa_ashby`). `.burbuja(nombre)` devuelve el VGroup elipse + etiqueta."""

    def burbuja(self, nombre):
        """Burbuja de una familia por nombre (sin distinguir mayusculas)."""
        clave = str(nombre).upper().strip()
        if clave not in self.burbujas:
            raise ValueError(
                f"mapa_ashby.burbuja: {nombre!r} no esta en el mapa; use una "
                f"de {sorted(self.burbujas)}")
        return self.burbujas[clave]

    def punto_rel(self, x_rel, y_rel):
        """Coordenada de escena de (x_rel, y_rel) en [0, 1] de la caja."""
        origen = np.asarray(self.eje_x.get_start(), dtype=np.float64)
        return origen + np.array([float(x_rel) * float(self.eje_x.width),
                                  float(y_rel) * float(self.eje_y.height),
                                  0.0])


def mapa_ashby(ancho=4.9, alto=3.0, font_size=14, color_ejes=COLOR_EJE):
    """Mapa de Ashby log-log: densidad (->) contra resistencia (^).

    Cuatro burbujas elipticas etiquetadas, ligeramente giradas para que se
    lean como nubes de datos y no como iconos: POLIMEROS abajo-izquierda,
    METALES al centro-derecha, CERAMICOS arriba-derecha (los tres violeta) y
    COMPUESTOS arriba-IZQUIERDA en cian, el barrio dorado (fuerte y ligero).

    Las dos diagonales punteadas son lineas de sigma/rho constante: sobre una
    misma diagonal, todos los materiales rinden igual POR GRAMO.

    El grupo se centra en ORIGIN.
    """
    ancho, alto = float(max(0.8, ancho)), float(max(0.8, alto))
    eje_x, eje_y, ejes = _ejes_xy(ancho, alto, color_ejes)

    mapa = MapaAshby(ejes)
    mapa.ejes, mapa.eje_x, mapa.eje_y = ejes, eje_x, eje_y

    etiquetas = _rotulos_ejes(eje_x, eje_y, "DENSIDAD (LOG)",
                              "RESISTENCIA (LOG)", color_ejes, font_size)

    # Diagonales de sigma/rho constante: paralelas, a 45 grados de la CAJA
    # (no de la pantalla), asi que se ven iguales con cualquier proporcion.
    diagonales = VGroup()
    for corte in (0.30, -0.28):
        p0 = mapa.punto_rel(max(0.0, -corte), max(0.0, corte))
        p1 = mapa.punto_rel(min(1.0, 1.0 - corte), min(1.0, 1.0 + corte))
        linea = DashedVMobject(Line(p0, p1, stroke_width=1.8,
                                    color=color_ejes), num_dashes=22)
        linea.set_stroke(opacity=0.85)
        diagonales.add(linea)

    burbujas = VGroup()
    mapa.burbujas = {}
    for nombre, x_rel, y_rel, w_rel, h_rel, giro, color in _BARRIOS:
        elipse = Ellipse(width=w_rel * ancho, height=h_rel * alto,
                         stroke_width=2.2, color=color)
        elipse.set_fill(color=color, opacity=0.18)
        elipse.rotate(np.deg2rad(giro))
        elipse.move_to(mapa.punto_rel(x_rel, y_rel))

        rotulo = _texto_hud(nombre, font_size=font_size - 2, color=color)
        # El rotulo NUNCA se sale de su burbuja: si el nombre es largo, se
        # encoge hasta caber en el 76% del ancho de la elipse.
        tope = w_rel * ancho * 0.76
        if float(rotulo.width) > tope:
            rotulo.scale_to_fit_width(tope)
        rotulo.move_to(elipse.get_center())
        rotulo.set_z_index(5)

        burbuja = VGroup(elipse, rotulo)
        burbuja.elipse, burbuja.rotulo, burbuja.nombre = elipse, rotulo, nombre
        burbujas.add(burbuja)
        mapa.burbujas[nombre] = burbuja

    mapa.add(diagonales, burbujas, etiquetas)
    mapa.diagonales, mapa.grupo_burbujas = diagonales, burbujas
    mapa.etiquetas = etiquetas
    return mapa


# --- la fatiga --------------------------------------------------------
class CurvaSN(VGroup):
    """Curva de fatiga S-N con su limite (la crea `curva_sn`).

    `.punto_en(t_rel)` cae SOBRE la curva dibujada y se calcula con el origen
    y el tamaño ACTUALES de los ejes.
    """

    def _y_rel(self, t_rel):
        """Amplitud normalizada en `t_rel` de [0, 1]: cae con codo al limite.

        Exponencial estirada: alta y casi plana al principio (unos pocos
        ciclos aguantan casi cualquier carga), codo marcado hacia el primer
        tercio y asintota al limite de fatiga por la derecha.
        """
        t = float(np.clip(t_rel, 0.0, 1.0))
        caida = float(np.exp(-3.4 * t ** 1.25))
        return float(self.limite_rel + (self.y0_rel - self.limite_rel) * caida)

    def punto_en(self, t_rel):
        """Coordenada de escena del punto de la curva en `t_rel` de [0, 1]."""
        origen = np.asarray(self.eje_x.get_start(), dtype=np.float64)
        return origen + np.array([
            float(np.clip(t_rel, 0.0, 1.0)) * float(self.eje_x.width),
            self._y_rel(t_rel) * float(self.eje_y.height), 0.0])


def curva_sn(ancho=4.8, alto=2.4, color=COLOR_FALLA, color_ejes=COLOR_EJE,
             font_size=14, muestras=160):
    """Ejes (ciclos log ->, amplitud ^) + la curva S-N y su limite de fatiga.

    La curva baja desde la resistencia estatica, dobla el codo y se acuesta
    sobre la linea punteada horizontal del limite: por debajo de esa
    amplitud, la pieza no acumula daño. El grupo se centra en ORIGIN.
    """
    muestras = _validar_muestras("curva_sn", muestras)
    ancho, alto = float(max(0.6, ancho)), float(max(0.6, alto))
    eje_x, eje_y, ejes = _ejes_xy(ancho, alto, color_ejes)

    sn = CurvaSN(ejes)
    sn.ejes, sn.eje_x, sn.eje_y = ejes, eje_x, eje_y
    sn.y0_rel, sn.limite_rel = 0.90, 0.27

    origen = np.asarray(eje_x.get_start(), dtype=np.float64)
    # La linea del limite nace en el gris del mobiliario: en el clip PULSA
    # verde (`Indicate(sn.limite, color=C_OK)`), y un verde de fabrica se
    # comeria ese golpe de atencion.
    limite = DashedVMobject(
        Line(origen + np.array([0.0, sn.limite_rel * alto, 0.0]),
             origen + np.array([ancho, sn.limite_rel * alto, 0.0]),
             stroke_width=2.2, color=color_ejes), num_dashes=26)
    limite.set_stroke(opacity=0.95)

    ts = np.linspace(0.0, 1.0, muestras)
    curva = _curva(np.array([sn.punto_en(t)[:2] for t in ts]), color,
                   grosor=3.4)

    etiquetas = _rotulos_ejes(eje_x, eje_y, "CICLOS (LOG)", "AMPLITUD",
                              color_ejes, font_size)
    # El rotulo va DEBAJO de la linea del limite: por encima lo cruza la cola
    # de la curva, que justamente se acuesta sobre ese nivel.
    tag_limite = _texto_hud("LIMITE DE FATIGA", font_size=font_size - 2,
                            color=CODE_MUTED)
    tag_limite.set_opacity(0.9)
    tag_limite.move_to(origen + np.array([ancho - float(tag_limite.width) / 2.0
                                          - 0.10,
                                          sn.limite_rel * alto - 0.22, 0.0]))
    etiquetas.add(tag_limite)

    sn.add(limite, curva, etiquetas)
    sn.curva, sn.limite, sn.etiquetas = curva, limite, etiquetas
    sn.tag_limite = tag_limite
    return sn


def grieta(largo=1.4, dientes=7, color=COLOR_FALLA, semilla=11):
    """Zigzag de grieta, listo para crecer con `Create`.

    Nace horizontal y centrado en ORIGIN: la BOCA es el extremo izquierdo (el
    borde de la pieza) y la PUNTA el derecho, asi que `Create` la dibuja en el
    sentido en que crece. La amplitud se estrecha hacia la punta, que es como
    se ve una grieta real, y el desorden es determinista (`semilla`).

    Para una grieta vertical, `.rotate(PI/2)`; para una que entre por el
    borde derecho, `.rotate(PI)`.
    """
    largo = float(max(0.1, largo))
    n = int(max(2, dientes))
    rng = np.random.default_rng(int(semilla))

    amp = largo * 0.085
    puntos = [np.array([-largo / 2.0, 0.0, 0.0])]
    for k in range(1, n + 1):
        t = k / n
        # El diente se encoge hacia la punta y lleva un jitter reproducible.
        escala = (1.0 - 0.72 * t) * (0.65 + 0.7 * float(rng.random()))
        signo = 1.0 if k % 2 else -1.0
        x = -largo / 2.0 + largo * (t - 0.5 / n * float(rng.random()))
        puntos.append(np.array([x, signo * amp * escala, 0.0]))
    puntos.append(np.array([largo / 2.0, 0.0, 0.0]))

    g = VMobject(color=color, stroke_width=3.2)
    g.set_points_as_corners(puntos)
    return g


def placa_con_ciclos(ancho=2.6, alto=1.5, color="#94a0b0",
                     color_flechas=COLOR_FALLA):
    """Placa redondeada con la carga ciclica dibujada encima.

    Dos flechas dobles verticales (arriba y abajo a la vez) sobre la placa:
    la carga que sube y baja miles de veces sin romper nada de golpe. Para
    los pulsos del clip basta con `Indicate(placa.flechas)`.

    El grupo se centra en ORIGIN (placa + flechas).
    """
    ancho, alto = float(max(0.3, ancho)), float(max(0.3, alto))

    placa = RoundedRectangle(corner_radius=min(0.18, alto * 0.18),
                             width=ancho, height=alto, stroke_width=2.6,
                             color=color)
    placa.set_fill(color=color, opacity=0.14)

    largo_flecha = min(0.9, alto * 0.62)
    flechas = VGroup()
    for signo in (-1.0, 1.0):
        x = signo * ancho * 0.26
        base = alto / 2.0 + 0.16
        flecha = DoubleArrow(
            np.array([x, base, 0.0]),
            np.array([x, base + largo_flecha, 0.0]),
            buff=0.0, color=color_flechas, stroke_width=3.4,
            tip_length=0.16, max_tip_length_to_length_ratio=0.4)
        flechas.add(flecha)

    grupo = VGroup(placa, flechas)
    grupo.placa, grupo.flechas = placa, flechas
    grupo.move_to(np.array([0.0, 0.0, 0.0]))
    return grupo
