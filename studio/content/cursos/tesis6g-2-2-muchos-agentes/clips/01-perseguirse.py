class Clip1(Scene):
    """2.2.1 - Dos satelites aprenden cada uno por su lado a no chocar en el
    mismo canal. Como cada uno cambia a la vez que el otro, al principio se
    persiguen. Un aprendiz conjunto se coordina casi de inmediato. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Aprender a la vez"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        n, lado, x0 = 40, 0.26, -5.4

        def fila(acc, col, y, titulo):
            celdas = VGroup()
            for k in range(n):
                a = acc[k]
                c = Square(side_length=lado, stroke_width=0, fill_opacity=1.0,
                           fill_color=C_ENLACE if a == 0 else C_PRIV)
                celdas.add(c.move_to([x0 + k * (lado + 0.04), y, 0]))
            e = tag_hud(titulo, font_size=16, color=C_TENUE).next_to(celdas, LEFT, buff=0.15)
            return celdas, e

        def choques(col, y):
            g = VGroup()
            for k in range(n):
                if col[k]:
                    g.add(Line([x0 + k * (lado + 0.04), y - 0.14, 0],
                               [x0 + k * (lado + 0.04), y + 0.14, 0], stroke_color=C_NO,
                               stroke_width=5))
            return g

        leyenda = VGroup(tag_hud("canal 0", font_size=17, color=C_ENLACE),
                         tag_hud("canal 1", font_size=17, color=C_PRIV),
                         tag_hud("choque", font_size=17, color=C_NO)).arrange(RIGHT, buff=0.6)
        leyenda.move_to([0.6, 2.35, 0])
        self.play(FadeIn(leyenda), run_time=0.5)

        f1, e1 = fila(ACC_IND[:, 0], COL_IND, 1.5, "sat 1")
        f2, e2 = fila(ACC_IND[:, 1], COL_IND, 1.1, "sat 2")
        ch = choques(COL_IND, 0.7)
        self.play(FadeIn(e1), FadeIn(e2), run_time=0.4)
        for k in range(n):
            anims = [FadeIn(f1[k]), FadeIn(f2[k])]
            self.play(*anims, run_time=0.07)
        self.play(FadeIn(ch), run_time=0.6)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"independientes: {MED_IND:.0f} pasos"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        g1, h1 = fila(ACC_CON[:, 0], COL_CON, -0.6, "sat 1")
        g2, h2 = fila(ACC_CON[:, 1], COL_CON, -1.0, "sat 2")
        ch2 = choques(COL_CON, -1.4)
        tit = tag_hud("un solo aprendiz conjunto", font_size=17, color=C_TENUE).move_to([0.6, -0.1, 0])
        self.play(FadeIn(tit), FadeIn(h1), FadeIn(h2), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(VGroup(g1[k], g2[k])) for k in range(n)], lag_ratio=0.05),
                  run_time=2.4)
        self.play(FadeIn(ch2), run_time=0.5)
        rot.mostrar(cifra_pie(f"conjunto: {MED_CON:.0f} paso"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(cifra_pie(f"p90: {P90_IND:.0f} contra {P90_CON:.0f} pasos"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie("mediana de 1000 semillas"), zona="abajo", run_time=0.5)
        self.wait(3.2)
        self.wait(2.4)
