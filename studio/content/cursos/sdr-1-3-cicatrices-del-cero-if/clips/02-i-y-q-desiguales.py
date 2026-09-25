class Clip2(Scene):
    """1.3.2 - I y Q desiguales: una ganancia y una fase distintas entre
    ramas convierten el circulo del plano IQ en una elipse, y abren una
    imagen espejo al otro lado del cero en el espectro. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("I y Q desiguales"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el plano IQ: circulo -> elipse ---------------------------------
        plano = S.PlanoIQ(unidad=1.7, alcance=1.15)
        plano.move_to(LEFT * 3.75 + DOWN * 0.15)
        xl160 = XL[:160]
        # el plano se dibuja con el desbalance EXAGERADO (30 % y 15 grados)
        # para que la elipse se vea; se declara en pantalla. La cifra (IRR)
        # es la de los parametros reales EPS, PHI.
        elip = S.desbalance_iq(xl160, 0.30, 15.0) / 1.3
        exag = tag_dato("dibujo exagerado", font_size=19)
        exag.next_to(plano, DOWN, buff=0.25)
        nube_circ = plano.nube(xl160, color=C_SENAL, radio=0.045)
        nube_elip = plano.nube(elip, color=C_SENAL, radio=0.045)

        # --- el espectro: aparece la imagen ---------------------------------
        f, db_limpio = S.espectro_db(XN, FS, nfft=2048)
        _, db_desb = S.espectro_db(YD, FS, nfft=2048)
        fr, dbr_limpio = S.para_dibujar(f, db_limpio, puntos=900,
                                        f_lo=-4.5e5, f_hi=4.5e5)
        _, dbr_desb = S.para_dibujar(f, db_desb, puntos=900,
                                     f_lo=-4.5e5, f_hi=4.5e5)
        esp = S.Espectro(fr, dbr_limpio, piso=-85.0, techo=3.0, ancho=7.4,
                         alto=3.7, color=C_SENAL)
        esp.move_to(RIGHT * 2.05 + DOWN * 0.15)
        ticks = esp.marcas([-4e5, 0.0, 4e5], ["-400", "0", "400"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=18)

        self.play(Create(plano.ejes), Create(plano.unidad_circulo),
                  Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.9)
        self.wait(0.4)
        self.play(FadeIn(nube_circ), run_time=1.1)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.wait(2.6)

        rot.mostrar(dato_pie("5% y 3 grados"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- el desbalance: circulo se vuelve elipse, aparece la imagen -----
        f_img, db_img = S.pico(f, db_desb, f_lo=-2.2e5, f_hi=-1.4e5)
        marca_img = esp.marca_f(f_img, color=C_RUIDO)
        etiqueta_img = tag_junto(marca_img, "imagen", UP, buff=0.16,
                                 font_size=20, color=C_RUIDO)
        esp2 = esp.con_db(dbr_desb, color=C_SENAL)
        self.play(FadeIn(exag), Transform(nube_circ, nube_elip),
                  Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area), run_time=1.8)
        self.play(Create(marca_img), FadeIn(etiqueta_img), run_time=0.7)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"IRR = {fmt(IRR_ANTES, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(11.0)
