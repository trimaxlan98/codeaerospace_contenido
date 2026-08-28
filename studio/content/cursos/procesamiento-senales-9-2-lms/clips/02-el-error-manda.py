class Clip2(Scene):
    """9.2.2 - El error es la orden: w[n+1] = w[n] + mu e[n] x[n]. Los
    cinco coeficientes acaban copiando el camino y la voz sale limpia.
    (~36 s)"""

    A, B = 2000, 2300        # ventana dibujada, ya convergido

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("El error manda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(r"w[n+1] = w[n] + \mu\,e[n]\,x[n]"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- 1. los cinco coeficientes, real contra aprendido ------------
        y_c = (-0.68, 1.12)
        real = Secuencia(CAMINO, 0, y_c, ancho=4.2, alto=2.2,
                         color=C_MUESTRA, radio=0.072, grosor=3.2,
                         eje_y=False)
        real.move_to(LEFT * 3.15 + UP * 0.55)
        et_real = tag_hud("camino real", font_size=19, color=C_MUESTRA)
        # los rotulos van a una altura FIJA: el bbox de cada pieza
        # depende de sus valores y si no bailan de una a otra.
        et_real.move_to(np.array([real.get_x(), 2.05, 0.0]))
        self.play(FadeIn(real), FadeIn(et_real), run_time=0.9)
        self.wait(1.5)

        w = W_FIN[MU_DEMO]
        apr = real.con_valores(w, color=C_APREND)
        apr.move_to(RIGHT * 3.15 + UP * 0.55)
        et_apr = tag_hud("aprendido", font_size=19, color=C_APREND)
        et_apr.move_to(np.array([apr.get_x(), 2.05, 0.0]))
        self.play(FadeIn(apr.ejes), FadeIn(et_apr), run_time=0.5)

        vals = VGroup()
        pasos = []
        for i, v in enumerate(w):
            t = tag_hud(fmt(v, 2), font_size=16, color=C_APREND)
            t.next_to(apr.punto(i), UP if v >= 0 else DOWN, buff=0.11)
            vals.add(t)
            pasos.append(AnimationGroup(
                FadeIn(VGroup(apr.tallos[i], apr.puntos[i])), FadeIn(t)))
        self.play(LaggedStart(*pasos, lag_ratio=0.34), run_time=2.6)
        self.wait(2.2)

        rot.mostrar(cifra_pie(
            f"error coef {fmt(100 * ERR_COEF[MU_DEMO], 1)} %"),
            zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- 2. lo que se oye al final ------------------------------------
        self.play(FadeOut(real), FadeOut(et_real), FadeOut(apr.ejes),
                  FadeOut(apr.tallos), FadeOut(apr.puntos), FadeOut(vals),
                  FadeOut(et_apr), run_time=0.7)

        a, b = self.A, self.B
        mic = Secuencia(D_LMS[a:b], a, (-3.7, 3.7), ancho=9.2, alto=1.65,
                        color=C_SENAL, radio=0.015, grosor=1.5, eje_y=False)
        mic.move_to(UP * 1.60 + RIGHT * 0.55)
        et_mic = tag_hud("microfono", font_size=19, color=C_SENAL)
        et_mic.next_to(mic, LEFT, buff=0.24)
        self.play(FadeIn(mic), FadeIn(et_mic), run_time=0.9)
        self.wait(1.6)

        sal = Secuencia(E_LMS[MU_DEMO][a:b], a, (-1.25, 1.25), ancho=9.2,
                        alto=1.65, color=C_SALIDA, radio=0.015, grosor=1.5,
                        eje_y=False)
        sal.move_to(DOWN * 1.20 + RIGHT * 0.55)
        et_sal = tag_hud("recuperada", font_size=19, color=C_SALIDA)
        et_sal.next_to(sal, LEFT, buff=0.24)
        self.play(FadeIn(sal), FadeIn(et_sal), run_time=1.0)
        self.wait(1.4)

        objetivo = sal.curva_de(np.arange(a, b), LIMPIA[a:b], color=C_IDEAL,
                                grosor=2.8)
        et_obj = tag_hud("limpia", font_size=19, color=C_IDEAL)
        et_obj.next_to(sal, DOWN, buff=0.22)
        self.play(Create(objetivo), FadeIn(et_obj), run_time=1.4)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"ruido -{fmt(MEJORA[MU_DEMO], 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras((f"{N_TAPS_LMS} coeficientes", C_APREND),
                             (f"coef {fmt(100 * ERR_COEF[MU_DEMO], 1)} %",
                              C_CALCULO),
                             (f"ruido -{fmt(MEJORA[MU_DEMO], 1)} dB",
                              C_SALIDA),
                             desplazar=DOWN * 2.55)
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.6)
