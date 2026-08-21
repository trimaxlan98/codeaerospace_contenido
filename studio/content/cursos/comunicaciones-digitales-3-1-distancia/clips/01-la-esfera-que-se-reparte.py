class Clip1(Scene):
    """3.1.1 - La esfera que se reparte: la potencia de la sonda no viaja
    en un rayo, se reparte sobre una esfera que crece con la distancia;
    doblar la distancia cuesta 6 dB -- MEDIDO con fspl_db. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La esfera que se reparte")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la senal sale de la sonda ----------------------------
        rot.mostrar(pie_curso("Una sonda dispara su senal rumbo a la "
                              "Tierra: el vacio no la frena ni la absorbe."),
                    zona="abajo", run_time=0.5)
        enl = enlace_tierra(dist=3.4, radio_tierra=0.42, curva=0.28)
        enl.rotate(PI)  # la nave a la izquierda, la Tierra a la derecha
        enl.move_to(DOWN * 1.9 + RIGHT * 2.6)
        # el camino nace en la Tierra: para ir sonda -> Tierra se invierte
        cam_ida = enl.camino.copy().reverse_points()
        paq = enl.paquete(radio=0.06)
        paq.move_to(cam_ida.point_from_proportion(0.0))
        self.play(FadeIn(enl), run_time=0.8)
        self.play(PulsoDeSenal(paq, cam_ida, rate_func=linear),
                  destello(enl.camino, color=C_SENAL), run_time=1.5)
        self.wait(3.4)

        # --- momento: la potencia se reparte en una esfera ------------------
        rot.mostrar(pie_curso("Pero no viaja en un rayo: se reparte sobre "
                              "una esfera que crece (corte plano de esa "
                              "esfera, aqui)."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(enl), FadeOut(paq), run_time=0.6)
        fuente = Dot(LEFT * 4.6, radius=0.09, color=C_BIT)
        et_fuente = tag_junto(fuente, "la senal", direccion=UP, buff=0.12)
        anillo1 = Circle(radius=1.3, color=C_SENAL, stroke_width=2.6,
                         stroke_opacity=0.9).move_to(fuente)
        anillo2 = Circle(radius=2.6, color=C_SENAL, stroke_width=2.2,
                         stroke_opacity=0.55).move_to(fuente)
        anillo3 = Circle(radius=3.9, color=C_SENAL, stroke_width=1.8,
                         stroke_opacity=0.3).move_to(fuente)
        self.play(FadeIn(fuente), FadeIn(et_fuente), run_time=0.4)
        self.play(LaggedStart(Create(anillo1), Create(anillo2),
                              Create(anillo3), lag_ratio=0.55), run_time=2.6)
        self.wait(3.4)

        # --- momento: doblar la distancia, medir el costo --------------------
        rot.mostrar(pie_curso("Doblar la distancia multiplica esa esfera "
                              "por cuatro: la senal por metro cuadrado cae "
                              "6 dB -- medido."),
                    zona="abajo", run_time=0.5)
        self.play(anillo1.animate.set_stroke(color=C_CIFRA, opacity=1.0),
                  anillo2.animate.set_stroke(color=C_CIFRA, opacity=0.85),
                  run_time=1.0)
        panel = panel_derecha(
            tag_hud(f"d = {fmt(D_LEO, 0)} km", font_size=17,
                    color=C_CIFRA),
            tag_hud(f"FSPL = {fmt(FSPL_LEO, 1)} dB", font_size=17,
                    color=C_CIFRA),
            tag_hud(f"d = {fmt(D_LEO_DOBLE, 0)} km", font_size=17,
                    color=C_CIFRA),
            tag_hud(f"FSPL = {fmt(FSPL_LEO_DOBLE, 1)} dB", font_size=17,
                    color=C_CIFRA),
            tag_hud(f"delta = {fmt(DELTA_DOBLE_DB, 1)} dB", font_size=19,
                    color=C_CIFRA),
            buff=0.16)
        self.play(FadeIn(panel, shift=0.15 * UP), run_time=0.7)
        self.wait(4.4)

        # --- momento: la formula --------------------------------------------
        rot.mostrar(formula_pie(r"\mathrm{FSPL}_{dB} = 92.45 + 20\log_{10} d"
                                r" + 20\log_{10} f"), zona="abajo",
                    run_time=0.5)
        self.wait(6.6)
