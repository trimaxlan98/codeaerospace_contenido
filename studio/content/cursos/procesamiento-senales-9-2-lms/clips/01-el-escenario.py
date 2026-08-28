class Clip1(Scene):
    """9.2.1 - El escenario de la cancelacion: la voz limpia, el ruido que
    se cuela por un camino desconocido y un microfono de referencia que
    oye SOLO el ruido, pero por otro camino. (~38 s)"""

    N_VER = 200          # muestras dibujadas (dos ciclos de la voz)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("El escenario"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n = self.N_VER
        y_d = (-3.7, 3.7)

        # --- 1. lo que se quiere y lo que llega --------------------------
        lim = Secuencia(LIMPIA[:n], 0, (-1.05, 1.05), ancho=10.0, alto=1.15,
                        color=C_IDEAL, radio=0.017, grosor=1.6, eje_y=False)
        lim.move_to(UP * 1.95)
        et_lim = tag_junto(lim, "limpia", direccion=UP, buff=0.16,
                           color=C_IDEAL)
        self.play(FadeIn(lim), FadeIn(et_lim), run_time=0.9)
        self.wait(1.6)

        mic = Secuencia(D_LMS[:n], 0, y_d, ancho=10.0, alto=1.9,
                        color=C_SENAL, radio=0.017, grosor=1.6, eje_y=False)
        mic.move_to(DOWN * 1.25)
        et_mic = tag_junto(mic, "microfono", direccion=DOWN, buff=0.18,
                           color=C_SENAL)
        self.play(FadeIn(mic), FadeIn(et_mic), run_time=1.0)
        rot.mostrar(formula_pie(r"d[n] = s[n] + v[n]"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # la voz sigue ahi dentro, enterrada
        enterrada = mic.curva_de(np.arange(n), LIMPIA[:n], color=C_IDEAL,
                                 grosor=2.6)
        self.play(Create(enterrada), run_time=1.4)
        self.wait(2.4)

        # --- 2. de donde sale ese ruido ----------------------------------
        self.play(FadeOut(lim), FadeOut(et_lim), FadeOut(mic),
                  FadeOut(et_mic), FadeOut(enterrada), run_time=0.8)

        ref = Secuencia(REF[:n], 0, y_d, ancho=8.4, alto=1.25,
                        color=C_MUESTRA, radio=0.017, grosor=1.6,
                        eje_y=False)
        ref.move_to(UP * 2.50 + RIGHT * 0.55)
        et_ref = tag_hud("referencia", font_size=19, color=C_MUESTRA)
        et_ref.next_to(ref, LEFT, buff=0.24)
        self.play(FadeIn(ref), FadeIn(et_ref), run_time=0.9)
        self.wait(1.4)

        ld = LineaRetardos(CAMINO, ancho=6.6, alto=1.40, color=C_MUESTRA)
        ld.move_to(DOWN * 0.25)
        et_ld = tag_junto(ld, "camino desconocido", direccion=DOWN,
                          buff=0.20, color=C_DATO)
        self.play(Create(ld), FadeIn(et_ld), run_time=1.3)

        coefs = VGroup()
        for i, c in enumerate(CAMINO):
            t = tag_hud(fmt(c, 2), font_size=17, color=C_MUESTRA)
            # a la derecha de la toma: centrado la cruzaria la vertical
            t.next_to(ld.coef(i), DOWN, buff=0.10).shift(RIGHT * 0.44)
            coefs.add(t)
        self.play(LaggedStart(*[FadeIn(t) for t in coefs], lag_ratio=0.22),
                  run_time=1.5)
        rot.mostrar(cifra_pie(f"{N_TAPS_LMS} coeficientes desconocidos"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- 3. el mismo ruido, otra forma -------------------------------
        ruido = ref.con_valores(RUIDO_ENTRA[:n], color=C_RUIDO)
        ruido.move_to(DOWN * 2.30 + RIGHT * 0.55)
        et_ruido = tag_hud("ruido que entra", font_size=19, color=C_RUIDO)
        et_ruido.next_to(ruido, LEFT, buff=0.24)

        # la señal entra por la IZQUIERDA de la linea y sale por la
        # DERECHA del sumador: las flechas van por ahi y no cruzan nada.
        x_in = ld.linea.get_left()[0]
        x_out = ld.suma.get_right()[0]
        f1 = Arrow(np.array([x_in, ref.get_bottom()[1], 0.0]),
                   np.array([x_in, ld.get_top()[1], 0.0]), buff=0.14,
                   color=C_DATO, stroke_width=2.4,
                   max_tip_length_to_length_ratio=0.16)
        f2 = Arrow(np.array([x_out, ld.suma.get_center()[1], 0.0]),
                   np.array([x_out, ruido.get_top()[1], 0.0]), buff=0.14,
                   color=C_DATO, stroke_width=2.4,
                   max_tip_length_to_length_ratio=0.16)
        self.play(Create(f1), Create(f2), run_time=0.7)

        viaje = ref.copy()
        self.play(flujo([f1, f2], color=C_CALCULO), run_time=1.2)
        self.play(Transform(viaje, ruido), FadeIn(et_ruido), run_time=1.5)
        self.wait(2.2)

        # restar la referencia a secas deja casi todo el ruido dentro
        resta = mejora_db(RUIDO_ENTRA, (D_LMS - REF) - LIMPIA)
        rot.mostrar(cifra_pie(f"restar solo {fmt(resta, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        panel = panel_cifras((f"camino {N_TAPS_LMS} taps", C_MUESTRA),
                             (f"restar {fmt(resta, 1)} dB", C_RUIDO),
                             desplazar=DOWN * 2.55)
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
