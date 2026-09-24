class Clip3(Scene):
    """1.2.3 - El plan guardado: la primera ejecucion compila (barra larga y
    tenue en la linea de tiempo) y dentro de la cache queda un plan legible
    de 2 operadores (Seek, Lookup: el mismo par de 1.2.2 para esta consulta);
    las siguientes ejecuciones lo reusan (barra corta y verde), incluso para
    OTRO valor de la misma columna -- semilla del sesgo del modulo 6. El
    contador de ejecuciones es una cuenta propia (1, 2, 3), no una medicion:
    va en tinta, ni ambar ni cian. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El plan guardado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.7)

        # --- la cache: grande, a la derecha, con un plan legible dentro -----
        cache = RoundedRectangle(width=4.2, height=2.8, corner_radius=0.14,
                                 stroke_color=C_TENUE, stroke_width=2.0,
                                 fill_color=C_TENUE, fill_opacity=0.06)
        cache.move_to(RIGHT * 2.7 + DOWN * 0.1)
        et_cache = tag_junto(cache, "cache de planes", UP, buff=0.24)
        self.play(FadeIn(cache), FadeIn(et_cache), run_time=0.7)
        self.wait(1.0)

        cont = Contador(0, rotulo="ejecuciones", font_size=30, digitos=1,
                        color=C_TENUE)
        cont.next_to(cache, DOWN, buff=0.45)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(0.8)

        # --- linea de tiempo de ejecuciones: una barra por ejecucion --------
        base_y = -1.7
        base = Line(LEFT * 6.35 + UP * base_y, LEFT * 2.15 + UP * base_y,
                   stroke_color=C_TENUE, stroke_width=2, stroke_opacity=0.6)
        self.play(Create(base), run_time=0.5)
        xs = (-5.75, -4.35, -2.95)

        def barra_ejecucion(x, alto, color):
            b = Rectangle(width=0.75, height=alto, stroke_width=0,
                         fill_color=color, fill_opacity=0.85)
            b.move_to(RIGHT * x + UP * base_y, aligned_edge=DOWN)
            return b

        # --- primera ejecucion: compila --------------------------------------
        q1 = S.codigo(["EXEC busca_cliente", "  @id = 501"], font_size=20)
        q1.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q1, shift=RIGHT * 0.2), run_time=0.6)
        b1 = barra_ejecucion(xs[0], 1.7, C_TENUE)
        et_b1 = tag_junto(b1, "compilar", DOWN, buff=0.16)
        self.play(GrowFromEdge(b1, DOWN), FadeIn(et_b1), run_time=1.0)
        self.wait(0.6)

        seek = S.operador("Seek", color=C_INDICE, ancho=1.5, alto=0.75,
                          font_size=22)
        lookup = S.operador("Lookup", color=C_INDICE, ancho=1.7, alto=0.75,
                            font_size=22)
        VGroup(seek, lookup).arrange(RIGHT, buff=0.55).move_to(cache.get_center())
        flecha_sl = Arrow(seek.get_right(), lookup.get_left(), buff=0.08,
                          stroke_width=2.4, color=C_INDICE,
                          max_tip_length_to_length_ratio=0.22)
        self.play(FadeIn(seek, shift=RIGHT * 0.15), run_time=0.5)
        self.play(Create(flecha_sl), FadeIn(lookup, shift=RIGHT * 0.15),
                  run_time=0.6)
        cont.fijar(1)
        self.wait(1.4)

        # --- segunda ejecucion: mismo valor, reusa el plan -------------------
        self.play(FadeOut(q1), run_time=0.4)
        q2 = S.codigo(["EXEC busca_cliente", "  @id = 501"], font_size=20)
        q2.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q2, shift=RIGHT * 0.2), run_time=0.6)
        b2 = barra_ejecucion(xs[1], 0.55, C_BUENO)
        et_b2 = tag_junto(b2, "reusar", DOWN, buff=0.16, color=C_BUENO)
        self.play(Indicate(VGroup(seek, lookup), color=C_BUENO,
                           scale_factor=1.08),
                  GrowFromEdge(b2, DOWN), FadeIn(et_b2), run_time=0.9)
        cont.fijar(2)
        self.wait(1.6)

        # --- tercera ejecucion: OTRO valor, mismo plan guardado --------------
        self.play(FadeOut(q2), run_time=0.4)
        q3 = S.codigo(["EXEC busca_cliente", "  @id = 1"], font_size=20)
        q3.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(q3, shift=RIGHT * 0.2), run_time=0.6)
        # el valor cambio: se subraya SOLO ese glifo, dentro del panel (sin
        # rectangulo que monte el borde). lineas[1] sin espacios: "@id=1",
        # el ultimo glifo (indice 4) es el "1".
        valor = q3.lineas[1][4:5]
        subrayado = Line(valor.get_corner(DOWN + LEFT),
                         valor.get_corner(DOWN + RIGHT),
                         stroke_color=C_TITULO, stroke_width=2.5)
        subrayado.shift(DOWN * 0.05)
        self.play(Create(subrayado), run_time=0.4)
        et_otro = tag_junto(q3, "otro valor", DOWN, buff=0.2, color=C_TENUE)
        self.play(FadeIn(et_otro), run_time=0.4)
        self.wait(1.2)

        b3 = barra_ejecucion(xs[2], 0.55, C_BUENO)
        et_b3 = tag_junto(b3, "reusar", DOWN, buff=0.16, color=C_BUENO)
        self.play(Indicate(VGroup(seek, lookup), color=C_BUENO,
                           scale_factor=1.08),
                  GrowFromEdge(b3, DOWN), FadeIn(et_b3), run_time=0.9)
        cont.fijar(3)
        self.wait(11.5)
