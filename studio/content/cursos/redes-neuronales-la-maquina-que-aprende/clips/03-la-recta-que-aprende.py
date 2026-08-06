class Clip3(Scene):
    """3 - La recta que aprende. Regresion lineal en vivo: una recta mala,
    el error medido como segmentos verticales, y el descenso de gradiente
    que corrige la recta paso a paso mientras la curva de perdida cae."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("La recta que aprende")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(1.1)

        # --- momento: plano de datos desplazado a la izquierda -------------
        ejes = ejes_plano(lado=4.4)
        ejes.shift(LEFT * 1.7)
        xs, ys = datos_recta(n=26, pendiente=0.55, ordenada=0.25, ruido=0.28,
                             semilla=7)
        puntos = VGroup(*[Dot(ejes.c2p(x, y), radius=0.055, color=C_DATO_A)
                          for x, y in zip(xs, ys)])
        self.play(Create(ejes), run_time=1.0)
        self.play(FadeIn(puntos, lag_ratio=0.05), run_time=1.2)
        self.wait(1.4)

        # --- momento: recta inicial mala y su error como segmentos ---------
        def segmentos_de(m, b):
            grupo = VGroup(*[
                Line(ejes.c2p(x, y), ejes.c2p(x, m * x + b),
                    color=C_PERDIDA, stroke_width=2.5)
                for x, y in zip(xs, ys)])
            grupo.set_stroke(opacity=0.6)
            return grupo

        m0, b0 = -0.4, -0.9
        recta = recta_modelo(ejes, m0, b0, color=C_ACENTO, grosor=3.5)
        self.play(Create(recta), run_time=1.0)
        segmentos = segmentos_de(m0, b0)
        self.play(Create(segmentos, lag_ratio=0.05), run_time=1.5)
        rot.mostrar(pie_curso("El error total: la suma de todas esas "
                             "distancias."), zona="abajo", run_time=0.5)
        self.wait(2.1)

        # --- momento: mini-eje de perdida a la derecha, sin tocar el plano -
        historial = entrenar_regresion(xs, ys, epocas=60, lr=0.08)
        mse_max = max(paso[2] for paso in historial) * 1.15
        mini_ejes = ejes_curva(x_max=1.0, x_min=0.0, y_max=mse_max,
                               y_min=0.0, x_length=3.2, y_length=2.4)
        mini_ejes.move_to(np.array([4.2, -1.2, 0.0]))
        tag_error = tag_eje(mini_ejes, "error", 0, mse_max, direccion=UP,
                           buff=0.12, font_size=16)
        self.play(Create(mini_ejes), FadeIn(tag_error), run_time=0.9)
        self.wait(1.0)

        # --- momento: entrenamiento -- la recta y la curva avanzan juntas --
        rot.mostrar(pie_curso("Cada paso: medir el error, corregir la "
                             "recta."), zona="abajo", run_time=0.5)
        self.wait(0.6)
        indices = [4, 12, 22, 34, 47, 59]
        curva = None
        for k in indices:
            m, b, _ = historial[k]
            nueva_recta = recta_modelo(ejes, m, b, color=C_ACENTO, grosor=3.5)
            nuevos_segmentos = segmentos_de(m, b)
            perdidas_parciales = [paso[2] for paso in historial[:k + 1]]
            nueva_curva = curva_perdida(mini_ejes, perdidas_parciales,
                                        color=C_PERDIDA, grosor=3.0)
            if curva is None:
                curva = nueva_curva
                self.play(Transform(recta, nueva_recta),
                         Transform(segmentos, nuevos_segmentos),
                         Create(curva), run_time=1.0)
            else:
                self.play(Transform(recta, nueva_recta),
                         Transform(segmentos, nuevos_segmentos),
                         Transform(curva, nueva_curva), run_time=0.8)
        self.wait(1.4)

        # --- momento: la formula del error medio -----------------------
        rot.mostrar(formula_pie(r"\text{MSE} = \tfrac{1}{n}\sum "
                               r"(y_i - \hat y_i)^2"), zona="abajo",
                   run_time=0.5)
        self.wait(2.7)

        # --- momento: cierre -- la recta ya ajustada -----------------------
        self.play(destello(recta, color=C_ACENTO, ancho=6, cola=0.4),
                  run_time=1.4)
        rot.mostrar(pie_curso("Esto es regresión: la forma más simple de "
                             "aprender."), zona="abajo", run_time=0.5)
        self.wait(3.0)
