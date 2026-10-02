"""Marca Co.De Aerospace en vertical 9:16 (reels de Instagram, 1080×1920).

No es girar el video horizontal: el logo es casi cuadrado y ocupa el ancho, así que el alto sobrante
se llena con el mismo lenguaje de la marca: un campo de estrellas, tres órbitas gigantes que cruzan
de arriba abajo (se dibujan con cometa al abrir) y un satélite que no deja de orbitar. Los rótulos
se rehacen para el formato (apilados, letra grande, dentro de la zona segura de Instagram).

Con `-r 1080,1920` Manim conserva el ANCHO del cuadro (14.22 unidades) y estira el alto de la CÁMARA
(25.28); `config.frame_height` se queda en 8. Por eso todo aquí mide con `marco(escena)` y nunca con
`config` ni con `to_corner/to_edge` (que usan `config`).

Zona segura de Instagram (de 1920 px): arriba ~14 % y abajo ~22 % los tapa la interfaz; a la derecha
~12 % los botones. El texto importante va entre y = +8.4 y y = −7.4 (unidades de escena).
"""

import numpy as np
from manim import (DOWN, ORIGIN, LEFT, RIGHT, UP, Dot, Ellipse, FadeIn, FadeOut, LaggedStart, Line, Rectangle,
                   Succession, VGroup, VMobject, Wait, rate_functions, smooth)

from estelas import dibujar_con_cometa, recorrer_con_estela
from marca_aerospace import (CIAN, FONDO, PAPEL, PLATA, PLATA_MEDIA, TINTA, LogoCoDe)
import rotulos_aerospace
from manim import config
from rotulos_aerospace import TENUE, regla_orbital

AZUL_CLARO = "#0A84C6"          # acento sobre papel (el de LogoCoDeIntroClaro)
SEGURA_ARRIBA = 8.4
SEGURA_ABAJO = -7.4


def _texto(*args, **kwargs):
    """`rotulos_aerospace._texto` con el lienzo de Pango ancho: Manim parte el `Text` en líneas cuando
    mide más que `config.pixel_width` (1080 aquí) y a 4× casi todo rótulo se pasa."""
    ancho = config.pixel_width
    config.pixel_width = 20000
    try:
        return rotulos_aerospace._texto(*args, **kwargs)
    finally:
        config.pixel_width = ancho


def marco(escena):
    """(ancho, alto) del cuadro de la cámara en unidades de escena."""
    return escena.camera.frame_width, escena.camera.frame_height


def envolver(texto, n):
    """Parte `texto` en líneas de ≲ n caracteres, repartidas parejo (sin viudas)."""
    palabras = texto.split()
    lineas = max(1, int(np.ceil(len(texto) / n)))
    objetivo = len(texto) / lineas
    salida, actual = [], ""
    for p in palabras:
        if actual and len(actual) + 1 + len(p) > objetivo * 1.15 and len(salida) < lineas - 1:
            salida.append(actual)
            actual = p
        else:
            actual = f"{actual} {p}".strip()
    salida.append(actual)
    return "\n".join(salida)


def bloque(texto, n, tam, peso, color, ancho_max, alinear=None):
    """Texto en varias líneas, cada una un `Text` propio (el multilínea de Pango a 4× se desordena)."""
    partes = texto.split("\n") if "\n" in texto else envolver(texto, n).split("\n")
    lineas = VGroup(*[_texto(l, tam, peso, color, ancho_max=ancho_max) for l in partes])
    lineas.arrange(DOWN, buff=tam * 0.004, aligned_edge=alinear if alinear is not None else ORIGIN)
    if lineas.width > ancho_max:
        lineas.scale_to_fit_width(ancho_max)
    return lineas


# ── Fondo de reel ─────────────────────────────────────────────────────────────────────

