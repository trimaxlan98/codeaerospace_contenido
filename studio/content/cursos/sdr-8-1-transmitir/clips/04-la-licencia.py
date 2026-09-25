class Clip4(Scene):
    """8.1.4 - La cadena corta de transmision: software, DAC, filtro de
    reconstruccion (fucsia, el del clip 3), amplificador y antena. Cierre
    de la leccion: recibir es libre, transmitir tiene reglas (licencia).
    (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La licencia"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        nombres = ["SOFTWARE", "DAC", "FILTRO", "AMPLIFICADOR", "ANTENA"]
        colores = [C_CALCULO, C_TENUE, C_LO, C_TENUE, C_TENUE]
        ancho_total, sep = 12.0, 0.4
        ancho_b = (ancho_total - sep * (len(nombres) - 1)) / len(nombres)
        bloques = VGroup(*[bloque(n, ancho=ancho_b, alto=1.5, color=c,
                                  tamano=21) for n, c in
                          zip(nombres, colores)])
        bloques.arrange(RIGHT, buff=sep)
        bloques.move_to(UP * 0.35)
        flechas = [conectar(bloques[i], bloques[i + 1])
                  for i in range(len(nombres) - 1)]

        for i, b in enumerate(bloques):
            anims = [FadeIn(b, shift=RIGHT * 0.15)]
            if i > 0:
                anims.append(GrowArrow(flechas[i - 1]))
            self.play(*anims, run_time=0.55)
        self.wait(0.6)

        # --- las ondas que irradia la antena, ambar (la senal transmitida) --
        centro = bloques[-1].get_top() + UP * 0.05
        ondas = VGroup(*[Arc(radius=0.4 + 0.32 * i, start_angle=PI / 2 - 0.55,
                             angle=1.1, arc_center=centro, color=C_SENAL,
                             stroke_width=2.6 - 0.4 * i) for i in range(3)])
        ondas.set_stroke(opacity=0.85)

        # --- el marco de la cadena, abajo -------------------------------------
        marco = Brace(bloques, DOWN, buff=1.35, color=C_TENUE)
        t_marco = tag_junto(marco, "cadena TX", DOWN, buff=0.14,
                            font_size=24)
        self.play(GrowFromCenter(marco), FadeIn(t_marco), run_time=0.7)
        self.wait(0.6)

        self.play(flujo(flechas, color=C_SENAL, por_conexion=0.4))
        self.play(LaggedStart(*[Create(o) for o in ondas], lag_ratio=0.25),
                  run_time=0.9)
        self.wait(1.4)

        self.play(Indicate(bloques[2], color=C_LO, scale_factor=1.06),
                  run_time=0.9)
        self.wait(0.8)

        rot.mostrar(dato_pie("transmitir requiere licencia"), zona="abajo",
                    run_time=0.5)
        self.wait(6.0)

        self.play(flujo(flechas, color=C_SENAL, por_conexion=0.4))
        self.wait(4.0)

        cierre_leccion(self, rot, "Recibir es libre.",
                       "Transmitir tiene reglas.", bloques,
                       VGroup(*flechas), marco, t_marco, ondas, espera=5.5)
