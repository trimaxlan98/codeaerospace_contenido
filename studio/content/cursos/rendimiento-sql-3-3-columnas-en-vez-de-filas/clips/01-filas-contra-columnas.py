class Clip1(Scene):
    """3.3.1 - La misma tabla de detalle guardada por filas (cada pagina
    mezcla las 4 columnas) y por columnas (cada segmento es una sola
    columna). Una suma solo necesita 2 columnas: por filas hay que abrir
    todo; por columnas, solo 2 de 4 segmentos. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Filas contra columnas"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        q = S.codigo(["SELECT SUM(cantidad * precio_unitario)",
                      "FROM detalle_pedido"], font_size=20)
        q.move_to(UP * 2.1)
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.7)
        self.wait(1.0)

        marca = SurroundingRectangle(q.lineas[0], color=C_BUENO, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marca), run_time=0.6)
        et_dos_cols = tag_junto(q, "solo 2 columnas", DOWN, buff=0.2,
                                color=C_BUENO)
        self.play(FadeIn(et_dos_cols), run_time=0.4)
        self.wait(1.8)

        colores = {"cantidad": C_BUENO, "precio_unitario": C_BUENO,
                  "id_pedido": C_TENUE, "id_producto": C_TENUE}

        # --- por filas (izquierda): un punado de paginas abstractas ------
        et_filas = Text("por filas", font_size=24, color=C_TITULO)
        et_filas.move_to(LEFT * 3.5 + UP * 0.95)
        self.play(FadeIn(et_filas), run_time=0.4)

        filas_ico = [S.pagina(0.55, 0.72, renglones=4, color=C_TENUE,
                              relleno=0.12) for _ in range(4)]
        muro = VGroup(VGroup(*filas_ico[:2]).arrange(RIGHT, buff=0.22),
                     VGroup(*filas_ico[2:]).arrange(RIGHT, buff=0.22))
        muro.arrange(DOWN, buff=0.22)
        muro.next_to(et_filas, DOWN, buff=0.32)
        self.play(LaggedStart(*[FadeIn(p, scale=0.7) for p in filas_ico],
                              lag_ratio=0.1), run_time=1.2)
        self.wait(0.8)

        fila_ej = fila_registro(colores, alto=0.5, fs=20)
        fila_ej.next_to(muro, DOWN, buff=0.4)
        self.play(FadeIn(fila_ej, shift=UP * 0.2), run_time=0.8)
        self.wait(1.2)
        et_mezcla = tag_junto(fila_ej, "una pagina, 4 columnas", DOWN,
                              buff=0.22)
        self.play(FadeIn(et_mezcla), run_time=0.4)
        self.wait(1.8)

        # --- por columnas (derecha): un segmento por columna -------------
        et_cols = Text("por columnas", font_size=24, color=C_TITULO)
        et_cols.move_to(RIGHT * 3.5 + UP * 0.95)
        self.play(FadeIn(et_cols), run_time=0.4)

        fila1 = VGroup(segmento_columna("id_pedido", C_TENUE, alto=1.1, fs=20),
                       segmento_columna("id_producto", C_TENUE, alto=1.1, fs=20))
        fila1.arrange(RIGHT, buff=0.3)
        fila2 = VGroup(segmento_columna("cantidad", C_BUENO, alto=1.1, fs=20),
                       segmento_columna("precio_unitario", C_BUENO, alto=1.1, fs=20))
        fila2.arrange(RIGHT, buff=0.3)
        grid = VGroup(fila1, fila2).arrange(DOWN, buff=0.3)
        grid.next_to(et_cols, DOWN, buff=0.32)
        self.play(LaggedStart(*[FadeIn(s, shift=UP * 0.15)
                                for s in [*fila1, *fila2]], lag_ratio=0.15),
                  run_time=1.4)
        self.wait(1.2)
        et_dos = tag_junto(fila2, "2 de 4 columnas", DOWN, buff=0.26,
                           color=C_BUENO)
        self.play(FadeIn(et_dos), run_time=0.4)
        self.wait(2.0)

        # --- se ejecuta la suma: cuanto tiene que abrir cada almacen -----
        self.play(*[p.animate.set_fill(C_MALO, 0.75).set_stroke(C_MALO)
                    for p in filas_ico], run_time=1.0)
        et_todo = tag_junto(muro, "abre todas", RIGHT, buff=0.3, color=C_MALO)
        self.play(FadeIn(et_todo), run_time=0.4)
        self.wait(1.6)

        self.play(fila2[0].caja.animate.set_fill(C_BUENO, 0.6)
                 .set_stroke(C_BUENO, width=2.6),
                 fila2[1].caja.animate.set_fill(C_BUENO, 0.6)
                 .set_stroke(C_BUENO, width=2.6), run_time=1.0)
        self.wait(6.5)
