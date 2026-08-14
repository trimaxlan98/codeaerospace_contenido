class Clip1(Scene):
    """2.5.1 - Tobera convergente: bloqueo sonico (choked flow).

    Baja la presion de salida y el gasto sube... hasta que deja de subir.
    A partir de ahi la garganta va a Mach 1 y ninguna noticia de aguas abajo
    puede remontar la corriente. La tobera deja de escuchar. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La tobera que deja de escuchar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tubo = conducto("convergente", area_garganta=AREA_GARGANTA,
                        largo=5.0, alto=2.0, color=C_TENUE)
        tubo.move_to(UP * 1.15)
        self.play(Create(tubo.paredes), FadeIn(tubo.eje), run_time=1.1)
        rot.mostrar(pie_curso("Un depósito a presión y un tubo que se "
                              "estrecha. Baja la presión de fuera y el aire "
                              "sale más rápido."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # --- momento: el gasto que se planta -------------------------------
        # El eje horizontal es la presion de salida, de 1 (nada de flujo) a
        # 0 (vacio). El gasto sube hasta la presion critica y ahi se planta.
        ancho, alto = 5.4, 1.9
        ejes = VGroup(Line(LEFT * ancho / 2, RIGHT * ancho / 2,
                           stroke_width=2.0, color=C_EJE),
                      Line(LEFT * ancho / 2, LEFT * ancho / 2 + UP * alto,
                           stroke_width=2.0, color=C_EJE))
        ejes.move_to(DOWN * 1.55)
        base = ejes[0].get_start()

        def punto(p_rel, gasto_rel):
            """p_rel = 1 a la izquierda, 0 a la derecha."""
            return base + np.array([(1 - p_rel) * ancho, gasto_rel * alto, 0])

        # Rama que sube (sin bloquear) y meseta (bloqueada), a la presion
        # critica que da la libreria — no un sitio elegido a ojo.
        ps = np.linspace(1.0, P_CRITICA, 60)
        gastos = np.sqrt(np.clip(1 - (ps / 1.0) ** 0.6, 0, 1))
        gastos = gastos / gastos.max()
        rama = VMobject(color=C_CALCULO, stroke_width=3.0)
        rama.set_points_smoothly([punto(p, g) for p, g in zip(ps, gastos)])
        meseta = Line(punto(P_CRITICA, 1.0), punto(0.0, 1.0),
                      stroke_width=3.0, color=C_SUPER)
        corte = DashedLine(punto(P_CRITICA, 0.0), punto(P_CRITICA, 1.12),
                           stroke_width=1.4, color=C_EJE, dash_length=0.07)
        tag_g = Text("gasto", font=FUENTE_HUD, font_size=15, color=C_EJE)
        tag_g.next_to(ejes[1], UP, buff=0.10)
        tag_p = Text("presion de salida  ->  menos", font=FUENTE_HUD,
                     font_size=14, color=C_EJE)
        tag_p.next_to(ejes[0], DOWN, buff=0.16)

        self.play(FadeIn(ejes), FadeIn(tag_g), FadeIn(tag_p), run_time=0.6)
        self.play(Create(rama), run_time=1.4)
        rot.mostrar(pie_curso("Cuanto más bajas la presión de fuera, más "
                              "aire sale. Hasta aquí, lo esperable."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        self.play(Create(corte), Create(meseta), run_time=1.0)
        rot.mostrar(pie_curso("Y entonces se planta. Puedes hacer el vacío "
                              "ahí fuera: no sale ni un gramo más."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: por que -----------------------------------------------
        garganta = Line(tubo.punto_de(1.0, -1.0), tubo.punto_de(1.0, 1.0),
                        stroke_width=3.2, color=C_SUPER)
        tag_m1 = Text("M = 1", font=FUENTE_HUD, font_size=20, color=C_SUPER)
        tag_m1.next_to(garganta, UP, buff=0.16)
        self.play(Create(garganta), FadeIn(tag_m1), run_time=0.7)
        rot.mostrar(pie_curso("En la garganta el aire ya va a Mach 1."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Y una noticia que viaja a la velocidad del "
                              "sonido no puede remontar una corriente que "
                              "va igual de rápido."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)

        rot.mostrar(pie_curso(f"Por debajo de {P_CRITICA:.4f} de la presión "
                              "del depósito, la tobera deja de enterarse."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
