"""Pulsos de señal viajando por cualquier camino, para escenas de telecom.

Manim trae ShowPassingFlash (un destello del propio trazo), pero no un
"paquete" físico que recorra un enlace. PulsoDeSenal mueve cualquier
mobject (típicamente un punto con halo de brillo.py) a lo largo de
cualquier VMobject usando point_from_proportion — sirven líneas, arcos,
Bézier, órbitas.

Uso:
    from senal import PulsoDeSenal, destello
    enlace = ArcBetweenPoints(tierra, satelite, angle=-0.6)
    self.play(PulsoDeSenal(paquete, enlace), destello(enlace), run_time=1.4)
"""

from manim import Animation, ShowPassingFlash, YELLOW


class PulsoDeSenal(Animation):
    """Mueve `mobject` a lo largo de `camino` (VMobject con puntos).

    `ida_y_vuelta=True` hace el trayecto de ida y regreso en la misma
    animación (eco / ACK). El rate_func se respeta (smooth por defecto).
    """

    def __init__(self, mobject, camino, ida_y_vuelta=False, **kwargs):
        if not camino.has_points():
            raise ValueError("el camino no tiene puntos")
        self.camino = camino
        self.ida_y_vuelta = ida_y_vuelta
        super().__init__(mobject, **kwargs)

    def interpolate_mobject(self, alpha):
        t = self.rate_func(alpha)
        if self.ida_y_vuelta:
            t = 1 - abs(2 * t - 1)  # 0 -> 1 -> 0
        t = min(max(t, 0.0), 1.0)
        self.mobject.move_to(self.camino.point_from_proportion(t))


def destello(camino, color=YELLOW, ancho=5, cola=0.35):
    """ShowPassingFlash preconfigurado sobre una copia del camino: un
    resplandor que recorre el enlace (combina bien con PulsoDeSenal)."""
    copia = camino.copy().set_fill(opacity=0).set_stroke(color=color,
                                                         width=ancho,
                                                         opacity=0.9)
    return ShowPassingFlash(copia, time_width=cola)
