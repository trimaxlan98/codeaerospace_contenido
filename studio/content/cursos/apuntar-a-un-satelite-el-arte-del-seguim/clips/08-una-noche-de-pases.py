class Clip8(Scene):
    """8 - Una noche de pases. La coreografia completa de un pase, de
    AOS a LOS: el satelite asoma, la antena ya lo espera y lo sigue en
    silencio, y al perderse la montura vuelve sola a su reposo. Cierra
    el curso con la tarjeta de marca. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ----------------------------------------------------
        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Una noche de pases")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.4)

        # --- momento: la vista polar y la antena, listas ----------------------
        vista = vista_polar(radio=2.0)
        vista.move_to((-3.1, -0.2, 0.0))
        traza = traza_pase(vista, el_max=55, az_culminacion=30)
        ant = antena(escala=0.9)
        ant.move_to((3.0, -0.6, 0.0))

        self.play(Create(vista), run_time=0.9)
        self.play(Create(traza), FadeIn(ant, shift=0.15 * RIGHT), run_time=0.9)
        rot.mostrar(pie_curso("A la izquierda, el cielo de la estación. A "
                              "la derecha, su antena."), zona="abajo")
        self.wait(5.2)

        # --- momento: AOS, el satelite asoma y la antena ya espera -------------
        punto = punto_brillante(traza.punto_en(0.0), color=C_SAT)
        t_track = ValueTracker(0.0)
        punto.add_updater(lambda m: m.move_to(traza.punto_en(
            t_track.get_value())))
        ant.add_updater(lambda m: m.orientar(traza.el_en(
            t_track.get_value())))

        self.play(FadeIn(punto, scale=0.6), run_time=0.4)
        # La zona "aos" no tiene layout propio: la etiqueta se coloca a
        # mano en el hueco libre sobre la antena (el origen caia encima
        # de la cardinal E de la vista polar).
        et_aos = etiqueta_hud("AOS 14:32")
        et_aos.move_to(np.array([2.9, 1.7, 0.0]))
        rot.mostrar(et_aos, zona="aos", run_time=0.4)
        rot.mostrar(pie_curso("AOS: el satélite asoma; la antena ya está "
                              "esperando."), zona="abajo")
        self.wait(5.6)

        # --- momento: cuatro minutos de persecucion silenciosa -----------------
        rot.mostrar(pie_curso("Cuatro minutos de persecución "
                              "silenciosa..."), zona="abajo")
        self.play(t_track.animate.set_value(0.92), run_time=5.6)

        # --- momento: LOS, se fue y la montura vuelve a su reposo ---------------
        self.play(t_track.animate.set_value(1.0), run_time=0.5)
        punto.clear_updaters()
        ant.clear_updaters()
        self.play(FadeOut(punto), run_time=0.3)
        et_los = etiqueta_hud("LOS 14:41")
        et_los.move_to(np.array([2.9, 1.7, 0.0]))
        rot.mostrar(et_los, zona="aos", run_time=0.4)
        rot.mostrar(pie_curso("LOS: se fue. La montura vuelve a su "
                              "reposo."), zona="abajo")
        self.wait(5.6)

        # --- momento: pantalla limpia para la tarjeta de cierre -----------------
        rot.limpiar(run_time=0.4)
        self.play(FadeOut(VGroup(vista, traza, ant, modulo)), run_time=0.9)

        # --- momento: tarjeta final, patron exacto del curso ---------------------
        titulo_final = titulo_marca("Apuntar a un satélite", font_size=42)
        subtitulo = Text("el arte del seguimiento", font_size=25,
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
