class Clip3(Scene):
    """3.1.3 - El duelo: por (fecha, estatus) hay que recorrer las 418,481
    filas de 2025 completas para separar las canceladas (1,978 lecturas
    medidas); por (estatus, fecha) se salta directo al bloque de
    cancelados y, dentro, al tramo de 2025: 33,275 filas, 161 lecturas.
    (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Cancelado si cambia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        top_y = 1.6

        # --- izquierda: por (fecha, estatus) -------------------------------
        # 2025 completo: casi todo entregado, con cancelados dispersos.
        secuencia_izq = [
            "entregado", "entregado", "enviado", "entregado", "entregado",
            "cancelado", "entregado", "pendiente", "entregado", "entregado",
            "entregado", "enviado", "entregado", "entregado", "cancelado",
            "entregado", "entregado", "pendiente", "entregado", "entregado",
        ]
        col_izq, _ = lista_indice([secuencia_izq], resaltado="cancelado",
                                  ancho=1.4, alto=0.14, buff=0.025)
        col_izq.move_to(LEFT * 2.6)
        col_izq.shift(UP * (top_y - col_izq.get_top()[1]))
        tag_izq = tag_junto(col_izq, "orden: fecha, estatus", UP, buff=0.3)

        self.play(FadeIn(col_izq, shift=RIGHT * 0.2), run_time=1.4)
        self.play(FadeIn(tag_izq), run_time=0.5)
        self.wait(1.8)

        corchete_izq = corchete(col_izq, lado="izquierda")
        tag_2025 = tag_hud(f"{S.miles(FILAS_2025)} en 2025", font_size=22)
        tag_2025.next_to(corchete_izq, LEFT, buff=0.15)
        self.play(Create(corchete_izq), FadeIn(tag_2025), run_time=0.8)
        self.wait(2.2)

        lec_izq = tag_motor(lecturas(LEC_FE), font_size=22)
        lec_izq.next_to(col_izq, DOWN, buff=0.3)
        self.play(FadeIn(lec_izq), run_time=0.5)
        self.wait(2.0)

        # --- derecha: por (estatus, fecha) ---------------------------------
        # salto por encima de pendiente/enviado/entregado (una franja tenue),
        # el bloque de cancelados (otros anios arriba y abajo) y, en medio,
        # el tramo de 2025 (resaltado).
        skip = Rectangle(width=1.4, height=0.3, stroke_width=1.0,
                         stroke_color=C_TENUE, fill_color=C_TENUE,
                         fill_opacity=0.10)
        arriba = VGroup(*[fila_indice("cancelado", 1.4, 0.14)
                          for _ in range(2)]).arrange(DOWN, buff=0.025)
        bloque_2025 = VGroup(*[fila_indice("cancelado", 1.4, 0.14,
                                           resaltar=True)
                               for _ in range(6)]).arrange(DOWN, buff=0.025)
        abajo = VGroup(*[fila_indice("cancelado", 1.4, 0.14)
                         for _ in range(2)]).arrange(DOWN, buff=0.025)
        col_der = VGroup(skip, arriba, bloque_2025, abajo)
        col_der.arrange(DOWN, buff=0.14)
        col_der.move_to(RIGHT * 2.2)
        col_der.shift(UP * (top_y - col_der.get_top()[1]))
        tag_der = tag_junto(col_der, "orden: estatus, fecha", UP, buff=0.3)

        et_skip = tag_junto(skip, "otros estatus", RIGHT, buff=0.25,
                            font_size=16)

        self.play(FadeIn(col_der, shift=LEFT * 0.2), run_time=1.4)
        self.play(FadeIn(tag_der), FadeIn(et_skip), run_time=0.6)
        self.wait(1.4)

        corchete_der = corchete(bloque_2025, lado="derecha")
        tag_canc = tag_hud(f"{S.miles(FILAS_2025_CANC)} cancelados",
                           font_size=22)
        tag_canc.next_to(corchete_der, RIGHT, buff=0.15)
        self.play(Create(corchete_der), FadeIn(tag_canc), run_time=0.8)
        self.wait(1.6)

        lec_der = tag_motor(lecturas(LEC_EF), font_size=22)
        lec_der.move_to(RIGHT * 2.2 + UP * lec_izq.get_y())
        self.play(FadeIn(lec_der), run_time=0.5)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"{round(RAZON_LEC)}x menos lecturas"),
                    zona="abajo", run_time=0.5)
        self.wait(9.0)
