class Clip1(Scene):
    """4.3.1 - La fase de un FIR simetrico es una RECTA, pero solo dentro
    de la banda de paso: en los nulos da saltos de pi. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Fase lineal"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- los 9 taps, todos iguales -------------------------------------
        sec = Secuencia(H_SIM, 0, (0.0, 0.16), ancho=4.6, alto=1.35,
                        color=C_MUESTRA)
        sec.move_to(UP * 1.55)
        et_h = tag_hud("h[n]: 9 taps", font_size=19, color=C_MUESTRA)
        et_h.next_to(sec, LEFT, buff=0.30)
        self.play(FadeIn(sec.ejes), FadeIn(et_h), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(9)],
                              lag_ratio=0.06),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(9)],
                              lag_ratio=0.06), run_time=1.5)
        self.wait(1.2)

        # --- su modulo: la banda de paso llega hasta el primer nulo --------
        mag = respuesta_dibujo(W_SIM, MAG_SIM, ancho=7.4, alto=2.0,
                               piso_db=-46.0, techo_db=4.0, color=C_SALIDA)
        mag.move_to(DOWN * 1.15)
        et_mag = tag_hud("|H| dB", font_size=18, color=C_SALIDA)
        et_mag.next_to(mag, LEFT, buff=0.26)
        self.play(FadeIn(mag.ejes), FadeIn(et_mag), run_time=0.5)
        self.play(Create(mag.curva), run_time=2.0)
        nulo = mag.marca_w(PRIMER_NULO, color=C_RUIDO)
        et_nulo = tag_hud("primer nulo", font_size=18, color=C_RUIDO)
        et_nulo.next_to(mag.en(PRIMER_NULO, 4.0), UP, buff=0.10)
        self.play(Create(nulo), FadeIn(et_nulo), run_time=0.7)
        rot.mostrar(cifra_pie(f"primer nulo = {fmt(PRIMER_NULO, 3)} rad"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- la fase: recta DENTRO de la banda, saltos fuera ----------------
        self.play(FadeOut(sec), FadeOut(et_h), FadeOut(mag),
                  FadeOut(et_mag), FadeOut(nulo), FadeOut(et_nulo),
                  run_time=0.7)
        fase = respuesta_dibujo(W_SIM, FASE_SIM, ancho=7.2, alto=3.3,
                                piso_db=-3.1, techo_db=1.7,
                                color=C_MUESTRA)
        fase.move_to(LEFT * 0.55 + DOWN * 0.15)
        et_fase = tag_hud("fase rad", font_size=18, color=C_MUESTRA)
        et_fase.next_to(fase, LEFT, buff=0.24)
        et_w = tag_hud("w", font_size=18, color=C_TENUE)
        et_w.next_to(fase, DOWN, buff=0.22)
        self.play(FadeIn(fase.ejes), FadeIn(et_fase), FadeIn(et_w),
                  run_time=0.5)
        self.play(Create(fase.curva), run_time=2.4)
        self.wait(2.2)

        # --- el ajuste, medido SOLO en la banda ----------------------------
        w_b = W_SIM[EN_BANDA]
        banda = fase.banda(w_b[0], w_b[-1], color=C_CALCULO, opacidad=0.13)
        recta = VMobject(color=C_CALCULO, stroke_width=3.4)
        recta.set_points_as_corners(
            [fase.en(w, np.polyval(AJUSTE, w)) for w in w_b])
        self.play(FadeIn(banda), run_time=0.6)
        self.play(Create(recta), run_time=1.5)
        panel = panel_cifras((f"pendiente {fmt(PENDIENTE_FASE, 4)}",
                              C_CALCULO),
                             (f"residuo {RESIDUO_FASE:.1e} rad", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.6)
        et_banda = tag_hud("ajuste solo aqui", font_size=18,
                           color=C_CALCULO)
        et_banda.next_to(banda, UP, buff=0.14)
        self.play(FadeIn(et_banda), run_time=0.4)
        self.wait(3.6)

        # --- la trampa: fuera de la banda la recta es mentira ---------------
        salto = fase.marca_w(PRIMER_NULO, color=C_RUIDO)
        et_salto = tag_hud("fuera: saltos de pi", font_size=19,
                           color=C_RUIDO)
        et_salto.next_to(fase.en(2.35, 1.7), UP, buff=0.10)
        self.play(Create(salto), FadeIn(et_salto), run_time=0.8)
        self.wait(3.6)

        rot.mostrar(formula_pie(r"\angle H(\omega) = -4\,\omega"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)
