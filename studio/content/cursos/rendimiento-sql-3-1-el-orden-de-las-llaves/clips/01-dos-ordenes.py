class Clip1(Scene):
    """3.1.1 - Dos listas ordenadas de la misma tabla: por (fecha, estatus)
    los estatus se mezclan dentro de cada dia; por (estatus, fecha) el
    mismo estatus queda junto, y dentro, ordenado por fecha. Solo la idea:
    sin cifras. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Dos ordenes de la tabla"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        leyenda = leyenda_estatus()
        leyenda.move_to(UP * 2.45)
        self.play(FadeIn(leyenda), run_time=0.7)
        self.wait(2.2)

        top_y = 1.35
        dims = dict(ancho=1.8, alto=0.24, buff=0.05, sep_grupo=0.2)

        # --- izquierda: por (fecha, estatus) -------------------------------
        grupos_izq = [
            ["entregado", "cancelado", "entregado"],
            ["entregado", "pendiente", "cancelado"],
            ["cancelado", "entregado", "enviado"],
            ["entregado", "cancelado", "entregado"],
        ]
        col_izq, bloques_izq = lista_indice(grupos_izq, **dims)
        col_izq.move_to(LEFT * 3.4)
        col_izq.shift(UP * (top_y - col_izq.get_top()[1]))

        self.play(LaggedStart(*[FadeIn(b, shift=RIGHT * 0.2)
                                for b in bloques_izq], lag_ratio=0.25),
                  run_time=1.8)
        tag_izq = tag_junto(col_izq, "orden: fecha, estatus", UP, buff=0.3)
        self.play(FadeIn(tag_izq), run_time=0.5)
        self.wait(2.0)

        marco_dia = SurroundingRectangle(bloques_izq[1], color=C_TITULO,
                                         buff=0.06, stroke_width=2.0)
        et_dia = tag_junto(marco_dia, "mismo dia, distinto estatus", RIGHT,
                           buff=0.4)
        self.play(Create(marco_dia), run_time=0.6)
        self.play(FadeIn(et_dia), run_time=0.4)
        self.wait(3.2)

        # --- derecha: por (estatus, fecha) ---------------------------------
        grupos_der = [
            ["pendiente"],
            ["enviado"],
            ["entregado", "entregado", "entregado", "entregado",
             "entregado", "entregado"],
            ["cancelado", "cancelado", "cancelado", "cancelado"],
        ]
        col_der, bloques_der = lista_indice(grupos_der, **dims)
        col_der.move_to(RIGHT * 3.4)
        col_der.shift(UP * (top_y - col_der.get_top()[1]))

        self.play(LaggedStart(*[FadeIn(b, shift=LEFT * 0.2)
                                for b in bloques_der], lag_ratio=0.25),
                  run_time=1.8)
        tag_der = tag_junto(col_der, "orden: estatus, fecha", UP, buff=0.3)
        self.play(FadeIn(tag_der), run_time=0.5)
        self.wait(1.4)

        marco_canc = SurroundingRectangle(bloques_der[3], color=C_TITULO,
                                          buff=0.06, stroke_width=2.0)
        et_canc = tag_junto(marco_canc, "mismo estatus, distinta fecha",
                            LEFT, buff=0.4)
        self.play(Create(marco_canc), run_time=0.6)
        self.play(FadeIn(et_canc), run_time=0.4)
        self.wait(12.0)
