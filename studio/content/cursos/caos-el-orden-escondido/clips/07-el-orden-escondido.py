class Clip7(Scene):
    """7 - El orden escondido. Dos señales igual de locas: el mapa de
    retorno delata cual tenia regla. Y dentro del caos, la isla del vals
    de tres pasos. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El orden escondido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: dos señales igual de locas --------------------------
        rot.mostrar(pie_curso("Dos señales que saltan igual de locas. Una "
                              "es azar; la otra, caos."), zona="abajo",
                    run_time=0.5)
        serie_caos = orbita_logistica(4.0, 0.2, 220)
        serie_azar = ruido_uniforme(220)

        def tira(serie, color, centro):
            pts = np.column_stack([np.linspace(0, 5.2, 60),
                                   serie[:60] * 0.9,
                                   np.zeros(60)])
            trazo = VMobject(color=color, stroke_width=2.0)
            trazo.set_points_as_corners(pts)
            trazo.move_to(centro)
            return trazo

        tira_c = tira(serie_caos, C_SISTEMA, UP * 2.15)
        tira_a = tira(serie_azar, C_FASE, UP * 1.05)
        self.play(Create(tira_c), Create(tira_a), run_time=2.4,
                  rate_func=linear)
        self.wait(3.2)

        # --- momento: el detector de reglas -------------------------------
        rot.mostrar(pie_curso("Grafica cada valor contra el siguiente: el "
                              "caos se delata — tenía una regla."),
                    zona="abajo", run_time=0.5)
        mapa_c = mapa_retorno(serie_caos, lado=2.7)
        mapa_c.move_to(LEFT * 2.4 + DOWN * 1.35)
        mapa_a = mapa_retorno(serie_azar, lado=2.7, color=C_FASE)
        mapa_a.move_to(RIGHT * 2.4 + DOWN * 1.35)
        self.play(FadeIn(mapa_c.caja), FadeIn(mapa_a.caja), run_time=0.6)
        self.play(
            LaggedStart(*[FadeIn(p, scale=0.5) for p in mapa_c.nube],
                        lag_ratio=0.012),
            LaggedStart(*[FadeIn(p, scale=0.5) for p in mapa_a.nube],
                        lag_ratio=0.012),
            run_time=3.0)
        tag_c = tag_junto(mapa_c, "caos: la regla aparece", DOWN,
                          buff=0.18, font_size=16, color=C_SISTEMA)
        tag_a = tag_junto(mapa_a, "azar: nada", DOWN, buff=0.18,
                          font_size=16, color=C_FASE)
        self.play(FadeIn(tag_c), FadeIn(tag_a), run_time=0.6)
        self.wait(4.0)

        # --- momento: la isla de orden ------------------------------------
        rot.mostrar(pie_curso("Y dentro del caos hay islas: por un "
                              "momento, el desorden se vuelve un vals de "
                              "tres pasos."), zona="abajo", run_time=0.5)
        self.play(FadeOut(tira_c), FadeOut(tira_a), FadeOut(mapa_c),
                  FadeOut(mapa_a), FadeOut(tag_c), FadeOut(tag_a),
                  run_time=0.7)
        ventana = imagen_bifurcacion(r=ZOOM_P3, res=(640, 380),
                                     alto_escena=4.3)
        ventana.move_to(UP * 0.25)
        self.play(FadeIn(ventana), run_time=1.2)
        self.wait(1.0)
        isla = VGroup(*[
            DashedLine(ventana.punto_de(r_v, 0.03),
                       ventana.punto_de(r_v, 0.97), stroke_width=1.8,
                       color=C_ORDEN).set_stroke(opacity=0.85)
            for r_v in VENTANA_P3])
        etiqueta = tag_hud("periodo 3", font_size=16, color=C_ORDEN)
        etiqueta.next_to(isla, UP, buff=0.12)
        self.play(Create(isla[0]), Create(isla[1]), FadeIn(etiqueta),
                  run_time=1.0)
        self.wait(7.6)
