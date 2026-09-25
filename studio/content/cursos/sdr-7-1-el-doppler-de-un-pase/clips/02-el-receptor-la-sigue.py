class Clip2(Scene):
    """7.1.2 - Dos waterfalls esquematicos de la MISMA senal (tono +
    ruido, S.tono/S.ruido_complejo/S.espectro_db fila a fila, eje +-15
    kHz): sin corregir, la raya sigue la curva del Doppler; el NCO
    (fucsia) recorre esa misma curva predicha y, al restarla, la senal
    corregida queda fija. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El receptor la sigue"), zona="arriba",
                   run_time=0.6)
        self.wait(0.4)

        # --- construir los dos waterfalls fila a fila -----------------------
        FS_WF = 48e3
        COLUMNAS = 256
        N_FILAS = 48
        idx = np.linspace(0, len(T_P) - 1, N_FILAS).astype(int)
        t_muestra = T_P[idx]
        dop_muestra = DOP[idx]

        f_ref, _ = S.espectro_db(S.ruido_complejo(COLUMNAS * 4, 1.0, 0),
                                 FS_WF, nfft=COLUMNAS, ref="abs")
        banda = (f_ref >= -15e3) & (f_ref <= 15e3)
        f_banda = f_ref[banda]

        filas_sin, filas_con = [], []
        for k, dk in enumerate(dop_muestra):
            x_sin = S.tono(dk, FS_WF, COLUMNAS * 4) + S.ruido_complejo(
                COLUMNAS * 4, 0.05, 1000 + k)
            _, d_sin = S.espectro_db(x_sin, FS_WF, nfft=COLUMNAS, ref="abs")
            filas_sin.append(d_sin[banda])

            x_con = S.tono(0.0, FS_WF, COLUMNAS * 4) + S.ruido_complejo(
                COLUMNAS * 4, 0.05, 5000 + k)
            _, d_con = S.espectro_db(x_con, FS_WF, nfft=COLUMNAS, ref="abs")
            filas_con.append(d_con[banda])

        filas_sin = np.array(filas_sin)
        filas_sin -= filas_sin.max()
        filas_con = np.array(filas_con)
        filas_con -= filas_con.max()

        picos_sin = np.array([S.pico(f_banda, fila)[0]
                              for fila in filas_sin])
        picos_con = np.array([S.pico(f_banda, fila)[0]
                              for fila in filas_con])
        excursion_khz = (picos_sin.max() - picos_sin.min()) / 1000.0
        residuo_hz = float(np.abs(picos_con).max())

        wf_sin = S.waterfall(filas_sin, ancho=4.8, alto=3.3, piso=-24.0,
                             techo=0.0)
        wf_con = S.waterfall(filas_con, ancho=4.8, alto=3.3, piso=-24.0,
                             techo=0.0)
        grupo = Group(wf_sin, wf_con).arrange(RIGHT, buff=1.9)
        grupo.move_to(UP * 0.35)
        marco_sin = Rectangle(width=wf_sin.width, height=wf_sin.height,
                             stroke_color=C_EJE, stroke_width=1.6)
        marco_sin.move_to(wf_sin.get_center())
        marco_con = Rectangle(width=wf_con.width, height=wf_con.height,
                             stroke_color=C_EJE, stroke_width=1.6)
        marco_con.move_to(wf_con.get_center())

        et_sin = tag_junto(wf_sin, "sin corregir", UP, buff=0.2,
                           font_size=22)
        et_con = tag_junto(wf_con, "corregida", UP, buff=0.2, font_size=22)

        self.play(FadeIn(wf_sin), FadeIn(wf_con), Create(marco_sin),
                  Create(marco_con), run_time=1.2)
        self.wait(0.8)
        self.play(FadeIn(et_sin), FadeIn(et_con), run_time=0.6)
        self.wait(0.6)

        # --- el eje de frecuencia (+-15 kHz) bajo cada panel -----------------
        def x_de(img, freq):
            return (img.get_left()[0] + (freq - f_banda[0])
                    / (f_banda[-1] - f_banda[0]) * img.width)

        def y_de(img, t):
            return (img.get_top()[1] - (t - t_muestra[0])
                    / (t_muestra[-1] - t_muestra[0]) * img.height)

        def eje_f(marco, img):
            g = VGroup()
            for khz, txt in [(-15, "-15"), (0, "0"), (15, "15")]:
                xp = x_de(img, khz * 1000.0)
                yb = marco.get_bottom()[1]
                t = Line(np.array([xp, yb, 0.0]), np.array([xp, yb - 0.08, 0.0]),
                         color=C_EJE, stroke_width=1.4)
                lbl = tag_hud(txt, font_size=14, color=C_TENUE)
                lbl.next_to(t, DOWN, buff=0.06)
                g.add(t, lbl)
            return g

        eje_sin = eje_f(marco_sin, wf_sin)
        eje_con = eje_f(marco_con, wf_con)
        u_khz = tag_junto(eje_con, "kHz", RIGHT, buff=0.12, font_size=15)

        # --- flecha "tiempo" a la izquierda del primer panel -----------------
        arriba_t = marco_sin.get_left() + LEFT * 0.3 + UP * (
            marco_sin.height / 2 - 0.05)
        abajo_t = marco_sin.get_left() + LEFT * 0.3 + DOWN * (
            marco_sin.height / 2 - 0.05)
        flecha_t = Arrow(arriba_t, abajo_t, buff=0.0, color=C_TENUE,
                         stroke_width=2.4, max_tip_length_to_length_ratio=0.14)
        et_t = tag_junto(flecha_t, "tiempo", UP, buff=0.12, font_size=16)

        self.play(FadeIn(eje_sin), FadeIn(eje_con), FadeIn(u_khz),
                  run_time=0.6)
        self.wait(0.5)
        self.play(GrowArrow(flecha_t), FadeIn(et_t), run_time=0.6)
        self.wait(1.0)

        # --- el NCO recorre la curva predicha (fucsia, sobre "sin corregir") --
        pts_nco = [np.array([x_de(wf_sin, dop_muestra[k]),
                            y_de(wf_sin, t_muestra[k]), 0.0])
                  for k in range(N_FILAS)]
        curva_nco = VMobject(stroke_color=C_LO, stroke_width=3.0)
        curva_nco.set_points_smoothly(pts_nco)
        curva_nco = DashedVMobject(curva_nco, num_dashes=36)
        et_nco = tag_hud("NCO", font_size=19, color=C_LO)
        et_nco.move_to(pts_nco[0] + np.array([0.5, 0.22, 0.0]))
        self.play(Create(curva_nco), run_time=3.6)
        self.wait(0.5)
        self.play(FadeIn(et_nco), run_time=0.5)
        self.wait(1.4)

        flecha = Arrow(marco_sin.get_right(), marco_con.get_left(),
                      buff=0.15, color=C_TENUE, stroke_width=3.0)
        self.play(GrowArrow(flecha), run_time=0.8)
        self.wait(2.0)

        cian_sin = tag_hud(f"{fmt(excursion_khz, 1)} kHz", font_size=21)
        cian_sin.next_to(eje_sin, DOWN, buff=0.35)
        cian_con = tag_hud(f"{fmt(residuo_hz, 0)} Hz", font_size=21)
        cian_con.next_to(eje_con, DOWN, buff=0.35)
        self.play(FadeIn(cian_sin), run_time=0.5)
        self.wait(1.8)
        self.play(FadeIn(cian_con), run_time=0.5)
        self.wait(13.0)
