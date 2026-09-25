class Clip2(Scene):
    """3.1.2 - El NCO desliza el espectro ENTERO de la captura del 1.1
    (CAP) hasta poner la emisora mas fuerte en 0 Hz: y = CAP *
    S.nco(off, FS, len(CAP)). El desplazamiento se mide con S.pico antes
    y despues (gemela Espectro.con_db, sin copia del array). (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Mover el espectro"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        f, db = S.espectro_db(CAP, FS, nfft=2048)
        esp = S.Espectro(f, db, piso=-70.0, techo=2.0, ancho=12.2, alto=3.8,
                         color=C_SENAL)
        esp.move_to(UP * 0.05)
        ticks = esp.marcas([-1.2e6, -0.6e6, 0.0, 0.6e6, 1.2e6],
                           ["-1200", "-600", "0", "600", "1200"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.7)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.8)
        self.wait(2.2)

        # --- las cinco emisoras de la captura (medidas, no la que interesa) -
        marcas_todas = VGroup(*[esp.marca_f(o, color=C_DATO, ancho=1.4)
                                for o in OFFS])
        self.play(*[Create(m) for m in marcas_todas], run_time=1.0)
        self.wait(2.0)

        i_fuerte = int(np.argmax(NIVS))
        off = float(OFFS[i_fuerte])
        f_antes, _ = S.pico(f, db, f_lo=off - 60e3, f_hi=off + 60e3)
        marca = esp.marca_f(f_antes, color=C_SENAL, ancho=2.6)
        self.play(FadeOut(marcas_todas), Create(marca), run_time=0.8)
        self.wait(1.6)

        # --- el NCO trae esa emisora a 0 ------------------------------------
        y = CAP * S.nco(off, FS, len(CAP))
        f2, db2 = S.espectro_db(y, FS, nfft=2048)
        esp2 = esp.con_db(db2)
        f_despues, _ = S.pico(f2, db2, f_lo=-60e3, f_hi=60e3)
        marca2 = esp.marca_f(f_despues, color=C_SENAL, ancho=2.6)

        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area),
                  Transform(marca, marca2), run_time=1.8)
        self.wait(2.0)

        desplazamiento_khz = (f_antes - f_despues) / 1e3
        rot.mostrar(cifra_pie(f"{fmt(desplazamiento_khz, 0)} kHz -> 0"),
                    zona="abajo", run_time=0.5)
        self.wait(13.5)
