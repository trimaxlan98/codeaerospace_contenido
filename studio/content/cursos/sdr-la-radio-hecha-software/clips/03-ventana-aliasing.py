class Clip3(Scene):
    """3 - La ventana y el aliasing. La ventana de espectro se abre con un
    pico ambar cerca de la sintonia; al deslizarlo hacia +fs/2 su campana
    termina medio salida por el borde derecho mientras un fantasma rojo
    crece plegado por la izquierda: lo que se sale de la ventana no
    desaparece, se pliega dentro. Eso es el aliasing."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("Una ventana de 2.4 MHz")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(0.8)

        # --- momento: la ventana se abre con el pico cerca de la sintonia --
        ventana = ventana_espectro(ancho=6.8, alto=2.3)
        ventana.move_to(np.array([0.0, 0.1, 0.0]))
        pico = pico_espectral(ventana, f_rel=-0.25, altura=1.5,
                              ancho_rel=0.085, color=C_SENAL)
        self.play(Create(ventana), run_time=1.0)
        self.play(FadeIn(pico, shift=0.15 * UP), run_time=0.5)
        rot.mostrar(pie_curso("Muestrear abre una ventana: fs hertz de "
                              "espectro alrededor de la sintonía."),
                   zona="abajo", run_time=0.5)
        self.wait(5.3)

        # --- momento: la formula del ancho de banda -------------------------
        rot.mostrar(formula_pie("B = f_s"), zona="abajo", run_time=0.45)
        self.wait(5.2)

        # --- momento: el numero concreto -------------------------------------
        rot.mostrar(pie_curso("A 2.4 megamuestras por segundo: 2.4 MHz de "
                              "radio de un solo vistazo."), zona="abajo",
                   run_time=0.45)
        self.wait(5.6)

        # --- momento: el pico se desliza a la derecha y el fantasma se pliega
        rot.mostrar(pie_curso("Lo que cae fuera no desaparece: se pliega "
                              "dentro. Eso es el aliasing."), zona="abajo",
                   run_time=0.45)
        vt = ValueTracker(-0.25)
        pico.add_updater(lambda m: m.move_to(
            np.array([ventana.x_de(vt.get_value()), m.get_center()[1], 0.0])))
        fantasma = pico_espectral(ventana, f_rel=-0.92, altura=1.5,
                                  ancho_rel=0.085, color=C_RUIDO)
        self.play(vt.animate.set_value(0.85), GrowFromEdge(fantasma, RIGHT),
                  run_time=2.4)
        pico.clear_updaters()
        self.wait(2.9)

        # --- momento: el fantasma pulsa ---------------------------------------
        self.play(Indicate(fantasma, color=C_RUIDO, scale_factor=1.15),
                  run_time=0.8)
        self.wait(0.2)

        # --- momento: cierre -- filtrar antes de digitalizar -------------------
        rot.mostrar(pie_curso("Filtra antes de digitalizar... o verás "
                              "señales que no existen."), zona="abajo",
                   run_time=0.45)
        self.wait(5.4)
