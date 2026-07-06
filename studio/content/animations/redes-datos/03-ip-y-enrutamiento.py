from manim import *


class IpYEnrutamiento(Scene):
    def construct(self):
        titulo = Text("IP y enrutamiento", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Topologia de routers
        pos = {
            "H1": LEFT * 5.6 + DOWN * 1.8, "R1": LEFT * 3.2 + DOWN * 0.4,
            "R2": LEFT * 0.4 + UP * 1.3, "R3": LEFT * 0.4 + DOWN * 1.9,
            "R4": RIGHT * 2.5 + DOWN * 0.3, "H2": RIGHT * 5.4 + DOWN * 1.6,
        }
        nodos = VGroup()
        for nombre, p in pos.items():
            es_host = nombre.startswith("H")
            c = (Square(side_length=0.55, color=BLUE_B, fill_opacity=0.2, fill_color=BLUE_B)
                 if es_host else Circle(radius=0.33, color=GOLD, fill_opacity=0.15,
                                        fill_color=GOLD))
            c.move_to(p)
            t = Text(nombre, font_size=18, color=BLUE_B if es_host else GOLD).move_to(c)
            nodos.add(VGroup(c, t))
        enlaces = [("H1", "R1"), ("R1", "R2"), ("R1", "R3"), ("R2", "R4"),
                   ("R3", "R4"), ("R4", "H2")]
        lineas = VGroup(*[Line(pos[u], pos[v], color=GREY_B, stroke_opacity=0.5,
                               z_index=-1) for u, v in enlaces])
        self.play(Create(lineas), LaggedStart(*[FadeIn(n) for n in nodos],
                                              lag_ratio=0.12), run_time=2.5)

        ips = Text("H1: 10.0.1.7        H2: 10.0.9.20", font_size=20, color=GREY_B)
        ips.next_to(titulo, DOWN, buff=0.25)
        self.play(FadeIn(ips), run_time=0.8)

        # Tabla de rutas de R1: prefijo mas largo gana
        tabla = VGroup(
            Text("Tabla de R1", font_size=19, color=GOLD),
            Text("10.0.0.0/16   → R3", font_size=18, color=GREY_B),
            Text("10.0.9.0/24   → R2", font_size=18, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
        tabla.move_to(LEFT * 3.6 + UP * 1.9)
        caja = SurroundingRectangle(tabla, color=GOLD, buff=0.2)
        self.play(FadeIn(tabla), Create(caja), run_time=1.5)

        # Paquete con TTL que viaja por saltos
        nota = Text("El paquete se decide salto a salto: gana el prefijo más específico",
                    font_size=20, color=YELLOW).to_edge(DOWN)
        paquete = Square(side_length=0.22, color=YELLOW, fill_opacity=1,
                         fill_color=YELLOW).move_to(pos["H1"])
        ttl = Integer(64, font_size=24, color=WHITE).next_to(paquete, UP, buff=0.12)
        ttl_txt = Text("TTL", font_size=14, color=GREY_B).next_to(ttl, RIGHT, buff=0.08)
        self.play(FadeIn(nota), FadeIn(paquete), FadeIn(ttl), FadeIn(ttl_txt), run_time=1)

        ruta = ["R1", "R2", "R4", "H2"]
        valor = 64
        for salto in ruta:
            valor -= 1
            self.play(
                paquete.animate.move_to(pos[salto]),
                ttl.animate.set_value(valor).next_to(pos[salto], UP, buff=0.35),
                ttl_txt.animate.next_to(pos[salto] + UP * 0.35 + RIGHT * 0.28, RIGHT,
                                        buff=0.05),
                run_time=1.1, rate_func=linear,
            )
            if salto == "R1":
                self.play(Indicate(tabla[2], color=YELLOW), run_time=1)
        self.play(Flash(nodos[5], color=YELLOW), run_time=0.8)

        # Que pasa si un enlace cae: la red converge
        caida = Cross(scale_factor=0.25).move_to(lineas[3].get_center())
        converge = Text("Si un enlace cae, los protocolos (OSPF/BGP) recalculan rutas",
                        font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(Create(caida), lineas[3].animate.set_stroke(opacity=0.15),
                  ReplacementTransform(nota, converge), run_time=1.3)
        paquete2 = Square(side_length=0.22, color=BLUE_B, fill_opacity=1,
                          fill_color=BLUE_B).move_to(pos["H1"])
        self.play(FadeIn(paquete2), FadeOut(ttl), FadeOut(ttl_txt), run_time=0.5)
        for salto in ["R1", "R3", "R4", "H2"]:
            self.play(paquete2.animate.move_to(pos[salto]), run_time=0.8,
                      rate_func=linear)
        self.wait(2)
