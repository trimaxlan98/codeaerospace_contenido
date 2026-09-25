class Clip1(Scene):
    """5.2.1 - Con un literal (id_cliente = 1) el optimizador SI conoce el
    valor al compilar: mira el histograma, encuentra la torre exacta del
    cliente 1 (149,970 filas, cian) y con eso elige un scan completo: es
    la opcion correcta para tantas filas. Lecturas medidas: 22,363
    (ambar). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El literal"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- el codigo: el literal resaltado -------------------------------
        q = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      "WHERE id_cliente = 1"], font_size=22)
        q.move_to(LEFT * 3.9 + UP * 1.75)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        linea = "WHERE id_cliente = 1"
        plano = linea.replace(" ", "")
        i = plano.rfind("1")
        marca = SurroundingRectangle(q.lineas[2][i:i + 1], color=C_TITULO,
                                     buff=0.06, stroke_width=2.4)
        self.play(Create(marca), run_time=0.6)
        tag_lit = tag_junto(q, "un valor conocido", DOWN, buff=0.22,
                            color=C_TITULO)
        self.play(FadeIn(tag_lit), run_time=0.4)
        self.wait(2.4)

        # --- el histograma: la torre exacta del cliente 1 ------------------
        base_y = -1.9
        barras = torre_histograma(base_y=base_y, color=C_CREE)
        barras.shift(RIGHT * 2.4)
        base = Line(barras.get_left(), barras.get_right(),
                   stroke_color=C_TENUE, stroke_width=2)
        base.set_y(base_y)
        self.play(Create(base), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b, shift=UP * 0.15) for b in barras],
                              lag_ratio=0.06), run_time=1.8)
        tag_hist = tag_junto(barras, "el histograma", UP, buff=0.3)
        self.play(FadeIn(tag_hist), run_time=0.4)
        self.wait(1.6)

        torre = barras[6]
        self.play(FadeOut(tag_hist), run_time=0.3)
        self.play(torre.animate.set_fill(C_CALCULO, 0.85)
                  .set_stroke(C_CALCULO, width=2.4), run_time=0.6)
        self.play(Indicate(torre, color=C_CALCULO, scale_factor=1.06),
                  run_time=0.8)
        cif_torre = tag_hud(f"{S.miles(C1)} filas", font_size=20)
        cif_torre.next_to(torre, UP, buff=0.28)
        self.play(FadeIn(cif_torre), run_time=0.5)
        tag_cli = tag_junto(torre, "cliente 1", DOWN, buff=0.24,
                            color=C_CALCULO)
        self.play(FadeIn(tag_cli), run_time=0.4)
        self.wait(2.6)

        # --- el plan elegido: un scan completo ------------------------------
        op = S.operador("Scan", color=C_TITULO)
        op.move_to(LEFT * 3.9 + DOWN * 0.7)
        self.play(FadeIn(op, shift=UP * 0.15), run_time=0.6)
        tag_op = tag_junto(op, "plan elegido", DOWN, buff=0.2)
        self.play(FadeIn(tag_op), run_time=0.4)
        self.wait(2.2)

        rot.mostrar(motor_pie(lecturas(LIT)), zona="abajo", run_time=0.5)
        self.play(op.caja.animate.set_stroke(C_TITULO, width=3.2), run_time=0.6)
        self.wait(9.5)
