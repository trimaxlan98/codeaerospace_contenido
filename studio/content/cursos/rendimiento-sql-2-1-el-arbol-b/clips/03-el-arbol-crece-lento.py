class Clip3(Scene):
    """2.1.3 - Grafica hecha a mano (sin Axes de manim): niveles del arbol
    contra filas en escala log10, de mil a diez mil millones. El escalon
    de 1.5 M cae en 3 niveles; el siguiente no llega hasta miles de
    millones de filas mas. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El arbol crece lento"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        caja = (-5.3, 5.3, -1.4, 2.2)
        rx, ry = (3, 10), (1.6, 4.4)
        cua = Cuadro(caja, rx, ry)

        eje_x = cua.suelo(y=ry[0], color=C_TENUE)
        eje_y = Line(cua.p(rx[0], ry[0]), cua.p(rx[0], ry[1]),
                    stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(eje_x), Create(eje_y),
                  run_time=0.8)
        self.wait(1.0)

        # --- eje x: potencias de diez, en MathTex --------------------------
        marcas_x = VGroup()
        for e in range(rx[0], rx[1] + 1):
            m = MathTex(f"10^{{{e}}}", font_size=22, color=C_TENUE)
            m.next_to(cua.p(e, ry[0]), DOWN, buff=0.16)
            marcas_x.add(m)
        rot_x = tag_junto(marcas_x, "filas", DOWN, buff=0.3)
        self.play(LaggedStart(*[FadeIn(m) for m in marcas_x], lag_ratio=0.08),
                  run_time=1.2)
        self.play(FadeIn(rot_x), run_time=0.4)
        self.wait(1.4)

        # --- eje y: niveles del arbol ---------------------------------------
        marcas_y = VGroup()
        for n in (2, 3, 4):
            t = tag_hud(str(n), font_size=18, color=C_TENUE)
            t.next_to(cua.p(rx[0], n), LEFT, buff=0.18)
            marcas_y.add(t)
        rot_y = tag_junto(eje_y, "niveles", UP, buff=0.28)
        self.play(FadeIn(marcas_y), run_time=0.5)
        self.play(FadeIn(rot_y), run_time=0.4)
        self.wait(2.0)

        # --- la escalera: se calcula recorriendo S.profundidad, no a mano --
        b1 = umbral_niveles(2)     # donde pasa de 2 a 3 niveles
        b2 = umbral_niveles(PROF)  # donde pasa de 3 a 4 niveles

        seg1 = cua.serie([rx[0], b1], [2, 2], C_CALCULO, ancho=4)
        salto1 = cua.serie([b1, b1], [2, 3], C_CALCULO, ancho=4)
        seg2 = cua.serie([b1, b2], [3, 3], C_CALCULO, ancho=4)
        salto2 = cua.serie([b2, b2], [3, 4], C_CALCULO, ancho=4)
        seg3 = cua.serie([b2, rx[1]], [4, 4], C_CALCULO, ancho=4)

        self.play(Create(seg1), run_time=1.0)
        self.wait(1.4)
        self.play(Create(salto1), run_time=0.4)
        self.wait(0.8)
        self.play(Create(seg2), run_time=1.0)
        self.wait(1.2)

        # --- el punto de la tienda: 1.5 M filas, 3 niveles ------------------
        x_marca = math.log10(FILAS_PED)
        guia_v = DashedLine(cua.p(x_marca, ry[0]), cua.p(x_marca, PROF),
                            dash_length=0.08, stroke_color=C_CALCULO,
                            stroke_width=1.6)
        guia_h = DashedLine(cua.p(rx[0], PROF), cua.p(x_marca, PROF),
                            dash_length=0.08, stroke_color=C_CALCULO,
                            stroke_width=1.6)
        punto = Dot(cua.p(x_marca, PROF), radius=0.09, color=C_CALCULO)
        self.play(Create(guia_v), Create(guia_h), run_time=0.7)
        self.play(FadeIn(punto, scale=0.5), run_time=0.4)
        marca_tag = tag_hud(f"{S.miles(FILAS_PED)} filas, {PROF} niveles",
                            font_size=18)
        marca_tag.next_to(punto, UL, buff=0.18)
        self.play(FadeIn(marca_tag), run_time=0.5)
        self.wait(3.5)

        self.play(Create(salto2), run_time=0.5)
        self.wait(0.8)
        self.play(Create(seg3), run_time=0.9)
        self.wait(2.5)

        # --- cuantas filas caben con un nivel mas (se recorre la funcion) --
        cap_extra = capacidad_niveles(PROF + 1)
        millones = round(cap_extra / 1_000_000)
        rot.mostrar(cifra_pie(f"{S.miles(millones)} millones con {PROF + 1} niveles"),
                    zona="abajo", run_time=0.5)
        self.wait(8.0)
