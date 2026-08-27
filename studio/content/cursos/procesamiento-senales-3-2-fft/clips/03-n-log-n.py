class Clip3(Scene):
    """3.2.3 - Las multiplicaciones CONTADAS sobre el grafo, en escala
    logaritmica: para N = 1024 la razon medida es 204.8x. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El precio, contado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        log_dft = np.log10(np.asarray(TABLA_DFT, float))
        log_fft = np.log10(np.asarray(TABLA_FFT, float))
        rango = (0.0, 7.9)
        bd = barras(log_dft, ancho=7.2, alto=2.0, color=C_RUIDO,
                    rango_y=rango)
        bd.move_to(UP * 1.75)
        bf = barras(log_fft, ancho=7.2, alto=2.0, color=C_SALIDA,
                    rango_y=rango)
        bf.move_to(DOWN * 1.35)
        et_d = tag_hud("DFT", font_size=20, color=C_RUIDO)
        et_d.next_to(bd, LEFT, buff=0.32)
        et_f = tag_hud("FFT", font_size=20, color=C_SALIDA)
        et_f.next_to(bf, LEFT, buff=0.32)
        # la nota de escala vale para las DOS filas: va en el pasillo de
        # la izquierda, entre las dos etiquetas.
        et_log = tag_hud("escala log", font_size=17, color=C_TENUE)
        et_log.next_to(et_d, DOWN, buff=0.34).align_to(et_d, RIGHT)

        # --- la DFT directa -----------------------------------------------
        self.play(FadeIn(bd.ejes), FadeIn(et_d), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bd.barras],
                              lag_ratio=0.16), run_time=1.7)
        rot.mostrar(cifra_pie(f"DFT 1024: {OPS_DFT} mult", color=C_RUIDO),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- la FFT sobre el grafo -----------------------------------------
        self.play(FadeIn(bf.ejes), FadeIn(et_f), FadeIn(et_log),
                  run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in bf.barras],
                              lag_ratio=0.16), run_time=1.7)
        rot.mostrar(cifra_pie(f"FFT 1024: {OPS_FFT} mult", color=C_SALIDA),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- que N es cada columna ------------------------------------------
        et_n = VGroup()
        for i, n in enumerate(TABLA_N):
            e = tag_hud(f"N = {n}", font_size=18, color=C_TENUE)
            e.move_to(np.array([bd.barra(i).get_center()[0], 0.18, 0.0]))
            et_n.add(e)
        self.play(LaggedStart(*[FadeIn(e) for e in et_n], lag_ratio=0.10),
                  run_time=1.2)
        self.wait(1.8)

        # --- la columna de 1024 ----------------------------------------------
        i_g = TABLA_N.index(N_GRANDE)
        banda = Rectangle(width=bd.ancho / len(TABLA_N),
                          height=bd.alto + bf.alto + 1.4,
                          stroke_color=C_CALCULO, stroke_width=1.6,
                          fill_color=C_CALCULO, fill_opacity=0.09)
        banda.move_to(np.array([bd.barra(i_g).get_center()[0], 0.20, 0.0]))
        self.play(FadeIn(banda), run_time=0.7)
        rot.mostrar(cifra_pie(f"razon = {RAZON:.1f}x"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- y la razon de cada N ---------------------------------------------
        et_r = VGroup()
        for i, r in enumerate(TABLA_RAZON):
            col = C_CALCULO if i == i_g else C_TENUE
            e = tag_hud(f"{r:.1f}x", font_size=18, color=col)
            e.move_to(np.array([bd.barra(i).get_center()[0], -0.32, 0.0]))
            et_r.add(e)
        self.play(LaggedStart(*[FadeIn(e) for e in et_r], lag_ratio=0.10),
                  run_time=1.2)
        self.wait(2.4)

        rot.mostrar(formula_pie(r"N^{2} \;\longrightarrow\; N\log_2 N"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        panel = panel_cifras((f"N = {N_GRANDE}", C_TENUE),
                             (f"DFT: {OPS_DFT}", C_RUIDO),
                             (f"FFT: {OPS_FFT}", C_SALIDA),
                             desplazar=UP * 0.42)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.4)
