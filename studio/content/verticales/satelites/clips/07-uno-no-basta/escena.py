class Clip(Scene):
    """07 · Uno no basta — ESQUELETO.

    El mapa se va pintando: 1 satelite, 6, 24, 66, 240; los huecos se cierran a ojo mientras la cifra sube. La cifra: el porcentaje de la Tierra cubierta por cada constelacion, medido sobre la malla con peso cos(lat) y promediado en varios instantes de la orbita.

    Piezas de la libreria previstas: `cobertura_vs_n`, `conteo_cobertura`, `fraccion_cubierta`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("07 . uno no basta"))
        self.wait(1.0)
