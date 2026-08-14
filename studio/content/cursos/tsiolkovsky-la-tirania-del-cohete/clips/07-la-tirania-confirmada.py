class Clip7(Scene):
    """7 - La tirania, confirmada. Las barras de carga util de tres
    cohetes REALES (Saturn V, Falcon 9, Soyuz) con sus masas citadas,
    contra la linea del modelo de dos etapas: sesenta anios de ingenieria
    distinta y la misma cuenta. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La tiranía, confirmada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: tres cohetes, la misma cuenta -----------------------
        rot.mostrar(pie_curso("Sesenta años, tres continentes de ingeniería: "
                              "la misma cuenta."),
                    zona="abajo", run_time=0.5)

        datos = tuple(c / t * 100 for _, c, t in COHETES_REALES)
        barras = barras_carga(datos, ancho=6.0, alto=6.2, ancho_barra=1.0)
        barras.shift(DOWN * 1.45)

        nombres = VGroup(*[
            Text(COHETES_REALES[i][0], font_size=20, color=C_TENUE)
            .next_to(barras.base(i), DOWN, buff=0.20)
            for i in range(len(datos))])
        cifras = VGroup(*[
            tag_hud(f"{v:.1f} %", font_size=21, color=C_CARGA)
            .next_to(barras.tope(i), UP, buff=0.15)
            for i, v in enumerate(datos)])

        self.play(Create(barras.eje), run_time=0.6)
        for i in range(len(datos)):
            self.play(GrowFromEdge(barras.barra(i), DOWN),
                      FadeIn(nombres[i], shift=0.10 * UP), run_time=0.65)
            self.wait(0.5)
        self.wait(2.3)

        # --- momento: las masas de verdad ---------------------------------
        rot.mostrar(pie_curso(f"Del {COHETES_REALES[1][0]}, "
                              f"{COHETES_REALES[1][2]:.0f} t despegan y "
                              f"{COHETES_REALES[1][1]:.1f} t llegan a "
                              f"órbita."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.30), run_time=1.5)
        self.wait(5.0)

        # --- momento: el modelo, al lado ----------------------------------
        rot.mostrar(pie_curso(f"El modelo de dos etapas predecía "
                              f"{CARGA_2ET * 100:.1f} %. La realidad ronda "
                              f"lo mismo."),
                    zona="abajo", run_time=0.5)

        y_cero = barras.eje.get_center()[1]
        escala = (barras.tope(0)[1] - y_cero) / datos[0]
        y_modelo = y_cero + escala * CARGA_2ET * 100
        linea = DashedLine(
            np.array([barras.eje.get_left()[0] - 0.15, y_modelo, 0.0]),
            np.array([barras.barra(2).get_right()[0] + 0.35, y_modelo, 0.0]),
            dash_length=0.13, stroke_width=2.2, color=C_ESTRUCTURA)
        linea.set_stroke(opacity=0.9)
        tag_modelo = tag_hud(f"modelo 2 etapas: {CARGA_2ET * 100:.1f} %",
                             font_size=16, color=C_ESTRUCTURA)
        tag_modelo.next_to(linea, RIGHT, buff=0.24)

        self.play(Create(linea), FadeIn(tag_modelo, shift=0.10 * LEFT),
                  run_time=1.0)
        self.wait(5.5)

        # --- momento: nadie le gana al logaritmo --------------------------
        rot.mostrar(pie_curso("Nadie le gana al logaritmo por fuerza bruta."),
                    zona="abajo", run_time=0.5)
        self.wait(7.0)
