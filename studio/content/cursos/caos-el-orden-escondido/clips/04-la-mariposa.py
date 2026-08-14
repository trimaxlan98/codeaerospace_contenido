class Clip4(Scene):
    """4 - La mariposa. Las tres ecuaciones de Lorenz y su atractor
    dibujandose entero: salta de un ala a la otra sin repetirse y sin
    cortarse. Un objeto, no una curva. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La mariposa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el clima en tres ecuaciones -------------------------
        rot.mostrar(pie_curso("1963: Edward Lorenz destila el clima a tres "
                              "ecuaciones de juguete."), zona="abajo",
                    run_time=0.5)
        ecuaciones = MathTex(
            r"\dot{x} = \sigma(y - x)\\"
            r"\dot{y} = x(\rho - z) - y\\"
            r"\dot{z} = xy - \beta z",
            font_size=26, color=C_TENUE)
        ecuaciones.move_to(LEFT * 5.0 + UP * 1.9)
        self.play(Write(ecuaciones), run_time=1.6)
        self.wait(1.8)

        # --- momento: la trayectoria que no se repite ---------------------
        rot.mostrar(pie_curso("La trayectoria salta de un ala a la otra "
                              "sin repetirse jamás."), zona="abajo",
                    run_time=0.5)
        pts = trayectoria_lorenz(n=12000)
        mariposa = curva_lorenz(pts, alto=4.9, color=C_SISTEMA, grosor=1.9)
        mariposa.move_to(RIGHT * 0.65 + DOWN * 0.3)
        mariposa.set_stroke(opacity=0.92)
        self.play(Create(mariposa), run_time=10.0, rate_func=linear)
        self.wait(2.4)

        # --- momento: un objeto, no una curva -----------------------------
        rot.mostrar(pie_curso("No es una curva: es un objeto — un atractor "
                              "extraño."), zona="abajo", run_time=0.5)
        etiqueta = tag_junto(mariposa, "atractor extraño", DOWN, buff=0.30,
                             font_size=19, color=C_FASE)
        self.play(FadeIn(etiqueta, shift=0.15 * UP), run_time=0.7)
        self.wait(9.2)
