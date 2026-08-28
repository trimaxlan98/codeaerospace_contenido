class Clip(Scene):
    """05 · La traza — ESQUELETO.

    El ground track: la sinusoide que no cierra sobre si misma, porque mientras el satelite daba la vuelta el planeta se giro debajo. La cifra: el corrimiento hacia el oeste por vuelta, en grados y en km de ecuador.

    Piezas de la libreria previstas: `corrimiento_traza`, `subsatelites_walker`, `traza_terrestre`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("05 . la traza"))
        self.wait(1.0)
