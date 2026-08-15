class Clip4(Scene):
    """2.1.4 - La regla con vueltas: modular el haz y medir la fase de
    la modulacion. A 10 MHz la vuelta mide 15 m; subir a 100 MHz afina
    la regla a 1.5 m pero acorta la vuelta: se combinan varias
    frecuencias. Cierra el modulo: el tiempo mide lejos, la fase mide
    fino. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La regla con vueltas"),
                    zona="arriba", run_time=0.6)

        # --- momento: se modula el haz -----------------------------------------
        rot.mostrar(pie_curso("Otra forma: modular el haz y medir la "
                              "fase de la modulación."), zona="abajo",
                    run_time=0.5)
        regla = regla_ambiguedad(f_mod=10e6, rango_m=45.0)
        regla.scale(0.92).move_to(np.array([0.0, -0.20, 0.0]))
        self.play(Create(regla.eje), FadeIn(regla.rotulos), run_time=0.6)
        self.play(Create(regla.onda), run_time=1.1)
        self.play(FadeIn(regla.marcas), FadeIn(regla.lectura),
                  FadeIn(regla.llave), run_time=0.6)
        self.wait(2.5)

        # --- momento: la vuelta mide 15 m ---------------------------------------
        rot.mostrar(pie_curso("La fase da la distancia dentro de una "
                              "vuelta; la vuelta mide c sobre dos f: "
                              "quince metros."), zona="abajo", run_time=0.5)
        formula = MathTex(r"L = \frac{c}{2f}", font_size=34,
                          color=C_MEDIDA)
        formula.move_to(np.array([-4.6, 1.9, 0.0]))
        cifra_10 = tag_hud(f"10 MHz -> {AMBIG_10MHZ_M:.0f} m", font_size=16,
                           color=C_MEDIDA)
        cifra_10.move_to(np.array([-4.6, 1.35, 0.0]))
        self.play(Write(formula), run_time=1.0)
        self.play(FadeIn(cifra_10, shift=0.10 * UP), run_time=0.5)
        self.wait(3.0)

        # --- momento: subir a 100 MHz --------------------------------------------
        rot.mostrar(pie_curso("Subir la frecuencia afina la regla, pero "
                              "acorta la vuelta: metro y medio."),
                    zona="abajo", run_time=0.5)
        gemela = regla.con_frecuencia(100e6)
        self.play(Transform(regla, gemela), run_time=1.6)
        cifra_100 = tag_hud(f"100 MHz -> {AMBIG_100MHZ_M:.1f} m",
                            font_size=16, color=C_MEDIDA)
        cifra_100.next_to(cifra_10, DOWN, buff=0.18, aligned_edge=LEFT)
        varias = tag_hud("varias frecuencias resuelven la vuelta",
                         font_size=13, color=C_TENUE)
        varias.move_to(np.array([0.0, -1.95, 0.0]))
        self.play(FadeIn(cifra_100, shift=0.10 * UP), run_time=0.5)
        self.play(FadeIn(varias), run_time=0.5)
        self.wait(5.0)

        # --- cierre: pantalla limpia ---------------------------------------------
        self.play(FadeOut(regla), FadeOut(formula), FadeOut(cifra_10),
                  FadeOut(cifra_100), FadeOut(varias), run_time=0.7)
        rot.limpiar("arriba", run_time=0.4)
        rot.limpiar("abajo", run_time=0.4)
        linea1 = Text("El tiempo mide lejos.", font_size=40, color=C_ONDA)
        linea2 = Text("La fase mide fino.", font_size=40, color=C_ONDA)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(7.5)
