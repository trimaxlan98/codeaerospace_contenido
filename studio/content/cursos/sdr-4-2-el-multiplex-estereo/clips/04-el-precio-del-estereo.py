class Clip4(Scene):
    """4.2.4 - El precio del estereo: el triangulo de ruido tras el
    discriminador (portadora sin modular + ruido a 20 dB de CNR) crece con
    la frecuencia; la banda de L-R vive donde el ruido es mayor que en la
    banda mono: +15.4 dB (S.precio_estereo). Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El precio del estereo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el ruido tras el discriminador, portadora + ruido a 20 dB CNR --
        n = 1 << 16
        x = np.ones(n, complex) + S.ruido_complejo(n, 10 ** (-20.0 / 10.0),
                                                    semilla=6)
        d = S.discriminador(x, FS)
        f, p = S.espectro_db(d, FS, nfft=4096, ref="abs")
        fr, pr = S.para_dibujar(f, p, puntos=900, f_lo=0.0)
        m = fr <= 60000.0
        fr, pr = fr[m], pr[m]

        esp = S.Espectro(fr, pr, piso=-30.0, techo=45.0, ancho=12.2,
                         alto=3.8, color=C_RUIDO)
        esp.move_to(DOWN * 0.1)
        ticks = esp.marcas([0.0, 10e3, 20e3, 30e3, 40e3, 50e3, 60e3],
                           ["0", "10", "20", "30", "40", "50", "60"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.4)
        self.wait(1.4)

        # --- las dos bandas: mono (gris) y L-R (rojo, donde el ruido pesa) --
        b_mono = esp.banda(0.0, 15e3, color=C_DATO, opacidad=0.14)
        et_mono = tag_dato("mono")
        et_mono.move_to(esp.en(7.5e3, 10.0))
        self.play(FadeIn(b_mono), FadeIn(et_mono), run_time=0.7)
        self.wait(1.8)

        b_dif = esp.banda(23e3, 53e3, color=C_RUIDO, opacidad=0.16)
        et_dif = tag_dato("L-R")
        et_dif.move_to(esp.en(38e3, 41.0))
        self.play(FadeIn(b_dif), FadeIn(et_dif), run_time=0.7)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"+{fmt(PRECIO, 1)} dB de ruido"),
                    zona="abajo", run_time=0.5)
        self.wait(11.0)

        cierre_leccion(self, rot, "El estereo viaja escondido,",
                       "colgado de un piloto.", esp.ejes, ticks, u,
                       esp.curva, esp.area, b_mono, et_mono, b_dif, et_dif)
