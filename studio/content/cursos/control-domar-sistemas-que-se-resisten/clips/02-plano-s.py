class Clip2(Scene):
    """2 - El plano s: el mapa del destino. Un par de polos conjugados
    viaja de un buen sitio en el semiplano izquierdo hasta cruzar al
    derecho, mientras a un costado la respuesta al escalon pasa de
    calmada a oscilona y finalmente a una exponencial que se dispara.
    (~36 s)"""

    def _curva_inestable(self, resp, color=C_MAL, muestras=120):
        """Curva roja creciente sobre los MISMOS ejes de `resp` (misma
        escena de coordenadas: origen, ancho y alto), para que el
        ReplacementTransform desde `resp.curva` no mueva el cuadro."""
        origen = np.asarray(resp.eje_t.get_start(), dtype=np.float64)
        ancho, alto = float(resp.eje_t.width), float(resp.eje_y.height)
        ts = np.linspace(0.0, 1.0, muestras)
        frac = np.clip((np.exp(5.0 * ts) - 1.0) / (np.exp(5.0) - 1.0),
                       0.0, 1.0)
        pts = np.array([origen + np.array([t * ancho, f * alto, 0.0])
                        for t, f in zip(ts, frac)])
        curva = VMobject(color=color, stroke_width=3.4)
        curva.set_points_smoothly(pts)
        return curva

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ------------------------------------------
        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("El plano s: el mapa del destino")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.2)

        # --- momento: el mapa y sus polos ------------------------------------
        plano = plano_s(ancho=4.6, alto=3.2).move_to((-2.9, -0.1, 0.0))
        self.play(Create(plano), run_time=0.9)

        pie1 = pie_curso("Cada sistema esconde sus polos: puntos en este "
                         "mapa que dictan su destino.")
        rot.mostrar(pie1, zona="abajo", run_time=0.45)

        p1 = polo(plano, -1.2, 0.9, color=C_OK)
        p2 = polo(plano, -1.2, -0.9, color=C_OK)
        self.play(FadeIn(p1, scale=0.7), FadeIn(p2, scale=0.7), run_time=0.5)

        resp = respuesta_escalon(zeta=0.7, wn=2.24, ancho=4.0, alto=2.0)
        resp.move_to((2.9, -0.1, 0.0))
        self.play(Create(resp.ejes), Create(resp.linea_ref),
                  FadeIn(resp.etiquetas), run_time=0.6)
        self.play(Create(resp.curva), run_time=0.6)
        self.wait(3.5)

        # --- momento: estable ---------------------------------------------
        pie2 = pie_curso("Polos a la izquierda: la respuesta se calma. "
                         "Estable.")
        rot.mostrar(pie2, zona="abajo", run_time=0.45)
        self.wait(5.4)

        # --- momento: cerca del borde, oscila ------------------------------
        pie3 = pie_curso("Cerca del borde: oscila sin ganas de parar.")
        rot.mostrar(pie3, zona="abajo", run_time=0.45)

        oscilona = respuesta_escalon(zeta=0.08, wn=2.24, ancho=4.0, alto=2.0)
        oscilona.move_to(resp.get_center())
        self.play(p1.animate.move_to(plano.punto(-0.1, 0.9)),
                  p2.animate.move_to(plano.punto(-0.1, -0.9)),
                  ReplacementTransform(resp, oscilona), run_time=1.1)
        self.wait(4.6)

        # --- momento: cruza y explota ----------------------------------------
        pie4 = pie_curso("Del lado derecho, el sistema explota. Inestable.")
        rot.mostrar(pie4, zona="abajo", run_time=0.45)

        curva_roja = self._curva_inestable(oscilona)
        self.play(p1.animate.set_color(C_MAL).move_to(plano.punto(0.5, 0.9)),
                  p2.animate.set_color(C_MAL).move_to(plano.punto(0.5, -0.9)),
                  ReplacementTransform(oscilona.curva, curva_roja),
                  run_time=1.1)
        self.play(Indicate(VGroup(p1, p2), color=C_MAL, scale_factor=1.3),
                  run_time=0.5)
        self.wait(4.0)

        # --- momento: el gancho -----------------------------------------------
        pie5 = pie_curso("Controlar es mover los polos al lugar correcto.")
        rot.mostrar(pie5, zona="abajo", run_time=0.45)
        self.wait(6.7)
