class Clip4(Scene):
    """6.2.4 - PSP (Parameter Sensitive Plan, SQL Server 2022+) decide SOLO
    si crea variantes del plan cuando detecta sesgo entre los dos clientes;
    en esta tienda no se activo: 0 variantes (medido, ambar). Moraleja: la
    heuristica automatica no sustituye un buen indice (el del clip 3).
    Cierre de la leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La ayuda que no llego"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- PSP: una funcion automatica que decide sola --------------------
        psp = S.operador("PSP", color=C_CREE, ancho=2.0, alto=0.85,
                         font_size=26)
        psp.move_to(UP * 1.75)
        et_psp = tag_junto(psp, "decide solo", DOWN, buff=0.22, color=C_CREE)
        self.play(FadeIn(psp), run_time=0.6)
        self.play(FadeIn(et_psp), run_time=0.4)
        self.wait(0.8)

        c501 = caja_cliente("501", color=C_TENUE, ancho=1.4)
        c501.move_to(LEFT * 3.6 + DOWN * 0.6)
        et501 = tag_junto(c501, "cliente 501", DOWN, buff=0.2)
        c1 = caja_cliente("mayorista", color=C_TENUE, ancho=2.3)
        c1.move_to(RIGHT * 3.5 + DOWN * 0.6)
        et1 = tag_junto(c1, "el mayorista", DOWN, buff=0.2)
        self.play(FadeIn(c501), FadeIn(et501), FadeIn(c1), FadeIn(et1),
                  run_time=0.7)
        self.wait(0.5)

        f1 = Arrow(c501.get_top(), psp.get_bottom() + LEFT * 0.5, buff=0.1,
                  stroke_width=2.4, color=C_TENUE,
                  max_tip_length_to_length_ratio=0.2)
        f2 = Arrow(c1.get_top(), psp.get_bottom() + RIGHT * 0.5, buff=0.1,
                  stroke_width=2.4, color=C_TENUE,
                  max_tip_length_to_length_ratio=0.2)
        self.play(Create(f1), Create(f2), run_time=0.7)
        self.wait(1.0)

        # --- variantes posibles: tres huecos vacios --------------------------
        huecos = VGroup(*[RoundedRectangle(width=1.1, height=0.7,
                                           corner_radius=0.08,
                                           stroke_color=C_TENUE,
                                           stroke_width=1.6,
                                           stroke_opacity=0.55)
                          for _ in range(3)])
        huecos.arrange(RIGHT, buff=0.35).move_to(RIGHT * 3.4 + UP * 1.75)
        et_huecos = tag_junto(huecos, "variantes posibles", UP, buff=0.22)
        f3 = Arrow(psp.get_right(), huecos.get_left(), buff=0.1,
                  stroke_width=2.0, color=C_CREE,
                  max_tip_length_to_length_ratio=0.2)
        self.play(Create(f3), FadeIn(huecos), FadeIn(et_huecos), run_time=0.8)
        self.wait(1.4)

        # --- pero aqui se quedan vacios: 0 variantes (medido) ----------------
        equis = VGroup(*[
            VGroup(
                Line(h.get_corner(UP + LEFT) + RIGHT * 0.08 + DOWN * 0.08,
                    h.get_corner(DOWN + RIGHT) + LEFT * 0.08 + UP * 0.08,
                    stroke_color=C_MOTOR, stroke_width=2.5),
                Line(h.get_corner(UP + RIGHT) + LEFT * 0.08 + DOWN * 0.08,
                    h.get_corner(DOWN + LEFT) + RIGHT * 0.08 + UP * 0.08,
                    stroke_color=C_MOTOR, stroke_width=2.5))
            for h in huecos])
        self.play(Create(equis), run_time=0.7)
        rot.mostrar(motor_pie(f"{S.miles(PSP_VARIANTES)} variantes"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- moraleja: lo automatico no basta; el indice si -----------------
        primero = VGroup(psp, et_psp, c501, et501, c1, et1, f1, f2, f3,
                         huecos, et_huecos, equis)
        self.play(FadeOut(primero), run_time=0.7)
        rot.limpiar("abajo", run_time=0.3)

        seek = S.operador("Seek", color=C_BUENO, ancho=2.2, alto=0.85,
                          font_size=24)
        seek.move_to(UP * 0.3)
        et_seek = tag_junto(seek, "un indice si", DOWN, buff=0.24,
                            color=C_BUENO)
        self.play(FadeIn(seek, shift=UP * 0.15), run_time=0.6)
        self.play(FadeIn(et_seek), run_time=0.4)
        self.wait(3.5)

        cierre_leccion(self, rot, "El mejor remedio",
                       "es un indice que sirva a todos.",
                       seek, et_seek, espera=9.0)
