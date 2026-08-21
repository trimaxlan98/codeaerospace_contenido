class Clip1(Scene):
    """2.2.1 - Soltar una particula en el campo viento: avanza tangente a
    la flecha local en cada instante. Ese rastro es la LINEA DE FLUJO,
    confirmada contra el campo. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Suelta una partícula")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo del viento ------------------------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_VIENTO, paso=0.9, escala=0.42)
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Este es el campo: el viento sopla distinto "
                              "en cada punto."), zona="abajo", run_time=0.5)
        self.play(FadeIn(campo), run_time=1.0)
        self.wait(2.6)

        # --- momento: soltar la particula -------------------------------------
        rot.mostrar(pie_curso("Sueltas una partícula ahí. ¿Hacia dónde "
                              "va?"), zona="abajo", run_time=0.5)
        p0 = P0_PARTICULA
        dot = Dot(pl.p(p0), radius=0.1, color=C_VEC)
        self.play(FadeIn(dot, scale=0.5), run_time=0.5)
        self.wait(1.6)

        # --- momento: el campo la empuja, tangente -----------------------------
        rot.mostrar(pie_curso("El campo la empuja: en cada instante, "
                              "avanza tangente a su flecha local."),
                    zona="abajo", run_time=0.5)
        lf = linea_flujo(pl, CAMPO_VIENTO, p0, T=T_FLUJO)
        self.play(Create(lf), MoveAlongPath(dot, lf), run_time=5.2,
                  rate_func=linear)
        self.wait(1.4)

        # --- momento: confirmar la tangencia en un punto ------------------------
        rot.mostrar(pie_curso("Comprueba en cualquier punto del rastro: "
                              "la flecha del campo coincide."),
                    zona="abajo", run_time=0.5)
        p_chk = lf.puntos[len(lf.puntos) // 2]
        flecha_chk = campo.en(*p_chk)
        self.play(Indicate(flecha_chk, color=C_CALCULO, scale_factor=1.18),
                  run_time=1.0)
        self.wait(2.8)

        # --- momento: el nombre y la formula --------------------------------------
        rot.mostrar(pie_curso("Ese rastro fucsia tiene nombre: LÍNEA DE "
                              "FLUJO."), zona="abajo", run_time=0.5)
        self.wait(2.2)
        rot.mostrar(formula_pie(r"\vec r\,'(t) = F(\vec r(t))"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Su velocidad, en todo momento, ES el "
                              "campo."), zona="abajo", run_time=0.5)
        self.wait(4.2)
