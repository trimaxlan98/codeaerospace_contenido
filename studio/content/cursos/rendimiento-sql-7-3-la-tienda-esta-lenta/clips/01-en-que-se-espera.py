class Clip1(Scene):
    """7.3.1 - Como sabe el motor que algo anda mal sin medir esta carga
    en particular: las categorias de espera, con alturas ILUSTRATIVAS (no
    hay medicion de esta carga en la libreria, se rotula "ilustrativo"), y
    Query Store, que ve las cuatro consultas de la tienda para poder
    ordenarlas por lecturas. Sin cifras: es el mecanismo, no una medicion
    nueva. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("En que se espera"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- categorias de espera: alturas ILUSTRATIVAS, sin medir --------
        categorias = [("leer paginas", 4.4), ("esperar a otro", 2.6),
                     ("CPU", 1.2)]
        xs = np.linspace(-3.9, 3.9, 3)
        y0 = -2.3
        barras = VGroup()
        etiquetas = VGroup()
        for x, (nombre, h) in zip(xs, categorias):
            b = Rectangle(width=1.3, height=h, stroke_width=0,
                         fill_color=C_TENUE, fill_opacity=0.55)
            b.move_to([x, y0 + h / 2, 0])
            barras.add(b)
            et = Text(nombre, font_size=22, color=C_TITULO)
            et.next_to(b, DOWN, buff=0.24)
            etiquetas.add(et)
        suelo = Line([-4.8, y0, 0], [4.8, y0, 0], stroke_color=C_TENUE,
                    stroke_width=2)
        self.play(Create(suelo), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras],
                              lag_ratio=0.25), run_time=1.8)
        self.play(FadeIn(etiquetas), run_time=0.5)
        self.wait(1.0)
        aviso = tag_junto(etiquetas, "ilustrativo", DOWN, buff=0.4)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(3.8)

        grupo1 = VGroup(barras, etiquetas, suelo, aviso)
        self.play(FadeOut(grupo1), run_time=0.7)

        # --- Query Store ve las cuatro consultas de la tienda --------------
        marco = RoundedRectangle(width=6.6, height=4.4, corner_radius=0.24,
                                 stroke_color=C_TENUE, stroke_width=2.0,
                                 fill_color=C_TENUE, fill_opacity=0.04)
        marco.move_to(LEFT * 1.7 + DOWN * 0.1)
        nom_qs = Text("Query Store", font_size=26, color=C_TITULO)
        nom_qs.next_to(marco, UP, buff=0.22)
        self.play(Create(marco), FadeIn(nom_qs), run_time=0.8)
        self.wait(0.7)

        tipos = [("login", 1.6), ("mis pedidos", 2.4), ("el ticket", 2.1),
                ("reporte", 1.8)]
        filas = VGroup()
        for nombre, ancho in tipos:
            caja = S.operador(nombre, color=C_INDICE, ancho=ancho, alto=0.68,
                              font_size=22)
            filas.add(caja)
        filas.arrange(DOWN, buff=0.32)
        filas.move_to(marco)
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.2) for f in filas],
                              lag_ratio=0.2), run_time=1.8)
        self.wait(1.2)

        flecha = Arrow(UP * 1.6, DOWN * 1.6, buff=0.0, stroke_width=3.4,
                      color=C_TENUE, max_tip_length_to_length_ratio=0.12)
        flecha.next_to(marco, RIGHT, buff=1.0)
        et_orden = tag_junto(flecha, "ordenar por lecturas", RIGHT, buff=0.3)
        self.play(Create(flecha), FadeIn(et_orden), run_time=0.8)
        self.wait(1.6)

        self.play(LaggedStart(*[Indicate(f.texto, color=C_TITULO, scale_factor=1.1)
                               for f in filas], lag_ratio=0.2), run_time=2.4)
        self.wait(9.2)
