class Clip2(Scene):
    """3.3.2 - Los 3,750,000 renglones de detalle_pedido se reparten en 4
    rowgroups de hasta 1,048,576 filas; el ultimo queda parcial. Adentro de
    un rowgroup, un segmento comprimido por columna. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Filas en grupos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        rot.mostrar(dato_pie(f"hasta {S.miles(CAP_RG)} filas"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        anchos_frac = [1.0, 1.0, 1.0, FRAC_ULTIMO]
        ancho_max, alto = 2.5, 2.0
        grupos = VGroup(*[grupo_filas(ancho_max, alto, f) for f in anchos_frac])
        grupos.arrange(RIGHT, buff=0.3, aligned_edge=DOWN)
        grupos.move_to(UP * 0.85)
        self.play(LaggedStart(*[FadeIn(g, shift=UP * 0.2) for g in grupos],
                              lag_ratio=0.2), run_time=1.6)
        self.wait(1.2)

        et_rg = tag_junto(grupos[0], "rowgroup", UP, buff=0.2)
        self.play(FadeIn(et_rg), run_time=0.4)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{S.miles(N_RG)} rowgroups"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        et_ult = tag_hud(f"{S.miles(ULTIMO_RG)} en el ultimo")
        et_ult.next_to(grupos[3], DOWN, buff=0.3)
        self.play(FadeIn(et_ult), run_time=0.5)
        self.wait(3.6)

        # --- adentro de un rowgroup: un segmento por columna --------------
        self.play(FadeOut(et_rg), run_time=0.3)
        marco_zoom = SurroundingRectangle(grupos[0], color=C_TITULO,
                                          buff=0.08, stroke_width=2.0)
        self.play(Create(marco_zoom), run_time=0.6)
        self.wait(1.2)

        segs = VGroup(*[segmento_columna(n, C_INDICE, alto=1.15, fs=18)
                       for n in COLUMNAS])
        segs.arrange(RIGHT, buff=0.24)
        segs.move_to(DOWN * 1.55)
        guia = DashedLine(grupos[0].get_bottom(), segs.get_top(),
                          dash_length=0.09, stroke_color=C_TITULO,
                          stroke_width=1.6)
        self.play(Create(guia), LaggedStart(*[FadeIn(s, shift=UP * 0.15)
                                              for s in segs], lag_ratio=0.12),
                  run_time=1.4)
        self.wait(1.0)
        et_comp = tag_junto(segs, "comprimido", DOWN, buff=0.26)
        self.play(FadeIn(et_comp), run_time=0.4)
        self.wait(8.5)
