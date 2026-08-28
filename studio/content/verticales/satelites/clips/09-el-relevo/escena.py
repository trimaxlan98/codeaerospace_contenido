class Clip(Scene):
    """09 · El relevo — ESQUELETO.

    Un punto en el suelo y el enjambre encima: la linea salta de un satelite al siguiente antes de que el primero se ponga. La cifra: cuantos relevos hay en 90 minutos y cada cuanto, mirando instante a instante cual es el satelite mas alto. Los huecos sin servicio se cuentan aparte y se declaran.

    Piezas de la libreria previstas: `relevos`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("09 . el relevo"))
        self.wait(1.0)
