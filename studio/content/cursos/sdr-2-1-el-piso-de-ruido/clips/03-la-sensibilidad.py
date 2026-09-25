class Clip3(Scene):
    """2.1.3 - La sensibilidad como escalera de TRES escalones, las DOS
    columnas sobre UNA sola escala vertical honesta (marcas cada 10 dBm):
    piso kTB*B (cian) -> +NF de la cascada (cian, escalon fino con leader)
    -> +SNR minima (gris, dato) = la sensibilidad (cian, resaltada). FM
    200 kHz llega a -107.9 dBm; la baliza de 2 kHz, mucho mas sensible,
    queda visiblemente mas ABAJO en -133.9 dBm: el mismo eje hace el
    contraste honesto (6 dB de la baliza no pueden medir en pantalla lo
    mismo que 12 dB de la FM). (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La sensibilidad"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- UNA escala vertical compartida, marcas cada 10 dBm ------------
        DB_LO, DB_HI = -145.0, -104.0
        Y_LO, Y_HI = -2.55, 2.85
        EJE_X = -6.4

        def y_de(dbm):
            return Y_LO + (dbm - DB_LO) / (DB_HI - DB_LO) * (Y_HI - Y_LO)

        eje = Line(np.array([EJE_X, Y_LO, 0.0]), np.array([EJE_X, Y_HI, 0.0]),
                  color=C_TENUE, stroke_width=2.2)
        u = tag_junto(eje, "dBm", UP, buff=0.16, font_size=20)
        u.move_to(np.array([EJE_X, Y_HI + 0.32, 0.0]))
        marcas = VGroup()
        for val in (-140, -130, -120, -110):
            y = y_de(val)
            tick = Line(np.array([EJE_X - 0.1, y, 0.0]),
                       np.array([EJE_X + 0.1, y, 0.0]), color=C_TENUE,
                       stroke_width=2.0)
            etq = tag_dato(str(val), font_size=20)
            etq.next_to(tick, RIGHT, buff=0.1)
            marcas.add(tick, etq)
        self.play(Create(eje), FadeIn(u), Create(marcas), run_time=1.0)
        self.wait(0.8)

        def columna(x0, db_floor, nf, snr_min, db_sens, caso_txt):
            y_floor, y_nf, y_sens = (y_de(db_floor), y_de(db_floor + nf),
                                     y_de(db_sens))
            l1, l_nf_largo, l3 = 1.8, 0.7, 2.4

            # --- escalon 1: el piso kTB*B (cian) ---------------------------
            t1 = Line(np.array([x0, y_floor, 0.0]),
                     np.array([x0 + l1, y_floor, 0.0]), color=C_CALCULO,
                     stroke_width=3.4)
            c1 = tag_hud(f"{fmt(db_floor, 1)} dBm", font_size=22)
            c1.next_to(t1, RIGHT, buff=0.2)
            self.play(Create(t1), FadeIn(c1), run_time=1.0)
            rot.mostrar(cifra_pie(f"piso {fmt(db_floor, 1)} dBm"),
                       zona="abajo", run_time=0.5)
            self.wait(1.6)

            # --- escalon 2: +NF (cian, fino, con leader a su rotulo) -------
            riser1 = DashedLine(np.array([x0, y_floor, 0.0]),
                                np.array([x0, y_nf, 0.0]), color=C_TENUE,
                                stroke_width=1.6, dash_length=0.05)
            t_nf = Line(np.array([x0, y_nf, 0.0]),
                       np.array([x0 + l_nf_largo, y_nf, 0.0]),
                       color=C_CALCULO, stroke_width=3.4)
            punta = np.array([x0 + l_nf_largo, y_nf, 0.0])
            fin_leader = punta + np.array([0.55, 0.42, 0.0])
            leader = Line(punta, fin_leader, color=C_CALCULO,
                         stroke_width=1.6)
            l_nf = tag_hud(f"+NF {fmt(nf, 2)} dB", font_size=20)
            l_nf.next_to(fin_leader, RIGHT, buff=0.08)
            self.play(Create(riser1), Create(t_nf), Create(leader),
                      FadeIn(l_nf), run_time=1.0)
            self.wait(1.8)

            # --- escalon 3: +SNR minima (gris, es dato) ---------------------
            riser2 = DashedLine(np.array([x0, y_nf, 0.0]),
                                np.array([x0, y_sens, 0.0]), color=C_TENUE,
                                stroke_width=1.8, dash_length=0.08)
            t3 = Line(np.array([x0, y_sens, 0.0]),
                     np.array([x0 + l3, y_sens, 0.0]), color=C_DATO,
                     stroke_width=3.6)
            rot_snr = tag_dato(f"SNR min {fmt(snr_min, 1)} dB", font_size=20)
            rot_snr.next_to(t3, UP, buff=0.14)
            rot_snr.align_to(t3, LEFT)
            self.play(Create(riser2), Create(t3), FadeIn(rot_snr),
                      run_time=1.1)
            self.wait(1.2)

            # --- la sensibilidad resultante, resaltada (cian) ---------------
            c3 = tag_hud(f"{fmt(db_sens, 1)} dBm", font_size=26)
            c3.next_to(t3, RIGHT, buff=0.22)
            caso = tag_dato(caso_txt, font_size=20)
            caso.next_to(c3, UP, buff=0.16)
            caso.align_to(c3, LEFT)
            self.play(FadeIn(c3, shift=RIGHT * 0.1), FadeIn(caso),
                      run_time=0.8)
            rot.mostrar(cifra_pie(f"sensibilidad {fmt(db_sens, 1)} dBm"),
                       zona="abajo", run_time=0.5)
            self.wait(3.2)

        columna(-4.6, KTB_200K, NF_ANT, SNR_FM, SENS_FM, "FM 200 kHz")
        columna(1.0, KTB_2K, NF_ANT, SNR_BAL, SENS_BAL, "baliza 2 kHz")

        self.wait(3.5)
