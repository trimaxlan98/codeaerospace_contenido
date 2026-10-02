"""Rotulación de video con la marca Co.De Aerospace: títulos, tercios inferiores, capítulos y cierres.

La familia visual sale del logo: Montserrat (la más cercana a sus letras, OFL, en fonts/), tinta
plata sobre el fondo del logo (#080F15), cian de codeaerospace.com como único acento y una regla fina
con un punto, que es la órbita con su luna reducida a una línea. Ningún rótulo usa más de dos pesos
ni más de un acento.

Piezas (todas devuelven un VGroup listo para `self.add` o para su animación de entrada):
    tarjeta_titulo(titulo, subtitulo, antetitulo)   portada de una pieza o sección
    tercio_inferior(nombre, cargo)                  quién habla (emblema + nombre + cargo)
    capitulo(numero, titulo)                        separador «01 · Título»
    cierre_marca(sitio, lema)                       logo + sitio, para el final
y sus animaciones: entrar_tarjeta, entrar_tercio / salir_tercio, entrar_capitulo,
cortinilla_orbital(escena, saliente, entrante) y animar_cierre.

Los textos se escriben a 4× y se reducen: Pango redondea la posición de cada glifo al pixel y, a
tamaños chicos, deja huecos desiguales entre letras (el mismo arreglo que `code_lib` en animaciones/).
Todo texto se encoge si no cabe en `ancho_max`; nunca se sale del cuadro.

Uso:
    import sys
    sys.path.insert(0, "/workspace/studio/content/manim_extensions")
    from rotulos_aerospace import tarjeta_titulo, entrar_tarjeta, FONDO
    class Portada(Scene):
        def construct(self):
            self.camera.background_color = FONDO
            t = tarjeta_titulo("Redes no terrestres", "Satélites en la 6G", antetitulo="Seminario")
            entrar_tarjeta(self, t)
"""

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Create, Dot, FadeIn, FadeOut, LaggedStart, Line, Rectangle,
                   Succession, Text, VGroup, VMobject, Wait, config, rate_functions)

from code_brand import registrar_fuentes
from estelas import dibujar_con_cometa, recorrer_con_estela
from marca_aerospace import (CIAN, FONDO, FUENTE, PLATA, PLATA_MEDIA, LogoCoDe, animar_entrada,
                             animar_salida)

TENUE = "#8E99A6"        # texto secundario sobre FONDO (contraste 6.6:1)
LINEA = "#2A3742"        # reglas y marcos discretos
_SUPER = 4


def _texto(s, tam, peso="NORMAL", color=PLATA_MEDIA, tracking=0.0, ancho_max=None):
    """Text de Montserrat a 4× y reducido. `tracking` en em (0.18 = espaciado ancho).

    El tracking se aplica corriendo cada glifo, no con MarkupText: el `letter_spacing` de Pango
    hace que MarkupText parta la línea a 4×. Text ya trae el interletrado del kerning; aquí solo se
    suma el espacio extra, contando también los espacios (que Text no convierte en glifos).
    """
    registrar_fuentes()
    t = Text(s, font=FUENTE, weight=peso, font_size=tam * _SUPER, color=color)
    if tracking:
        paso = tracking * t.height / 0.72 if t.height else 0   # ≈ em del texto a partir de la altura de mayúsculas
        glifos = iter(t.submobjects)
        for i, ch in enumerate(s):
            if ch.isspace():
                continue
            g = next(glifos, None)
            if g is None:
                break
            g.shift(RIGHT * paso * i)
    t.scale(1 / _SUPER)
    if ancho_max and t.width > ancho_max:
        t.scale_to_fit_width(ancho_max)
    return t


def regla_orbital(ancho=3.0, color=CIAN, radio=0.055):
    """Línea fina con un punto en el extremo derecho: la órbita y la luna del logo, en una línea."""
    linea = Line(LEFT * ancho / 2, RIGHT * ancho / 2, stroke_width=2.2, color=color)
    punto = Dot(linea.get_end(), radius=radio, color=color)
    return VGroup(linea, punto)


# ── Tarjeta de título ─────────────────────────────────────────────────────────────────

