class Clip3(Scene):
    """7.1.3 - La tasa de cambio del Doppler (derivada de la curva S, Hz
    por segundo): siempre negativa, con el maximo en valor absoluto justo
    en el cenit, 123.1 Hz/s. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La tasa del Doppler"), zona="arriba",
                   run_time=0.6)
        self.wait(0.5)

        t_min = T_P / 60.0
        tasa_hz_s = TASA
        piso = -TASA_MAX * 1.65
        techo = TASA_MAX * 0.15
        esp = S.Espectro(t_min, tasa_hz_s, piso=piso, techo=techo,
                         ancho=11.2, alto=4.6, color=C_CALCULO, area=False)
        esp.move_to(DOWN * 0.2)
        cero = Line(esp.en(t_min[0], 0.0), esp.en(t_min[-1], 0.0),
                   color=C_EJE, stroke_width=1.5)
        u_x = tag_junto(esp.ejes, "min", RIGHT, buff=0.2, font_size=20)
        u_y = tag_hud("Hz/s", font_size=18)
        u_y.move_to(esp.en(t_min[0], 0.0) + UP * 0.35 + RIGHT * 0.35)

        self.play(Create(esp.ejes), Create(cero), FadeIn(u_x), FadeIn(u_y),
                  run_time=1.0)
        self.wait(0.4)
        self.play(Create(esp.curva), run_time=3.6)
        self.wait(2.2)

        i0 = len(t_min) // 2
        cruce = Dot(esp.en(t_min[i0], tasa_hz_s[i0]), radius=0.09,
                   color=C_CALCULO)
        vert = DashedLine(esp.en(t_min[i0], 0.0),
                          esp.en(t_min[i0], tasa_hz_s[i0]), color=C_EJE,
                          stroke_width=1.6, dash_length=0.08)
        cenit = tag_hud("cenit: pendiente maxima", font_size=18)
        cenit.next_to(cruce, DOWN, buff=0.35)
        self.play(Create(vert), run_time=0.6)
        self.play(FadeIn(cruce, scale=1.6), FadeIn(cenit), run_time=0.7)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"\dot f = \tfrac{d}{dt}\, f_d(t)"),
                   zona="abajo", run_time=0.5)
        self.wait(4.4)

        et_max = tag_hud(f"{fmt(TASA_MAX, 1)} Hz/s", font_size=22)
        et_max.next_to(cruce, DOWN, buff=0.4)
        self.play(FadeOut(cenit), run_time=0.35)
        self.play(FadeIn(et_max), run_time=0.35)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"{fmt(TASA_MAX, 1)} Hz/s en el cenit"),
                   zona="abajo", run_time=0.5)
        self.wait(10.5)
