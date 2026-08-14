class Clip3(Scene):
    """3 - La cascada. El diagrama de bifurcacion completo, los tres
    primeros escalones marcados y los cocientes convergiendo a la
    constante universal de Feigenbaum. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La cascada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el mapa de todos los destinos -----------------------
        rot.mostrar(pie_curso("Un mapa de todos los destinos: cada columna "
                              "vertical es un valor de r."), zona="abajo",
                    run_time=0.5)
        diagrama = imagen_bifurcacion(alto_escena=4.9)
        diagrama.move_to(LEFT * 1.15 + UP * 0.25)
        diagrama.width = min(diagrama.width, 9.2)
        self.play(FadeIn(diagrama), run_time=1.6)
        eje_r = tag_junto(diagrama, "r →", DOWN, buff=0.22, font_size=18)
        self.play(FadeIn(eje_r), run_time=0.4)
        self.wait(4.6)

        # --- momento: la escalera se aprieta ------------------------------
        rot.mostrar(pie_curso("1 se vuelve 2, 2 se vuelve 4, 4 se vuelve "
                              "8… cada vez más rápido."), zona="abajo",
                    run_time=0.5)
        marcas = VGroup()
        for r_n in R_BIFURCACIONES[:3]:
            linea = DashedLine(diagrama.punto_de(r_n, 0.02),
                               diagrama.punto_de(r_n, 0.98),
                               stroke_width=1.8, color=C_GEMELO)
            linea.set_stroke(opacity=0.8)
            marca = VGroup(linea, tag_hud(f"{r_n:.3f}", font_size=13))
            marca[1].next_to(linea, UP, buff=0.08)
            marcas.add(marca)
            self.play(Create(linea), FadeIn(marca[1]), run_time=0.7)
        self.wait(3.2)

        # --- momento: el ritmo es una constante ---------------------------
        cocientes = VGroup(*[
            tag_hud(f"{c:.3f}", font_size=17, color=C_TENUE)
            for c in COCIENTES_FEIG])
        cocientes.arrange(DOWN, buff=0.30, aligned_edge=RIGHT)
        cocientes.move_to(RIGHT * 5.15 + UP * 1.5)
        self.play(LaggedStart(*[FadeIn(c, shift=0.15 * DOWN)
                                for c in cocientes], lag_ratio=0.4),
                  run_time=1.6)
        delta = MathTex(rf"\delta = {FEIGENBAUM_DELTA:.4f}\ldots",
                        font_size=30, color=C_GEMELO)
        delta.next_to(cocientes, DOWN, buff=0.45)
        flecha = Arrow(cocientes.get_bottom() + DOWN * 0.02,
                       delta.get_top() + UP * 0.02, buff=0.06,
                       stroke_width=2.5, color=C_EJE, max_tip_length_to_length_ratio=0.4)
        self.play(GrowArrow(flecha), Write(delta), run_time=1.1)
        self.wait(2.4)

        # --- momento: universalidad ---------------------------------------
        rot.mostrar(pie_curso("Feigenbaum, 1978: el mismo ritmo en "
                              "cualquier sistema que se duplica. Una "
                              "constante de la naturaleza."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(delta, color=C_GEMELO), run_time=0.9)
        self.wait(7.0)
