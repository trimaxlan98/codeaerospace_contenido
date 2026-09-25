class Clip2(Scene):
    """1.1.2 - La banda de FM entera y la ventana de fs = 2.4 MHz que el LO
    desliza por ella; con I y Q la ventana mide fs, no fs/2. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Una ventana que se mueve"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        f, db = S.espectro_banda_fm()
        esp = S.Espectro(f, db, piso=-82.0, techo=2.0, ancho=12.4, alto=3.7,
                         color=C_SENAL)
        esp.move_to(DOWN * 0.15)
        ticks = esp.marcas([88e6, 92e6, 96e6, 100e6, 104e6, 108e6],
                           ["88", "92", "96", "100", "104", "108"])
        u = tag_junto(ticks[-1], "MHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        self.wait(1.4)
        rot.mostrar(dato_pie("banda FM: 88-108 MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- la ventana del SDR ------------------------------------------
        centro = ValueTracker(CENTRO_A)
        ven = always_redraw(lambda: esp.banda(centro.get_value() - FS / 2,
                                              centro.get_value() + FS / 2,
                                              color=C_LO, opacidad=0.13))
        lo = always_redraw(lambda: esp.marca_f(centro.get_value(),
                                               color=C_LO))
        self.play(FadeIn(ven), Create(lo), run_time=0.8)
        rot.mostrar(cifra_pie(f"ancho = fs = {FS / 1e6:.1f} MHz"),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)
        cuenta = tag_hud(f"{N_A} emisoras", font_size=22)
        cuenta.add_updater(lambda m: m.next_to(ven, UP, buff=0.12))
        self.play(FadeIn(cuenta), run_time=0.4)
        self.wait(2.0)

        # --- el LO se mueve: la ventana se desliza -----------------------
        self.play(FadeOut(cuenta), run_time=0.3)
        cuenta.clear_updaters()
        self.play(centro.animate.set_value(104.2e6), run_time=2.6,
                  rate_func=smooth)
        self.wait(0.4)
        self.play(centro.animate.set_value(CENTRO_B), run_time=2.4,
                  rate_func=smooth)
        dentro = VGroup(*[esp.marca_f(fc, color=C_SENAL, ancho=2.4)
                          for fc in F_B])
        self.play(LaggedStart(*[Create(m) for m in dentro], lag_ratio=0.2),
                  run_time=1.0)
        cuenta = tag_hud(f"{N_B} emisoras", font_size=22)
        cuenta.next_to(ven, UP, buff=0.12)
        self.play(FadeIn(cuenta), run_time=0.4)
        rot.mostrar(cifra_pie(f"{N_B} emisoras a la vez"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- los bordes de la ventana: LO +- fs/2 ------------------------
        c = centro.get_value()
        b0 = tag_hud(mhz(c - FS / 2), font_size=20, color=C_LO)
        b1 = tag_hud(mhz(c + FS / 2), font_size=20, color=C_LO)
        b0.next_to(esp.en(c - FS / 2, -82.0), DOWN, buff=0.55)
        b1.next_to(esp.en(c + FS / 2, -82.0), DOWN, buff=0.55)
        b0.shift(LEFT * 0.35)
        b1.shift(RIGHT * 0.35)
        self.play(FadeIn(b0), FadeIn(b1), run_time=0.6)
        rot.mostrar(formula_pie(r"f_{LO} \pm \tfrac{f_s}{2}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)
        rot.mostrar(cifra_pie(f"de {mhz(c - FS / 2)} a {mhz(c + FS / 2)} MHz"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)
