class Clip2(Scene):
    """2.3.2 - Las tres fases de PBFT con cuatro replicas: el primario
    propone, todos confirman a todos, todos se comprometen. El trafico crece
    con el cuadrado de n. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Tres fases"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        n = Q4["n"]
        ys = [1.6, 0.55, -0.5, -1.55]
        x_fases = [-3.0, 0.6, 4.2]
        nombres = list(Q4["mensajes"].keys())
        filas = VGroup(*[Line([-5.6, y, 0], [6.2, y, 0], stroke_color=C_TENUE, stroke_width=1.5,
                              stroke_opacity=0.5) for y in ys])
        etq = VGroup(*[tag_hud("primario" if i == 0 else f"replica {i}", font_size=16,
                               color=C_ADAPTA if i == 0 else C_TENUE).move_to([-6.1, y, 0])
                       for i, y in enumerate(ys)])
        etq.shift(RIGHT * 0.2)
        self.play(FadeIn(filas), FadeIn(etq), run_time=0.8)
        cab = VGroup(*[tag_hud(nm, font_size=18, color=CODE_INK).move_to([x + 0.9, 2.25, 0])
                       for nm, x in zip(nombres, x_fases)])
        self.play(FadeIn(cab), run_time=0.5)
        self.wait(1.2)

        def flechas(x, emisores):
            g = VGroup()
            for e in emisores:
                for r in range(n):
                    if r != e:
                        g.add(Arrow([x, ys[e], 0], [x + 1.8, ys[r], 0], buff=0.08, stroke_width=2.5,
                                    color=C_ADAPTA if e == 0 else C_ENLACE,
                                    max_tip_length_to_length_ratio=0.12))
            return g
        emisores = [[0], list(range(1, n)), list(range(n))]
        cuentas = VGroup()
        for fase, x, em in zip(nombres, x_fases, emisores):
            fl = flechas(x, em)
            self.play(LaggedStart(*[GrowArrow(a) for a in fl], lag_ratio=0.05), run_time=1.8)
            c = tag_hud(f"{Q4['mensajes'][fase]}", font_size=22, color=C_CALCULO)
            c.move_to([x + 0.9, -2.2, 0])
            self.play(FadeIn(c), run_time=0.4)
            cuentas.add(c)
            self.wait(1.8)
        rot.mostrar(cifra_pie(f"total = {Q4['mensajes_total']} mensajes"), zona="abajo", run_time=0.5)
        self.wait(3.4)
        rot.mostrar(formula_pie(r"2\,n\,(n-1)"), zona="abajo", run_time=0.5)
        self.wait(3.4)
        rot.mostrar(cifra_pie(f"n=1000: {ntn.quorum_pbft(1000)['mensajes_total']:,}".replace(",", " ")),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
        self.wait(0.8)
