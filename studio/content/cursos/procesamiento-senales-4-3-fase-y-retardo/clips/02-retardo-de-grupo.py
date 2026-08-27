class Clip2(Scene):
    """4.3.2 - El retardo de grupo es la pendiente cambiada de signo: plano
    en 4 muestras, y un pulso lo cruza entero sin torcerse. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Retardo de grupo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- el retardo de grupo dentro de la banda de paso -----------------
        mascara = W_GD < PRIMER_NULO * 0.9
        w_b, gd_b = W_GD[mascara], GD_SIM[mascara]
        gd = respuesta_dibujo(w_b, gd_b, ancho=6.8, alto=2.2, piso_db=0.0,
                              techo_db=8.0, color=C_CALCULO)
        gd.move_to(UP * 0.55)
        et_gd = tag_hud("retardo muestras", font_size=18, color=C_CALCULO)
        et_gd.next_to(gd, LEFT, buff=0.26)
        et_wb = tag_hud("w en la banda", font_size=18, color=C_TENUE)
        et_wb.next_to(gd, DOWN, buff=0.22)
        self.play(FadeIn(gd.ejes), FadeIn(et_gd), FadeIn(et_wb),
                  run_time=0.5)
        self.play(Create(gd.curva), run_time=2.4)
        self.wait(0.6)
        punto = Dot(gd.en(w_b[0], gd_b[0]), radius=0.075, color=C_CALCULO)
        self.play(FadeIn(punto), run_time=0.3)
        self.play(punto.animate.move_to(gd.en(w_b[-1], gd_b[-1])),
                  run_time=2.0)
        panel = panel_cifras((f"minimo {fmt(GD_MIN, 4)}", C_CALCULO),
                             (f"maximo {fmt(GD_MAX, 4)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.6)
        rot.mostrar(formula_pie(
            r"\tau_g(\omega) = -\frac{d\,\angle H(\omega)}{d\omega}"),
            zona="abajo", run_time=0.5)
        self.wait(4.0)

        # --- lo que ese numero le hace a un pulso ---------------------------
        self.play(FadeOut(gd), FadeOut(et_gd), FadeOut(et_wb),
                  FadeOut(punto), FadeOut(panel), run_time=0.7)

        n_vis = 32
        p_in = np.zeros(n_vis)
        ven = ventana_de("hann", 13)
        p_in[2:2 + len(ven)] = ven
        p_out = convolucion(p_in, H_SIM)[:n_vis]
        n_ent = int(np.argmax(p_in))
        n_sal = int(np.argmax(p_out))
        d_med = n_sal - n_ent

        ent = Secuencia(p_in, 0, (0.0, 1.18), ancho=8.4, alto=1.35,
                        color=C_MUESTRA, radio=0.048)
        ent.move_to(UP * 1.42)
        sal = Secuencia(p_out, 0, (0.0, 1.18), ancho=8.4, alto=1.35,
                        color=C_SALIDA, radio=0.048)
        sal.move_to(DOWN * 0.72)
        et_ent = tag_hud("entrada", font_size=18, color=C_MUESTRA)
        et_ent.next_to(ent, LEFT, buff=0.24)
        et_sal = tag_hud("salida", font_size=18, color=C_SALIDA)
        et_sal.next_to(sal, LEFT, buff=0.24)
        self.play(FadeIn(ent.ejes), FadeIn(et_ent), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(ent.tallo(i)) for i in range(n_vis)],
                              lag_ratio=0.02),
                  LaggedStart(*[FadeIn(ent.punto(i)) for i in range(n_vis)],
                              lag_ratio=0.02), run_time=1.4)
        self.wait(1.2)
        self.play(FadeIn(sal.ejes), FadeIn(et_sal), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sal.tallo(i)) for i in range(n_vis)],
                              lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sal.punto(i)) for i in range(n_vis)],
                              lag_ratio=0.02), run_time=1.6)
        self.wait(2.0)

        # --- las cuatro muestras, medidas sobre lo dibujado -----------------
        l_ent = DashedLine(ent.en(n_ent, 1.18), sal.en(n_ent, 0.0),
                           color=C_MUESTRA, stroke_width=1.8,
                           dash_length=0.08)
        l_sal = DashedLine(ent.en(n_sal, 1.18), sal.en(n_sal, 0.0),
                           color=C_SALIDA, stroke_width=1.8,
                           dash_length=0.08)
        self.play(Create(l_ent), run_time=0.6)
        self.play(Create(l_sal), run_time=0.6)
        y_flecha = (ent.en(0, 0.0)[1] + sal.en(0, 1.18)[1]) / 2.0
        flecha = DoubleArrow(
            np.array([ent.en(n_ent, 0.0)[0], y_flecha, 0.0]),
            np.array([ent.en(n_sal, 0.0)[0], y_flecha, 0.0]),
            color=C_CALCULO, buff=0.0, stroke_width=3.0, tip_length=0.16)
        et_flecha = tag_hud(f"{d_med} muestras", font_size=19,
                            color=C_CALCULO)
        et_flecha.next_to(flecha, RIGHT, buff=0.20)
        self.play(Create(flecha), FadeIn(et_flecha), run_time=0.8)
        rot.mostrar(cifra_pie(f"retardo medido = {d_med} muestras"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        rot.mostrar(formula_pie(r"\tau_g = \frac{N-1}{2} = \frac{9-1}{2} = 4"),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)
