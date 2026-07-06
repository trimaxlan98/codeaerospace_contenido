from manim import *


class EthernetYConmutacionLan(Scene):
    def construct(self):
        titulo = Text("Ethernet y conmutación LAN", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Switch central con 4 hosts
        switch = Rectangle(width=1.8, height=0.7, color=GOLD, fill_opacity=0.2,
                           fill_color=GOLD).move_to(DOWN * 0.4)
        sw_txt = Text("Switch", font_size=20, color=GOLD).move_to(switch)
        hosts = {
            "A": LEFT * 4.5 + UP * 1.2, "B": RIGHT * 4.5 + UP * 1.2,
            "C": LEFT * 4.5 + DOWN * 2.2, "D": RIGHT * 4.5 + DOWN * 2.2,
        }
        cajas = VGroup()
        for nombre, p in hosts.items():
            c = Square(side_length=0.6, color=BLUE_B, fill_opacity=0.2, fill_color=BLUE_B)
            c.move_to(p)
            t = Text(nombre, font_size=22, color=BLUE_B).move_to(c)
            cajas.add(VGroup(c, t))
        cables = VGroup(*[
            Line(switch.get_center(), p, color=GREY_B, stroke_opacity=0.6, z_index=-1)
            for p in hosts.values()
        ])
        self.play(FadeIn(switch), FadeIn(sw_txt), Create(cables),
                  LaggedStart(*[FadeIn(c) for c in cajas], lag_ratio=0.15), run_time=2.5)

        # Trama Ethernet
        trama = VGroup()
        for campo, ancho, color in [("MAC dst", 1.1, BLUE_B), ("MAC src", 1.1, BLUE_D),
                                    ("tipo", 0.6, GREY_B), ("datos", 1.6, WHITE),
                                    ("CRC", 0.6, GOLD)]:
            r = Rectangle(width=ancho, height=0.45, color=color, fill_opacity=0.2,
                          fill_color=color)
            t = Text(campo, font_size=14, color=color).move_to(r)
            trama.add(VGroup(r, t))
        trama.arrange(RIGHT, buff=0).to_edge(UP).shift(DOWN * 1.1)
        trama_txt = Text("Trama Ethernet", font_size=18, color=GREY_B)
        trama_txt.next_to(trama, DOWN, buff=0.12)
        self.play(FadeIn(trama, lag_ratio=0.15), FadeIn(trama_txt), run_time=1.8)

        # Primer envio A->D: el switch no conoce a D, inunda
        tabla_titulo = Text("Tabla MAC", font_size=18, color=GOLD)
        tabla_titulo.move_to(RIGHT * 1.9 + DOWN * 0.2 + RIGHT * 0.6)
        tabla = VGroup(tabla_titulo)
        flood_txt = Text("1) Destino desconocido → inunda todos los puertos",
                         font_size=20, color=YELLOW).to_edge(DOWN)
        f1 = Dot(hosts["A"], color=YELLOW, radius=0.09)
        self.play(FadeIn(flood_txt), FadeIn(f1), run_time=0.8)
        self.play(f1.animate.move_to(switch.get_center()), run_time=0.8)
        copias = VGroup(*[Dot(switch.get_center(), color=YELLOW, radius=0.09)
                          for _ in range(3)])
        self.add(copias)
        self.play(copias[0].animate.move_to(hosts["B"]),
                  copias[1].animate.move_to(hosts["C"]),
                  copias[2].animate.move_to(hosts["D"]),
                  FadeOut(f1), run_time=1.2)
        aprendio = Text("A → puerto 1", font_size=17, color=GREY_B)
        aprendio.next_to(tabla_titulo, DOWN, buff=0.15)
        self.play(FadeIn(aprendio), FadeOut(copias), run_time=0.8)

        # Respuesta D->A: ahora conmutacion exacta
        unicast_txt = Text("2) Ya aprendió las direcciones → reenvía solo al puerto correcto",
                           font_size=20, color=BLUE_B).to_edge(DOWN)
        aprendio2 = Text("D → puerto 4", font_size=17, color=GREY_B)
        aprendio2.next_to(aprendio, DOWN, buff=0.12)
        f2 = Dot(hosts["D"], color=BLUE_B, radius=0.09)
        self.play(ReplacementTransform(flood_txt, unicast_txt), FadeIn(f2),
                  FadeIn(aprendio2), run_time=1)
        self.play(f2.animate.move_to(switch.get_center()), run_time=0.8)
        self.play(f2.animate.move_to(hosts["A"]), run_time=0.8)
        self.play(Flash(cajas[0], color=BLUE_B), FadeOut(f2), run_time=0.8)

        cierre = Text("El switch aprende MACs y crea un camino dedicado por trama: adiós colisiones",
                      font_size=19, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(unicast_txt, cierre), run_time=1.2)
        self.wait(2)
