from manim import *


class ArquitecturasDistribuidasModernas(Scene):
    def construct(self):
        titulo = Text("Arquitecturas distribuidas modernas",
                      font_size=32, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Monolito
        mono = Rectangle(width=2.2, height=2.4, color=GREY_B, fill_opacity=0.12,
                         fill_color=GREY_B).move_to(LEFT * 4.6 + DOWN * 0.5)
        mono_txt = Text("Monolito", font_size=21, color=GREY_B).next_to(mono, UP, buff=0.2)
        partes = VGroup(*[
            Text(t, font_size=16, color=GREY_B) for t in
            ["ventas", "usuarios", "pagos", "envíos"]
        ]).arrange(DOWN, buff=0.22).move_to(mono)
        self.play(Create(mono), FadeIn(mono_txt), FadeIn(partes), run_time=1.8)
        pro = Text("simple de operar, difícil de escalar por partes",
                   font_size=18, color=GREY_B).to_edge(DOWN)
        self.play(FadeIn(pro), run_time=1)

        # Microservicios: cada parte es un servicio independiente
        micro_txt = Text("Microservicios", font_size=21, color=BLUE_B)
        micro_txt.move_to(RIGHT * 2.6 + UP * 1.9)
        servicios = VGroup()
        destinos = [RIGHT * 0.8 + UP * 0.9, RIGHT * 3.0 + UP * 0.9,
                    RIGHT * 0.8 + DOWN * 0.7, RIGHT * 3.0 + DOWN * 0.7]
        for texto, p in zip(["ventas", "usuarios", "pagos", "envíos"], destinos):
            s = VGroup(
                RoundedRectangle(width=1.7, height=0.75, corner_radius=0.12,
                                 color=BLUE_B, fill_opacity=0.12, fill_color=BLUE_B),
                Text(texto, font_size=17, color=BLUE_B),
            )
            s[1].move_to(s[0])
            s.move_to(p)
            servicios.add(s)
        self.play(FadeIn(micro_txt), run_time=0.6)
        self.play(*[ReplacementTransform(partes[i].copy(), servicios[i])
                    for i in range(4)], run_time=2)
        migracion = Text("cada servicio se despliega y escala solo",
                         font_size=18, color=BLUE_B).to_edge(DOWN)
        self.play(ReplacementTransform(pro, migracion), run_time=1)

        # Comunicacion asincrona: bus de eventos
        bus = Rectangle(width=4.6, height=0.4, color=GOLD, fill_opacity=0.2,
                        fill_color=GOLD).move_to(RIGHT * 1.9 + DOWN * 2.0)
        bus_txt = Text("bus de eventos (Kafka)", font_size=16, color=GOLD).move_to(bus)
        conexiones = VGroup(*[
            DashedLine(s.get_bottom(), [s.get_bottom()[0], bus.get_top()[1], 0],
                       color=GOLD, stroke_opacity=0.7)
            for s in servicios
        ])
        self.play(FadeIn(bus), FadeIn(bus_txt), Create(conexiones), run_time=1.5)
        evento = Dot(servicios[0].get_bottom(), color=YELLOW, radius=0.07)
        self.play(FadeIn(evento), run_time=0.3)
        self.play(evento.animate.move_to([servicios[0].get_bottom()[0],
                                          bus.get_center()[1], 0]), run_time=0.6)
        self.play(evento.animate.move_to([servicios[3].get_bottom()[0],
                                          bus.get_center()[1], 0]), run_time=0.8)
        self.play(evento.animate.move_to(servicios[3].get_bottom()), run_time=0.6)
        self.play(Flash(servicios[3], color=YELLOW), FadeOut(evento), run_time=0.8)

        # El precio: complejidad distribuida
        precio = Text("El precio: fallas parciales, trazabilidad, versiones — se paga con tooling",
                      font_size=19, color=YELLOW).to_edge(DOWN)
        self.play(ReplacementTransform(migracion, precio), run_time=1.2)
        malla = VGroup(*[
            SurroundingRectangle(s, color=GREY_B, buff=0.08, stroke_opacity=0.6)
            for s in servicios
        ])
        malla_txt = Text("service mesh: TLS, reintentos y métricas fuera del código",
                         font_size=17, color=GREY_B).next_to(micro_txt, RIGHT, buff=0.4)
        self.play(Create(malla), FadeIn(malla_txt), run_time=1.2)

        cierre = Text("No hay arquitectura correcta: hay compromisos que se eligen a conciencia",
                      font_size=19, color=GOLD).to_edge(DOWN)
        self.play(ReplacementTransform(precio, cierre), run_time=1.2)
        self.wait(2)
