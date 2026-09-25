class Clip1(Scene):
    """7.3.1 - La captura GPS: 200 muestras que son ruido a la vista, con la
    senal (la misma captura sin ruido) a la MISMA escala, casi una raya; y
    el espectro de 1 ms, plano, con la senal 20 dB por debajo. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La senal no se ve"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        FS_GPS = 2.046e6
        N_T = 200
        # la misma captura sin ruido (la libreria, con SNR enorme)
        limpia = S.gps_captura(prn=PRN, snr_db=300.0)
        xr = X[:N_T].real
        sr = limpia[:N_T].real
        amp = float(np.abs(xr).max()) * 1.05

        # --- panel de tiempo -------------------------------------------------
        ANCHO, ALTO = 11.2, 2.3
        c_t = UP * 1.5 + RIGHT * 0.5

        def pt(k, v):
            return c_t + np.array([(k / (N_T - 1) - 0.5) * ANCHO,
                                   v / amp * ALTO / 2, 0.0])

        cero = Line(pt(0, 0), pt(N_T - 1, 0), color=C_EJE, stroke_width=1.6)
        traza = VMobject(stroke_color=C_RUIDO, stroke_width=2.0)
        traza.set_points_as_corners([pt(k, v) for k, v in enumerate(xr)])
        senal = VMobject(stroke_color=C_SENAL, stroke_width=3.2)
        senal.set_points_as_corners([pt(k, v) for k, v in enumerate(sr)])
        t_cap = tag_junto(cero, "captura", LEFT, buff=0.2, font_size=20,
                          color=C_RUIDO).shift(UP * 0.28)
        t_sen = tag_junto(cero, "senal", LEFT, buff=0.2, font_size=20,
                          color=C_SENAL).shift(DOWN * 0.28)
        t_sen.align_to(t_cap, RIGHT)
        t_n = tag_hud(f"{N_T} muestras", font_size=19, color=C_TENUE)
        t_n.move_to(pt(N_T - 1, amp) + UP * 0.25).align_to(cero, RIGHT)

        self.play(Create(cero), FadeIn(t_cap), run_time=0.6)
        self.play(Create(traza), run_time=2.6, rate_func=linear)
        self.play(FadeIn(t_n), run_time=0.4)
        self.wait(1.2)
        rot.mostrar(dato_pie("SNR -20 dB por muestra"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        # la senal, a la misma escala
        self.play(traza.animate.set_stroke(opacity=0.3), run_time=0.6)
        self.play(Create(senal), FadeIn(t_sen), run_time=1.6)
        # cuanto mas alto es el ruido que la senal, medido en esta ventana
        p_s = float(np.mean(np.abs(limpia[:N_T]) ** 2))
        p_r = float(np.mean(np.abs(X[:N_T] - limpia[:N_T]) ** 2))
        veces = math.sqrt(p_r / p_s)
        rot.mostrar(cifra_pie(f"ruido: x{fmt(veces, 1)} en amplitud"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)
        self.play(traza.animate.set_stroke(opacity=1.0), run_time=0.6)
        rot.limpiar(zona="abajo", run_time=0.3)
        self.wait(0.8)

        # --- espectro de 1 ms -----------------------------------------------
        PISO = -45.0
        c_e = DOWN * 1.0 + RIGHT * 0.5
        f, db = S.espectro_db(X[:2046], FS_GPS, nfft=2046)
        _, d_abs = S.espectro_db(X[:2046], FS_GPS, nfft=2046, ref="abs")
        ref = float(d_abs.max())
        _, d_sen = S.espectro_db(limpia[:2046], FS_GPS, nfft=2046,
                                 ref=ref)
        fd, dbd = S.para_dibujar(f, db, puntos=520)
        fs_, dbs = S.para_dibujar(f, d_sen, puntos=520)
        esp = S.Espectro(fd, dbd, piso=PISO, techo=0.0, ancho=ANCHO,
                         alto=2.3, color=C_RUIDO, grosor=2.0)
        esp.shift(c_e)
        esp_s = S.Espectro(fs_, dbs, piso=PISO, techo=0.0, ancho=ANCHO,
                           alto=2.3, color=C_SENAL, grosor=2.6)
        esp_s.shift(c_e)
        ticks = esp.marcas([-1e6, -0.5e6, 0.0, 0.5e6, 1e6],
                           ["-1", "-0.5", "0", "+0.5", "+1"])
        u = tag_junto(ticks[-1], "MHz", RIGHT, buff=0.2, font_size=20)
        t_esp = tag_junto(esp.ejes, "espectro", LEFT, buff=0.2,
                          font_size=20, color=C_RUIDO)
        t_esp.move_to(esp.en(fd[0], PISO * 0.35)).align_to(t_cap, RIGHT)

        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), FadeIn(t_esp),
                  run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        rot.mostrar(dato_pie("1 ms: 1023 chips"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # la senal en el espectro, con la MISMA referencia
        self.play(esp.curva.animate.set_stroke(opacity=0.45), run_time=0.5)
        self.play(Create(esp_s.curva), FadeIn(esp_s.area), run_time=1.8)
        m_r = float(np.mean(10 ** (db / 10)))
        m_s = float(np.mean(10 ** (d_sen / 10)))
        bajo = 10 * math.log10(m_r / m_s)
        rot.mostrar(cifra_pie(f"senal {fmt(bajo, 1)} dB por debajo"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)
        rot.mostrar(dato_pie("portadora 1575.42 MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)
