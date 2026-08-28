class Clip3(Scene):
    """9.1.3 - Welch: partir en trozos solapados, estimar cada uno y
    PROMEDIAR. El piso se calma. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("Promediar"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la señal partida en trozos -----------------------------------
        n_ver = 1024
        sec = Secuencia(X_E[:n_ver], 0, None, ancho=10.4, alto=1.3,
                        color=C_SENAL, radio=0.015, eje_y=False)
        sec.move_to(UP * 2.25)
        self.play(FadeIn(sec), run_time=0.8)
        trozos = VGroup()
        for i in range(0, n_ver - 256, 128):
            trozos.add(sec.ventana(i, i + 255, color=C_CALCULO,
                                   opacidad=0.10))
        self.play(LaggedStart(*[FadeIn(v) for v in trozos], lag_ratio=0.18),
                  run_time=1.8)
        rot.mostrar(cifra_pie(f"{TROZOS[256]} trozos de 256"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- el periodograma de antes, y el promedio ----------------------
        piso = -25.0
        rf = respuesta_dibujo(F_PER, DB_PER, ancho=10.2, alto=2.6,
                              piso_db=piso, techo_db=12.0, color=C_RUIDO)
        rf.move_to(DOWN * 1.35)
        self.play(FadeIn(rf), run_time=1.0)
        self.wait(1.6)

        rf_w = respuesta_dibujo(F_W[256], DB_W[256], ancho=10.2, alto=2.6,
                                piso_db=piso, techo_db=12.0, color=C_SALIDA)
        rf_w.move_to(DOWN * 1.35)
        self.play(rf.curva.animate.set_stroke(opacity=0.25), run_time=0.5)
        self.play(Create(rf_w.curva), run_time=1.8)
        self.add(rf_w.curva)
        rot.mostrar(cifra_pie(f"dispersion {fmt(DISP_W[256], 2)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras((f"una vez: {fmt(DISP_PER, 2)} dB", C_RUIDO),
                             (f"{TROZOS[256]} trozos: {fmt(DISP_W[256], 2)} dB",
                              C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(cifra_pie(f"{fmt(MEJORA_DISP, 1)} veces mas liso"),
                    zona="abajo", run_time=0.5)
        self.wait(9.0)
