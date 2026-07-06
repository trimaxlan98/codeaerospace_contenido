"""Constelaciones LEO animadas en 2D (vista tipo "shell" de planos orbitales).

Cada plano orbital es una elipse achatada y rotada (la proyección clásica de
las láminas de marketing de Starlink/OneWeb); los satélites recorren su plano
con fases repartidas y sentidos alternos. Sin 3D real: todo VMobjects baratos.

Uso:
    from constelacion import ConstelacionLEO, AnimarConstelacion, enlaces_isl
    cons = ConstelacionLEO(planos=4, sats_por_plano=8)
    enlaces = enlaces_isl(cons)
    self.add(cons, enlaces)
    self.play(AnimarConstelacion(cons, vueltas=1), run_time=8)
    enlaces.clear_updaters()  # al terminar, si la escena sigue
"""

import numpy as np

from manim import (Animation, Circle, Dot, Ellipse, Line, VGroup,
                   BLUE, BLUE_E, GREY_C, TEAL_B, YELLOW, linear)


class ConstelacionLEO(VGroup):
    def __init__(self, planos=4, sats_por_plano=8, radio=2.6,
                 achatamiento=0.35, radio_tierra=0.85, mostrar_tierra=True,
                 color_orbita=GREY_C, color_sat=YELLOW, color_tierra=BLUE,
                 **kwargs):
        super().__init__(**kwargs)
        self.planos_orbitales: list[dict] = []

        if mostrar_tierra:
            self.tierra = Circle(radius=radio_tierra, color=color_tierra,
                                 fill_color=BLUE_E, fill_opacity=0.55,
                                 stroke_width=2)
            self.add(self.tierra)

        for i in range(planos):
            angulo = np.pi * i / planos
            camino = Ellipse(width=2 * radio, height=2 * radio * achatamiento,
                             color=color_orbita, stroke_width=1.6,
                             stroke_opacity=0.7).rotate(angulo)
            sats = VGroup()
            fases = []
            for j in range(sats_por_plano):
                fase = (j / sats_por_plano + 0.13 * i) % 1.0
                sat = Dot(camino.point_from_proportion(fase), radius=0.055,
                          color=color_sat)
                sats.add(sat)
                fases.append(fase)
            # Sentidos alternos: planos pares e impares giran al reves,
            # como los cruces ascendente/descendente vistos de lejos.
            self.planos_orbitales.append(
                {"camino": camino, "sats": sats, "fases": fases,
                 "sentido": 1 if i % 2 == 0 else -1})
            self.add(camino, sats)


class AnimarConstelacion(Animation):
    """Todos los satelites recorren su plano `vueltas` veces."""

    def __init__(self, constelacion: ConstelacionLEO, vueltas=1.0, **kwargs):
        self.vueltas = vueltas
        kwargs.setdefault("rate_func", linear)
        super().__init__(constelacion, **kwargs)

    def interpolate_mobject(self, alpha):
        t = self.rate_func(alpha) * self.vueltas
        for plano in self.mobject.planos_orbitales:
            for sat, fase in zip(plano["sats"], plano["fases"]):
                f = (fase + t * plano["sentido"]) % 1.0
                sat.move_to(plano["camino"].point_from_proportion(f))


def enlaces_isl(constelacion: ConstelacionLEO, color=TEAL_B, grosor=1.2,
                opacidad=0.55):
    """Enlaces inter-satelitales intra-plano (cada sat con el siguiente).

    Las lineas llevan updater y siguen a los satelites durante la animacion.
    Llamar `.clear_updaters()` sobre el grupo devuelto cuando ya no se anime.
    """
    enlaces = VGroup()
    for plano in constelacion.planos_orbitales:
        sats = list(plano["sats"])
        for a, b in zip(sats, sats[1:] + sats[:1]):
            linea = Line(a.get_center(), b.get_center(), color=color,
                         stroke_width=grosor, stroke_opacity=opacidad)
            linea.add_updater(
                lambda l, a=a, b=b: l.put_start_and_end_on(a.get_center(),
                                                           b.get_center()))
            enlaces.add(linea)
    return enlaces
