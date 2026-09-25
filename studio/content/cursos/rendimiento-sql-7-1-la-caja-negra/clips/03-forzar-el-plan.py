class Clip3(Scene):
    """7.1.3 - Sin tocar el codigo: sp_query_store_force_plan pone un
    candado sobre el plan A y las lecturas del mayorista vuelven a 22,363
    en cada intervalo, aunque el plan B siga guardado. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Forzar el plan"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        cod = S.codigo(["EXEC sp_query_store_force_plan",
                       "  @query_id, @plan_id"], font_size=19)
        cod.to_edge(UP, buff=1.25)
        self.play(FadeIn(cod, shift=DOWN * 0.2), run_time=0.7)
        et_cod = tag_junto(cod, "sin tocar el codigo", DOWN, buff=0.22)
        self.play(FadeIn(et_cod), run_time=0.4)
        self.wait(1.8)

        pa = plan_a(pos=LEFT * 3.3 + UP * 0.05)
        pb = plan_b(pos=RIGHT * 3.2 + UP * 0.05)
        et_pa = tag_junto(pa, "plan A", DOWN, buff=0.26)
        et_pb = tag_junto(pb, "plan B", DOWN, buff=0.26)
        self.play(FadeIn(pa), FadeIn(pb.seek), run_time=0.6)
        self.play(Create(pb.flecha), FadeIn(pb.lookup), run_time=0.6)
        self.play(FadeIn(et_pa), FadeIn(et_pb), run_time=0.4)
        self.wait(1.4)

        c = candado(pos=pa.get_top() + UP * 0.32, color=C_BUENO)
        self.play(FadeIn(c, shift=DOWN * 0.15), run_time=0.6)
        et_c = tag_junto(c, "plan forzado", UP, buff=0.18, color=C_BUENO)
        self.play(FadeIn(et_c), run_time=0.4)
        self.play(pb.animate.set_opacity(0.25), et_pb.animate.set_opacity(0.35),
                  run_time=0.6)
        self.wait(1.6)

        grupo = VGroup(cod, et_cod, pa, pb, et_pa, et_pb, c, et_c)
        self.play(FadeOut(grupo), run_time=0.7)

        # --- la linea de tiempo: vuelve a 22,363 en cada intervalo ---------
        eje, xs = eje_intervalos(6, ancho=10.2, y=-1.5)
        self.play(Create(eje), run_time=0.7)
        aviso = tag_junto(eje, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        barras = VGroup()
        for i, x in enumerate(xs):
            valor = SNIFF_B if i < 2 else SNIFF_A
            color = C_MALO if i < 2 else C_BUENO
            h = alto_log(valor)
            b = barra_intervalo(h, color)
            b.move_to([x, -1.5 + h / 2, 0])
            barras.add(b)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras],
                              lag_ratio=0.12), run_time=2.2)
        self.wait(0.6)

        medio = (xs[1] + xs[2]) / 2
        corte = DashedLine([medio, -1.7, 0], [medio, 1.6, 0], dash_length=0.1,
                           stroke_color=C_BUENO, stroke_width=2.2)
        self.play(Create(corte), run_time=0.5)
        et_corte = tag_junto(corte, "se fuerza aqui", UP, buff=0.2,
                             color=C_BUENO)
        self.play(FadeIn(et_corte), run_time=0.4)
        self.wait(1.2)

        tag_v = tag_motor(lecturas(SNIFF_A))
        tag_v.next_to(barras[4], UP, buff=0.2)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(1.4)

        et_final = tag_junto(barras, "mismo plan, cada vez", DOWN, buff=0.9)
        self.play(FadeIn(et_final), run_time=0.5)
        self.play(*[Indicate(b, color=C_BUENO, scale_factor=1.06)
                   for b in barras[2:]], run_time=1.0)
        self.wait(9.0)
