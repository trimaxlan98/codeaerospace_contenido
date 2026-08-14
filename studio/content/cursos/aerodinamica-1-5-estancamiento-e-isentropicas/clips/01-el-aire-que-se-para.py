class Clip1(Scene):
    """1.5.1 - Definicion de T0, p0 y rho0.

    Antes de la formula, el sitio: la linea de corriente central muere en el
    morro del obstaculo, y ahi el aire no se desvia — se para. T0 no es una
    temperatura que exista en la corriente libre; es la que habria si la
    frenaras. Y el morro de un supersonico la nota. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El aire que se para")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la corriente encuentra un obstaculo -----------------
        flujo = remanso(radio=0.72, n_lineas=7, separacion=0.38, largo=2.9)
        flujo.move_to(LEFT * 1.5 + UP * 0.45)
        self.play(FadeIn(flujo.cuerpo), run_time=0.5)
        self.play(LaggedStart(*[Create(l) for l in flujo.lineas],
                              lag_ratio=0.16), run_time=2.0)
        rot.mostrar(pie_curso("Pon un obstáculo en la corriente. Casi todo "
                              "el aire lo esquiva."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        # --- momento: el punto donde no se esquiva ------------------------
        # El punto lo da la pieza (`flujo.punto()`), no una coordenada a ojo:
        # si el dibujo se mueve, el marcador va con el.
        punto = Dot(flujo.punto(), radius=0.08, color=C_SUPER)
        # El rotulo cuelga POR DEBAJO de todo el haz, no del punto: a media
        # altura cae justo sobre las lineas de corriente que rodean el
        # cuerpo, que es donde mas apretadas van.
        tag = Text("punto de remanso", font_size=19, color=C_SUPER)
        tag.move_to([punto.get_center()[0] - 0.20,
                     flujo.get_bottom()[1] - 0.42, 0])
        guia = DashedLine(punto.get_center() + DOWN * 0.10,
                          tag.get_top() + UP * 0.06, stroke_width=1.2,
                          color=C_SUPER, dash_length=0.06).set_opacity(0.6)

        self.play(FadeIn(punto, scale=1.8), run_time=0.5)
        self.play(Create(guia), FadeIn(tag, shift=0.1 * UP), run_time=0.6)
        rot.mostrar(pie_curso("Menos una línea. Esa no se desvía: se para "
                              "del todo."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Y su energía de movimiento no desaparece: se "
                              "le convierte en temperatura y en presión."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(formula_pie(r"T_0 = T\left(1 + \tfrac{\gamma-1}{2}"
                                r"M^2\right)"), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: cuanto es eso, en grados ----------------------------
        # Las dos cifras salen de isa() y razon_temperatura(): el rotulo no
        # puede discrepar del caso que se esta contando.
        fuera = Text(f"{T_VUELO - CERO_C:+.0f} °C", font=FUENTE_HUD,
                     font_size=21, color=C_CALCULO)
        fuera.move_to(flujo.get_left() + LEFT * 0.10 + UP * 1.55)
        morro = Text(f"{T0_MORRO - CERO_C:+.0f} °C", font=FUENTE_HUD,
                     font_size=24, color=C_SUPER)
        morro.move_to(RIGHT * 3.55 + UP * 0.15)
        eco = Text(f"M {M_VUELO:g}   ·   11 km", font=FUENTE_HUD,
                   font_size=16, color=C_TENUE).set_opacity(0.85)
        eco.next_to(morro, DOWN, buff=0.22)

        self.play(FadeIn(fuera, shift=0.1 * DOWN), run_time=0.6)
        self.play(FadeIn(VGroup(morro, eco), shift=0.12 * UP), run_time=0.7)
        rot.mostrar(pie_curso(f"A Mach {M_VUELO:g} y once kilómetros: fuera "
                              f"hace {CERO_C - T_VUELO:.0f} bajo cero y el "
                              f"morro va a {T0_MORRO - CERO_C:.0f} grados."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Eso es la temperatura de estancamiento. No "
                              "está en ningún sitio del aire: está en el "
                              "morro."), zona="abajo", run_time=0.5)
        self.wait(5.2)
