class Clip3(Scene):
    """6.3.3 - La silla a tamano completo: dos direcciones propias, una que
    estira y otra que encoge, y todas las trayectorias obedecen. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Las direcciones propias mandan")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la silla, a tamano completo ---------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Volvemos a la silla, ahora a tamaño "
                              "completo."), zona="abajo", run_time=0.5)
        mat = matriz_columnas(A_SILLA, dec=2, font_size=32)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.0)

        rot.mostrar(pie_curso("Un paso: la rejilla estira por una dirección "
                              "y encoge por la otra."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A_SILLA), run_time=2.0)
        self.wait(3.2)

        # --- momento: los dos ejes propios ----------------------------------
        rot.mostrar(pie_curso("Dos direcciones no giran nunca. Son los ejes "
                              "propios de la matriz."),
                    zona="abajo", run_time=0.5)
        rectas = VGroup(span_recta(pl, DIR_ESTIRA, color=C_PROPIO,
                                   opacidad=0.55),
                        span_recta(pl, DIR_ENCOGE, color=C_PROPIO,
                                   opacidad=0.55))
        v1 = vector(pl, V_ESTIRA, color=C_PROPIO, nombre=r"\vec v_1")
        v2 = vector(pl, V_ENCOGE, color=C_PROPIO, nombre=r"\vec v_2")
        self.play(*pl.anim_matriz(np.eye(2)), run_time=1.1)
        self.play(Create(rectas), run_time=0.7)
        self.play(GrowArrow(v1.flecha), GrowArrow(v2.flecha), run_time=0.8)
        self.play(FadeIn(v1.etiqueta), FadeIn(v2.etiqueta), run_time=0.3)
        self.wait(2.6)

        # --- momento: sobre ellos solo multiplica ---------------------------
        rot.mostrar(pie_curso("Sobre ellos la matriz solo multiplica: por "
                              + fmt(LAM_SILLA[0], 2) + " en una y por "
                              + fmt(LAM_SILLA[1], 2) + " en la otra."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A_SILLA, v1, v2), run_time=2.0)
        # Segunda caja DEBAJO del panel: un Transform del panel a otro con
        # mas piezas deja medio segundo de glifos a medio morphar.
        f1 = MathTex(r"A\vec v_1 =", fmt(LAM_SILLA[0], 2), r"\,\vec v_1",
                     font_size=28, color=C_PROPIO)
        f1[1].set_color(C_CALCULO)
        f2 = MathTex(r"A\vec v_2 =", fmt(LAM_SILLA[1], 2), r"\,\vec v_2",
                     font_size=28, color=C_PROPIO)
        f2[1].set_color(C_CALCULO)
        caja = _con_fondo(VGroup(f1, f2).arrange(DOWN, buff=0.24), buff=0.18,
                          opacidad=0.78)
        caja.next_to(panel, DOWN, buff=0.28).align_to(panel, RIGHT)
        self.play(FadeIn(caja, shift=0.15 * LEFT), run_time=0.7)
        self.wait(2.6)

        # --- momento: las trayectorias --------------------------------------
        rot.mostrar(pie_curso("Cualquier estado se reparte entre las dos: "
                              "una parte crece y la otra se apaga."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(v1), FadeOut(v2), *pl.anim_matriz(np.eye(2)),
                  run_time=1.2)
        trs = [trayectoria(pl, t, color=C_VEC, radio=0.055, grosor=2.0)
               for t in TRAYS_3]
        self.play(*[Create(t.segmentos) for t in trs],
                  *[FadeIn(t.puntos) for t in trs], run_time=2.2)
        self.wait(2.0)

        rot.mostrar(pie_curso("Todas acaban pegadas al eje que estira, y "
                              "huyen por él. El destino lo ponen los ejes."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(rectas[0], color=C_PROPIO, scale_factor=1.0),
                  run_time=0.9)
        self.wait(4.6)
