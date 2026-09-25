class Clip3(Scene):
    """4.1.3 - Carson: el espectro de una FM de tono de 15 kHz cabe casi
    exacto en la banda de Carson, 2*(desviacion + fm); el ancho medido al
    98% de la potencia coincide con la regla. El estereo (subcanal a
    53 kHz) pide mas ancho: 256 kHz. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Carson"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        f, db = S.espectro_db(X15, FS, nfft=8192)
        fr, dbr = S.para_dibujar(f, db, puntos=900, f_lo=-114e3, f_hi=114e3)
        esp = S.Espectro(fr, dbr, piso=-80.0, techo=3.0, ancho=11.2,
                         alto=3.9, color=C_SENAL)
        esp.move_to(DOWN * 0.15)
        ticks = esp.marcas([-100e3, -50e3, 0.0, 50e3, 100e3],
                           ["-100", "-50", "0", "50", "100"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)

        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.4)
        self.wait(1.8)

        rot.mostrar(dato_pie(f"desviacion {fmt(DESV / 1e3, 0)} kHz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.5)

        # --- la banda de Carson: 2 x (desviacion + fm) ---------------------
        banda = esp.banda(-CARSON_MONO / 2, CARSON_MONO / 2,
                          color=C_CALCULO, opacidad=0.14)
        self.play(FadeIn(banda), run_time=1.2)
        self.wait(0.8)
        rot.mostrar(cifra_pie(f"Carson: {fmt(CARSON_MONO / 1e3, 0)} kHz"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        # --- el ancho medido (98% de la potencia) coincide -----------------
        marca_lo = esp.marca_f(-OCUPADO / 2, color=C_CALCULO, ancho=2.2)
        marca_hi = esp.marca_f(OCUPADO / 2, color=C_CALCULO, ancho=2.2)
        self.play(Create(marca_lo), Create(marca_hi), run_time=0.9)
        self.wait(0.7)
        rot.mostrar(cifra_pie(f"medido: {fmt(OCUPADO / 1e3, 1)} kHz"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- el estereo pide mas ancho del que cabe en este cuadro ---------
        rot.mostrar(cifra_pie(f"estereo: {fmt(CARSON_EST / 1e3, 0)} kHz"),
                    zona="abajo", run_time=0.5)
        self.wait(6.5)
