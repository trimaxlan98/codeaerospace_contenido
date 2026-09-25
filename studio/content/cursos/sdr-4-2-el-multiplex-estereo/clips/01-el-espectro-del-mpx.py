class Clip1(Scene):
    """4.2.1 - El espectro del MPX: L+R en banda base, el piloto de 19 kHz
    y las cuatro bandas laterales de L-R repartidas alrededor de 38 kHz;
    una banda gris marca donde iria el RDS de 57 kHz (no incluido en esta
    senal). Picos medidos con S.pico. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El espectro del MPX"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        f, db = S.espectro_db(Y_MPX, FS, nfft=8192)
        fr, dbr = S.para_dibujar(f, db, puntos=900, f_lo=0.0)
        m = fr <= 60000.0
        fr, dbr = fr[m], dbr[m]

        esp = S.Espectro(fr, dbr, piso=-85.0, techo=3.0, ancho=12.2,
                         alto=3.8, color=C_SENAL)
        esp.move_to(DOWN * 0.1)
        ticks = esp.marcas([0.0, 10e3, 20e3, 30e3, 40e3, 50e3, 60e3],
                           ["0", "10", "20", "30", "40", "50", "60"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        self.wait(1.0)

        # --- las cuatro regiones, en gris (norma); rotulo ENCIMA de la caja -
        b_suma = esp.banda(0.0, 15e3, color=C_DATO, opacidad=0.12)
        et_suma = tag_dato("L+R")
        et_suma.next_to(b_suma, UP, buff=0.18)
        self.play(FadeIn(b_suma), FadeIn(et_suma), run_time=0.7)
        self.wait(1.8)

        m_piloto = esp.marca_f(19e3, color=C_DATO)
        et_piloto = tag_dato("piloto")
        et_piloto.next_to(m_piloto, UP, buff=0.18)
        self.play(Create(m_piloto), FadeIn(et_piloto), run_time=0.6)
        self.wait(1.8)

        b_dif = esp.banda(23e3, 53e3, color=C_DATO, opacidad=0.12)
        et_dif = tag_dato("L-R")
        et_dif.next_to(b_dif, UP, buff=0.18)
        self.play(FadeIn(b_dif), FadeIn(et_dif), run_time=0.7)
        self.wait(1.8)

        b_rds = esp.banda(55e3, 59e3, color=C_DATO, opacidad=0.1)
        m_rds = esp.marca_f(57e3, color=C_DATO)
        et_rds = tag_dato("RDS")
        et_rds.next_to(b_rds, UP, buff=0.18)
        self.play(FadeIn(b_rds), Create(m_rds), FadeIn(et_rds), run_time=0.7)
        self.wait(2.6)

        # --- los picos medidos, cian -----------------------------------------
        f1, _ = S.pico(f, db, 500.0, 1500.0)
        p1 = esp.marca_f(f1, color=C_CALCULO)
        self.play(Create(p1), run_time=0.5)
        rot.mostrar(cifra_pie(f"{fmt(f1 / 1e3, 1)} kHz"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        f19, _ = S.pico(f, db, 18000.0, 20000.0)
        p19 = esp.marca_f(f19, color=C_CALCULO)
        self.play(Create(p19), run_time=0.5)
        rot.mostrar(cifra_pie(f"{fmt(f19 / 1e3, 1)} kHz"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        f37, _ = S.pico(f, db, 36500.0, 37500.0)
        f39, _ = S.pico(f, db, 38500.0, 39500.0)
        p37 = esp.marca_f(f37, color=C_CALCULO)
        p39 = esp.marca_f(f39, color=C_CALCULO)
        self.play(Create(p37), Create(p39), run_time=0.6)
        rot.mostrar(cifra_pie(f"{fmt(f37 / 1e3, 1)} y {fmt(f39 / 1e3, 1)} kHz"),
                    zona="abajo", run_time=0.5)
        self.wait(6.5)
