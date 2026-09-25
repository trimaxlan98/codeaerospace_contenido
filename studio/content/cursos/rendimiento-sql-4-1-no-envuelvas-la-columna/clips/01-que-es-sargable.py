class Clip1(Scene):
    """4.1.1 - Que es sargable: el indice ordenado por fecha_pedido se ve
    como una fila de anios (ancho real, calculado, CADA UNO rotulado en
    zigzag para que quepan). Un predicado de rango marca dos limites sobre
    la lista y enciende el tramo de en medio en verde: un SARG, un
    argumento de busqueda que el motor puede usar como rango en vez de
    recorrer todo. Codigo y franja centrados como un solo bloque. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Que es sargable"), zona="arriba",
                    run_time=0.6)
        self.wait(0.9)

        fila = fila_indice(ancho=11.0, alto=1.15)
        fila.move_to(ORIGIN)

        q = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      "WHERE fecha_pedido >= '2025-01-01'",
                      "  AND fecha_pedido <  '2026-01-01'"], font_size=20)
        q.next_to(fila, UP, buff=0.55)

        # --- un rotulo por anio, en ZIGZAG (dos alturas) para que no se
        # encimen entre franjas angostas y anchas ------------------------
        labels = VGroup()
        for idx, a in enumerate(ANIOS):
            buff = 0.22 if idx % 2 == 0 else 0.68
            labels.add(tag_junto(fila.anios[a], str(a), DOWN, buff=buff,
                                 font_size=22))

        bloque = VGroup(q, fila, labels)
        bloque.move_to(ORIGIN)

        self.play(LaggedStart(*[FadeIn(seg, shift=UP * 0.15) for seg in fila],
                              lag_ratio=0.12), run_time=1.8)
        self.wait(0.6)
        self.play(LaggedStart(*[FadeIn(t) for t in labels], lag_ratio=0.1),
                  run_time=0.9)
        self.wait(1.2)

        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.8)
        self.wait(3.4)

        seg = fila.anios[2025]
        marca_izq = Line(seg.get_left() + UP * 0.85, seg.get_left() + DOWN * 0.85,
                         stroke_color=C_BUENO, stroke_width=4)
        marca_der = Line(seg.get_right() + UP * 0.85, seg.get_right() + DOWN * 0.85,
                         stroke_color=C_BUENO, stroke_width=4)
        self.play(Create(marca_izq), run_time=0.5)
        self.wait(0.4)
        self.play(Create(marca_der), run_time=0.5)
        self.wait(0.7)

        self.play(seg.animate.set_fill(C_BUENO, 0.85).set_stroke(C_BUENO),
                  run_time=0.9)
        sarg = tag_junto(seg, "SARG", UP, buff=0.24, color=C_BUENO)
        self.play(FadeIn(sarg, shift=DOWN * 0.15), run_time=0.5)
        self.wait(2.2)

        # cifra cian del propio 2025, UNA sola vez y como tag junto a la
        # franja (en el clip 2 la misma cuenta va en el pie, no aqui)
        filas2025 = tag_hud(f"{S.miles(RANGO_2025)} filas", font_size=19)
        filas2025.next_to(seg, DOWN, buff=0.95)
        self.play(FadeIn(filas2025), run_time=0.5)
        self.wait(2.8)

        self.play(Indicate(seg, color=C_BUENO, scale_factor=1.05), run_time=1.0)
        self.wait(11.0)
