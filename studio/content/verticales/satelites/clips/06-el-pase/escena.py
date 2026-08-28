class Clip(Scene):
    """06 · El pase — ESQUELETO.

    Desde el suelo: la boveda polar, el satelite entra por el horizonte, culmina y se va. La cifra: cuanto dura el pase y cuanto sube, medidas de la ventana de visibilidad. Ojo con el knob: lo que decide si te pasa por encima es el RAAN de su plano, no la fase.

    Piezas de la libreria previstas: `pase`, `ventana_visibilidad`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("06 . el pase"))
        self.wait(1.0)
