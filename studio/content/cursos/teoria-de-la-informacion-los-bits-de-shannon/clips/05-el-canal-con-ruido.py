class Clip5(Scene):
    """5 - El canal con ruido. Sesenta y cuatro bits salen por un canal
    binario simetrico con p = 0.1: los que llegan se comparan bit a bit y
    los volteados se marcan en rojo y se CUENTAN sobre el dibujo (5 de
    64, sembrados). El esquema del BSC con sus cuatro caminos pone el
    modelo, y la curva C = 1 - h(p) pone lo que sobrevive: 0.531 bits por
    uso a p = 0.1, 0.919 a p = 0.01 y cero a p = 0.5, donde el canal es
    puro azar. Cierre: hasta la capacidad se transmite sin errores, no
    bajando el ruido sino codificando. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El canal con ruido"), zona="arriba",
                    run_time=0.6)

        # Geometria: las dos tiras de 64 bits (2 filas de 32, celda 0.24 ->
        # 7.68 de ancho) viven en la banda central, la enviada arriba
        # (y = +1.45) y la recibida debajo (y = -0.15), corridas 0.35 a la
        # derecha para dejarles sitio a los tags de la izquierda. Cuando
        # entra el modelo, la recibida se encoge al filo superior y libera
        # la banda para el esquema (izquierda) y la curva (derecha).
        env = tira_bits(BITS_ENVIADOS, C_FUENTE, celda=0.24, filas=2)
        env.move_to(np.array([0.35, 1.45, 0.0]))
        rec = tira_bits(BITS_RECIBIDOS, C_FUENTE, celda=0.24, filas=2)
        rec.move_to(np.array([0.35, -0.15, 0.0]))

        tag_env = tag_hud("enviados", font_size=13, color=C_TENUE)
        tag_env.next_to(env, LEFT, buff=0.26)
        tag_rec = tag_hud("recibidos", font_size=13, color=C_TENUE)
        tag_rec.next_to(rec, LEFT, buff=0.26)

        # --- momento 1: 64 bits salen ---------------------------------------
        rot.mostrar(pie_curso("Sesenta y cuatro bits salen por un canal. "
                              "El ruido voltea uno de cada diez."),
                    zona="abajo")
        self.play(FadeIn(tag_env),
                  LaggedStart(*[FadeIn(c, scale=0.6) for c in env.celdas],
                              lag_ratio=0.012), run_time=1.6)
        self.wait(3.4)

        # --- momento 2: los que llegan --------------------------------------
        rot.mostrar(pie_curso("Los que llegan: cada bit volteado es "
                              "información que se borra."), zona="abajo")
        self.play(FadeIn(tag_rec), TransformFromCopy(env, rec), run_time=1.1)

        # La marca es una MUTACION: se prepara una tira gemela ya marcada y
        # se transforma la que esta en escena (asi la animacion se ve).
        rec_marcado = tira_bits(BITS_RECIBIDOS, C_FUENTE, celda=0.24,
                                filas=2)
        rec_marcado.move_to(rec.get_center())
        n_marcados = rec_marcado.marcar_distintos(BITS_ENVIADOS, C_RUIDO)
        if n_marcados != N_VOLTEADOS:
            raise ValueError(f"volteos contados {n_marcados} != "
                             f"{N_VOLTEADOS}: el canal dejo de ser "
                             f"determinista")
        tag_volteados = tag_hud(f"{N_VOLTEADOS} de {N_BITS_CANAL} volteados",
                                font_size=16, color=C_RUIDO)
        tag_volteados.next_to(rec, DOWN, buff=0.24)
        self.play(Transform(rec, rec_marcado), run_time=1.2)
        self.play(FadeIn(tag_volteados, shift=0.1 * UP), run_time=0.5)
        self.wait(2.6)

        # --- momento 3: el modelo -------------------------------------------
        rot.mostrar(pie_curso("El modelo: canal binario simétrico, con "
                              "probabilidad p de error."), zona="abajo")
        tag_volteados_alto = tag_hud(f"{N_VOLTEADOS} de {N_BITS_CANAL} "
                                     f"volteados", font_size=13,
                                     color=C_RUIDO)
        tag_volteados_alto.move_to(np.array([0.0, 1.50, 0.0]))
        self.play(FadeOut(env), FadeOut(tag_env), FadeOut(tag_rec),
                  rec.animate.scale(0.62).move_to(np.array([0.0, 1.94, 0.0])),
                  Transform(tag_volteados, tag_volteados_alto), run_time=1.0)

        esquema = esquema_bsc(P_BSC).scale(0.92)
        esquema.move_to(np.array([-3.5, -0.55, 0.0]))
        tag_bsc = tag_hud(f"BSC: p = {P_BSC}", font_size=13, color=C_TENUE)
        tag_bsc.next_to(esquema, DOWN, buff=0.28)
        self.play(FadeIn(esquema.nodos), Create(esquema.flechas),
                  run_time=1.0)
        self.play(FadeIn(esquema.etiquetas), FadeIn(tag_bsc), run_time=0.5)
        self.wait(2.6)

        # --- momento 4: lo que sobrevive ------------------------------------
        rot.mostrar(pie_curso(f"Cuánta información sobrevive: C = 1 - h(p). "
                              f"Con p = {P_BSC}, {C_BSC_01:.3f} bits por "
                              f"bit."), zona="abajo")
        curva = curva_capacidad_bsc().scale(0.92)
        curva.move_to(np.array([2.55, -0.50, 0.0]))
        formula = MathTex(r"C = 1 - h(p)", font_size=30, color=C_LIMITE)
        formula.move_to(np.array([2.55, 1.45, 0.0]))
        self.play(Create(curva.ejes), FadeIn(curva.ticks),
                  FadeIn(curva.etiqueta_x), FadeIn(curva.etiqueta_y),
                  run_time=0.7)
        self.play(Create(curva.curva), Write(formula), run_time=1.3)

        # Los rotulos viven DENTRO del plano, en el triangulo que la curva
        # (decreciente) deja vacio arriba a la derecha, escalonados para
        # que ninguno toque a otro ni cruce la curva.
        p_01 = curva.en(P_BSC)
        dot_01 = Dot(p_01, radius=0.075, color=C_BIT)
        tag_01 = tag_hud(f"C({P_BSC}) = {C_BSC_01:.3f} bits/uso",
                         font_size=13, color=C_LIMITE)
        tag_01.move_to(curva.punto(0.275, 0.74))
        guia_01 = DashedLine(p_01, tag_01.get_bottom() + DOWN * 0.05,
                             stroke_width=1.2, color=C_LIMITE,
                             dash_length=0.07)
        guia_01.set_stroke(opacity=0.45)
        p_001 = curva.en(0.01)
        dot_001 = Dot(p_001, radius=0.062, color=C_BIT)
        tag_001 = tag_hud(f"p = 0.01 -> {C_BSC_001:.2f}", font_size=13,
                          color=C_LIMITE)
        tag_001.move_to(p_001 + RIGHT * 1.00 + UP * 0.05)
        self.play(FadeIn(dot_01, scale=0.5), Create(guia_01),
                  FadeIn(tag_01), run_time=0.7)
        self.play(FadeIn(dot_001, scale=0.5), FadeIn(tag_001), run_time=0.5)
        self.wait(2.4)

        # --- momento 5: p = 0.5, puro azar ----------------------------------
        rot.mostrar(pie_curso("Con p = 0.5 el canal es puro azar: no llega "
                              "nada."), zona="abajo")
        p_05 = curva.en(0.5)
        dot_05 = Dot(p_05, radius=0.075, color=C_RUIDO)
        tag_05 = tag_hud(f"C(0.5) = {C_BSC_05:.0f}", font_size=14,
                         color=C_RUIDO)
        tag_05.move_to(curva.punto(0.39, 0.28))
        guia_05 = DashedLine(p_05, tag_05.get_right() + RIGHT * 0.05,
                             stroke_width=1.2, color=C_RUIDO,
                             dash_length=0.07)
        guia_05.set_stroke(opacity=0.45)
        self.play(FadeIn(dot_05, scale=0.5), Create(guia_05),
                  FadeIn(tag_05), run_time=0.6)
        self.wait(3.6)

        # --- momento 6: el teorema de 1948 ----------------------------------
        rot.mostrar(pie_curso("Y el teorema de 1948: por debajo de ese "
                              "techo se transmite sin errores... "
                              "codificando."), zona="abajo")
        tag_techo = tag_hud("capacidad = techo", font_size=13, color=C_LIMITE)
        tag_techo.move_to(curva.punto(0.34, 0.48))
        self.play(FadeIn(tag_techo, shift=0.1 * UP), run_time=0.5)
        self.wait(3.8)

        # --- cierre ----------------------------------------------------------
        rot.mostrar(pie_curso("Hasta la capacidad, cero errores. No bajando "
                              "el ruido: codificando."), zona="abajo")
        self.wait(5.0)
