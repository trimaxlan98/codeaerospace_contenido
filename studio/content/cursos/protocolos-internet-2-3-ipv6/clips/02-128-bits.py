class Clip2(Scene):
    """2.3.2 - Si 32 bits no alcanzaron: 128 bits, y una escala honesta
    (direcciones por metro cuadrado de la superficie terrestre). La
    direccion se escribe en hex, en 8 grupos, y `ipv6_comprimir` aplica la
    regla del doble dos puntos sobre el hueco de ceros mas largo. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("128 bits")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la magnitud -------------------------------------------
        rot.mostrar(pie_curso("Si 32 bits no alcanzaron, se hace una "
                              "direccion que no se pueda agotar."),
                    zona="abajo", run_time=0.5)
        formula = MathTex(r"2^{128} \approx %s \times 10^{%d}"
                          % (E128_MANT, E128_EXP),
                          font_size=46, color=C_CIFRA)
        formula.move_to(UP * 1.7)
        self.play(FadeIn(formula, shift=0.2 * UP), run_time=0.9)
        self.wait(5.0)

        # --- momento: la escala honesta ---------------------------------
        rot.mostrar(pie_curso("La escala honesta: direcciones por cada "
                              "metro cuadrado de la superficie terrestre."),
                    zona="abajo", run_time=0.5)
        tierra = Circle(radius=0.62, color=C_RED, stroke_width=2.4,
                        fill_color=C_RED, fill_opacity=0.10)
        tierra.move_to(LEFT * 3.0 + DOWN * 0.15)
        et_tierra = tag_hud("superficie terrestre", font_size=15,
                            color=C_EJE)
        et_tierra.next_to(tierra, DOWN, buff=0.20)
        m2 = MathTex(r"%s \times 10^{%d}\ \text{dir.}/\text{m}^2"
                    % (M2_MANT, M2_EXP), font_size=34, color=C_CIFRA)
        m2.next_to(tierra, RIGHT, buff=0.75)
        self.play(FadeIn(tierra), FadeIn(et_tierra), run_time=0.6)
        self.play(FadeIn(m2, shift=0.2 * RIGHT), run_time=0.8)
        self.wait(4.6)

        # --- momento: ocho grupos de hex -------------------------------------
        rot.mostrar(pie_curso("En hexadecimal: ocho grupos de 16 bits "
                              "cada uno."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(formula), FadeOut(tierra), FadeOut(et_tierra),
                  FadeOut(m2), run_time=0.5)
        filas = [[g] for g in DIR6_GRUPOS]
        t = tabla(["g%d" % (i + 1) for i in range(8)], [DIR6_GRUPOS],
                  anchos=[1.05] * 8, alto=0.6, fs=17, color=C_CAPA,
                  color_cab=C_EJE)
        t.move_to(UP * 0.9)
        self.play(FadeIn(t), run_time=0.8)
        self.wait(3.2)

        # --- momento: la regla del :: ----------------------------------------
        rot.mostrar(pie_curso("El doble dos puntos comprime el hueco de "
                              "ceros mas largo, y solo uno."),
                    zona="abajo", run_time=0.5)
        marco = SurroundingRectangle(VGroup(t.celda(0, 2), t.celda(0, 3),
                                            t.celda(0, 4)), color=C_PERDIDA,
                                     buff=0.08)
        self.play(Create(marco), run_time=0.7)
        self.wait(1.4)
        comprimida = tag_hud(DIR6_COMPRIMIDA, font_size=32, color=C_CIFRA)
        comprimida.move_to(DOWN * 1.2)
        self.play(FadeOut(marco), FadeIn(comprimida, shift=0.2 * UP),
                  run_time=0.9)
        self.wait(5.0)
