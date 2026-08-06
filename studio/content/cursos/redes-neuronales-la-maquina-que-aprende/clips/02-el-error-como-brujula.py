class Clip2(Scene):
    """2 - El error como brujula. Una bola ambar desciende la parabola de
    perdida salto a salto hasta el minimo; una segunda bola, con un paso
    demasiado grande, diverge y sale del cuadro: la tasa de aprendizaje
    es la diferencia entre aprender y explotar."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD de modulo y titulo -------------------------------------
        modulo = hud_modulo("Modulo 02")
        titulo = titulo_curso("El error como brújula")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.8)

        # --- El paisaje de error: una parabola ------------------------------
        def f(x):
            return 0.55 * x ** 2

        def df(x):
            return 1.1 * x

        ejes = ejes_curva()
        self.play(Create(ejes), run_time=1.3)

        parabola = ejes.plot(f, x_range=[-2.0, 2.0, 0.02], color=C_TENUE,
                             stroke_width=3)
        self.play(Create(parabola), run_time=1.6)

        tag_error = tag_eje(ejes, "error", 0.0, 2.0, direccion=UP)
        tag_parametro = tag_eje(ejes, "parámetro", 2.0, 0.0,
                                direccion=RIGHT)
        self.play(FadeIn(VGroup(tag_error, tag_parametro)), run_time=0.7)
        self.wait(1.9)

        # --- Bajar la cuesta, salto a salto ----------------------------------
        xs1 = descenso_1d(df, x0=1.8, lr=0.3, pasos=8)
        bola, saltos = camino_descenso(ejes, f, xs1, color=C_ACENTO)
        self.play(FadeIn(bola, scale=0.5), run_time=0.5)
        rot.mostrar(pie_curso("El error es un paisaje: aprender es bajar "
                              "la cuesta."), zona="abajo", run_time=0.5)

        for k, salto in enumerate(saltos):
            x_k = xs1[k]
            tangente = Line(
                ejes.c2p(x_k - 0.35, f(x_k) - 0.35 * df(x_k)),
                ejes.c2p(x_k + 0.35, f(x_k) + 0.35 * df(x_k)),
                color=C_ACENTO, stroke_width=2.5,
            )
            tangente.set_opacity(0.85)
            self.play(FadeIn(tangente), run_time=0.3)
            self.play(FadeOut(tangente), run_time=0.25)
            self.play(Create(salto), MoveAlongPath(bola, salto),
                      run_time=0.6)
        self.wait(1.7)

        # --- La regla del paso -----------------------------------------------
        rot.mostrar(formula_pie(r"x_{k+1} = x_k - \eta \, f'(x_k)"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- Segundo acto: un paso demasiado grande ----------------------------
        # lr=2.0 -> factor -1.2 por paso: diverge de verdad pero despacio,
        # y arrancando en x0=0.55 los 6 saltos caben DENTRO del eje
        # (f(1.64)=1.49 < y_max=2): la curva roja jamas pisa titulo ni HUD.
        xs2 = descenso_1d(df, x0=0.55, lr=2.0, pasos=6)
        bola_2, saltos_2 = camino_descenso(ejes, f, xs2, color=C_PERDIDA)
        self.play(FadeIn(bola_2, scale=0.5), run_time=0.5)
        rot.mostrar(pie_curso("Con pasos demasiado grandes, el "
                              "aprendizaje explota."), zona="abajo",
                    run_time=0.5)

        for salto in saltos_2:
            self.play(Create(salto), MoveAlongPath(bola_2, salto),
                      run_time=0.65)
        self.wait(1.3)

        # --- La bola diverge y se retira ------------------------------------
        self.play(FadeOut(VGroup(bola_2, saltos_2), shift=0.4 * UP),
                  run_time=0.7)

        # --- Cierre: elegir el paso es un arte -------------------------------------
        rot.mostrar(pie_curso("Elegir el tamaño del paso es un arte: se "
                              "llama tasa de aprendizaje."), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