def tarjeta_titulo(titulo, subtitulo=None, antetitulo=None, ancho_max=None):
    """Antetítulo en cian con tracking, título plata, regla orbital y subtítulo tenue."""
    ancho_max = ancho_max or config.frame_width * 0.82
    partes = VGroup()
    ante = _texto(antetitulo.upper(), 20, "MEDIUM", CIAN, tracking=0.22, ancho_max=ancho_max) if antetitulo else None
    tit = _texto(titulo, 60, "SEMIBOLD", PLATA[0], ancho_max=ancho_max)
    tit.set_color([PLATA[0], PLATA[1]]).set_sheen_direction(DOWN)
    regla = regla_orbital(ancho=min(3.2, ancho_max))
    sub = _texto(subtitulo, 28, "NORMAL", TENUE, ancho_max=ancho_max) if subtitulo else None
    for p in (ante, tit, regla, sub):
        if p is not None:
            partes.add(p)
    partes.arrange(DOWN, buff=0.32)
    if ante is not None:
        ante.shift(0.06 * UP)
    t = VGroup(*partes)
    t.antetitulo, t.titulo, t.regla, t.subtitulo = ante, tit, regla, sub
    return t


def entrar_tarjeta(escena, t, ritmo=1.0):
    """La regla se dibuja con cometa, el título sube y el resto aparece en cascada."""
    linea, punto = t.regla
    anims = [dibujar_con_cometa(linea, run_time=0.9 * ritmo), FadeIn(punto, scale=0.3, run_time=0.4 * ritmo)]
    entradas = [FadeIn(t.titulo, shift=0.18 * UP, run_time=0.8 * ritmo)]
    if t.antetitulo is not None:
        entradas.insert(0, FadeIn(t.antetitulo, run_time=0.6 * ritmo))
    if t.subtitulo is not None:
        entradas.append(FadeIn(t.subtitulo, shift=0.1 * UP, run_time=0.7 * ritmo))
    escena.play(Succession(*anims), LaggedStart(*entradas, lag_ratio=0.25))


# ── Tercio inferior ───────────────────────────────────────────────────────────────────

def tercio_inferior(nombre, cargo=None, emblema=True, ancho_max=6.4):
    """Emblema chico + nombre + cargo, sobre una placa translúcida con borde cian a la izquierda.
    Se coloca en la esquina inferior izquierda con margen de seguridad."""
    nom = _texto(nombre, 30, "SEMIBOLD", PLATA[0], ancho_max=ancho_max)
    textos = VGroup(nom)
    if cargo:
        textos.add(_texto(cargo, 20, "NORMAL", TENUE, ancho_max=ancho_max))
    textos.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
    contenido = VGroup(textos)
    if emblema:
        e = LogoCoDe(altura=textos.height * 1.25, aerospace=False, contorno=True)
        contenido = VGroup(e, textos).arrange(RIGHT, buff=0.28)
    placa = Rectangle(width=contenido.width + 0.7, height=contenido.height + 0.42, stroke_width=0,
                      fill_color=FONDO, fill_opacity=0.82)
    borde = Line(placa.get_corner(DOWN + LEFT), placa.get_corner(UP + LEFT), stroke_width=4, color=CIAN)
    contenido.move_to(placa).shift(0.06 * RIGHT)
    t = VGroup(placa, borde, contenido)
    t.to_corner(DOWN + LEFT, buff=0.55)
    t.placa, t.borde, t.contenido = placa, borde, contenido
    return t


def entrar_tercio(escena, t, ritmo=1.0):
    escena.play(FadeIn(t.placa, shift=0.3 * RIGHT), FadeIn(t.borde, shift=0.3 * RIGHT),
                LaggedStart(*[FadeIn(m, shift=0.15 * RIGHT) for m in t.contenido], lag_ratio=0.2),
                run_time=0.8 * ritmo, rate_func=rate_functions.ease_out_cubic)


def salir_tercio(escena, t, ritmo=1.0):
    escena.play(FadeOut(t, shift=0.25 * LEFT), run_time=0.5 * ritmo)


# ── Capítulo ──────────────────────────────────────────────────────────────────────────

