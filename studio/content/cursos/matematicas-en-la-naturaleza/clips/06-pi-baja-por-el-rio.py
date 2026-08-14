class Clip6(Scene):
    """6 - Pi baja por el rio. El rio joven casi recto envejece hasta
    serpentear; la sinuosidad se MIDE sobre la curva y ronda pi. Cada
    curva se abraza con su arco de circunferencia. Con caveat. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("π baja por el río")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el rio joven va casi recto --------------------------
        rot.mostrar(pie_curso("Un río joven va casi recto: camino y "
                              "distancia miden casi lo mismo."),
                    zona="abajo", run_time=0.5)
        rio = rio_meandro(OMEGA_JOVEN, ancho=6.9)
        rio.move_to(UP * 0.3)
        self.play(Create(rio), run_time=1.6)

        a, b = rio.extremos()
        cuerda = DashedLine(a, b, stroke_width=2.2, color=C_CONSTANTE)
        cuerda.set_stroke(opacity=0.8)
        self.play(Create(cuerda), run_time=0.8)

        medida = tag_hud(f"sinuosidad = {rio.sinuosidad():.2f}",
                         font_size=17)
        medida.move_to(LEFT * 4.3 + UP * 2.55)
        rot.mostrar(medida, zona="medida", run_time=0.4)
        self.wait(3.4)

        # --- momento: al envejecer, serpentea -----------------------------
        rot.mostrar(pie_curso("Al envejecer, serpentea: cada curva es casi "
                              "un arco de circunferencia."), zona="abajo",
                    run_time=0.5)
        rio_medio = rio.con_omega(OMEGA_MEDIO)
        self.play(Transform(rio, rio_medio), run_time=1.4)
        medida2 = tag_hud(f"sinuosidad = {rio.sinuosidad():.2f}",
                          font_size=17)
        medida2.move_to(LEFT * 4.3 + UP * 2.55)
        rot.mostrar(medida2, zona="medida", run_time=0.4)
        self.wait(1.2)

        rio_pi = rio.con_omega(OMEGA_PI_DEG)
        self.play(Transform(rio, rio_pi), run_time=1.6)
        medida3 = tag_hud(f"sinuosidad = {rio.sinuosidad():.2f}",
                          font_size=17, color=C_CONSTANTE)
        medida3.move_to(LEFT * 4.3 + UP * 2.55)
        rot.mostrar(medida3, zona="medida", run_time=0.4)

        arco0 = rio.arco_ajustado(1)
        arco1 = rio.arco_ajustado(2)
        self.play(Create(arco0), Create(arco1), run_time=1.2)
        self.wait(2.6)

        # --- momento: el promedio ronda pi, y es promedio -----------------
        rot.mostrar(pie_curso("En promedio, sobre muchos ríos maduros, la "
                              "sinuosidad ronda π. Ningún río está "
                              "obligado."), zona="abajo", run_time=0.5)
        self.wait(5.2)
        formula = formula_pie(r"\frac{\text{camino}}{\text{recta}}\ "
                              r"\approx\ \pi", font_size=38,
                              color=C_CONSTANTE)
        rot.mostrar(formula, zona="abajo", run_time=0.5)
        self.wait(5.4)
