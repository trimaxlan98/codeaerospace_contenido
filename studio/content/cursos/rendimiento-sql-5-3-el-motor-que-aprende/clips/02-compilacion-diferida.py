class Clip2(Scene):
    """5.3.2 - Con el nivel de compatibilidad viejo el motor COMPILA antes
    de llenar la variable (por eso supone 1 fila); con el nuevo, llena
    primero y compila despues, viendo las filas reales. El resultado: el
    mismo trabajo tarda 1.8 s contra 0.67 s (ambar, barras lineales
    rojo/verde), 2.7x menos tiempo (cian). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Compilacion diferida"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el orden se invierte: compila-luego-llena vs llena-luego-compila -
        c1 = S.operador("Compila", color=C_MALO, ancho=2.6)
        l1 = S.operador("Llena @t", color=C_MALO, ancho=2.6)
        c1.move_to(LEFT * 3.3 + UP * 1.8)
        l1.move_to(LEFT * 3.3 + DOWN * 0.4)
        f1 = Arrow(c1.get_bottom(), l1.get_top(), buff=0.14, color=C_MALO,
                  stroke_width=3.4, max_tip_length_to_length_ratio=0.16)
        self.play(FadeIn(c1, shift=RIGHT * 0.15), run_time=0.5)
        self.play(Create(f1), FadeIn(l1, shift=UP * 0.15), run_time=0.7)
        tag_antes = tag_junto(l1, "compila primero", DOWN, buff=0.3,
                              color=C_MALO)
        self.play(FadeIn(tag_antes), run_time=0.4)

        l2 = S.operador("Llena @t", color=C_BUENO, ancho=2.6)
        c2 = S.operador("Compila", color=C_BUENO, ancho=2.6)
        l2.move_to(RIGHT * 3.3 + UP * 1.8)
        c2.move_to(RIGHT * 3.3 + DOWN * 0.4)
        f2 = Arrow(l2.get_bottom(), c2.get_top(), buff=0.14, color=C_BUENO,
                  stroke_width=3.4, max_tip_length_to_length_ratio=0.16)
        self.play(FadeIn(l2, shift=LEFT * 0.15), run_time=0.5)
        self.play(Create(f2), FadeIn(c2, shift=UP * 0.15), run_time=0.7)
        tag_ahora = tag_junto(c2, "llena primero", DOWN, buff=0.3,
                              color=C_BUENO)
        self.play(FadeIn(tag_ahora), run_time=0.4)
        self.wait(3.0)

        grupo_arriba = VGroup(c1, l1, f1, tag_antes, l2, c2, f2, tag_ahora)
        self.play(FadeOut(grupo_arriba), run_time=0.7)

        # --- el duelo de tiempos: lineal (rango chico, log sobraria) ----------
        largo = 7.0
        maximo = TVAR_140
        base_x = LEFT * 3.5

        bar_buena = S.barra_lecturas(TVAR_170, maximo, largo=largo, alto=0.7,
                                     color=C_BUENO, log=False)
        bar_buena.shift(base_x + UP * 0.6)
        bar_mala = S.barra_lecturas(TVAR_140, maximo, largo=largo, alto=0.7,
                                    color=C_MALO, log=False)
        bar_mala.shift(base_x + DOWN * 1.2)

        lab_b = tag_junto(bar_buena, "compila despues", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_buena, LEFT), FadeIn(lab_b), run_time=0.9)
        tag_b = tag_motor(tiempo(TVAR_170))
        tag_b.next_to(bar_buena, RIGHT, buff=0.22)
        self.play(FadeIn(tag_b), run_time=0.4)
        self.wait(0.6)

        lab_m = tag_junto(bar_mala, "compila antes", LEFT, buff=0.3,
                          color=C_MALO)
        self.play(GrowFromEdge(bar_mala, LEFT), FadeIn(lab_m), run_time=0.9)
        tag_m = tag_motor(tiempo(TVAR_140))
        tag_m.next_to(bar_mala, RIGHT, buff=0.22)
        self.play(FadeIn(tag_m), run_time=0.4)
        self.wait(1.2)

        tag_medido = tag_junto(bar_mala, "tiempo medido", DOWN, buff=0.55,
                               color=C_TENUE)
        tag_medido.align_to(bar_mala, LEFT)
        self.play(FadeIn(tag_medido), run_time=0.4)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{RAZON_TVAR:.1f}x menos tiempo"),
                   zona="abajo", run_time=0.5)
        self.play(Indicate(bar_buena, color=C_BUENO, scale_factor=1.06),
                  Indicate(bar_mala, color=C_MALO, scale_factor=1.04),
                  run_time=1.0)
        self.wait(15.0)
