class Clip5(Scene):
    """5 - Keyhole: el agujero del cenit. El pase casi cenital que mejor
    señal da es tambien el que exige un giro de acimut imposible: la aguja
    de velocidad se dispara al acercarse al cenit y revela la zona ciega
    de la montura Az/El. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ---------------------------------------------------
        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Keyhole: el agujero del cénit")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.2)

        # --- momento: la vista polar y el pase casi cenital ------------------
        vista = vista_polar(radio=2.2)
        vista.move_to(np.array([-3.0, -0.15, 0.0]))
        traza = traza_pase(vista, el_max=87.0, az_culminacion=5.0,
                           color=C_SAT)

        aguja = aguja_velocidad(maximo=10.0, valor=0.5)
        aguja.move_to(np.array([3.2, 0.6, 0.0]))
        tag = tag_junto(aguja, "grados/s en acimut", direccion=DOWN,
                       buff=0.24)

        self.play(FadeIn(vista), run_time=0.6)
        self.play(Create(traza), run_time=1.1)
        self.play(FadeIn(aguja), FadeIn(tag), run_time=0.6)
        rot.mostrar(pie_curso("El mejor pase para la señal es el peor "
                              "para la mecánica."), zona="abajo",
                   run_time=0.5)
        self.wait(5.6)

        rot.mostrar(formula_pie(r"\dot{Az} = \omega_t / \cos(el)"),
                   zona="abajo", run_time=0.5)
        self.wait(5.3)

        # --- momento: el punto sube y la aguja se dispara --------------------
        vt = ValueTracker(0.0)
        punto = punto_brillante(traza.punto_en(0.0), color=C_SAT, radio=0.07)
        punto.add_updater(lambda m: m.move_to(traza.punto_en(vt.get_value())))
        self.play(FadeIn(punto), run_time=0.3)

        rot.mostrar(pie_curso("Cerca del cénit el acimut pide un giro "
                              "imposible: la demanda se dispara."),
                   zona="abajo", run_time=0.5)
        self.play(vt.animate.set_value(0.32), run_time=1.4)
        self.play(Rotate(aguja.aguja, aguja.a_valor(2.0) - aguja.angulo,
                         about_point=aguja.pivote), run_time=0.5)
        self.play(vt.animate.set_value(0.5), run_time=1.4)
        self.play(Rotate(aguja.aguja, aguja.a_valor(9.0) - aguja.angulo,
                         about_point=aguja.pivote), run_time=0.5)
        self.wait(1.3)

        # --- momento: el cono ciego del keyhole -------------------------------
        cono = cono_keyhole(vista, radio_deg=8.0)
        self.play(GrowFromCenter(cono), run_time=0.7)
        rot.mostrar(pie_curso("Ese cono ciego es el keyhole: ahí la "
                              "montura no puede seguir."), zona="abajo",
                   run_time=0.5)
        self.play(Indicate(cono, color=C_PELIGRO, scale_factor=1.15),
                  run_time=0.7)
        self.wait(0.4)
        self.play(Indicate(cono, color=C_PELIGRO, scale_factor=1.15),
                  run_time=0.7)
        self.wait(3.0)

        # --- momento: cierre --------------------------------------------------
        rot.mostrar(pie_curso("Las salidas: aceptar el hueco, girar "
                              "antes, o cambiar de montura."), zona="abajo",
                   run_time=0.5)
        self.wait(5.6)
        punto.clear_updaters()
