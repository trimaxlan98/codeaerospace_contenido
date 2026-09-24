class Clip1(Scene):
    """2.3.1 - El indice delgado (id_cliente + id_pedido) engorda: tres
    columnas de la tabla bajan y se pegan a la hoja. Una cuarta
    (comentarios) se queda arriba, sin bajar: la semilla del clip 4. El
    codigo aparece DESPUES de resuelta la caida, para que nunca comparta
    fotograma con las celdas en movimiento. Sin cifras. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La hoja engorda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- arriba: cuatro columnas candidatas, tenues (toda la fila,
        # ancho completo: todavia no hay panel de codigo en pantalla) ------
        candidatas = ["fecha_pedido", "estatus", "total", "comentarios"]
        arriba = fila_de([celda_campo(n, color=C_TENUE, fs=22, alto=0.8,
                                      relleno=0.08, opacidad_borde=0.7)
                          for n in candidatas], buff=0.35)
        arriba.move_to(UP * 1.75)
        et_arriba = tag_junto(arriba, "en la tabla", UP, buff=0.24)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.15) for c in arriba],
                              lag_ratio=0.15), run_time=1.2)
        self.play(FadeIn(et_arriba), run_time=0.4)
        self.wait(1.2)

        # --- abajo: la hoja delgada (2 celdas) ----------------------------
        hoja = fila_de([celda_campo("id_cliente"), celda_campo("id_pedido")])
        hoja.move_to(DOWN * 1.7)
        et_hoja = tag_junto(hoja, "hoja delgada", DOWN, buff=0.26,
                            color=C_TENUE)
        self.play(FadeIn(hoja, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(et_hoja), run_time=0.4)
        self.wait(1.4)

        # --- tres columnas bajan, una se queda (sin panel de codigo aun,
        # nada con que puedan encimarse) -----------------------------------
        self.play(FadeOut(et_hoja), run_time=0.3)
        for i in range(3):
            origen = arriba[i]
            self.play(origen.caja.animate.set_stroke(C_INDICE, opacity=1.0)
                      .set_fill(C_INDICE, 0.3), run_time=0.4)
            hoja.add(origen)
            objetivo = hoja.copy().arrange(RIGHT, buff=0.1).move_to(DOWN * 1.7)
            self.play(*[c.animate.move_to(t.get_center())
                       for c, t in zip(hoja, objetivo)], run_time=0.8)
            self.wait(0.35)

        et_ancha = tag_junto(hoja, "hoja ancha", DOWN, buff=0.26,
                             color=C_INDICE)
        self.play(FadeIn(et_ancha), run_time=0.4)
        self.wait(1.4)

        # --- comentarios se queda arriba, gris: no bajo -------------------
        self.play(Indicate(arriba[3], color=C_TENUE, scale_factor=1.12),
                  run_time=0.9)
        et_queda = tag_junto(arriba[3], "no esta aqui", DOWN, buff=0.35,
                             color=C_TENUE)
        self.play(FadeIn(et_queda), run_time=0.4)
        self.wait(1.2)

        # --- AHORA el codigo: el piso ya esta quieto ----------------------
        q = S.codigo(["CREATE INDEX ix_cliente",
                      "ON pedidos (id_cliente)",
                      "INCLUDE (fecha_pedido,",
                      "estatus, total)"], font_size=19)
        q.to_corner(UL, buff=0.5).shift(DOWN * 0.5)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        marco_include = SurroundingRectangle(VGroup(q.lineas[2], q.lineas[3]),
                                             color=C_INDICE, buff=0.06,
                                             stroke_width=2.2)
        self.play(Create(marco_include), run_time=0.6)
        self.wait(11.0)
