class Clip3(Scene):
    """3.3.3 - La plantilla PN se desliza sobre el ruido y la correlacion
    se dibuja: EXPLOTA en el desplazamiento 40. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Deslizar y correlar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- montaje: el ruido arriba, la correlacion abajo ---------------
        rot.mostrar(pie_curso("Tenemos la llave. Deslicémosla sobre el mar "
                              "de ruido, muestra a muestra."),
                    zona="abajo", run_time=0.5)
        ancho_rx = 10.6
        on = onda(T_RX, RX, rango_y=(-3.3, 3.3), ancho=ancho_rx, alto=2.0)
        on.move_to(UP * 1.65)
        on.curva.set_stroke(opacity=0.7)
        corr_on = onda(T_CORR, CORR, rango_y=(-13.0, 36.0),
                       ancho=ancho_rx * (N_VENTANAS - 1) / (N_TOTAL - 1),
                       alto=2.3, color=C_CIFRA)
        corr_on.move_to(DOWN * 1.35)
        corr_on.shift(RIGHT * float(on.en(0.0, 0.0)[0]
                                    - corr_on.en(0.0, 0.0)[0]))
        et_rx = tag_junto(on, "lo recibido", direccion=UP, buff=0.1)
        et_rx.set_x(float(on.en(4.0, 0.0)[0]) + et_rx.width / 2)
        et_c = tag_junto(corr_on, "correlación con la llave",
                         direccion=UP, buff=0.12)
        et_c.set_x(float(corr_on.en(14.0, 0.0)[0]))
        self.play(FadeIn(on.ejes), FadeIn(on.curva), FadeIn(et_rx),
                  run_time=0.8)
        self.play(FadeIn(corr_on.ejes), FadeIn(et_c), run_time=0.6)

        paso = float(on.en(1.0, 0.0)[0] - on.en(0.0, 0.0)[0])
        plantilla = VMobject(color=C_BIT, stroke_width=2.8)
        plantilla.set_points_as_corners([on.en(t, y)
                                         for t, y in zip(T_PN, Y_PN)])
        marco = Rectangle(width=N_CHIPS * paso, height=on.alto,
                          color=C_BIT, stroke_width=1.6)
        marco.set_fill(C_BIT, opacity=0.05)
        marco.move_to(on.en((N_CHIPS - 1) / 2.0, 0.0))
        llave_g = VGroup(marco, plantilla)
        base_c = llave_g.get_center()
        self.play(FadeIn(llave_g), run_time=0.7)
        self.wait(3.0)

        # --- momento: un numero por posicion ------------------------------
        rot.mostrar(pie_curso("En cada posición multiplicamos chip a chip "
                              "y sumamos: un número por desplazamiento."),
                    zona="abajo", run_time=0.5)
        kv = ValueTracker(0.0)

        def _k():
            return int(np.clip(round(kv.get_value()), 0, N_VENTANAS - 1))

        llave_g.add_updater(
            lambda m: m.move_to(base_c + RIGHT * kv.get_value() * paso))
        traza = always_redraw(
            lambda: corr_on.curva_de(T_CORR[:max(2, _k() + 1)],
                                     CORR[:max(2, _k() + 1)],
                                     color=C_CIFRA, grosor=2.6))
        punta = always_redraw(
            lambda: Dot(corr_on.en(float(_k()), CORR[_k()]), radius=0.055,
                        color=C_CIFRA))
        lectura = always_redraw(
            lambda: VGroup(
                tag_hud(f"k = {_k()}", font_size=22),
                tag_hud(f"R = {fmt(CORR[_k()], 1)}", font_size=22),
            ).arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to(
                RIGHT * 4.15 + DOWN * 0.7, aligned_edge=LEFT))
        self.play(FadeIn(traza), FadeIn(punta), FadeIn(lectura),
                  run_time=0.5)
        self.play(kv.animate.set_value(38.0), run_time=4.4,
                  rate_func=linear)
        self.wait(1.0)

        # --- momento: la explosion ----------------------------------------
        rot.mostrar(pie_curso("Y en una sola posición, la suma explota."),
                    zona="abajo", run_time=0.5)
        self.play(kv.animate.set_value(43.0), run_time=1.8,
                  rate_func=linear)
        self.wait(3.2)

        # --- momento: nada se le acerca -----------------------------------
        rot.mostrar(pie_curso("En las 110 ventanas posibles, ninguna otra "
                              "se le acerca."),
                    zona="abajo", run_time=0.5)
        self.play(kv.animate.set_value(float(N_VENTANAS - 1)), run_time=3.2,
                  rate_func=linear)
        self.wait(1.8)

        # --- momento: ahi empieza el preambulo ----------------------------
        rot.mostrar(pie_curso("El máximo cae en 40: ahí, dentro del ruido, "
                              "empieza el preámbulo."),
                    zona="abajo", run_time=0.5)
        llave_g.clear_updaters()
        traza_fija = corr_on.curva_de(T_CORR, CORR, color=C_CIFRA,
                                      grosor=2.6)
        for m in (traza, punta, lectura):
            m.clear_updaters()
        self.remove(traza, punta, lectura)
        self.add(traza_fija)
        v_rx = on.vertical_en(float(OFFSET_HALLADO), color=C_CIFRA)
        v_c = corr_on.vertical_en(float(OFFSET_HALLADO), color=C_CIFRA)
        pico = Dot(corr_on.en(float(OFFSET_HALLADO), C_PICO), radius=0.07,
                   color=C_CIFRA)
        self.play(llave_g.animate.move_to(
            base_c + RIGHT * OFFSET_HALLADO * paso), run_time=0.9)
        self.play(Create(v_rx), Create(v_c), FadeIn(pico),
                  marco.animate.set_fill(C_BIT, opacity=0.14),
                  run_time=0.9)
        cifras = VGroup(
            tag_hud(f"offset = {OFFSET_HALLADO}", font_size=22),
            tag_hud(f"pico = {fmt(C_PICO, 1)}", font_size=21),
            tag_hud(f"2do mayor = {fmt(C_SEGUNDO, 1)}", font_size=20),
            tag_hud(f"en k = {OFFSET_2}", font_size=20),
            tag_hud(f"razon = {fmt(RAZON_PICO, 1)}x", font_size=20),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        cifras.move_to(RIGHT * 3.75 + DOWN * 0.75, aligned_edge=LEFT)
        self.play(FadeIn(cifras, shift=0.12 * UP), run_time=0.7)
        self.wait(4.6)
