class Clip3(Scene):
    """4.2.3 - El duelo: 960 lecturas cuando el parametro llega NVARCHAR
    (recorre el indice completo, sobre 200,000 clientes) contra 3 cuando
    llega VARCHAR (seek directo). Razon en cian con S.razon. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        titulo_txt = f"{S.miles(EMAIL_NV)} contra {S.miles(EMAIL_V)}"
        rot.mostrar(titulo_curso(titulo_txt), zona="arriba", run_time=0.6)
        self.wait(0.6)

        largo = 8.0
        maximo = EMAIL_NV
        base_x = LEFT * 4.6

        bar_bueno = S.barra_lecturas(EMAIL_V, maximo, largo=largo, alto=0.55,
                                     color=C_BUENO, log=True)
        bar_bueno.shift(base_x + UP * 0.9)
        bar_malo = S.barra_lecturas(EMAIL_NV, maximo, largo=largo, alto=0.55,
                                    color=C_MALO, log=True)
        bar_malo.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_bueno = tag_junto(bar_bueno, "con VARCHAR", LEFT, buff=0.3,
                              color=C_BUENO)
        lab_malo = tag_junto(bar_malo, "con NVARCHAR", LEFT, buff=0.3,
                             color=C_MALO)
        self.play(FadeIn(bar_bueno, shift=RIGHT * 0.2), FadeIn(lab_bueno),
                  run_time=0.8)
        self.wait(0.4)
        self.play(FadeIn(bar_malo, shift=RIGHT * 0.2), FadeIn(lab_malo),
                  run_time=0.9)
        self.wait(1.0)

        tag_b = tag_motor(lecturas(EMAIL_V))
        tag_b.next_to(bar_bueno, RIGHT, buff=0.2)
        tag_m = tag_motor(lecturas(EMAIL_NV))
        tag_m.next_to(bar_malo, RIGHT, buff=0.2)
        self.play(FadeIn(tag_b), run_time=0.4)
        self.wait(0.6)
        self.play(FadeIn(tag_m), run_time=0.4)
        self.wait(1.2)

        self.wait(2.4)

        razon = S.razon(EMAIL_NV, EMAIL_V)
        rot.mostrar(cifra_pie(f"{razon:.0f}x menos lecturas"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(bar_malo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_bueno, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(16.0)
