class Clip3(Scene):
    """3 - La espiral que no cambia de forma. Los cocientes de Fibonacci
    convergen a phi; los cuadrados arman la espiral; escalarla es girarla
    (autosemejanza); el nautilus honesto y el gato enroscado. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La espiral que no cambia de forma")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: los cocientes se acercan a phi ----------------------
        rot.mostrar(pie_curso("Los cocientes de Fibonacci se acercan a un "
                              "número que la geometría conocía: φ."),
                    zona="abajo", run_time=0.5)
        pares = VGroup()
        for i, c in enumerate(COCIENTES_FIB):
            frac = MathTex(rf"\tfrac{{{FIB[i + 2]}}}{{{FIB[i + 1]}}}",
                           font_size=34, color=C_ACENTO)
            valor = Text(f"{c:.3f}", font=FUENTE_HUD, font_size=15,
                         color=C_TENUE)
            valor.next_to(frac, DOWN, buff=0.18)
            pares.add(VGroup(frac, valor))
        pares.arrange(RIGHT, buff=0.66).move_to(UP * 1.9)
        self.play(LaggedStart(*[FadeIn(p, shift=0.15 * UP) for p in pares],
                              lag_ratio=0.18), run_time=2.2)

        phi_tag = MathTex(rf"\varphi = {PHI:.6f}\ldots", font_size=40,
                          color=C_CONSTANTE)
        phi_tag.next_to(pares, DOWN, buff=0.55)
        self.play(Write(phi_tag), run_time=0.9)
        self.wait(2.6)

        # --- momento: los cuadrados arman la espiral ----------------------
        rot.mostrar(pie_curso("Crecer multiplicando es girar: la espiral "
                              "logarítmica es la firma del crecimiento."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pares), phi_tag.animate.scale(0.72).move_to(
            LEFT * 4.9 + UP * 2.15), run_time=0.7)

        cuadros = rectangulos_fibonacci(7, lado=0.155)
        cuadros.move_to(LEFT * 3.3 + DOWN * 0.55)
        self.play(LaggedStart(*[cuadros.aparecer(i) for i in range(7)],
                              lag_ratio=0.35), run_time=2.6)
        self.wait(1.2)

        # --- momento: escalar la espiral es girarla -----------------------
        espiral = espiral_log(vueltas=2.75, escala=1.9)
        espiral.move_to(RIGHT * 2.4 + DOWN * 0.45)
        self.play(Create(espiral), run_time=1.4)
        copia, ang = espiral.autosemejante(PHI)
        copia.set_color(C_CONSTANTE)
        copia.set_stroke(opacity=0.55)
        self.add(copia)
        self.play(Rotate(copia, ang, about_point=espiral.polo()),
                  run_time=1.6)
        self.wait(1.2)
        self.play(FadeOut(copia), run_time=0.4)

        # --- momento: el nautilus honesto ---------------------------------
        rot.mostrar(pie_curso("El nautilus dibuja una espiral logarítmica. "
                              "La «espiral áurea» del póster es un mito."),
                    zona="abajo", run_time=0.5)
        nautilo = espiral_log(b=B_NAUTILUS, vueltas=2.75, escala=1.05,
                              color=C_VIDA)
        nautilo.move_to(LEFT * 3.3 + DOWN * 0.55)
        tag_n = tag_junto(nautilo, f"nautilus  b = {B_NAUTILUS:.2f}", DOWN,
                          buff=0.30, font_size=17, color=C_VIDA)
        tag_a = tag_junto(espiral, f"áurea  b = {B_AUREA:.2f}", DOWN,
                          buff=0.30, font_size=17, color=C_ACENTO)
        self.play(FadeOut(cuadros), run_time=0.5)
        self.play(Create(nautilo), FadeIn(tag_n), FadeIn(tag_a),
                  run_time=1.4)
        self.wait(4.2)

        # --- momento: el gato tambien lo sabe -----------------------------
        rot.mostrar(pie_curso("Un gato dormido también lo sabe: enroscarse "
                              "igual a cualquier tamaño."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(nautilo), FadeOut(tag_n), run_time=0.5)
        gato = gato_dormido(escala=1.05)
        gato.move_to(LEFT * 3.3 + DOWN * 0.5)
        self.play(FadeIn(gato, shift=0.2 * UP), run_time=0.9)
        abrazo = espiral_log(b=0.35, vueltas=2.2, escala=1.12, color=C_VIDA,
                             grosor=2.6)
        # Anclada por el POLO, no por move_to: la espiral es asimetrica y
        # centrar su bounding box la descoloca del ovillo.
        abrazo.shift(gato.get_center() + RIGHT * 0.15 + DOWN * 0.05
                     - abrazo.polo())
        self.play(Create(abrazo), run_time=1.3)
        self.wait(4.6)
