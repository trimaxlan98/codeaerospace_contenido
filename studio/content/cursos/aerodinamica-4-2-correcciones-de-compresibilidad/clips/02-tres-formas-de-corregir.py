class Clip2(Scene):
    """4.2.2 - Correcciones de Karman-Tsien y de Laitone.

    Prandtl-Glauert es la mas simple porque tira TODA la no linealidad.
    Karman-Tsien devuelve una parte y Laitone la evalua con las propiedades
    locales. Las tres arrancan juntas y se separan al acercarse a Mach 1 —
    esa separacion es su desacuerdo, y crece justo donde importa. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Tres formas de corregir")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curvas = curvas_correcciones(cp0=CP0, m_max=M_MAX_CURVAS, ancho=5.0,
                                     alto=2.7)
        curvas.move_to(LEFT * 0.55 + DOWN * 0.35)
        self.play(FadeIn(curvas.ejes), run_time=0.6)
        rot.mostrar(pie_curso("El mismo dato de túnel, corregido de tres "
                              "maneras."), zona="abajo", run_time=0.5)
        self.wait(1.2)
        self.play(LaggedStart(*[Create(curvas.curva(i)) for i in range(3)],
                              lag_ratio=0.35), run_time=2.2)
        self.play(FadeIn(curvas.etiquetas), run_time=0.6)
        self.wait(2.4)

        rot.mostrar(pie_curso("A baja velocidad las tres coinciden. Ninguna "
                              "corrige nada."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: donde se separan -------------------------------------
        # El corte y las tres cifras salen de la pieza: leer la grafica y
        # contarla no pueden dar cosas distintas.
        corte = curvas.vertical_en(M_COMPARA, color=C_TENUE)
        self.play(Create(corte), run_time=0.6)
        # Cada cifra va bajo el NOMBRE de su curva, no a la altura de su
        # punto: en Mach 0.7 las tres estan a menos de un renglon una de
        # otra y colocadas por altura se apilan. La columna de la derecha ya
        # esta repartida por la propia pieza.
        marcas = VGroup()
        for i in range(3):
            punto = Dot(curvas.punto_de(i, M_COMPARA), radius=0.065,
                        color=curvas.color_de(i))
            cifra = Text(f"{abs(curvas.valor(i, M_COMPARA)):.3f}",
                         font=FUENTE_HUD, font_size=17,
                         color=curvas.color_de(i))
            cifra.next_to(curvas.etiquetas[i][1], DOWN, buff=0.10)
            cifra.align_to(curvas.etiquetas[i][1], LEFT)
            marcas.add(VGroup(punto, cifra))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.3), run_time=1.2)

        rot.mostrar(pie_curso(f"A Mach {M_COMPARA:g} ya no se ponen de "
                              "acuerdo."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Prandtl-Glauert es la más optimista porque "
                              "tira toda la no linealidad."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Laitone la evalúa con las propiedades "
                              "locales, y por eso se dispara antes."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
