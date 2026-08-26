class Clip3(Scene):
    """8.1.3 - LEO: bajar la orbita. A la MISMA escala del clip 1 el LEO
    roza el suelo, y el ida y vuelta de usuario a usuario cae 65 veces.
    Pero no se queda quieto: el pase dura 12.1 min y cada traspaso cambia
    la ruta. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("LEO: bajar la orbita")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la misma escala, otra altura -----------------------
        rot.mostrar(pie_curso("Misma escala que antes. A 550 km, el satelite "
                              "casi roza el suelo."),
                    zona="abajo", run_time=0.5)
        cx, y_centro = -3.20, -2.35
        y_suelo = y_centro + R_TIERRA_U
        centro = np.array([cx, y_centro, 0.0])
        tierra = Arc(radius=R_TIERRA_U, start_angle=-20 * DEGREES,
                     angle=220 * DEGREES, arc_center=centro,
                     color=C_EJE, stroke_width=3.0)
        est = nodo("host", None, tam=0.30, color=C_RED)
        est.move_to(np.array([cx, y_suelo + 0.20, 0.0]))
        sat_geo = nodo("satelite", None, tam=0.40, color=C_RED)
        sat_geo.move_to(np.array([cx, y_suelo + GEO_U, 0.0]))
        et_geo = tag_junto(sat_geo, "GEO", LEFT, buff=0.22, font_size=18)
        # La orbita LEO, a la MISMA escala: un halo pegado a la Tierra.
        orbita = Arc(radius=R_TIERRA_U + LEO_U, start_angle=-20 * DEGREES,
                     angle=220 * DEGREES, arc_center=centro,
                     color=C_RED, stroke_width=2.0)
        ang = 42 * DEGREES
        p_leo = centro + (R_TIERRA_U + LEO_U) * np.array(
            [math.cos(ang), math.sin(ang), 0.0])
        sat_leo = nodo("satelite", None, tam=0.22, color=C_PAQUETE)
        sat_leo.move_to(p_leo)
        guia = Line(p_leo + np.array([0.16, 0.10, 0.0]),
                    np.array([-1.05, -0.95, 0.0]), color=C_PAQUETE,
                    stroke_width=1.6)
        et_leo = tag_hud("LEO  %s km   (%s de pantalla)"
                         % (miles(LEO_KM), fmt(LEO_U, 2)),
                         font_size=18, color=C_PAQUETE)
        et_leo.next_to(guia.get_end(), RIGHT, buff=0.16)
        escala = tag_hud("la misma escala: %s km por unidad de pantalla"
                         % miles(ESCALA_KM), font_size=16, color=C_EJE)
        escala.move_to(np.array([1.60, 2.45, 0.0]))
        self.play(Create(tierra), FadeIn(est), run_time=0.7)
        self.play(FadeIn(sat_geo), FadeIn(et_geo), FadeIn(escala),
                  run_time=0.6)
        self.play(Create(orbita), FadeIn(sat_leo, scale=1.6), run_time=0.7)
        self.play(Create(guia), FadeIn(et_leo), run_time=0.5)
        cifras = VGroup(
            tag_hud("GEO   %s km    un tramo  %s ms"
                    % (miles(GEO_KM), fmt(GEO_IDA, 1)), font_size=19),
            tag_hud("LEO      %s km    un tramo    %s ms"
                    % (miles(LEO_KM), fmt(LEO_IDA, 1)), font_size=19,
                    color=C_PAQUETE),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.move_to(np.array([2.30, 0.95, 0.0]))
        self.play(LaggedStart(*[FadeIn(c, shift=0.10 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=0.9)
        self.wait(3.4)

        # --- momento: los dos tiempos, a la misma escala ------------------
        rot.mostrar(pie_curso("Los dos viajes a la misma escala de tiempo: "
                              "aqui la longitud ES el tiempo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(tierra, est, sat_geo, et_geo, orbita,
                                 sat_leo, guia, et_leo, escala, cifras)),
                  run_time=0.5)
        x0, av = -5.30, 2.05
        r_geo = regla_viajes(4, "GEO", ancho_viaje=av, alto=0.48, fs=15,
                             nombres=["subir", "bajar", "subir", "bajar"])
        r_geo.shift(np.array([x0, 0.75, 0.0]))
        # El MISMO milisegundo por unidad de pantalla que la regla de arriba:
        # por eso el LEO sale como una astilla y no como cuatro casillas.
        av_leo = av * LEO_IDA / GEO_IDA
        r_leo = regla_viajes(4, "LEO", ancho_viaje=av_leo, alto=0.48, fs=15,
                             color=C_PAQUETE)
        r_leo.shift(np.array([x0, -0.35, 0.0]))
        c_geo = cifra_ms(r_geo, GEO_USR, font_size=22)
        c_leo = cifra_ms(r_leo, LEO_USR, font_size=22, color=C_PAQUETE)
        self.play(FadeIn(r_geo, shift=0.10 * RIGHT), FadeIn(c_geo),
                  run_time=0.6)
        self.wait(1.6)
        self.play(FadeIn(r_leo, shift=0.10 * RIGHT), FadeIn(c_leo),
                  run_time=0.6)
        et_veces = tag_hud("%s veces menos" % fmt(VECES_LEO, 1),
                           font_size=26)
        et_veces.move_to(np.array([0.60, -1.45, 0.0]))
        self.play(FadeIn(et_veces, scale=1.2), run_time=0.5)
        self.wait(3.2)

        # --- momento: pero no se queda quieto -----------------------------
        rot.mostrar(pie_curso("El precio: no se queda quieto. Este es un "
                              "pase entero sobre la antena."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(r_geo, c_geo, r_leo, c_leo, et_veces)),
                  run_time=0.5)
        g = grafica(ELEV, (PASE_T0, PASE_T1), (0.0, 66.0), ancho=8.6,
                    alto=2.30, color=C_CIFRA, muestras=121,
                    etiqueta_x="t (s)", etiqueta_y="elevacion (grados)")
        g.move_to(np.array([0.0, 0.95, 0.0]))
        curva = g.curva
        g.remove(curva)
        umbral = g.horizontal_en(ELEV_UMBRAL, color=C_COLA)
        et_umbral = tag_hud("%s grados" % fmt(ELEV_UMBRAL, 0),
                            font_size=17, color=C_COLA)
        et_umbral.next_to(umbral, UP, buff=0.08).shift(LEFT * 3.10)
        self.play(FadeIn(g), run_time=0.5)
        self.play(Create(curva), run_time=1.3)
        self.play(Create(umbral), FadeIn(et_umbral), run_time=0.5)
        datos = VGroup(
            tag_hud("pase entero, horizonte a horizonte   %s min"
                    % fmt(PASE_MIN, 1), font_size=18),
            tag_hud("por encima de %s grados (debajo, la antena lo "
                    "suelta)    %s min"
                    % (fmt(ELEV_UMBRAL, 0), fmt(PASE_UTIL_MIN, 1)),
                    font_size=18),
            tag_hud("y el retardo cambia con el: de %s a %s ms por tramo"
                    % (fmt(LEO_IDA_CENIT, 1), fmt(LEO_IDA_HORIZ, 1)),
                    font_size=18, color=C_PAQUETE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        datos.move_to(np.array([0.0, -1.85, 0.0]))
        self.play(LaggedStart(*[FadeIn(d, shift=0.10 * UP) for d in datos],
                              lag_ratio=0.32), run_time=1.1)
        self.wait(3.6)

        # --- momento: el traspaso -----------------------------------------
        rot.mostrar(pie_curso("Cuando se pone, otro entra. Y ese traspaso "
                              "es una ruta que cambia."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(g, curva, umbral, et_umbral, datos)),
                  run_time=0.5)
        base = np.array([0.0, -1.95, 0.0])
        antena = nodo("host", None, tam=0.40, color=C_RED)
        antena.move_to(base)
        et_ant = tag_junto(antena, "la antena", DOWN, buff=0.16,
                           font_size=17)
        cielo = DashedLine(base + np.array([-3.10, 0.0, 0.0]),
                           base + np.array([3.10, 0.0, 0.0]),
                           color=C_EJE, stroke_width=1.6, dash_length=0.10)
        arco = Arc(radius=2.95, start_angle=8 * DEGREES,
                   angle=164 * DEGREES, arc_center=base,
                   color=C_EJE, stroke_width=1.4)

        def en_cielo(grados):
            a = grados * DEGREES
            return base + 2.95 * np.array([math.cos(a), math.sin(a), 0.0])

        sat_a = nodo("satelite", None, tam=0.34, color=C_RED)
        sat_a.move_to(en_cielo(158))
        sat_b = nodo("satelite", None, tam=0.34, color=C_RED)
        sat_b.move_to(en_cielo(38))
        self.play(FadeIn(antena), FadeIn(et_ant), Create(cielo),
                  Create(arco), run_time=0.7)
        self.play(FadeIn(sat_a), FadeIn(sat_b), run_time=0.5)
        v_a = Line(base + np.array([0.0, 0.26, 0.0]), en_cielo(158),
                   color=C_OK, stroke_width=3.4)
        self.play(Create(v_a), run_time=0.5)
        et_a = tag_hud("se pone", font_size=18, color=C_PERDIDA)
        et_a.next_to(sat_a, UP, buff=0.18)
        et_b = tag_hud("entra", font_size=18, color=C_OK)
        et_b.next_to(sat_b, UP, buff=0.18)
        self.wait(1.4)
        v_b = Line(base + np.array([0.0, 0.26, 0.0]), en_cielo(38),
                   color=C_OK, stroke_width=3.4)
        self.play(v_a.animate.set_stroke(C_PERDIDA, opacity=0.35),
                  FadeIn(et_a), run_time=0.5)
        self.play(Create(v_b), FadeIn(et_b), run_time=0.6)
        et_tras = tag_hud("un pase de %s min  ->  %s traspasos por hora, "
                          "cada uno una ruta nueva"
                          % (fmt(PASE_MIN, 1), fmt(TRASPASOS_HORA, 1)),
                          font_size=19)
        et_tras.move_to(np.array([0.0, 1.98, 0.0]))
        nota = tag_hud("(Tierra sin rotar: el pase real es algo mas corto)",
                       font_size=16, color=C_EJE)
        nota.move_to(np.array([0.0, 1.48, 0.0]))
        self.play(FadeIn(et_tras, shift=0.10 * UP), run_time=0.5)
        self.play(FadeIn(nota), run_time=0.4)
        self.wait(4.0)
