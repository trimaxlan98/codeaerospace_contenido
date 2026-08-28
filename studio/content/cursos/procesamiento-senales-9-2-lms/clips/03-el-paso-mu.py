class Clip3(Scene):
    """9.2.3 - El compromiso del paso, medido: las tres curvas de
    aprendizaje del RESIDUO, su punto de convergencia y el suelo en que se
    quedan. Los dos ejes van en escala logaritmica. (~36 s)"""

    PISO, TECHO = -36.0, 0.0
    COLOR = {0.02: C_RUIDO, 0.005: C_SALIDA, 0.001: C_IDEAL}

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("El paso mu"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el eje: logaritmico en las dos direcciones ------------------
        # 76, 459 y 2894 muestras no caben legibles en un eje lineal (la
        # primera quedaria pegada al borde). Y la curva se dibuja
        # promediada POR TRAMO del eje log: tomar un punto de cada ocho
        # alias el rizado y llena el dibujo de picos que no existen.
        largo = len(CURVA[MUS[0]])
        bordes = np.unique(np.round(
            np.logspace(0.0, np.log10(largo), 190)).astype(int))
        wl = 0.5 * (np.log10(bordes[:-1]) + np.log10(bordes[1:]))
        db = {}
        for m in MUS:
            y = np.array([CURVA[m][a - 1:max(b, a)].mean()
                          for a, b in zip(bordes[:-1], bordes[1:])])
            db[m] = 10.0 * np.log10(np.maximum(y, 1e-12))

        rf = respuesta_dibujo(wl, db[MUS[0]], ancho=8.2, alto=3.7,
                              piso_db=self.PISO, techo_db=self.TECHO,
                              color=self.COLOR[MUS[0]])
        rf.move_to(LEFT * 1.25 + UP * 0.45)

        et_y = tag_hud("MSE en dB", font_size=18, color=C_DATO)
        et_y.next_to(rf.en(wl[0], self.TECHO), UR, buff=0.10)
        marcas_x = VGroup()
        for k in (1, 2, 3):
            p = rf.en(float(k), self.PISO)
            marcas_x.add(Line(p, p + DOWN * 0.13, color=C_EJE,
                              stroke_width=1.6))
            t = tag_hud(str(10 ** k), font_size=17, color=C_DATO)
            t.next_to(p + DOWN * 0.13, DOWN, buff=0.07)
            marcas_x.add(t)
        et_x = tag_hud("muestras log10", font_size=18, color=C_DATO)
        et_x.next_to(marcas_x, DOWN, buff=0.12)
        self.play(FadeIn(rf.ejes), FadeIn(marcas_x), FadeIn(et_y),
                  FadeIn(et_x), run_time=0.8)

        # --- las tres curvas, de la mas rapida a la mas fina -------------
        curvas, etiquetas = {}, {}
        for j, m in enumerate(MUS):
            c = rf.curva if j == 0 else rf.con_mag(db[m],
                                                   self.COLOR[m]).curva
            curvas[m] = c
            # el rotulo va a la ALTURA DEL SUELO medido, no al ultimo
            # punto dibujado (que salta con el rizado).
            t = tag_hud(f"mu {fmt(m, 3)}", font_size=19, color=self.COLOR[m])
            t.next_to(rf.en(wl[-1], 10.0 * np.log10(SUELO[m])), RIGHT,
                      buff=0.16)
            etiquetas[m] = t
            self.play(Create(c), FadeIn(t), run_time=1.4)
            self.wait(1.4 if j < 2 else 1.8)

        # --- donde converge cada una ------------------------------------
        pasos = []
        for m in MUS:
            x = float(np.log10(N_CONV[m]))
            y = 10.0 * np.log10(2.0 * SUELO[m])
            linea = DashedLine(rf.en(x, self.PISO), rf.en(x, y),
                               color=self.COLOR[m], stroke_width=1.8,
                               dash_length=0.07)
            punto = Dot(rf.en(x, y), radius=0.065, color=C_CALCULO)
            t = tag_hud(str(N_CONV[m]), font_size=18, color=C_CALCULO)
            # el ultimo cae junto al borde: ese rotulo se va a la
            # izquierda de su vertical y no al reves.
            lado = RIGHT * 0.32 if x < 3.2 else LEFT * 0.36
            t.next_to(rf.en(x, self.PISO), UP, buff=0.10).shift(lado)
            pasos.append(AnimationGroup(Create(linea), FadeIn(punto),
                                        FadeIn(t)))
        self.play(LaggedStart(*pasos, lag_ratio=0.35), run_time=2.2)
        rot.mostrar(cifra_pie("convergencia en muestras"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras(
            *[(f"mu {fmt(m, 3)}  n {N_CONV[m]}", self.COLOR[m])
              for m in MUS])
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)

        # --- y en que suelo se queda ------------------------------------
        # el suelo de mu = 0.001 es un tramo corto a proposito: no
        # converge hasta la muestra 2894 de las 3873 que hay.
        pasos = []
        for m in MUS:
            y = 10.0 * np.log10(SUELO[m])
            linea = DashedLine(rf.en(float(np.log10(N_CONV[m])), y),
                               rf.en(wl[-1], y), color=self.COLOR[m],
                               stroke_width=2.6, dash_length=0.10)
            v = tag_hud(fmt(SUELO[m], 4), font_size=18, color=C_CALCULO)
            v.next_to(etiquetas[m], RIGHT, buff=0.24)
            pasos.append(AnimationGroup(Create(linea), FadeIn(v)))
        self.play(LaggedStart(*pasos, lag_ratio=0.32), run_time=1.8)
        rot.mostrar(cifra_pie("suelo del temblor"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        veces = SUELO[MUS[0]] / SUELO[MUS[2]]
        rot.mostrar(cifra_pie(f"{fmt(veces, 0)} veces mas fino"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)
