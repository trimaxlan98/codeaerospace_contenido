class Clip2(Scene):
    """1.3.2 - La suma de sincs: cada muestra pone una sinc escalada; la
    suma reconstruye la curva casi exacta, con error ~100x menor que el
    ZOH sobre la misma ventana. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La suma de sincs"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        sec = Secuencia(XK, 0, (-1.18, 1.18), ancho=10.4, alto=2.6,
                        color=C_MUESTRA)
        sec.move_to(DOWN * 0.20)
        curva_real = sec.curva_de(T_DENSO, vibracion(T_DENSO),
                                  color=C_SENAL, grosor=2.0, fs=FS)
        self.play(FadeIn(sec.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in
                                range(N_MUESTRAS)], lag_ratio=0.015),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in
                                range(N_MUESTRAS)], lag_ratio=0.015),
                  run_time=1.3)
        self.play(Create(curva_real), run_time=1.3)
        self.wait(1.4)

        # --- cada muestra pone una sinc -------------------------------------
        idx_sincs = [24, 27, 30, 33, 36, 39, 42, 45]
        sincs = VGroup()
        for i in idx_sincs:
            y_i = XK[i] * np.sinc((T_DENSO - TK[i]) * FS)
            c = sec.curva_de(T_DENSO, y_i, color=C_IDEAL, grosor=1.4, fs=FS)
            c.set_stroke(opacity=0.5)
            sincs.add(c)
        self.play(LaggedStart(*[Create(c) for c in sincs], lag_ratio=0.12),
                  run_time=2.4)
        et_sinc = tag_junto(sincs, "sincs", UP, buff=0.14, font_size=19,
                            color=C_IDEAL)
        et_sinc.move_to(sec.en(30.0, 1.02))
        self.play(FadeIn(et_sinc), run_time=0.6)
        self.wait(2.2)

        # --- la suma cae exacta sobre la curva -------------------------------
        curva_sinc = sec.curva_de(T_DENSO, REC_SINC, color=C_SALIDA,
                                  grosor=3.0, fs=FS)
        self.play(FadeOut(sincs), FadeOut(et_sinc), run_time=0.6)
        self.play(Create(curva_sinc), run_time=1.8)
        self.wait(2.4)

        ventana = sec.ventana(6, 57, color=C_CALCULO, opacidad=0.10)
        # tag_hud: tag_junto con dos+ palabras pierde el hueco del espacio
        # en Rajdhani ("interior sinbordes"); Space Mono si lo dibuja.
        et_vent = tag_hud("interior sin bordes", font_size=18, color=C_TENUE)
        et_vent.next_to(ventana, DOWN, buff=0.14)
        self.play(FadeIn(ventana), FadeIn(et_vent), run_time=0.8)
        self.wait(2.0)

        rot.mostrar(formula_pie(r"x(t) = \sum_n x[n]\,\mathrm{sinc}\!"
                                r"\left(\frac{t - nT_s}{T_s}\right)"),
                    zona="abajo", run_time=0.6)
        self.wait(3.6)

        panel = panel_cifras((f"sinc: {fmt(ERR_SINC, 4)}", C_SALIDA),
                             (f"zoh: {fmt(ERR_ZOH, 4)}", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(5.0)
