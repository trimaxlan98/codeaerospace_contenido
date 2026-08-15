class Clip2(Scene):
    """2.3.2 - La onda transporta energia: la esfera que se reparte, la
    impedancia del vacio y el kilovoltio por metro que trae la luz del Sol.

    El mismo parche de antena sobre dos frentes hace visible el 1/r^2; luego
    eta0 pone la razon E/H y campo_de_flujo saca el numero gancho. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La energía a bordo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        esf = esfera_reparto(radios=(0.85, 1.7, 2.55))
        esf.move_to(LEFT * 2.9)

        def cono(arco):
            """Las dos generatrices del parche: el ANGULO que abarca."""
            centro = esf.emisor.get_center()
            return VGroup(
                Line(centro, arco.get_start(), stroke_width=1.5,
                     color=C_CALCULO, stroke_opacity=0.55),
                Line(centro, arco.get_end(), stroke_width=1.5,
                     color=C_CALCULO, stroke_opacity=0.55))

        # --- momento: la potencia se reparte --------------------------------
        rot.mostrar(pie_curso("La onda no solo viaja: lleva energía. El "
                              "emisor la suelta y el frente se abre."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(esf.emisor, scale=1.6),
                  LaggedStart(*[Create(f) for f in esf.frentes],
                              lag_ratio=0.35),
                  run_time=1.7)
        self.wait(4.6)

        # --- momento: el parche de cerca ------------------------------------
        # El parche tiene AREA FIJA: es siempre el mismo trozo de antena.
        parche_a = esf.parche(0, angulo_deg=22.0)
        cono_a = cono(parche_a)
        tag_antena = tag_hud("tu antena: el mismo trozo", font_size=18)
        tag_antena.move_to(RIGHT * 2.0 + UP * 1.85)
        guia_a = Line(parche_a.get_center(), tag_antena.get_left(),
                      buff=0.20, stroke_width=1.4, color=C_EJE)
        rot.mostrar(pie_curso("Tu antena es siempre el mismo trozo. De "
                              "cerca abarca un buen ángulo del frente."),
                    zona="abajo", run_time=0.5)
        self.play(Create(parche_a), Create(cono_a), Create(guia_a),
                  FadeIn(tag_antena), run_time=0.9)
        self.wait(4.4)

        # --- momento: el mismo parche, tres veces mas lejos ------------------
        parche_b = esf.parche(2, angulo_deg=-22.0)
        cono_b = cono(parche_b)
        tag_flujo = tag_hud(f"mismo trozo: 1/"
                            f"{1.0 / esf.flujo_relativo(2):.0f} del flujo",
                            font_size=18)
        tag_flujo.move_to(RIGHT * 2.0 + DOWN * 1.55)
        guia_b = Line(parche_b.get_center(), tag_flujo.get_left(),
                      buff=0.20, stroke_width=1.4, color=C_EJE)
        rot.mostrar(pie_curso("Al triple de distancia recoge un tercio de "
                              "ángulo, y una novena parte del flujo."),
                    zona="abajo", run_time=0.5)
        self.play(Create(parche_b), Create(cono_b), Create(guia_b),
                  FadeIn(tag_flujo), run_time=1.0)
        self.wait(4.6)

        # --- momento: la impedancia del vacio --------------------------------
        # A partir de aqui no se usan localizadores: la pieza puede escalar.
        geometria = VGroup(esf, parche_a, cono_a, parche_b, cono_b)
        eta_tex = MathTex(r"\eta_0 = \sqrt{\mu_0/\varepsilon_0} = "
                          rf"{ETA0:.2f}\ \Omega", font_size=36,
                          color=C_CALCULO)
        eta_tex.move_to(RIGHT * 1.9 + UP * 1.35)
        rot.mostrar(pie_curso("En el vacío, E y H guardan siempre la misma "
                              "razón: la impedancia del espacio libre."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tag_antena), FadeOut(tag_flujo),
                  FadeOut(guia_a), FadeOut(guia_b),
                  geometria.animate.scale(0.70).move_to(LEFT * 3.6),
                  run_time=1.0)
        self.play(FadeIn(eta_tex, shift=0.12 * UP), run_time=0.6)
        self.wait(4.4)

        # --- momento: lo que entrega el Sol ----------------------------------
        sol_tex = MathTex(rf"S_\odot = {S_SOL:.0f}\ \mathrm{{W/m^2}}",
                          font_size=32, color=C_ONDA)
        sol_tex.move_to(RIGHT * 1.9 + UP * 0.25)
        rot.mostrar(pie_curso("En la órbita terrestre, el Sol entrega mil "
                              "trescientos sesenta y un vatios por metro "
                              "cuadrado."), zona="abajo", run_time=0.5)
        self.play(FadeIn(sol_tex, shift=0.12 * UP), run_time=0.5)
        self.wait(4.4)

        # --- momento: un kilovoltio por metro ---------------------------------
        e_tex = MathTex(r"E = \sqrt{2\,\eta_0\,S} = "
                        rf"{E_SOL:.0f}\ \mathrm{{V/m}}", font_size=36,
                        color=C_CALCULO)
        e_tex.move_to(RIGHT * 1.9 + DOWN * 0.95)
        rot.mostrar(pie_curso("Con esa razón, la luz del Sol lleva mil "
                              "voltios por metro. Un kilovoltio, "
                              "atravesándote ahora."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(e_tex, shift=0.12 * UP), run_time=0.7)
        self.wait(4.8)
