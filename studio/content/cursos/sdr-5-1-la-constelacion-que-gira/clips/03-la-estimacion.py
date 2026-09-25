class Clip3(Scene):
    """5.1.3 - La estimacion: se ubica la raya de RX**4 y se divide entre
    4 (S.estimar_desfase_x4 hace exactamente esa cuenta, con interpolacion
    parabolica). En cian: los grados por simbolo medidos (GRADOS_EST, 3
    decimales) y el error frente al parametro elegido, en ppm de la tasa
    de simbolo (1 decimal). Misma ventana de espectro que 5.1.2 (nfft=
    len(RX), no 8192: ver la nota de libreria en ese clip). (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La estimacion"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        f, db = S.espectro_db(RX ** 4, 1.0, nfft=len(RX))
        fr, dbr = S.para_dibujar(f, db, puntos=900, f_lo=-0.05, f_hi=0.05)
        esp = S.Espectro(fr, dbr, piso=-40.0, techo=3.0, ancho=11.0,
                         alto=3.8, color=C_SENAL)
        ticks = esp.marcas([-0.05, 0.0, 0.05], ["-0.05", "0", "0.05"])
        u = tag_junto(ticks[-1], "ciclos/simb", RIGHT, buff=0.2,
                     font_size=18)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.9)
        self.wait(0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        self.wait(1.6)

        pico4 = 4.0 * DF_EST
        marca = esp.marca_f(pico4, color=C_CALCULO)
        self.play(Create(marca), run_time=0.7)
        self.wait(1.6)

        # --- la raya medida, dividida entre 4 -------------------------------
        rot.mostrar(formula_pie(r"\Delta f_{est} = \frac{f_{pico}}{4}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"{fmt(GRADOS_EST, 3)} grados/simbolo"),
                    zona="abajo", run_time=0.5)
        self.wait(6.0)

        error_ppm = abs(DF_EST - DF_RS) * 1e6
        rot.mostrar(cifra_pie(f"error {fmt(error_ppm, 1)} ppm"),
                    zona="abajo", run_time=0.5)
        self.wait(10.0)
