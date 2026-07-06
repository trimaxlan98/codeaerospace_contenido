from manim import *


class MemoriaYGestionDeContexto(Scene):
    def construct(self):
        titulo = Text("Memoria y gestión de contexto", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # La ventana de contexto: un contenedor finito
        ventana = Rectangle(width=2.8, height=4.2, color=BLUE_B)
        ventana.move_to(LEFT * 4.2 + DOWN * 0.6)
        v_txt = Text("ventana de contexto", font_size=18, color=BLUE_B)
        v_txt.next_to(ventana, UP, buff=0.2)
        lim_txt = Text("(finita: todo lo que el\nmodelo 've' a la vez)",
                       font_size=15, color=GREY_B, line_spacing=0.85)
        lim_txt.next_to(v_txt, RIGHT, buff=0.3)
        self.play(Create(ventana), FadeIn(v_txt), FadeIn(lim_txt), run_time=1.5)

        # Se va llenando con turnos de conversacion
        bloques = VGroup()
        contenidos = [("sistema", GOLD), ("turno 1", GREY_B), ("turno 2", GREY_B),
                      ("turno 3", GREY_B), ("herramienta", YELLOW),
                      ("turno 4", GREY_B), ("turno 5", GREY_B)]
        for nombre, color in contenidos:
            b = Rectangle(width=2.5, height=0.48, color=color, fill_opacity=0.2,
                          fill_color=color)
            t = Text(nombre, font_size=15, color=color).move_to(b)
            bloques.add(VGroup(b, t))
        bloques.arrange(DOWN, buff=0.06)
        bloques.move_to(ventana.get_top() + DOWN * (len(bloques) * 0.27 + 0.15))
        for b in bloques[:5]:
            self.play(FadeIn(b, shift=DOWN * 0.2), run_time=0.5)

        # Desborde: ya no cabe todo
        self.play(FadeIn(bloques[5], shift=DOWN * 0.2), run_time=0.5)
        bloques[6].next_to(bloques[5], DOWN, buff=0.06)
        self.play(FadeIn(bloques[6], shift=DOWN * 0.2), run_time=0.5)
        alerta = Text("¡desborde!", font_size=18, color=RED_D)
        alerta.next_to(ventana, DOWN, buff=0.15)
        self.play(FadeIn(alerta), Wiggle(ventana), run_time=1.2)

        # Estrategia 1: resumir lo viejo
        resumen_txt = Text("Estrategia 1: comprimir lo viejo en un resumen",
                           font_size=20, color=YELLOW).to_edge(DOWN)
        resumen = VGroup(
            Rectangle(width=2.5, height=0.48, color=YELLOW, fill_opacity=0.25,
                      fill_color=YELLOW),
            Text("resumen(1-3)", font_size=15, color=YELLOW),
        )
        resumen[1].move_to(resumen[0])
        resumen.move_to(bloques[1].get_center())
        self.play(FadeIn(resumen_txt), run_time=0.8)
        self.play(ReplacementTransform(VGroup(bloques[1], bloques[2], bloques[3]),
                                       resumen), run_time=1.5)
        resto = VGroup(bloques[4], bloques[5], bloques[6])
        self.play(resto.animate.arrange(DOWN, buff=0.06)
                  .next_to(resumen, DOWN, buff=0.06), FadeOut(alerta), run_time=1.2)

        # Estrategia 2: memoria externa con recuperacion
        mem_txt = Text("Estrategia 2: memoria externa — guardar fuera y recuperar lo relevante",
                       font_size=19, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(resumen_txt, mem_txt), run_time=1)
        disco = VGroup(
            Ellipse(width=2.1, height=0.5, color=GOLD),
            Line(LEFT * 1.05 + DOWN * 0.7, LEFT * 1.05, color=GOLD),
            Line(RIGHT * 1.05 + DOWN * 0.7, RIGHT * 1.05, color=GOLD),
            Arc(radius=1.05, start_angle=PI, angle=PI, color=GOLD).stretch(0.24, 1)
            .shift(DOWN * 0.7),
        ).move_to(RIGHT * 3.6 + UP * 0.7)
        disco_txt = Text("memoria persistente\n(archivos, vectores)", font_size=16,
                         color=GOLD, line_spacing=0.85).next_to(disco, DOWN, buff=0.25)
        guardar = Arrow(ventana.get_right() + UP * 1.2, disco.get_left(), color=GREY_B,
                        buff=0.2)
        g_txt = Text("guardar", font_size=15, color=GREY_B)
        g_txt.next_to(guardar, UP, buff=0.08)
        traer = Arrow(disco.get_left() + DOWN * 0.4, ventana.get_right() + DOWN * 0.4,
                      color=YELLOW, buff=0.2)
        t_txt = Text("recuperar solo lo relevante", font_size=15, color=YELLOW)
        t_txt.next_to(traer, DOWN, buff=0.08)
        self.play(FadeIn(disco), FadeIn(disco_txt), run_time=1.2)
        self.play(GrowArrow(guardar), FadeIn(g_txt), run_time=1)
        self.play(GrowArrow(traer), FadeIn(t_txt), run_time=1)

        cierre = Text("Gestionar contexto es decidir qué recordar, qué resumir y qué olvidar",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(mem_txt, cierre), run_time=1.2)
        self.wait(2)
