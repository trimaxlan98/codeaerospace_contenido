class Clip2(Scene):
    """1.5.2 - Relaciones T0/T, p0/p y rho0/rho en funcion de M y gamma.

    Las tres razones son la MISMA razon elevada a tres exponentes distintos,
    y los exponentes no son arbitrarios: salen de exigir que el frenado sea
    isentropico. De ahi que la presion caiga mas rapido que la densidad y la
    densidad mas rapido que la temperatura. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Tres razones, un solo número")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # La pieza es ancha por su columna de etiquetas: se centra por su
        # caja y queda ligeramente a la izquierda, que es donde hace falta.
        curvas = curvas_isentropicas(m_max=3.0, ancho=5.4, alto=2.7)
        curvas.move_to(DOWN * 0.35)
        self.play(FadeIn(curvas.ejes), run_time=0.6)

        rot.mostrar(pie_curso("Frena el flujo hasta pararlo. ¿Cuánto suben "
                              "las tres propiedades?"), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)
        self.play(LaggedStart(*[Create(c) for c in curvas.curvas],
                              lag_ratio=0.35), run_time=2.2)
        self.play(FadeIn(curvas.etiquetas), run_time=0.7)
        self.wait(2.4)

        # --- momento: las tres formulas -----------------------------------
        rot.mostrar(formula_pie(r"\frac{T_0}{T} = 1 + "
                                r"\tfrac{\gamma-1}{2}M^2"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"\frac{\rho_0}{\rho} = "
                                r"\left(\frac{T_0}{T}\right)^{2.5}"
                                r"\qquad "
                                r"\frac{p_0}{p} = "
                                r"\left(\frac{T_0}{T}\right)^{3.5}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("La misma razón, elevada a tres exponentes "
                              "distintos."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Y los exponentes no son arbitrarios: salen de "
                              "exigir que el frenado sea isentrópico."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: quien cae mas rapido --------------------------------
        # El orden de la lectura es el orden de los exponentes, y el grafico
        # lo enseña sin que haya que decirlo.
        rot.mostrar(pie_curso("Por eso la presión se desploma antes que la "
                              "densidad, y la densidad antes que la "
                              "temperatura."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # El porcentaje sale de la misma curva que se esta mirando (indice 2
        # = p/p0), no de la memoria.
        rot.mostrar(pie_curso(f"A Mach 3 solo queda un "
                              f"{curvas.valor(2, 3.0) * 100:.0f} % de la "
                              "presión de estancamiento."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
