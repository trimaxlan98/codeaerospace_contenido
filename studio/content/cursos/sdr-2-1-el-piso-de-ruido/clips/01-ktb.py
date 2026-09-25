class Clip1(Scene):
    """2.1.1 - El piso de ruido termico kTB: -174.0 dBm por hercio, y sube
    con el ancho de banda: -141.0 en 2 kHz, -121.0 en 200 kHz, -110.2 en
    2.4 MHz. Escala vertical de dBm propia con tres escalones. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El piso de kTB"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- escala vertical de dBm, marco propio -------------------------
        DB_LO, DB_HI = -148.0, -104.0
        Y_LO, Y_HI = -1.9, 2.0
        EJE_X = -4.4
        LARGO_MAX = 8.4

        def y_de(dbm):
            return Y_LO + (dbm - DB_LO) / (DB_HI - DB_LO) * (Y_HI - Y_LO)

        eje = Line(np.array([EJE_X, Y_LO, 0.0]), np.array([EJE_X, Y_HI, 0.0]),
                  color=C_TENUE, stroke_width=2.2)
        piso_ref = Line(np.array([EJE_X, Y_LO, 0.0]),
                        np.array([EJE_X + LARGO_MAX, Y_LO, 0.0]),
                        color=S.C_EJE, stroke_width=1.6)
        u = tag_junto(eje, "dBm", UP, buff=0.16, font_size=20)
        u.move_to(np.array([EJE_X, Y_HI + 0.4, 0.0]))
        self.play(Create(eje), Create(piso_ref), FadeIn(u), run_time=0.9)
        self.wait(0.6)

        rot.mostrar(cifra_pie(f"{fmt(KTB_HZ, 1)} dBm/Hz"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        # --- tres escalones: el piso SUBE con el ancho de banda -----------
        pasos = [("2 kHz", KTB_2K, 3.4), ("200 kHz", KTB_200K, 6.0),
                ("2.4 MHz", KTB_2M4, LARGO_MAX)]
        for bw_txt, db, largo in pasos:
            y = y_de(db)
            tramo = Line(np.array([EJE_X, y, 0.0]),
                        np.array([EJE_X + largo, y, 0.0]),
                        color=C_CALCULO, stroke_width=3.6)
            marca = Line(np.array([EJE_X - 0.1, y, 0.0]),
                        np.array([EJE_X + 0.1, y, 0.0]), color=C_CALCULO,
                        stroke_width=2.4)
            cifra = tag_hud(f"{fmt(db, 1)} dBm", font_size=21)
            cifra.next_to(np.array([EJE_X + largo, y, 0.0]), RIGHT, buff=0.22)
            dato = tag_dato(bw_txt, font_size=19)
            dato.next_to(tramo, UP, buff=0.12)
            dato.align_to(tramo, LEFT)
            dato.shift(RIGHT * 0.22)
            self.play(Create(marca), Create(tramo), FadeIn(dato),
                      run_time=1.3)
            self.play(FadeIn(cifra, shift=RIGHT * 0.1), run_time=0.5)
            self.wait(2.8)

        self.wait(2.6)
        rot.mostrar(formula_pie(r"P_n = kTB"), zona="abajo", run_time=0.5)
        self.wait(6.5)
