class Clip3(Scene):
    """5.1.3 - Si el optimizador no conoce el valor de la variable, no
    tiene un paso al que mirar: reparte las filas entre TODOS los clientes
    distintos por igual. El resultado es una barra violeta plana (lo que
    CREE) minusculo comparado con la torre real del cliente 1 (cian).
    Duelo en escala logaritmica. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Densidad: un promedio parejo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.7)

        rot.mostrar(cifra_pie(f"{S.miles(CLIENTES_DIST)} clientes distintos"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"\frac{1500000}{189248} \approx 7.9"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- duelo: la torre real contra la barra pareja de la estimacion --
        largo = 7.2
        maximo = C1_MODELO
        base_x = LEFT * 3.6

        bar_real = S.barra_lecturas(C1_MODELO, maximo, largo=largo, alto=0.6,
                                    color=C_CALCULO, log=True)
        bar_real.shift(base_x + UP * 0.5)
        bar_est = S.barra_lecturas(EST_VAR, maximo, largo=largo, alto=0.6,
                                   color=C_CREE, log=True)
        bar_est.shift(base_x + DOWN * 1.4)

        base = Line(base_x + UP * 1.1, base_x + DOWN * 1.85,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_real = tag_junto(bar_real, "cliente real", LEFT, buff=0.3,
                             color=C_CALCULO)
        self.play(GrowFromEdge(bar_real, LEFT), FadeIn(lab_real), run_time=0.9)
        tag_real = tag_hud(f"{S.miles(C1_MODELO)} filas", font_size=22,
                           color=C_CALCULO)
        tag_real.next_to(bar_real, RIGHT, buff=0.24)
        self.play(FadeIn(tag_real), run_time=0.4)
        self.wait(1.8)

        lab_est = tag_junto(bar_est, "cualquier cliente", LEFT, buff=0.3,
                            color=C_CREE)
        self.play(GrowFromEdge(bar_est, LEFT), FadeIn(lab_est), run_time=0.9)
        tag_est = tag_hud(f"{fmt(EST_VAR, 1)} filas", font_size=22,
                          color=C_CREE)
        tag_est.next_to(bar_est, RIGHT, buff=0.24)
        self.play(FadeIn(tag_est), run_time=0.4)
        self.wait(1.8)

        mismo = tag_junto(tag_est, "mismo para todos", RIGHT, buff=0.4,
                          color=C_CREE)
        self.play(FadeIn(mismo), run_time=0.5)
        self.wait(1.0)
        self.play(Indicate(bar_real, color=C_CALCULO, scale_factor=1.04),
                  Indicate(bar_est, color=C_CREE, scale_factor=1.15),
                  run_time=1.0)
        self.wait(10.2)
