class Clip1(Scene):
    """1 - La promesa rota. Portada; la promesa de Laplace y, detras, el
    atractor dibujandose; el gemelo cian arranca del mismo punto y en
    segundos vive otro futuro. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso ----------------------------------
        portada = VGroup(
            titulo_marca("Caos", font_size=54),
            Text("el orden escondido", font_size=25, color=C_GEMELO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.2)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.8)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("La promesa rota")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la promesa de Laplace -------------------------------
        rot.mostrar(pie_curso("1814: Laplace promete que conocer el "
                              "presente es conocer el futuro."),
                    zona="abajo", run_time=0.5)
        cita = VGroup(
            Text("«Una inteligencia que conociera todas las fuerzas…»",
                 font_size=22, color=C_TENUE),
            Text("«…abarcaría en una sola fórmula el porvenir.»",
                 font_size=22, color=C_TENUE),
        ).arrange(DOWN, buff=0.2)
        cita.move_to(UP * 2.35)
        self.play(FadeIn(cita, shift=0.15 * UP), run_time=0.9)

        pts_a, pts_b, _ = par_lorenz(EPS_LORENZ, n=8000)
        traza_a = curva_lorenz(pts_a, alto=4.0, color=C_SISTEMA,
                               grosor=1.8)
        traza_a.shift(DOWN * 0.55)
        traza_a.set_stroke(opacity=0.9)
        self.play(Create(traza_a), run_time=4.6, rate_func=linear)
        self.wait(1.4)

        # --- momento: el gemelo que traiciona -----------------------------
        rot.mostrar(pie_curso("Dos mundos idénticos hasta la sexta cifra "
                              "decimal…"), zona="abajo", run_time=0.5)
        # `como=`: el gemelo comparte centro y escala con la original, y
        # recibe el MISMO shift — la separacion que se ve es la fisica,
        # no un artefacto de centrar cada bbox por su cuenta.
        traza_b = curva_lorenz(pts_b, alto=4.0, color=C_GEMELO, grosor=1.8,
                               como=traza_a)
        traza_b.shift(DOWN * 0.55)
        traza_b.set_stroke(opacity=0.85)
        self.play(Create(traza_b), run_time=4.2, rate_func=linear)
        self.wait(2.4)

        # --- momento: la traicion -----------------------------------------
        rot.mostrar(pie_curso("…y en minutos, dos futuros distintos. Este "
                              "curso es sobre esa traición."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cita), run_time=0.6)
        self.wait(6.8)
