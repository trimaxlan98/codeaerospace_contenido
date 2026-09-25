class Clip1(Scene):
    """6.2.1 - La fase de X_GMSK (np.unwrap(np.angle)) sobre 16 bits del
    cuerpo de la trama: sube y baja suave, +-90 grados por bit (h=0.5).
    Debajo, la frecuencia instantanea (derivada de la fase, suavizada por
    el filtro gaussiano BT=0.4) contra los niveles NRZ sin filtrar, en
    gris, como referencia: la GMSK es el NRZ pasado por el filtro. Un
    marcador recorre las dos curvas a la vez. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("GMSK a 9600"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        sps = 8
        i0, n_bits = 100, 16
        seg = X_GMSK[i0 * sps:(i0 + n_bits) * sps]
        fase = np.unwrap(np.angle(seg))
        fase_deg = np.degrees(fase - fase[0])
        idx = np.arange(len(seg)) / sps

        # --- panel de la fase (ambar): sube y baja suave -------------------
        panel_fase = S.Espectro(idx, fase_deg,
                                piso=float(fase_deg.min()) - 15.0,
                                techo=float(fase_deg.max()) + 15.0,
                                ancho=10.6, alto=1.9, color=C_SENAL,
                                area=False, grosor=3.0)
        panel_fase.move_to(UP * 1.25)
        et_fase = tag_junto(panel_fase, "fase", UP, buff=0.18,
                            font_size=22, color=C_SENAL)

        self.play(Create(panel_fase.ejes), run_time=0.5)
        self.play(FadeIn(et_fase), run_time=0.4)
        self.play(Create(panel_fase.curva), run_time=2.6)
        self.wait(1.3)

        # --- panel de la frecuencia (ambar) contra el NRZ crudo (gris) -----
        freq = np.gradient(fase_deg)
        nrz = np.repeat(2 * NIVELES[i0:i0 + n_bits] - 1, sps).astype(float)
        pico = float(max(np.max(np.abs(freq)), np.max(np.abs(nrz))))
        nrz_esc = nrz * pico
        techo_f = pico * 1.2

        panel_ref = S.Espectro(idx, nrz_esc, piso=-techo_f, techo=techo_f,
                               ancho=10.6, alto=2.15, color=C_DATO,
                               area=False, grosor=2.2)
        panel_ref.move_to(DOWN * 1.55)
        panel_freq = panel_ref.con_db(freq, color=C_SENAL)
        panel_freq.curva.set_stroke(width=3.0)
        et_freq = tag_junto(panel_ref, "frecuencia", UP, buff=0.18,
                            font_size=22, color=C_SENAL)

        self.play(Create(panel_ref.ejes), run_time=0.5)
        self.play(FadeIn(et_freq), run_time=0.4)
        self.play(Create(panel_ref.curva), run_time=1.8)
        self.wait(0.8)
        self.play(Create(panel_freq.curva), run_time=2.0)
        self.wait(1.5)

        # --- un marcador recorre las dos curvas a la vez -------------------
        marcador = ValueTracker(0.0)

        def _k():
            return min(int(marcador.get_value() * (len(idx) - 1)),
                       len(idx) - 1)

        linea1 = always_redraw(lambda: panel_fase.marca_f(idx[_k()],
                                                           color=C_TENUE))
        punto1 = always_redraw(lambda: Dot(
            panel_fase.en(idx[_k()], fase_deg[_k()]), radius=0.055,
            color=C_SENAL))
        linea2 = always_redraw(lambda: panel_ref.marca_f(idx[_k()],
                                                          color=C_TENUE))
        punto2 = always_redraw(lambda: Dot(
            panel_ref.en(idx[_k()], freq[_k()]), radius=0.055,
            color=C_SENAL))
        self.add(linea1, punto1, linea2, punto2)
        self.play(marcador.animate.set_value(1.0), run_time=5.0,
                  rate_func=linear)
        self.wait(1.2)
        self.remove(linea1, punto1, linea2, punto2)

        rot.mostrar(dato_pie("filtro gaussiano BT 0.4"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)
        rot.mostrar(dato_pie("canal 161.975 MHz"), zona="abajo",
                    run_time=0.5)
        self.wait(5.8)
