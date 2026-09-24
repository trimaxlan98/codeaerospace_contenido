class Clip4(Scene):
    """3.2.4 - El duelo final de la leccion: dieciocho mil lecturas contra
    tres, en escala log10, para el mismo ticket. Cierre. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El ticket, antes y despues"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        largo = 8.0
        maximo = M["ticket_sin_indice"]
        base_x = LEFT * 4.6

        bar_verde = S.barra_lecturas(M["ticket_con_indice"], maximo, largo=largo,
                                     alto=0.55, color=C_BUENO, log=True)
        bar_verde.shift(base_x + UP * 0.9)
        bar_rojo = S.barra_lecturas(M["ticket_sin_indice"], maximo, largo=largo,
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
        tag_v = tag_motor(lecturas(M["ticket_con_indice"]))
        tag_v.next_to(bar_verde, RIGHT, buff=0.2)
        tag_r = tag_motor(lecturas(M["ticket_sin_indice"]))
        tag_r.next_to(bar_rojo, RIGHT, buff=0.2)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(0.8)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(4.0)

        # el carril de abajo solo lleva la razon (cian): no duplica el ambar
        rot.mostrar(cifra_pie(f"{S.miles(round(RAZON_TICKET))}x mas lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(bar_rojo, color=C_MALO, scale_factor=1.03),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(7.5)

        grupo = VGroup(base, aviso, bar_verde, bar_rojo, lab_v, lab_r, tag_v, tag_r)
        cierre_leccion(self, rot, "Toda llave foranea pide indice.",
                       "Y lo raro, un indice filtrado.", grupo, espera=6.0)
