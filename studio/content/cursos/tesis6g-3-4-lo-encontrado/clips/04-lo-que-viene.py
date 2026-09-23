class Clip4(Scene):
    """3.4.4 - Lo que viene: llevar el marco a un simulador con orbitas
    reales y preguntar si el margen sobrevive al realismo (si no, tambien es
    un resultado); y el reloj: el estandar 6G se congela, potencialmente, a
    inicios de 2029, y la defensa cae justo despues. Cierre del curso.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Lo que viene"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        X0, X1, Y0, Y1, MAX = -5.6, 5.4, -1.9, 2.3, 0.45
        y_de = lambda m: Y0 + (Y1 - Y0) * m / MAX
        ex = Line([X0, Y0, 0], [X1, Y0, 0], stroke_color=C_TENUE, stroke_width=2).add_tip(tip_length=0.2)
        ey = Line([X0, Y0, 0], [X0, Y1, 0], stroke_color=C_TENUE, stroke_width=2)
        tx = tag_hud("realismo", font_size=17, color=C_TENUE).next_to(ex, DOWN, buff=0.12).align_to(ex, RIGHT)
        ty = tag_hud("margen", font_size=17, color=C_TENUE).next_to(ey, UP, buff=0.1).align_to(ey, LEFT)
        yu = y_de(D["umbral"])
        um = DashedLine([X0, yu, 0], [X1 - 0.2, yu, 0], dash_length=0.14, stroke_color=CODE_INK, stroke_width=3)
        self.play(Create(ex), Create(ey), FadeIn(tx), FadeIn(ty), Create(um), run_time=1.0)
        v1 = Dot([X0 + 1.3, y_de(D["g0_ma"]), 0], radius=0.13, color=C_NO)
        v2 = Dot([X0 + 2.9, y_de(D["g1_ma"]), 0], radius=0.13, color=C_OK)
        e1 = tag_hud("v1", font_size=18, color=C_NO).next_to(v1, UP, buff=0.12)
        e2 = tag_hud("v2 hoy", font_size=18, color=C_OK).next_to(v2, UP, buff=0.12)
        self.play(FadeIn(v1), FadeIn(e1), FadeIn(v2), FadeIn(e2), run_time=0.8)
        rot.mostrar(dato_pie("2 satelites y 1 gateway"), zona="abajo", run_time=0.5)
        self.wait(2.8)
        x3 = X1 - 1.6
        abanico = VGroup(*[DashedLine(v2.get_center(), [x3, y_de(m), 0], dash_length=0.12, stroke_color=C_TENUE,
                                      stroke_width=2.5) for m in (0.38, 0.30, 0.22, 0.12, 0.05)])
        q = VGroup(DashedVMobject(Circle(radius=0.32, stroke_color=CODE_INK, stroke_width=3), num_dashes=14),
                   Text("?", font=FUENTE_HUD, font_size=30, color=CODE_INK)).move_to([x3, y_de(0.215), 0])
        e3 = tag_hud("orbitas reales", font_size=18, color=CODE_INK).next_to(abanico, UP, buff=0.15).set_x(x3 - 0.9)
        self.play(Create(abanico), run_time=1.6)
        self.play(FadeIn(q), FadeIn(e3), run_time=0.6)
        rot.mostrar(dato_pie("si no sobrevive, es resultado"), zona="abajo", run_time=0.5)
        self.wait(4.0)

        # el reloj
        grafica = VGroup(ex, ey, tx, ty, um, v1, v2, e1, e2, abanico, q, e3)
        self.play(FadeOut(grafica), run_time=0.8)
        A0, A1, XL0, XL1, YL = 2026.0, 2030.5, -5.8, 5.8, -0.2
        xa = lambda a: XL0 + (XL1 - XL0) * (a - A0) / (A1 - A0)
        riel = Line([XL0, YL, 0], [XL1, YL, 0], stroke_color=C_TIERRA, stroke_width=12)
        anios = VGroup(*[tag_hud(str(a), font_size=17, color=C_TENUE).move_to([xa(a), YL + 0.55, 0]) for a in range(2026, 2031)])
        hecho = Line([xa(T6.INICIO_DOCTORADO), YL, 0], [xa(H["hoy"]["anio"]), YL, 0], stroke_color=C_ADAPTA, stroke_width=12)
        self.play(Create(riel), FadeIn(anios), run_time=0.8)
        self.play(Create(hecho), run_time=1.0)

        def hito(k, col, alto=1.0):
            x = xa(H[k]["anio"])
            return VGroup(Dot([x, YL, 0], radius=0.13, color=col),
                          Line([x, YL - 0.18, 0], [x, YL - alto, 0], stroke_color=col, stroke_width=2.5),
                          tag_hud(H[k]["texto"].lower(), font_size=18, color=col).move_to([x, YL - alto - 0.25, 0]))
        for k, col, alto in (("hoy", C_ADAPTA, 0.8), ("freeze", C_PRIV, 1.0), ("defensa", C_OK, 1.0)):
            self.play(GrowFromCenter(hito(k, col, alto)), run_time=0.6)
            self.wait(1.0)
        rot.mostrar(dato_pie("3GPP: 6G, inicios de 2029"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        cierre_leccion(self, rot, "Que gane o que pierda.",
                       "Que la medicion signifique algo.",
                       *[m for m in self.mobjects if m not in (self.mobjects[0],)][2:])
