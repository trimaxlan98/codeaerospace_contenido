class Clip4(Scene):
    """4.2.4 - Con una fuente puntual el flujo solo ve lo ENCERRADO: el
    mismo 6.28 para cualquier radio, y 0.00 si la fuente queda fuera. Esa
    es la ley de Gauss. Cierre de la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La ley de Gauss")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la fuente puntual -----------------------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, campo_fuente, paso=1.0, escala=0.5,
                              x0=-3.5, x1=3.5, y0=-2.5, y1=2.5,
                              magnitud_max=MAG_MAX_FUENTE, opacidad=0.8)
        fuente = punto_brillante(pl.p(np.array([0.0, 0.0])), color=C_GRAD,
                                 radio=0.09)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Una fuente puntual en el origen: de ella "
                              "brota todo el campo."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(fuente, scale=0.5), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in campo.flechas],
                              lag_ratio=0.02), run_time=1.8)
        panel = panel_derecha(MathTex(r"F = \frac{\vec r}{|\vec r|^{2}}",
                                      font_size=34, color=C_TITULO))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.6)

        # --- momento: un circulo pequeno que la encierra -------------------
        rot.mostrar(pie_curso("Rodeémosla con un círculo pequeño y "
                              "midamos el flujo que lo cruza."),
                    zona="abajo", run_time=0.5)
        r_a = circulo((0.0, 0.0), R_GAUSS_A)
        curva_a = camino(pl, r_a, color=C_REGION, grosor=3.4, n=220)
        norm_a = normales_borde(pl, r_a, n=10, largo=0.36, color=C_GRAD)
        medida = _con_fondo(tag_hud(f"flujo = {fmt(FLUJO_GAUSS_A, 2)}",
                                    font_size=22, color=C_RES),
                            buff=0.10, opacidad=0.88)
        medida.to_edge(UP, buff=1.18).shift(LEFT * 3.6)
        # el campo se atenua en cuanto entra la curva: a partir de aqui las
        # protagonistas son la cerrada y sus normales (ambas calidas)
        self.play(campo.animate.set_opacity(0.28), run_time=0.4)
        self.play(Create(curva_a.trazo), run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(n) for n in norm_a],
                              lag_ratio=0.07), run_time=1.2)
        self.play(FadeIn(medida, shift=0.12 * DOWN), run_time=0.6)
        self.wait(2.6)

        # --- momento: otro radio, el mismo numero -------------------------
        rot.mostrar(pie_curso("Ahora otro del doble de radio. Más lejos el "
                              "campo es más débil, pero hay más borde."),
                    zona="abajo", run_time=0.5)
        r_b = circulo((0.0, 0.0), R_GAUSS_B)
        curva_b = camino(pl, r_b, color=C_REGION, grosor=3.4, n=220)
        norm_b = normales_borde(pl, r_b, n=10, largo=0.36, color=C_GRAD)
        medida_b = _con_fondo(tag_hud(f"flujo = {fmt(FLUJO_GAUSS_B, 2)}",
                                      font_size=22, color=C_RES),
                              buff=0.10, opacidad=0.88)
        medida_b.move_to(medida.get_center())
        self.play(FadeOut(norm_a), Transform(curva_a.trazo, curva_b.trazo),
                  run_time=1.2)
        self.play(LaggedStart(*[GrowArrow(n) for n in norm_b],
                              lag_ratio=0.07), run_time=1.2)
        self.play(FadeOut(medida), FadeIn(medida_b), run_time=0.5)
        self.wait(2.9)

        # --- momento: una curva que NO la encierra ------------------------
        rot.mostrar(pie_curso("Y una curva que deja la fuente fuera: "
                              "entra por un lado y sale por el otro."),
                    zona="abajo", run_time=0.5)
        r_c = circulo(C_FUERA, R_FUERA)
        curva_c = camino(pl, r_c, color=C_FLUJO, grosor=3.4, n=220)
        norm_c = normales_borde(pl, r_c, n=10, largo=0.3, color=C_GRAD)
        medida_c = _con_fondo(tag_hud(f"flujo = "
                                      f"{fmt(FLUJO_GAUSS_FUERA, 2)}",
                                      font_size=20, color=C_RES),
                              buff=0.10, opacidad=0.88)
        medida_c.move_to(pl.p(np.array(C_FUERA) + np.array([0.0, -1.45])))
        self.play(Create(curva_c.trazo), run_time=0.9)
        self.play(LaggedStart(*[GrowArrow(n) for n in norm_c],
                              lag_ratio=0.07), run_time=1.0)
        self.play(FadeIn(medida_c, shift=0.12 * UP), run_time=0.6)
        self.wait(3.2)

        # --- momento: eso es la ley de Gauss ------------------------------
        rot.mostrar(pie_curso("El flujo no mide la distancia: mide cuánta "
                              "fuente hay dentro. Eso es la ley de Gauss."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(panel), run_time=0.3)
        panel2 = panel_derecha(
            MathTex(r"\oint_{S} E\cdot dS = \frac{Q_{enc}}{\varepsilon_0}",
                    font_size=28, color=C_CALCULO),
            tag_hud(f"encierra: {fmt(DOS_PI, 2)}", font_size=19,
                    color=C_RES),
            tag_hud(f"no encierra: {fmt(FLUJO_GAUSS_FUERA, 2)}",
                    font_size=19, color=C_RES), buff=0.22)
        self.play(FadeIn(panel2, shift=0.15 * LEFT), run_time=0.7)
        self.wait(3.8)

        # --- cierre -------------------------------------------------------
        cierre_leccion(self, rot,
                       "Suma las fuentes de dentro.",
                       "O cuenta lo que cruza la frontera.",
                       "Siguiente lección: Stokes y Maxwell, los campos "
                       "que nos comunican.",
                       pl, campo, fuente, curva_a.trazo, norm_b,
                       curva_c.trazo, norm_c, medida_b, medida_c, panel2)
