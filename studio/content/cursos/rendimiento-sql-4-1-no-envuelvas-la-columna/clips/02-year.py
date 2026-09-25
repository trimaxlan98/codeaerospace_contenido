class Clip2(Scene):
    """4.1.2 - YEAR(fecha_pedido) envuelve la columna: el motor ya no puede
    entrar al indice por un rango y lo recorre entero (la lista se enciende
    en rojo). El duelo final compara ese recorrido completo contra lo que
    costaria si el predicado fuera un rango sobre la misma columna. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("YEAR() lee todo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        linea_year = "WHERE YEAR(fecha_pedido) = 2025"
        q = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      linea_year], font_size=20)
        q.move_to(UP * 1.95)
        i, j = pos_sin_espacios(linea_year, "YEAR(")
        q.lineas[2][i:j].set_color(C_MALO)
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.8)
        self.wait(0.6)
        envuelta = tag_junto(q, "columna envuelta", DOWN, buff=0.22,
                             color=C_MALO)
        self.play(FadeIn(envuelta), run_time=0.4)
        self.wait(2.0)

        fila = fila_indice(ancho=11.0, alto=1.0)
        fila.move_to(DOWN * 0.5)
        self.play(LaggedStart(*[FadeIn(seg, shift=UP * 0.12) for seg in fila],
                              lag_ratio=0.1), run_time=1.6)
        self.wait(0.8)

        self.play(LaggedStart(*[seg.animate.set_fill(C_MALO, 0.85)
                                .set_stroke(C_MALO) for seg in fila],
                              lag_ratio=0.1), run_time=1.8)
        cada_entrada = tag_junto(fila, "YEAR en cada entrada", UP, buff=0.24,
                                 color=C_MALO)
        self.play(FadeIn(cada_entrada), run_time=0.5)
        self.wait(2.2)

        self.play(FadeOut(fila), FadeOut(cada_entrada), run_time=0.7)
        self.wait(0.3)

        largo = 8.0
        maximo = M["year_scan"]
        base_x = LEFT * 4.4

        bar_rojo = S.barra_lecturas(M["year_scan"], maximo, largo=largo,
                                    alto=0.55, color=C_MALO, log=True)
        bar_rojo.shift(base_x + UP * 0.6)
        bar_verde = S.barra_lecturas(M["year_rango"], maximo, largo=largo,
                                     alto=0.55, color=C_BUENO, log=True)
        bar_verde.shift(base_x + DOWN * 0.6)

        base = Line(base_x + UP * 1.15, base_x + DOWN * 1.15,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_r = tag_junto(bar_rojo, "indice completo", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_rojo, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_motor(lecturas(M["year_scan"]))
        tag_r.next_to(bar_rojo, RIGHT, buff=0.22)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(1.8)

        lab_v = tag_junto(bar_verde, "solo el rango", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(M["year_rango"]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.22)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(2.0)

        rot.mostrar(cifra_pie(f"{S.miles(RANGO_2025)} filas de 2025"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_rojo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(9.0)
