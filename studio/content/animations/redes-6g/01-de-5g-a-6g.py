from manim import *


class De5gA6g(Scene):
    def construct(self):
        titulo = Text("De 5G a 6G: visión y calendario", font_size=34, color=GOLD).to_edge(UP)
        self.play(FadeIn(titulo, shift=DOWN * 0.3), run_time=1)

        # Linea de tiempo de estandarizacion
        linea = NumberLine(x_range=[2020, 2032, 2], length=11, color=GREY_B,
                           include_numbers=False).move_to(UP * 1.6)
        anios = VGroup(*[
            Text(str(a), font_size=18, color=GREY_B)
            .next_to(linea.number_to_point(a), DOWN, buff=0.2)
            for a in range(2020, 2033, 2)
        ])
        self.play(Create(linea), FadeIn(anios), run_time=1.5)

        hitos = [
            (2020, "5G comercial", BLUE_B),
            (2024, "5G-Advanced", BLUE_B),
            (2026, "estándar 6G\n(3GPP Rel-21)", YELLOW),
            (2030, "6G comercial", GOLD),
        ]
        marcas = VGroup()
        for anio, texto, color in hitos:
            p = linea.number_to_point(anio)
            d = Dot(p, color=color, radius=0.08)
            t = Text(texto, font_size=17, color=color, line_spacing=0.85)
            t.next_to(p, UP, buff=0.25)
            marcas.add(VGroup(d, t))
        self.play(LaggedStart(*[FadeIn(m, shift=DOWN * 0.2) for m in marcas],
                              lag_ratio=0.35), run_time=3)

        # Comparacion de KPIs
        kpis = [
            ("Velocidad pico", "20 Gb/s", "1 Tb/s", 0.35, 1.0),
            ("Latencia", "1 ms", "0.1 ms", 0.5, 1.0),
            ("Densidad", "1M disp/km²", "10M disp/km²", 0.3, 1.0),
        ]
        tabla = VGroup()
        encabezado = VGroup(
            Text("KPI", font_size=19, color=GREY_B),
            Text("5G", font_size=19, color=BLUE_B),
            Text("6G", font_size=19, color=GOLD),
        ).arrange(RIGHT, buff=1.4)
        filas = VGroup(encabezado)
        for nombre, v5, v6, _, _ in kpis:
            fila = VGroup(
                Text(nombre, font_size=18, color=GREY_B),
                Text(v5, font_size=18, color=BLUE_B),
                Text(v6, font_size=18, color=GOLD),
            ).arrange(RIGHT, buff=0.9)
            filas.add(fila)
        filas.arrange(DOWN, aligned_edge=LEFT, buff=0.3)
        filas.move_to(LEFT * 3.2 + DOWN * 1.4)
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.3) for f in filas],
                              lag_ratio=0.25), run_time=2.5)

        # Nuevos casos de uso
        casos = VGroup(
            Text("· Telepresencia holográfica", font_size=19, color=YELLOW),
            Text("· Sensado integrado (ISAC)", font_size=19, color=YELLOW),
            Text("· Gemelos digitales en tiempo real", font_size=19, color=YELLOW),
            Text("· IA nativa en la red", font_size=19, color=YELLOW),
            Text("· Cobertura tierra + satélite (NTN)", font_size=19, color=YELLOW),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        casos.move_to(RIGHT * 3.6 + DOWN * 1.4)
        casos_txt = Text("Qué habilita 6G:", font_size=20, color=GOLD)
        casos_txt.next_to(casos, UP, buff=0.25).align_to(casos, LEFT)
        self.play(FadeIn(casos_txt),
                  LaggedStart(*[FadeIn(c, shift=RIGHT * 0.3) for c in casos],
                              lag_ratio=0.25), run_time=3)

        cierre = Text("6G no es solo más rápido: la red pasa de comunicar a percibir y razonar",
                      font_size=20, color=BLUE_B).to_edge(DOWN)
        self.play(FadeIn(cierre), run_time=1.2)
        self.wait(2)
