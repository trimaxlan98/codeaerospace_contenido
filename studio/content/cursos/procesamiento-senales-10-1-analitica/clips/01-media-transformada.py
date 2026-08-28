class Clip1(Scene):
    """10.1.1 - La receta es literal: DFT, cero a las frecuencias
    negativas, vuelta. Un seno se convierte en un fasor de modulo
    constante. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Media transformada"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el espectro bilateral del tono puro ---------------------------
        Xf = np.fft.fft(X_TONO)
        freqs = np.fft.fftfreq(N_A, d=1.0 / FS_A)
        orden = np.argsort(freqs)
        f_eje = freqs[orden]

        h = np.zeros(N_A)
        h[0] = 1.0
        h[N_A // 2] = 1.0
        h[1:N_A // 2] = 2.0
        Xf_a = Xf * h
        ref = float(np.max(np.abs(Xf_a)) ** 2)
        db_antes = a_db(np.abs(Xf) ** 2, ref=ref)[orden]
        db_despues = a_db(np.abs(Xf_a) ** 2, ref=ref)[orden]

        ed = EspectroDoble(f_eje, db_antes, piso_db=-40.0, ancho=10.6,
                           alto=2.6, color=C_BANDA)
        ed.move_to(UP * 1.65)
        et_x = tag_hud("X[k]", font_size=19, color=C_BANDA)
        et_x.next_to(ed, LEFT, buff=0.24)
        cero_f = tag_hud("0", font_size=17, color=C_TENUE)
        cero_f.next_to(ed.en(0.0, -40.0), DOWN, buff=0.12)
        self.play(FadeIn(ed.ejes), FadeIn(et_x), FadeIn(cero_f), run_time=0.6)
        self.play(Create(ed.curva), FadeIn(ed.area), run_time=1.6)
        self.wait(1.8)

        # --- se apaga la mitad negativa -------------------------------------
        gem = ed.con_db(db_despues)
        self.play(Transform(ed.curva, gem.curva), Transform(ed.area, gem.area),
                  run_time=1.8)
        rot.mostrar(cifra_pie("mitad negativa a cero"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        self.play(FadeOut(ed), FadeOut(et_x), FadeOut(cero_f), run_time=0.7)

        # --- lo que queda en el tiempo: un fasor de modulo constante -------
        centro = DOWN * 0.35
        eje_re = Line(centro + LEFT * 1.7, centro + RIGHT * 1.7,
                     color=C_TENUE, stroke_width=1.3)
        eje_im = Line(centro + DOWN * 1.7, centro + UP * 1.7,
                     color=C_TENUE, stroke_width=1.3)
        et_re = tag_hud("Re", font_size=17, color=C_TENUE)
        et_re.next_to(eje_re, RIGHT, buff=0.10)
        et_im = tag_hud("Im", font_size=17, color=C_TENUE)
        et_im.next_to(eje_im, UP, buff=0.10)
        self.play(FadeIn(eje_re), FadeIn(eje_im), FadeIn(et_re), FadeIn(et_im),
                  run_time=0.6)

        ESCALA = 1.5
        idx = np.arange(100, 135)
        pts = [centro + ESCALA * np.array([RE_TONO[i], IM_TONO[i], 0.0])
              for i in idx]
        traza = VMobject(color=C_CALCULO, stroke_width=1.5)
        traza.set_points_smoothly(pts)
        punto = Dot(pts[0], radius=0.09, color=C_CALCULO)
        radio = Line(centro, pts[0], color=C_CALCULO, stroke_width=2.6)
        radio.add_updater(lambda m: m.put_start_and_end_on(
            centro, punto.get_center()))
        self.play(Create(traza), run_time=1.2)
        self.add(radio)
        self.play(FadeIn(punto), run_time=0.3)
        self.play(MoveAlongPath(punto, traza), run_time=2.4, rate_func=linear)
        radio.clear_updaters()
        rot.mostrar(cifra_pie(f"modulo {fmt(MOD_TONO, 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"desviacion {fmt(DESV_MOD, 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras((f"modulo {fmt(MOD_TONO, 4)}", C_CALCULO),
                             (f"desviacion {fmt(DESV_MOD, 4)}", C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"X_a[k] = H[k]\,X[k]"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
