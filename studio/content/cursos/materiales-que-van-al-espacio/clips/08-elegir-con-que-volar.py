class Clip8(Scene):
    """8 - Elegir con que volar. El mapa de Ashby a la izquierda contra tres
    exigencias de mision en columna a la derecha: nadie gana en todo, el
    material ganador es el que menos compromete. Cierra el curso con la
    tarjeta de marca. (~34 s)"""

    def _etiqueta_lateral(self, texto, y):
        """Etiqueta HUD de exigencia, columna derecha (x=3.0), sin encimar
        el mapa ni salirse del cuadro."""
        t = etiqueta_hud(texto)
        if t.width > 3.6:
            t.scale_to_fit_width(3.6)
        t.move_to(np.array([3.0, y, 0.0]))
        return t

    def _check(self, pos, color=C_OK):
        """Palomita de dos trazos (no Text) junto a una burbuja aprobada."""
        a = pos + np.array([-0.10, 0.0, 0.0])
        b = pos + np.array([-0.02, -0.09, 0.0])
        c = pos + np.array([0.14, 0.12, 0.0])
        return VGroup(Line(a, b, stroke_width=3.0, color=color),
                     Line(b, c, stroke_width=3.0, color=color))

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Elegir con qué volar")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.7)

        # --- momento: el mapa de Ashby a la izquierda ---------------------------
        mapa = mapa_ashby()
        mapa.scale(0.85)
        mapa.move_to(np.array([-2.9, -0.1, 0.0]))
        self.play(FadeIn(mapa, scale=0.96), run_time=0.9)
        self.wait(0.4)

        # --- momento: tres exigencias en columna, una a una ----------------------
        e1 = self._etiqueta_lateral("RÍGIDO Y LIGERO", 1.0)
        self.play(FadeIn(e1, shift=0.15 * LEFT), run_time=0.45)
        self.wait(0.35)
        e2 = self._etiqueta_lateral("MIL CICLOS TÉRMICOS", 0.0)
        self.play(FadeIn(e2, shift=0.15 * LEFT), run_time=0.45)
        self.wait(0.35)
        e3 = self._etiqueta_lateral("AÑOS SIN TALLER", -1.0)
        self.play(FadeIn(e3, shift=0.15 * LEFT), run_time=0.45)
        self.wait(0.5)
        columna = VGroup(e1, e2, e3)

        # --- momento: una mision es una lista de exigencias que se contradicen -
        rot.mostrar(pie_curso("Una misión es una lista de exigencias que "
                              "se contradicen."), zona="abajo", run_time=0.5)
        self.wait(5.6)

        # --- momento: el ganador nunca es el mejor en todo -----------------------
        rot.mostrar(pie_curso("El material ganador nunca es el mejor en "
                              "todo: es el que menos compromete."),
                   zona="abajo", run_time=0.5)
        self.wait(5.6)

        # --- momento: la burbuja COMPUESTOS pulsa y aprueba -----------------------
        # El pie entra ANTES del pulso (regla del curso) y la palomita va
        # ARRIBA de la burbuja: a la derecha invadia el pasillo angosto
        # hacia CERAMICOS y se encimaba con la diagonal punteada.
        rot.mostrar(pie_curso("Para el espacio, casi siempre: compuestos "
                              "y aleaciones ligeras, elegidos gramo a "
                              "gramo."), zona="abajo", run_time=0.5)
        burbuja = mapa.burbuja("COMPUESTOS")
        self.play(Indicate(burbuja, color=C_MAT, scale_factor=1.15),
                  run_time=0.9)
        check = self._check(burbuja.get_top() + np.array([0.0, 0.24, 0.0]))
        self.play(FadeIn(check, scale=0.8), run_time=0.45)
        self.wait(5.6)

        # --- momento: pantalla limpia para la tarjeta de cierre --------------------
        rot.limpiar(run_time=0.4)
        self.play(FadeOut(VGroup(mapa, columna, check, modulo)),
                  run_time=0.9)

        # --- momento: tarjeta final, patron exacto del curso ------------------------
        titulo_final = titulo_marca("Materiales", font_size=46)
        subtitulo = Text("que van al espacio", font_size=25,
                         color=C_ACENTO)
        cuerpo = VGroup(titulo_final, subtitulo).arrange(DOWN, buff=0.26)

        subrayado = Line(LEFT, RIGHT, color=C_ACENTO)
        subrayado.set_width(subtitulo.width * 1.1)
        subrayado.next_to(subtitulo, DOWN, buff=0.16)
        brillo_subrayado = con_brillo(subrayado, color=C_ACENTO)

        tarjeta = VGroup(cuerpo, brillo_subrayado)
        tarjeta.move_to(ORIGIN)

        self.play(Write(titulo_final), run_time=1.6)
        self.play(FadeIn(subtitulo, shift=0.15 * UP), run_time=0.8)
        self.wait(1.2)
        self.play(Create(brillo_subrayado), run_time=1.2)
        self.wait(2)