def capitulo(numero, titulo, ancho_max=None):
    """«01» grande en contorno plata + título; separador entre secciones de un video."""
    ancho_max = ancho_max or config.frame_width * 0.7
    num = _texto(f"{int(numero):02d}", 120, "SEMIBOLD", PLATA[0])
    num.set_fill(opacity=0).set_stroke(color=PLATA[1], width=1.6)
    tit = _texto(titulo, 40, "MEDIUM", PLATA[0], ancho_max=ancho_max)
    regla = regla_orbital(ancho=1.4)
    derecha = VGroup(regla, tit).arrange(DOWN, aligned_edge=LEFT, buff=0.24)
    t = VGroup(num, derecha).arrange(RIGHT, buff=0.55)
    if t.width > config.frame_width * 0.9:
        t.scale_to_fit_width(config.frame_width * 0.9)
    t.numero, t.titulo, t.regla = num, tit, regla
    return t


def entrar_capitulo(escena, t, ritmo=1.0):
    escena.play(Create(t.numero, run_time=1.0 * ritmo, lag_ratio=0.1),
                Succession(Wait(0.25 * ritmo), dibujar_con_cometa(t.regla[0], run_time=0.6 * ritmo)),
                FadeIn(t.regla[1], run_time=0.3 * ritmo),
                Succession(Wait(0.45 * ritmo), FadeIn(t.titulo, shift=0.12 * UP, run_time=0.6 * ritmo)))


# ── Cortinilla orbital ────────────────────────────────────────────────────────────────

def cortinilla_orbital(escena, saliente, entrante, color=CIAN, ritmo=1.0):
    """Transición: un satélite cruza la pantalla por una órbita amplia con su estela; lo que hay
    detrás del paso se desvanece y aparece lo nuevo. Saca `saliente` y deja `entrante` en escena."""
    w, h = config.frame_width, config.frame_height
    # Arco que entra abajo a la izquierda y sale arriba a la derecha, más empinado al final.
    s = np.linspace(0, 1, 24)
    tray = VMobject().set_points_smoothly([np.array([(-0.62 + 1.24 * k) * w, (-0.46 + 0.95 * k ** 1.6) * h, 0])
                                           for k in s])
    sat = Dot(radius=0.07, color=color)
    sat.move_to(tray.get_start())
    escena.play(recorrer_con_estela(sat, tray, largo=0.35, color=color, ancho=5, run_time=1.2 * ritmo,
                                    rate_func=rate_functions.ease_in_out_sine),
                FadeOut(saliente, run_time=0.6 * ritmo),
                Succession(Wait(0.5 * ritmo), FadeIn(entrante, run_time=0.7 * ritmo)))
    escena.remove(sat)


# ── Cierre de marca ───────────────────────────────────────────────────────────────────

def cierre_marca(sitio="codeaerospace.com", lema=None, altura_logo=None):
    """El logo con el sitio (y un lema opcional) debajo, centrado."""
    altura_logo = altura_logo or config.frame_height * 0.56
    logo = LogoCoDe(altura=altura_logo)
    textos = VGroup()
    if lema:
        textos.add(_texto(lema, 26, "NORMAL", TENUE, ancho_max=config.frame_width * 0.8))
    if sitio:
        textos.add(_texto(sitio, 24, "MEDIUM", CIAN, tracking=0.08))
    textos.arrange(DOWN, buff=0.16)
    t = VGroup(logo, textos).arrange(DOWN, buff=0.38) if len(textos) else VGroup(logo)
    if t.height > config.frame_height * 0.9:
        t.scale_to_fit_height(config.frame_height * 0.9)
    t.logo, t.textos = logo, textos
    return t


def animar_cierre(escena, t, estilo="trazo", espera=1.6, salir=True):
    """Entrada del logo (estilo de `marca_aerospace`), los textos, una pausa y la salida."""
    animar_entrada(escena, t.logo, estilo=estilo, ritmo=0.8)
    if len(t.textos):
        escena.play(LaggedStart(*[FadeIn(m, shift=0.1 * UP) for m in t.textos], lag_ratio=0.3), run_time=0.8)
    escena.wait(espera)
    if salir:
        animar_salida(escena, t.logo)
        if len(t.textos):
            escena.play(FadeOut(t.textos), run_time=0.4)
