class Clip3(Scene):
    """4.3.3 - Las otras dos de Maxwell: un B que crece enrolla un E
    horario (rot medido -2.0) y un E que crece enrolla un B antihorario
    (+2.0). El encadenamiento, con dos ruedecitas girando. (~34 s)"""

    R0 = 0.30
    FACTOR = 1.85

    def _nucleo(self, pl, color, radio):
        """El campo que sale del plano, visto de punta: un circulo con su
        punto en el centro (el simbolo de "hacia el lector")."""
        g = VGroup(Circle(radius=radio, color=color, stroke_width=3.2,
                          fill_color=color, fill_opacity=0.16),
                   Dot(radius=0.07, color=color))
        g.move_to(pl.p(0, 0))
        return g

    def _panel(self, etiqueta, cifra):
        fila = VGroup(tag_hud(etiqueta, font_size=16, color=C_TENUE),
                      tag_hud(cifra, font_size=24, color=C_RES))
        fila.arrange(DOWN, buff=0.07)
        return _con_fondo(fila, buff=0.14, opacidad=0.92).to_corner(
            UR, buff=0.5).shift(DOWN * 0.98)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Leer a Maxwell: los rotacionales")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: quedan dos, y hablan de giro ----------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Las otras dos ecuaciones hablan de "
                              "rotacional: de remolinos."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # --- momento: un B que crece enrolla un E -----------------------
        rot.mostrar(pie_curso("Un campo magnético que CRECE enrolla a su "
                              "alrededor un campo eléctrico."),
                    zona="abajo", run_time=0.5)
        nucleo = self._nucleo(pl, C_CIFRA, self.R0)
        etiqueta = _con_fondo(tag_hud("B crece", font_size=19,
                                      color=C_CIFRA), buff=0.12,
                              opacidad=0.92)
        etiqueta.move_to(pl.p(0, -2.5))
        self.play(FadeIn(nucleo, scale=0.5), FadeIn(etiqueta), run_time=0.5)
        self.play(nucleo.animate.scale(self.FACTOR), run_time=1.6)
        remolino = campo_flechas(pl, REMOLINO_E, escala=0.6,
                                 magnitud_max=2.4, **MALLA_REMOLINO)
        self.play(LaggedStart(*[GrowArrow(f) for f in remolino.flechas],
                              lag_ratio=0.04), run_time=1.7)
        ley_e = _con_fondo(
            MathTex(r"\nabla\times E = -\,\partial B/\partial t",
                    font_size=34, color=C_CALCULO), buff=0.14,
            opacidad=0.92)
        ley_e.move_to(pl.p(0, 2.75))
        panel_e = self._panel("rot medido (E)", fmt(ROT_E))
        self.play(FadeIn(ley_e, shift=0.15 * DOWN),
                  FadeIn(panel_e, shift=0.15 * LEFT), run_time=0.7)
        self.wait(1.6)

        # --- momento: y al reves ----------------------------------------
        rot.mostrar(pie_curso("Y al revés: un campo eléctrico que cambia "
                              "enrolla un campo magnético."), zona="abajo",
                    run_time=0.5)
        destino = self._nucleo(pl, C_GRAD, self.R0).scale(self.FACTOR)
        etiqueta_e = _con_fondo(tag_hud("E crece", font_size=19,
                                        color=C_GRAD), buff=0.12,
                                opacidad=0.92)
        etiqueta_e.move_to(pl.p(0, -2.5))
        ley_b = _con_fondo(
            MathTex(r"\nabla\times B = \mu_0\varepsilon_0\,"
                    r"\partial E/\partial t", font_size=34,
                    color=C_CALCULO), buff=0.14, opacidad=0.92)
        ley_b.move_to(pl.p(0, 2.75))
        self.play(Transform(nucleo, destino),
                  Transform(remolino, remolino.con_campo(REMOLINO_B)),
                  FadeOut(etiqueta), FadeIn(etiqueta_e),
                  FadeOut(ley_e), FadeIn(ley_b), run_time=1.7)
        panel_b = self._panel("rot medido (B)", fmt(ROT_B))
        panel_b.shift(DOWN * 1.05)
        self.play(nucleo.animate.scale(1.22),
                  FadeIn(panel_b, shift=0.15 * LEFT), run_time=1.0)
        self.wait(2.0)

        # --- momento: la cadena, con dos ruedecitas ---------------------
        rot.mostrar(pie_curso("Cada uno enciende al otro. Esa cadena no "
                              "necesita cargas ni cables."), zona="abajo",
                    run_time=0.5)
        rd_e = rueda(pl, P_RUEDA_E, radio=0.52, color=C_GRAD)
        rd_b = rueda(pl, P_RUEDA_B, radio=0.52, color=C_CIFRA)
        rot_e = _con_fondo(tag_hud("remolino de E", font_size=18,
                                   color=C_GRAD), buff=0.11, opacidad=0.92)
        rot_e.move_to(pl.p(P_RUEDA_E[0], 1.15))
        rot_b = _con_fondo(tag_hud("remolino de B", font_size=18,
                                   color=C_CIFRA), buff=0.11, opacidad=0.92)
        rot_b.move_to(pl.p(P_RUEDA_B[0], 1.15))
        giro_e = _con_fondo(tag_hud(f"giro = {fmt(VEL_E)} rad/s",
                                    font_size=17, color=C_RES), buff=0.11,
                            opacidad=0.92)
        giro_e.move_to(pl.p(P_RUEDA_E[0], -1.4))
        giro_b = _con_fondo(tag_hud(f"giro = {fmt(VEL_B)} rad/s",
                                    font_size=17, color=C_RES), buff=0.11,
                            opacidad=0.92)
        giro_b.move_to(pl.p(P_RUEDA_B[0], -1.4))
        self.play(FadeOut(remolino), FadeOut(nucleo), FadeOut(etiqueta_e),
                  run_time=0.5)
        self.play(FadeIn(rd_e), FadeIn(rd_b), FadeIn(rot_e), FadeIn(rot_b),
                  FadeIn(giro_e), FadeIn(giro_b), run_time=0.6)
        for _ in range(2):
            self.play(Rotate(rd_e.aspas, angle=VEL_E * 1.3,
                             about_point=rd_e.centro()), run_time=1.3,
                      rate_func=linear)
            self.play(Rotate(rd_b.aspas, angle=VEL_B * 1.3,
                             about_point=rd_b.centro()), run_time=1.3,
                      rate_func=linear)
        self.wait(0.9)

        rot.mostrar(pie_curso("Un remolino que se sostiene a sí mismo y "
                              "se va: eso es una onda."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
