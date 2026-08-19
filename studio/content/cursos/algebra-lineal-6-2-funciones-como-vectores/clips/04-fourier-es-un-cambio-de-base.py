class Clip4(Scene):
    """6.2.4 - Cambiar de base es girar los ejes; en R^12 los ejes nuevos
    son los armonicos, y las coordenadas del vector son los coeficientes de
    Fourier. Cierra la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        hud = hud_modulo("Modulo 04")
        self.add(hud)

        titulo = titulo_curso("Fourier es un cambio de base")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: cambiar de base es girar los ejes --------------------
        pie_plano = pie_curso("Cambiar de base es girar los ejes: el vector "
                              "no se mueve, cambian sus coordenadas.")
        rot.mostrar(pie_plano, zona="abajo", run_time=0.5)
        pl = plano_leccion()
        pl.fijo.set_stroke(opacity=0.95)   # la comparacion vieja/nueva ES el mensaje
        v = vector(pl, V_PLANO, color=C_VEC, nombre=r"\vec v")
        matriz = matriz_columnas(GIRO_BASE, font_size=30)
        panel = panel_derecha(matriz)
        self.play(FadeIn(pl), run_time=0.7)
        # El plano entra despues del pie y del titulo: sin esto la rejilla
        # viva se dibuja ENCIMA de sus letras (aqui es azul y se nota).
        self.bring_to_front(pie_plano, titulo, hud)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.7)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.5)
        # Sin pasar `v`: la rejilla (los ejes) gira y la flecha se queda.
        self.play(*pl.anim_matriz(GIRO_BASE), run_time=1.7)
        self.wait(3.4)

        # --- geometria de las filas ---------------------------------------
        ANCHO_B = 0.34
        Y_SENAL, Y_REC, Y_COEF = 2.00, 0.55, -1.50
        X_CIF = 4.75

        def fila(valores, color, y, ancho=ANCHO_B, escala=ESC_4,
                 etiquetas=None):
            b = barras(valores, colores=color, ancho=ancho, alto=1.0,
                       escala=escala, etiquetas=etiquetas, font_size=13)
            b.shift(np.array([0.0, y, 0.0]) - b.base.get_center())
            return b

        def crecer(b, valores):
            return [GrowFromEdge(r, DOWN if v >= 0 else UP)
                    for r, v in zip(b.barras, valores)]

        # --- momento: una senal periodica y sus doce muestras --------------
        rot.mostrar(pie_curso("Una señal de telemetría que se repite cada "
                              "órbita, muestreada doce veces."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pl), FadeOut(v), FadeOut(panel), run_time=0.6)
        ancho_g = 6.6
        g = grafica(f_senal, (0.0, 1.0), (-1.35, 1.35), ancho=ancho_g,
                    alto=2.0, color=C_VEC, etiqueta_x="t")
        g.move_to(UP * 1.45)
        curva = g.curva
        g.remove(curva)
        fila_v = fila(V_SENAL, C_VEC, -0.75, ancho=ancho_g / N_MUESTRAS)
        fila_v.shift(RIGHT * (g.ejes[0].get_center()[0] - 0.0))
        self.play(FadeIn(g), run_time=0.5)
        self.play(Create(curva), run_time=1.0)
        self.play(FadeIn(fila_v.base), *crecer(fila_v, V_SENAL), run_time=1.0)
        self.wait(3.3)

        # --- momento: sus coordenadas en la base de Fourier ----------------
        rot.mostrar(pie_curso("Sus coordenadas en la base de Fourier: un "
                              "producto punto con cada armónico."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(g), FadeOut(curva), run_time=0.5)
        destino_v = fila(V_SENAL, C_VEC, Y_SENAL)
        self.play(Transform(fila_v, destino_v), run_time=0.8)
        et_v = tag_junto(destino_v, "señal", LEFT, buff=0.45, font_size=20,
                         color=C_VEC)
        coef = fila(COEFS, C_J, Y_COEF, ancho=0.62, escala=ESC_4C,
                    etiquetas=TAGS_B)
        et_c = tag_junto(coef, "coeficientes", LEFT, buff=0.45, font_size=20,
                         color=C_J)
        self.play(FadeIn(coef.base), FadeIn(et_v), FadeIn(et_c),
                  FadeIn(VGroup(*coef.submobjects[1 + len(coef.barras):])),
                  *crecer(coef, COEFS), run_time=1.0)
        self.wait(3.4)

        # --- momento: reconstruir con 1, 2 y 3 armonicos -------------------
        rot.mostrar(pie_curso("Con uno, dos y tres armónicos la señal se "
                              "rehace: el error cae hasta cero."),
                    zona="abajo", run_time=0.5)
        lineas = VGroup()
        for k, y in zip(range(3), (1.15, 0.55, -0.05)):
            n = ARMONICOS[k]
            t = tag_hud(("1 armonico " if n == 1 else str(n) + " armonicos")
                        + " -> error " + fmt(ERRORES[k], 2), font_size=18)
            t.move_to(np.array([X_CIF, y, 0.0]))
            t.shift(RIGHT * (2.75 - t.get_left()[0]))   # alineadas por la izquierda
            t.set_opacity(0.3)
            lineas.add(t)
        rec = fila(RECONS[0], C_IMG, Y_REC)
        et_r = tag_junto(rec, "reconstrucción", LEFT, buff=0.45, font_size=20,
                         color=C_IMG)
        self.play(FadeIn(rec.base), FadeIn(et_r), FadeIn(lineas),
                  *crecer(rec, RECONS[0]),
                  *[Indicate(coef.barras[i], color=C_IMG) for i in (0, 1, 2)],
                  run_time=1.0)
        self.play(lineas[0].animate.set_opacity(1.0), run_time=0.4)
        self.wait(1.7)
        for k, nuevas in ((1, (3, 4)), (2, (5, 6))):
            self.play(Transform(rec, fila(RECONS[k], C_IMG, Y_REC)),
                      lineas[k].animate.set_opacity(1.0),
                      *[Indicate(coef.barras[i], color=C_IMG)
                        for i in nuevas], run_time=1.2)
            self.wait(1.9)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(self, rot, "Una señal es un vector.",
                       "Fourier, una base que la entiende.",
                       "Y si una matriz mueve el estado de un sistema paso "
                       "a paso, ¿a dónde lleva? Siguiente lección.",
                       fila_v, rec, coef, lineas, et_v, et_r, et_c)
