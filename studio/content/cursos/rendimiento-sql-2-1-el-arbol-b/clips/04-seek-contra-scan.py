class Clip4(Scene):
    """2.1.4 - El duelo de la leccion: tres lecturas contra veintidos mil,
    en escala log10 (se avisa: la barra roja no es "diez veces" la verde,
    es miles de veces). Cierre sin cifras. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Seek contra scan"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        largo = 8.0
        maximo = M["scan_pedidos"]
        base_x = LEFT * 4.6

        bar_verde = S.barra_lecturas(M["pk_seek"], maximo, largo=largo,
                                     alto=0.55, color=C_BUENO, log=True)
        bar_verde.shift(base_x + UP * 0.9)
        bar_rojo = S.barra_lecturas(M["scan_pedidos"], maximo, largo=largo,
                                    alto=0.55, color=C_MALO, log=True)
        bar_rojo.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_v = tag_junto(bar_verde, "con indice", LEFT, buff=0.3, color=C_BUENO)
        lab_r = tag_junto(bar_rojo, "sin indice", LEFT, buff=0.3, color=C_MALO)
        self.play(FadeIn(bar_verde, shift=RIGHT * 0.2), FadeIn(lab_v), run_time=0.8)
        self.wait(0.5)
        self.play(FadeIn(bar_rojo, shift=RIGHT * 0.2), FadeIn(lab_r), run_time=0.9)
        self.wait(1.2)

        # las cifras ambar viven junto a cada barra: no se repiten abajo
        tag_v = tag_motor(lecturas(M["pk_seek"]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.2)
        tag_r = tag_motor(lecturas(M["scan_pedidos"]))
        tag_r.next_to(bar_rojo, RIGHT, buff=0.2)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(0.8)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(3.2)

        # el carril de abajo solo lleva la razon (cian): no duplica el ambar
        razon = S.razon(M["scan_pedidos"], M["pk_seek"])
        rot.mostrar(cifra_pie(f"{S.miles(round(razon))}x mas lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_rojo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(8.5)

        grupo = VGroup(base, aviso, bar_verde, bar_rojo, lab_v, lab_r, tag_v, tag_r)
        cierre_leccion(self, rot, "Un indice es un orden.",
                       "Y el orden ahorra lecturas.", grupo, espera=5.5)
