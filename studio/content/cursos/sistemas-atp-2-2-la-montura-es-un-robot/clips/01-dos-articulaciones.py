class Clip1(Scene):
    """2.2.1 - La montura tiene dos articulaciones: el anillo de acimut
    gira, el brazo de elevacion sube. Se le hace seguir un Az/El
    concreto de un pase real. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Dos articulaciones"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la montura, anclada por su pivote ----------------------------
        mont = montura(alto=3.3, font_size=17)
        destino = LEFT * 2.55 + DOWN * 0.85
        delta = destino - mont.pivote
        mont.shift(delta)
        # `pivote`, `base_izq` y `base_der` son atributos FIJOS: hay que
        # arrastrarlos con el shift o `apuntar(az)` deja la marca del
        # anillo en el sitio donde nacio la pieza.
        mont.pivote = mont.pivote + delta
        mont.base_izq = mont.base_izq + delta
        mont.base_der = mont.base_der + delta
        self.play(FadeIn(mont), run_time=1.2)
        self.wait(1.0)

        # --- un pase real: la traza que va a seguir ------------------------
        perfil = perfil_pase(H_LEO, el_max_deg=60.0, mascara_deg=MASCARA,
                             az_culminacion_deg=100.0, n=241)
        n = len(perfil["az"])
        wp = [0, n // 4, n // 2, 3 * n // 4, n - 1]
        az_wp = [float(perfil["az"][i]) for i in wp]
        el_wp = [float(perfil["el"][i]) for i in wp]

        mont.apuntar(az_deg=az_wp[0], el_deg=el_wp[0])

        # --- primera articulacion: el anillo de acimut gira ----------------
        self.play(Indicate(mont.t_az, color=C_CALCULO, scale_factor=1.7),
                  run_time=1.2)
        az_t = ValueTracker(az_wp[0])
        mont.add_updater(lambda m: m.apuntar(az_deg=az_t.get_value()))
        self.play(az_t.animate.set_value(az_wp[1]), run_time=1.9,
                  rate_func=linear)
        mont.clear_updaters()
        self.wait(0.6)

        # --- segunda articulacion: el brazo de elevacion sube --------------
        self.play(Indicate(mont.t_el, color=C_CALCULO, scale_factor=1.7),
                  run_time=1.2)
        el_t = ValueTracker(el_wp[0])
        mont.add_updater(lambda m: m.apuntar(el_deg=el_t.get_value()))
        self.play(el_t.animate.set_value(el_wp[1]), run_time=1.9,
                  rate_func=linear)
        mont.clear_updaters()
        self.wait(0.6)

        rot.mostrar(cifra_pie("2 grados de libertad"), zona="abajo")
        self.wait(2.4)

        # --- las dos a la vez: siguiendo la traza entera -------------------
        az_t2 = ValueTracker(az_wp[1])
        el_t2 = ValueTracker(el_wp[1])
        mont.apuntar(az_deg=az_wp[1], el_deg=el_wp[1])
        mont.add_updater(lambda m: m.apuntar(az_deg=az_t2.get_value(),
                                             el_deg=el_t2.get_value()))

        lectura = always_redraw(
            lambda: tag_hud(f"az {fmt(az_t2.get_value(), 0)}  "
                            f"el {fmt(el_t2.get_value(), 0)}",
                            font_size=20).move_to(RIGHT * 3.25 + UP * 1.35))
        self.add(lectura)
        for i in range(2, len(wp)):
            self.play(az_t2.animate.set_value(az_wp[i]),
                      el_t2.animate.set_value(el_wp[i]), run_time=2.1,
                      rate_func=linear)
        mont.clear_updaters()
        self.wait(1.3)

        panel = panel_cifras(f"az {fmt(az_wp[-1], 0)} deg",
                             f"el {fmt(el_wp[-1], 0)} deg")
        self.play(FadeOut(lectura), run_time=0.3)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(10.5)
