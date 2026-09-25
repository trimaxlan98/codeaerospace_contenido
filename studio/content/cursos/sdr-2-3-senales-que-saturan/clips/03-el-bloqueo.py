class Clip3(Scene):
    """2.3.3 - Una emisora de FM fuerte comprime el mismo amplificador que
    intenta oir un satelite debil, 39 MHz mas arriba: en cuanto la emisora
    se enciende, la ganancia que ve el satelite se hunde. Formato mudo: las
    dos barras y su rotulo de mobiliario cuentan la historia, sin pie
    narrado. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El bloqueo"), zona="arriba", run_time=0.6)
        self.wait(1.0)

        f_lo, f_hi = 90e6, 145e6
        ancho_eje = 10.6
        y_eje = DOWN * 2.15

        def x_de(f):
            return (f - f_lo) / (f_hi - f_lo) * ancho_eje - ancho_eje / 2

        eje = Line(y_eje + LEFT * ancho_eje / 2, y_eje + RIGHT * ancho_eje / 2,
                  color=C_TENUE, stroke_width=1.8)
        self.play(Create(eje), run_time=0.7)

        x1, x2 = x_de(F1), x_de(F_SAT)
        t1 = tag_dato(f"{mhz(F1)} MHz", font_size=18)
        t2 = tag_dato(f"{mhz(F_SAT)} MHz", font_size=18)
        t1.next_to(y_eje + RIGHT * x1, DOWN, buff=0.2)
        t2.next_to(y_eje + RIGHT * x2, DOWN, buff=0.2)
        self.play(FadeIn(t1), FadeIn(t2), run_time=0.5)
        self.wait(1.6)

        # --- el amplificador, como contexto arriba a la izquierda --------
        amp = S.bloque("AMPLIFICADOR", ancho=2.6, alto=0.6, color=C_TENUE,
                       tamano=18)
        amp.move_to(LEFT * 4.6 + UP * 2.4)
        self.play(FadeIn(amp), run_time=0.6)
        self.wait(1.2)

        db_min, db_max, alto_max = 0.0, 25.0, 2.9

        def h(db):
            return alto_max * float(np.clip(db, db_min, db_max) - db_min) \
                / (db_max - db_min)

        def raya(x, altura, color):
            r = Rectangle(width=0.5, height=max(altura, 0.02),
                          stroke_width=0, fill_color=color, fill_opacity=0.9)
            r.move_to(y_eje + RIGHT * x + UP * altura / 2)
            return r

        # --- rotulos de mobiliario a un lado de cada barra: fijos, no
        # se mueven aunque la barra cambie de altura -----------------------
        p_sat = y_eje + RIGHT * (x2 - 0.25) + UP * 1.8
        p_fm = y_eje + RIGHT * (x1 + 0.25) + UP * 1.8
        et_sat = tag_junto(p_sat, "satelite", LEFT, buff=0.35, color=C_OK)
        et_fm = tag_junto(p_fm, "emisora FM", RIGHT, buff=0.35, color=C_SENAL)

        raya_sat = raya(x2, h(G_LIN), C_OK)
        self.play(FadeIn(raya_sat, shift=UP * 0.1), FadeIn(et_sat),
                  run_time=0.8)
        self.wait(2.8)

        raya_fm = raya(x1, 3.2, C_SENAL)
        self.play(FadeIn(raya_fm, shift=UP * 0.15), FadeIn(et_fm),
                  run_time=1.0)
        self.wait(2.6)

        raya_sat2 = raya(x2, h(G_LIN + DESENS), C_OK)
        self.play(Transform(raya_sat, raya_sat2), run_time=1.4)
        rot.mostrar(cifra_pie(f"{fmt(DESENS, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(15.0)
