class Clip3(Scene):
    """8.3.3 - Partir la señal en dos bandas y volver a juntarla. Los dos
    filtros de Haar separan fatal (dos taps) y aun asi el banco reconstruye
    EXACTO: 4.4e-16. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("Dos canales"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- los dos filtros del banco: se cruzan y separan fatal ---------
        resp = RespuestaFrec(W_H, MAG_H0, ancho=7.6, alto=3.0, piso_db=-40.0,
                             techo_db=6.0, color=C_SALIDA)
        resp.move_to(DOWN * 0.30)
        cur_h1 = resp.con_mag(MAG_H1, color=C_BANDA).curva
        cero_db = DashedLine(resp.en(W_H[0], 0.0), resp.en(W_H[-1], 0.0),
                             color=C_REJILLA, stroke_width=1.0,
                             dash_length=0.06)
        et_0 = tag_hud("0 dB", font_size=17, color=C_TENUE)
        et_0.next_to(resp.en(W_H[0], 0.0), LEFT, buff=0.16)
        et_w0 = tag_hud("0", font_size=17, color=C_TENUE)
        et_w0.next_to(resp.en(W_H[0], -40.0), DOWN, buff=0.18)
        et_w1 = tag_hud("pi", font_size=17, color=C_TENUE)
        et_w1.next_to(resp.en(W_H[-1], -40.0), DOWN, buff=0.18)
        et_h0 = tag_hud("paso bajo", font_size=19, color=C_SALIDA)
        et_h0.next_to(resp.en(0.10 * np.pi, 3.0), UP, buff=0.20)
        et_h1 = tag_hud("paso alto", font_size=19, color=C_BANDA)
        et_h1.next_to(resp.en(0.90 * np.pi, 3.0), UP, buff=0.20)

        self.play(FadeIn(resp.ejes), FadeIn(cero_db), FadeIn(et_0),
                  FadeIn(et_w0), FadeIn(et_w1), run_time=0.8)
        self.play(Create(resp.curva), FadeIn(et_h0), run_time=1.0)
        self.play(Create(cur_h1), FadeIn(et_h1), run_time=1.0)
        self.add(resp)
        rot.mostrar(cifra_pie(f"{TAPS_HAAR} taps"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        # --- lo que separan de verdad, medido donde la malla no manda -----
        w_ref = 0.75 * np.pi
        db_ref = float(np.interp(w_ref, W_H, MAG_H0))
        marca = resp.marca_w(w_ref)
        punto = Dot(resp.en(w_ref, db_ref), radius=0.07, color=C_CALCULO)
        self.play(Create(marca), FadeIn(punto), run_time=0.7)
        rot.mostrar(cifra_pie(f"0.75 pi: {fmt(db_ref, 1)} dB"), zona="abajo",
                    run_time=0.45)
        self.wait(3.0)

        self.play(FadeOut(resp), FadeOut(cur_h1), FadeOut(cero_db),
                  FadeOut(et_0), FadeOut(et_w0), FadeOut(et_w1),
                  FadeOut(et_h0), FadeOut(et_h1), FadeOut(marca),
                  FadeOut(punto), run_time=0.7)

        # --- partir, diezmar, sumar: la senal entera --------------------
        # los dos canales son el ANALISIS del banco tal como lo hace
        # error_reconstruccion: filtrar con h0/h1 y quedarse con una de
        # cada dos muestras.
        h0, h1, g0, g1 = BANCO_HAAR
        v0 = diezmar(convolucion(X_B, h0), 2)
        v1 = diezmar(convolucion(X_B, h1), 2)
        rango = (-1.75, 1.75)

        sec_x = Secuencia(X_B[:64], 0, rango, ancho=7.0, alto=1.15,
                          color=C_MUESTRA, radio=0.030)
        sec_x.move_to(UP * 2.15)
        sec_v0 = Secuencia(v0[:32], 0, rango, ancho=3.5, alto=1.05,
                           color=C_SENAL, radio=0.034, eje_y=False)
        sec_v0.move_to(LEFT * 2.95 + UP * 0.15)
        sec_v1 = Secuencia(v1[:32], 0, rango, ancho=3.5, alto=1.05,
                           color=C_BANDA, radio=0.034, eje_y=False)
        sec_v1.move_to(RIGHT * 2.95 + UP * 0.15)
        sec_y = Secuencia(Y_HAAR[1:65], 0, rango, ancho=7.0, alto=1.15,
                          color=C_SALIDA, radio=0.030)
        sec_y.move_to(DOWN * 2.05)

        et_in = tag_hud("x[n]", font_size=19, color=C_MUESTRA)
        et_in.next_to(sec_x, LEFT, buff=0.30)
        et_out = tag_hud("y[n]", font_size=19, color=C_SALIDA)
        et_out.next_to(sec_y, LEFT, buff=0.30)
        et_v0 = tag_hud("bajo /2", font_size=19, color=C_SENAL)
        et_v0.next_to(sec_v0, UP, buff=0.16)
        et_v1 = tag_hud("alto /2", font_size=19, color=C_BANDA)
        et_v1.next_to(sec_v1, UP, buff=0.16)

        def _fl(desde, hasta, color):
            return Arrow(desde, hasta, buff=0.16, color=color,
                         stroke_width=2.4,
                         max_tip_length_to_length_ratio=0.16)

        a1 = _fl(sec_x.get_corner(DL), sec_v0.get_corner(UL), C_SENAL)
        a2 = _fl(sec_x.get_corner(DR), sec_v1.get_corner(UR), C_BANDA)
        a3 = _fl(sec_v0.get_corner(DL), sec_y.get_corner(UL), C_SENAL)
        a4 = _fl(sec_v1.get_corner(DR), sec_y.get_corner(UR), C_BANDA)
        mas = tag_hud("+", font_size=30, color=C_SALIDA)
        mas.move_to(DOWN * 1.05)

        self.play(FadeIn(sec_x), FadeIn(et_in), run_time=0.8)
        self.wait(1.0)
        self.play(Create(a1), Create(a2), run_time=0.7)
        self.play(FadeIn(sec_v0), FadeIn(et_v0), FadeIn(sec_v1),
                  FadeIn(et_v1), run_time=0.9)
        rot.mostrar(cifra_pie("dos bandas   /2"), zona="abajo",
                    run_time=0.45)
        self.wait(2.4)

        self.play(LaggedStart(AnimationGroup(Create(a3), Create(a4),
                                             FadeIn(mas)),
                              AnimationGroup(FadeIn(sec_y), FadeIn(et_out)),
                              lag_ratio=0.55), run_time=1.7)
        self.wait(1.6)
        self.play(flujo([a1, a3, a2, a4], color=C_SALIDA), run_time=2.2)
        rot.mostrar(cifra_pie(f"error = {ERR_HAAR:.1e}"), zona="abajo",
                    run_time=0.45)
        self.wait(3.2)
        self.play(Indicate(sec_y, scale_factor=1.03, color=C_CALCULO),
                  Indicate(sec_x, scale_factor=1.03, color=C_CALCULO),
                  run_time=1.0)
        self.wait(4.6)
