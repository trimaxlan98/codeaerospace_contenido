class Clip1(Scene):
    """5.3.1 - Subir de banda una ultima vez: de Ka (32 GHz) al laser
    (193 THz) sobre la regla `banda_espacio` extendida; la regla de 1.3
    llevada al extremo y el haz que se vuelve estrecho. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Subir de banda una última vez")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la regla, ya conocida --------------------------------
        rot.mostrar(pie_curso("El espectro es una escalera: S, X, Ka, cada "
                              "peldaño diez veces más arriba."),
                    zona="abajo", run_time=0.5)
        be = banda_espacio(exp0=0, exp1=6, ancho=9.2)
        be.move_to(DOWN * 0.4)
        marca_s = be.marca(F_S_GHZ, f"S {fmt(F_S_GHZ, 1)}", color=C_BANDA)
        marca_x = be.marca(F_X_GHZ, f"X {fmt(F_X_GHZ, 1)}", color=C_BANDA)
        marca_ka = be.marca(F_KA_GHZ, f"Ka {fmt(F_KA_GHZ, 0)}",
                            color=C_BANDA)
        self.play(FadeIn(be), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(m, scale=0.7)
                                for m in (marca_s, marca_x, marca_ka)],
                              lag_ratio=0.25), run_time=1.2)
        self.wait(2.8)

        # --- momento: un escalon mas, hasta dejar de ser radio -------------
        rot.mostrar(pie_curso("Subamos un escalón más: tan arriba que ya "
                              "no es radio. Es luz."),
                    zona="abajo", run_time=0.5)
        marca_laser = be.marca(F_LASER_GHZ,
                               f"laser {fmt(F_LASER_THZ, 0)} THz",
                               color=C_BANDA)
        self.play(FadeIn(marca_laser, scale=0.7), run_time=0.9)
        self.wait(4.3)

        # --- momento: la regla de 1.3, al extremo ---------------------------
        rot.mostrar(pie_curso("La regla de siempre, al extremo: más "
                              "portadora, más ancho para el símbolo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.1)

        # --- momento: el haz se vuelve estrecho -----------------------------
        rot.mostrar(pie_curso("Y un haz tan corto de longitud de onda es "
                              "un haz ESTRECHO: antena chica, apuntar con "
                              "precisión."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(be, marca_s, marca_x, marca_ka, marca_laser),
                  run_time=0.7)

        origen_rf = LEFT * 3.6 + UP * 1.0
        origen_laser = LEFT * 3.6 + DOWN * 1.1
        antena_rf = Dot(origen_rf, radius=0.07, color=C_EJE)
        antena_laser = Dot(origen_laser, radius=0.07, color=C_EJE)
        haz_rf = Sector(radius=3.4, angle=50 * DEGREES,
                        start_angle=-25 * DEGREES, color=C_SENAL,
                        fill_opacity=0.28, stroke_width=1.6)
        haz_rf.shift(origen_rf)
        haz_laser = Sector(radius=3.4, angle=6 * DEGREES,
                           start_angle=-3 * DEGREES, color=C_SENAL,
                           fill_opacity=0.5, stroke_width=1.6)
        haz_laser.shift(origen_laser)
        et_rf = tag_junto(antena_rf, "radio: haz ancho", direccion=LEFT,
                          buff=0.18)
        et_laser = tag_junto(antena_laser, "láser: haz estrecho",
                             direccion=LEFT, buff=0.18)
        self.play(FadeIn(antena_rf), FadeIn(haz_rf), FadeIn(et_rf),
                  run_time=1.0)
        self.play(FadeIn(antena_laser), FadeIn(haz_laser), FadeIn(et_laser),
                  run_time=1.0)
        self.wait(4.6)

        # --- momento: sin espectro que pedir --------------------------------
        rot.mostrar(pie_curso("El láser no pide permiso a la WRC: ahí "
                              "arriba no hay espectro que repartir."),
                    zona="abajo", run_time=0.5)
        self.wait(5.5)
