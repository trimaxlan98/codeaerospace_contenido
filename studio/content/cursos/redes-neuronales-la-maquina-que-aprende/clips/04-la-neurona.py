class Clip4(Scene):
    """4 - La neurona. El esquema minimo: dos entradas, dos pesos, una
    suma y una sigmoide que decide. Abajo, la unica figura que una
    neurona sabe dibujar: una recta."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("La neurona")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(1.0)

        # --- momento: dos entradas ------------------------------------------
        centro_y = 0.95
        x1 = MathTex(r"x_1", color=C_DATO_A, font_size=32)
        x1.move_to(LEFT * 3.4 + UP * (centro_y + 0.25))
        x2 = MathTex(r"x_2", color=C_DATO_A, font_size=32)
        x2.move_to(LEFT * 3.4 + UP * (centro_y - 0.25))
        self.play(FadeIn(x1, shift=0.15 * RIGHT),
                  FadeIn(x2, shift=0.15 * RIGHT), run_time=0.8)

        # --- momento: el nodo de suma ----------------------------------------
        suma = Circle(radius=0.35, color=C_ACENTO, stroke_width=3)
        suma.move_to(LEFT * 0.7 + UP * centro_y)
        suma_lbl = MathTex(r"\Sigma", color=C_TITULO, font_size=30)
        suma_lbl.move_to(suma.get_center())
        self.play(Create(suma), FadeIn(suma_lbl), run_time=0.7)

        # --- momento: aristas con pesos, pegados sin tocar los circulos -----
        arista_x1 = conectar(x1, suma, color=C_ACENTO, grosor=2.5)
        arista_x2 = conectar(x2, suma, color=C_ACENTO, grosor=2.5)
        w1 = MathTex(r"w_1", color=C_ACENTO, font_size=20)
        w1.next_to(arista_x1.point_from_proportion(0.5), UP, buff=0.08)
        w2 = MathTex(r"w_2", color=C_ACENTO, font_size=20)
        w2.next_to(arista_x2.point_from_proportion(0.5), DOWN, buff=0.08)
        self.play(GrowArrow(arista_x1), GrowArrow(arista_x2), run_time=0.6)
        self.play(FadeIn(w1), FadeIn(w2), run_time=0.4)
        self.wait(0.6)

        # --- momento: la caja sigmoide con su curva en miniatura ------------
        caja = bloque("σ", ancho=1.3, alto=0.85, color=C_ACENTO,
                     color_texto=C_TITULO, tamano=24)
        caja.move_to(RIGHT * 1.3 + UP * centro_y)
        caja[1].shift(0.2 * UP)
        mini_curva = ParametricFunction(
            lambda t: np.array([0.4 * t, 0.16 * (2 / (1 + np.exp(-6 * t))
                                                 - 1), 0.0]),
            t_range=[-1, 1, 0.05], color=C_ACENTO, stroke_width=2.5)
        mini_curva.move_to(caja.get_center() + 0.18 * DOWN)
        arista_caja = conectar(suma, caja, color=C_ACENTO, grosor=2.5)
        self.play(Create(caja), run_time=0.7)
        self.play(Create(mini_curva), GrowArrow(arista_caja), run_time=0.9)

        # --- momento: la salida ----------------------------------------------
        y_hat = MathTex(r"\hat y", color=C_TITULO, font_size=32)
        y_hat.move_to(RIGHT * 3.2 + UP * centro_y)
        arista_salida = conectar(caja, y_hat, color=C_ACENTO, grosor=2.5)
        self.play(GrowArrow(arista_salida), FadeIn(y_hat, shift=0.15 * RIGHT),
                  run_time=0.6)
        self.wait(0.8)

        # --- momento: el pulso que recorre la red de entrada a salida -------
        self.play(flujo([arista_x1, arista_x2, arista_caja, arista_salida],
                        color=C_DATO_A, ancho=5, cola=0.45,
                        por_conexion=0.55))
        self.wait(0.4)
        rot.mostrar(pie_curso("Pesa cada prueba, suma, y decide."),
                   zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- momento: la unica figura que dibuja una neurona -----------------
        plano = ejes_plano(lado=3.0)
        plano.move_to(np.array([0.0, -1.3, 0.0]))
        X, y = datos_dos_nubes(n=60, separacion=1.5, semilla=7)
        puntos = puntos_datos(plano, X, y)
        frontera = recta_modelo(plano, -1.0, 0.0, color=C_ACENTO, grosor=3.5)
        self.play(Create(plano), run_time=1.0)
        self.play(FadeIn(puntos, lag_ratio=0.05), run_time=1.3)
        self.play(Create(frontera), run_time=1.0)
        self.wait(2.0)

        rot.mostrar(pie_curso("Toda neurona traza una única línea recta."),
                   zona="abajo", run_time=0.5)
        self.wait(1.9)
        rot.mostrar(formula_pie(r"\hat y = \sigma(w_1 x_1 + w_2 x_2 + b)"),
                   zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- momento: cierre -- gancho para el muro de XOR -------------------
        rot.mostrar(pie_curso("¿Y si una recta no basta?"), zona="abajo",
                   run_time=0.5)
        self.wait(3.1)
