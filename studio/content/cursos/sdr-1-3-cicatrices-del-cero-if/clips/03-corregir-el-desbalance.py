class Clip3(Scene):
    """1.3.3 - Corregir el desbalance: una correccion ciega por momentos
    (Gram-Schmidt) devuelve la elipse a circulo y hunde la imagen bajo el
    piso de ruido; el IRR pasa de 28.9 a mas de 80 dB. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Corregir el desbalance"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el plano IQ: elipse (ya desbalanceada) -------------------------
        plano = S.PlanoIQ(unidad=1.7, alcance=1.15)
        plano.move_to(LEFT * 3.75 + DOWN * 0.15)
        xl160 = XL[:160]
        # el plano se dibuja con el desbalance EXAGERADO (30 % y 15 grados)
        # para que la elipse se vea; se declara en pantalla. La cifra (IRR)
        # es la de los parametros reales EPS, PHI.
        elip = S.desbalance_iq(xl160, 0.30, 15.0) / 1.3
        exag = tag_dato("dibujo exagerado", font_size=19)
        exag.next_to(plano, DOWN, buff=0.25)
        circ_corr = S.corregir_iq(elip) * 1.3   # vuelve al radio 1
        nube_elip = plano.nube(elip, color=C_SENAL, radio=0.045)
        nube_corr = plano.nube(circ_corr, color=C_OK, radio=0.045)

        # --- el espectro: imagen visible (YD) ------------------------------
        f, db_yd = S.espectro_db(YD, FS, nfft=2048)
        _, db_yc = S.espectro_db(YC, FS, nfft=2048)
        fr, dbr_yd = S.para_dibujar(f, db_yd, puntos=900, f_lo=-4.5e5,
                                    f_hi=4.5e5)
        _, dbr_yc = S.para_dibujar(f, db_yc, puntos=900, f_lo=-4.5e5,
                                   f_hi=4.5e5)
        esp = S.Espectro(fr, dbr_yd, piso=-85.0, techo=3.0, ancho=7.4,
                         alto=3.7, color=C_SENAL)
        esp.move_to(RIGHT * 2.05 + DOWN * 0.15)
        ticks = esp.marcas([-4e5, 0.0, 4e5], ["-400", "0", "400"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=18)

        f_img, _ = S.pico(f, db_yd, f_lo=-2.2e5, f_hi=-1.4e5)
        marca_img = esp.marca_f(f_img, color=C_RUIDO)
        etiqueta_img = tag_junto(marca_img, "imagen", UP, buff=0.16,
                                 font_size=20, color=C_RUIDO)

        self.play(Create(plano.ejes), Create(plano.unidad_circulo),
                  Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.9)
        self.wait(0.3)
        self.play(FadeIn(nube_elip), FadeIn(exag), run_time=1.0)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.play(Create(marca_img), FadeIn(etiqueta_img), run_time=0.6)
        self.wait(2.4)
        rot.mostrar(cifra_pie(f"IRR: {fmt(IRR_ANTES, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

        # --- la correccion ciega: elipse -> circulo, imagen bajo el piso ---
        esp2 = esp.con_db(dbr_yc, color=C_SENAL)
        marca_gris = esp.marca_f(f_img, color=C_DATO, ancho=1.4)
        self.play(Transform(nube_elip, nube_corr),
                  Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area),
                  Transform(marca_img, marca_gris),
                  FadeOut(etiqueta_img), run_time=2.0)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"mas de {IRR_SUELO} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(11.5)
