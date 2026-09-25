# =====================================================================
# CO.DE Academy - "Rendimiento SQL · 4.1 No envuelvas la columna".
# Bloque de estilo del proyecto: se antepone al script de CADA clip; los
# clips NO repiten imports, solo definen su ClipN(Scene).
#
# Copia del MOLDE (1.1) de la familia "Rendimiento SQL" (curso 37, 21 lecciones). Entre
# dos lecciones solo cambian la cabecera y el bloque "--- Numeros de la
# leccion ---". FORMATO MUDO (sin pie narrativo, guardian `_vigilar()`)
# y SIN "Modulo 0N": hud_modulo() ABORTA el render.
#
# Publico general de YouTube: nada de referencias a un curso presencial
# (sesion, demo, script, laboratorio). La base es "la tienda".
# =====================================================================
import math
import sys

sys.path.insert(0, "/workspace/studio/content/manim_extensions")

import numpy as np
from manim import *

import code_brand as _code_brand
from brillo import con_brillo, punto_brillante
from code_brand import (CODE_ACCENT, CODE_ACCENT_2, CODE_BG, CODE_INK,
                        CODE_MUTED, FUENTE_DISPLAY, FUENTE_HUD, Rotulos,
                        esquinas_hud, etiqueta_hud, marca_agua,
                        registrar_fuentes, titulo_marca)

import sqlperf as S

# --- Tipografia de marca ---------------------------------------------
registrar_fuentes()
Text.set_default(font=FUENTE_DISPLAY)

_TextBase = Text


