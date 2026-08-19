class Clip2(Scene):
    """6.2.2 - Dos funciones se suman barra a barra y se escalan barra a
    barra: exactamente las dos operaciones de un vector. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Sumar y escalar funciones")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- geometria del clip -------------------------------------------
        CAJA = LEFT * 4.0 + UP * 0.35
        ANCHO_CAJA, ALTO_CAJA = 4.6, 2.9
        RANGO_Y = (-0.95, 1.75)          # entra f, entra g y entra f + g
        X_BARRAS = 3.1
        Y_F, Y_G, Y_S = 2.00, 0.60, -1.30
        ANCHO_BARRA = ANCHO_CAJA / N_MUESTRAS

        def caja(f, color):
            """Una grafica en LA MISMA caja: se alinea por el ancla (el
            bbox no sirve, cada curva tiene su propia altura)."""
            gr = grafica(f, (0.0, 1.0), RANGO_Y, ancho=ANCHO_CAJA,
                         alto=ALTO_CAJA, color=color, etiqueta_x="t")
            gr.move_to(CAJA)
            gr.shift(CAJA - gr._ancla.get_center())
            return gr

        def fila(valores, color, y):
            b = barras(valores, colores=color, ancho=ANCHO_BARRA, alto=1.0,
                       escala=ESC_2)
            b.shift(np.array([X_BARRAS, y, 0.0]) - b.base.get_center())
            return b

        # --- momento: dos funciones ---------------------------------------
        gf = caja(f_campana, C_VEC)
        curva_f = gf.curva
        gf.remove(curva_f)               # se anima aparte (ver clip 1)
        curva_g = caja(f_onda, C_VEC_2).curva
        curva_s = caja(f_suma, C_IMG).curva
        curva_m = caja(f_media, C_VEC).curva

        rot.mostrar(pie_curso("Dos funciones sobre el mismo intervalo: f en "
                              "rojo, g en violeta."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(gf), run_time=0.5)
        self.play(Create(curva_f), run_time=0.9)
        self.play(Create(curva_g), run_time=0.9)
        self.wait(3.0)

        # --- momento: las dos, muestreadas --------------------------------
        rot.mostrar(pie_curso("Muestreadas en los mismos doce instantes: "
                              "dos vectores de R de doce."), zona="abajo",
                    run_time=0.5)
        fila_f = fila(V_F, C_VEC, Y_F)
        fila_g = fila(V_G, C_VEC_2, Y_G)
        et_f = MathTex(r"\vec f", font_size=30, color=C_VEC)
        et_g = MathTex(r"\vec g", font_size=30, color=C_VEC_2)
        et_s = MathTex(r"\vec f + \vec g", font_size=30, color=C_IMG)
        for et, y in ((et_f, Y_F), (et_g, Y_G), (et_s, Y_S)):
            et.move_to(np.array([X_BARRAS + ANCHO_CAJA / 2 + 0.85, y, 0.0]))
        mas = MathTex("+", font_size=38, color=C_TENUE)
        mas.move_to(np.array([0.35, (Y_F + Y_G) / 2, 0.0]))
        igual = MathTex("=", font_size=38, color=C_TENUE)
        igual.move_to(np.array([0.35, (Y_G + Y_S) / 2, 0.0]))
        self.play(FadeIn(fila_f.base), FadeIn(et_f),
                  *[GrowFromEdge(b, DOWN) for b in fila_f.barras],
                  run_time=0.9)
        self.play(FadeIn(fila_g.base), FadeIn(et_g), FadeIn(mas),
                  *[GrowFromEdge(b, DOWN if v >= 0 else UP)
                    for b, v in zip(fila_g.barras, V_G)], run_time=0.9)
        self.wait(3.2)

        # --- momento: sumar barra a barra ---------------------------------
        rot.mostrar(pie_curso("Sumarlas es sumar barra a barra: la "
                              "coordenada k de f más la coordenada k de g."),
                    zona="abajo", run_time=0.5)
        copia_f = fila(V_F, C_VEC, Y_S)
        self.play(TransformFromCopy(fila_f, copia_f), FadeIn(igual),
                  run_time=1.1)
        suma = fila(V_MAS, C_IMG, Y_S)
        self.play(Transform(copia_f, suma), FadeIn(et_s),
                  Indicate(fila_g, color=C_VEC_2, scale_factor=1.05),
                  run_time=1.4)
        self.play(Create(curva_s), run_time=0.9)
        self.wait(3.4)

        # --- momento: escalar ---------------------------------------------
        rot.mostrar(pie_curso("Y multiplicarla por un medio encoge cada "
                              "barra a la mitad. Nada más."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(fila_g), FadeOut(copia_f), FadeOut(curva_g),
                  FadeOut(curva_s), FadeOut(mas), FadeOut(igual),
                  FadeOut(et_g), FadeOut(et_s), FadeOut(et_f),
                  run_time=0.6)
        self.play(fila_f.animate.shift(UP * (Y_G - Y_F)), run_time=0.7)
        media = fila(V_MEDIA, C_VEC, Y_G)
        et_m = MathTex(r"\tfrac{1}{2}\,\vec f", font_size=30, color=C_VEC)
        et_m.move_to(np.array([X_BARRAS + ANCHO_CAJA / 2 + 0.85, Y_G, 0.0]))
        # La etiqueta cambia de estructura (2 glifos -> fraccion): et_f ya
        # se fue con el resto y et_m entra sola (un Transform morfearia
        # glifos rotos, y un fundido cruzado las encima medio segundo).
        self.play(Transform(fila_f, media), Transform(curva_f, curva_m),
                  FadeIn(et_m), run_time=1.4)
        self.wait(3.6)

        # --- momento: eso ES un espacio vectorial --------------------------
        rot.mostrar(pie_curso("Sumar y escalar: las dos únicas operaciones "
                              "que hacen falta. Las funciones ya son "
                              "vectores."), zona="abajo", run_time=0.5)
        ley = MathTex(r"a\,\vec f + b\,\vec g \in \mathbb{R}^{12}",
                      font_size=32, color=C_CALCULO)
        panel = panel_derecha(ley)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.4)
