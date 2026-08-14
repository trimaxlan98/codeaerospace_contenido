class Clip3(Scene):
    """2.3.3 - Errores del anemometro incompresible a alto Mach.

    El instrumento que traduce presion a velocidad con la formula de
    Bernoulli funciona muy bien... hasta que deja de hacerlo. La curva del
    error es la misma historia de la leccion 1.1 contada desde el
    instrumento. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuánto miente el anemómetro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curva = curva_anemometro(m_max=1.0, ancho=5.4, alto=2.7)
        curva.move_to(DOWN * 0.28)
        self.play(FadeIn(curva.ejes), run_time=0.6)
        rot.mostrar(pie_curso("Un anemómetro sencillo supone que la presión "
                              "dinámica es un medio rho V al cuadrado."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        self.play(Create(curva.curva), run_time=1.8)
        rot.mostrar(pie_curso("Esto es lo que se equivoca al suponerlo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        self.play(Create(curva.umbral), FadeIn(curva.etiquetas), run_time=0.7)
        rot.mostrar(pie_curso("Por debajo del 5 % nadie se queja: cae dentro "
                              "de la tolerancia del instrumento."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: los dos puntos de siempre ---------------------------
        # El punto de Mach 0.3 vive en un hueco muy estrecho: el eje justo
        # debajo, su propia curva encima y la linea del 5 % un poco mas
        # arriba. Su cifra se saca FUERA de la caja, a su misma altura; la
        # de Mach alto si tiene sitio de sobra pegada al punto.
        x_fuera = curva.ejes[1].get_left()[0] - 0.52
        marcas = VGroup()
        for m, color, fuera in ((0.30, C_SUB, True), (M_TAS, C_TRANS, False)):
            punto = Dot(curva.punto_de(m), radius=0.07, color=color)
            cifra = Text(f"{curva.error(m) * 100:.0f} %", font=FUENTE_HUD,
                         font_size=19, color=color)
            if fuera:
                cifra.move_to([x_fuera, punto.get_center()[1], 0])
            else:
                cifra.next_to(punto, UL, buff=0.10)
            marcas.add(VGroup(punto, cifra))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.45), run_time=1.2)

        rot.mostrar(pie_curso(f"A Mach 0.3, un "
                              f"{curva.error(0.30) * 100:.0f} %. El mismo "
                              "límite de siempre, visto desde el "
                              "instrumento."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso(f"Pero a Mach {M_TAS:.2f} —nuestro avión de "
                              f"crucero— ya es un {ERROR_TAS * 100:.0f} %."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Un veinte por ciento de error en la presión "
                              "dinámica no es un detalle: es otro avión."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
