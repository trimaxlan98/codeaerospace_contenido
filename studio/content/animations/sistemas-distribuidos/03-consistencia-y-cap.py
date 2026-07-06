from manim import *


class ConsistenciaYElTeoremaCap(Scene):
    def construct(self):
        titulo = Text("Consistencia y el teorema CAP", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Triangulo CAP
        v_c = UP * 1.9 + LEFT * 3.6
        v_a = DOWN * 1.6 + LEFT * 5.4
        v_p = DOWN * 1.6 + LEFT * 1.8
        tri = Polygon(v_c, v_a, v_p, color=GREY_B)
        lc = Text("C: consistencia", font_size=20, color=BLUE_B).next_to(v_c, UP, buff=0.15)
        la = Text("A: disponibilidad", font_size=20, color=GOLD).next_to(v_a, DOWN, buff=0.15)
        lp = Text("P: tolerancia a particiones", font_size=20, color=YELLOW)
        lp.next_to(v_p, DOWN, buff=0.15).shift(RIGHT * 0.6)
        self.play(Create(tri), FadeIn(lc), FadeIn(la), FadeIn(lp), run_time=2)
        regla = Text("Con la red partida, solo puedes quedarte con dos",
                     font_size=21, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(regla), run_time=1)

        # Dos replicas con un valor
        r1 = VGroup(Circle(radius=0.5, color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B),
                    Text("x = 5", font_size=20, color=WHITE)).move_to(RIGHT * 2.0 + UP * 0.9)
        r2 = VGroup(Circle(radius=0.5, color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B),
                    Text("x = 5", font_size=20, color=WHITE)).move_to(RIGHT * 5.4 + UP * 0.9)
        red = Line(r1.get_right(), r2.get_left(), color=GREY_B)
        self.play(FadeIn(r1), FadeIn(r2), Create(red), run_time=1.5)

        # Particion de red
        rayo = Line(RIGHT * 3.7 + UP * 1.7, RIGHT * 3.7 + UP * 0.1, color=RED_D,
                    stroke_width=6)
        part = Text("¡Partición!", font_size=20, color=RED_D)
        part.next_to(rayo, UP, buff=0.15)
        self.play(Create(rayo), FadeIn(part), red.animate.set_stroke(opacity=0.15),
                  run_time=1.2)

        # Opcion CP: rechazar escrituras para no divergir
        cp = Text("Elegir C (CP): la réplica aislada rechaza escrituras → consistente pero no disponible",
                  font_size=18, color=BLUE_B).to_edge(DOWN)
        cliente = Text("escribir x=9", font_size=17, color=WHITE)
        cliente.next_to(r2, UP, buff=0.5)
        no = Text("rechazado", font_size=17, color=RED_D).next_to(r2, DOWN, buff=0.3)
        self.play(ReplacementTransform(regla, cp), FadeIn(cliente), run_time=1.2)
        self.play(FadeIn(no), Indicate(r2, color=RED_D), run_time=1.2)
        self.play(FadeOut(cliente), FadeOut(no), run_time=0.6)

        # Opcion AP: aceptar y divergir
        ap = Text("Elegir A (AP): ambas aceptan escrituras → disponible pero los valores divergen",
                  font_size=18, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(cp, ap), run_time=1.2)
        nuevo1 = Text("x = 7", font_size=20, color=GOLD).move_to(r1[1])
        nuevo2 = Text("x = 9", font_size=20, color=GOLD).move_to(r2[1])
        self.play(Transform(r1[1], nuevo1), Transform(r2[1], nuevo2), run_time=1.2)
        self.play(Wiggle(r1), Wiggle(r2), run_time=1.5)

        # Al sanar: reconciliacion / consistencia eventual
        sana = Text("Al sanar la red: reconciliar versiones → consistencia eventual",
                    font_size=19, color=YELLOW).to_edge(DOWN)
        self.play(ReplacementTransform(ap, sana), FadeOut(rayo), FadeOut(part),
                  red.animate.set_stroke(opacity=1), run_time=1.5)
        final1 = Text("x = 9", font_size=20, color=WHITE).move_to(r1[1])
        self.play(Transform(r1[1], final1), Flash(r1, color=YELLOW), run_time=1.2)

        cierre = Text("CAP no es un dogma: es el precio de una red imperfecta, pagado por diseño",
                      font_size=19, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(sana, cierre), run_time=1.2)
        self.wait(2)
