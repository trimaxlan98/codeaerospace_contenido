class Clip4(Scene):
    """5.2.4 - Duelo final en escala logaritmica: el camino del literal
    (verde, 22,363 lecturas) contra el camino de la variable (rojo,
    450,173 lecturas). La razon (~20x) en cian. Cierre de la leccion:
    una mala estimacion es un mal plan. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El costo de errar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        largo = 7.2
        maximo = VARLOC
        base_x = LEFT * 3.6

        bar_verde = S.barra_lecturas(LIT, maximo, largo=largo, alto=0.6,
                                     color=C_BUENO, log=True)
        bar_verde.shift(base_x + UP * 0.7)
        bar_roja = S.barra_lecturas(VARLOC, maximo, largo=largo, alto=0.6,
                                    color=C_MALO, log=True)
        bar_roja.shift(base_x + DOWN * 1.1)

        base = Line(base_x + UP * 1.5, base_x + DOWN * 1.9,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.8)

        lab_v = tag_junto(bar_verde, "el literal", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(LIT))
        tag_v.next_to(bar_verde, RIGHT, buff=0.22)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(1.8)

        lab_r = tag_junto(bar_roja, "la variable", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_roja, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_motor(lecturas(VARLOC))
        tag_r.next_to(bar_roja, RIGHT, buff=0.22)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(4.0)

        rot.mostrar(cifra_pie(f"{S.miles(round(RAZON4))}x mas lecturas"),
                   zona="abajo", run_time=0.5)
        self.play(Indicate(bar_verde, color=C_BUENO, scale_factor=1.06),
                  Indicate(bar_roja, color=C_MALO, scale_factor=1.04),
                  run_time=1.0)
        self.wait(5.0)

        grupo = VGroup(base, aviso, bar_verde, lab_v, tag_v, bar_roja,
                       lab_r, tag_r)
        cierre_leccion(self, rot, "Una mala estimacion",
                       "es un mal plan.", grupo, espera=8.0)
