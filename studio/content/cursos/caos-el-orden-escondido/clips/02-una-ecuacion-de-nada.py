class Clip2(Scene):
    """2 - Una ecuacion de nada. La parabola de los conejos: equilibrio
    (r=2.9), vals de dos pasos (r=3.3) y caos que no se repite (r=3.9),
    todo con la misma telarana. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Una ecuación de nada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la ecuacion y su parabola ---------------------------
        rot.mostrar(pie_curso("Una población de conejos: crecen si son "
                              "pocos, se frenan si son muchos."),
                    zona="abajo", run_time=0.5)
        formula = MathTex(r"x_{n+1} = r\,x_n(1 - x_n)", font_size=34,
                          color=C_SISTEMA)
        formula.move_to(RIGHT * 4.15 + UP * 2.1)
        self.play(Write(formula), run_time=0.9)

        tela = cobweb(R_EQUILIBRIO, lado=4.4)
        tela.move_to(DOWN * 0.35)
        r_tag = tag_hud(f"r = {R_EQUILIBRIO}", font_size=17)
        r_tag.move_to(RIGHT * 4.15 + UP * 1.45)
        self.play(Create(tela.caja), Create(tela.diagonal), run_time=0.7)
        self.play(Create(tela.parabola), run_time=1.0)
        rot.mostrar(r_tag, zona="r", run_time=0.4)
        self.wait(1.2)

        # --- momento: el equilibrio ---------------------------------------
        rot.mostrar(pie_curso("Con r pequeño, la población se calma en un "
                              "equilibrio."), zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[Create(s) for s in tela.telarana],
                              lag_ratio=0.35), run_time=3.2)
        pf = tela.punto_fijo()
        punto = Dot(tela.en(pf, pf), radius=0.07, color=C_ORDEN)
        self.play(FadeIn(punto, scale=2.0), run_time=0.6)
        self.wait(2.6)

        # --- momento: el vals de dos pasos --------------------------------
        rot.mostrar(pie_curso("Sube r y la población oscila: un año "
                              "muchos, un año pocos."), zona="abajo",
                    run_time=0.5)
        tela2 = tela.con_r(R_CICLO2)
        r_tag2 = tag_hud(f"r = {R_CICLO2}", font_size=17)
        r_tag2.move_to(RIGHT * 4.15 + UP * 1.45)
        self.play(FadeOut(punto), run_time=0.3)
        self.play(Transform(tela, tela2), run_time=1.8)
        rot.mostrar(r_tag2, zona="r", run_time=0.4)
        o2 = orbita_logistica(R_CICLO2, 0.2, 400)[-2:]
        ciclo = VGroup(*[Dot(tela.en(v, v), radius=0.06, color=C_ORDEN)
                         for v in o2])
        self.play(FadeIn(ciclo), run_time=0.5)
        self.wait(3.0)

        # --- momento: el caos ---------------------------------------------
        rot.mostrar(pie_curso("Sube r un poco más… y no se repite nunca. "
                              "Eso es el caos."), zona="abajo",
                    run_time=0.5)
        tela3 = tela.con_r(R_CAOS)
        r_tag3 = tag_hud(f"r = {R_CAOS}", font_size=17, color=C_SISTEMA)
        r_tag3.move_to(RIGHT * 4.15 + UP * 1.45)
        self.play(FadeOut(ciclo), run_time=0.3)
        self.play(Transform(tela, tela3), run_time=2.0)
        rot.mostrar(r_tag3, zona="r", run_time=0.4)
        self.wait(6.2)
