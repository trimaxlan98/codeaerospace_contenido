class Clip3(Scene):
    """6.2.3 - El desplazamiento maximo de un polo: 2.09e-01 en forma
    directa contra 1.78e-04 en cascada. 1173 veces. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("La cifra"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        b16, b12 = BITS

        def marcas_directa(bits):
            """Las cruces rojas de los polos en forma directa."""
            g = pz.con_pz([], POLOS_DIRECTA[bits]).polos
            g.set_color(C_RUIDO)
            for m in g:
                m.scale(0.55)
            return g

        def puntos_cascada(bits, lado=0.062):
            """Una cruz cian EN ASPA VERTICAL por polo de la cascada.

            Va encima del polo exacto: si fuese otra x de 45 grados taparia
            exactamente los brazos ambar y no se veria que coinciden.
            """
            g = VGroup()
            for z in POLOS_CASCADA[bits]:
                d = pz.en(z)
                g.add(VGroup(
                    Line(d + LEFT * lado, d + RIGHT * lado,
                         color=C_CALCULO, stroke_width=2.6),
                    Line(d + DOWN * lado, d + UP * lado,
                         color=C_CALCULO, stroke_width=2.6)))
            return g

        # --- los 10 polos que se querian ----------------------------------
        pz = PlanoZ([], POLOS_EXACTOS, unidad=2.00, alcance=1.30,
                    color_polo=C_MUESTRA)
        pz.shift(LEFT * 3.55 + DOWN * 0.15 - pz.en(0))
        pz.circulo.set_color(C_DATO)
        for m in pz.polos:
            m.scale(0.55)
        self.play(Create(pz.ejes), Create(pz.circulo), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(m) for m in pz.polos],
                              lag_ratio=0.07), run_time=1.3)
        rot.mostrar(cifra_pie(f"{ORDEN} polos exactos"), zona="abajo",
                    run_time=0.5)
        self.wait(1.4)

        # --- a donde los manda cada forma ---------------------------------
        cruces = marcas_directa(b16)
        self.play(LaggedStart(*[FadeIn(m) for m in cruces], lag_ratio=0.06),
                  run_time=1.2)
        rot.mostrar(cifra_pie(f"directa {b16} bits: "
                              f"{ERR_DIRECTA[b16]:.2e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        puntos = puntos_cascada(b16)
        self.play(LaggedStart(*[FadeIn(d) for d in puntos], lag_ratio=0.06),
                  run_time=1.2)
        rot.mostrar(cifra_pie(f"cascada {b16} bits: "
                              f"{ERR_CASCADA[b16]:.2e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- las dos distancias, en decadas -------------------------------
        def altura(err):
            """Decadas por encima de 1e-05 (la barra es logaritmica)."""
            return float(np.log10(err)) + 5.0

        bar = barras([altura(ERR_DIRECTA[b16]), altura(ERR_CASCADA[b16])],
                     ancho=3.4, alto=2.3, color=C_CALCULO, rango_y=(0.0, 5.0))
        bar.move_to(np.array([3.7, -0.75, 0.0]))
        bar.barra(0).set_color(C_RUIDO)
        et_d = tag_hud(f"{ERR_DIRECTA[b16]:.2e}", font_size=19,
                       color=C_RUIDO)
        et_d.next_to(bar.barra(0), UP, buff=0.12)
        et_c = tag_hud(f"{ERR_CASCADA[b16]:.2e}", font_size=19,
                       color=C_CALCULO)
        et_c.next_to(bar.barra(1), UP, buff=0.12)
        nb_d = tag_hud("directa", font_size=19, color=C_RUIDO)
        nb_d.next_to(bar.barra(0), DOWN, buff=0.16)
        nb_c = tag_hud("cascada", font_size=19, color=C_CALCULO)
        nb_c.next_to(bar.barra(1), DOWN, buff=0.16)
        et_log = tag_hud("escala log", font_size=18, color=C_DATO)
        et_log.next_to(bar, DOWN, buff=0.62)
        self.play(FadeIn(bar), FadeIn(nb_d), FadeIn(nb_c), FadeIn(et_log),
                  run_time=0.8)
        self.play(FadeIn(et_d), FadeIn(et_c), run_time=0.5)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"{RAZON[b16]:.0f}x mejor"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- lo mismo con 12 bits -----------------------------------------
        gem = bar.con_valores([altura(ERR_DIRECTA[b12]),
                               altura(ERR_CASCADA[b12])])
        gem.barra(0).set_color(C_RUIDO)
        et_d12 = tag_hud(f"{ERR_DIRECTA[b12]:.2e}", font_size=19,
                         color=C_RUIDO)
        et_c12 = tag_hud(f"{ERR_CASCADA[b12]:.2e}", font_size=19,
                         color=C_CALCULO)
        et_d12.next_to(gem.barra(0), UP, buff=0.12)
        et_c12.next_to(gem.barra(1), UP, buff=0.12)
        self.play(Transform(bar.barras, gem.barras),
                  Transform(cruces, marcas_directa(b12)),
                  Transform(puntos, puntos_cascada(b12)),
                  Transform(et_d, et_d12), Transform(et_c, et_c12),
                  run_time=1.3)
        rot.mostrar(cifra_pie(f"{b12} bits: {RAZON[b12]:.0f}x mejor"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- y de vuelta a los 16 bits de siempre -------------------------
        vuelta = bar.con_valores([altura(ERR_DIRECTA[b16]),
                                  altura(ERR_CASCADA[b16])])
        vuelta.barra(0).set_color(C_RUIDO)
        et_d16 = tag_hud(f"{ERR_DIRECTA[b16]:.2e}", font_size=19,
                         color=C_RUIDO)
        et_c16 = tag_hud(f"{ERR_CASCADA[b16]:.2e}", font_size=19,
                         color=C_CALCULO)
        et_d16.next_to(vuelta.barra(0), UP, buff=0.12)
        et_c16.next_to(vuelta.barra(1), UP, buff=0.12)
        self.play(Transform(bar.barras, vuelta.barras),
                  Transform(cruces, marcas_directa(b16)),
                  Transform(puntos, puntos_cascada(b16)),
                  Transform(et_d, et_d16), Transform(et_c, et_c16),
                  run_time=1.3)

        panel = panel_cifras(
            (f"{b16} bits directa {ERR_DIRECTA[b16]:.2e}", C_RUIDO),
            (f"{b16} bits cascada {ERR_CASCADA[b16]:.2e}", C_CALCULO),
            (f"{b12} bits directa {ERR_DIRECTA[b12]:.2e}", C_RUIDO),
            (f"{b12} bits cascada {ERR_CASCADA[b12]:.2e}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"{RAZON[b16]:.0f}x mejor a {b16} bits"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)
