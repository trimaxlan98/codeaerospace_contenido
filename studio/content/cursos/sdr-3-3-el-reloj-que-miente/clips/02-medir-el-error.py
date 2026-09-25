class Clip2(Scene):
    """3.3.2 - Medir el error: una portadora de referencia conocida
    (144.39 MHz, sintonizada a +50 kHz en banda base) llega corrida por
    el error del cristal; el pico medido cae en +3898 Hz de donde
    deberia, y eso son 27.0 ppm. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Medir el error"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el espectro de la referencia corrida -------------------------
        F_OFF = 50e3
        x = S.tono(F_OFF + HZ_EST, 2.4e6, 32768) + S.ruido_complejo(
            32768, 0.01, 8)
        f, db = S.espectro_db(x, 2.4e6, nfft=32768)
        fr, dbr = S.para_dibujar(f, db, puntos=900, f_lo=40e3, f_hi=60e3)
        fp, _ = S.pico(fr, dbr, f_lo=45e3, f_hi=55e3)

        esp = S.Espectro(fr, dbr, piso=-70.0, techo=3.0, ancho=11.4,
                         alto=4.2, color=C_SENAL)
        esp.move_to(UP * 0.15)
        ticks = esp.marcas([40e3, 45e3, 50e3, 55e3, 60e3],
                           ["40", "45", "50", "55", "60"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.wait(0.3)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.0)
        self.wait(1.2)

        # --- la referencia esperada, punteada gris -------------------------
        ref = esp.marca_f(F_OFF, color=C_DATO)
        et_ref = tag_junto(ref, "esperada", UP, buff=0.16, font_size=19,
                           color=C_DATO)
        self.play(Create(ref), FadeIn(et_ref), run_time=0.6)
        self.wait(0.6)
        rot.mostrar(dato_pie("144.39 MHz de referencia"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- el pico medido, corrido ----------------------------------------
        med = esp.marca_f(fp, color=C_CALCULO)
        et_med = tag_junto(med, "medida", UP, buff=0.16, font_size=19,
                           color=C_CALCULO)
        flecha = Arrow(esp.en(F_OFF, 1.6), esp.en(fp, 1.6), color=C_CALCULO,
                       buff=0.08, stroke_width=3.4)
        self.play(Create(med), FadeIn(et_med), run_time=0.6)
        self.wait(0.4)
        self.play(GrowArrow(flecha), run_time=0.8)
        self.wait(1.2)

        rot.mostrar(cifra_pie(f"+{fmt(HZ_EST, 0)} Hz = {fmt(PPM_EST, 1)} ppm"),
                   zona="abajo", run_time=0.5)
        self.wait(15.5)
