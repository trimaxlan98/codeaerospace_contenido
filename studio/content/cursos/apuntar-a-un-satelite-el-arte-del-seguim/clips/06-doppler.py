class Clip6(Scene):
    """6 - Doppler: la S del pase. La frecuencia recibida no es la que
    transmite el satelite: sube al acercarse, cruza la nominal en la
    maxima aproximacion y cae al alejarse, trazando una S perfecta.
    (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ---------------------------------------------------
        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("La frecuencia que se mueve")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.2)

        # --- momento: ejes, linea f0 y la S del Doppler -----------------------
        curva = curva_s_doppler(ancho=5.4, alto=2.6)
        curva.move_to(np.array([0.0, -0.1, 0.0]))

        self.play(Create(curva.ejes), Create(curva.linea_f0),
                  FadeIn(curva.etiquetas), run_time=0.9)
        self.play(Create(curva.curva), run_time=1.2)
        rot.mostrar(pie_curso("Apuntas perfecto... y no oyes nada: el "
                              "satélite no transmite donde crees."),
                   zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"f_d = -\frac{v_r}{c}\, f_0"),
                   zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: el punto brillante sube la S ----------------------------
        vt = ValueTracker(0.0)
        punto = punto_brillante(curva.punto_en(0.0), color=C_SAT, radio=0.075)
        punto.add_updater(lambda m: m.move_to(curva.punto_en(vt.get_value())))
        self.play(FadeIn(punto), run_time=0.3)

        rot.mostrar(pie_curso("Se acerca: la frecuencia llega comprimida, "
                              "más alta."), zona="abajo", run_time=0.5)
        self.play(vt.animate.set_value(0.35), run_time=1.7)
        self.wait(2.7)

        # --- momento: el cruce con f0 ------------------------------------------
        rot.mostrar(pie_curso("En la máxima aproximación, la nominal "
                              "exacta..."), zona="abajo", run_time=0.5)
        self.play(vt.animate.set_value(0.5), run_time=0.9)
        self.play(Flash(curva.punto_en(0.5), color=C_SAT, line_length=0.22,
                        flash_radius=0.3), run_time=0.5)
        self.play(vt.animate.set_value(0.55), run_time=0.4)
        self.wait(2.6)

        # --- momento: cae hacia el LOS ------------------------------------------
        rot.mostrar(pie_curso("...y al alejarse, cae. Una S perfecta."),
                   zona="abajo", run_time=0.5)
        self.play(vt.animate.set_value(1.0), run_time=1.7)
        self.wait(2.6)

        # --- momento: las bandas --------------------------------------------
        rot.mostrar(pie_curso("Cuanto más alta la banda, más grande la "
                              "S: corrige en vivo."), zona="abajo",
                   run_time=0.5)
        etiqueta = etiqueta_hud("VHF ±3.4 kHz · UHF ±10 kHz")
        etiqueta.move_to(np.array([0.0, -2.2, 0.0]))
        self.play(FadeIn(etiqueta, shift=0.15 * UP), run_time=0.5)

        self.wait(5.0)
        punto.clear_updaters()
