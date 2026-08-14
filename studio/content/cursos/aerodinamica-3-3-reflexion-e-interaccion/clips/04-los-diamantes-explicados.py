class Clip4(Scene):
    """3.3.4 - Patrones en el chorro de una tobera (diamantes de Mach).

    Los rombos del clip 3 de la leccion 2.5 quedaron sin explicar. Aqui se
    explican solos: son el rebote de la leccion, repetido. Choque contra el
    borde libre, abanico de vuelta, abanico contra el otro borde, choque de
    vuelta. Cierre de la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Los diamantes, explicados")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Chorro: dos bordes libres punteados y el zigzag de ondas dentro.
        ancho, semi = 7.4, 0.85
        x0 = -ancho / 2
        bordes = VGroup(*[
            DashedLine((x0, signo * semi, 0), (x0 + ancho, signo * semi, 0),
                       stroke_width=2.4, color=C_SUB, dash_length=0.14)
            for signo in (1, -1)])
        salida = Line((x0, semi + 0.45, 0), (x0, -semi - 0.45, 0),
                      stroke_width=4.0, color=C_TENUE)
        chorro = VGroup(bordes, salida).move_to(UP * 0.35)

        self.play(FadeIn(chorro), run_time=0.7)
        rot.mostrar(pie_curso("El chorro de una tobera no adaptada, visto de "
                              "lado. Los bordes son libres."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # El zigzag: alterna choque (rojo) y abanico (cian) en cada rebote,
        # que es exactamente lo que dicen los dos primeros clips.
        paso = ancho / 4.2
        ondas = VGroup()
        colores = []
        for k in range(4):
            xi = x0 + 0.35 + k * paso
            for signo in (1, -1):
                comprime = (k % 2 == 0)
                color = C_SUPER if comprime else C_CALCULO
                linea = Line((xi, signo * semi, 0),
                             (xi + paso, -signo * semi, 0),
                             stroke_width=3.0 if comprime else 1.8,
                             color=color)
                if not comprime:
                    linea.set_stroke(opacity=0.8)
                ondas.add(linea)
                colores.append(comprime)
        ondas.move_to(chorro.get_center())

        self.play(LaggedStart(*[Create(o) for o in ondas[:2]],
                              lag_ratio=0.3), run_time=0.9)
        rot.mostrar(pie_curso("Del labio sale un choque, que cruza y llega "
                              "al borde de enfrente."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        self.play(LaggedStart(*[Create(o) for o in ondas[2:4]],
                              lag_ratio=0.3), run_time=0.9)
        rot.mostrar(pie_curso("Borde libre: rebota como abanico. Lo del clip "
                              "anterior."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        self.play(LaggedStart(*[Create(o) for o in ondas[4:]],
                              lag_ratio=0.22), run_time=1.4)
        rot.mostrar(pie_curso("Y el abanico rebota como choque. Y vuelta a "
                              "empezar."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Los rombos que se ven en la llama no son "
                              "adorno: son este zigzag, celda a celda."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(chorro, ondas)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Una onda no elige cómo rebotar.", font_size=35,
                         color=C_TITULO),
            titulo_marca("Lo elige el contorno.", font_size=35,
                         color=C_SUB)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
