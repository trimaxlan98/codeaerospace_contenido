class Clip(Scene):
    """04 · La huella — ESQUELETO.

    El casquete que un satelite ve: el cono baja al mapa y pinta una tapa, con 10 grados de elevacion minima. La cifra: el radio de la huella en km y el porcentaje de la SUPERFICIE terrestre que ve uno solo — calculado sobre la esfera, nunca contando pixeles del mapa plano.

    Piezas de la libreria previstas: `radio_huella_km`, `fraccion_visible`, `angulo_cobertura`.

    Pendiente de escribir. El stub existe para que `render_vertical.py` no
    aborte y para poder producir las piezas en paralelo.
    """

    def construct(self):
        self.add(hud_pieza("04 . la huella"))
        self.wait(1.0)
