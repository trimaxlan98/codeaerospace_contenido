class Clip2(Scene):
    """4.3.2 - Las dos ecuaciones de Maxwell que hablan de divergencia:
    E nace en las cargas (flujo 6.28 por una curva que la encierra) y B no
    nace en ninguna parte (div 0.0, flujo 0.00, lineas cerradas). (~41 s)"""

    def _panel(self, etiqueta, cifra, esquina):
        fila = VGroup(tag_hud(etiqueta, font_size=16, color=C_TENUE),
                      tag_hud(cifra, font_size=24, color=C_RES))
        fila.arrange(DOWN, buff=0.07)
        return _con_fondo(fila, buff=0.14, opacidad=0.92).to_corner(
            esquina, buff=0.5).shift(DOWN * 0.98)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Leer a Maxwell: las divergencias")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano partido en dos ---------------------------
        pl = plano_leccion()
        divisor = DashedLine(pl.p(0, -2.6), pl.p(0, 2.3), color=C_TENUE,
                             stroke_width=1.6, dash_length=0.13)
        divisor.set_opacity(0.45)
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Con la divergencia y el flujo ya se pueden "
                              "LEER dos de las cuatro de Maxwell."),
                    zona="abajo", run_time=0.5)
        self.play(Create(divisor), run_time=0.6)
        self.wait(4.2)

        # --- momento: E nace en la carga --------------------------------
        rot.mostrar(pie_curso("A la izquierda, una carga. Su campo sale de "
                              "ella y se va al infinito."), zona="abajo",
                    run_time=0.5)
        carga = Dot(pl.p(P_CARGA), radius=0.12, color=C_VEC)
        campo_e = campo_flechas(pl, CAMPO_E, escala=0.55,
                                magnitud_max=MAG_MAX_CAMPOS, **MALLA_E)
        rotulo_e = _con_fondo(tag_hud("carga puntual", font_size=18,
                                      color=C_TENUE), buff=0.12,
                              opacidad=0.92)
        rotulo_e.move_to(pl.p(P_CARGA[0], -2.45))
        self.play(FadeIn(carga, scale=0.4), FadeIn(rotulo_e), run_time=0.6)
        self.play(LaggedStart(*[GrowArrow(f) for f in campo_e.flechas],
                              lag_ratio=0.03), run_time=1.7)
        ley_e = _con_fondo(MathTex(r"\nabla\cdot E = \rho/\varepsilon_0",
                                   font_size=32, color=C_CALCULO),
                           buff=0.14, opacidad=0.92)
        ley_e.move_to(pl.p(P_CARGA[0], 2.55))
        self.play(FadeIn(ley_e, shift=0.15 * DOWN), run_time=0.6)
        self.wait(2.2)

        # --- momento: el flujo delata a la fuente -----------------------
        rot.mostrar(pie_curso("Rodeémosla con una curva cerrada: el flujo "
                              "que la cruza no es cero."), zona="abajo",
                    run_time=0.5)
        curva_e = camino(pl, CURVA_E, color=C_REGION, grosor=3.0)
        norm_e = normales_borde(pl, CURVA_E, n=10, largo=0.42)
        self.play(Create(curva_e.trazo),
                  LaggedStart(*[GrowArrow(f) for f in norm_e],
                              lag_ratio=0.1), run_time=1.4)
        panel_e = self._panel("flujo por la curva", fmt(FLUJO_E, 2), UL)
        self.play(FadeIn(panel_e, shift=0.15 * RIGHT), run_time=0.5)
        self.wait(2.8)

        # --- momento: B, el campo del iman ------------------------------
        rot.mostrar(pie_curso("A la derecha, el campo de un imán. Mismas "
                              "herramientas, otra respuesta."),
                    zona="abajo", run_time=0.5)
        iman = Line(pl.p(P_IMAN + np.array([-0.28, 0.0])),
                    pl.p(P_IMAN + np.array([0.28, 0.0])), color=C_VEC,
                    stroke_width=7.0)
        campo_b = campo_flechas(pl, CAMPO_B, escala=0.55,
                                magnitud_max=MAG_MAX_CAMPOS, **MALLA_B)
        rotulo_b = _con_fondo(tag_hud("iman (dipolo)", font_size=18,
                                      color=C_TENUE), buff=0.12,
                              opacidad=0.92)
        rotulo_b.move_to(pl.p(P_IMAN[0], -2.45))
        self.play(FadeIn(iman, scale=0.4), FadeIn(rotulo_b), run_time=0.6)
        self.play(LaggedStart(*[GrowArrow(f) for f in campo_b.flechas],
                              lag_ratio=0.03), run_time=1.7)
        ley_b = _con_fondo(MathTex(r"\nabla\cdot B = 0", font_size=32,
                                   color=C_CALCULO), buff=0.14,
                           opacidad=0.92)
        ley_b.move_to(pl.p(P_IMAN[0], 2.55))
        self.play(FadeIn(ley_b, shift=0.15 * DOWN), run_time=0.6)
        self.wait(2.0)

        # --- momento: lineas cerradas, divergencia nula -----------------
        rot.mostrar(pie_curso("Sus líneas no empiezan ni acaban: se "
                              "cierran sobre sí mismas."), zona="abajo",
                    run_time=0.5)
        lineas = VGroup(*[
            linea_flujo(pl, CAMPO_B, P_IMAN + np.array([0.0, sy]), T=T,
                        color=C_FLUJO, grosor=2.8)
            for (sy, T) in SEMILLAS_B])
        self.play(LaggedStart(*[Create(c) for c in lineas], lag_ratio=0.35),
                  run_time=2.4)
        sondas = VGroup(*[Dot(pl.p(q), radius=0.08, color=C_RES)
                          for q in P_DIV_B])
        anillos = VGroup(*[Circle(radius=0.2, color=C_RES, stroke_width=2.0)
                           .move_to(d.get_center()) for d in sondas])
        panel_div = self._panel(
            "div en dos sondas",
            f"{fmt(DIV_B[0])}  y  {fmt(DIV_B[1])}", UR)
        self.play(FadeIn(sondas, scale=0.6), Create(anillos),
                  FadeIn(panel_div, shift=0.15 * LEFT), run_time=1.0)
        self.wait(1.8)

        # --- momento: ninguna curva encuentra fuente --------------------
        rot.mostrar(pie_curso("La misma curva cerrada, aquí: entra tanto "
                              "campo como sale. Cero."), zona="abajo",
                    run_time=0.5)
        curva_b = camino(pl, CURVA_B, color=C_REGION, grosor=3.0)
        norm_b = normales_borde(pl, CURVA_B, n=10, largo=0.42)
        self.play(Create(curva_b.trazo),
                  LaggedStart(*[GrowArrow(f) for f in norm_b],
                              lag_ratio=0.1), run_time=1.4)
        panel_b = self._panel("flujo por la curva", fmt(FLUJO_B, 2), UR)
        panel_b.shift(DOWN * 1.05)
        self.play(FadeIn(panel_b, shift=0.15 * LEFT), run_time=0.5)
        self.wait(2.8)

        rot.mostrar(pie_curso("Las cargas encienden el campo eléctrico. "
                              "El magnético no tiene dónde nacer."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)
