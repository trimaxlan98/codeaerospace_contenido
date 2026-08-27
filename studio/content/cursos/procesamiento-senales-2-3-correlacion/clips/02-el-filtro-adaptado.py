class Clip2(Scene):
    """2.3.2 - El eco de radar esta ahi, 10 dB por debajo del ruido, y en la
    traza no se ve. La correlacion con la plantilla lo saca: un pico limpio
    y el retardo exacto. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("El filtro adaptado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- misma rejilla de muestras en los tres carriles ---------------
        PASO = 0.0096
        n_rx = np.arange(N_REGISTRO)

        o_ch = Onda(np.arange(len(CHIRP)), CHIRP, (-1.25, 1.25),
                    ancho=PASO * (len(CHIRP) - 1), alto=1.10,
                    color=C_MUESTRA, grosor=2.2)
        o_ch.move_to(UP * 2.05)
        o_rx = Onda(n_rx, RX, (-7.4, 7.4), ancho=PASO * (N_REGISTRO - 1),
                    alto=1.60, color=C_SENAL, grosor=1.5)
        o_rx.move_to(UP * 0.45)
        o_rc = Onda(LAGS, R_CORR, (-140.0, 140.0),
                    ancho=PASO * (len(LAGS) - 1), alto=2.00,
                    color=C_CALCULO, grosor=1.7)
        o_rc.move_to(DOWN * 1.75)

        # los tres carriles comparten origen de muestra: n=0 en la misma x
        x0 = o_rx.en(0.0, 0.0)[0]
        o_ch.shift(RIGHT * (x0 - o_ch.en(0.0, 0.0)[0]))
        o_rc.shift(RIGHT * (x0 - o_rc.en(0.0, 0.0)[0]))

        et_ch = tag_junto(o_ch, "plantilla", UP, buff=0.10, font_size=19,
                          color=C_MUESTRA)
        et_rx = tag_junto(o_rx, "recibido", LEFT, buff=0.18, font_size=19,
                          color=C_SENAL)
        et_rc = tag_junto(o_rc, "correlacion", UP, buff=0.10,
                          font_size=19, color=C_CALCULO)

        # --- la plantilla que se emitio -----------------------------------
        self.play(FadeIn(o_ch.ejes), FadeIn(et_ch), run_time=0.5)
        self.play(Create(o_ch.curva), run_time=1.9)
        panel = panel_cifras(f"T = {fmt(LARGO_US, 0)} us",
                             f"B = {fmt(B_CHIRP / 1e3, 0)} kHz",
                             f"N = {len(CHIRP)}")
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(2.0)

        # --- el registro que llega: solo ruido, a la vista ----------------
        self.play(FadeIn(o_rx.ejes), FadeIn(et_rx), run_time=0.5)
        self.play(Create(o_rx.curva), run_time=2.6)
        rot.mostrar(cifra_pie(f"SNR entrada = {fmt(SNR_MEDIDA, 1)} dB",
                              color=C_RUIDO), zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- correlar con la plantilla ------------------------------------
        self.play(FadeIn(o_rc.ejes), FadeIn(et_rc), run_time=0.5)
        self.play(Create(o_rc.curva), run_time=3.0)
        self.wait(1.2)

        marca = o_rc.vertical_en(float(RETARDO), color=C_CALCULO)
        et_k = tag_hud(f"k = {RETARDO}", font_size=20)
        et_k.next_to(o_rc.en(float(RETARDO), float(R_CORR.max())), RIGHT,
                     buff=0.10)
        self.play(Create(marca), FadeIn(et_k), run_time=0.9)
        rot.mostrar(cifra_pie(f"retardo = {RETARDO} muestras"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- donde estaba el eco, ahora que sabemos donde mirar -----------
        xa = o_rx.en(float(OFFSET), 0.0)[0]
        xb = o_rx.en(float(OFFSET + len(CHIRP)), 0.0)[0]
        ventana = Rectangle(width=abs(xb - xa), height=1.60,
                            stroke_width=1.4, stroke_color=C_CALCULO,
                            fill_color=C_CALCULO, fill_opacity=0.16)
        ventana.move_to(np.array([(xa + xb) / 2.0, 0.45, 0.0]))
        guia = DashedLine(np.array([xa, -0.75, 0.0]),
                          np.array([xa, 1.50, 0.0]), color=C_CALCULO,
                          stroke_width=1.6, dash_length=0.08)
        self.play(VGroup(o_ch, et_ch).animate.shift(
            RIGHT * (xa - o_ch.en(0.0, 0.0)[0])), run_time=1.6)
        self.play(FadeIn(ventana), Create(guia), run_time=1.0)
        self.wait(1.8)

        panel2 = panel_cifras((f"ganancia = {fmt(GANANCIA, 1)} dB",
                               C_CALCULO),
                              (f"retardo = {RETARDO}", C_CALCULO),
                              (f"real = {OFFSET}", C_TENUE))
        self.play(FadeOut(panel), run_time=0.3)
        self.play(FadeIn(panel2), run_time=0.6)
        self.wait(2.8)

        rot.mostrar(dato_pie(f"10log10(N) = "
                             f"{fmt(10.0 * math.log10(len(CHIRP)), 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
