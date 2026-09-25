class Clip3(Scene):
    """7.3.3 - La rejilla Doppler x fase de codigo (|corr|^2 sumada en 10
    ms, dB sobre la media) se barre fila a fila: el receptor prueba cada
    Doppler. Dibujo reducido al maximo de cada 22 muestras. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La rejilla"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        GRUPO = 22                                   # muestras por columna
        n_f, n_j = REJ.shape
        red = REJ.reshape(n_f, n_j // GRUPO, GRUPO).max(axis=2)
        mapa_db = 10 * np.log10(red / REJ.mean())
        TECHO = float(mapa_db.max())

        MX0, MX1, MY_T, MY_B = -5.3, 5.3, 2.5, -1.75
        W, H = MX1 - MX0, MY_T - MY_B
        h_f = H / n_f

        def y_fila(i):                   # fila 0 (-5 kHz) abajo
            return MY_B + (i + 0.5) * h_f

        def x_chip(ch):
            return MX0 + (2 * ch / n_j) * W

        def imagen(filas, ancho, alto):
            img = S.waterfall(filas, ancho=ancho, alto=alto, piso=0.0,
                              techo=TECHO)
            img.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
            return img

        # --- el marco y los ejes ---------------------------------------------
        marco = Rectangle(width=W, height=H, stroke_color=C_EJE,
                          stroke_width=1.4)
        marco.move_to([(MX0 + MX1) / 2, (MY_T + MY_B) / 2, 0])
        t_dop = VGroup()
        for fd in (-5000.0, 0.0, 5000.0):
            i = int(np.argmin(np.abs(DOPS - fd)))
            t = tag_hud(f"{fd / 1e3:+.0f}" if fd else "0", font_size=19,
                        color=C_TENUE)
            t.move_to([MX0 - 0.38, y_fila(i), 0])
            t_dop.add(t)
        u_k = tag_hud("kHz", font_size=19, color=C_TENUE)
        u_k.move_to([MX0 - 0.38, MY_T + 0.3, 0])
        t_ch = VGroup()
        for ch in (0, 250, 500, 750, 1000):
            p = np.array([x_chip(ch), MY_B, 0])
            t_ch.add(Line(p, p + DOWN * 0.1, color=C_EJE, stroke_width=1.6))
            t = tag_hud(f"{ch}", font_size=19, color=C_TENUE)
            t.next_to(p, DOWN, buff=0.16)
            t_ch.add(t)
        u_c = tag_junto(t_ch[-1], "chips", DOWN, buff=0.1, font_size=20)

        # barra de color (dB sobre la media de la rejilla)
        barra = imagen(np.linspace(TECHO, 0.0, 120)[:, None], 0.2, H)
        barra.set_resampling_algorithm(RESAMPLING_ALGORITHMS["bilinear"])
        barra.move_to([MX1 + 0.45, (MY_T + MY_B) / 2, 0])
        t_bar = VGroup()
        for v in (0, 5, 10):
            t = tag_hud(f"{v}", font_size=18, color=C_TENUE)
            t.move_to([MX1 + 0.85, MY_B + v / TECHO * H, 0])
            t_bar.add(t)
        u_b = tag_hud("dB", font_size=19, color=C_TENUE)
        u_b.move_to([MX1 + 0.55, MY_T + 0.3, 0])

        self.play(Create(marco), FadeIn(t_dop), FadeIn(u_k), FadeIn(t_ch),
                  FadeIn(u_c), run_time=0.8)
        self.play(FadeIn(barra), FadeIn(t_bar), FadeIn(u_b), run_time=0.5)
        rot.mostrar(dato_pie("pasos de 500 Hz"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        # --- el barrido: una fila por Doppler probado --------------------------
        cursor = Rectangle(width=W + 0.08, height=h_f + 0.04,
                           stroke_color=C_LO, stroke_width=3.0)
        cursor.move_to([(MX0 + MX1) / 2, y_fila(0), 0])

        def lectura(i):
            t = tag_hud(f"NCO {DOPS[i] / 1e3:+.1f} kHz", font_size=20,
                        color=C_LO)
            t.move_to([MX1 - 1.1, MY_T + 0.3, 0])
            return t

        lect = lectura(0)
        self.play(Create(cursor), FadeIn(lect), run_time=0.5)
        rot.mostrar(dato_pie("10 ms sumados"), zona="abajo", run_time=0.5)
        filas = Group()
        for i in range(n_f):
            fila = imagen(mapa_db[i][None, :], W, h_f * 1.12)
            fila.move_to([(MX0 + MX1) / 2, y_fila(i), 0])
            filas.add(fila)
            lect.become(lectura(i))
            self.play(FadeIn(fila), cursor.animate.move_to(
                [(MX0 + MX1) / 2, y_fila(i), 0]), run_time=0.55)
            self.add(cursor)
        self.wait(0.8)
        self.play(FadeOut(cursor), FadeOut(lect), run_time=0.5)
        self.add(marco)

        # --- lo que costo -----------------------------------------------------
        rot.mostrar(cifra_pie(f"{n_f} x {n_j} = {REJ.size} celdas"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)
        d_red = tag_dato(f"dibujo: max de {GRUPO} muestras", font_size=19)
        d_red.move_to([0, MY_T + 0.3, 0]).align_to(marco, RIGHT)
        self.play(FadeIn(d_red), run_time=0.4)
        self.wait(1.2)
        rot.mostrar(dato_pie("fase: 2 muestras por chip"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"{n_f} x {n_j} = {REJ.size} celdas"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
