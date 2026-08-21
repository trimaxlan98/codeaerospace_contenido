class Clip2(Scene):
    """6.3.2 - La curva de aprendizaje MEDIDA: 400 episodios de recompensa,
    la media movil de 20 y el salto del primer quinto (67.5) al ultimo
    (93.6), con epsilon decayendo. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Explorar y explotar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        on = onda(EP, REC, rango_y=(REC_Y0, REC_Y1), ancho=9.2, alto=3.45,
                  color=C_EJE, grosor=1.6)
        on.move_to(LEFT * 0.60 + DOWN * 0.10)
        on.curva.set_stroke(opacity=0.55)
        et_x = tag_hud(f"episodios (0 - {len(REC)}), {PASOS_EP} decisiones "
                       "cada uno", font_size=17, color=C_TENUE)
        et_x.next_to(on, DOWN, buff=0.20)
        et_y = tag_hud("bits-simb. cobrados", font_size=17, color=C_TENUE)
        et_y.rotate(PI / 2).next_to(on, LEFT, buff=0.16)

        def banda(i0, i1, color):
            a, b = on.en(EP[i0], REC_Y0), on.en(EP[i1], REC_Y1)
            r = Rectangle(width=abs(b[0] - a[0]), height=abs(b[1] - a[1]),
                          color=color, stroke_width=1.4)
            r.set_fill(color, opacity=0.10)
            r.move_to((a + b) / 2.0)
            return r

        # --- momento: los primeros episodios son a ciegas ------------------
        rot.mostrar(pie_curso("Cuatrocientos episodios de cuarenta "
                              "decisiones. Al principio el agente prueba "
                              "casi a ciegas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(on.ejes), FadeIn(et_x), FadeIn(et_y), run_time=0.7)
        self.play(Create(on.curva), run_time=3.2, rate_func=linear)
        self.wait(3.4)

        # --- momento: la media movil deja ver la tendencia -----------------
        rot.mostrar(pie_curso(f"Bajo el ruido hay una tendencia: la media "
                              f"movil de {VENTANA_MM} episodios."),
                    zona="abajo", run_time=0.5)
        suave = on.curva_de(EP_MM, MM, color=C_IA, grosor=3.4)
        muestra_a = Line(ORIGIN, RIGHT * 0.42, color=C_EJE, stroke_width=2.0)
        muestra_a.set_stroke(opacity=0.6)
        ley_a = VGroup(muestra_a,
                       tag_hud("recompensa por episodio", font_size=16,
                               color=C_TENUE).next_to(muestra_a, RIGHT,
                                                      buff=0.14))
        muestra_b = Line(ORIGIN, RIGHT * 0.42, color=C_IA, stroke_width=3.4)
        ley_b = VGroup(muestra_b,
                       tag_hud(f"media movil de {VENTANA_MM}", font_size=16,
                               color=C_IA).next_to(muestra_b, RIGHT,
                                                   buff=0.14))
        leyenda = VGroup(ley_a, ley_b).arrange(RIGHT, buff=0.75)
        leyenda.next_to(et_x, DOWN, buff=0.22)
        self.play(Create(suave), run_time=2.6, rate_func=linear)
        self.play(FadeIn(leyenda), run_time=0.5)
        self.wait(3.5)

        # --- momento: el salto MEDIDO del primer al ultimo quinto ----------
        rot.mostrar(pie_curso(f"El primer quinto promedia "
                              f"{fmt(REC_INI, 1)} bits-simbolo; el ultimo, "
                              f"{fmt(REC_FIN, 1)}."),
                    zona="abajo", run_time=0.5)
        b_ini = banda(0, Q5 - 1, C_TENUE)
        b_fin = banda(len(REC) - Q5, len(REC) - 1, C_CIFRA)
        lin_ini = on.horizontal_en(REC_INI, color=C_TENUE)
        lin_fin = on.horizontal_en(REC_FIN, color=C_CIFRA)
        cif_ini = tag_hud(f"{fmt(REC_INI, 1)}", font_size=21, color=C_TENUE)
        cif_ini.next_to(on.en(EP[0], REC_INI), UR, buff=0.08)
        cif_ini.shift(RIGHT * 0.16)
        cif_ini = _con_fondo(cif_ini, buff=0.08, opacidad=0.85)
        cif_fin = tag_hud(f"{fmt(REC_FIN, 1)}", font_size=21)
        cif_fin.next_to(on.en(EP[0], REC_FIN), UR, buff=0.08)
        cif_fin.shift(RIGHT * 0.16)
        cif_fin = _con_fondo(cif_fin, buff=0.08, opacidad=0.85)
        self.play(FadeIn(b_ini), Create(lin_ini), FadeIn(cif_ini),
                  run_time=0.9)
        self.play(FadeIn(b_fin), Create(lin_fin), FadeIn(cif_fin),
                  run_time=0.9)
        subida = _con_fondo(tag_hud(f"+{fmt(SUBIDA_PCT, 0)} % por episodio",
                                    font_size=22),
                            buff=0.10, opacidad=0.88)
        subida.move_to(on.en(EP[len(REC) // 2], REC_Y1) + DOWN * 0.30)
        self.play(FadeIn(subida, shift=0.15 * UP), run_time=0.5)
        self.wait(4.2)

        # --- momento: epsilon decae ----------------------------------------
        rot.mostrar(pie_curso("Explorar primero, explotar despues: la "
                              "fraccion de tiradas al azar se apaga sola."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"al azar al empezar: {fmt(EPS_INI_PCT, 0)} %",
                    font_size=18, color=C_RUIDO),
            tag_hud(f"al azar al final: {fmt(EPS_FIN_PCT, 1)} %",
                    font_size=18, color=C_COD),
            tag_hud(f"piso en el episodio {fmt(EP_CONGELA, 0)}",
                    font_size=16, color=C_TENUE),
            buff=0.22)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(6.2)
