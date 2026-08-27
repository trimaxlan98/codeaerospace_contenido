class Clip2(Scene):
    """3.2.2 - El grafo radix-2: tres etapas de cuatro mariposas, y en
    cada mariposa un giro, una suma y una resta. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La mariposa"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el grafo, con las aristas apagadas -------------------------------
        mp = mariposa_dibujo(N_FFT, ancho=6.2, alto=4.0, color=C_MUESTRA)
        mp.move_to(LEFT * 3.3 + DOWN * 0.35)
        mp.aristas.set_stroke(opacity=0.10)
        et_in = tag_hud("x[n]", font_size=18, color=C_MUESTRA)
        et_in.next_to(mp.nodo(0, 0), UP, buff=0.22)
        et_out = tag_hud("X[k]", font_size=18, color=C_CALCULO)
        et_out.next_to(mp.nodo(mp.cols - 1, 0), UP, buff=0.22)
        self.play(FadeIn(mp.aristas), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in mp.nodos],
                              lag_ratio=0.16), run_time=1.4)
        self.add(mp)
        self.play(FadeIn(et_in), FadeIn(et_out), run_time=0.5)
        self.wait(0.8)

        # --- una etapa cada vez ------------------------------------------------
        for k in range(N_ETAPAS):
            rot.mostrar(cifra_pie(f"etapa {k + 1} de {N_ETAPAS}"),
                        zona="abajo", run_time=0.45)
            self.play(mp.etapa(k).animate.set_stroke(opacity=1.0),
                      run_time=0.9)
            self.wait(1.5)

        rot.mostrar(cifra_pie(f"por etapa: {POR_ETAPA} mariposas"),
                    zona="abajo", run_time=0.45)
        self.wait(1.9)

        # --- una mariposa por dentro -------------------------------------------
        cen = RIGHT * 3.4 + DOWN * 0.3
        p_a = cen + LEFT * 1.3 + UP * 0.9
        p_b = cen + LEFT * 1.3 + DOWN * 0.9
        q_a = cen + RIGHT * 1.3 + UP * 0.9
        q_b = cen + RIGHT * 1.3 + DOWN * 0.9
        caja = Square(side_length=0.38, color=C_MUESTRA, stroke_width=2.0,
                      fill_color=CODE_BG, fill_opacity=1.0)
        caja.move_to(p_b + RIGHT * 0.62)
        et_w = tag_hud("W", font_size=17, color=C_MUESTRA)
        et_w.move_to(caja.get_center())
        salida_w = caja.get_right()
        detalle = VGroup(
            Line(p_a, q_a, color=C_EJE, stroke_width=2.0),
            Line(p_b, caja.get_left(), color=C_MUESTRA, stroke_width=2.0),
            Line(salida_w, q_b, color=C_EJE, stroke_width=2.0),
            Line(p_a, q_b, color=C_CALCULO, stroke_width=2.0),
            Line(salida_w, q_a, color=C_CALCULO, stroke_width=2.0))
        pts = VGroup(*[Dot(p, radius=0.055, color=C_MUESTRA)
                       for p in (p_a, p_b)],
                     *[Dot(p, radius=0.055, color=C_CALCULO)
                       for p in (q_a, q_b)])
        e_a = tag_hud("a", font_size=19, color=C_MUESTRA)
        e_a.next_to(p_a, LEFT, buff=0.18)
        e_b = tag_hud("b", font_size=19, color=C_MUESTRA)
        e_b.next_to(p_b, LEFT, buff=0.18)
        e_qa = tag_hud("a + Wb", font_size=19, color=C_CALCULO)
        e_qa.next_to(q_a, RIGHT, buff=0.18)
        e_qb = tag_hud("a - Wb", font_size=19, color=C_CALCULO)
        e_qb.next_to(q_b, RIGHT, buff=0.18)

        self.play(FadeIn(pts), FadeIn(e_a), FadeIn(e_b), run_time=0.7)
        self.play(Create(detalle[1]), FadeIn(caja), FadeIn(et_w),
                  run_time=0.9)
        rot.mostrar(cifra_pie("un giro por mariposa", color=C_MUESTRA),
                    zona="abajo", run_time=0.45)
        self.wait(1.6)
        self.play(Create(detalle[0]), Create(detalle[2]),
                  Create(detalle[3]), Create(detalle[4]), run_time=1.2)
        self.play(FadeIn(e_qa), FadeIn(e_qb), run_time=0.6)
        rot.mostrar(formula_pie(r"a \pm W_N^{k}\,b"), zona="abajo",
                    run_time=0.45)
        self.wait(2.8)

        # --- las cuatro mariposas de la ultima etapa, con su giro --------------
        grupo_det = VGroup(detalle, pts, caja, et_w, e_a, e_b, e_qa, e_qb)
        self.play(FadeOut(grupo_det), run_time=0.7)

        # el giro multiplica la entrada BAJA de cada mariposa: la etiqueta
        # va pegada a ese nodo, no en mitad del cruce (ahi no se sabe de
        # que mariposa es).
        etiquetas_w = VGroup()
        for i, j, tw in ETAPAS[-1]:
            e = tag_hud(f"W{tw}", font_size=16, color=C_CALCULO)
            eb = _con_fondo(e, buff=0.07, opacidad=0.92)
            eb.next_to(mp.nodo(N_ETAPAS - 1, j), UR, buff=0.05)
            etiquetas_w.add(eb)
        self.play(LaggedStart(*[FadeIn(e) for e in etiquetas_w],
                              lag_ratio=0.16), run_time=1.2)
        rot.mostrar(formula_pie(rf"\log_2 {N_FFT} = {N_ETAPAS}"),
                    zona="abajo", run_time=0.45)
        self.wait(2.2)

        panel = panel_cifras((f"etapas = {N_ETAPAS}", C_CALCULO),
                             (f"por etapa = {POR_ETAPA}", C_CALCULO),
                             (f"giros = {ops_fft(N_FFT)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.4)
