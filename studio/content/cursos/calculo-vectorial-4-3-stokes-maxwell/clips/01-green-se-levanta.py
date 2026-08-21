class Clip1(Scene):
    """4.3.1 - Green sube al espacio: la circulacion por un circuito
    cerrado es el flujo del rotacional por CUALQUIER tapa que se apoye en
    ese borde. Medido en la tapa plana y en la abombada: 4.0 y 4.0. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Green se levanta: Stokes")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el circuito cerrado, ahora en el espacio ------------
        esp = espacio_leccion(unidad=1.4, alcance=2, centro=DOWN * 0.12)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("Green vivía en el plano. Subamos su "
                              "circuito cerrado al espacio."),
                    zona="abajo", run_time=0.5)
        lados = VGroup(*[
            Line(esp.p(*ESQ_CIRCUITO[i]), esp.p(*ESQ_CIRCUITO[(i + 1) % 4]),
                 color=C_REGION, stroke_width=3.4)
            for i in range(4)])
        marcas = VGroup(*[
            flecha3(esp, BORDE3(t - 0.035), BORDE3(t + 0.035), C_REGION,
                    grosor=3.4, punta=0.15)
            for t in (0.125, 0.375, 0.625, 0.875)])
        self.play(Create(lados), run_time=1.3)
        self.play(FadeIn(marcas), run_time=0.5)
        self.wait(3.4)

        # --- momento: el borde cobra su circulacion -----------------------
        rot.mostrar(pie_curso("El campo empuja a lo largo del borde. "
                              "Sumemos ese empuje por toda la vuelta."),
                    zona="abajo", run_time=0.5)
        muestras = VGroup()
        for t in T_MUESTRAS_BORDE:
            q = BORDE3(t)
            F = CAMPO_3D(q)
            m = float(np.linalg.norm(F))
            muestras.add(flecha3(esp, q, q + F * 0.6,
                                 color_calor(0.15 + 0.85 * m
                                             / MAG_BORDE_MAX),
                                 grosor=2.8, punta=0.12))
        self.play(LaggedStart(*[GrowArrow(f) for f in muestras],
                              lag_ratio=0.16), run_time=2.0)
        dato_borde = VGroup(tag_hud("borde (circulacion)", font_size=16,
                                    color=C_TENUE),
                            tag_hud(fmt(CIRC_BORDE), font_size=24,
                                    color=C_RES))
        dato_borde.arrange(DOWN, buff=0.07)
        fila_borde = _con_fondo(dato_borde, buff=0.14, opacidad=0.92)
        fila_borde.to_corner(UR, buff=0.5).shift(DOWN * 0.62)
        self.play(FadeIn(fila_borde, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.2)

        # --- momento: la tapa plana y el rotacional que la atraviesa ------
        rot.mostrar(pie_curso("Tapemos el circuito. El rotacional del "
                              "campo atraviesa esa tapa."), zona="abajo",
                    run_time=0.5)
        tapa = parche3(esp, S_PLANO, nu=9, nv=9, normales=3)
        self.play(FadeIn(tapa.malla), run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(f) for f in tapa.normales],
                              lag_ratio=0.12), run_time=1.2)
        rot3 = _con_fondo(MathTex(r"\nabla\times F = (0,\,0,\,2)",
                                  font_size=30, color=C_CALCULO), buff=0.16)
        rot3.to_corner(UL, buff=0.5).shift(DOWN * 0.95)
        self.play(FadeIn(rot3, shift=0.15 * RIGHT), run_time=0.6)
        fila_tapa = VGroup(tag_hud("tapa plana (flujo)", font_size=16,
                                   color=C_TENUE),
                           tag_hud(fmt(FLUJO_PLANO), font_size=24,
                                   color=C_RES))
        fila_tapa.arrange(DOWN, buff=0.07)
        fila_tapa = _con_fondo(fila_tapa, buff=0.14, opacidad=0.92)
        fila_tapa.next_to(fila_borde, DOWN, buff=0.28)
        fila_tapa.align_to(fila_borde, RIGHT)
        self.play(FadeIn(fila_tapa, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.6)

        # --- momento: la tapa se abomba y el numero no se mueve -----------
        rot.mostrar(pie_curso("Abombemos la tapa: el borde es el mismo y "
                              "la cuenta tampoco cambia."), zona="abajo",
                    run_time=0.5)
        domo = parche3(esp, S_DOMO, nu=9, nv=9, normales=3)
        self.play(Transform(tapa, domo), run_time=2.2)
        dato_domo = VGroup(tag_hud("tapa abombada (flujo)", font_size=16,
                                   color=C_TENUE),
                           tag_hud(fmt(FLUJO_DOMO), font_size=24,
                                   color=C_RES))
        dato_domo.arrange(DOWN, buff=0.07)
        fila_domo = _con_fondo(dato_domo, buff=0.14, opacidad=0.92)
        fila_domo.next_to(fila_borde, DOWN, buff=0.28)
        fila_domo.align_to(fila_borde, RIGHT)
        self.play(FadeOut(fila_tapa), FadeIn(fila_domo), run_time=0.6)
        # Indicate SOLO sobre el contenido: si toca el _con_fondo, el
        # rectangulo del fondo tambien se tine y el rotulo deja de leerse.
        self.play(Indicate(dato_borde, color=C_RES, scale_factor=1.06),
                  Indicate(dato_domo, color=C_RES, scale_factor=1.06),
                  run_time=1.0)
        self.wait(2.8)

        # --- momento: el teorema ------------------------------------------
        rot.mostrar(formula_pie(r"\oint_{\partial S} F\cdot dr "
                                r"= \iint_S (\nabla\times F)\cdot dS"),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)
