class Clip1(Scene):
    """1.3.1 - El DAC retiene: sale por escalones (ZOH), no por la curva
    verdadera; la caida en fs/2 es -3.92 dB. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El DAC retiene"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- momento 1: la secuencia sale retenida -------------------------
        sec = Secuencia(XK, 0, (-1.18, 1.18), ancho=10.4, alto=2.6,
                        color=C_MUESTRA)
        sec.move_to(DOWN * 0.20)
        self.play(FadeIn(sec.ejes), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in
                                range(N_MUESTRAS)], lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in
                                range(N_MUESTRAS)], lag_ratio=0.02),
                  run_time=1.6)
        self.wait(1.0)

        curva_zoh = sec.curva_de(T_DENSO, REC_ZOH, color=C_SALIDA,
                                 grosor=2.8, fs=FS)
        et_zoh = tag_junto(curva_zoh, "retencion", UP, buff=0.12,
                           font_size=19, color=C_SALIDA)
        et_zoh.move_to(sec.en(50.0, 1.02))
        self.play(Create(curva_zoh), FadeIn(et_zoh), run_time=1.6)
        self.wait(1.4)

        curva_real = sec.curva_de(T_DENSO, vibracion(T_DENSO),
                                  color=C_SENAL, grosor=2.0, fs=FS)
        # tag_hud (Space Mono): tag_junto con dos palabras deja el hueco
        # del espacio sin dibujar en Rajdhani, "senal real" -> "senalreal"
        et_real = tag_hud("senal real", font_size=19, color=C_SENAL)
        et_real.move_to(sec.en(14.0, -1.02))
        self.play(Create(curva_real), FadeIn(et_real), run_time=1.6)
        self.wait(2.6)

        self.play(FadeOut(sec), FadeOut(curva_zoh), FadeOut(curva_real),
                  FadeOut(et_zoh), FadeOut(et_real), run_time=0.8)
        self.wait(0.4)

        # --- momento 2: la respuesta en frecuencia del ZOH -----------------
        def curva_droop(f):
            return float(np.interp(f, F_ZOH, DB_ZOH))

        g = grafica(curva_droop, (float(F_ZOH[0]), float(F_ZOH[-1])),
                   (-40.0, 0.5), ancho=8.8, alto=2.8, color=C_IDEAL,
                   etiqueta_x="Hz", etiqueta_y="dB")
        g.move_to(DOWN * 0.1)
        self.play(FadeIn(g.ejes), run_time=0.5)
        self.play(Create(g.curva), run_time=1.8)
        self.wait(1.2)

        marca_nyq = g.vertical_en(FS / 2, color=C_CALCULO)
        punto_nyq = Dot(g.punto_de(FS / 2), color=C_CALCULO, radius=0.075)
        et_nyq = tag_hud("fs/2", font_size=19, color=C_CALCULO)
        et_nyq.next_to(marca_nyq, UP, buff=0.08)
        self.play(Create(marca_nyq), FadeIn(punto_nyq), FadeIn(et_nyq),
                  run_time=0.9)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"fs/2 = {fmt(DROOP_NYQ, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        marca_alta = g.vertical_en(F_ALTA, color=C_MUESTRA)
        punto_alta = Dot(g.punto_de(F_ALTA), color=C_MUESTRA, radius=0.075)
        self.play(Create(marca_alta), FadeIn(punto_alta), run_time=0.8)
        self.wait(0.8)

        rot.mostrar(cifra_pie(f"{fmt(F_ALTA, 0)} Hz = "
                              f"{fmt(DROOP_ALTA, 2)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- cierre: vuelve el titular, fs/2 -------------------------------
        self.play(FadeOut(marca_alta), FadeOut(punto_alta), run_time=0.5)
        self.play(Indicate(punto_nyq, scale_factor=1.6, color=C_CALCULO),
                  run_time=0.9)
        rot.mostrar(cifra_pie(f"fs/2 = {fmt(DROOP_NYQ, 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)
