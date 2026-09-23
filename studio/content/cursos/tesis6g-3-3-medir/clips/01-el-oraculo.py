class Clip1(Scene):
    """3.3.1 - El oraculo de la tesis ve todo pero solo mira un paso
    adelante: no es el techo. Mirando dos pasos (729 secuencias por
    decision) se gana algo mas en las tres semillas, siempre menos del
    1 %. El margen medido es una cota inferior ajustada. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El oraculo no es el techo"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        filas = K2["por_semilla"]
        y0, alto = -2.2, 4.0
        vmin = min(p["k1"] for p in filas) * 0.97
        vmax = max(p["k2"] for p in filas) * 1.005
        xs = [-3.8, 0.0, 3.8]
        suelo = Line([-6.0, y0, 0], [6.0, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        sem = VGroup(*[tag_hud(f"semilla {p['semilla']}", font_size=17, color=C_TENUE)
                       .move_to([x, y0 - 0.35, 0]) for x, p in zip(xs, filas)])
        corte = tag_hud(f"eje desde {vmin:,.0f}".replace(",", " "), font_size=16, color=C_DATO)
        corte.to_corner(UR, buff=0.6).shift(DOWN * 0.5)
        self.play(FadeIn(suelo), FadeIn(sem), FadeIn(corte), run_time=0.6)
        rot.mostrar(dato_pie("eje recortado: se declara"), zona="abajo", run_time=0.5)
        self.wait(3.9)

        def barra(x, v, col):
            h = alto * (v - vmin) / (vmax - vmin)
            return Rectangle(width=1.1, height=h, stroke_width=0, fill_color=col,
                             fill_opacity=1.0).move_to([x, y0 + h / 2, 0])
        b1 = [barra(x - 0.62, p["k1"], C_PRIV) for x, p in zip(xs, filas)]
        b2 = [barra(x + 0.62, p["k2"], C_OK) for x, p in zip(xs, filas)]
        l1 = tag_hud("voraz k=1", font_size=18, color=C_PRIV).move_to([-1.3, 2.4, 0])
        l2 = tag_hud("dos pasos k=2", font_size=18, color=C_OK).move_to([1.6, 2.4, 0])
        self.play(*[GrowFromEdge(b, DOWN) for b in b1], FadeIn(l1), run_time=1.0)
        self.wait(3.3)
        self.play(*[GrowFromEdge(b, DOWN) for b in b2], FadeIn(l2), run_time=1.0)
        gan = VGroup(*[tag_hud(f"+{fmt(100 * p['ganancia'], 2)} %", font_size=18, color=C_CALCULO)
                       .next_to(b, UP, buff=0.12) for b, p in zip(b2, filas)])
        self.play(FadeIn(gan), run_time=0.6)
        rot.mostrar(dato_pie("729 secuencias por decision"), zona="abajo", run_time=0.5)
        self.wait(5.1)
        rot.mostrar(formula_pie(r"\widehat{\mathrm{MA}} \le \mathrm{MA}"), zona="abajo", run_time=0.5)
        self.wait(5.1)
        c = K2["correccion_G1"]
        rot.mostrar(dato_pie(f"correccion en G1: +{fmt(c['correccion_max'], 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(5.3)
