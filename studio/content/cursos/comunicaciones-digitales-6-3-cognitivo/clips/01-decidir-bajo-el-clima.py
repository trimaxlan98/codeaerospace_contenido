class Clip1(Scene):
    """6.3.1 - El enlace como problema de decision: estados (el cielo),
    acciones (los modcods) y recompensa (los bits que llegan). Nadie
    entrega la tabla. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Decidir bajo el clima")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        XS = [-4.35, 0.0, 4.35]
        Y_CIELO, Y_MODCOD = 1.52, -0.95

        # --- momento: los estados (el cielo sobre la antena) ---------------
        rot.mostrar(pie_curso("El cielo sobre la antena no se queda quieto: "
                              "claro, nubes, lluvia."),
                    zona="abajo", run_time=0.5)
        cielos = VGroup()
        for s, nombre in enumerate(ESTADOS):
            col = C_ESTADO[s]
            caja = RoundedRectangle(corner_radius=0.12, width=2.95,
                                    height=1.18, color=col,
                                    fill_color=col, fill_opacity=0.14,
                                    stroke_width=2.4)
            caja.move_to([XS[s], Y_CIELO, 0])
            et = Text(nombre, font_size=22, color=col)
            et.move_to(caja.get_center() + UP * 0.24)
            cif = tag_hud(f"SNR = {fmt(SNR_ESTADO[s], 1)} dB", font_size=18)
            cif.move_to(caja.get_center() + DOWN * 0.28)
            cielos.add(VGroup(caja, et, cif))
        et_estados = tag_junto(cielos, "los ESTADOS que ve el agente",
                               direccion=UP, buff=0.20, font_size=18)
        self.play(LaggedStart(*[FadeIn(c, shift=0.18 * DOWN)
                                for c in cielos], lag_ratio=0.28),
                  run_time=1.4)
        self.play(FadeIn(et_estados), run_time=0.4)
        self.wait(3.6)

        # --- momento: las acciones (los modcods) ---------------------------
        rot.mostrar(pie_curso("El transmisor solo puede elegir una cosa: "
                              "con que modcod hablar."),
                    zona="abajo", run_time=0.5)
        chips = VGroup()
        for a, nombre in enumerate(MODCOD_NOMBRES):
            col = MODCOD_COLORES[a]
            caja = RoundedRectangle(corner_radius=0.12, width=2.95,
                                    height=1.40, color=col,
                                    fill_color=col, fill_opacity=0.12,
                                    stroke_width=2.4)
            caja.move_to([XS[a], Y_MODCOD, 0])
            et = Text(nombre, font_size=22, color=col)
            et.move_to(caja.get_center() + UP * 0.38)
            umb = tag_hud(f"umbral {fmt(MODCOD_UMBRALES[a], 1)} dB",
                          font_size=16, color=C_TENUE)
            umb.move_to(caja.get_center() + DOWN * 0.06)
            tas = tag_hud(f"{fmt(MODCOD_TASAS[a], 2)} bits/simb",
                          font_size=18)
            tas.move_to(caja.get_center() + DOWN * 0.44)
            chips.add(VGroup(caja, et, umb, tas))
        et_acciones = tag_junto(chips, "las ACCIONES que puede tomar",
                                direccion=DOWN, buff=0.20, font_size=18)
        self.play(LaggedStart(*[FadeIn(c, shift=0.18 * UP)
                                for c in chips], lag_ratio=0.28),
                  run_time=1.4)
        self.play(FadeIn(et_acciones), run_time=0.4)
        self.wait(3.4)

        # --- momento: la recompensa son los bits que LLEGAN ----------------
        rot.mostrar(pie_curso("La recompensa son los bits que LLEGAN: si el "
                              "modcod no cierra, no llega nada."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_estados), FadeOut(et_acciones), run_time=0.4)

        def enlazar(s, a, color):
            fl = Arrow(cielos[s][0].get_bottom(), chips[a][0].get_top(),
                       buff=0.12, color=color, stroke_width=3.0,
                       max_tip_length_to_length_ratio=0.09)
            return fl

        # lluvia + el modcod mas denso: no cierra, no llega nada
        fl_mal = enlazar(2, 2, C_RUIDO)
        cruz = Cross(stroke_color=C_RUIDO, stroke_width=6.0,
                     scale_factor=0.21)
        cruz.move_to(fl_mal.get_center())
        pago_mal = tag_hud(f"recompensa = {fmt(RECOMPENSA[2][2], 2)} "
                           "bits/simb", font_size=24, color=C_RUIDO)
        pago_mal.move_to([0.0, -2.42, 0])
        self.play(Indicate(cielos[2][0], color=C_ESTADO[2], scale_factor=1.06),
                  run_time=0.6)
        self.play(GrowArrow(fl_mal), run_time=0.7)
        self.play(FadeIn(cruz), FadeIn(pago_mal, shift=0.15 * UP),
                  run_time=0.6)
        self.wait(2.9)

        # el MISMO modcod con cielo claro: paga el maximo
        self.play(FadeOut(fl_mal), FadeOut(cruz), FadeOut(pago_mal),
                  run_time=0.4)
        fl_bien = enlazar(0, 2, C_CIFRA)
        pago_bien = tag_hud(f"recompensa = {fmt(RECOMPENSA[0][2], 2)} "
                            "bits/simb", font_size=24)
        pago_bien.move_to([0.0, -2.42, 0])
        self.play(Indicate(cielos[0][0], color=C_ESTADO[0],
                           scale_factor=1.06), run_time=0.6)
        self.play(GrowArrow(fl_bien), run_time=0.8)
        self.play(FadeIn(pago_bien, shift=0.15 * UP), run_time=0.5)
        self.wait(3.0)

        # --- momento: nadie entrega la tabla -------------------------------
        rot.mostrar(pie_curso("Nadie entrega la tabla. El agente solo ve el "
                              "cielo, elige, y cobra."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cielos), FadeOut(chips), FadeOut(fl_bien),
                  FadeOut(pago_bien), run_time=0.7)

        ANCHO_ET, ANCHO_C, ALTO_C = 2.30, 1.62, 0.70
        X0 = -3.55
        cx = [X0 + ANCHO_ET + ANCHO_C * (j + 0.5) for j in range(3)]
        ry = [0.30 - ALTO_C * i for i in range(3)]
        tabla = VGroup()
        cabeceras = VGroup()
        for a, nombre in enumerate(MODCOD_NOMBRES):
            h = Text(nombre, font_size=19, color=MODCOD_COLORES[a])
            h.move_to([cx[a], ry[0] + ALTO_C * 0.95, 0])
            cabeceras.add(h)
        filas = VGroup()
        for s, nombre in enumerate(ESTADOS):
            et = Text(nombre, font_size=20, color=C_ESTADO[s])
            et.move_to([X0 + ANCHO_ET - 0.18, ry[s], 0], aligned_edge=RIGHT)
            filas.add(et)
            for a in range(3):
                celda = Rectangle(width=ANCHO_C, height=ALTO_C,
                                  color=C_EJE, stroke_width=1.4)
                celda.move_to([cx[a], ry[s], 0])
                q = tag_hud("?", font_size=26, color=C_TENUE)
                q.move_to(celda.get_center())
                tabla.add(VGroup(celda, q))
        et_tabla = Text("cuanto paga cada eleccion", font_size=19,
                        color=C_TENUE)
        et_tabla.move_to([X0 + ANCHO_ET + 1.5 * ANCHO_C, ry[2] - 0.66, 0])
        VGroup(cabeceras, filas, tabla,
               et_tabla).move_to(LEFT * 0.32 + DOWN * 0.15)
        self.play(LaggedStart(*[FadeIn(c) for c in cabeceras],
                              lag_ratio=0.15), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(f) for f in filas], lag_ratio=0.15),
                  run_time=0.7)
        self.play(LaggedStart(*[FadeIn(c, scale=0.85) for c in tabla],
                              lag_ratio=0.06), run_time=1.2)
        self.play(FadeIn(et_tabla), run_time=0.4)
        self.wait(5.0)
