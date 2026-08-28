class Clip(Scene):
    """13 · La red aprende — ESQUELETO.

    El asignador de haces: primero reparte a ciegas, luego va moviendo cada haz a donde mas sube la demanda servida. La cifra: la demanda servida antes y despues, medida sobre la matriz de cobertura REAL del enjambre. La matriz de demanda es sintetica y se declara en gris: lo que se mide es la MEJORA.

    Piezas de la libreria previstas: `asignar_haces`, `demanda_por_celda`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("13 . la red aprende"))
        self.wait(1.0)
