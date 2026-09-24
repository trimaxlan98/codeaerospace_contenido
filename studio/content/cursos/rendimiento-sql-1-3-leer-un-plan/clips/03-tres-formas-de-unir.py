class Clip3(Scene):
    """1.3.3 - Como empareja cada operador de union sus dos entradas. Cada
    metodo se muestra grande y solo, uno a la vez (bucle anidado, dos
    listas que avanzan juntas, una tabla en cubetas con sus filas cayendo);
    al final los tres quedan chicos en tres columnas para comparar. Sin
    cifras: solo el mecanismo. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Tres formas de unir"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # =====================================================================
        # A) NESTED LOOPS, grande y solo: por cada fila de afuera se repite
        #    adentro entero
        # =====================================================================
        caja_a = S.operador("Nested Loops", color=C_TITULO, ancho=3.6,
                            font_size=26)
        caja_a.move_to(UP * 2.3)
        self.play(FadeIn(caja_a, shift=UP * 0.15), run_time=0.6)

        outer = VGroup(*[Rectangle(width=1.7, height=0.6, stroke_color=C_INDICE,
                                   stroke_width=2.6) for _ in range(3)])
        outer.arrange(DOWN, buff=0.22)
        inner = VGroup(*[Rectangle(width=1.7, height=0.52, stroke_color=C_TENUE,
                                    stroke_width=2.6) for _ in range(5)])
        inner.arrange(DOWN, buff=0.16)
        grupoA = VGroup(outer, inner).arrange(RIGHT, buff=1.6)
        grupoA.move_to(DOWN * 0.35)
        t_out = tag_junto(outer, "afuera", DOWN, buff=0.22, font_size=24)
        t_in = tag_junto(inner, "adentro", DOWN, buff=0.22, font_size=24)
        self.play(FadeIn(outer), FadeIn(inner), FadeIn(t_out), FadeIn(t_in),
                  run_time=0.7)
        self.wait(0.4)

        for i in range(3):
            conector = Arrow(outer[i].get_right(), inner.get_left(), buff=0.1,
                             stroke_width=3, color=C_TENUE,
                             max_tip_length_to_length_ratio=0.15)
            self.play(outer[i].animate.set_stroke(C_BUENO, width=4),
                      Create(conector), run_time=0.5)
            self.play(LaggedStart(*[Indicate(r, color=C_BUENO, scale_factor=1.1)
                                    for r in inner], lag_ratio=0.15),
                      run_time=0.9)
            self.play(FadeOut(conector), run_time=0.25)
        self.wait(1.0)
        self.play(FadeOut(caja_a), FadeOut(outer), FadeOut(inner),
                  FadeOut(t_out), FadeOut(t_in), run_time=0.6)

        # =====================================================================
        # B) MERGE JOIN, grande y solo: dos listas ordenadas, dos punteros
        #    que avanzan juntos
        # =====================================================================
        caja_b = S.operador("Merge", color=C_TITULO, ancho=3.0, font_size=26)
        caja_b.move_to(UP * 2.3)
        self.play(FadeIn(caja_b, shift=UP * 0.15), run_time=0.6)

        listaA = VGroup(*[Rectangle(width=1.5, height=0.5, stroke_color=C_TENUE,
                                    stroke_width=2.6) for _ in range(5)])
        listaA.arrange(DOWN, buff=0.18)
        listaB = VGroup(*[Rectangle(width=1.5, height=0.5, stroke_color=C_TENUE,
                                    stroke_width=2.6) for _ in range(5)])
        listaB.arrange(DOWN, buff=0.18)
        parejas = VGroup(listaA, listaB).arrange(RIGHT, buff=1.6)
        parejas.move_to(DOWN * 0.35)
        self.play(FadeIn(listaA), FadeIn(listaB), run_time=0.7)

        pA = Triangle(color=C_MOTOR, fill_color=C_MOTOR, fill_opacity=1,
                     stroke_width=0).scale(0.16).rotate(-PI / 2)
        pA.next_to(listaA[0], LEFT, buff=0.16)
        pB = Triangle(color=C_MOTOR, fill_color=C_MOTOR, fill_opacity=1,
                     stroke_width=0).scale(0.16).rotate(PI / 2)
        pB.next_to(listaB[0], RIGHT, buff=0.16)
        self.play(FadeIn(pA), FadeIn(pB), run_time=0.4)

        for i in range(5):
            self.play(pA.animate.next_to(listaA[i], LEFT, buff=0.16),
                      pB.animate.next_to(listaB[i], RIGHT, buff=0.16),
                      run_time=0.4)
            self.play(listaA[i].animate.set_stroke(C_BUENO, width=4),
                      listaB[i].animate.set_stroke(C_BUENO, width=4),
                      run_time=0.35)
        self.wait(1.0)
        self.play(FadeOut(caja_b), FadeOut(listaA), FadeOut(listaB),
                  FadeOut(pA), FadeOut(pB), run_time=0.6)

        # =====================================================================
        # C) HASH JOIN, grande y solo: la fila de entrada CAE en su cubeta
        # =====================================================================
        caja_c = S.operador("Hash", color=C_TITULO, ancho=2.6, font_size=26)
        caja_c.move_to(UP * 2.5)
        self.play(FadeIn(caja_c, shift=UP * 0.15), run_time=0.6)

        colores_h = paleta_categorica(4)
        entrada = VGroup(*[Dot(radius=0.16, color=colores_h[i % 4])
                          for i in range(8)])
        entrada.arrange(RIGHT, buff=0.42)
        entrada.move_to(UP * 1.5)
        self.play(FadeIn(entrada), run_time=0.6)
        self.wait(0.3)

        cubetas = VGroup(*[Rectangle(width=1.3, height=1.7, stroke_color=C_TENUE,
                                     stroke_width=2.4) for _ in range(4)])
        cubetas.arrange(RIGHT, buff=0.45)
        cubetas.move_to(DOWN * 1.15)
        t_cub = tag_junto(cubetas, "cubetas", DOWN, buff=0.22, font_size=24)
        self.play(FadeIn(cubetas), FadeIn(t_cub), run_time=0.6)
        self.wait(0.3)

        conteo = [0, 0, 0, 0]
        anims = []
        for i, d in enumerate(entrada):
            k = i % 4
            destino = cubetas[k].get_bottom() + UP * (0.24 + conteo[k] * 0.4)
            conteo[k] += 1
            anims.append(d.animate(rate_func=rush_into).move_to(destino))
        self.play(LaggedStart(*anims, lag_ratio=0.2), run_time=2.4)
        self.play(LaggedStart(*[Indicate(c, color=C_TENUE, scale_factor=1.05)
                                for c in cubetas], lag_ratio=0.15), run_time=1.0)
        self.wait(1.0)
        self.play(FadeOut(caja_c), FadeOut(entrada), FadeOut(cubetas),
                  FadeOut(t_cub), run_time=0.6)

        # =====================================================================
        # D) LOS TRES, chicos y juntos, para comparar
        # =====================================================================
        cx1, cx2, cx3 = LEFT * 4.4, ORIGIN, RIGHT * 4.4
        y_caja = UP * 1.35

        mini_caja1 = S.operador("Nested Loops", color=C_TITULO, ancho=2.2)
        mini_caja1.move_to(cx1 + y_caja)
        mini_fuera = VGroup(*[Rectangle(width=0.62, height=0.26,
                                        stroke_color=C_BUENO, stroke_width=2)
                              for _ in range(3)])
        mini_fuera.arrange(DOWN, buff=0.1)
        mini_dentro = VGroup(*[Rectangle(width=0.62, height=0.26,
                                         stroke_color=C_BUENO, stroke_width=2)
                               for _ in range(5)])
        mini_dentro.arrange(DOWN, buff=0.08)
        mini_grupo1 = VGroup(mini_fuera, mini_dentro).arrange(RIGHT, buff=1.0)
        mini_grupo1.next_to(mini_caja1, DOWN, buff=0.35)

        mini_caja2 = S.operador("Merge", color=C_TITULO)
        mini_caja2.move_to(cx2 + y_caja)
        mini_A = VGroup(*[Rectangle(width=0.5, height=0.24, stroke_color=C_BUENO,
                                    stroke_width=2) for _ in range(5)])
        mini_A.arrange(DOWN, buff=0.09)
        mini_B = VGroup(*[Rectangle(width=0.5, height=0.24, stroke_color=C_BUENO,
                                    stroke_width=2) for _ in range(5)])
        mini_B.arrange(DOWN, buff=0.09)
        mini_grupo2 = VGroup(mini_A, mini_B).arrange(RIGHT, buff=0.85)
        mini_grupo2.next_to(mini_caja2, DOWN, buff=0.35)

        mini_caja3 = S.operador("Hash", color=C_TITULO)
        mini_caja3.move_to(cx3 + y_caja)
        mini_puntos = VGroup(*[Dot(radius=0.07, color=colores_h[i % 4])
                              for i in range(8)])
        mini_puntos.arrange(RIGHT, buff=0.12)
        mini_cubetas = VGroup(*[Rectangle(width=0.62, height=0.5,
                                          stroke_color=C_TENUE, stroke_width=1.8)
                                for _ in range(4)])
        mini_cubetas.arrange(RIGHT, buff=0.18)
        mini_grupo3 = VGroup(mini_puntos, mini_cubetas).arrange(DOWN, buff=0.2)
        mini_grupo3.next_to(mini_caja3, DOWN, buff=0.35)
        conteo2 = [0, 0, 0, 0]
        for i, d in enumerate(mini_puntos):
            k = i % 4
            d.move_to(mini_cubetas[k].get_bottom() + UP * (0.14 + conteo2[k] * 0.16))
            conteo2[k] += 1

        self.play(FadeIn(mini_caja1), FadeIn(mini_grupo1),
                  FadeIn(mini_caja2), FadeIn(mini_grupo2),
                  FadeIn(mini_caja3), FadeIn(mini_grupo3), run_time=0.9)
        self.wait(6.0)
