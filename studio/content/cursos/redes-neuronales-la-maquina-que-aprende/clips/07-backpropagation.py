class Clip7(Scene):
    """7 - Backpropagation: el error viaja de vuelta. Una pasada hacia
    adelante que produce un error, la señal que recorre la red al reves
    repartiendo culpas entre los pesos, y los pesos que se corrigen un
    poco: la esencia de como aprende una red neuronal profunda."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo -------------------------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("El error viaja de vuelta")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)

        # --- La red: 2 entradas, dos capas ocultas de 4, una salida --------
        red = RedNeuronal(capas=(2, 4, 4, 1), color_neurona=C_DATO_A,
                          color_conexion=C_EJE)
        red.shift(0.35 * UP)
        self.play(Create(red), run_time=2.5)
        self.wait(1.0)

        # --- Acto 1: hacia adelante nace una prediccion y un error ---------
        self.play(red.activacion(color=C_DATO_A))
        error = MathTex(r"\text{error}", font_size=26, color=C_PERDIDA)
        error.next_to(red.capas_neuronas[-1][0], RIGHT, buff=0.22)
        self.play(FadeIn(error, shift=0.12 * RIGHT), run_time=0.5)
        rot.mostrar(pie_curso("Hacia adelante: una predicción. Y una "
                              "medida del error."), zona="abajo",
                   run_time=0.5)
        self.wait(2.1)

        # --- Acto 2: hacia atras el error reparte culpas --------------------
        self.play(retropropagacion(red, color=C_PERDIDA))
        rot.mostrar(pie_curso("Hacia atrás: el error reparte culpas entre "
                              "los pesos."), zona="abajo", run_time=0.5)
        self.wait(2.1)

        # --- La etiqueta de error se retira antes del acto final -----------
        self.play(FadeOut(error), run_time=0.4)
        self.wait(0.5)

        # --- Acto 3: los pesos se corrigen (algunos engordan, otros ceden) -
        engordan = [red.conexiones[1][0], red.conexiones[1][5],
                    red.conexiones[1][10], red.conexiones[2][0],
                    red.conexiones[2][2]]
        adelgazan = [red.conexiones[1][3], red.conexiones[1][12],
                     red.conexiones[0][2]]
        self.play(
            *[c.animate.set_stroke(width=6.5, color=C_ACENTO, opacity=0.95)
              for c in engordan],
            *[c.animate.set_stroke(width=0.5, opacity=0.12)
              for c in adelgazan],
            run_time=1.6,
        )
        rot.mostrar(pie_curso("Cada peso se corrige un poco. Eso es "
                              "aprender."), zona="abajo", run_time=0.5)
        self.wait(2.0)
        rot.mostrar(formula_pie(r"w \leftarrow w - \eta \, "
                                r"\frac{\partial E}{\partial w}"),
                   zona="abajo", run_time=0.5)
        self.wait(2.1)

        # --- Cierre: hacia adelante otra vez, ahora mas segura -------------
        self.play(red.activacion(color=C_DATO_A, ancho=7.5))
        rot.mostrar(pie_curso("Repítelo un millón de veces: así se entrena "
                              "una red."), zona="abajo", run_time=0.5)
        self.wait(2.8)
