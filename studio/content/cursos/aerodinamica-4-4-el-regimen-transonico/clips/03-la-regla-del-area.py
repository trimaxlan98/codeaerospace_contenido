class Clip3(Scene):
    """4.4.3 - Regla del area y su efecto en el arrastre de onda.

    La tercera solucion, y la mas contraintuitiva: al aire transonico no le
    importa donde esta cada pieza, solo cuanta SECCION encuentra estacion a
    estacion. Si el ala mete un bulto, quitalo del fuselaje. Y sale un avion
    con cintura. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La regla del área")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        area = distribucion_area(ancho=5.4, alto=2.5)
        area.move_to(LEFT * 0.65 + DOWN * 0.45)
        self.play(FadeIn(area.ejes), run_time=0.6)
        rot.mostrar(pie_curso("Cuánta sección transversal encuentra el aire, "
                              "a lo largo del avión."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        self.play(Create(area.aporte), FadeIn(area.etiquetas[2]),
                  run_time=0.9)
        rot.mostrar(pie_curso("El ala aporta esto: una campana justo en el "
                              "centro."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        self.play(Create(area.sin_regla), FadeIn(area.etiquetas[0]),
                  run_time=1.0)
        # La cifra sale de la pieza: es el pico medido contra el fuselaje en
        # esa misma estacion, no un numero de adorno.
        rot.mostrar(pie_curso(f"Y sumado al fuselaje deja un bulto de un "
                              f"{area.bulto() * 100:.0f} %."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Al aire transónico eso le parece un obstáculo "
                              "que aparece y desaparece de golpe."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- momento: quitarlo del fuselaje ---------------------------------
        self.play(Create(area.con_regla), FadeIn(area.etiquetas[1]),
                  run_time=1.0)
        rot.mostrar(pie_curso("Así que estrecha el fuselaje exactamente lo "
                              "que el ala añade."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("La curva vuelve a ser lisa. Y el arrastre de "
                              "onda cae en picado."), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("El precio es un avión con cintura de avispa. "
                              "Y eso es exactamente lo que se construyó."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
