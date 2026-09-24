class Clip4(Scene):
    """3.1.4 - La regla: en un indice compuesto, la columna de IGUALDAD va
    primero y la de RANGO despues. Dentro de la casilla 'estatus' se fija
    UN valor (un punto); dentro de 'fecha_pedido' se recorre un tramo (un
    rango). Se cierra con el CREATE INDEX que arma el duelo del clip
    anterior. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Igualdad primero"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- la llave compuesta: dos casillas grandes -----------------------
        col1 = S.operador("estatus", color=C_INDICE, ancho=3.4, alto=1.9,
                          font_size=32)
        col2 = S.operador("fecha_pedido", color=C_INDICE, ancho=3.4,
                          alto=1.9, font_size=30)
        llave = VGroup(col1, col2).arrange(RIGHT, buff=0.7)
        llave.move_to(UP * 1.45)

        self.play(FadeIn(col1, shift=UP * 0.2), run_time=0.6)
        self.wait(0.4)
        self.play(FadeIn(col2, shift=UP * 0.2), run_time=0.6)
        self.wait(0.6)

        flecha_orden = Arrow(col1.get_right(), col2.get_left(), buff=0.12,
                             stroke_width=3.5, color=C_TENUE,
                             max_tip_length_to_length_ratio=0.2)
        self.play(Create(flecha_orden), run_time=0.5)
        self.wait(0.8)

        # --- por que: en 'estatus' se fija UN valor (un punto) --------------
        valores = list(S.ESTATUS)
        puntos = VGroup(*[Dot(radius=0.13, color=TONOS_ESTATUS[e])
                          for e in valores])
        puntos.arrange(RIGHT, buff=0.42)
        puntos.move_to(col1.get_center() + DOWN * 0.45)
        self.play(FadeIn(puntos), run_time=0.6)
        self.wait(0.8)

        objetivo = puntos[valores.index("cancelado")]
        anillo = Circle(radius=0.27, color=C_MALO, stroke_width=3.4)
        anillo.move_to(objetivo)
        self.play(Create(anillo),
                  *[p.animate.set_opacity(0.25) for p in puntos
                    if p is not objetivo],
                  run_time=0.9)
        self.wait(1.6)

        # --- por que: en 'fecha_pedido' se recorre un RANGO ------------------
        eje = Line(LEFT * 1.15, RIGHT * 1.15, color=C_TENUE, stroke_width=2)
        eje.move_to(col2.get_center() + DOWN * 0.45)
        tramo = Rectangle(width=1.3, height=0.22, stroke_width=0,
                          fill_color=C_INDICE, fill_opacity=0.55)
        tramo.move_to(eje.get_center())
        self.play(Create(eje), run_time=0.5)
        self.play(GrowFromCenter(tramo), run_time=0.8)
        self.wait(1.8)

        et1 = tag_junto(col1, "=", DOWN, buff=0.25, color=C_BUENO,
                        font_size=56)
        et2 = tag_junto(col2, "rango", DOWN, buff=0.25, color=C_INDICE,
                        font_size=30)
        self.play(FadeIn(et1), run_time=0.4)
        self.wait(0.5)
        self.play(FadeIn(et2), run_time=0.4)
        self.wait(1.6)

        # --- el codigo: el indice real del clip anterior --------------------
        q = S.codigo(["CREATE INDEX ix_cancelados",
                      "ON pedidos",
                      "(estatus, fecha_pedido)"], font_size=22)
        q.move_to(DOWN * 2.05)
        self.play(FadeIn(q, shift=UP * 0.2), run_time=0.7)
        self.wait(1.2)

        linea = q.lineas[2]
        marca_eq = SurroundingRectangle(linea[1:8], color=C_BUENO,
                                        buff=0.03, stroke_width=2.2)
        marca_rango = SurroundingRectangle(linea[9:21], color=C_INDICE,
                                           buff=0.03, stroke_width=2.2)
        self.play(Create(marca_eq), run_time=0.6)
        self.wait(0.9)
        self.play(Create(marca_rango), run_time=0.6)
        self.wait(3.2)

        cierre_leccion(self, rot, "El orden de las llaves importa.",
                       "Igualdad primero, rango despues.",
                       llave, flecha_orden, puntos, anillo, eje, tramo,
                       et1, et2, q, marca_eq, marca_rango, espera=5.5)