def fondo_reel(escena, claro=False, entrada=True, retraso=0.0, periodo=None):
    """Campo de estrellas + 3 órbitas gigantes + satélite orbitando, todo detrás (z = −10).

    entrada   las órbitas se dibujan con cometa al empezar (0, 0.5 y 1.0 s tras `retraso`; 2 s cada
              una). Si es False aparecen ya dibujadas.
    periodo   si se da (s), el fondo es PERIÓDICO para loops perfectos: sin entrada, las estrellas titilan
              con ciclos enteros por periodo y el satélite da una vuelta exacta en `periodo`.
    Devuelve el grupo; los movimientos son updaters, corren en cualquier play/wait.
    """
    W, H = marco(escena)
    if periodo:
        entrada = False
    rng = np.random.default_rng(11)
    acento = AZUL_CLARO if claro else CIAN
    reloj = [0.0]
    ctrl = VMobject()
    ctrl.add_updater(lambda m, dt: reloj.__setitem__(0, reloj[0] + dt))
    escena.add(ctrl)

    grupo = VGroup().set_z_index(-10)
    # Estrellas (solo sobre fondo oscuro; sobre papel serían manchas).
    if not claro:
        puntos = []
        for _ in range(170):
            r = rng.choice([0.016, 0.024, 0.034, 0.05], p=[.4, .3, .2, .1])
            d = Dot([rng.uniform(-W / 2, W / 2), rng.uniform(-H / 2, H / 2), 0], radius=r, color=PLATA_MEDIA)
            vel = 2 * np.pi * rng.integers(1, 4) / periodo if periodo else rng.uniform(.4, 1.3)
            puntos.append((d, rng.uniform(.15, .7), rng.uniform(0, 6.28), vel))

        def titilar(_m):
            t = reloj[0]
            rampa = min(1.0, max(0.0, (t - retraso) / 1.2)) if entrada else 1.0
            for d, base, fase, vel in puntos:
                d.set_fill(opacity=base * (0.6 + 0.4 * np.sin(vel * t + fase)) * rampa)
        estrellas = VGroup(*[p[0] for p in puntos])
        estrellas.add_updater(titilar)
        escena.add(estrellas.set_z_index(-10))
        grupo.add(estrellas)

    # Órbitas gigantes.
    specs = [(W * 0.97, H * 0.93, 7), (W * 0.74, H * 0.80, -13), (W * 1.08, H * 0.56, 24)]
    colores = [(acento, 0.62), (PLATA_MEDIA if not claro else TINTA, 0.26), (acento, 0.36)]
    elipses = []
    for (w, h, ang), (col, op) in zip(specs, colores):
        completa = Ellipse(width=w, height=h).rotate(ang * np.pi / 180)
        completa.set_stroke(color=col, width=2.6, opacity=op).set_fill(opacity=0)
        trazo = completa.copy().set_z_index(-10)
        punta = VGroup(Dot(radius=0.30, color=acento).set_opacity(0.16), Dot(radius=0.11, color=acento))
        punta.set_z_index(-9)
        elipses.append((completa, trazo, punta))
        escena.add(trazo, punta)

    def dibujar(k):
        completa, trazo, punta = elipses[k]
        t0, dur = retraso + 0.5 * k, 2.0

        def actualizar(_m):
            if not entrada:
                trazo.become(completa)
                punta.set_opacity(0)
                return
            p = smooth(min(1.0, max(0.0, (reloj[0] - t0) / dur)))
            if p <= 0:
                trazo.set_stroke(opacity=0)
                punta.set_opacity(0)
            elif p >= 1:
                trazo.become(completa)
                punta.set_opacity(0)
            else:
                trazo.pointwise_become_partial(completa, 0, p)
                trazo.set_stroke(opacity=colores[k][1])
                punta.move_to(trazo.get_end())
                f = min(1.0, (1 - p) * 8)
                punta[0].set_opacity(0.16 * f)
                punta[1].set_opacity(f)
        trazo.add_updater(actualizar)

    for k in range(3):
        dibujar(k)

    # Satélite que no deja de orbitar por la primera órbita.
    completa0 = elipses[0][0]
    sat = VGroup(Dot(radius=0.34, color=acento).set_opacity(0.14), Dot(radius=0.12, color=acento)).set_z_index(-9)
    t_ini = retraso + 1.0 + 2.0 if entrada else 0.0
    sat.move_to(completa0.point_from_proportion(0.001))

    def orbitar(m):
        f = ((reloj[0] - t_ini) / (periodo or 14.0)) % 1.0
        m.move_to(completa0.point_from_proportion(min(max(f, 0.001), 0.999)))
        a = 1.0 if periodo else min(1.0, max(0.0, reloj[0] - t_ini + 0.5))
        m.set_opacity(a)
        m[0].set_opacity(0.14 * a)
    sat.add_updater(orbitar)
    escena.add(sat)
    grupo.add(*[e[1] for e in elipses], sat)
    return grupo


# ── Rótulos verticales ────────────────────────────────────────────────────────────────

def tarjeta_vertical(escena, titulo, subtitulo=None, antetitulo=None):
    """Emblema arriba, antetítulo cian, título grande en 2–3 líneas, regla orbital y subtítulo."""
    W, H = marco(escena)
    ancho = W * 0.84
    emblema = LogoCoDe(altura=4.4, aerospace=False, contorno=True)
    emblema.move_to(UP * 6.3)
    ante = _texto(antetitulo.upper(), 36, "MEDIUM", CIAN, tracking=0.22, ancho_max=ancho) if antetitulo else None
    tit = bloque(titulo, 12, 132, "SEMIBOLD", PLATA[0], ancho)
    tit.set_color([PLATA[0], PLATA[1]]).set_sheen_direction(DOWN)
    regla = regla_orbital(ancho=ancho * 0.7, radio=0.08)
    sub = bloque(subtitulo, 24, 56, "NORMAL", TENUE, ancho) if subtitulo else None
    partes = VGroup(*[p for p in (ante, tit, regla, sub) if p is not None]).arrange(DOWN, buff=0.6)
    partes.move_to(DOWN * 0.2)
    t = VGroup(emblema, *partes)
    t.emblema, t.antetitulo, t.titulo, t.regla, t.subtitulo = emblema, ante, tit, regla, sub
    return t


