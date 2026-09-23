class Clip4(Scene):
    """3.3.4 - La regla R5: toda corrida que supere 1.05 veces al oraculo se
    invalida sola. Un piloto mal configurado dio casi tres veces el oraculo,
    lo que ninguna politica legitima puede hacer, y el protocolo lo tumbo.
    Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La guardia R5"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        sem = sorted(ORC)
        y0, alto = -2.3, 3.9
        vmax = max(MOCK.values())
        xs = [-3.6, 0.0, 3.6]
        h = lambda v: alto * v / vmax
        suelo = Line([-6.0, y0, 0], [6.0, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        es = VGroup(*[tag_hud(f"semilla {s}", font_size=17, color=C_TENUE).move_to([x, y0 - 0.35, 0])
                      for x, s in zip(xs, sem)])
        self.play(FadeIn(suelo), FadeIn(es), run_time=0.5)
        orc = [Rectangle(width=0.95, height=h(ORC[s]), stroke_width=0, fill_color=C_PRIV, fill_opacity=1.0)
               .move_to([x - 0.55, y0 + h(ORC[s]) / 2, 0]) for x, s in zip(xs, sem)]
        topes = VGroup(*[DashedLine([x - 1.25, y0 + h(TOPE_R5 * ORC[s]), 0], [x + 1.25, y0 + h(TOPE_R5 * ORC[s]), 0],
                                    dash_length=0.12, stroke_color=CODE_INK, stroke_width=3)
                         for x, s in zip(xs, sem)])
        ley = VGroup(tag_hud("oraculo", font_size=17, color=C_PRIV), tag_hud("tope R5", font_size=17, color=CODE_INK),
                     tag_hud("piloto", font_size=17, color=C_ADAPTA)).arrange(RIGHT, buff=0.8).move_to([0, 2.45, 0])
        self.play(*[GrowFromEdge(b, DOWN) for b in orc], FadeIn(ley[0]), run_time=1.0)
        self.play(Create(topes), FadeIn(ley[1]), run_time=0.8)
        rot.mostrar(formula_pie(rf"J(\pi) > {TOPE_R5}\cdot J(\pi_{{gr}}) \Rightarrow \text{{invalida}}"),
                    zona="abajo", run_time=0.5)
        self.wait(5.3)

        pil = [Rectangle(width=0.95, height=h(MOCK[s]), stroke_width=0, fill_color=C_ADAPTA, fill_opacity=1.0)
               .move_to([x + 0.55, y0 + h(MOCK[s]) / 2, 0]) for x, s in zip(xs, sem)]
        self.play(*[GrowFromEdge(b, DOWN) for b in pil], FadeIn(ley[2]), run_time=1.6)
        veces = VGroup(*[tag_hud(f"{MOCK[s] / ORC[s]:.1f}x", font_size=20, color=C_ADAPTA).next_to(b, UP, buff=0.12)
                         for b, s in zip(pil, sem)])
        self.play(FadeIn(veces), run_time=0.5)
        rot.mostrar(dato_pie("piloto de G2b, junio 2026"), zona="abajo", run_time=0.5)
        self.wait(5.1)
        cruces = VGroup()
        for b in pil:
            cruces.add(Line(b.get_corner(DL), b.get_corner(UR), stroke_color=CODE_BG, stroke_width=7),
                       Line(b.get_corner(UL), b.get_corner(DR), stroke_color=CODE_BG, stroke_width=7))
        self.play(*[b.animate.set_fill(C_NO) for b in pil], veces.animate.set_color(C_NO), run_time=0.6)
        self.play(Create(cruces), run_time=0.8)
        rot.mostrar(cifra_pie("invalidado en las 3 semillas"), zona="abajo", run_time=0.5)
        self.wait(5.5)

        cierre_leccion(self, rot, "Un protocolo que nunca invalida",
                       "no esta midiendo nada.",
                       suelo, es, ley, topes, veces, cruces, *orc, *pil)
