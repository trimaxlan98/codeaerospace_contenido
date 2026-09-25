class Clip4(Scene):
    """7.3.4 - El duelo final del curso: sin los cuatro arreglos, la tienda
    tarda 53 segundos en atender las 300 peticiones; con ellos, 3.9. Escala
    LINEAL (la barra corta se ve corta: no hace falta aviso logaritmico).
    Cierre del CURSO completo. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Despues de los arreglos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        largo = 7.6
        maximo = ANTES
        base_x = LEFT * 4.3
        bar_antes = S.barra_lecturas(ANTES, maximo, largo=largo, alto=0.6,
                                     color=C_MALO, log=False)
        bar_antes.shift(base_x + UP * 0.9)
        bar_despues = S.barra_lecturas(DESPUES, maximo, largo=largo, alto=0.6,
                                       color=C_BUENO, log=False)
        bar_despues.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        self.wait(0.5)

        lab_a = tag_junto(bar_antes, "sin arreglos", LEFT, buff=0.3, color=C_MALO)
        lab_d = tag_junto(bar_despues, "con arreglos", LEFT, buff=0.3, color=C_BUENO)
        self.play(FadeIn(bar_antes, shift=RIGHT * 0.2), FadeIn(lab_a), run_time=0.9)
        self.wait(0.5)
        self.play(FadeIn(bar_despues, shift=RIGHT * 0.2), FadeIn(lab_d), run_time=0.9)
        self.wait(1.2)

        tag_a = tag_motor(txt_seg_corto(ANTES))
        tag_a.next_to(bar_antes, RIGHT, buff=0.2)
        tag_d = tag_motor(txt_seg_corto(DESPUES))
        tag_d.next_to(bar_despues, RIGHT, buff=0.2)
        self.play(FadeIn(tag_a), run_time=0.4)
        self.wait(0.6)
        self.play(FadeIn(tag_d), run_time=0.4)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"{RAZON:.1f}x mas rapido"), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(bar_antes, color=C_MALO, scale_factor=1.02),
                  Indicate(bar_despues, color=C_BUENO, scale_factor=1.06),
                  run_time=1.0)
        self.wait(5.8)

        cierre_leccion(self, rot, "Medir, leer el plan, leer menos.",
                       "Eso es optimizar.", base, bar_antes, bar_despues,
                       lab_a, lab_d, tag_a, tag_d, espera=9.0)
