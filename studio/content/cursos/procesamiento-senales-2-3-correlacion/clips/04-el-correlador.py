class Clip4(Scene):
    """2.3.4 - El correlador barre el registro entero con el codigo de 127
    chips y clava el retardo real, con la senal 6 dB por debajo del ruido.
    Cierre de la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("El correlador"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        N_RX = len(RX_PN)
        PASO = 0.0165                       # misma rejilla en los carriles

        # --- el codigo, de cerca ------------------------------------------
        o_big = Onda(np.arange(len(PN)), PN, (-1.35, 1.35), ancho=9.8,
                     alto=1.20, color=C_MUESTRA, grosor=2.0)
        o_big.move_to(UP * 1.45)
        et_big = tag_junto(o_big, "codigo PN", UP, buff=0.12, font_size=19,
                           color=C_MUESTRA)
        self.play(FadeIn(o_big.ejes), FadeIn(et_big), run_time=0.5)
        self.play(Create(o_big.curva), run_time=1.9)
        rot.mostrar(cifra_pie(f"{len(PN)} chips"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)
        self.play(FadeOut(o_big), FadeOut(et_big), run_time=0.6)

        # --- el registro que llega ----------------------------------------
        o_rx = Onda(np.arange(N_RX), RX_PN, (-6.6, 6.6),
                    ancho=PASO * (N_RX - 1), alto=1.70, color=C_SENAL,
                    grosor=1.6)
        o_rx.move_to(UP * 1.75)
        x0 = o_rx.en(0.0, 0.0)[0]
        et_rx = tag_junto(o_rx, "registro", LEFT, buff=0.16, font_size=19,
                          color=C_SENAL)
        self.play(FadeIn(o_rx.ejes), FadeIn(et_rx), run_time=0.5)
        self.play(Create(o_rx.curva), run_time=2.5)
        rot.mostrar(cifra_pie(f"SNR = {fmt(SNR_PN, 1)} dB", color=C_RUIDO),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- la plantilla que va a barrer ---------------------------------
        o_pl = Onda(np.arange(len(PN)), PN, (-1.35, 1.35),
                    ancho=PASO * (len(PN) - 1), alto=0.75,
                    color=C_MUESTRA, grosor=1.8)
        o_pl.move_to(UP * 0.05)
        o_pl.shift(RIGHT * (o_rx.en(float(LAGS_PN[0]), 0.0)[0]
                            - o_pl.en(0.0, 0.0)[0]))
        et_pl = tag_junto(o_pl, "plantilla", UP, buff=0.10, font_size=18,
                          color=C_MUESTRA)
        barre = VGroup(o_pl, et_pl)

        # --- el carril donde se va escribiendo la correlacion -------------
        o_rc = Onda(LAGS_PN, R_PN_RX, (-140.0, 140.0),
                    ancho=PASO * (len(LAGS_PN) - 1), alto=1.90,
                    color=C_CALCULO, grosor=1.7)
        o_rc.move_to(DOWN * 1.85)
        o_rc.shift(RIGHT * (x0 - o_rc.en(0.0, 0.0)[0]))
        et_rc = tag_junto(o_rc, "correlacion", UP, buff=0.10,
                          font_size=19, color=C_CALCULO)

        self.play(FadeIn(barre), run_time=0.6)
        self.play(FadeIn(o_rc.ejes), FadeIn(et_rc), run_time=0.5)
        self.wait(0.5)

        # el barrido: la plantilla avanza retardo a retardo y detras se
        # dibuja el valor que va saliendo (los dos, lineales y a la par)
        recorrido = (o_rx.en(float(LAGS_PN[-1]), 0.0)[0]
                     - o_rx.en(float(LAGS_PN[0]), 0.0)[0])
        self.play(barre.animate.shift(RIGHT * recorrido),
                  Create(o_rc.curva), run_time=7.0, rate_func=linear)
        self.wait(0.8)

        # --- el pico: donde estaba -----------------------------------------
        marca = o_rc.vertical_en(float(RETARDO_PN), color=C_CALCULO)
        et_k = tag_hud(f"k = {RETARDO_PN}", font_size=20)
        et_k.next_to(o_rc.en(float(RETARDO_PN), float(R_PN_RX.max())),
                     RIGHT, buff=0.10)
        xa = o_rx.en(float(OFFSET_PN), 0.0)[0]
        xb = o_rx.en(float(OFFSET_PN + len(PN)), 0.0)[0]
        ventana = Rectangle(width=abs(xb - xa), height=1.70,
                            stroke_width=1.4, stroke_color=C_CALCULO,
                            fill_color=C_CALCULO, fill_opacity=0.16)
        ventana.move_to(np.array([(xa + xb) / 2.0, 1.75, 0.0]))
        self.play(Create(marca), FadeIn(et_k), run_time=0.8)
        self.play(FadeIn(ventana), run_time=0.8)
        rot.mostrar(cifra_pie(f"retardo = {RETARDO_PN} muestras"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # el panel sube: a esta altura el carril del registro llega hasta
        # y = 2.6 y la columna de cifras se le echaria encima
        panel = panel_cifras((f"ganancia = {fmt(GANANCIA_PN, 1)} dB",
                              C_CALCULO),
                             (f"hallado = {RETARDO_PN}", C_CALCULO),
                             desplazar=UP * 0.40)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"hallado {RETARDO_PN} = real {OFFSET_PN}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        cierre_leccion(self, rot, "El ruido no se parece a nada.",
                       "Por eso la señal aparece.",
                       o_rx, et_rx, barre, o_rc, et_rc, marca, et_k,
                       ventana, panel)
