class Clip1(Scene):
    """5.1.1 - El filtro ideal es un rectangulo en frecuencia, y eso en el
    tiempo es una sinc que no termina nunca. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("La sinc que no cabe"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- lo que se pide: un rectangulo -------------------------------
        w_ideal = np.linspace(0.0, np.pi, 400)
        db_ideal = np.where(w_ideal <= FC * np.pi, 0.0, -60.0)
        rf = respuesta_dibujo(w_ideal, db_ideal, ancho=5.4, alto=2.1,
                              piso_db=-60.0, techo_db=6.0, color=C_IDEAL)
        rf.move_to(UP * 1.75 + LEFT * 3.3)
        et_rf = tag_hud("lo que se pide", font_size=19, color=C_IDEAL)
        et_rf.next_to(rf, DOWN, buff=0.22)
        self.play(FadeIn(rf), FadeIn(et_rf), run_time=0.9)
        self.wait(1.6)

        # --- lo que eso vale en el tiempo: una sinc sin fin ---------------
        sec = Secuencia(H_SINC, -(N_SINC // 2), (-0.12, 0.55), ancho=11.0,
                        alto=2.0, color=C_MUESTRA, radio=0.04)
        sec.move_to(DOWN * 1.55)
        et_sec = tag_hud("h[n]", font_size=19, color=C_MUESTRA)
        et_sec.next_to(sec, LEFT, buff=0.26)
        self.play(FadeIn(sec.ejes), FadeIn(et_sec), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(N_SINC)],
                              lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(N_SINC)],
                              lag_ratio=0.02), run_time=2.4)
        self.wait(1.8)

        puntos = VGroup(*[tag_hud("...", font_size=22, color=C_MUESTRA)
                          for _ in range(2)])
        puntos[0].next_to(sec.en(-(N_SINC // 2) - 0.5, 0.0), LEFT, buff=0.12)
        puntos[1].next_to(sec.en(N_SINC // 2 + 0.5, 0.0), RIGHT, buff=0.12)
        self.play(FadeIn(puntos), run_time=0.6)
        self.wait(3.2)

        # --- solo se puede guardar un trozo -------------------------------
        rot.mostrar(cifra_pie(f"orden = {ORDEN}"), zona="abajo",
                    run_time=0.5)
        corte = sec.ventana(N_SINC // 2 - ORDEN // 2,
                            N_SINC // 2 + ORDEN // 2, color=C_CALCULO,
                            opacidad=0.12)
        self.play(FadeIn(corte), run_time=0.9)
        self.wait(1.6)
        fuera = VGroup(*[sec.tallo(i) for i in range(N_SINC)
                         if abs(i - N_SINC // 2) > ORDEN // 2]
                       + [sec.punto(i) for i in range(N_SINC)
                          if abs(i - N_SINC // 2) > ORDEN // 2])
        self.play(fuera.animate.set_opacity(0.13), FadeOut(puntos),
                  run_time=1.0)
        self.wait(2.2)

        panel = panel_cifras(f"orden = {ORDEN}", f"{N_TAPS} taps",
                             (f"corte = {fmt(FC, 2)} pi", C_IDEAL))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"h[n] = 2f_c\,\mathrm{sinc}(2f_c n)"),
                    zona="abajo", run_time=0.5)
        self.wait(6.2)
