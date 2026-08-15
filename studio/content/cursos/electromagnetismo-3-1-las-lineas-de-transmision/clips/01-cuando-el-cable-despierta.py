class Clip1(Scene):
    """3.1.1 - Cuando el cable despierta: el mismo cable a 50 Hz (la onda
    es, a esa escala, una recta) y a 1 GHz (caben varias ondas enteras).

    De ahi sale la regla: si el cable mide mas de lambda/10, ya no es un
    cable, es una linea de transmision — cada punto vive en un instante
    distinto de la señal. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Cuando el cable despierta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el cable a 50 Hz, la onda es casi una recta ---------
        rot.mostrar(pie_curso("Este es un cable cualquiera, y esta es la "
                              "señal de la red electrica dentro."),
                    zona="abajo", run_time=0.5)
        cable = cable_onda(largo=6.0, lam=48.0, amplitud=0.42,
                           color_onda=C_ONDA)
        cable.move_to(UP * 0.3)
        self.play(FadeIn(cable.cable), FadeIn(cable.extremos), run_time=0.7)
        self.play(Create(cable.onda), run_time=1.2)
        self.wait(4.6)

        etiqueta_50 = tag_hud(f"50 Hz  ->  lambda = {LAMBDA_RED_KM:.0f} km",
                              font_size=17)
        etiqueta_50.next_to(cable, DOWN, buff=0.55)
        rot.mostrar(pie_curso("A cincuenta hercios, esa onda mide seis mil "
                              "kilometros: en los pocos metros de un cable "
                              "de andar por casa, es sencillamente una "
                              "recta."), zona="abajo", run_time=0.5)
        self.play(FadeIn(etiqueta_50, shift=0.1 * UP), run_time=0.6)
        self.wait(4.8)

        # --- momento: sube la frecuencia a 1 GHz ---------------------------
        rot.mostrar(pie_curso("Sube la frecuencia a un gigahercio y el "
                              "MISMO cable ya no ve una recta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(etiqueta_50), run_time=0.4)
        nuevo = cable.con_lambda(1.2)
        self.play(ReplacementTransform(cable, nuevo), run_time=1.6)
        cable = nuevo
        self.wait(3.6)

        etiqueta_giga = tag_hud(
            f"1 GHz  ->  {cable.ondas_dentro():.0f} ondas completas "
            "dentro del cable", font_size=17)
        etiqueta_giga.next_to(cable, DOWN, buff=0.55)
        rot.mostrar(pie_curso("Ahora caben varias ondas ENTERAS dentro "
                              "del mismo trozo de cable."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(etiqueta_giga, shift=0.1 * UP), run_time=0.6)
        self.wait(4.6)

        # --- momento: la regla ----------------------------------------------
        rot.mostrar(formula_pie(r"\ell > \frac{\lambda}{10}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Cada punto del cable vive entonces en un "
                              "instante distinto de la misma señal."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
