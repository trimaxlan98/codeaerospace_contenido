class Clip4(Scene):
    """4.1.4 - El deenfasis: el ruido a la salida del discriminador sube
    con la frecuencia (triangulo, rojo); un filtro de un polo (75 us) lo
    dobla en los agudos y baja el ruido de audio 12.2 dB (verde). Cierre
    de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El deenfasis"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- ruido a la salida del discriminador, sin y con deenfasis ------
        n = 1 << 16
        x = np.ones(n, complex) + S.ruido_complejo(n, 10 ** (-15.0 / 10), 5)
        d = S.discriminador(x, FS)
        e = S.deenfasis(d, FS)
        f1, p1 = S.espectro_db(d, FS, nfft=4096, ref="abs")
        f2, p2 = S.espectro_db(e, FS, nfft=4096, ref="abs")
        fr, dbr1 = S.para_dibujar(f1, p1, puntos=400, f_lo=0.0, f_hi=15e3)
        _, dbr2 = S.para_dibujar(f2, p2, puntos=400, f_lo=0.0, f_hi=15e3)

        esp = S.Espectro(fr, dbr1, piso=-25.0, techo=35.0, ancho=10.8,
                         alto=3.9, color=C_RUIDO)
        esp.move_to(DOWN * 0.1)
        ticks = esp.marcas([0.0, 5e3, 10e3, 15e3], ["0", "5", "10", "15"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)

        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.4)
        self.wait(2.2)

        rot.mostrar(dato_pie("deenfasis 75 microsegundos"), zona="abajo",
                    run_time=0.5)
        self.wait(3.5)

        # --- el filtro de deenfasis baja el ruido en los agudos ------------
        esp2 = esp.con_db(dbr2, color=C_OK)
        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area), run_time=2.2)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"-{fmt(MEJORA_DE, 1)} dB de ruido"),
                    zona="abajo", run_time=0.5)
        self.wait(5.5)

        cierre_leccion(self, rot, "La FM se oye en el angulo.",
                       "Una resta de fases basta.", esp, ticks, u,
                       espera=6.5)
