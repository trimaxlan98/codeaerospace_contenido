class Clip1(Scene):
    """10.3.1 - A la red no se le dice como filtrar: se le dan pares
    (entrada, salida deseada) y ella mueve sus 17 pesos hasta que el
    error del entrenamiento se hunde. (~32 s)"""

    # el lote con el que el style_block entrena: entrenar_filtro(3000, ...)
    N_EJ = N_EJEMPLOS   # sale del style_block, no a mano

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Aprender por ejemplos"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- uno de los 3000 pares: entrada y salida deseada --------------
        n_ver = 120
        x_ver = ruido_blanco(n_ver, 1.0, 9)
        d_ver = convolucion(x_ver, H_OBJETIVO)[:n_ver]

        sec_x = Secuencia(x_ver, 0, None, ancho=10.6, alto=1.5,
                          color=C_MUESTRA, radio=0.022, grosor=1.7,
                          eje_y=False)
        sec_x.move_to(UP * 2.15)
        et_x = tag_hud("x[n]", font_size=19, color=C_MUESTRA)
        et_x.next_to(sec_x, LEFT, buff=0.20)
        self.play(FadeIn(sec_x), FadeIn(et_x), run_time=0.9)
        self.wait(1.6)

        sec_d = Secuencia(d_ver, 0, None, ancho=10.6, alto=1.5,
                          color=C_SALIDA, radio=0.022, grosor=1.7,
                          eje_y=False)
        sec_d.move_to(UP * 0.42)
        et_d = tag_hud("d[n]", font_size=19, color=C_SALIDA)
        et_d.next_to(sec_d, LEFT, buff=0.20)
        self.play(FadeIn(sec_d), FadeIn(et_d), run_time=0.9)
        rot.mostrar(cifra_pie(f"{self.N_EJ} ejemplos"), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        par = VGroup(sec_x, et_x, sec_d, et_d)
        self.play(FadeOut(par), run_time=0.7)

        # --- lo unico que la red mueve: sus 17 pesos ----------------------
        rango_w = (-0.06, 0.30)
        pasos_vistos = (1, 3, 8, 20, 60, 150, PASOS)
        w_paso = [entrenar_filtro(self.N_EJ, N_TAPS_RED, k, 0.05, 9)[0]
                  for k in pasos_vistos]

        sec_w = Secuencia(w_paso[0], 0, rango_w, ancho=5.2, alto=2.3,
                          color=C_APREND, radio=0.045, grosor=2.6,
                          eje_y=False)
        sec_w.move_to(LEFT * 3.35 + DOWN * 0.05)
        et_w = tag_hud(f"{N_TAPS_RED} pesos", font_size=19, color=C_APREND)
        et_w.next_to(sec_w, DOWN, buff=0.30)

        # --- y lo que mide: el error, en escala logaritmica ---------------
        eje_paso = np.arange(1.0, PASOS + 1.0)
        hist_db = 10.0 * np.log10(HIST)
        rf = respuesta_dibujo(eje_paso, hist_db, ancho=5.2, alto=2.5,
                              piso_db=-190.0, techo_db=0.0, color=C_CALCULO)
        rf.move_to(RIGHT * 3.55 + UP * 0.05)
        ticks = VGroup()
        for db_t, txt in ((0.0, "1e+00"), (-60.0, "1e-06"),
                          (-120.0, "1e-12"), (-180.0, "1e-18")):
            p = rf.en(eje_paso[0], db_t)
            marca = Line(p, p + LEFT * 0.13, color=C_EJE, stroke_width=1.6)
            et = tag_hud(txt, font_size=15, color=C_TENUE)
            et.next_to(marca, LEFT, buff=0.08)
            ticks.add(marca, et)
        et_paso = tag_hud("paso", font_size=17, color=C_TENUE)
        et_paso.next_to(rf, DOWN, buff=0.30)

        self.play(FadeIn(sec_w), FadeIn(et_w), FadeIn(rf.ejes),
                  FadeIn(ticks), FadeIn(et_paso), run_time=0.9)
        self.wait(0.8)

        # los pesos crecen mientras el error se hunde
        self.play(
            Create(rf.curva, run_time=4.9),
            Succession(*[Transform(sec_w, sec_w.con_valores(w),
                                   run_time=0.7)
                         for w in w_paso[1:]]))
        self.add(rf.curva)
        self.wait(1.0)

        marca_fin = rf.punto(eje_paso[-1], color=C_CALCULO)
        self.play(FadeIn(marca_fin), run_time=0.5)
        rot.mostrar(cifra_pie(f"error {fmt(ERR_INICIAL, 4)} a "
                              f"{ERR_FINAL:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras((f"{PASOS} pasos", C_APREND),
                             (f"{N_TAPS_RED} pesos", C_APREND),
                             (f"error {ERR_FINAL:.1e}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
        rot.mostrar(formula_pie(r"w \leftarrow w + \eta\,X^{T}e"),
                    zona="abajo", run_time=0.5)
        self.wait(7.4)
