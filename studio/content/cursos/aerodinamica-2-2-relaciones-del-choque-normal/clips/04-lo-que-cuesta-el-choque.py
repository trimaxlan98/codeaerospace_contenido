class Clip4(Scene):
    """2.2.4 - Perdida de presion de estancamiento y generacion de entropia.

    La entalpia total se conserva a traves del choque; la presion de
    estancamiento NO. Esa perdida es el precio, y se paga en entropia. Es el
    numero que decide si una toma de aire supersonica sirve o no. Cierre de
    la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Lo que cuesta el choque")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curvas = curvas_choque(grupo="perdidas", m_max=M_MAX_CURVAS,
                               ancho=5.0, alto=2.7)
        curvas.move_to(LEFT * 0.55 + DOWN * 0.35)
        self.play(FadeIn(curvas.ejes), run_time=0.6)
        self.play(*[Create(c) for c in curvas.curvas], run_time=1.6)
        self.play(FadeIn(curvas.etiquetas), run_time=0.6)

        rot.mostrar(pie_curso("La entalpía total cruza el choque intacta: no "
                              "entra calor ni sale trabajo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("La presión de estancamiento, no. Esa se "
                              "pierde, y no se recupera."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: cuanto se pierde -------------------------------------
        corte = curvas.vertical_en(M1_REF, color=C_TENUE)
        punto = Dot(curvas.punto_de(1, M1_REF), radius=0.075, color=C_SUPER)
        cifra = Text(f"{SALTO['p02/p01']:.4f}", font=FUENTE_HUD,
                     font_size=19, color=C_SUPER)
        cifra.move_to([curvas.ejes[1].get_left()[0] - 0.62,
                       punto.get_center()[1], 0])
        self.play(Create(corte), run_time=0.5)
        self.play(FadeIn(punto, scale=1.6), FadeIn(cifra), run_time=0.6)
        rot.mostrar(pie_curso(f"A Mach {M1_REF:g} se pierde el "
                              f"{(1 - SALTO['p02/p01']) * 100:.0f} % de la "
                              "presión de estancamiento."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso(f"A Mach {M_MAX_CURVAS:g}, el "
                              f"{(1 - choque_normal(M_MAX_CURVAS)['p02/p01']) * 100:.0f} %. "
                              "Y la curva sigue cayendo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Por eso la toma de aire de un supersónico no "
                              "usa un choque fuerte, sino varios flojos."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(curvas, corte, punto, cifra)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Un choque no destruye energía.", font_size=36,
                         color=C_TITULO),
            titulo_marca("Destruye la capacidad de usarla.", font_size=36,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
