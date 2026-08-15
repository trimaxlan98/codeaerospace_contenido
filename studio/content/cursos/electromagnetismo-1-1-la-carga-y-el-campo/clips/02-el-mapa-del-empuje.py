class Clip2(Scene):
    """1.1.2 - El campo electrico: el mapa del empuje que existe aunque no
    haya nadie que lo sienta.

    Una carga sola y sus lineas integradas; despues entra la segunda y el
    mapa entero se recompone, con su punto de equilibrio en el centro.
    (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El campo: el mapa del empuje")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la carga sola y su mapa ------------------------------
        sola = lineas_campo([(1.0, 0.0, -0.1)], n_lineas=10)
        self.play(FadeIn(sola.cargas, scale=1.3), run_time=0.6)
        rot.mostrar(pie_curso("Quita la segunda carga. ¿Qué queda? "
                              "Faraday dijo: queda un mapa."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        self.play(Create(sola.lineas), FadeIn(sola.flechas), run_time=1.8)
        rot.mostrar(pie_curso("En cada punto del espacio hay una flecha "
                              "esperando: eso es el campo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(formula_pie(r"\vec{E} = \frac{\vec{F}}{q}"),
                    zona="abajo", run_time=0.5)
        etiqueta = tag_hud(f"{E_1M:.0f} V/m a 1 m de 1 uC", font_size=16)
        etiqueta.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(etiqueta, shift=0.1 * DOWN), run_time=0.5)
        self.wait(4.4)

        # --- momento: entra la segunda y el mapa se recompone --------------
        rot.mostrar(pie_curso("Con dos cargas, los mapas no se pisan: se "
                              "SUMAN, flecha a flecha."), zona="abajo",
                    run_time=0.5)
        doble = lineas_campo([(1.0, -1.5, -0.1), (1.0, 1.5, -0.1)],
                             n_lineas=10)
        self.play(ReplacementTransform(sola, doble), FadeOut(etiqueta),
                  run_time=1.6)
        self.wait(3.6)

        # El punto de equilibrio del centro no se marca a ojo: es el punto
        # medio exacto de las dos cargas, donde la suma se cancela.
        centro = Dot((doble.cargas[0].punto() + doble.cargas[1].punto())
                     / 2.0, radius=0.09, color=C_CALCULO)
        rot.mostrar(pie_curso("Justo en medio, los dos empujes se "
                              "cancelan: hay un punto quieto."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(centro, scale=2.0), run_time=0.6)
        self.wait(4.4)

        rot.mostrar(pie_curso("El campo es el verdadero protagonista: "
                              "las cargas solo lo encienden."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
