class Clip2(Scene):
    """3.2.2 - La curva S del Doppler a 437 MHz: de +10.1 kHz a -10.1 kHz
    medidos, con la pendiente maxima justo en el cenit (cruce por cero).
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La curva S")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.9)

        # --- momento: la frecuencia tambien se mueve ---------------------
        rot.mostrar(pie_curso("Y no solo la distancia cambia: la "
                              "frecuencia que llega tampoco es la que "
                              "se manda."), zona="abajo", run_time=0.5)
        on = onda(T_MIN, FD_KHZ, rango_y=(-13.0, 13.0), ancho=8.6,
                  alto=3.2, color=C_SENAL)
        on.move_to(DOWN * 0.35)
        self.play(FadeIn(on.ejes), run_time=0.4)
        self.play(Create(on.curva), run_time=2.8)
        self.wait(3.0)

        # --- momento: los extremos medidos ---------------------------------
        rot.mostrar(pie_curso("Entra corrida hacia arriba... y sale "
                              "corrida hacia abajo."), zona="abajo",
                    run_time=0.5)
        p_alto = Dot(on.en(T_MIN[0], FD_KHZ[0]), radius=0.07, color=C_CIFRA)
        et_alto = tag_hud(f"+{fmt(FD_MAX_KHZ, 1)} kHz", font_size=19)
        et_alto.next_to(p_alto, UR, buff=0.14)
        p_bajo = Dot(on.en(T_MIN[-1], FD_KHZ[-1]), radius=0.07,
                    color=C_CIFRA)
        et_bajo = tag_hud(f"{fmt(FD_MIN_KHZ, 1)} kHz", font_size=19)
        et_bajo.next_to(p_bajo, DR, buff=0.14)
        self.play(FadeIn(p_alto, scale=1.6), FadeIn(et_alto),
                  FadeIn(p_bajo, scale=1.6), FadeIn(et_bajo), run_time=0.7)
        self.wait(4.6)

        # --- momento: el cruce por cero, pendiente maxima -----------------
        rot.mostrar(pie_curso("Cruza cero justo en el cenit: ahi es "
                              "donde la frecuencia cambia mas deprisa."),
                    zona="abajo", run_time=0.5)
        i0 = idx_de_frac(0.5)
        cero = on.horizontal_en(0.0, color=C_EJE)
        vert = on.vertical_en(0.0, color=C_EJE)
        p_cruce = Dot(on.en(T_MIN[i0], FD_KHZ[i0]), radius=0.08,
                     color=C_CIFRA)
        pendiente = on.curva_de(T_MIN[i0 - 15:i0 + 16],
                                FD_KHZ[i0 - 15:i0 + 16], color=C_CIFRA,
                                grosor=4.0)
        et_cenit = tag_hud("cenit: pendiente maxima", font_size=17,
                           color=C_CIFRA)
        et_cenit.next_to(p_cruce, UP, buff=0.4).shift(RIGHT * 1.1)
        self.play(Create(cero), Create(vert), run_time=0.6)
        self.play(Create(pendiente), FadeIn(p_cruce, scale=1.6),
                  FadeIn(et_cenit), run_time=1.2)
        self.wait(4.4)

        # --- momento: el resumen de la curva medida ------------------------
        panel = panel_derecha(
            tag_hud(f"portadora {fmt(F_UHF_MHZ, 0)} MHz"),
            tag_hud(f"maximo +{fmt(FD_MAX_KHZ, 1)} kHz"),
            tag_hud(f"minimo {fmt(FD_MIN_KHZ, 1)} kHz"))
        rot.mostrar(pie_curso("Diez kilohercios arriba, diez abajo: la "
                              "frecuencia recibida nunca es la "
                              "transmitida."), zona="abajo", run_time=0.5)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(6.4)
