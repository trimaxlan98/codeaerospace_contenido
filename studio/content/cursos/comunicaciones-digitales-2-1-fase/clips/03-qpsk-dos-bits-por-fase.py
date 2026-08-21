class Clip3(Scene):
    """2.1.3 - QPSK: cuatro fases a 90 grados, mapa de Gray rotulado desde
    la libreria (00/01/11/10); la onda salta entre cuatro formas; doble
    de bits en el mismo ritmo de simbolos. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("QPSK: dos bits por fase")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: ahora van dos bits por simbolo ------------------------
        rot.mostrar(pie_curso("Si la fase tiene CUATRO posiciones, cada "
                              "simbolo puede llevar dos bits."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(BITS_QPSK_FLAT, lado=0.4)
        tren.move_to(LEFT * 3.3 + DOWN * 1.95)
        self.play(LaggedStart(*[FadeIn(c) for c in tren.celdas],
                              lag_ratio=0.1),
                  FadeIn(tren.digitos), run_time=1.0)
        self.wait(2.4)

        # --- momento: el mapa de Gray, rotulado desde la libreria ------------
        rot.mostrar(pie_curso("Cuatro fases, el mapa de Gray: vecinos que "
                              "difieren en un solo bit."),
                    zona="abajo", run_time=0.5)
        on = onda(T_QPSK, Y_QPSK, rango_y=(-1.15, 1.15), ancho=6.2, alto=2.3)
        on.move_to(LEFT * 3.3 + UP * 0.65)
        piq = plano_iq(unidad=1.0, alcance=1.6)
        piq.move_to(RIGHT * 3.5 + DOWN * 0.25)
        puntos_qpsk = piq.puntos(PUNTOS_QPSK, bits=BITS_TABLA_QPSK,
                                 color=C_BIT)
        self.play(FadeIn(on.ejes), FadeIn(piq), FadeIn(puntos_qpsk),
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: la onda salta entre cuatro formas -----------------------
        rot.mostrar(pie_curso("La onda salta entre cuatro formas: una por "
                              "cada par de bits."),
                    zona="abajo", run_time=0.5)
        i0 = _indice_par(PARES_QPSK[0])
        marcador = Dot(piq.p(PUNTOS_QPSK[i0]), radius=0.11, color=C_CIFRA)
        tren.marcar(0, color=C_CIFRA)
        tren.marcar(1, color=C_CIFRA)
        seg0 = on.curva_de(*SEG_QPSK[0], color=C_SENAL)
        self.play(Create(seg0), FadeIn(marcador, scale=0.4), run_time=0.7)
        self.wait(1.8)

        for k in range(1, len(PARES_QPSK)):
            seg = on.curva_de(*SEG_QPSK[k], color=C_SENAL)
            frontera = on.vertical_en(FRONTERAS_QPSK[k - 1], color=C_CIFRA)
            ik = _indice_par(PARES_QPSK[k])
            tren.marcar(2 * k, color=C_CIFRA)
            tren.marcar(2 * k + 1, color=C_CIFRA)
            self.play(Create(frontera), Create(seg),
                      marcador.animate.move_to(piq.p(PUNTOS_QPSK[ik])),
                      run_time=1.0)
            self.wait(1.1)

        self.wait(1.8)

        # --- momento: el doble de bits, mismo ritmo de simbolos -----------------
        rot.mostrar(pie_curso("Mismo ritmo de simbolos, el doble de "
                              "bits: el cubesat baja mas en el mismo "
                              "espectro."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"BPSK: {fmt(TASA_BITS_BPSK, 1)} bit/s", color=C_BIT),
            tag_hud(f"QPSK: {fmt(TASA_BITS_QPSK, 1)} bit/s", color=C_CIFRA))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(7.5)
