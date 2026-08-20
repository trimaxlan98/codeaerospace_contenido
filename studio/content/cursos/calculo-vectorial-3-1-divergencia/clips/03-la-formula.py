class Clip3(Scene):
    """3.1.3 - La formula divide el balance en dos mitades: el estiron
    horizontal (dFx/dx) y el vertical (dFy/dy); sumados dan la misma
    divergencia medida en la cajita. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La fórmula")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la cajita vuelve, ahora para desmenuzarla -------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_FUENTE, paso=1.0, escala=0.4,
                              opacidad=0.5)
        cj = caja_conteo(pl, CAMPO_FUENTE, P_CAJA, lado=LADO_CAJA)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.8)
        self.play(FadeIn(cj), run_time=0.8)
        rot.mostrar(pie_curso("Separemos ese balance en dos mitades: lo "
                              "que pasa en x, y lo que pasa en y."),
                    zona="abajo", run_time=0.5)
        formula = MathTex(r"\nabla\cdot F = ",
                          r"\frac{\partial F_x}{\partial x}",
                          r" + ",
                          r"\frac{\partial F_y}{\partial y}",
                          font_size=32, color=C_TITULO)
        if formula.width > 5.6:
            formula.scale_to_fit_width(5.6)
        panel = panel_derecha(formula, buff=0.2)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        area = LADO_CAJA * LADO_CAJA
        term_x = (cj.flujos_lados[0] + cj.flujos_lados[2]) / area
        term_y = (cj.flujos_lados[1] + cj.flujos_lados[3]) / area

        # --- momento: el primer termino, un estiron horizontal --------------
        rot.mostrar(pie_curso("El lado derecho e izquierdo miden el "
                              "estirón horizontal: dFx/dx."), zona="abajo",
                    run_time=0.5)
        self.play(formula[1].animate.set_color(C_GRAD), run_time=0.4)
        self.play(Indicate(VGroup(cj.flechas[0], cj.flechas[2]),
                           color=C_GRAD, scale_factor=1.15), run_time=1.0)
        term_x_t = tag_hud(f"dFx/dx = {fmt(term_x)}", font_size=17,
                           color=C_GRAD)
        term_x_t.next_to(panel, DOWN, buff=0.18).align_to(panel, RIGHT)
        self.play(FadeIn(term_x_t, shift=0.1 * UP), run_time=0.6)
        self.wait(3.6)

        # --- momento: el segundo termino, un estiron vertical ----------------
        rot.mostrar(pie_curso("Arriba y abajo miden el estirón vertical: "
                              "dFy/dy."), zona="abajo", run_time=0.5)
        self.play(formula[3].animate.set_color(C_GRAD), run_time=0.4)
        self.play(Indicate(VGroup(cj.flechas[1], cj.flechas[3]),
                           color=C_GRAD, scale_factor=1.15), run_time=1.0)
        term_y_t = tag_hud(f"dFy/dy = {fmt(term_y)}", font_size=17,
                           color=C_GRAD)
        term_y_t.next_to(term_x_t, DOWN, buff=0.12).align_to(panel, RIGHT)
        self.play(FadeIn(term_y_t, shift=0.1 * UP), run_time=0.6)
        self.wait(3.8)

        # --- momento: la suma coincide con la caja completa -------------------
        rot.mostrar(pie_curso("Sumados, dan lo mismo que la cajita entera "
                              "midió de un tirón."), zona="abajo",
                    run_time=0.5)
        suma_t = tag_hud(f"suma = div = {fmt(term_x + term_y)}",
                         font_size=18, color=C_RES)
        suma_t.next_to(term_y_t, DOWN, buff=0.16).align_to(panel, RIGHT)
        self.play(FadeIn(suma_t, shift=0.1 * UP), run_time=0.6)
        self.play(Indicate(suma_t, color=C_RES, scale_factor=1.08),
                  run_time=0.9)
        self.wait(5.1)
