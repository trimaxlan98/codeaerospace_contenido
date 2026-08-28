class Clip3(Scene):
    """10.1.3 - La derivada de la fase es la frecuencia instantanea: sobre
    un tono de 60 Hz, la fase desenrollada sube recta y la frecuencia
    queda plana en 60.00 Hz medidos (sobre el interior). (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("La frecuencia instantanea"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        t_rel = T_A[INTERIOR] - T_A[INTERIOR][0]
        fase_rel = FASE_A[INTERIOR] - FASE_A[INTERIOR][0]
        frec_int = FREC_A[INTERIOR]

        # --- la fase desenrollada: una recta ---------------------------------
        f_fase = lambda tt: float(np.interp(tt, t_rel, fase_rel))
        g_fase = grafica(f_fase, (0.0, float(t_rel[-1])),
                         (0.0, float(fase_rel[-1]) * 1.03), ancho=9.0,
                         alto=1.85, color=C_SENAL, etiqueta_y="fase")
        g_fase.move_to(UP * 1.75)
        et_fase = tag_hud("fase", font_size=17, color=C_SENAL)
        et_fase.next_to(g_fase, RIGHT, buff=0.26)
        self.play(FadeIn(g_fase.ejes), FadeIn(et_fase), run_time=0.5)
        self.play(Create(g_fase.curva), run_time=2.6)
        rot.mostrar(cifra_pie("la fase sube recta"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- su derivada: la frecuencia instantanea, plana --------------------
        y0f = float(np.min(frec_int)) - 1.0
        y1f = float(np.max(frec_int)) + 1.0
        f_frec = lambda tt: float(np.interp(tt, t_rel, frec_int))
        g_frec = grafica(f_frec, (0.0, float(t_rel[-1])), (y0f, y1f),
                         ancho=9.0, alto=1.75, color=C_CALCULO,
                         etiqueta_y="Hz")
        g_frec.move_to(DOWN * 1.55)
        et_frec = tag_hud("Hz", font_size=17, color=C_CALCULO)
        et_frec.next_to(g_frec, RIGHT, buff=0.26)
        self.play(FadeIn(g_frec.ejes), FadeIn(et_frec), run_time=0.5)
        self.play(Create(g_frec.curva), run_time=2.6)
        self.wait(2.2)

        marca = g_frec.horizontal_en(FREC_MEDIA, color=C_MUESTRA)
        self.play(Create(marca), run_time=0.8)
        rot.mostrar(cifra_pie(f"frecuencia media {fmt(FREC_MEDIA, 2)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        panel = panel_cifras(f"portadora {fmt(F_PORTADORA, 0)} Hz",
                             (f"media {fmt(FREC_MEDIA, 2)} Hz", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
        rot.mostrar(formula_pie(
            r"f(t) = \frac{1}{2\pi}\frac{d\varphi}{dt}"), zona="abajo",
            run_time=0.5)
        self.wait(6.4)
