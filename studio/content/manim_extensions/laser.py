"""Láseres y enlaces ópticos: haz con núcleo brillante, disparo e impacto.

El haz son líneas superpuestas (núcleo blanco fino + capas del color con
ancho creciente y opacidad decreciente — mismo truco que brillo.py). El
disparo es Crear el haz + Flash en el objetivo + desvanecer.

Uso:
    from laser import rayo, disparo, rafaga
    self.play(disparo(canon.get_center(), blanco.get_center(), color=RED))
    self.play(rafaga(a, b, pulsos=3, color=GREEN))
"""

from manim import (AnimationGroup, Create, FadeOut, Flash, Line,
                   ShowPassingFlash, Succession, VGroup, RED, WHITE)


def rayo(origen, destino, color=RED, nucleo=2.2, capas=4, alcance=4.0):
    """VGroup de líneas superpuestas: halo del color + núcleo blanco."""
    grupo = VGroup()
    for i in range(capas, 0, -1):
        grupo.add(Line(origen, destino, color=color,
                       stroke_width=nucleo * (1 + alcance * i / capas),
                       stroke_opacity=0.45 * (1 - (i - 1) / capas) ** 2))
    grupo.add(Line(origen, destino, color=WHITE, stroke_width=nucleo,
                   stroke_opacity=0.95))
    return grupo


def disparo(origen, destino, color=RED, duracion=1.2, radio_impacto=0.45):
    """Disparo completo: el haz crece, impacta (Flash) y se desvanece."""
    haz = rayo(origen, destino, color=color)
    return Succession(
        Create(haz, run_time=duracion * 0.35),
        AnimationGroup(
            Flash(destino, color=color, flash_radius=radio_impacto,
                  line_length=0.25, run_time=duracion * 0.4),
            FadeOut(haz, run_time=duracion * 0.65),
        ),
    )


def rafaga(origen, destino, color=RED, pulsos=3, duracion=1.8):
    """Pulsos cortos que recorren el enlace (comunicación óptica continua):
    el haz tenue queda fijo y los destellos viajan por él."""
    guia = rayo(origen, destino, color=color)
    for linea in guia:
        linea.set_stroke(opacity=linea.get_stroke_opacity() * 0.3)
    tren = [
        ShowPassingFlash(
            Line(origen, destino, color=WHITE, stroke_width=4),
            time_width=0.25, run_time=duracion / pulsos)
        for _ in range(pulsos)
    ]
    return Succession(Create(guia, run_time=0.3), *tren,
                      FadeOut(guia, run_time=0.3))
