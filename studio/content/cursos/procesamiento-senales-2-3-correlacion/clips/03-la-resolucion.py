class Clip3(Scene):
    """2.3.3 - Mismo largo de pulso, distinta banda: el chirp comprime su
    eco a 2 us y el pulso llano se queda en 42.5 us, y ademas se equivoca de
    sitio por dos muestras. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("La resolucion"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        NIVEL = 10.0 ** (-3.0 / 20.0)        # el umbral de -3 dB medido
        US = 1e6 / FS_RADAR                  # microsegundos por muestra
        DES_P = (RETARDO_P - OFFSET) * US    # donde cae el pico del pulso

        def ventana(w):
            """Las dos correlaciones normalizadas, en us alrededor del eco
            real, dentro de +-w muestras."""
            m = (LAGS >= OFFSET - w) & (LAGS <= OFFSET + w)
            mp = (LAGS_P >= OFFSET - w) & (LAGS_P <= OFFSET + w)
            return ((LAGS[m] - OFFSET) * US, R_CORR[m] / R_CORR.max(),
                    (LAGS_P[mp] - OFFSET) * US, R_PULSO[mp] / R_PULSO.max())

        # --- vista ancha: la ventana mide justo el pulso emitido ---------
        us_c, rc, us_p, rp = ventana(int(round(LARGO_US / US / 2)))
        caja = Onda(us_p, rp, (-0.74, 1.18), ancho=10.6, alto=2.60,
                    color=C_MUESTRA, grosor=2.4)
        caja.move_to(DOWN * 0.42)
        curva_ch = caja.curva_de(us_c, rc, color=C_CALCULO, grosor=2.6)
        et_p = tag_junto(caja, "pulso llano", UP, buff=0.12, font_size=19,
                         color=C_MUESTRA)

        self.play(FadeIn(caja.ejes), FadeIn(et_p), run_time=0.5)
        self.play(Create(caja.curva), run_time=2.2)
        self.wait(0.9)

        nivel = caja.horizontal_en(NIVEL, color=C_DATO)
        anchura_p = Line(caja.en(DES_P - ANCHO_P_US / 2, NIVEL),
                         caja.en(DES_P + ANCHO_P_US / 2, NIVEL),
                         color=C_MUESTRA, stroke_width=5.0)
        et_ap = tag_hud(f"{fmt(ANCHO_P_US, 1)} us", font_size=20,
                        color=C_MUESTRA)
        et_ap.next_to(anchura_p, UP, buff=0.30).shift(LEFT * 1.95)
        self.play(Create(nivel), run_time=0.7)
        self.play(Create(anchura_p), FadeIn(et_ap), run_time=1.0)
        rot.mostrar(cifra_pie(f"pulso: ancho {fmt(ANCHO_P_US, 1)} us",
                              color=C_MUESTRA), zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el chirp, en la misma caja -----------------------------------
        et_c = tag_junto(caja, "chirp", DOWN, buff=0.14, font_size=19,
                         color=C_CALCULO)
        self.play(Create(curva_ch), FadeIn(et_c), run_time=1.8)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"chirp: ancho {fmt(ANCHO_US, 1)} us"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        panel = panel_cifras((f"chirp {fmt(COMPRESION, 0)}x", C_CALCULO),
                             (f"pulso {fmt(COMPRESION_P, 1)}x", C_MUESTRA),
                             (f"emitido {fmt(LARGO_US, 0)} us", C_TENUE))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(3.0)

        # --- el mismo pico, de cerca --------------------------------------
        self.play(FadeOut(caja), FadeOut(curva_ch), FadeOut(nivel),
                  FadeOut(anchura_p), FadeOut(et_ap), FadeOut(et_p),
                  FadeOut(et_c), FadeOut(panel), run_time=0.8)

        us_c2, rc2, us_p2, rp2 = ventana(12)
        caja2 = Onda(us_p2, rp2, (-0.74, 1.18), ancho=10.6, alto=2.60,
                     color=C_MUESTRA, grosor=2.4)
        caja2.move_to(DOWN * 0.42)
        curva_ch2 = caja2.curva_de(us_c2, rc2, color=C_CALCULO, grosor=2.8)
        self.play(FadeIn(caja2.ejes), run_time=0.4)
        self.play(Create(caja2.curva), Create(curva_ch2), run_time=1.8)
        self.wait(1.0)

        nivel2 = caja2.horizontal_en(NIVEL, color=C_DATO)
        anchura_c = Line(caja2.en(-ANCHO_US / 2, NIVEL),
                         caja2.en(ANCHO_US / 2, NIVEL), color=C_CALCULO,
                         stroke_width=5.0)
        et_ac = tag_hud(f"{fmt(ANCHO_US, 1)} us", font_size=20)
        et_ac.next_to(anchura_c, DOWN, buff=0.12)
        self.play(Create(nivel2), run_time=0.6)
        self.play(Create(anchura_c), FadeIn(et_ac), run_time=1.0)
        self.wait(1.8)

        v_real = caja2.vertical_en(0.0, color=C_CALCULO)
        v_pulso = caja2.vertical_en(DES_P, color=C_MUESTRA)
        self.play(Create(v_real), run_time=0.6)
        self.play(Create(v_pulso), run_time=0.6)
        rot.mostrar(cifra_pie(f"chirp {RETARDO}   pulso {RETARDO_P}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        panel2 = panel_cifras((f"chirp k = {RETARDO}", C_CALCULO),
                              (f"pulso k = {RETARDO_P}", C_MUESTRA),
                              (f"real = {OFFSET}", C_TENUE))
        self.play(FadeIn(panel2), run_time=0.6)
        self.wait(2.8)

        rot.mostrar(formula_pie(r"\frac{1}{B} = " + fmt(INV_B_US, 1) +
                                r"\ \mu s", color=C_DATO), zona="abajo",
                    run_time=0.5)
        self.wait(3.8)
