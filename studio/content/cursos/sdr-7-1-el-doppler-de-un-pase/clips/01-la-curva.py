class Clip1(Scene):
    """7.1.1 - La curva S del Doppler de un pase LEO a 437 MHz (550 km,
    60 grados de elevacion maxima, parametros): entra corrida +10.11 kHz
    y sale corrida -10.11 kHz, con la pendiente maxima en el cenit.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La curva del Doppler"), zona="arriba",
                   run_time=0.6)
        self.wait(0.5)

        # --- la curva en cuadro propio: minutos en x, kHz en y ------------
        t_min = T_P / 60.0
        dop_khz = DOP / 1000.0
        limite = DOP_MAX / 1000.0 * 1.2
        esp = S.Espectro(t_min, dop_khz, piso=-limite, techo=limite,
                         ancho=11.2, alto=4.6, color=C_CALCULO, area=False)
        esp.move_to(DOWN * 0.2)
        cero = Line(esp.en(t_min[0], 0.0), esp.en(t_min[-1], 0.0),
                   color=C_EJE, stroke_width=1.5)
        u_x = tag_junto(esp.ejes, "min", DOWN, buff=0.2, font_size=20)
        panel = panel_cifras(("437 MHz", C_DATO), ("550 km", C_DATO),
                             ("60 grados", C_DATO))

        self.play(Create(esp.ejes), Create(cero), FadeIn(u_x), FadeIn(panel),
                  run_time=1.0)
        self.wait(0.4)
        self.play(Create(esp.curva), run_time=3.4)
        self.wait(1.6)

        # --- los extremos medidos ------------------------------------------
        p_ini = Dot(esp.en(t_min[0], dop_khz[0]), radius=0.075,
                   color=C_CALCULO)
        et_ini = tag_hud(f"+{fmt(DOP_MAX / 1000, 2)} kHz", font_size=20)
        et_ini.next_to(p_ini, UR, buff=0.16)
        p_fin = Dot(esp.en(t_min[-1], dop_khz[-1]), radius=0.075,
                   color=C_CALCULO)
        et_fin = tag_hud(f"-{fmt(DOP_MAX / 1000, 2)} kHz", font_size=20)
        et_fin.next_to(p_fin, UP, buff=0.18)
        self.play(FadeIn(p_ini, scale=1.6), FadeIn(et_ini),
                  FadeIn(p_fin, scale=1.6), FadeIn(et_fin), run_time=0.8)
        self.wait(2.2)

        # --- el pase recorrido en tiempo real (dramatiza el eje x) --------
        idx = ValueTracker(0)
        n = len(t_min)

        def _k():
            return min(int(round(idx.get_value())), n - 1)

        viajero = always_redraw(lambda: Dot(
            esp.en(t_min[_k()], dop_khz[_k()]), radius=0.09,
            color=C_SENAL))
        self.add(viajero)
        self.play(idx.animate.set_value(n - 1), run_time=7.5,
                  rate_func=linear)
        self.wait(0.3)

        i0 = n // 2
        cruce = Dot(esp.en(t_min[i0], dop_khz[i0]), radius=0.085,
                   color=C_CALCULO)
        cenit = tag_hud("cenit", font_size=19)
        cenit.next_to(cruce, UR, buff=0.3)
        self.play(FadeOut(viajero), FadeIn(cruce, scale=1.6), FadeIn(cenit),
                  run_time=0.6)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"+-{fmt(DOP_MAX / 1000, 2)} kHz"),
                   zona="abajo", run_time=0.5)
        self.wait(8.0)
