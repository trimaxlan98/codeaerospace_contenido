class Clip2(Scene):
    """7.1.2 - La regresion: la misma consulta del sesgo de 6.1 compilo dos
    planes en momentos distintos, y Query Store guardo las lecturas de cada
    uno por intervalo. Con el plan A (scan) el mayorista paga 22,363; en
    cuanto entra el plan B (seek + lookup), paga 459,555. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La regresion"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        q = S.codigo(["EXEC usp_PedidosCliente @id"], font_size=20)
        q.to_edge(UP, buff=1.3)
        self.play(FadeIn(q, shift=DOWN * 0.2), run_time=0.6)
        et_q = tag_junto(q, "la misma consulta", DOWN, buff=0.2)
        self.play(FadeIn(et_q), run_time=0.4)
        self.wait(1.4)
        self.play(FadeOut(et_q), run_time=0.3)

        # --- plan A: un scan completo --------------------------------------
        pa = plan_a(pos=LEFT * 3.4 + UP * 0.05)
        et_pa = tag_junto(pa, "plan A", DOWN, buff=0.28)
        self.play(FadeIn(pa, shift=UP * 0.15), FadeIn(et_pa), run_time=0.7)
        self.wait(1.2)

        # --- plan B: seek + lookup, de derecha a izquierda -----------------
        pb = plan_b(pos=RIGHT * 3.3 + UP * 0.05)
        et_pb = tag_junto(pb, "plan B", DOWN, buff=0.28)
        self.play(FadeIn(pb.seek, shift=UP * 0.15), run_time=0.5)
        self.play(Create(pb.flecha), FadeIn(pb.lookup, shift=UP * 0.15),
                  run_time=0.7)
        self.play(FadeIn(et_pb), run_time=0.4)
        self.wait(1.8)

        grupo_planes = VGroup(q, pa, et_pa, pb, et_pb)
        self.play(FadeOut(grupo_planes), run_time=0.7)

        # --- la linea de tiempo: el salto cuando entra el plan B -----------
        eje, xs = eje_intervalos(6, ancho=10.2, y=-1.7)
        self.play(Create(eje), run_time=0.7)
        aviso = tag_junto(eje, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.7)

        barras = VGroup()
        for i, x in enumerate(xs):
            valor = SNIFF_A if i < 3 else SNIFF_B
            color = C_BUENO if i < 3 else C_MALO
            h = alto_log(valor)
            b = barra_intervalo(h, color)
            b.move_to([x, -1.7 + h / 2, 0])
            barras.add(b)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras],
                              lag_ratio=0.12), run_time=2.4)
        self.wait(0.6)

        medio = (xs[2] + xs[3]) / 2
        corte = DashedLine([medio, -1.9, 0], [medio, 2.0, 0], dash_length=0.1,
                           stroke_color=C_TENUE, stroke_width=2.2)
        self.play(Create(corte), run_time=0.5)
        et_corte = tag_junto(corte, "entra el plan B", UP, buff=0.2)
        self.play(FadeIn(et_corte), run_time=0.4)
        self.wait(1.2)

        tag_verde = tag_motor(lecturas(SNIFF_A))
        tag_verde.next_to(barras[1], UP, buff=0.2)
        self.play(FadeIn(tag_verde), run_time=0.4)
        self.wait(1.2)

        tag_roja = tag_motor(lecturas(SNIFF_B))
        tag_roja.next_to(barras[4], UP, buff=0.2)
        self.play(FadeIn(tag_roja), run_time=0.4)
        self.wait(1.4)

        razon = S.razon(SNIFF_B, SNIFF_A)
        rot.mostrar(cifra_pie(f"{round(razon)}x mas lecturas"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(barras[4], color=C_MALO, scale_factor=1.05),
                  run_time=0.8)
        self.wait(8.5)
