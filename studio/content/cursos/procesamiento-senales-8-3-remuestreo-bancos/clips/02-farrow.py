class Clip2(Scene):
    """8.3.2 - A veces hace falta el valor de la señal ENTRE dos muestras.
    Farrow lo interpola, y coincide con el valor de verdad... mientras
    sobre banda: el error se dispara al acercarse a Nyquist. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("El retardo fraccionario"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el tono muestreado y el valor que cae ENTRE dos muestras -----
        # se dibuja el tramo interior (4..59): error_farrow ya descarta 4
        # muestras a cada lado, donde la interpolacion no tiene vecinos.
        i0, i1 = 4, 36
        sec = Secuencia(X_F[i0:i1], i0, (-1.25, 1.25), ancho=9.4, alto=2.9,
                        color=C_MUESTRA, radio=0.05)
        sec.move_to(UP * 0.30)
        n_denso = np.linspace(i0, i1 - 1, 700)
        curva = sec.curva_de(n_denso, np.sin(2 * np.pi * 300 * n_denso / FS_R),
                             color=C_SENAL, grosor=2.2)
        et_x = tag_hud("300 Hz", font_size=19, color=C_MUESTRA)
        et_x.next_to(sec, UP, buff=0.14).align_to(sec, LEFT)
        self.play(FadeIn(sec), FadeIn(et_x), run_time=0.9)
        self.wait(1.2)
        self.play(Create(curva), run_time=1.4)
        rot.mostrar(cifra_pie(f"mu = {MU} muestras"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        # --- lo que calcula Farrow, y el valor exacto: encima -------------
        idx = list(range(i0 + 2, i1 - 1, 3))
        puntos_f = VGroup(*[Dot(sec.en(k - MU, Y_F[k]), radius=0.062,
                                color=C_SALIDA) for k in idx])
        anillos = VGroup(*[Circle(radius=0.115, color=C_IDEAL,
                                  stroke_width=2.4)
                           .move_to(sec.en(k - MU, X_EXACTO[k])) for k in idx])
        et_f = tag_hud("Farrow", font_size=19, color=C_SALIDA)
        et_f.next_to(sec, DOWN, buff=0.16).align_to(sec, LEFT)
        et_e = tag_hud("exacto", font_size=19, color=C_IDEAL)
        et_e.next_to(et_f, RIGHT, buff=0.55)
        self.play(LaggedStart(*[FadeIn(p, scale=0.6) for p in puntos_f],
                              lag_ratio=0.06), FadeIn(et_f), run_time=1.3)
        self.wait(1.4)
        self.play(LaggedStart(*[Create(a) for a in anillos], lag_ratio=0.06),
                  FadeIn(et_e), run_time=1.3)
        rot.mostrar(cifra_pie(f"error rms {RMS_FARROW[FRECS_F[0]]:.1e}"),
                    zona="abajo", run_time=0.45)
        self.wait(3.0)

        # --- donde deja de valer: el error contra la frecuencia -----------
        self.play(FadeOut(sec), FadeOut(curva), FadeOut(puntos_f),
                  FadeOut(anillos), FadeOut(et_x), FadeOut(et_f),
                  FadeOut(et_e), run_time=0.8)

        ANCHO_E, ALTO_E = 7.6, 3.5
        CENTRO_E = DOWN * 0.30 + RIGHT * 0.45
        F_LO, F_HI = FRECS_F[0], FRECS_F[-1]
        DEC_LO, DEC_HI = -5, 0

        def _pe(f, v):
            fx = (float(f) - F_LO) / (F_HI - F_LO)
            fy = (float(np.log10(v)) - DEC_LO) / (DEC_HI - DEC_LO)
            return CENTRO_E + np.array([(fx - 0.5) * ANCHO_E,
                                        (fy - 0.5) * ALTO_E, 0.0])

        eje_x = Line(_pe(F_LO, 10.0 ** DEC_LO), _pe(F_HI, 10.0 ** DEC_LO),
                     color=C_EJE, stroke_width=1.6)
        eje_y = Line(_pe(F_LO, 10.0 ** DEC_LO), _pe(F_LO, 10.0 ** DEC_HI),
                     color=C_EJE, stroke_width=1.6)
        rejilla = VGroup()
        etiquetas_y = VGroup()
        for d in range(DEC_LO, DEC_HI + 1):
            v = 10.0 ** d
            rejilla.add(DashedLine(_pe(F_LO, v), _pe(F_HI, v),
                                   color=C_REJILLA, stroke_width=1.0,
                                   dash_length=0.06))
            e = tag_hud(f"1e{d}", font_size=17, color=C_TENUE)
            e.next_to(_pe(F_LO, v), LEFT, buff=0.16)
            etiquetas_y.add(e)
        et_esc = tag_hud("rms", font_size=19, color=C_RUIDO)
        et_esc.next_to(_pe(F_LO, 10.0 ** DEC_HI), UP, buff=0.34)
        etiquetas_x = VGroup()
        for f in FRECS_F:
            e = tag_hud(f"{int(f)}", font_size=17, color=C_TENUE)
            e.next_to(_pe(f, 10.0 ** DEC_LO), DOWN, buff=0.18)
            etiquetas_x.add(e)
        et_hz = tag_hud("Hz", font_size=17, color=C_TENUE)
        et_hz.next_to(etiquetas_x[-1], RIGHT, buff=0.30)

        self.play(Create(eje_x), Create(eje_y),
                  FadeIn(rejilla), FadeIn(etiquetas_y), FadeIn(et_esc),
                  FadeIn(etiquetas_x), FadeIn(et_hz), run_time=1.3)
        self.wait(0.8)

        pts = [_pe(f, RMS_FARROW[f]) for f in FRECS_F]
        traza = VMobject(color=C_RUIDO, stroke_width=3.0)
        traza.set_points_as_corners(pts)
        marcas = VGroup(*[Dot(p, radius=0.07, color=C_RUIDO) for p in pts])
        self.play(FadeIn(marcas[0]), run_time=0.4)
        rot.mostrar(cifra_pie(f"{int(FRECS_F[0])} Hz rms "
                              f"{RMS_FARROW[FRECS_F[0]]:.1e}"),
                    zona="abajo", run_time=0.45)
        self.wait(1.6)
        self.play(Create(traza), run_time=1.6)
        for f in FRECS_F[1:]:
            self.play(FadeIn(marcas[list(FRECS_F).index(f)]), run_time=0.3)
            rot.mostrar(cifra_pie(f"{int(f)} Hz rms {RMS_FARROW[f]:.1e}"),
                        zona="abajo", run_time=0.45)
            self.wait(1.9)

        rot.mostrar(cifra_pie(f"x{RMS_FARROW[F_HI] / RMS_FARROW[F_LO]:.0f} "
                              f"peor"), zona="abajo", run_time=0.45)
        self.play(Indicate(marcas[-1], scale_factor=1.6, color=C_RUIDO),
                  run_time=0.8)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"y[n] = x(n - \mu)"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)
