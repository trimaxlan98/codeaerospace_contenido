class Clip(Scene):
    """08 · Los planos — ESQUELETO.

    La Walker-delta por dentro: los planos con su RAAN repartido y la fase entre planos, girando la camara. La cifra: hasta que latitud llega una constelacion inclinada 53 grados (68 grados) — los polos se quedan fuera, y por eso Iridium va a 86.

    Piezas de la libreria previstas: `latitud_maxima_cubierta`, `ConstelacionWalker`, `AnimarWalker`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("08 . los planos"))
        self.wait(1.0)
