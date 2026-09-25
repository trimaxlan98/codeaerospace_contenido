class Clip2(Scene):
    """6.2.2 - OPTIMIZE FOR: se compila UNA sola vez, fijando el valor
    'tipico' (501). Ese plan queda guardado y se reusa para TODOS, incluso
    cuando llega el mayorista: bueno para la mayoria, muy caro para el
    mayorista. Reutiliza la medicion del sniffing 501-luego-1 porque es
    matematicamente el MISMO plan forzado. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Fijar un valor tipico"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        q = S.codigo(["SELECT id_pedido, total",
                      "FROM pedidos",
                      "WHERE id_cliente = @id_cliente",
                      "OPTION (OPTIMIZE FOR (@id_cliente = 501))"],
                     font_size=17)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.6)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        marco = SurroundingRectangle(q.lineas[3], color=C_TITULO, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marco), run_time=0.6)
        self.wait(0.9)

        # --- fila unica, BIEN por debajo del panel de codigo (la ultima
        # linea es larga y ensancha el panel) --------------------------------
        y0 = -0.55
        x_cli, x_op, x_may = -3.9, 0.2, 4.1

        # --- se compila UNA vez, con 501 como valor tipico ------------------
        cliente501 = caja_cliente("501", color=C_BUENO, ancho=1.4)
        cliente501.move_to(RIGHT * x_cli + UP * y0)
        et_tip = tag_junto(cliente501, "valor tipico", UP, buff=0.2,
                           color=C_BUENO)
        self.play(FadeIn(cliente501), FadeIn(et_tip), run_time=0.6)
        self.wait(0.6)

        op1 = S.operador("Seek + Lookup", color=C_BUENO, ancho=2.8, alto=0.85,
                         font_size=22)
        op1.move_to(RIGHT * x_op + UP * y0)
        fl1 = Arrow(cliente501.get_right(), op1.get_left(), buff=0.1,
                   stroke_width=2.2, color=C_BUENO,
                   max_tip_length_to_length_ratio=0.22)
        self.play(Create(fl1), FadeIn(op1, shift=LEFT * 0.15), run_time=0.7)
        et_guarda = tag_junto(op1, "queda guardado", DOWN, buff=0.22)
        self.play(FadeIn(et_guarda), run_time=0.4)
        rot.mostrar(motor_pie(lecturas(OPTFOR_501)), zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- llega el mayorista: mismo plan, forzado ------------------------
        self.play(FadeOut(et_guarda), run_time=0.3)
        mayorista = caja_cliente("mayorista", color=C_TENUE, ancho=2.3)
        mayorista.move_to(RIGHT * x_may + UP * y0)
        et_may = tag_junto(mayorista, "el mayorista", UP, buff=0.2)
        self.play(FadeIn(mayorista), FadeIn(et_may), run_time=0.6)
        self.wait(0.5)

        fl2 = Arrow(mayorista.get_left(), op1.get_right(), buff=0.1,
                   stroke_width=2.2, color=C_TENUE,
                   max_tip_length_to_length_ratio=0.22)
        self.play(Create(fl2), run_time=0.6)
        et_mismo = tag_junto(fl2, "mismo plan", DOWN, buff=0.2)
        self.play(FadeIn(et_mismo), run_time=0.4)
        rot.mostrar(motor_pie(lecturas(OPTFOR_1)), zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el duelo: bueno para uno, carisimo para el otro ----------------
        primero = VGroup(q, marco, cliente501, et_tip, op1, mayorista, et_may,
                         fl1, fl2, et_mismo)
        self.play(FadeOut(primero), run_time=0.7)
        rot.limpiar("abajo", run_time=0.3)

        largo = 7.6
        maximo = OPTFOR_1
        base_x = LEFT * 4.1
        bar_verde = S.barra_lecturas(OPTFOR_501, maximo, largo=largo,
                                     alto=0.55, color=C_BUENO, log=True)
        bar_verde.shift(base_x + UP * 0.9)
        bar_rojo = S.barra_lecturas(OPTFOR_1, maximo, largo=largo,
                                    alto=0.55, color=C_MALO, log=True)
        bar_rojo.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.5)

        lab_v = tag_junto(bar_verde, "tipico", LEFT, buff=0.3, color=C_BUENO)
        lab_r = tag_junto(bar_rojo, "mayorista", LEFT, buff=0.3, color=C_MALO)
        self.play(FadeIn(bar_verde, shift=RIGHT * 0.2), FadeIn(lab_v), run_time=0.8)
        self.wait(0.4)
        self.play(FadeIn(bar_rojo, shift=RIGHT * 0.2), FadeIn(lab_r), run_time=0.8)
        self.wait(1.0)

        tag_v = tag_motor(lecturas(OPTFOR_501))
        tag_v.next_to(bar_verde, RIGHT, buff=0.2)
        tag_r = tag_motor(lecturas(OPTFOR_1))
        tag_r.next_to(bar_rojo, RIGHT, buff=0.2)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(0.5)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(1.8)

        razon = S.razon(OPTFOR_1, OPTFOR_501)
        rot.mostrar(cifra_pie(f"{razon:.0f}x mas caro"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(bar_verde, color=C_BUENO, scale_factor=1.05),
                  Indicate(bar_rojo, color=C_MALO, scale_factor=1.02),
                  run_time=1.0)
        self.wait(6.0)
