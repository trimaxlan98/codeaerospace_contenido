class Clip3(Scene):
    """1.2.3 - La Tierra es un iman: un dipolo a escala de planeta. En el
    ecuador quedan 31 uT; el cubo se los come camino de GEO, donde apenas
    sobreviven 0.11 uT. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La Tierra es un imán")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el planeta -------------------------------------------
        tierra = tierra_iman()
        tierra.move_to(DOWN * 0.2)
        rot.mostrar(pie_curso("La brújula de Oersted ya se movía sola: la "
                              "Tierra entera es un imán."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(tierra.tierra, scale=1.2), run_time=0.8)
        self.wait(4.4)

        # --- momento: las lineas del dipolo --------------------------------
        rot.mostrar(pie_curso("Su campo es un dipolo: líneas cerradas de "
                              "polo a polo, a escala de planeta."),
                    zona="abajo", run_time=0.5)
        self.play(Create(tierra.lineas, lag_ratio=0.1), run_time=1.8)
        self.wait(4.4)

        # --- momento: la cifra de superficie -------------------------------
        rot.mostrar(pie_curso("En el ecuador quedan treinta y una "
                              "millonésimas de tesla: tu brújula vive de eso."),
                    zona="abajo", run_time=0.5)
        cifra_sup = tag_hud(f"{B_SUP * 1e6:.1f} uT en superficie",
                            font_size=16, color=C_B)
        cifra_sup.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(cifra_sup, shift=0.1 * DOWN), run_time=0.5)
        self.wait(4.4)

        # --- momento: la curva del cubo ------------------------------------
        rot.mostrar(pie_curso("¿Y subiendo? El dipolo cobra con el CUBO "
                              "de la distancia."), zona="abajo",
                    run_time=0.5)
        curva = haz_curvas([lambda r: b_tierra(r) * 1e6], (1.0, 7.0),
                           [C_B], ancho=6.0, alto=2.9,
                           etiqueta_x="distancia (radios terrestres)",
                           etiqueta_y="campo (uT)")
        curva.move_to(DOWN * 0.25)
        self.play(ReplacementTransform(tierra, curva),
                  FadeOut(cifra_sup), run_time=1.4)
        self.wait(3.0)

        # --- momento: el punto de partida ----------------------------------
        rot.mostrar(formula_pie(
            r"B(r) = B_{\text{ec}}\left(\frac{R_E}{r}\right)^{3}"),
            zona="abajo", run_time=0.5)
        p_sup = Dot(curva.punto_de(0, 1.0), radius=0.06, color=C_B)
        tag_sup = tag_hud(f"{B_SUP * 1e6:.1f} uT", font_size=16, color=C_B)
        tag_sup.next_to(p_sup, DR, buff=0.16)
        self.play(FadeIn(p_sup, scale=1.6),
                  FadeIn(tag_sup, shift=0.1 * RIGHT), run_time=0.6)
        self.wait(4.4)

        # --- momento: GEO --------------------------------------------------
        rot.mostrar(pie_curso("La órbita geoestacionaria queda a 6.6 "
                              "radios: allí el campo casi ha muerto."),
                    zona="abajo", run_time=0.5)
        guia = curva.vertical_en(R_GEO_RE, color=C_EJE)
        p_geo = Dot(curva.punto_de(0, R_GEO_RE), radius=0.06,
                    color=C_CALCULO)
        tag_geo = tag_hud(f"{B_GEO * 1e6:.2f} uT en GEO", font_size=16)
        tag_geo.next_to(p_geo, UL, buff=0.15)
        self.play(Create(guia), FadeIn(p_geo, scale=1.6),
                  FadeIn(tag_geo, shift=0.1 * UP), run_time=0.9)
        self.wait(4.4)

        rot.mostrar(pie_curso("Abajo, en órbita baja, aún hay empuje que "
                              "cosechar. Vamos a por él."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
