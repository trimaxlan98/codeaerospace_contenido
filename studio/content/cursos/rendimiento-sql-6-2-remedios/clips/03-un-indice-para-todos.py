class Clip3(Scene):
    """6.2.3 - El remedio de fondo: un indice compuesto (id_cliente,
    fecha_pedido DESC) INCLUDE (...). El MISMO plan (un solo Seek, sin
    lookup ni sort) sirve al 501 (6 lecturas) y al mayorista (1,974): ya no
    importa quien compile primero. Duelo antes/despues para el mayorista:
    459,555 (con el remedio anterior) contra 1,974. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Un indice para todos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["CREATE INDEX ix_cliente_fecha",
                      "ON pedidos (id_cliente, fecha_pedido DESC)",
                      "INCLUDE (estatus, total, comentarios)"], font_size=18)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.55)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        marco = SurroundingRectangle(q.lineas[1], color=C_INDICE, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marco), run_time=0.6)
        self.wait(1.0)

        # --- un solo plan para los dos ---------------------------------
        op = S.operador("Seek", color=C_BUENO, ancho=2.4, alto=0.9,
                        font_size=24)
        op.move_to(DOWN * 1.55)
        et_op = tag_junto(op, "un solo plan", DOWN, buff=0.22, color=C_BUENO)

        c501 = caja_cliente("501", color=C_TENUE, ancho=1.4)
        c501.move_to(LEFT * 3.6 + UP * 0.25)
        et501 = tag_junto(c501, "cliente 501", UP, buff=0.2)

        c1 = caja_cliente("mayorista", color=C_TENUE, ancho=2.3)
        c1.move_to(RIGHT * 3.5 + UP * 0.25)
        et1 = tag_junto(c1, "el mayorista", UP, buff=0.2)

        self.play(FadeIn(c501), FadeIn(et501), FadeIn(c1), FadeIn(et1),
                  run_time=0.7)
        self.wait(0.6)
        self.play(FadeIn(op, shift=UP * 0.15), run_time=0.5)
        self.play(FadeIn(et_op), run_time=0.4)
        self.wait(0.5)

        filas_501 = S.filas_cliente(501)
        filas_1 = S.filas_cliente(1)
        f1 = S.flecha_plan(c501.get_bottom(), op.get_top() + LEFT * 0.5,
                           filas_501, color=C_TENUE)
        f2 = S.flecha_plan(c1.get_bottom(), op.get_top() + RIGHT * 0.5,
                           filas_1, color=C_TENUE)
        self.play(Create(f1), run_time=0.6)
        rot.mostrar(motor_pie(lecturas(IDX_501)), zona="abajo", run_time=0.5)
        self.wait(1.6)
        self.play(Create(f2), run_time=0.6)
        rot.mostrar(motor_pie(lecturas(IDX_1)), zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- el duelo: el mayorista, antes y despues del indice -----------
        primero = VGroup(q, marco, op, et_op, c501, et501, c1, et1, f1, f2)
        self.play(FadeOut(primero), run_time=0.7)
        rot.limpiar("abajo", run_time=0.3)

        largo = 7.6
        maximo = OPTFOR_1
        base_x = LEFT * 4.1
        bar_antes = S.barra_lecturas(OPTFOR_1, maximo, largo=largo,
                                     alto=0.55, color=C_MALO, log=True)
        bar_antes.shift(base_x + UP * 0.9)
        bar_despues = S.barra_lecturas(IDX_1, maximo, largo=largo,
                                       alto=0.55, color=C_BUENO, log=True)
        bar_despues.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.5)

        lab_a = tag_junto(bar_antes, "antes", LEFT, buff=0.3, color=C_MALO)
        lab_d = tag_junto(bar_despues, "despues", LEFT, buff=0.3, color=C_BUENO)
        self.play(FadeIn(bar_antes, shift=RIGHT * 0.2), FadeIn(lab_a),
                  run_time=0.8)
        self.wait(0.4)
        self.play(FadeIn(bar_despues, shift=RIGHT * 0.2), FadeIn(lab_d),
                  run_time=0.8)
        self.wait(1.0)

        tag_a = tag_motor(lecturas(OPTFOR_1))
        tag_a.next_to(bar_antes, RIGHT, buff=0.2)
        tag_d = tag_motor(lecturas(IDX_1))
        tag_d.next_to(bar_despues, RIGHT, buff=0.2)
        self.play(FadeIn(tag_a), run_time=0.4)
        self.wait(0.5)
        self.play(FadeIn(tag_d), run_time=0.4)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"{RAZON_INDICE:.0f}x menos lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_antes, color=C_MALO, scale_factor=1.02),
                  Indicate(bar_despues, color=C_BUENO, scale_factor=1.06),
                  run_time=1.0)
        self.wait(6.5)
