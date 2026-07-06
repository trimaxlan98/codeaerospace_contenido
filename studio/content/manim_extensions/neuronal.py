"""Red neuronal animable para las series de IA.

Construye la red completa (neuronas + conexiones) como un VGroup y expone
`activacion()`: una pasada forward donde el pulso recorre las conexiones
capa a capa y enciende las neuronas al llegar. Todo con primitivas vectoriales
baratas (ShowPassingFlash + Indicate), sin updaters residuales.

Uso:
    from neuronal import RedNeuronal
    red = RedNeuronal(capas=(4, 6, 6, 3))
    self.play(Create(red), run_time=2)
    self.play(red.activacion(color=YELLOW))
"""

from manim import (AnimationGroup, Circle, Indicate, Line, ShowPassingFlash,
                   Succession, VGroup, BLUE_B, GREY_C, YELLOW)


class RedNeuronal(VGroup):
    def __init__(self, capas=(4, 6, 6, 3), separacion_x=1.9,
                 separacion_y=0.62, radio=0.13, color_neurona=BLUE_B,
                 color_conexion=GREY_C, **kwargs):
        super().__init__(**kwargs)
        self.capas_neuronas: list[VGroup] = []
        self.conexiones: list[VGroup] = []

        for i, n in enumerate(capas):
            capa = VGroup(*[
                Circle(radius=radio, color=color_neurona, stroke_width=2.5,
                       fill_color=color_neurona, fill_opacity=0.12)
                for _ in range(n)
            ])
            capa.arrange(direction=[0, -1, 0], buff=separacion_y)
            capa.move_to([i * separacion_x, 0, 0])
            self.capas_neuronas.append(capa)

        for izq, der in zip(self.capas_neuronas, self.capas_neuronas[1:]):
            grupo = VGroup(*[
                Line(a.get_center(), b.get_center(), stroke_width=1.4,
                     color=color_conexion, stroke_opacity=0.35,
                     buff=radio * 1.15)
                for a in izq for b in der
            ])
            self.conexiones.append(grupo)

        # Conexiones primero para que queden debajo de las neuronas.
        self.add(*self.conexiones, *self.capas_neuronas)
        self.center()

    def activacion(self, color=YELLOW, ancho=4.5, cola=0.5):
        """Una pasada forward: destellos por las conexiones de cada salto y
        pulso en las neuronas de la capa que recibe."""
        pasos = []
        for grupo, capa_destino in zip(self.conexiones,
                                       self.capas_neuronas[1:]):
            flashes = [
                ShowPassingFlash(
                    linea.copy().set_stroke(color=color, width=ancho,
                                            opacity=1),
                    time_width=cola)
                for linea in grupo
            ]
            llegada = [Indicate(neurona, color=color, scale_factor=1.25)
                       for neurona in capa_destino]
            pasos.append(AnimationGroup(*flashes, run_time=0.7))
            pasos.append(AnimationGroup(*llegada, run_time=0.45))
        return Succession(*pasos)
