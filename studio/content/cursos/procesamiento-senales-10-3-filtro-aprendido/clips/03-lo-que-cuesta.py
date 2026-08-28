class Clip3(Scene):
    """10.3.3 - La otra cara: 400 pasos, 3000 ejemplos y una red para
    llegar a donde una sola linea de diseño llega sin datos. (~31 s)"""

    # el lote con el que el style_block entrena: entrenar_filtro(3000, ...)
    N_EJ = N_EJEMPLOS   # sale del style_block, no a mano

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Lo que ha costado"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        divisor = Line(UP * 2.75, DOWN * 2.35, color=C_EJE,
                       stroke_width=1.4)
        self.play(FadeIn(divisor), run_time=0.5)

        # --- IZQUIERDA: lo que cuesta aprenderlo --------------------------
        eje_paso = np.arange(1.0, PASOS + 1.0)
        hist_db = 10.0 * np.log10(HIST)
        rf = respuesta_dibujo(eje_paso, hist_db, ancho=4.2, alto=2.0,
                              piso_db=-190.0, techo_db=0.0, color=C_CALCULO)
        rf.move_to(LEFT * 3.25 + UP * 0.7)
        ticks = VGroup()
        for db_t, txt in ((0.0, "1e+00"), (-180.0, "1e-18")):
            p = rf.en(eje_paso[0], db_t)
            marca = Line(p, p + LEFT * 0.13, color=C_EJE, stroke_width=1.6)
            et = tag_hud(txt, font_size=15, color=C_TENUE)
            et.next_to(marca, LEFT, buff=0.08)
            ticks.add(marca, et)

        pasos_cont = (1, 50, 100, 200, 300, PASOS)
        cont = tag_hud(f"paso {pasos_cont[0]:03d}", font_size=21,
                       color=C_APREND)
        cont.move_to(LEFT * 3.25 + UP * 2.30)

        self.play(FadeIn(rf.ejes), FadeIn(ticks), FadeIn(cont),
                  run_time=0.7)
        marcha, dur, t_previo = [], 5.0, 0.0
        for k in pasos_cont[1:]:
            nuevo = tag_hud(f"paso {k:03d}", font_size=21, color=C_APREND)
            nuevo.move_to(cont.get_center())
            t_k = dur * k / PASOS            # cuando el trazo llega a k
            marcha += [Wait(max(t_k - t_previo - 0.02, 0.02)),
                       Transform(cont, nuevo, run_time=0.02)]
            t_previo = t_k
        self.play(Create(rf.curva, run_time=dur), Succession(*marcha))
        self.add(rf.curva)
        self.wait(0.6)

        rot.mostrar(cifra_pie(f"error {ERR_FINAL:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        coste = VGroup(tag_hud(f"{self.N_EJ} ejemplos", font_size=20,
                               color=C_APREND),
                       tag_hud(f"{N_TAPS_RED} pesos", font_size=20,
                               color=C_APREND),
                       tag_hud(f"{PASOS} pasos", font_size=20,
                               color=C_APREND))
        coste.arrange(DOWN, buff=0.24)
        coste.move_to(LEFT * 3.25 + DOWN * 1.45)
        self.play(LaggedStart(*[FadeIn(t) for t in coste], lag_ratio=0.35),
                  run_time=0.9)
        self.wait(2.2)

        # --- DERECHA: lo que cuesta diseñarlo -----------------------------
        codigo = tag_hud(f'fir_ventana({N_TAPS_RED - 1}, 0.25, "hann", 2.0)',
                         font_size=18, color=C_MUESTRA)
        codigo.move_to(RIGHT * 3.5 + UP * 2.30)
        self.play(FadeIn(codigo), run_time=0.8)
        self.wait(2.0)

        rango_h = (-0.06, 0.30)
        sec_h = Secuencia(H_OBJETIVO, 0, rango_h, ancho=4.4, alto=1.9,
                          color=C_MUESTRA, radio=0.070, grosor=4.2,
                          eje_y=False)
        sec_h.move_to(RIGHT * 3.5 + UP * 0.7)
        diseno = VGroup(tag_hud("1 linea", font_size=20, color=C_MUESTRA),
                        tag_hud("sin datos", font_size=20, color=C_MUESTRA))
        diseno.arrange(DOWN, buff=0.24)
        diseno.move_to(RIGHT * 3.5 + DOWN * 1.33)
        self.play(FadeIn(sec_h), FadeIn(diseno), run_time=0.7)
        self.wait(2.2)

        # --- y lo aprendido cae justo encima ------------------------------
        sec_w = Secuencia(W_APRENDIDO, 0, rango_h, ancho=4.4, alto=1.9,
                          color=C_APREND, radio=0.034, grosor=1.8,
                          eje_y=False)
        sec_w.shift(sec_h._origen() - sec_w._origen())
        et_w = tag_hud("w aprendido", font_size=20, color=C_APREND)
        et_w.next_to(diseno, DOWN, buff=0.24)
        self.play(FadeIn(sec_w), FadeIn(et_w), run_time=0.9)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"coseno {COS:.6f}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(cifra_pie("el mismo filtro"), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
