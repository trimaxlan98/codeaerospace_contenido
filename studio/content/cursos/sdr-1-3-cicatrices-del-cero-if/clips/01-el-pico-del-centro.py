class Clip1(Scene):
    """1.3.1 - El pico del centro: la fuga del LO deja una raya en 0 Hz que
    no es ninguna emisora; el bloqueador de DC la hunde bajo el piso. (~33 s)
    """

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El pico del centro"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el espectro de la captura con fuga de DC ----------------------
        xdc_tail = XDC[4096:]
        xb_tail = XB[4096:]
        f, db_antes = S.espectro_db(xdc_tail, FS, nfft=2048)
        _, db_desp = S.espectro_db(xb_tail, FS, nfft=2048)
        fr, dbr_antes = S.para_dibujar(f, db_antes, puntos=900,
                                       f_lo=-4.5e5, f_hi=4.5e5)
        _, dbr_desp = S.para_dibujar(f, db_desp, puntos=900,
                                     f_lo=-4.5e5, f_hi=4.5e5)

        esp = S.Espectro(fr, dbr_antes, piso=-85.0, techo=3.0, ancho=11.6,
                         alto=4.0, color=C_SENAL)
        esp.move_to(ORIGIN)
        ticks = esp.marcas([-4e5, -2e5, 0.0, 2e5, 4e5],
                           ["-400", "-200", "0", "200", "400"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.wait(0.3)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        self.wait(1.6)

        # --- el pico que no es una emisora ---------------------------------
        marca = esp.marca_f(0.0, color=C_RUIDO)
        etiqueta = tag_junto(marca, "fuga del LO", UP, buff=0.16,
                             font_size=20, color=C_RUIDO)
        self.play(Create(marca), FadeIn(etiqueta), run_time=0.7)
        self.wait(1.0)
        rot.mostrar(cifra_pie(f"pico DC: {fmt(DC_ANTES, 1)} dBc"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- el bloqueador de DC lo hunde ------------------------------------
        esp2 = esp.con_db(dbr_desp, color=C_SENAL)
        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area),
                  FadeOut(marca), FadeOut(etiqueta), run_time=1.8)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"quitar DC: {fmt(DC_DESP, 1)} dBc"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- ya no hay pico --------------------------------------------------
        marca2 = esp.marca_f(0.0, color=C_DATO, ancho=1.4)
        etiqueta2 = tag_junto(marca2, "ya no hay pico", UP, buff=0.16,
                              font_size=20, color=C_DATO)
        self.play(Create(marca2), FadeIn(etiqueta2), run_time=0.6)
        self.wait(8.5)
