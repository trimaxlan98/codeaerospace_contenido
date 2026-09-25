class Clip4(Scene):
    """6.1.4 - El sesgo no esta en el codigo: esta en el dato. La MISMA
    columna (id_cliente) trae 191 filas para un cliente y 149,970 para
    otro. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El sesgo"), zona="arriba", run_time=0.6)
        self.wait(0.9)

        base_y = -1.3
        alto_max = 2.6
        base = Line(LEFT * 3.6 + UP * base_y, RIGHT * 3.6 + UP * base_y,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.6)
        aviso = tag_junto(base.get_left(), "escala logaritmica", DOWN,
                          buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.8)

        h501 = alto_max * math.log10(C501) / math.log10(C1)
        h1 = alto_max

        bar501 = Rectangle(width=1.6, height=h501, stroke_width=0,
                           fill_color=C_CALCULO, fill_opacity=0.85)
        bar501.move_to(LEFT * 1.9 + UP * base_y, aligned_edge=DOWN)
        bar1 = Rectangle(width=1.6, height=h1, stroke_width=0,
                         fill_color=C_CALCULO, fill_opacity=0.5)
        bar1.move_to(RIGHT * 1.9 + UP * base_y, aligned_edge=DOWN)

        # --- cada barra: su cifra pegada arriba, su nombre mas arriba -----------
        self.play(GrowFromEdge(bar501, DOWN), run_time=0.9)
        cif_501 = tag_hud(f"{S.miles(C501)} filas", font_size=20)
        cif_501.next_to(bar501, UP, buff=0.2)
        et_501 = tag_junto(cif_501, "cliente 501", UP, buff=0.15)
        self.play(FadeIn(cif_501), FadeIn(et_501), run_time=0.5)
        self.wait(1.4)

        self.play(GrowFromEdge(bar1, DOWN), run_time=1.0)
        cif_1 = tag_hud(f"{S.miles(C1)} filas", font_size=20)
        cif_1.next_to(bar1, UP, buff=0.2)
        et_1 = tag_junto(cif_1, "cliente 1", UP, buff=0.15)
        self.play(FadeIn(cif_1), FadeIn(et_1), run_time=0.5)
        self.wait(2.4)

        razon = S.razon(C1, C501)
        rot.mostrar(cifra_pie(f"{S.miles(round(razon))}x mas filas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar501, color=C_CALCULO, scale_factor=1.05),
                  Indicate(bar1, color=C_CALCULO, scale_factor=1.03),
                  run_time=1.0)
        self.wait(3.0)

        grupo = VGroup(base, aviso, bar501, et_501, cif_501, bar1, et_1,
                       cif_1)
        cierre_leccion(self, rot, "El primero que llega",
                       "decide por todos.", grupo, espera=11.0)
