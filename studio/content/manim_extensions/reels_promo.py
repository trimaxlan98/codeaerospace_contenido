"""Piezas para reels promocionales en LOOP PERFECTO (9:16, 1080×1920).

Regla de oro: cada elemento es una función PERIÓDICA del reloj (`Reloj.t`, en segundos, periodo `T`).
Nada entra ni sale «una sola vez»: lo que desaparece al final es lo que aparece al principio, así el
último cuadro empalma con el primero y no se sabe dónde acaba el video. Los textos rotan en ventanas
cíclicas con fundido cruzado (`ventana`), y el audio se compone con la misma fase (sonido_reels.py).

Todo texto va por `marca_vertical._texto` (el lienzo de Pango ancho) y `bloque` (una línea = un Text).
"""

import numpy as np
from manim import (DOWN, LEFT, RIGHT, UP, Dot, Line, RoundedRectangle, Rectangle, VGroup, VMobject, config)

from marca_aerospace import AMBAR, CIAN, FONDO, PLATA, PLATA_MEDIA, LogoCoDe
from marca_vertical import _texto, bloque, marco
from rotulos_aerospace import TENUE


class Reloj:
    """Reloj de la escena: `t` avanza con cada cuadro. Se añade ANTES que todo lo demás."""

    def __init__(self, escena, periodo, desfase=0.0):
        """desfase: el video empieza en la fase `desfase` del ciclo (para que el primer cuadro, que es la
        portada, muestre el momento más legible)."""
        self.t = desfase
        self.T = periodo
        ctrl = VMobject()
        ctrl.add_updater(lambda m, dt: setattr(self, "t", self.t + dt))
        escena.add(ctrl)

    @property
    def fase(self):
        return (self.t % self.T) / self.T


def suave(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


def ventana(t, a, b, f, T):
    """1 dentro de [a, b) del ciclo (módulo T) y 0 fuera, con rampas suaves de f segundos centradas en
    a y en b. Dos ventanas contiguas hacen un fundido cruzado exacto (suman 1) y la función es
    periódica: sirve para que lo último del video sea lo primero."""
    x = ((t - a + f / 2) % T) - f / 2
    largo = (b - a) % T or T
    return min(suave((x + f / 2) / f), suave((largo - x + f / 2) / f))


def ventana_texto(t, a, b, f, T):
    """Como `ventana` pero SIN solape entre textos contiguos: sale en [b−f, b] y entra en [a, a+f], así
    nunca se ven dos frases encimadas."""
    x = (t - a) % T
    largo = (b - a) % T or T
    return min(suave(x / f), suave((largo - x) / f)) if x < largo else 0.0


def cabecera(escena, kicker, titulo, n=18, tam=92):
    """Emblema + kicker cian arriba (y = 8.1) y el título en 2–3 líneas debajo. Constante: no rota."""
    W, H = marco(escena)
    emblema = LogoCoDe(altura=1.15, aerospace=False, contorno=True)
    emblema.move_to([-W / 2 + 1.0, 8.15, 0])
    k = _texto(kicker.upper(), 30, "MEDIUM", CIAN, tracking=0.2, ancho_max=W * 0.72)
    k.next_to(emblema, RIGHT, buff=0.35)
    t = bloque(titulo, n, tam, "SEMIBOLD", PLATA[0], W * 0.88)
    t.set_color([PLATA[0], PLATA[1]]).set_sheen_direction(DOWN)
    t.move_to([0, 6.35 - (t.height - 2.4) / 2 if t.height > 2.4 else 6.35, 0])
    g = VGroup(emblema, k, t).set_z_index(20)
    escena.add(g)
    return g


def chip(texto, color=CIAN, tam=26):
    """Etiqueta redondeada (para «ilustrativo», «demo»…)."""
    t = _texto(texto, tam, "MEDIUM", color)
    caja = RoundedRectangle(corner_radius=0.22, width=t.width + 0.7, height=t.height + 0.42, stroke_width=2.2,
                            stroke_color=color, fill_color=FONDO, fill_opacity=0.82)
    t.move_to(caja)
    return VGroup(caja, t).set_z_index(30)


def leyenda(escena, reloj, grande, pequena, t0, t1, y, f=0.5, tam_g=58, tam_p=33, color_p=CIAN):
    """Pareja (frase + línea técnica) que solo se ve en la ventana [t0, t1) del ciclo."""
    W, _ = marco(escena)
    g = bloque(grande, 40, tam_g, "SEMIBOLD", PLATA[0], W * 0.88)
    p = bloque(pequena, 70, tam_p, "MEDIUM", color_p, W * 0.9)
    grupo = VGroup(g, p).arrange(DOWN, buff=0.34).move_to([0, y, 0]).set_z_index(25)
    base = grupo.get_center().copy()

    def actualizar(m):
        o = ventana_texto(reloj.t, t0, t1, f, reloj.T)
        m.set_opacity(o)
        m.move_to(base + UP * 0.35 * (1 - o))
    grupo.add_updater(actualizar)
    actualizar(grupo)
    escena.add(grupo)
    return grupo


def polilinea(puntos, **est):
    vm = VMobject()
    vm.set_points_as_corners(np.asarray(puntos, dtype=float))
    vm.set_stroke(**est).set_fill(opacity=0)
    return vm


def linea_ciclica(escena, reloj, texto, t0, t1, y, f=0.5, tam=46, color=PLATA[0]):
    """Una sola línea de texto que vive en la ventana [t0, t1) del ciclo."""
    W, _ = marco(escena)
    t = bloque(texto, 60, tam, "MEDIUM", color, W * 0.9).move_to([0, y, 0]).set_z_index(25)
    base = t.get_center().copy()

    def actualizar(m):
        o = ventana_texto(reloj.t, t0, t1, f, reloj.T)
        m.set_opacity(o)
        m.move_to(base + UP * 0.3 * (1 - o))
    t.add_updater(actualizar)
    actualizar(t)
    escena.add(t)
    return t
