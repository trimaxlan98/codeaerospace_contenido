class Clip(Scene):
    """02 · Alto es lento — ESQUELETO.

    Cuatro alturas compitiendo en la misma columna: LEO a 550 km, los 2000 km, los 20200 de GPS y la GEO a 35786. El de arriba parece parado. La cifra: el periodo orbital de cada uno, resuelto con la tercera de Kepler por satelites.periodo_orbital — y la GEO cae en el dia sidereo, 23 h 56 min, no en 24 h.

    Piezas de la libreria previstas: `periodo_orbital`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("02 . alto es lento"))
        self.wait(1.0)
