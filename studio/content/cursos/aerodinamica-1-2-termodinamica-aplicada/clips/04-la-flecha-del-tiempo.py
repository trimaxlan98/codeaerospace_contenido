class Clip4(Scene):
    """1.2.4 - Segunda ley, entropia y el proceso isentropico.

    El plano T-s como brujula: la primera ley no distingue entre el proceso
    ideal y el real, y la segunda si. De aqui sale por que casi todo el curso
    puede escribirse con relaciones isentropicas — y por que el modulo 2
    tendra que romper esa comodidad. Cierre de la leccion. (~43 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La segunda ley: la flecha del tiempo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        ts = diagrama_ts(ancho=5.8, alto=3.2)
        ts.move_to(DOWN * 0.15)
        self.play(FadeIn(ts.ejes), run_time=0.7)

        # --- momento: el estado de partida ---------------------------------
        uno = ts.estado(0.22, 0.84, "1", color=C_TRANS)
        self.play(FadeIn(uno, scale=1.5), run_time=0.6)
        rot.mostrar(pie_curso("Un estado de partida: una temperatura y una "
                              "entropía."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: el camino ideal --------------------------------------
        rot.mostrar(pie_curso("Si la expansión fuese adiabática y reversible, "
                              "la entropía no cambiaría."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)
        ideal = ts.trayecto([(0.22, 0.84), (0.22, 0.30)], color=C_SUB)
        dos_s = ts.estado(0.22, 0.30, "2s", color=C_SUB, direccion=DOWN)
        self.play(Create(ideal), run_time=1.0)
        self.play(FadeIn(dos_s, scale=1.4), run_time=0.5)
        self.wait(3.2)

        rot.mostrar(pie_curso("Baja recta. Eso es un proceso isentrópico."),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: el camino real ---------------------------------------
        rot.mostrar(pie_curso("Ningún proceso real es reversible: siempre "
                              "deriva hacia la derecha."), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)
        real = ts.trayecto([(0.22, 0.84), (0.40, 0.62), (0.60, 0.44)],
                           color=C_SUPER, punteado=True)
        dos = ts.estado(0.60, 0.44, "2", color=C_SUPER, direccion=RIGHT)
        self.play(Create(real), run_time=1.1)
        self.play(FadeIn(dos, scale=1.4), run_time=0.5)
        self.wait(3.0)

        rot.mostrar(formula_pie(r"\Delta s \geq 0", color=C_SUPER),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("A la izquierda no se va nunca. Esa es toda la "
                              "segunda ley."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion -------------------------------------------
        self.play(FadeOut(VGroup(ts, uno, ideal, dos_s, real, dos)),
                  run_time=0.8)
        cierre = VGroup(
            titulo_marca("Casi todo este curso es isentrópico.", font_size=36,
                         color=C_TITULO),
            titulo_marca("Salvo cuando aparece un choque.", font_size=36,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.2)
