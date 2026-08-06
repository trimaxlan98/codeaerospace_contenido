class Clip3(Scene):
    """3 - Del TLE a la antena. Cadena de seis marcos de referencia en dos
    filas (TLE -> SGP4 -> ECI arriba; ECEF -> ENU -> AZ/EL abajo, en "S"
    bajo ECI para mantener corta la diagonal entre filas) que traduce el
    texto del TLE en los dos numeros que el rotor entiende. Un pulso marca
    el paso critico ECI->ECEF (la Tierra rota bajo la orbita) y un reloj
    desincronizado dispara un destello rojo de error sobre toda la cadena.
    (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Del TLE a la antena")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.2)

        # --- momento: la fila de arriba, el mundo de los datos -------------------
        tle = bloque("TLE", ancho=1.9, color=C_CIELO)
        sgp4 = bloque("SGP4", ancho=1.9, color=C_CIELO)
        eci = bloque("ECI", ancho=1.9, color=C_CIELO)
        tle.move_to(np.array([-2.4, 1.1, 0.0]))
        sgp4.move_to(np.array([0.0, 1.1, 0.0]))
        eci.move_to(np.array([2.4, 1.1, 0.0]))
        fila_sup = VGroup(tle, sgp4, eci)

        self.play(FadeIn(fila_sup, lag_ratio=0.15), run_time=0.7)
        self.wait(0.4)

        # --- momento: la fila de abajo, en "S" bajo ECI ---------------------------
        # ECEF queda casi debajo de ECI (diagonal corta, sin cruzar SGP4/ENU) y
        # el resto de la fila avanza hacia la izquierda: ECEF -> ENU -> AZ/EL.
        ecef = bloque("ECEF", ancho=1.9, color=C_ANTENA)
        enu = bloque("ENU", ancho=1.9, color=C_ANTENA)
        azel = bloque("AZ/EL", ancho=1.9, color=C_ANTENA)
        ecef.move_to(np.array([2.1, -0.5, 0.0]))
        enu.move_to(np.array([-0.3, -0.5, 0.0]))
        azel.move_to(np.array([-2.7, -0.5, 0.0]))
        fila_inf = VGroup(ecef, enu, azel)

        self.play(FadeIn(fila_inf, lag_ratio=0.15), run_time=0.7)
        self.wait(0.4)

        # --- momento: la cadena completa, seis marcos conectados -----------------
        c1 = conectar(tle, sgp4, color=C_EJE)
        c2 = conectar(sgp4, eci, color=C_EJE)
        c3 = conectar(eci, ecef, color=C_EJE)          # la diagonal entre filas
        c4 = conectar(ecef, enu, color=C_EJE)
        c5 = conectar(enu, azel, color=C_EJE)
        self.play(Create(c1), Create(c2), run_time=0.5)
        self.play(Create(c3), run_time=0.5)
        self.play(Create(c4), Create(c5), run_time=0.5)

        self.play(flujo([c1, c2, c3, c4, c5], color=C_ACENTO,
                        por_conexion=0.5))
        rot.mostrar(pie_curso("Del texto a los dos números que el rotor "
                              "entiende: seis marcos de referencia."),
                   zona="abajo", run_time=0.45)
        self.wait(5.2)

        # --- momento: el paso critico, ECI -> ECEF --------------------------------
        self.play(Indicate(eci, color=C_CIELO, scale_factor=1.15),
                  Indicate(ecef, color=C_ANTENA, scale_factor=1.15),
                  flujo([c3], color=C_ACENTO, por_conexion=0.7),
                  run_time=1.0)
        rot.mostrar(pie_curso("El paso clave: la Tierra rota bajo la "
                              "órbita."), zona="abajo", run_time=0.45)
        self.wait(5.0)

        # --- momento: el reloj desincronizado, destello rojo sobre la cadena -----
        reloj = etiqueta_hud("RELOJ +1 S → 0.8° DE ERROR", color=C_PELIGRO)
        reloj.move_to(np.array([0.0, -1.7, 0.0]))
        self.play(FadeIn(reloj, shift=0.15 * UP), run_time=0.5)
        self.play(flujo([c1, c2, c3, c4, c5], color=C_PELIGRO,
                        por_conexion=0.42))
        rot.mostrar(pie_curso("Un segundo de reloj desincronizado: ocho "
                              "veces el presupuesto de error. Sincroniza "
                              "por GPS."), zona="abajo", run_time=0.45)
        self.wait(5.4)

        # --- momento: cierre, pura trigonometria ----------------------------------
        rot.mostrar(pie_curso("Al final, pura trigonometría: acimut y "
                              "elevación."), zona="abajo", run_time=0.45)
        self.wait(5.4)