def entrar_tarjeta_vertical(escena, t, ritmo=1.0):
    """Mismos tiempos que `entrar_tarjeta` (1.3 s) + el emblema que se asienta arriba."""
    linea, punto = t.regla
    anims = [dibujar_con_cometa(linea, run_time=0.9 * ritmo), FadeIn(punto, scale=0.3, run_time=0.4 * ritmo)]
    entradas = [FadeIn(t.titulo, shift=0.35 * UP, run_time=0.8 * ritmo)]
    if t.antetitulo is not None:
        entradas.insert(0, FadeIn(t.antetitulo, run_time=0.6 * ritmo))
    if t.subtitulo is not None:
        entradas.append(FadeIn(t.subtitulo, shift=0.2 * UP, run_time=0.7 * ritmo))
    escena.play(Succession(*anims), LaggedStart(*entradas, lag_ratio=0.25),
                FadeIn(t.emblema, shift=0.5 * DOWN, scale=0.92, run_time=1.2 * ritmo))


def tercio_vertical(escena, nombre, cargo=None):
    """Placa ancha con emblema, nombre y cargo, sobre la zona segura inferior (y ≈ −5.2)."""
    W, _ = marco(escena)
    ancho = W * 0.9
    nom = _texto(nombre, 58, "SEMIBOLD", PLATA[0], ancho_max=ancho * 0.62)
    textos = VGroup(nom)
    if cargo:
        textos.add(_texto(cargo, 38, "NORMAL", TENUE, ancho_max=ancho * 0.62))
    textos.arrange(DOWN, aligned_edge=LEFT, buff=0.2)
    e = LogoCoDe(altura=textos.height * 1.5, aerospace=False, contorno=True)
    contenido = VGroup(e, textos).arrange(RIGHT, buff=0.5)
    placa = Rectangle(width=ancho, height=contenido.height + 1.0, stroke_width=0, fill_color=FONDO,
                      fill_opacity=0.86)
    borde = Line(placa.get_corner(DOWN + LEFT), placa.get_corner(UP + LEFT), stroke_width=7, color=CIAN)
    contenido.move_to(placa).align_to(placa, LEFT).shift(0.8 * RIGHT)
    t = VGroup(placa, borde, contenido)
    t.move_to(DOWN * 5.7)
    t.placa, t.borde, t.contenido = placa, borde, contenido
    return t


def capitulo_vertical(escena, numero, titulo):
    """«01» enorme en contorno plata, regla orbital y el título debajo (centrado)."""
    W, _ = marco(escena)
    ancho = W * 0.84
    num = _texto(f"{int(numero):02d}", 520, "SEMIBOLD", PLATA[0])
    num.set_fill(opacity=0).set_stroke(color=PLATA[1], width=3.2)
    tit = bloque(titulo, 12, 116, "MEDIUM", PLATA[0], ancho)
    regla = regla_orbital(ancho=ancho * 0.5, radio=0.08)
    t = VGroup(num, regla, tit).arrange(DOWN, buff=0.8).move_to(UP * 1.0)
    t.numero, t.titulo, t.regla = num, tit, regla
    return t


def cortinilla_vertical(escena, saliente, entrante, color=CIAN, ritmo=1.0):
    """Un satélite cruza TODO el alto (de abajo a la izquierda a arriba a la derecha)."""
    w, h = marco(escena)
    s = np.linspace(0, 1, 24)
    tray = VMobject().set_points_smoothly([np.array([(-0.55 + 1.1 * k ** 0.9) * w, (-0.56 + 1.12 * k) * h, 0])
                                           for k in s])
    sat = Dot(radius=0.14, color=color)
    sat.move_to(tray.get_start())
    escena.play(recorrer_con_estela(sat, tray, largo=0.35, color=color, ancho=8, run_time=1.2 * ritmo,
                                    rate_func=rate_functions.ease_in_out_sine),
                FadeOut(saliente, run_time=0.6 * ritmo),
                Succession(Wait(0.5 * ritmo), FadeIn(entrante, run_time=0.7 * ritmo)))
    escena.remove(sat)


def cierre_vertical(escena, sitio="codeaerospace.com", ancho_logo=0.86, y_logo=1.6):
    """Logo grande (centro en y_logo) y el sitio debajo, en la zona segura."""
    W, _ = marco(escena)
    logo = LogoCoDe(altura=W * ancho_logo / 1.05)
    logo.mover_a(UP * y_logo)
    texto = _texto(sitio, 44, "MEDIUM", CIAN, tracking=0.08, ancho_max=W * 0.8)
    texto.move_to(DOWN * 6.4)
    textos = VGroup(texto)
    t = VGroup(logo, textos)
    t.logo, t.textos = logo, textos
    return t
