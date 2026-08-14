class Clip1(Scene):
    """1.1.1 - Limitaciones del modelo incompresible: el criterio M < 0.3.

    La curva del error de densidad crece sola; encima cae el umbral del 5 %
    que la ingenieria tolera, y de ahi sale la banda verde. El 0.3 de los
    libros no se postula: se lee del corte. (~44 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("¿Cuándo deja de valer «incompresible»?")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la hipotesis que traiamos de Aerodinamica I ---------
        curva = curva_compresibilidad(ancho=6.6, alto=3.05)
        curva.move_to(DOWN * 0.20)

        self.play(FadeIn(curva.ejes), run_time=0.6)
        rot.mostrar(pie_curso("Aerodinámica I dio por buena una hipótesis: "
                              "que la densidad del aire no cambia."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: cuanto miente esa hipotesis -------------------------
        self.play(Create(curva.curva), run_time=2.0)
        rot.mostrar(pie_curso("Al frenar contra el vehículo, el aire se "
                              "comprime. Esto es cuánto."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(formula_pie(r"\frac{\rho_0}{\rho} = "
                                r"\left(1 + \tfrac{\gamma-1}{2}M^2\right)"
                                r"^{\frac{1}{\gamma-1}}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # --- momento: el umbral que la ingenieria tolera ------------------
        # El pie va ANTES de la animacion que ilustra: si entra despues, el
        # espectador ve el corte sin saber todavia que esta mirando.
        rot.mostrar(pie_curso("La ingeniería tolera un 5 % de error. "
                              "¿Hasta qué Mach se cumple?"), zona="abajo",
                    run_time=0.5)
        self.play(Create(curva.umbral), FadeIn(curva.etiquetas[0]),
                  run_time=0.8)
        self.wait(4.2)

        # El corte lo pone la libreria: la banda verde y el rotulo del Mach
        # salen del mismo `mach_de_error(0.05)` que dibuja la curva.
        self.play(FadeIn(curva.banda), FadeIn(curva.etiquetas[1]),
                  run_time=0.9)
        corte = Dot(curva.punto_de(M_UMBRAL), radius=0.07, color=C_SUB)
        self.play(FadeIn(corte, scale=1.6), run_time=0.5)
        rot.mostrar(pie_curso(f"Hasta Mach {M_UMBRAL:.2f}. Ese es el "
                              "verdadero origen de la regla del 0.3."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: al otro lado del umbral -----------------------------
        alto = Dot(curva.punto_de(M_CRUCERO), radius=0.07, color=C_TRANS)
        # El rotulo va a la IZQUIERDA del punto: a la derecha se sale del
        # encuadre y encima queda pegado a la etiqueta del 5 %.
        tag = Text(f"{ERR_CRUCERO * 100:.0f} %", font=FUENTE_HUD,
                   font_size=20, color=C_TRANS)
        tag.next_to(alto, LEFT, buff=0.18)

        self.play(FadeIn(alto, scale=1.6), FadeIn(tag, shift=0.1 * RIGHT),
                  run_time=0.7)
        rot.mostrar(pie_curso("A Mach 0.8 —un vuelo de línea— la densidad "
                              "cambia un tercio."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Ahí ya no hay hipótesis que valga: empieza "
                              "otra aerodinámica."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
