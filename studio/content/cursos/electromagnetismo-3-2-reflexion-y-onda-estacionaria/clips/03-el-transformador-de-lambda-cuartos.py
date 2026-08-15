class Clip3(Scene):
    """3.2.3 - El transformador de cuarto de onda. El escalon de 50 a 75
    se parte en dos escalones separados lambda/4: sus dos reflejos vuelven
    en contrafase y se matan entre ellos. Adaptar no es amortiguar. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El transformador de cuarto de onda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el escalon que rebota --------------------------------
        fro = frontera_z(Z_LINEA, Z_CARGA)
        fro.move_to(UP * 0.20)
        t_pot = tag_hud(f"vuelve el {fro.reflejada() * 100:.0f} % de la "
                        f"potencia", font_size=19)
        t_pot.next_to(fro, DOWN, buff=0.22)
        rot.mostrar(pie_curso("El escalón de 50 a 75 devuelve un 4 %. Y no "
                              "se pierde: se te vuelve encima."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fro), run_time=0.8)
        self.play(FadeIn(t_pot), run_time=0.4)
        self.wait(4.4)

        # --- momento: partir el escalon en dos -----------------------------
        lcu = linea_cuartos(Z_LINEA, Z_CARGA, largo_total=7.6,
                            alto=1.0)
        lcu.move_to(DOWN * 0.30)
        t_linea = tag_hud("linea", font_size=17, color=C_TENUE)
        t_linea.next_to(lcu.tramo(0), DOWN, buff=0.24)
        t_carga = tag_hud("carga", font_size=17, color=C_TENUE)
        t_carga.next_to(lcu.tramo(2), DOWN, buff=0.24)
        rot.mostrar(pie_curso("El truco no es amortiguar: es partir ese "
                              "escalón en DOS escalones."), zona="abajo",
                    run_time=0.5)
        self.play(ReplacementTransform(fro, lcu), FadeOut(t_pot),
                  run_time=1.2)
        self.play(FadeIn(t_linea), FadeIn(t_carga), run_time=0.5)
        self.wait(4.2)

        # --- momento: la media geometrica ----------------------------------
        # El marco abraza tambien la etiqueta del tramo: si solo rodea
        # el rectangulo, la linea de arriba parte el 61.2 por la mitad.
        marco = SurroundingRectangle(
            VGroup(lcu.tramo(1), lcu.etiquetas[1]), color=C_CALCULO,
            buff=0.12, stroke_width=2.4)
        rot.mostrar(pie_curso("El tramo de en medio no es un promedio "
                              "cualquiera: es la media geométrica."),
                    zona="abajo", run_time=0.5)
        self.play(Create(marco), run_time=0.7)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"Z = \sqrt{Z_1 Z_2} = "
                                rf"{lcu.z_adaptadora():.1f}\ \Omega"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: el cuarto de onda y los dos reflejos -----------------
        br = Brace(lcu.tramo(1), DOWN, color=C_CALCULO)
        lab = MathTex(r"\lambda/4", font_size=28, color=C_CALCULO)
        lab.next_to(br, DOWN, buff=0.10)
        x1 = lcu.tramo(0).get_right()[0]
        x2 = lcu.tramo(1).get_right()[0]
        ref1 = Arrow(np.array([x1, 1.15, 0.0]),
                     np.array([x1 - 1.1, 1.15, 0.0]), buff=0,
                     color=C_CARGA, stroke_width=4.0, tip_length=0.16)
        ref2 = Arrow(np.array([x2, 1.80, 0.0]),
                     np.array([x2 - 1.1, 1.80, 0.0]), buff=0,
                     color=C_CARGA, stroke_width=4.0, tip_length=0.16)
        s1 = MathTex("+", font_size=34, color=C_CARGA)
        s1.next_to(ref1, RIGHT, buff=0.16)
        s2 = MathTex("-", font_size=34, color=C_CARGA)
        s2.next_to(ref2, RIGHT, buff=0.16)
        rot.mostrar(pie_curso("Y mide un cuarto de onda: el segundo "
                              "reflejo hace ida y vuelta y sale al revés."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(br), FadeIn(lab), run_time=0.6)
        self.play(GrowArrow(ref1), GrowArrow(ref2), FadeIn(s1), FadeIn(s2),
                  run_time=0.8)
        self.wait(4.2)

        # --- momento: se matan entre ellos ---------------------------------
        cifras = tag_hud(f"reflejo: {GAMMA_SALTO ** 2 * 100:.0f} %  ->  "
                         f"{GAMMA_ADAPTADO ** 2 * 100:.0f} %",
                         font_size=22)
        cifras.move_to(np.array([0.0, 1.72, 0.0]))
        swr = MathTex(rf"\mathrm{{SWR}} = {swr_de(GAMMA_ADAPTADO):.2f}",
                      font_size=30, color=C_CALCULO)
        swr.move_to(np.array([0.0, 1.10, 0.0]))
        rot.mostrar(pie_curso("Los dos reflejos vuelven en contrafase y se "
                              "matan. Adaptar no es amortiguar."),
                    zona="abajo", run_time=0.5)
        self.play(ref2.animate.shift(DOWN * 0.65),
                  s2.animate.shift(DOWN * 0.65), run_time=0.8)
        self.play(FadeOut(ref1, scale=0.2), FadeOut(ref2, scale=0.2),
                  FadeOut(s1, scale=0.2), FadeOut(s2, scale=0.2),
                  run_time=0.6)
        self.play(FadeIn(cifras), FadeIn(swr), run_time=0.6)
        self.wait(4.6)
