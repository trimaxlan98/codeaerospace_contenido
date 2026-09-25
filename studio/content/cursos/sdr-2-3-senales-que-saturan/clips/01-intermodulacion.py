class Clip1(Scene):
    """2.3.1 - Dos tonos fuertes entran a un amplificador no lineal y nacen
    productos de intermodulacion de tercer orden justo al lado de los tonos
    que entraron: 2f1-f2 y 2f2-f1. Ventana rectangular: los cuatro tonos
    caen exactos en bin, sin fuga espectral, y se dibujan como rayas
    limpias (no como una joroba). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Intermodulacion"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        rot.mostrar(formula_pie(r"y = 10x - x^3", color=C_DATO),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)

        f_lo, f_hi = 96e6, 100.5e6

        def espectro_rect(a):
            t = np.arange(S.N_IM) / S.FS_IM
            y = S.amplificador(a * (np.cos(2 * np.pi * F1 * t) +
                                    np.cos(2 * np.pi * F2 * t)))
            f, d = S.espectro_db(y, S.FS_IM, nfft=S.N_IM,
                                 ventana_nombre="rect", ref="abs")
            m = (f >= f_lo) & (f <= f_hi)
            return f[m], d[m]

        fc, dc_baja = espectro_rect(0.02)
        _, dc_alta = espectro_rect(0.2)

        piso, techo = -140.0, 10.0
        esp = S.Espectro(fc, dc_baja, piso=piso, techo=techo, ancho=11.6,
                         alto=4.2, color=C_SENAL)
        esp.move_to(UP * 0.25)
        self.play(Create(esp.ejes), run_time=0.6)

        def nivel(fc_arr, dc_arr, f):
            return float(dc_arr[np.argmin(np.abs(fc_arr - f))])

        def raya(f, dc_arr, color):
            return Line(esp.en(f, piso), esp.en(f, nivel(fc, dc_arr, f)),
                       color=color, stroke_width=7)

        r1 = raya(F1, dc_baja, C_SENAL)
        r2 = raya(F2, dc_baja, C_SENAL)
        rb = raya(F_IM_BAJO, dc_baja, C_RUIDO)
        ra = raya(F_IM_ALTO, dc_baja, C_RUIDO)
        self.play(Create(r1), Create(r2), Create(rb), Create(ra),
                  run_time=1.4)
        self.wait(1.0)

        t1 = tag_dato(f"{mhz(F1)} MHz", font_size=18)
        t2 = tag_dato(f"{mhz(F2)} MHz", font_size=18)
        t1.next_to(esp.en(F1, piso), DOWN, buff=0.3).shift(LEFT * 0.4)
        t2.next_to(esp.en(F2, piso), DOWN, buff=0.3).shift(RIGHT * 0.4)
        tb = tag_hud(f"{mhz(F_IM_BAJO)} MHz", font_size=19, color=C_CALCULO)
        ta = tag_hud(f"{mhz(F_IM_ALTO)} MHz", font_size=19, color=C_CALCULO)
        tb.next_to(esp.en(F_IM_BAJO, piso), DOWN, buff=0.85)
        ta.next_to(esp.en(F_IM_ALTO, piso), DOWN, buff=0.85)
        self.play(FadeIn(t1), FadeIn(t2), FadeIn(tb), FadeIn(ta),
                  run_time=0.8)
        self.wait(2.6)

        # --- sube la entrada: los productos de intermodulacion crecen ----
        r1b = raya(F1, dc_alta, C_SENAL)
        r2b = raya(F2, dc_alta, C_SENAL)
        rbb = raya(F_IM_BAJO, dc_alta, C_RUIDO)
        rab = raya(F_IM_ALTO, dc_alta, C_RUIDO)
        self.play(Transform(r1, r1b), Transform(r2, r2b),
                  Transform(rb, rbb), Transform(ra, rab), run_time=2.0)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"2f_1 - f_2"), zona="abajo", run_time=0.5)
        self.wait(4.2)
        rot.mostrar(cifra_pie("97.7 y 98.9 MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(8.0)
