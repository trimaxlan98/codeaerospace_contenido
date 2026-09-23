class Clip4(Scene):
    """2.3.4 - El lider por reputacion: el mejor candidato de partida es un
    traidor que propone decisiones invalidas; cada fallo le resta, y en unas
    rondas el liderazgo pasa a otro sin votacion global. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Quien manda"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        f = MathTex(r"\mathrm{rep} = w_1\,\mathrm{uptime} + w_2\,\mathrm{calidad} - w_3\,\mathrm{fallos}",
                    color=CODE_INK, font_size=40).move_to([0, 2.2, 0])
        self.play(Write(f), run_time=1.6)
        rot.mostrar(dato_pie(f"pesos elegidos {W_REP[0]:g} {W_REP[1]:g} {W_REP[2]:g}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        y0, esc = -2.1, 1.9
        xs = [-4.4 + 2.2 * i for i in range(5)]
        suelo = Line([-5.4, y0, 0], [5.4, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        noms = VGroup(*[tag_hud(f"sat {i + 1}", font_size=17, color=C_NO if i == TRAIDOR else C_TENUE)
                        .move_to([x, y0 - 0.35, 0]) for i, x in enumerate(xs)])
        self.play(FadeIn(suelo), FadeIn(noms), run_time=0.5)

        def barras(r):
            g = VGroup()
            for i, x in enumerate(xs):
                h = max(esc * REPS[r, i], 0.03)
                col = C_ADAPTA if LIDER[r] == i else (C_NO if i == TRAIDOR else C_ESTATICA)
                g.add(Rectangle(width=1.1, height=h, stroke_width=0, fill_color=col,
                                fill_opacity=1.0).move_to([x, y0 + h / 2, 0]))
            return g
        bs = barras(0)
        corona = Triangle(color=C_ADAPTA, fill_opacity=1.0).scale(0.16).rotate(PI)
        corona.next_to(bs[LIDER[0]], UP, buff=0.12)
        self.play(*[GrowFromEdge(b, DOWN) for b in bs], run_time=1.0)
        self.play(FadeIn(corona), run_time=0.4)
        self.wait(2.0)
        for r in range(1, 5):
            nb = barras(r)
            self.play(Transform(bs, nb), corona.animate.next_to(nb[LIDER[r]], UP, buff=0.12),
                      run_time=1.0)
            rot.mostrar(cifra_pie(f"ronda {r}: lider sat {LIDER[r] + 1}"), zona="abajo", run_time=0.4)
            self.wait(1.8)
        rot.mostrar(cifra_pie(f"nuevo lider en ronda {RONDA_CAMBIO}"), zona="abajo", run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "Decidir entre muchos",
                       "aunque alguno mienta.",
                       f, suelo, noms, bs, corona)
