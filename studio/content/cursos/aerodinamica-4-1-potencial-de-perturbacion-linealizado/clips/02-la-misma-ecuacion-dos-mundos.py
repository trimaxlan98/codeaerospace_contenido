class Clip2(Scene):
    """4.1.2 - Obtencion de la ecuacion y su caracter eliptico o hiperbolico.

    Una sola ecuacion, un solo coeficiente, y ese coeficiente cambia de signo
    en Mach 1. No es un detalle matematico: en subsonico una perturbacion se
    entera todo el campo, y en supersonico solo lo que cae dentro del cono.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La misma ecuación, dos mundos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # En partes: recuadrar el parentesis por indices de glifo
        # (ecuacion[0][:9]) acaba encerrando tambien media derivada.
        ecuacion = MathTex(r"(1 - M_\infty^2)", r"\phi_{xx} + \phi_{yy} = 0",
                           font_size=50, color=C_CALCULO)
        ecuacion.move_to(UP * 2.05)
        self.play(Write(ecuacion), run_time=1.2)
        rot.mostrar(pie_curso("Toda la aerodinámica linealizada, en un "
                              "renglón."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        marco = SurroundingRectangle(ecuacion[0], color=C_SUPER,
                                     stroke_width=2.6, buff=0.10)
        self.play(Create(marco), run_time=0.7)
        rot.mostrar(pie_curso("Y todo lo que importa está en el signo de "
                              "ese paréntesis."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: los dos mundos ---------------------------------------
        # Izquierda: una perturbacion que se entera todo el campo (eliptica).
        # Derecha: la misma, encerrada en su cono (hiperbolica).
        fuente_sub = Dot(LEFT * 3.4 + DOWN * 0.35, radius=0.07, color=C_SUB)
        anillos = VGroup(*[
            DashedVMobject(Circle(radius=r, color=C_SUB, stroke_width=1.8)
                           .move_to(fuente_sub.get_center()), num_dashes=34)
            .set_stroke(opacity=0.65) for r in (0.55, 1.0, 1.45)])
        eliptico = VGroup(anillos, fuente_sub)
        tag_sub = VGroup(
            MathTex(r"M_\infty < 1", font_size=30, color=C_SUB),
            Text("elíptico: se entera todo el campo", font_size=19,
                 color=C_SUB)).arrange(DOWN, buff=0.14)
        tag_sub.next_to(eliptico, DOWN, buff=0.30)

        fuente_sup = Dot(RIGHT * 3.4 + DOWN * 0.35, radius=0.07,
                         color=C_SUPER)
        mu = np.deg2rad(MU_SUPER)
        cono = VGroup(*[
            Line(fuente_sup.get_center(),
                 fuente_sup.get_center() + np.array([np.cos(mu),
                                                     signo * np.sin(mu), 0])
                 * 2.1, stroke_width=2.8, color=C_SUPER)
            for signo in (1, -1)])
        region = Polygon(fuente_sup.get_center(),
                         cono[0].get_end(), cono[1].get_end(),
                         stroke_width=0, fill_color=C_SUPER,
                         fill_opacity=0.14)
        hiperbolico = VGroup(region, cono, fuente_sup)
        tag_sup = VGroup(
            MathTex(r"M_\infty > 1", font_size=30, color=C_SUPER),
            Text("hiperbólico: solo dentro del cono", font_size=19,
                 color=C_SUPER)).arrange(DOWN, buff=0.14)
        tag_sup.next_to(hiperbolico, DOWN, buff=0.30)

        self.play(FadeIn(eliptico), FadeIn(tag_sub), run_time=0.9)
        rot.mostrar(pie_curso("Si es positivo, la ecuación es elíptica: una "
                              "perturbación la nota todo el campo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        self.play(FadeIn(hiperbolico), FadeIn(tag_sup), run_time=0.9)
        rot.mostrar(pie_curso("Si es negativo, hiperbólica: solo se entera "
                              "lo que cae dentro del cono de Mach."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("La misma ecuación describe los dos mundos. "
                              "Solo cambia de signo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
