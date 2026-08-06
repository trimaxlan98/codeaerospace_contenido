class Clip2(Scene):
    """2 - Dos lineas que valen oro. HUD Modulo 02, titulo y tarjeta_tle
    de la ISS centrada. Se resaltan en relevo los campos "inclinacion"
    (violeta, el cielo) y "movimiento_medio" (ambar, el satelite) con
    Indicate + set_color bajo un mismo pie. De ahi sale la cuenta del
    periodo y, con Kepler, la altitud (formula_pie en relevo con los
    pies, misma zona). Cierra resaltando "epoca" en rojo suave: el TLE
    caduca. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ------------------------------------------
        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Dos líneas que valen oro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la tarjeta TLE ------------------------------------------
        tarjeta = tarjeta_tle(font_size=15)
        tarjeta.move_to(np.array([0.0, 0.7, 0.0]))

        self.play(FadeIn(tarjeta, scale=0.94), run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("Todo lo que hace falta para encontrar un "
                              "satélite cabe en dos líneas de texto: el "
                              "TLE."), zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: cuanto se inclina y cuantas vueltas da al dia -------------
        campo_inc = tarjeta.campos["inclinacion"]
        campo_mm = tarjeta.campos["movimiento_medio"]

        self.play(Indicate(campo_inc, scale_factor=1.2, color=C_CIELO),
                  run_time=0.7)
        campo_inc.set_color(C_CIELO)

        rot.mostrar(pie_curso("Cuánto se inclina su órbita y cuántas "
                              "vueltas da al día: 15.5."), zona="abajo",
                   run_time=0.45)
        self.wait(1.8)

        self.play(campo_inc.animate.set_color(CODE_INK),
                  Indicate(campo_mm, scale_factor=1.2, color=C_SAT),
                  run_time=0.7)
        campo_mm.set_color(C_SAT)
        self.wait(2.2)

        campo_mm.set_color(CODE_INK)

        # --- momento: del movimiento medio sale el periodo, y con kepler la altitud --
        rot.mostrar(pie_curso("Del movimiento medio sale el periodo, y "
                              "con Kepler, la altitud."), zona="abajo",
                   run_time=0.45)
        self.wait(2.2)

        rot.mostrar(formula_pie(r"T = 86400 / 15.5 = 92.9\ \text{min}"),
                   zona="abajo", run_time=0.45)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"h \approx 424\ \text{km}\ (\text{ISS})"),
                   zona="abajo", run_time=0.45)
        self.wait(2.6)

        # --- momento: pero caduca -------------------------------------------------
        campo_epoca = tarjeta.campos["epoca"]
        rot.mostrar(pie_curso("Pero caduca: cada día de propagación suma "
                              "kilómetros de error."), zona="abajo",
                   run_time=0.45)
        self.play(Indicate(campo_epoca, scale_factor=1.2, color=C_PELIGRO),
                  run_time=0.8)
        campo_epoca.set_color(C_PELIGRO)
        self.wait(3.0)

        # --- momento: refresca antes de cada pase ----------------------------------
        rot.mostrar(pie_curso("Refresca el TLE antes de cada pase."),
                   zona="abajo", run_time=0.45)
        self.wait(5.0)
