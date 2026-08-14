class Clip4(Scene):
    """4.5.4 - Introduccion al regimen hipersonico y al calentamiento
    aerodinamico.

    El aviso final: mas alla de Mach 5 el modelo de gas ideal que ha
    sostenido todo el curso empieza a mentir. La temperatura de
    estancamiento que sale de la formula es tan alta que el aire ya no puede
    ser aire — se disocia, y absorbe energia haciendolo. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cuando el aire deja de ser aire")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(pie_curso("Coge la relación de estancamiento de la "
                              "lección 1.5 y métele Mach 10."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)

        cuenta = VGroup(
            MathTex(rf"T_0 = T\left(1 + \tfrac{{\gamma-1}}{{2}}"
                    rf"M^2\right)", font_size=42, color=C_TENUE),
            MathTex(rf"T_0 = {T_HIPER:.0f} \cdot "
                    rf"{float(razon_temperatura(M_HIPER)):.0f} = "
                    rf"{T0_HIPER:.0f}\ \mathrm{{K}}", font_size=46,
                    color=C_HIPER)).arrange(DOWN, buff=0.40)
        cuenta.move_to(UP * 0.95)
        self.play(Write(cuenta[0]), run_time=1.0)
        self.wait(2.6)
        self.play(FadeIn(cuenta[1], shift=0.12 * UP), run_time=0.8)
        rot.mostrar(pie_curso(f"{T0_HIPER:.0f} kelvin. Cuatro mil grados "
                              "centígrados en el morro."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: lo que pasa de verdad ---------------------------------
        rot.mostrar(pie_curso("Pero eso no ocurre. Y no porque la fórmula "
                              "esté mal."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # Escalera de lo que le pasa al aire al calentarse.
        etapas = VGroup(
            Text("1500 K   las moléculas empiezan a vibrar", font_size=19,
                 color=C_TRANS),
            Text("2500 K   el oxígeno se disocia", font_size=19,
                 color=C_SUPER),
            Text("4000 K   el nitrógeno se disocia", font_size=19,
                 color=C_HIPER),
            Text("9000 K   el aire se ioniza", font_size=19,
                 color=C_HIPER)).arrange(DOWN, aligned_edge=LEFT, buff=0.20)
        etapas.move_to(DOWN * 1.35)
        self.play(LaggedStart(*[FadeIn(e, shift=0.10 * UP) for e in etapas],
                              lag_ratio=0.3), run_time=1.6)
        rot.mostrar(pie_curso("Es que gamma deja de valer 1.4. El aire gasta "
                              "energía en romperse en vez de en "
                              "calentarse."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        rot.mostrar(pie_curso("Todo el curso ha supuesto un gas ideal con "
                              "gamma constante. Aquí esa suposición se "
                              "acaba."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        rot.mostrar(pie_curso("Y empieza otra asignatura."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
