class Clip3(Scene):
    """6.3.3 - Recompensa acumulada sobre el MISMO clima: agente (33541)
    contra conservador (14422) y optimista (30446); y la politica
    aprendida resulta ser la tabla sensata. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El agente contra las reglas fijas")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        on = onda(PASOS_DIB, ACUM_A_DIB, rango_y=(0.0, ACUM_Y1), ancho=6.5,
                  alto=3.30, color=C_IA, grosor=3.0)
        on.move_to(LEFT * 2.95 + DOWN * 0.30)

        def rotulo_curva(texto, color, serie, frac, direccion):
            """Etiqueta pegada a SU curva, en la fraccion pedida del
            recorrido: las tres quedan a alturas distintas."""
            i = int(frac * (len(PASOS_DIB) - 1))
            t = tag_hud(texto, font_size=18, color=color)
            t.next_to(on.en(PASOS_DIB[i], serie[i]), direccion, buff=0.20)
            # las tres rectas son empinadas: el fondo garantiza que la
            # etiqueta se lea aunque una curva le pase por detras.
            return _con_fondo(t, buff=0.08, opacidad=0.78)
        et_x = tag_hud(f"decisiones (0 - {N_DEC})", font_size=17,
                       color=C_TENUE)
        et_x.next_to(on, DOWN, buff=0.20)
        et_y = tag_hud("bits-simb. acumulados", font_size=17, color=C_TENUE)
        et_y.rotate(PI / 2).next_to(on, LEFT, buff=0.16)

        def cifra_fin(valor, color, desplazar):
            t = tag_hud(f"{fmt(valor, 0)}", font_size=22, color=color)
            t.next_to(on.en(PASOS_DIB[-1], valor), RIGHT, buff=0.14)
            t.shift(UP * desplazar)
            return t

        # --- momento: el mismo clima, tres maneras de operarlo -------------
        rot.mostrar(pie_curso(f"El mismo clima y las mismas {N_DEC} "
                              "decisiones seguidas, operadas de tres "
                              "maneras."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(on.ejes), FadeIn(et_x), FadeIn(et_y), run_time=0.7)
        self.wait(4.2)

        # --- momento: el conservador ---------------------------------------
        rot.mostrar(pie_curso(f"El conservador habla SIEMPRE en "
                              f"{MODCOD_NOMBRES[0]}: nunca se cae, y nunca "
                              "aprovecha el cielo despejado."),
                    zona="abajo", run_time=0.5)
        cur_c = on.curva_de(PASOS_DIB, ACUM_C_DIB, color=C_SENAL,
                            grosor=2.6)
        et_c = rotulo_curva("conservador", C_SENAL, ACUM_C_DIB, 0.68, DOWN)
        self.play(Create(cur_c), run_time=2.0, rate_func=linear)
        cif_c = cifra_fin(FIN_C, C_SENAL, 0.0)
        self.play(FadeIn(et_c), FadeIn(cif_c), run_time=0.5)
        self.wait(3.2)

        # --- momento: el optimista -----------------------------------------
        rot.mostrar(pie_curso(f"El optimista exprime SIEMPRE "
                              f"{MODCOD_NOMBRES[2]}: vuela con cielo claro "
                              "y calla bajo la lluvia."),
                    zona="abajo", run_time=0.5)
        cur_o = on.curva_de(PASOS_DIB, ACUM_O_DIB, color=C_BANDA,
                            grosor=2.6)
        et_o = rotulo_curva("optimista", C_BANDA, ACUM_O_DIB, 0.42, DOWN)
        self.play(Create(cur_o), run_time=2.0, rate_func=linear)
        cif_o = cifra_fin(FIN_O, C_BANDA, -0.19)
        self.play(FadeIn(et_o), FadeIn(cif_o), run_time=0.5)
        self.wait(3.2)

        # --- momento: el agente ---------------------------------------------
        rot.mostrar(pie_curso("El agente mira el cielo antes de hablar: se "
                              "adapta, y los rebasa a los dos."),
                    zona="abajo", run_time=0.5)
        et_a = rotulo_curva("el agente", C_IA, ACUM_A_DIB, 0.78, UP)
        self.play(Create(on.curva), run_time=2.2, rate_func=linear)
        cif_a = cifra_fin(FIN_A, C_IA, 0.19)
        self.play(FadeIn(et_a), FadeIn(cif_a), run_time=0.5)
        factores = VGroup(
            tag_hud(f"x{fmt(FACTOR_CONS, 1)} sobre el conservador",
                    font_size=19),
            tag_hud(f"+{fmt(GANA_OPT_PCT, 0)} % sobre el optimista",
                    font_size=19)).arrange(DOWN, buff=0.24)
        factores.move_to([4.20, 1.62, 0])
        self.play(FadeIn(factores, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.6)

        # --- momento: la politica aprendida ----------------------------------
        rot.mostrar(pie_curso("Y la politica que aprendio es, exactamente, "
                              "la tabla que un ingeniero habria escrito."),
                    zona="abajo", run_time=0.5)
        cab = Text("la politica aprendida", font_size=20, color=C_IA)
        cab.move_to([4.20, 0.26, 0])
        filas = VGroup()
        for s, nombre in enumerate(ESTADOS):
            a = int(POLITICA[s])
            et_s = Text(nombre, font_size=19, color=C_ESTADO[s])
            et_s.move_to([3.86, -0.36 - 0.62 * s, 0], aligned_edge=RIGHT)
            fl = Arrow([3.98, -0.36 - 0.62 * s, 0],
                       [4.42, -0.36 - 0.62 * s, 0], buff=0.0,
                       color=C_TENUE, stroke_width=2.4,
                       max_tip_length_to_length_ratio=0.30)
            et_a2 = Text(MODCOD_NOMBRES[a], font_size=19,
                         color=MODCOD_COLORES[a])
            et_a2.move_to([4.54, -0.36 - 0.62 * s, 0], aligned_edge=LEFT)
            filas.add(VGroup(et_s, fl, et_a2))
        self.play(FadeIn(cab), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(f, shift=0.15 * LEFT) for f in filas],
                              lag_ratio=0.35), run_time=1.5)
        self.wait(3.6)

        # --- momento: esto ya se hace ----------------------------------------
        rot.mostrar(pie_curso("DVB-S2X ya conmuta asi, y la Red del Espacio "
                              "Profundo ensaya enlaces cognitivos."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
