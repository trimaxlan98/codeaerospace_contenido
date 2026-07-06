from manim import *


class TransporteTcpUdpQuic(Scene):
    def construct(self):
        titulo = Text("Transporte: TCP, UDP y QUIC", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Tres columnas: cliente/servidor por protocolo
        def columna(x, nombre, color):
            cli = Line(UP * 1.9 + RIGHT * (x - 1.15), DOWN * 2.4 + RIGHT * (x - 1.15),
                       color=GREY_B)
            srv = Line(UP * 1.9 + RIGHT * (x + 1.15), DOWN * 2.4 + RIGHT * (x + 1.15),
                       color=GREY_B)
            head = Text(nombre, font_size=24, color=color)
            head.move_to(UP * 2.3 + RIGHT * x)
            return VGroup(cli, srv, head)

        col_tcp = columna(-4.4, "TCP + TLS", BLUE_B)
        col_udp = columna(0, "UDP", GREY_B)
        col_quic = columna(4.4, "QUIC", GOLD)
        self.play(FadeIn(col_tcp), FadeIn(col_udp), FadeIn(col_quic), run_time=1.5)

        def mensaje(x, y0, y1, texto, color, hacia_derecha=True):
            x_a, x_b = x - 1.15, x + 1.15
            if not hacia_derecha:
                x_a, x_b = x_b, x_a
            fl = Arrow([x_a, y0, 0], [x_b, y1, 0], color=color, buff=0.05,
                       stroke_width=3, max_tip_length_to_length_ratio=0.1)
            t = Text(texto, font_size=15, color=color)
            t.move_to([(x_a + x_b) / 2, (y0 + y1) / 2 + 0.18, 0])
            return VGroup(fl, t)

        # TCP: 3 vias + TLS = lento en arrancar
        tcp_msgs = [
            mensaje(-4.4, 1.6, 1.3, "SYN", BLUE_B),
            mensaje(-4.4, 1.2, 0.9, "SYN-ACK", BLUE_B, False),
            mensaje(-4.4, 0.8, 0.5, "ACK", BLUE_B),
            mensaje(-4.4, 0.4, 0.1, "TLS hello", YELLOW),
            mensaje(-4.4, 0.0, -0.3, "TLS ok", YELLOW, False),
            mensaje(-4.4, -0.5, -0.8, "datos", WHITE),
        ]
        for m in tcp_msgs:
            self.play(GrowArrow(m[0]), FadeIn(m[1]), run_time=0.55)
        tcp_nota = Text("fiable y ordenado,\npero 2-3 viajes antes del dato",
                        font_size=17, color=BLUE_B, line_spacing=0.85)
        tcp_nota.move_to(DOWN * 3.05 + LEFT * 4.4)
        self.play(FadeIn(tcp_nota), run_time=0.8)

        # UDP: sin apreton de manos
        udp_msgs = [
            mensaje(0, 1.6, 1.3, "datos", WHITE),
            mensaje(0, 1.1, 0.8, "datos", WHITE),
            mensaje(0, 0.6, 0.3, "datos (perdido)", RED_D),
        ]
        for m in udp_msgs:
            self.play(GrowArrow(m[0]), FadeIn(m[1]), run_time=0.55)
        cruz = Cross(scale_factor=0.18).move_to([1.15, 0.3, 0])
        self.play(Create(cruz), run_time=0.5)
        udp_nota = Text("sin garantías, sin espera:\nideal para voz y juegos",
                        font_size=17, color=GREY_B, line_spacing=0.85)
        udp_nota.move_to(DOWN * 3.05)
        self.play(FadeIn(udp_nota), run_time=0.8)

        # QUIC: transporte + cifrado en 1 viaje, sobre UDP
        quic_msgs = [
            mensaje(4.4, 1.6, 1.3, "hello + clave", GOLD),
            mensaje(4.4, 1.2, 0.9, "ok + clave", GOLD, False),
            mensaje(4.4, 0.8, 0.5, "datos cifrados", WHITE),
            mensaje(4.4, 0.4, 0.1, "datos cifrados", WHITE),
        ]
        for m in quic_msgs:
            self.play(GrowArrow(m[0]), FadeIn(m[1]), run_time=0.55)
        quic_nota = Text("cifrado y multiplexado\nen 1 viaje (HTTP/3)",
                         font_size=17, color=GOLD, line_spacing=0.85)
        quic_nota.move_to(DOWN * 3.05 + RIGHT * 4.4)
        self.play(FadeIn(quic_nota), run_time=0.8)

        self.play(Circumscribe(col_quic[2], color=GOLD), run_time=1.2)
        self.wait(2)
