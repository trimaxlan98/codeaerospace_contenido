class Clip1(Scene):
    """2.3.1 - Tubo de Pitot en regimen subsonico compresible.

    Un Pitot no mide velocidad: mide la presion del aire que ha parado
    contra su boca. Traducir esa presion a velocidad exige saber cuanto se
    comprime al pararse — y eso es exactamente la relacion de estancamiento
    de la leccion 1.5. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El Pitot y la compresibilidad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # Se reutiliza el remanso de la leccion 1.5: la boca de un Pitot es
        # un punto de remanso con un manometro detras, ni mas ni menos.
        flujo = remanso(radio=0.55, n_lineas=5, separacion=0.34, largo=2.4)
        flujo.move_to(LEFT * 2.6 + UP * 0.55)
        boca = Dot(flujo.punto(), radius=0.075, color=C_SUPER)

        self.play(FadeIn(flujo), run_time=0.8)
        self.play(FadeIn(boca, scale=1.6), run_time=0.5)
        rot.mostrar(pie_curso("Un tubo de Pitot no mide velocidad. Mide la "
                              "presión del aire que ha parado en su boca."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(formula_pie(r"\frac{p_0}{p} = "
                                r"\left(1 + \tfrac{\gamma-1}{2}M^2\right)"
                                r"^{3.5}"), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Esa es la relación de la lección 1.5, leída al "
                              "revés: de la presión al Mach."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: el mismo avion de la leccion 1.3 ---------------------
        tarjeta = VGroup(
            Text(f"V = {V_TAS:.0f} m/s", font=FUENTE_HUD, font_size=21,
                 color=C_TENUE),
            Text(f"M = {M_TAS:.2f}", font=FUENTE_HUD, font_size=26,
                 color=C_TRANS),
            Text(f"p0/p = {razon_presion(M_TAS):.3f}", font=FUENTE_HUD,
                 font_size=21, color=C_CALCULO)).arrange(DOWN, buff=0.20)
        tarjeta.move_to(RIGHT * 3.2 + UP * 0.55)
        self.play(FadeIn(tarjeta, shift=0.12 * UP), run_time=0.8)
        rot.mostrar(pie_curso(f"El avión de la lección 1.3, a "
                              f"{V_TAS:.0f} metros por segundo y once "
                              "kilómetros."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso(f"Su Pitot lee {razon_presion(M_TAS):.2f} veces "
                              "la presión de fuera. No el doble de nada "
                              "sencillo."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Sin compresibilidad, ese número no se traduce "
                              "bien a velocidad."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
