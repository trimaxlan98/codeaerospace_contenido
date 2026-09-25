class Clip3(Scene):
    """8.3.3 - El pase de Meteor (137.9 MHz, 830 km, elevacion maxima 60
    grados: parametros en gris): la curva S del Doppler en kHz contra los
    minutos; antes y despues del pase el satelite esta bajo el horizonte y
    no hay curva. La ventana de recepcion (verde) es el pase entero; cian
    el Doppler maximo (+-, de DOP) y la duracion de la ventana. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El pase"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        t_min = T_P / 60.0
        dop_khz = DOP / 1000.0
        dop_max = float(np.abs(DOP).max()) / 1000.0
        import inspect
        elev_max = inspect.signature(S.doppler_pase).parameters[
            "elev_max"].default
        dur_min = float(T_P[-1] - T_P[0]) / 60.0
        # eje de tiempo mas ancho que el pase: antes y despues, bajo el
        # horizonte
        borde = math.ceil(t_min[-1] * 1.45)
        t_eje = np.linspace(-borde, borde, 3)
        lim = math.ceil(dop_max * 1.35)
        esp = S.Espectro(t_eje, np.zeros_like(t_eje), piso=-lim, techo=lim,
                         ancho=11.0, alto=4.6, color=C_CALCULO, area=False)
        esp.curva.set_stroke(opacity=0)
        esp.shift(DOWN * 0.1 + RIGHT * 0.35 - esp._origen())

        curva = VMobject(stroke_color=C_SENAL, stroke_width=4)
        curva.set_points_as_corners([esp.en(a, b)
                                     for a, b in zip(t_min, dop_khz)])
        cero = Line(esp.en(-borde, 0.0), esp.en(borde, 0.0), color=C_EJE,
                    stroke_width=1.5)
        x_izq = esp.en(-borde, 0.0)[0]
        ticks_y = VGroup()
        for v in (-lim, 0, lim):
            p = np.array([x_izq, esp.en(0.0, v)[1], 0.0])
            ticks_y.add(Line(p, p + LEFT * 0.1, color=C_EJE, stroke_width=1.8))
            t = Text(f"{v:+d}" if v else "0", font=FUENTE_HUD, font_size=18,
                     color=C_TENUE)
            t.next_to(p + LEFT * 0.1, LEFT, buff=0.1)
            ticks_y.add(t)
        eje_y = Line(esp.en(-borde, -lim), esp.en(-borde, lim), color=C_EJE,
                     stroke_width=1.8)
        u_y = Text("kHz", font=FUENTE_HUD, font_size=18, color=C_TENUE)
        u_y.next_to(eje_y, UP, buff=0.14)
        marcas = esp.marcas([-borde, 0, borde],
                            [f"{-borde}", "0", f"+{borde}"], font_size=18)
        u_x = Text("min", font=FUENTE_HUD, font_size=18, color=C_TENUE)
        u_x.next_to(esp.en(borde, -lim), RIGHT, buff=0.2)

        panel = panel_cifras((f"{mhz(P['f_hz'])} MHz", C_DATO),
                             (f"{fmt(P['h_km'], 0)} km", C_DATO),
                             (f"{fmt(elev_max, 0)} grados max", C_DATO),
                             desplazar=DOWN * 0.25)

        self.play(Create(esp.ejes), Create(eje_y), Create(cero),
                  FadeIn(ticks_y), FadeIn(u_y), FadeIn(marcas), FadeIn(u_x),
                  run_time=1.0)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(1.4)

        # --- el satelite recorre el pase ------------------------------------
        idx = ValueTracker(0)
        n = len(t_min)

        def _k():
            return min(int(round(idx.get_value())), n - 1)

        parcial = always_redraw(lambda: VMobject(
            stroke_color=C_SENAL, stroke_width=4).set_points_as_corners(
            [esp.en(t_min[j], dop_khz[j]) for j in range(max(_k(), 1) + 1)]))
        viajero = always_redraw(lambda: Dot(
            esp.en(t_min[_k()], dop_khz[_k()]), radius=0.09,
            color=C_SENAL))
        self.add(parcial, viajero)
        self.play(idx.animate.set_value(n - 1), run_time=8.0,
                  rate_func=linear)
        self.remove(parcial)
        self.add(curva)
        self.play(FadeOut(viajero), run_time=0.4)
        self.wait(1.0)

        # --- los extremos (cian, de DOP) --------------------------------------
        p_ini = Dot(esp.en(t_min[0], dop_khz[0]), radius=0.08,
                    color=C_CALCULO)
        p_fin = Dot(esp.en(t_min[-1], dop_khz[-1]), radius=0.08,
                    color=C_CALCULO)
        e_ini = tag_hud(f"+{fmt(dop_max, 2)} kHz", font_size=24)
        e_ini.next_to(p_ini, UR, buff=0.12)
        e_fin = tag_hud(f"-{fmt(dop_max, 2)} kHz", font_size=24)
        e_fin.next_to(p_fin, UL, buff=0.12)
        self.play(FadeIn(p_ini, scale=1.6), FadeIn(p_fin, scale=1.6),
                  FadeIn(e_ini), FadeIn(e_fin), run_time=0.8)
        rot.mostrar(cifra_pie(f"Doppler +-{fmt(dop_max, 2)} kHz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- la ventana de recepcion: todo el pase sobre el horizonte ------
        ventana = esp.banda(t_min[0], t_min[-1], color=C_OK, opacidad=0.12)
        t_ven = tag_junto(ventana, "sobre el horizonte", UP, buff=0.14,
                          font_size=22, color=C_OK)
        t_ven.move_to(esp.en(0.0, lim) + DOWN * 0.3)
        def bajo(t_centro):
            g = VGroup(tag_junto(esp.ejes, "bajo el", UP, font_size=22),
                       tag_junto(esp.ejes, "horizonte", UP, font_size=22)
                       ).arrange(DOWN, buff=0.1)
            return g.move_to(esp.en(t_centro, 1.0))

        zona = (borde + t_min[-1]) / 2
        bajo_i = bajo(-zona)
        bajo_d = bajo(zona)
        self.play(FadeIn(ventana), FadeIn(t_ven), run_time=0.9)
        self.play(FadeIn(bajo_i), FadeIn(bajo_d), run_time=0.6)
        self.wait(1.6)
        llave = BraceBetweenPoints(esp.en(t_min[0], -lim),
                                   esp.en(t_min[-1], -lim), UP, color=C_OK)
        llave.shift(UP * 0.02)
        t_dur = tag_hud(f"{fmt(dur_min, 1)} min", font_size=26)
        t_dur.next_to(llave, UP, buff=0.12)
        self.play(GrowFromCenter(llave), FadeIn(t_dur), run_time=0.8)
        rot.mostrar(cifra_pie(f"ventana de {fmt(dur_min, 1)} min"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        self.play(Indicate(curva, color=C_SENAL, scale_factor=1.0),
                  run_time=1.2)
        self.wait(8.0)
