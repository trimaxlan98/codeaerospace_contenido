class Clip(Scene):
    """10 · La malla — ESQUELETO.

    Un paquete cruza el oceano saltando de satelite en satelite; al lado, la ruta por fibra. La cifra: la longitud del camino por la malla (Dijkstra sobre saltos reales, con la atmosfera bloqueando los rayos rasantes) y su latencia frente a la de la fibra. El rodeo del cable y los 2c/3 son SUPUESTOS: se declaran.

    Piezas de la libreria previstas: `ruta_malla`, `latencia_fibra`, `gran_circulo_km`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("10 . la malla"))
        self.wait(1.0)
