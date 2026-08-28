class Clip(Scene):
    """12 · El trafico no esta repartido — ESQUELETO.

    La constelacion pasa y la mayor parte del tiempo esta sobre agua; los haces fijos riegan el oceano. La cifra: el porcentaje del tiempo-satelite sobre el mar, contado con la mascara de continentes de la propia libreria.

    Piezas de la libreria previstas: `tiempo_sobre_mar`, `mascara_tierra`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("12 . el trafico no esta repartido"))
        self.wait(1.0)
