class Clip1(Scene):
    """4.2.1 - La respuesta en frecuencia ES el recorrido del circulo
    unidad: w avanza, el punto gira y |H| se dibuja al lado. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("El punto que recorre"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el plano con los dos polos del resonador ---------------------
        pz = plano_z(CEROS_D, POLOS_D, unidad=1.95, alcance=1.28)
        pz.move_to(LEFT * 3.95 + UP * 0.15)
        et_pz = tag_hud("plano z", font_size=19, color=C_TENUE)
        et_pz.next_to(pz, DOWN, buff=0.24)
        self.play(FadeIn(pz.ejes), FadeIn(et_pz), run_time=0.5)
        self.play(Create(pz.circulo), run_time=1.3)
        self.play(LaggedStart(*[FadeIn(m, scale=0.5) for m in pz.polos],
                              lag_ratio=0.25), run_time=0.7)
        self.wait(1.0)

        # --- la respuesta, todavia sin curva -------------------------------
        piso = float(MAG[R_DEMO].min()) - 4.0
        techo = PICO[R_DEMO] + 4.0
        rf = respuesta_dibujo(W_EJE[R_DEMO], MAG[R_DEMO], ancho=5.0,
                              alto=2.6, piso_db=piso, techo_db=techo)
        rf.move_to(RIGHT * 4.0 + UP * 0.15)
        rf.remove(rf.curva)          # la curva se dibuja a mano, por tramos
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, DOWN, buff=0.26)

        # La curva partida en el pico: el punto se detiene ahi a enseñar la
        # cifra y luego sigue hasta pi.
        w_eje, mag = W_EJE[R_DEMO], MAG[R_DEMO]
        idx = int(np.argmin(np.abs(w_eje - W0)))
        pts = [rf.en(a, b) for a, b in zip(w_eje, mag)]
        seg1 = VMobject(color=C_SALIDA, stroke_width=2.8)
        seg1.set_points_as_corners(pts[:idx + 1])
        seg2 = VMobject(color=C_SALIDA, stroke_width=2.8)
        seg2.set_points_as_corners(pts[idx:])

        self.play(FadeIn(rf.ejes), FadeIn(et_rf), run_time=0.5)
        self.wait(0.6)

        # --- el punto que recorre, y su gemelo en la respuesta -------------
        wt = ValueTracker(0.0)
        radio = always_redraw(
            lambda: Line(pz.en(0), pz.punto_en(wt.get_value()),
                         color=C_CALCULO, stroke_width=1.8,
                         stroke_opacity=0.6))
        arco = always_redraw(
            lambda: pz.arco(0.0, max(wt.get_value(), 0.004), grosor=3.4))
        d_pz = Dot(pz.punto_en(0.0), radius=0.06, color=C_CALCULO)
        d_pz.add_updater(lambda m: m.move_to(pz.punto_en(wt.get_value())))
        d_rf = Dot(rf.en(0.0, rf.valor(0.0)), radius=0.065, color=C_CALCULO)
        d_rf.add_updater(
            lambda m: m.move_to(rf.en(wt.get_value(),
                                      rf.valor(wt.get_value()))))
        self.add(arco, radio)
        self.play(FadeIn(d_pz), FadeIn(d_rf), run_time=0.4)
        self.wait(0.6)

        # --- del origen al pico --------------------------------------------
        self.play(wt.animate.set_value(W0), Create(seg1),
                  run_time=4.0, rate_func=linear)
        self.wait(0.5)
        marca = rf.marca_w(W0)
        self.play(FadeIn(marca), run_time=0.4)
        rot.mostrar(cifra_pie(f"pico = {fmt(PICO[R_DEMO], 1)} dB en pi/4"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- y del pico hasta pi -------------------------------------------
        self.play(wt.animate.set_value(np.pi), Create(seg2),
                  run_time=7.0, rate_func=linear)
        self.wait(0.6)
        rot.mostrar(cifra_pie(f"w = pi: {fmt(rf.valor(np.pi), 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        rot.mostrar(formula_pie(
            r"H(e^{j\omega}) = \left. H(z) \right|_{z = e^{j\omega}}"),
            zona="abajo", run_time=0.5)
        self.wait(4.0)
