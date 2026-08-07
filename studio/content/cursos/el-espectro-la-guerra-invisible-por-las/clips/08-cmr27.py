class Clip8(Scene):
    """8 - CMR-27: la proxima batalla. Una linea de tiempo con cuatro
    CMR marca el ritmo de cuatro anos; un punto brillante avanza hasta
    CMR-27, que pulsa ambar. Debajo, tres etiquetas HUD listan lo que
    esta en la mesa. Cierra el curso con la tarjeta de marca (patron
    identico al de SDR clip 8). (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ----------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("CMR-27: la próxima batalla")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.2)

        # --- momento: la linea de tiempo, cuatro conferencias ----------------
        tiempo = linea_tiempo([("CMR-19", ""), ("CMR-23", ""),
                               ("CMR-27", ""), ("CMR-31", "")], ancho=6.4)
        tiempo.move_to(np.array([0.0, 0.6, 0.0]))
        self.play(FadeIn(tiempo.linea), FadeIn(tiempo.muescas),
                  LaggedStart(*[FadeIn(r) for r in tiempo.rotulos],
                              lag_ratio=0.2), run_time=0.8)
        self.wait(0.3)

        recorre = punto_brillante(tiempo.muesca(0), color=C_ONDA)
        self.play(FadeIn(recorre), run_time=0.3)
        self.play(recorre.animate.move_to(tiempo.muesca(2)), run_time=1.6)
        self.play(Indicate(tiempo.rotulo(2), color=C_ONDA, scale_factor=1.25),
                  run_time=1.2)

        rot.mostrar(pie_curso("Cada cuatro años el mundo entero se sienta "
                              "a repartir las ondas de nuevo."),
                   zona="abajo", run_time=0.5)
        self.wait(6.0)

        # --- momento: lo que esta sobre la mesa, tres frentes -----------------
        etiquetas = VGroup(
            etiqueta_hud("MAS IMT", color=C_ONDA),
            etiqueta_hud("D2D", color=C_ONDA),
            etiqueta_hud("NUEVAS BANDAS NGSO", color=C_ONDA),
        ).arrange(RIGHT, buff=0.9)
        if etiquetas.width > config.frame_width - 1.2:
            etiquetas.scale_to_fit_width(config.frame_width - 1.2)
        etiquetas.move_to(np.array([0.0, -1.2, 0.0]))

        rot.mostrar(pie_curso("Sobre la mesa: más espectro móvil, teléfonos "
                              "que hablan con satélites, nuevas bandas para "
                              "constelaciones."), zona="abajo", run_time=0.5)
        self.wait(0.4)
        self.play(FadeIn(etiquetas[0], shift=0.12 * UP), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(etiquetas[1], shift=0.12 * UP), run_time=0.5)
        self.wait(0.5)
        self.play(FadeIn(etiquetas[2], shift=0.12 * UP), run_time=0.5)
        self.wait(4.0)

        # --- momento: cierre del cuerpo ------------------------------------
        rot.mostrar(pie_curso("Lo que ahí se firme decidirá qué misiones "
                              "existen en 2035."), zona="abajo", run_time=0.5)
        self.wait(6.0)

        # --- momento: pantalla limpia para la tarjeta de cierre -------------
        # El pie/titulo se limpian ANTES del fundido del cuerpo: si el
        # fundido corriera con el pie de "2035" aun visible, imagen y
        # texto se pisarian durante la transicion.
        rot.limpiar(run_time=0.4)
        self.play(FadeOut(VGroup(tiempo, recorre, etiquetas, modulo)),
                  run_time=0.9)

        # --- momento: tarjeta final, patron exacto del curso -----------------
        titulo_final = titulo_marca("El espectro", font_size=46)
        subtitulo = Text("la guerra invisible por las ondas", font_size=25,
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
