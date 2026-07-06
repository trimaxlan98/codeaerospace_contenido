from manim import *


class ModelosOsiYTcpip(Scene):
    def construct(self):
        titulo = Text("Modelos OSI y TCP/IP", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Pila OSI de 7 capas
        capas_osi = ["Aplicación", "Presentación", "Sesión", "Transporte",
                     "Red", "Enlace", "Física"]
        colores = [GOLD, GOLD, GOLD, YELLOW, BLUE_B, BLUE_D, GREY_B]
        osi = VGroup()
        for nombre, color in zip(capas_osi, colores):
            caja = Rectangle(width=2.6, height=0.52, color=color,
                             fill_opacity=0.15, fill_color=color)
            txt = Text(nombre, font_size=17, color=color).move_to(caja)
            osi.add(VGroup(caja, txt))
        osi.arrange(DOWN, buff=0.06).move_to(LEFT * 4 + DOWN * 0.55)
        osi_txt = Text("OSI (7 capas)", font_size=22, color=GREY_B).next_to(osi, UP, buff=0.2)
        self.play(FadeIn(osi_txt), LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3)
                                                 for c in osi], lag_ratio=0.12),
                  run_time=2.5)

        # Pila TCP/IP de 4 capas y su correspondencia
        capas_tcp = [("Aplicación", 3, GOLD), ("Transporte", 1, YELLOW),
                     ("Internet", 1, BLUE_B), ("Acceso a red", 2, BLUE_D)]
        tcp = VGroup()
        for nombre, peso, color in capas_tcp:
            caja = Rectangle(width=2.6, height=0.52 * peso + 0.06 * (peso - 1),
                             color=color, fill_opacity=0.15, fill_color=color)
            txt = Text(nombre, font_size=17, color=color).move_to(caja)
            tcp.add(VGroup(caja, txt))
        tcp.arrange(DOWN, buff=0.06).move_to(RIGHT * 0.4 + DOWN * 0.55)
        tcp_txt = Text("TCP/IP (4 capas)", font_size=22, color=GREY_B).next_to(tcp, UP, buff=0.2)
        self.play(FadeIn(tcp_txt), LaggedStart(*[FadeIn(c, shift=LEFT * 0.3)
                                                 for c in tcp], lag_ratio=0.2),
                  run_time=2)
        mapa = VGroup(*[
            DashedLine(osi[i][0].get_right(), tcp[j][0].get_left(), color=GREY_B,
                       stroke_opacity=0.6)
            for i, j in [(0, 0), (1, 0), (2, 0), (3, 1), (4, 2), (5, 3), (6, 3)]
        ])
        self.play(Create(mapa), run_time=1.5)

        # Encapsulamiento: los datos van ganando cabeceras
        dato = Rectangle(width=0.9, height=0.4, color=WHITE, fill_opacity=0.3,
                         fill_color=WHITE)
        dato.move_to(RIGHT * 4.3 + UP * 1.9)
        dato_txt = Text("datos", font_size=15, color=WHITE).move_to(dato)
        paquete = VGroup(dato, dato_txt)
        enc_txt = Text("Encapsulamiento", font_size=21, color=YELLOW)
        enc_txt.next_to(paquete, UP, buff=0.25)
        self.play(FadeIn(paquete), FadeIn(enc_txt), run_time=1)

        for etiqueta, color, dy in [("TCP", YELLOW, 1.1), ("IP", BLUE_B, 2.2),
                                    ("Eth", BLUE_D, 3.3)]:
            cab = Rectangle(width=0.55, height=0.4, color=color, fill_opacity=0.4,
                            fill_color=color)
            cab.next_to(paquete, LEFT, buff=0)
            cab_txt = Text(etiqueta, font_size=14, color=WHITE).move_to(cab)
            self.play(paquete.animate.shift(DOWN * 1.1), run_time=0.6)
            cab.shift(DOWN * 0)
            cab.next_to(paquete, LEFT, buff=0)
            self.play(FadeIn(VGroup(cab, cab_txt), shift=RIGHT * 0.2), run_time=0.7)
            paquete = VGroup(cab, cab_txt, *paquete)

        cierre = Text("Cada capa habla solo con su par: por eso Internet es intercambiable",
                      font_size=21, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
