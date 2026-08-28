class Clip(Scene):
    """14 · Sobre tu cabeza — ESQUELETO.

    Se apaga el mapa y queda el cielo de un patio: los satelites que en ESTE instante estan sobre el horizonte de un punto del suelo, con su elevacion y su azimut. La cifra: cuantos hay sobre tu cabeza ahora mismo, contados con la propagacion del enjambre.

    Piezas de la libreria previstas: `sobre_el_horizonte`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("14 . sobre tu cabeza"))
        self.wait(1.0)
