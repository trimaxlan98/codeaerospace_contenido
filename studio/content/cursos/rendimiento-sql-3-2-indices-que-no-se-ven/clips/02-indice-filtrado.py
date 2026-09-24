class Clip2(Scene):
    """3.2.2 - Un indice filtrado solo guarda las filas pendientes: mucho
    mas chico que un indice completo sobre fecha, que tendria que guardar
    la tabla entera (sin inventar su tamano: basta el dibujo). El arbol
    filtrado cabe en pocas paginas y la consulta lee casi todas. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Un indice filtrado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["CREATE INDEX IX_pendientes ON pedidos",
                      "(fecha_pedido) WHERE estatus = 'pendiente'"],
                     font_size=19)
        q.move_to(UP * 2.15)
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.8)
        marca = SurroundingRectangle(q.lineas[1], color=C_INDICE, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marca), run_time=0.6)
        self.wait(2.4)

        # --- divisoria: la misma tabla, dos formas de indexarla ------------
        divisoria = DashedLine(UP * 1.35, DOWN * 2.55,
                              dash_length=0.1, stroke_color=C_TENUE,
                              stroke_width=1.6)
        self.play(Create(divisoria), run_time=0.6)

        # --- izquierda: un indice completo sobre fecha (todo el muro) -----
        muro = S.MuroPaginas(columnas=20, filas=10, lado=0.21, sep=0.05,
                             color=C_INDICE, opacidad=0.14)
        muro.move_to(LEFT * 3.7 + DOWN * 0.9)
        tag_completo = tag_junto(muro, "indice completo", UP, buff=0.25,
                                 color=C_INDICE)
        self.play(FadeIn(muro), run_time=1.1)
        self.play(FadeIn(tag_completo), run_time=0.4)
        self.wait(2.4)

        # --- derecha: el indice filtrado, un arbol pequeno -----------------
        arbol = S.ArbolB(anchos=(1, 3, 10), ancho=4.4, alto=3.0, lado=0.34,
                         color=C_INDICE)
        arbol.move_to(RIGHT * 3.7 + DOWN * 0.9)
        self.play(FadeIn(arbol.niveles[0]), run_time=0.4)
        self.play(Create(arbol.aristas[:3]), FadeIn(arbol.niveles[1]), run_time=0.5)
        self.play(Create(arbol.aristas[3:]), FadeIn(arbol.niveles[2]), run_time=0.6)
        tag_filtrado = tag_junto(arbol, "indice filtrado", UP, buff=0.25,
                                 color=C_INDICE)
        self.play(FadeIn(tag_filtrado), run_time=0.4)
        self.wait(2.2)

        pag_tag = tag_motor(f"{S.miles(M['pendientes_paginas'])} paginas")
        pag_tag.next_to(arbol, DOWN, buff=0.32)
        self.play(FadeIn(pag_tag), run_time=0.5)
        self.wait(3.0)

        rot.mostrar(motor_pie(lecturas(M["pendientes_lecturas"])),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(arbol, color=C_INDICE, scale_factor=1.06),
                  run_time=1.0)
        self.wait(10.4)
