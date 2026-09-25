class Clip1(Scene):
    """3.2.1 - El filtro de canal: la emisora mas fuerte de la captura
    (-700 kHz) se centra en 0 con el NCO de la leccion 3.1; la respuesta del
    FIR de 219 coeficientes (fucsia) se superpone al espectro y lo que cae
    fuera de la banda de paso se apaga al filtrar de verdad. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El filtro de canal"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- centrar la emisora mas fuerte (-700 kHz) en 0 con el NCO -------
        x = CAP * S.nco(-700e3, FS, len(CAP))

        # --- el espectro de la captura, banda base (kHz, 0 marcado) --------
        nfft = 2048
        f, db_crudo = S.espectro_db(x, FS, nfft=nfft)
        filtrada = S.diezmar(x, 1, H)
        _, db_filtrado = S.espectro_db(filtrada, FS, nfft=nfft)
        f_lo, f_hi = -1.2e6, 1.2e6
        fr, dbr_crudo = S.para_dibujar(f, db_crudo, 900, f_lo, f_hi)
        _, dbr_filtrado = S.para_dibujar(f, db_filtrado, 900, f_lo, f_hi)

        esp = S.Espectro(fr, dbr_crudo, piso=-70.0, techo=6.0, ancho=11.6,
                         alto=4.2, color=C_SENAL)
        esp.move_to(UP * 0.2)
        ticks = esp.marcas([-1.2e6, -0.6e6, 0.0, 0.6e6, 1.2e6],
                           ["-1200", "-600", "0", "600", "1200"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.9)
        self.wait(0.2)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        self.wait(2.0)

        # --- la respuesta del FIR, fucsia, sobre el mismo eje de dB --------
        dbh_en_fr = np.interp(fr, *S.respuesta_db(H, FS, n=16384))
        filtro = esp.con_db(dbh_en_fr, color=C_LO)
        etiqueta_filtro = tag_junto(filtro.curva, "filtro", UP, buff=0.18,
                                    font_size=20, color=C_LO)
        etiqueta_filtro.move_to(esp.en(0.0, 5.4))
        self.play(Create(filtro.curva), FadeIn(etiqueta_filtro),
                  run_time=1.6)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"{N_TAPS} coeficientes"), zona="abajo",
                    run_time=0.5)
        self.wait(4.5)
        rot.mostrar(cifra_pie(f"{fmt(ATEN, 1)} dB de rechazo"), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- filtrar de verdad: lo que queda fuera se apaga -----------------
        esp2 = esp.con_db(dbr_filtrado, color=C_SENAL)
        self.play(Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area), run_time=2.6)
        self.wait(9.0)
