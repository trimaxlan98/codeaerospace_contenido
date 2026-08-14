class Clip3(Scene):
    """1.3.3 - Dependencia con la altitud: la atmosfera estandar (ISA).

    Si `a` solo depende de T, y T cae con la altitud, entonces subir cambia
    el Mach sin tocar los mandos. El remate del clip es exactamente ese: el
    mismo avion, la misma velocidad verdadera, dos regimenes. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Más alto, más lento el sonido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        perfil = perfil_isa(ancho=4.4, alto=3.0)
        perfil.move_to(LEFT * 2.9 + DOWN * 0.15)
        self.play(FadeIn(perfil.ejes), run_time=0.6)
        self.play(Create(perfil.curva), run_time=1.6)
        rot.mostrar(pie_curso("En la troposfera la temperatura cae seis "
                              "grados y medio por kilómetro."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: la tropopausa ---------------------------------------
        self.play(FadeIn(perfil.tropopausa), run_time=0.7)
        rot.mostrar(pie_curso("A once kilómetros deja de caer. Y con ella se "
                              "estanca la velocidad del sonido."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el mismo avion, dos alturas --------------------------
        # Las dos columnas cuelgan del perfil por sus propios localizadores:
        # si el grafico se mueve, las guias lo siguen.
        rot.mostrar(pie_curso(f"Ahora un avión a {V_EJEMPLO:.0f} metros por "
                              "segundo verdaderos. Los mismos, arriba y "
                              "abajo."), zona="abajo", run_time=0.5)
        self.wait(1.2)

        tarjetas = VGroup()
        for h, mach, color, alto in ((0.0, M_MAR, C_SUB, -1.35),
                                     (11000.0, M_TROPO, C_TRANS, 0.95)):
            punto = Dot(perfil.punto_de(h), radius=0.068, color=color)
            texto = VGroup(
                Text(f"a = {perfil.a(h):.0f} m/s", font=FUENTE_HUD,
                     font_size=17, color=C_TENUE),
                Text(f"M = {mach:.2f}", font=FUENTE_HUD, font_size=24,
                     color=color)).arrange(DOWN, buff=0.14)
            texto.move_to(RIGHT * 3.15 + UP * alto)
            guia = DashedLine(punto.get_center(), texto.get_left()
                              + LEFT * 0.14, stroke_width=1.2, color=color,
                              dash_length=0.07).set_opacity(0.5)
            tarjetas.add(VGroup(guia, punto, texto))

        self.play(LaggedStart(*[FadeIn(t, shift=0.1 * RIGHT)
                                for t in tarjetas], lag_ratio=0.5),
                  run_time=1.6)
        self.wait(3.4)

        rot.mostrar(pie_curso(f"Abajo vuela a Mach {M_MAR:.2f}. "
                              f"Arriba, a {M_TROPO:.2f}."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Sin tocar los mandos ha pasado de subsónico "
                              "cómodo a transónico."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