class Text(_TextBase):
    """Sombra de Text que descarta los glifos vacios (espacios): el glifo
    del espacio queda anclado donde nacio el texto e infla el bounding box
    (bug de manim 0.20.1)."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.submobjects = [s for s in self.submobjects if s.has_points()]


_code_brand.Text = Text
_RotulosBase = Rotulos


class Rotulos(_RotulosBase):
    """Relevo SECUENCIAL por zona: el rotulo anterior sale ANTES de que
    entre el nuevo."""

    def mostrar(self, mobjeto, zona="abajo", run_time=0.42, salida=0.22,
                **kwargs):
        if self._zonas.get(zona) is not None:
            self.limpiar(zona, run_time=salida)
        return super().mostrar(mobjeto, zona=zona, run_time=run_time,
                               **kwargs)


config.background_color = CODE_BG

# --- Paleta del curso: el color dice el PAPEL -------------------------
# Cian = calculado aqui (conteo sobre la reproduccion de la tienda o
# modelo). AMBAR = medido por SQL Server 2025 (lecturas, paginas,
# segundos): SOLO eso va en ambar. Gris = dato publico.
C_TITULO = CODE_INK
C_TENUE = CODE_MUTED
C_CALCULO = S.CIAN
C_MOTOR = S.AMBAR
C_DATO = "#94a0b0"
C_BUENO = S.VERDE        # el camino barato: seek, plan bueno
C_MALO = S.ROJO          # el camino caro: scan de mas, plan malo
C_INDICE = S.AZUL        # un indice (estructura) y palabras clave
C_CREE = S.VIOLETA       # lo que el optimizador CREE (estimacion)

MARGEN_PIE = 0.62

# --- EL GUARDIAN DEL FORMATO MUDO -------------------------------------
MAX_TITULO = 6
MAX_CIFRA = 5
MAX_TAG = 4
FS_MIN_DISPLAY = 18
FS_MIN_MULTI = 22            # Rajdhani junta palabras por debajo de 22 px


def _palabras(texto):
    return [p for p in str(texto).split() if any(c.isalnum() for c in p)]


def _vigilar(texto, maximo, quien):
    n = len(_palabras(texto))
    if n > maximo:
        raise ValueError(
            f"FORMATO MUDO: {quien} admite {maximo} palabras y le llegaron "
            f"{n}: {texto!r}. La frase va en la NARRACION, no en pantalla.")
    return texto


def fmt(x, dec=1):
    """Numero con `dec` decimales, sin rstrip (se come ceros de enteros)."""
    return f"{float(x):.{dec}f}"


# --- Numeros de la leccion --------------------------------------------
# (este bloque y "Dibujo compartido" son los UNICOS que cambian entre
# lecciones; toda cifra sale de sqlperf: S.MEDIDO = motor, S.* = calculo)
M = S.MEDIDO
FILAS_PED = M["filas_pedidos"]                                  # 1,500,000

# clip 1: el indice ordenado por fecha_pedido, un tramo por anio (ancho
# real: filas de ese anio sobre pedidos_por_dia, no un numero inventado)
_DIAS_POR_DIA, _CONTEO_POR_DIA = S.pedidos_por_dia()
ANIOS = list(range(2021, 2027))


def _filas_anio(anio):
    ini = min(S.dia(f"{anio}-01-01"), len(_CONTEO_POR_DIA))
    fin = min(S.dia(f"{anio + 1}-01-01"), len(_CONTEO_POR_DIA))
    return int(_CONTEO_POR_DIA[ini:fin].sum())


FILAS_ANIO = {a: _filas_anio(a) for a in ANIOS}
# 2021: 46,602 · 2022: 139,560 · 2023: 232,391 · 2024: 325,705
# 2025: 418,481 (= S.filas_rango del propio 2025) · 2026 (parcial): 337,261

# clip 2: YEAR(fecha_pedido) envuelve la columna: el motor ya no puede
# usar el indice como rango y lo recorre entero
RANGO_2025 = S.filas_rango("2025-01-01", "2026-01-01")          # 418,481 (cian)

# clip 3: CAST se convierte en rango, CONVERT(CHAR) no
FILAS_DIA_CAST = S.filas_dia("2026-09-01")                      # (cian)

# clip 4: mover el DATEADD al otro lado del ">"
RAZON_DATEADD = S.razon(M["dateadd_mal"], M["dateadd_bien"])    # ~31.6
# fraccion de la lista que queda del lado correcto del rango final
# (fecha_pedido > '2026-08-16', el mismo corte que deja el DATEADD movido):
# ancho REAL del tramo verde que se enciende al cruzar, no un numero a ojo
FRACCION_30D = float((S.pedidos()["dia"] > S.dia("2026-08-16")).sum()) / FILAS_PED


# --- Rotulos ----------------------------------------------------------
def _con_fondo(mobjeto, buff=0.14, opacidad=0.82):
    fondo = BackgroundRectangle(mobjeto, color=CODE_BG, fill_opacity=opacidad,
                                buff=buff)
    return VGroup(fondo, mobjeto)


def titulo_curso(texto, font_size=34, color=None):
    _vigilar(texto, MAX_TITULO, "titulo_curso")
    t = titulo_marca(texto, font_size=font_size,
                     color=C_TITULO if color is None else color)
    if t.width > 7.6:
        t.scale_to_fit_width(7.6)
    t.to_edge(UP, buff=0.52)
    return _con_fondo(t)


def cifra_pie(texto, font_size=26, color=None):
    """El carril de la cifra (zona 'abajo'), Space Mono, SOLO ASCII."""
    _vigilar(texto, MAX_CIFRA, "cifra_pie")
    t = Text(str(texto), font=FUENTE_HUD, font_size=font_size,
             color=C_CALCULO if color is None else color)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def formula_pie(tex, font_size=36, color=None):
    m = MathTex(tex, font_size=font_size,
                color=C_CALCULO if color is None else color)
    if m.width > config.frame_width - 3.0:
        m.scale_to_fit_width(config.frame_width - 3.0)
    m.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(m)


def dato_pie(texto, font_size=24):
    """Un dato que NO se calculo aqui: en GRIS."""
    _vigilar(texto, MAX_CIFRA, "dato_pie")
    t = Text(f"{texto}   · dato", font=FUENTE_HUD, font_size=font_size,
             color=C_DATO)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def hud_modulo(*_a, **_k):
    raise RuntimeError(
        "Curso 37: NO hay etiqueta 'Modulo 0N' en pantalla (pedido del "
        "dueno). Quita la llamada a hud_modulo().")


def motor_pie(texto, font_size=26):
    """Lectura MEDIDA por SQL Server (ambar) en el carril de la cifra."""
    _vigilar(texto, MAX_CIFRA, "motor_pie")
    t = Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=C_MOTOR)
    if t.width > config.frame_width - 2.6:
        t.scale_to_fit_width(config.frame_width - 2.6)
    t.to_edge(DOWN, buff=MARGEN_PIE)
    return _con_fondo(t)


def tag_motor(texto, font_size=19):
    """Cifra flotante MEDIDA por el motor (ambar, Space Mono, ASCII)."""
    _vigilar(texto, MAX_CIFRA, "tag_motor")
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size, color=C_MOTOR)


def tag_junto(mobjeto, texto, direccion=DOWN, buff=0.16, font_size=18,
              color=None):
    _vigilar(texto, MAX_TAG, "tag_junto")
    minimo = FS_MIN_MULTI if len(_palabras(texto)) > 1 else FS_MIN_DISPLAY
    t = Text(str(texto), font_size=max(font_size, minimo),
             color=C_TENUE if color is None else color)
    t.set_opacity(0.9)
    t.next_to(mobjeto, direccion, buff=buff)
    return t


def tag_hud(texto, font_size=19, color=None):
    """Cifra tecnica flotante en Space Mono (SOLO ASCII)."""
    _vigilar(texto, MAX_CIFRA, "tag_hud")
    return Text(str(texto), font=FUENTE_HUD, font_size=font_size,
                color=C_CALCULO if color is None else color)


def panel_cifras(*lineas, buff=0.22, esquina=UR, desplazar=None):
    g = VGroup()
    for ln in lineas:
        texto, color = ln if isinstance(ln, tuple) else (ln, None)
        g.add(tag_hud(texto, font_size=19, color=color))
    g.arrange(DOWN, buff=buff, aligned_edge=RIGHT)
    g.to_corner(esquina, buff=0.55).shift(DOWN * 0.45)
    if desplazar is not None:
        g.shift(desplazar)
    return _con_fondo(g, buff=0.18, opacidad=0.78)


def cierre_leccion(escena, rot, linea_blanca, linea_cian, *apagar,
                   espera=4.4):
    if apagar:
        escena.play(*[FadeOut(m) for m in apagar], run_time=0.8)
    rot.limpiar(run_time=0.4)
    l1 = Text(linea_blanca, font_size=40, color=C_TITULO)
    l2 = Text(linea_cian, font_size=40, color=C_CALCULO)
    l1.move_to(UP * 0.42)
    l2.move_to(DOWN * 0.42)
    escena.play(FadeIn(l1, shift=0.2 * UP), run_time=0.7)
    escena.play(FadeIn(l2, shift=0.2 * UP), run_time=0.7)
    escena.wait(espera)
    return VGroup(l1, l2)


# --- Dibujo compartido de la leccion ---------------------------------
def lecturas(n):
    """'22,363 lecturas' (texto para motor_pie / tag_motor)."""
    return f"{S.miles(n)} lecturas"


def pos_sin_espacios(linea, sub):
    """Indice (i, j), SIN contar espacios, de `sub` dentro de `linea`: para
    tomar el trozo con S.codigo(...).lineas[k][i:j] (glifos)."""
    compacta = linea.replace(" ", "")
    i = compacta.index(sub)
    return i, i + len(sub)


def fila_indice(ancho=11.0, alto=1.0, color=None):
    """El indice ordenado por fecha_pedido: un tramo por anio, ANCHO
    proporcional a sus filas reales (FILAS_ANIO / FILAS_PED). `.anios[a]`
    da el rectangulo del anio `a`."""
    color = C_INDICE if color is None else color
    fila = VGroup()
    for a in ANIOS:
        w = max(ancho * FILAS_ANIO[a] / FILAS_PED, 0.08)
        r = Rectangle(width=w, height=alto, stroke_color=color,
                      stroke_width=1.6, fill_color=color, fill_opacity=0.18)
        fila.add(r)
    fila.arrange(RIGHT, buff=0.05)
    fila.anios = {a: fila[i] for i, a in enumerate(ANIOS)}
    return fila


def fila_lista(columnas=48, lado=0.18, sep=0.05, color=None):
    """La misma idea que MuroPaginas pero en UNA fila: el indice ordenado
    visto como una lista de entradas (no la tabla completa)."""
    color = C_TENUE if color is None else color
    return S.MuroPaginas(columnas=columnas, filas=1, lado=lado, sep=sep,
                         color=color, opacidad=0.16)


class Contador(VGroup):
    """Contador de lecturas en ambar: numero + rotulo debajo. Reserva el
    ancho de `digitos` cifras (una muestra invisible) y crece hacia la
    IZQUIERDA desde su borde derecho, asi que se coloca por su caja
    completa. Se actualiza con `fijar(v)` (become, FUERA de play) o con
    `anim(escena, hasta, run_time)` (ValueTracker + updater)."""

    def __init__(self, valor=0, rotulo="lecturas", font_size=40, digitos=6,
                 color=None):
        super().__init__()
        self._fs = font_size
        self._color = C_MOTOR if color is None else color
        self.muestra = S.contador_texto(10 ** digitos - 1, color=self._color,
                                        font_size=font_size)
        self.muestra.set_opacity(0)
        self.num = S.contador_texto(valor, color=self._color, font_size=font_size)
        self.num.move_to(self.muestra, aligned_edge=RIGHT)
        self.rot = Text(rotulo, font_size=22, color=C_TENUE)
        self.rot.next_to(self.muestra, DOWN, buff=0.14, aligned_edge=RIGHT)
        self.add(self.muestra, self.num, self.rot)

    def fijar(self, v):
        nuevo = S.contador_texto(v, color=self._color, font_size=self._fs)
        nuevo.move_to(self.muestra, aligned_edge=RIGHT)
        self.num.become(nuevo)

    def anim(self, escena, hasta, run_time=2.0, desde=0, rate_func=linear,
             extra=()):
        vt = ValueTracker(desde)
        self.num.add_updater(lambda m: self.fijar(vt.get_value()))
        escena.play(vt.animate.set_value(hasta), *extra, run_time=run_time,
                    rate_func=rate_func)
        self.num.clear_updaters()
        self.fijar(hasta)


class Cuadro:
    """Un cuadro de datos sin ejes de manim (que cruzan por el origen): mapea
    (x, y) de datos a pantalla dentro de la caja (x0, x1, y0, y1). El rango y
    se ELIGE, no se recorta despues (trampas.md)."""

    def __init__(self, caja, rango_x, rango_y):
        self.x0, self.x1, self.y0, self.y1 = caja
        self.rx, self.ry = rango_x, rango_y

    def p(self, x, y):
        fx = (x - self.rx[0]) / (self.rx[1] - self.rx[0])
        fy = (y - self.ry[0]) / (self.ry[1] - self.ry[0])
        return np.array([self.x0 + (self.x1 - self.x0) * fx,
                         self.y0 + (self.y1 - self.y0) * fy, 0.0])

    def serie(self, xs, ys, color, ancho=4, esquinas=True):
        m = VMobject(stroke_color=color, stroke_width=ancho)
        pts = [self.p(x, y) for x, y in zip(xs, ys)]
        (m.set_points_as_corners if esquinas else m.set_points_smoothly)(pts)
        return m

    def suelo(self, y=None, color=None):
        y = self.ry[0] if y is None else y
        return Line(self.p(self.rx[0], y), self.p(self.rx[1], y),
                    stroke_color=C_TENUE if color is None else color, stroke_width=2)

    def raya(self, y, color, dash=0.1, ancho=2):
        return DashedLine(self.p(self.rx[0], y), self.p(self.rx[1], y),
                          dash_length=dash, stroke_color=color, stroke_width=ancho)

    def franjas(self, xs, mascara, color, opacidad=0.18):
        """Rectangulos verticales donde `mascara` es cierta (tramos seguidos)."""
        g = VGroup()
        i, n = 0, len(xs)
        dx = (xs[1] - xs[0]) if n > 1 else 1
        while i < n:
            if mascara[i]:
                j = i
                while j + 1 < n and mascara[j + 1]:
                    j += 1
                a, b = self.p(xs[i] - dx / 2, self.ry[0]), self.p(xs[j] + dx / 2, self.ry[1])
                r = Rectangle(width=b[0] - a[0], height=b[1] - a[1], stroke_width=0,
                              fill_color=color, fill_opacity=opacidad)
                g.add(r.move_to((a + b) / 2))
                i = j + 1
            else:
                i += 1
        return g


# --- Marca de la escena (sombra de Scene) -----------------------------
_SceneBase = Scene


class Scene(_SceneBase):
    def setup(self):
        super().setup()
        self.camera.background_color = CODE_BG
        self.add(esquinas_hud(), marca_agua())
