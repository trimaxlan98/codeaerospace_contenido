class Clip2(Scene):
    """3.1.2 - Invariancia de la componente tangencial.

    Por que la tangencial no cambia: la unica fuerza que actua a traves del
    choque es la presion, y la presion empuja PERPENDICULAR a la onda. Sin
    fuerza a lo largo, no hay cambio de cantidad de movimiento a lo largo.
    Una linea de razonamiento, y de ahi sale medio modulo. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La que no cambia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        onda = onda_oblicua(M_RAMPA, THETA_RAMPA, largo=3.4, entrada=2.4)
        onda.move_to(DOWN * 0.60)
        self.play(FadeIn(VGroup(onda.pared, onda.choque)), run_time=0.7)
        self.play(FadeIn(onda.vectores), run_time=0.9)
        rot.mostrar(pie_curso("¿Por qué la componente de lado no se entera "
                              "de nada?"), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: la unica fuerza que hay ------------------------------
        # Flechas de presion, perpendiculares a la onda por los dos lados.
        b = np.deg2rad(onda.beta())
        normal = np.array([np.sin(b), -np.cos(b), 0.0])
        # En gris y no en ambar: el ambar es el FLUJO en toda la familia, y
        # estas flechas son una fuerza. Y a partir del 40 % de la onda, que
        # mas abajo cruzan la rampa.
        empujes = VGroup()
        for k in (0.42, 0.62, 0.82):
            base = onda.esquina() + np.array([np.cos(b), np.sin(b), 0.0]) * (
                3.4 * k)
            empujes.add(Arrow(base + normal * 0.58, base + normal * 0.10,
                              buff=0, stroke_width=2.2, color=C_TENUE,
                              max_tip_length_to_length_ratio=0.30))
            empujes.add(Arrow(base - normal * 0.58, base - normal * 0.10,
                              buff=0, stroke_width=2.2, color=C_TENUE,
                              max_tip_length_to_length_ratio=0.30))
        self.play(FadeIn(empujes), run_time=0.8)
        rot.mostrar(pie_curso("A través de la onda solo actúa una fuerza: la "
                              "presión."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Y la presión empuja perpendicular a la "
                              "superficie. Siempre."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("No hay ninguna fuerza a lo largo de la onda."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"V_{t2} = V_{t1}", color=C_SUB),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("Sin fuerza no hay cambio de cantidad de "
                              "movimiento. Eso es todo el argumento."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
