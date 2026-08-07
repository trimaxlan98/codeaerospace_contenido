class Clip6(Scene):
    """6 - El anillo lleno: el arco GSO casi asignado, el haz protegido por
    decadas de apuntado, el cruce geometrico inevitable de una constelacion
    NGSO y la asimetria de la regla 22.2."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo --------------------------------------------------
        modulo = hud_modulo("Modulo 06")
        titulo = titulo_curso("NGSO contra GSO: el anillo lleno")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.0)

        # --- momento: el anillo casi lleno -------------------------------------
        tierra = tierra_y_anillos()
        tierra.move_to(np.array([-0.6, -0.1, 0.0]))
        self.play(FadeIn(tierra.tierra), Create(tierra.anillo_gso),
                  Create(tierra.anillo_ngso), FadeIn(tierra.rotulos),
                  run_time=0.8)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in tierra.sats_gso],
                              lag_ratio=0.04),
                  LaggedStart(*[GrowFromCenter(d) for d in tierra.sats_ngso],
                              lag_ratio=0.05), run_time=0.7)
        self.play(LaggedStart(*[Indicate(d, color=C_GSO, scale_factor=1.6)
                                for d in tierra.sats_gso], lag_ratio=0.05),
                  run_time=1.2)
        rot.mostrar(pie_curso("A 36 000 km, un anillo único: el arco "
                              "geoestacionario. Casi todo asignado."),
                   zona="abajo", run_time=0.45)
        self.wait(5.4)

        # --- momento: el haz protegido -----------------------------------------
        estacion = Dot(tierra.estacion(-35.0), radius=0.06, color=C_ONDA)
        estacion.set_z_index(7)
        objetivo = tierra.sat_gso_mas_cercano(tierra.pos_gso(-35.0))
        enlace = haz(estacion, objetivo, semiancho=0.16, color=C_GSO)
        self.play(FadeIn(estacion), FadeIn(enlace), run_time=0.5)
        rot.mostrar(pie_curso("Cada estación lleva décadas apuntando a su "
                              "posición... bajo promesa de que nadie se "
                              "cruce."), zona="abajo", run_time=0.45)
        self.wait(5.5)

        # --- momento: el cruce geometrico -----------------------------------
        # 40 grados verificado en frames: el satelite NGSO que arranca en
        # 288 grados cae DENTRO del haz al terminar el giro.
        self.play(Rotate(tierra.sats_ngso, np.deg2rad(40.0),
                         about_point=tierra.centro), run_time=3.0)
        dentro = [d for d in tierra.sats_ngso if enlace.contiene(d)]
        for _ in range(2):
            self.play(enlace.animate.set_fill(color=C_PERDIDA, opacity=0.34)
                      .set_stroke(color=C_PERDIDA, opacity=0.9),
                      run_time=0.28)
            self.play(enlace.animate.set_fill(color=C_GSO, opacity=0.18)
                      .set_stroke(color=C_GSO, opacity=0.55),
                      run_time=0.28)
        if dentro:
            self.play(Indicate(dentro[0], color=C_PERDIDA, scale_factor=1.7),
                      run_time=0.5)
        rot.mostrar(pie_curso("Una constelación cruza ese haz varias veces "
                              "por minuto. El conflicto es geométrico: "
                              "inevitable."), zona="abajo", run_time=0.45)
        self.wait(5.3)

        # --- momento: la regla asimetrica ---------------------------------------
        etiqueta = etiqueta_hud("Regla 22.2")
        etiqueta.move_to(np.array([3.1, 1.2, 0.0]))
        self.play(FadeIn(etiqueta, shift=0.15 * DOWN), run_time=0.5)
        rot.mostrar(pie_curso("La regla es asimétrica: el que llega "
                              "después, se aparta. Sin importar cuántos "
                              "satélites traiga."), zona="abajo",
                   run_time=0.45)
        self.wait(5.5)
