class Clip2(Scene):
    """4.2.2 - La esfera que se reparte: la misma potencia sobre una
    superficie que crece con el cuadrado. No hay absorcion — el vacio no
    se queda nada — solo reparto. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La esfera que se reparte")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el emisor no apunta a nadie --------------------------
        esf = esfera_reparto(radios=(0.7, 1.3, 1.9, 2.5))
        esf.move_to(LEFT * 2.0 + DOWN * 0.2)
        rot.mostrar(pie_curso("Un transmisor no le habla a nadie en "
                              "concreto: reparte en todas direcciones."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(esf.emisor, scale=1.6),
                  Create(esf.frente(0)), run_time=0.8)
        self.wait(4.6)

        # --- momento: la misma energia, mas superficie ---------------------
        rot.mostrar(pie_curso("Cada frente lleva la MISMA energía, "
                              "estirada sobre una esfera mayor."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esf.frente(1)), Create(esf.frente(2)),
                  Create(esf.frente(3)), run_time=1.4)
        self.wait(4.4)

        # --- momento: el parche de antena, siempre el mismo ----------------
        # Los dos parches, arriba: mismo arco (la misma antena), cada vez
        # menos angulo del total. El ancho lo calcula la pieza.
        parche_cerca = esf.parche(0, angulo_deg=90.0)
        parche_lejos = esf.parche(3, angulo_deg=90.0)
        parche_cerca.set_stroke(width=7.5)
        parche_lejos.set_stroke(width=7.5)
        # La cuña se dibuja a los EXTREMOS del arco: el angulo que abarca
        # ese mismo trozo de antena, que se estrecha al alejarse.
        cuna_cerca = VGroup(*[
            DashedLine(esf.emisor.get_center(), extremo, stroke_width=1.4,
                       color=C_CALCULO, dash_length=0.07)
            for extremo in (parche_cerca.get_start(),
                            parche_cerca.get_end())])
        cuna_lejos = VGroup(*[
            DashedLine(esf.emisor.get_center(), extremo, stroke_width=1.4,
                       color=C_CALCULO, dash_length=0.07)
            for extremo in (parche_lejos.get_start(),
                            parche_lejos.get_end())])
        cuna_cerca.set_stroke(opacity=0.5)
        cuna_lejos.set_stroke(opacity=0.5)
        tag_cerca = tag_hud(f"{esf.flujo_relativo(0) * 100:.0f} %",
                            font_size=18)
        # A la izquierda del arco: encima pasan las dos rectas de la cuña
        # del parche lejano y se cruzarian con el rotulo.
        tag_cerca.next_to(parche_cerca, UL, buff=0.10)
        tag_lejos = tag_hud(f"{esf.flujo_relativo(3) * 100:.0f} %",
                            font_size=18)
        tag_lejos.next_to(parche_lejos, UP, buff=0.20)

        rot.mostrar(pie_curso("Tu antena recoge siempre el mismo trozo de "
                              "arco. Cerca, es una tajada del total."),
                    zona="abajo", run_time=0.5)
        self.play(Create(parche_cerca), FadeIn(cuna_cerca),
                  FadeIn(tag_cerca), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Más lejos, ese mismo trozo apenas abarca "
                              "ángulo: recoge un ocho por ciento."),
                    zona="abajo", run_time=0.5)
        self.play(Create(parche_lejos), FadeIn(cuna_lejos),
                  FadeIn(tag_lejos), run_time=0.7)
        self.wait(4.6)

        # --- momento: la cifra monstruo ------------------------------------
        cifras = VGroup(
            tag_hud(f"{P_EMISOR:.0f} W a {H_GEO / 1e3:,.0f} km"
                    .replace(",", " ")),
            tag_hud(f"{FLUJO_GEO * 1e15:.1f} fW por m2"),
            tag_hud(f"reparto: {FSPL_GEO:.1f} dB"))
        cifras.arrange(DOWN, aligned_edge=LEFT, buff=0.42)
        cifras.move_to(RIGHT * 4.0 + UP * 0.15)

        rot.mostrar(pie_curso("Cien vatios sobre la esfera de GEO: seis "
                              "femtovatios por metro cuadrado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cifras, shift=0.15 * RIGHT), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Nadie absorbe nada: el vacío solo reparte. "
                              "Es el 1/r² de la primera lección."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
