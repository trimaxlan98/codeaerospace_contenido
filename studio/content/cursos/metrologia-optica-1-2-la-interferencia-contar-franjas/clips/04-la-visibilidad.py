class Clip4(Scene):
    """4 - La visibilidad. Dos patrones con la misma fase y distinta salud:
    V = 1 (nitido) y V = 0.3 (lavado). La visibilidad compara el maximo con
    el minimo y se lava cuando la diferencia de camino supera la coherencia
    de la fuente. Cierre de la leccion a pantalla limpia. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La visibilidad"), zona="arriba",
                    run_time=0.6)

        # Los dos patrones apilados a la izquierda del centro, con su V a la
        # derecha de cada uno; la formula debajo, dentro de la banda.
        p_nitido = patron_franjas(0.0, 1.0, n_franjas=6, ancho=5.8, alto=1.30,
                                  n_barras=160)
        p_nitido.move_to(np.array([-0.90, 1.28, 0.0]))
        p_lavado = patron_franjas(0.0, 0.3, n_franjas=6, ancho=5.8, alto=1.30,
                                  n_barras=160)
        p_lavado.move_to(np.array([-0.90, -0.52, 0.0]))

        # Las dos cifras salen de `visibilidad` sobre las intensidades REALES
        # de cada pieza, no de la etiqueta que se le puso al construirla.
        i_a = p_nitido.intensidades()
        i_b = p_lavado.intensidades()
        v_a = visibilidad(float(i_a.max()), float(i_a.min()))
        v_b = visibilidad(float(i_b.max()), float(i_b.min()))
        t_a = tag_hud(f"V = {v_a:.1f}", font_size=19)
        t_a.next_to(p_nitido, RIGHT, buff=0.34)
        t_b = tag_hud(f"V = {v_b:.1f}", font_size=19)
        t_b.next_to(p_lavado, RIGHT, buff=0.34)

        # --- momento: no todas son iguales ----------------------------------
        rot.mostrar(pie_curso("No todas las franjas son iguales de nítidas."),
                    zona="abajo")
        self.play(FadeIn(p_nitido, shift=0.12 * UP), run_time=0.9)
        self.play(FadeIn(p_lavado, shift=0.12 * UP), run_time=0.9)
        self.wait(4.2)

        # --- momento: la definicion -----------------------------------------
        rot.mostrar(pie_curso("La visibilidad compara el máximo con el "
                              "mínimo: de uno a cero."), zona="abajo")
        eq = MathTex(r"V = \frac{I_{max}-I_{min}}{I_{max}+I_{min}}",
                     font_size=34, color=C_MEDIDA)
        eq.move_to(np.array([-0.90, -2.20, 0.0]))
        self.play(Write(eq), run_time=1.6)
        self.play(FadeIn(t_a), FadeIn(t_b), run_time=0.6)
        self.wait(4.6)

        # --- momento: se lava con el camino ---------------------------------
        rot.mostrar(pie_curso("Se lava cuando la diferencia de camino supera "
                              "la coherencia de la fuente."), zona="abajo")
        # El patron nitido se transforma en su gemela lavada: misma fase,
        # misma posicion, otra visibilidad.
        self.play(FadeOut(t_a), run_time=0.3)
        self.play(Transform(p_nitido, p_nitido.con_visibilidad(0.1)),
                  run_time=1.6)
        t_lc = tag_hud("L > Lc", font_size=19)
        t_lc.move_to(t_a.get_center())
        self.play(FadeIn(t_lc, shift=0.10 * UP), run_time=0.5)
        self.wait(4.4)

        # --- cierre a pantalla limpia -----------------------------------------
        self.play(FadeOut(p_nitido), FadeOut(p_lavado), FadeOut(t_b),
                  FadeOut(t_lc), FadeOut(eq), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        rot.limpiar("abajo", run_time=0.4)
        frase_1 = Text("Contar franjas es medir.", font_size=40,
                       color=C_TITULO)
        frase_2 = Text("Y se cuentan de una en una.", font_size=40,
                       color=C_FRANJA)
        VGroup(frase_1, frase_2).arrange(DOWN, buff=0.44)
        VGroup(frase_1, frase_2).move_to(np.array([0.0, 0.10, 0.0]))
        self.play(FadeIn(frase_1, shift=0.12 * UP), run_time=0.9)
        self.play(FadeIn(frase_2, shift=0.12 * UP), run_time=0.9)
        self.wait(5.0)
