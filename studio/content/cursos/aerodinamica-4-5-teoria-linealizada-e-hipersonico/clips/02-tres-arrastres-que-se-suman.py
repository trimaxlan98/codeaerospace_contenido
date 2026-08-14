class Clip2(Scene):
    """4.5.2 - Arrastre de onda por espesor, curvatura y sustentacion.

    Lo que la linealizacion regala y la teoria exacta no puede dar: los tres
    origenes del arrastre de onda salen SEPARADOS y se suman. Y eso convierte
    el diseño en una cuenta, no en un tanteo. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Tres arrastres que se suman")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        formula = MathTex(r"c_d = \frac{4}{\sqrt{M_\infty^2 - 1}}"
                          r"\left(\alpha^2 + \overline{\epsilon^2} + "
                          r"\overline{\kappa^2}\right)", font_size=48,
                          color=C_SUPER)
        formula.move_to(UP * 1.55)
        self.play(Write(formula), run_time=1.4)
        rot.mostrar(pie_curso("El arrastre de onda tiene tres orígenes, y la "
                              "teoría linealizada los separa."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # Tres columnas con su cuota. Los numeros salen de `ackeret` con el
        # caso del modulo 3, asi que el clip compara peras con peras.
        casos = (("ángulo de ataque", ROMBO_ACK["cd_sustentacion"], C_TRANS),
                 ("espesor", ROMBO_ACK["cd_espesor"], C_SUB),
                 ("curvatura", 0.0, C_CALCULO))
        columnas = VGroup()
        for nombre, valor, color in casos:
            columnas.add(VGroup(
                Text(nombre, font_size=20, color=color),
                Text(f"{valor:.4f}", font=FUENTE_HUD, font_size=24,
                     color=color)).arrange(DOWN, buff=0.16))
        columnas.arrange(RIGHT, buff=1.15).move_to(DOWN * 0.45)

        pies = ("El ángulo de ataque: el precio de sustentar.",
                "El espesor: el precio de que el perfil ocupe sitio.",
                "Y la curvatura, que en un rombo simétrico es cero.")
        for columna, pie in zip(columnas, pies):
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(columna, shift=0.12 * UP), run_time=0.7)
            self.wait(4.4)

        # --- momento: la suma -----------------------------------------------
        suma = MathTex(rf"c_d = {ROMBO_ACK['cd']:.4f}", font_size=40,
                       color=C_SUPER)
        suma.move_to(DOWN * 1.95)
        self.play(FadeIn(suma, shift=0.12 * UP), run_time=0.7)
        rot.mostrar(pie_curso("Se suman sin mezclarse. Y eso convierte el "
                              "diseño en una cuenta."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Puedes decidir cuánto espesor te puedes "
                              "permitir. La teoría exacta no te deja "
                              "separarlo."), zona="abajo", run_time=0.5)
        self.wait(5.4)
