class Clip3(Scene):
    """1.4.3 - Ecuacion de la energia en terminos de entalpia total.

    La barra apilada de altura fija es el clip entero: h0 no se mueve, y
    acelerar el flujo consiste literalmente en gastarse su temperatura. Los
    numeros de salida se calculan con las relaciones de la libreria, no a
    mano. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La entalpía total no se mueve")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        barras = barras_entalpia(M_ENTRADA, alto=2.7, ancho=1.0)
        barras.move_to(LEFT * 3.6 + DOWN * 0.35)
        self.play(FadeIn(barras), run_time=0.9)
        rot.mostrar(pie_curso("La barra entera es la entalpía total. Y esa "
                              "altura no va a cambiar en todo el clip."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        formula = MathTex(r"h + \frac{V^2}{2} = h_0 = c_p\,T_0",
                          font_size=44, color=C_TENUE)
        formula.move_to(RIGHT * 1.5 + UP * 1.30)
        self.play(Write(formula), run_time=1.1)
        rot.mostrar(pie_curso("Abajo, la parte térmica. Arriba, la de "
                              "movimiento."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: acelerar cuesta temperatura --------------------------
        tubo = conducto("divergente", area_garganta=AREA_GARGANTA, largo=4.6,
                        alto=1.7, color=C_TENUE)
        # Arriba lo justo para que las tres cifras de debajo no se peguen al
        # pie: con el conducto mas bajo quedaban a un dedo de la narracion.
        tubo.move_to(RIGHT * 1.6 + DOWN * 0.60)
        self.play(Create(tubo.paredes), FadeIn(tubo.eje), run_time=1.1)

        rot.mostrar(pie_curso("Acelera el flujo y la parte de arriba crece. "
                              "La de abajo tiene que ceder."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)
        self.play(barras.a_mach(1.0), run_time=1.2)
        self.wait(2.6)
        self.play(barras.a_mach(M_SALIDA), run_time=1.4)
        self.wait(2.8)

        # --- momento: el precio, en grados --------------------------------
        # T de salida y V de salida salen de razon_temperatura y de
        # velocidad_sonido: el rotulo no puede discrepar de la barra.
        cuentas = VGroup(
            Text(f"T0 = {T0_EJEMPLO:.0f} K", font=FUENTE_HUD, font_size=19,
                 color=C_CALCULO),
            Text(f"T = {T_SALIDA:.0f} K", font=FUENTE_HUD, font_size=19,
                 color=C_TRANS),
            Text(f"V = {V_SALIDA:.0f} m/s", font=FUENTE_HUD, font_size=19,
                 color=C_TRANS)).arrange(DOWN, aligned_edge=LEFT, buff=0.16)
        cuentas.next_to(tubo, DOWN, buff=0.26)
        self.play(FadeIn(cuentas, shift=0.12 * UP), run_time=0.8)
        rot.mostrar(pie_curso(f"Para llegar a Mach {M_SALIDA:g} el aire ha "
                              f"bajado de {T0_EJEMPLO:.0f} a "
                              f"{T_SALIDA:.0f} kelvin."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Una tobera no crea energía. Solo la cambia de "
                              "sitio."), zona="abajo", run_time=0.5)
        self.wait(4.8)
