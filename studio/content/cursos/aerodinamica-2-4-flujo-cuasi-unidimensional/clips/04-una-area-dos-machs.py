class Clip4(Scene):
    """2.4.4 - Relacion area-Mach A/A* y su doble solucion.

    La curva tiene dos ramas y una relacion de areas corta las dos: la
    geometria por si sola no decide el Mach. Quien decide es la presion de
    salida — y ese es exactamente el hilo de la leccion 2.5. Cierre de la
    leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Un área, dos Machs")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curva = curva_area_mach(m_max=3.2, ancho=5.4, alto=2.8)
        curva.move_to(LEFT * 0.30 + DOWN * 0.30)
        self.play(FadeIn(curva.ejes), run_time=0.6)
        self.play(Create(curva.rama_sub), Create(curva.rama_super),
                  run_time=1.6)
        self.play(FadeIn(curva.garganta), FadeIn(curva.etiquetas),
                  run_time=0.7)
        rot.mostrar(pie_curso("El área que necesita el flujo, comparada con "
                              "la de la garganta."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Vale 1 en la garganta y crece hacia los dos "
                              "lados."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: una recta horizontal corta DOS veces -----------------
        # La construye la pieza sobre sus coordenadas, y los dos Machs los
        # saca invirtiendo A/A* — el clip no escribe ningun numero a mano.
        recta = curva.horizontal_en(AREA_EJEMPLO, color=C_TENUE)
        self.play(Create(recta), run_time=0.8)
        rot.mostrar(pie_curso(f"Ahora fija una relación de áreas. "
                              f"{AREA_EJEMPLO:.4f}, por ejemplo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # Las dos van por encima de su punto (la recta de area constante
        # pasa justo por ellos y debajo no hay sitio), pero la supersonica
        # ademas hacia la IZQUIERDA: a su derecha la rama sube deprisa y le
        # atraviesa el rotulo.
        marcas = VGroup()
        for m, color, lado in ((M_EJEMPLO_SUB, C_SUB, UP),
                               (M_EJEMPLO_SUPER, C_SUPER, UL)):
            punto = Dot(curva.punto_de(m), radius=0.075, color=color)
            cifra = Text(f"M = {m:.2f}", font=FUENTE_HUD, font_size=19,
                         color=color)
            cifra.next_to(punto, lado, buff=0.16)
            marcas.add(VGroup(punto, cifra))
        self.play(LaggedStart(*[FadeIn(m, scale=1.5) for m in marcas],
                              lag_ratio=0.45), run_time=1.2)
        rot.mostrar(pie_curso("Corta dos veces. La misma tobera admite estos "
                              "dos Machs de salida."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("La geometría no basta para decidir cuál de "
                              "los dos ocurre."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(curva, recta, marcas)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("La forma del tubo pone las opciones.", font_size=35,
                         color=C_TITULO),
            titulo_marca("La presión de salida elige.", font_size=35,
                         color=C_TRANS)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.2)
