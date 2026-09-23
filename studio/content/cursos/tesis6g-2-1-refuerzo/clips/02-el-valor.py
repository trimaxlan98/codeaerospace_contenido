class Clip2(Scene):
    """2.1.2 - Q-learning en un juguete del banco de la tesis: dos estados
    (visible, eclipse) y tres acciones. La tabla aprende que con el
    satelite a la vista conviene el espectro alto y en eclipse, la ruta.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Aprender el valor"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        filas = ["visible", "eclipse"]
        x0, y0, lado = -2.4, 1.0, 1.45
        celdas, textos = {}, {}
        tabla = VGroup()
        for s in range(2):
            for a in range(3):
                c = Square(side_length=lado, stroke_color=C_TENUE, stroke_width=2,
                           fill_color=C_ADAPTA, fill_opacity=0.0)
                c.move_to([x0 + a * (lado + 0.1), y0 - s * (lado + 0.1), 0])
                celdas[(s, a)] = c
                tabla.add(c)
        cab = VGroup(*[tag_hud(ACC[a], font_size=18, color=C_TENUE)
                       .next_to(celdas[(0, a)], UP, buff=0.15) for a in range(3)])
        lat = VGroup(*[tag_hud(filas[s], font_size=18, color=C_TENUE)
                       .next_to(celdas[(s, 0)], LEFT, buff=0.2) for s in range(2)])
        self.play(FadeIn(tabla), FadeIn(cab), FadeIn(lat), run_time=1.0)
        self.wait(1.6)

        def valores(Q):
            g = VGroup()
            for (s, a), c in celdas.items():
                t = Text(f"{Q[s, a]:5.1f}", font=FUENTE_HUD, font_size=22, color=CODE_INK)
                g.add(t.move_to(c))
            return g

        qmax = QJ["r"].max()
        vals = valores(QJ["Q"][0])
        self.add(vals)
        paso = ValueTracker(0)
        for k in list(range(0, 60, 6)) + list(range(60, 601, 60)):
            Q = QJ["Q"][k]
            anims = [c.animate.set_fill(opacity=0.85 * max(Q[s, a], 0) / qmax)
                     for (s, a), c in celdas.items()]
            self.play(*anims, run_time=0.35)
            vals.become(valores(Q))
        self.wait(1.0)
        # la mejor accion de cada estado
        marcos = VGroup(*[SurroundingRectangle(celdas[(s, int(QJ["Q"][-1][s].argmax()))],
                                               color=C_CALCULO, buff=0.05, stroke_width=4)
                          for s in range(2)])
        self.play(Create(marcos), run_time=0.8)
        rot.mostrar(cifra_pie(f"visible: alto  eclipse: ruta"), zona="abajo", run_time=0.5)
        self.wait(4.2)
        rot.mostrar(formula_pie(r"Q(s,a) \leftarrow Q + \alpha\,(r - Q)"), zona="abajo", run_time=0.5)
        self.wait(4.2)
        rot.mostrar(cifra_pie(f"margen del juguete = {fmt(100 * QJ['MA'], 1)} %"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)
        self.wait(0.8)
        self.wait(1.8)
