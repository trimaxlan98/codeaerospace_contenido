class Clip1(Scene):
    """7.1.1 - Que es Query Store: cada consulta que corre queda grabada,
    con sus planes y sus metricas, repartida en intervalos de tiempo (como
    la caja negra de un avion). Introduce el mecanismo sin cifras: las
    lecturas reales llegan en el clip 2. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Query Store"), zona="arriba", run_time=0.6)
        self.wait(1.0)

        marco = RoundedRectangle(width=11.6, height=5.0, corner_radius=0.28,
                                 stroke_color=C_TENUE, stroke_width=2.2,
                                 fill_color=C_TENUE, fill_opacity=0.04)
        marco.move_to(DOWN * 0.05)
        self.play(Create(marco), run_time=0.9)
        self.wait(0.6)

        # --- una consulta que entra, en cascada hacia su registro ----------
        q = S.codigo(["EXEC usp_PedidosCliente @id"], font_size=20)
        q.move_to(LEFT * 3.0 + UP * 1.75)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.6)

        caja_planes = S.operador("Planes", color=C_TITULO, ancho=2.2,
                                 alto=0.78, font_size=22)
        caja_planes.move_to(LEFT * 0.2 + UP * 0.35)
        f1 = Arrow(q.get_bottom() + DOWN * 0.05, caja_planes.get_top() + UP * 0.05,
                  buff=0.05, stroke_width=3.0, color=C_TENUE,
                  max_tip_length_to_length_ratio=0.22)
        self.play(Create(f1), FadeIn(caja_planes, shift=UP * 0.15), run_time=0.7)
        et_planes = tag_junto(caja_planes, "que planes uso", RIGHT, buff=0.3)
        self.play(FadeIn(et_planes), run_time=0.4)
        self.wait(1.8)

        caja_metricas = S.operador("Metricas", color=C_TITULO, ancho=2.2,
                                   alto=0.78, font_size=22)
        caja_metricas.move_to(RIGHT * 2.8 + DOWN * 1.55)
        f2 = Arrow(caja_planes.get_bottom() + DOWN * 0.05,
                  caja_metricas.get_top() + UP * 0.15, buff=0.05,
                  stroke_width=3.0, color=C_TENUE,
                  max_tip_length_to_length_ratio=0.22)
        self.play(Create(f2), FadeIn(caja_metricas, shift=UP * 0.15), run_time=0.7)
        et_metricas = tag_junto(caja_metricas, "lecturas y tiempo", DOWN,
                                buff=0.28)
        self.play(FadeIn(et_metricas), run_time=0.4)
        self.wait(2.2)

        # --- esto se repite: una linea de tiempo por intervalos ------------
        detalle = VGroup(q, f1, caja_planes, et_planes, f2, caja_metricas,
                         et_metricas)
        self.play(FadeOut(detalle), run_time=0.7)

        eje = Line(LEFT * 5.2, RIGHT * 5.2, stroke_color=C_TENUE,
                  stroke_width=2.2)
        eje.move_to(UP * 0.5)
        self.play(Create(eje), run_time=0.7)

        n = 6
        xs = np.linspace(-4.6, 4.6, n)
        marcas = VGroup()
        planes_mini = VGroup()
        metricas_mini = VGroup()
        alturas = [0.7, 1.1, 0.55, 1.5, 0.85, 1.05]
        for x, h in zip(xs, alturas):
            marca = Line([x, 0.4, 0], [x, 0.6, 0], stroke_color=C_TENUE,
                        stroke_width=2)
            marcas.add(marca)
            caja = Rectangle(width=0.46, height=0.34, stroke_width=1.6,
                             stroke_color=C_TITULO, fill_color=C_TITULO,
                             fill_opacity=0.14)
            caja.move_to([x, 1.55, 0])
            planes_mini.add(caja)
            barra = Rectangle(width=0.34, height=h, stroke_width=0,
                              fill_color=C_TENUE, fill_opacity=0.8)
            barra.move_to([x, 0.5 - h / 2, 0])
            metricas_mini.add(barra)
        self.play(LaggedStart(*[FadeIn(m, scale=0.6) for m in marcas],
                              lag_ratio=0.1), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.15)
                                for c in planes_mini], lag_ratio=0.1),
                  run_time=1.4)
        self.play(LaggedStart(*[GrowFromEdge(b, UP) for b in metricas_mini],
                              lag_ratio=0.1), run_time=1.4)
        et_linea = tag_junto(VGroup(eje, metricas_mini), "un registro por intervalo",
                             DOWN, buff=0.35)
        self.play(FadeIn(et_linea), run_time=0.5)
        self.wait(2.4)

        self.play(LaggedStart(*[Indicate(VGroup(planes_mini[i], metricas_mini[i]),
                                         color=C_TITULO, scale_factor=1.15)
                               for i in range(n)], lag_ratio=0.1), run_time=1.8)
        self.wait(8.0)
