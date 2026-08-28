class Clip(Scene):
    """03 · La elipse — ESQUELETO.

    La orbita no tiene por que ser un circulo. Una elipse muestreada en TIEMPOS iguales (no en angulos iguales) apelotona los puntos en el apogeo y los separa en el perigeo: corre abajo y se arrastra arriba. La cifra: las dos areas barridas en la misma fraccion de periodo, medidas sobre la trayectoria dibujada, y su cociente 1.000.

    Piezas de la libreria previstas: `elipse_kepler`, `areas_barridas`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("03 . la elipse"))
        self.wait(1.0)
