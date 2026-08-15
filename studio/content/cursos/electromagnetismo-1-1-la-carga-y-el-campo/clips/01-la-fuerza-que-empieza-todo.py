class Clip1(Scene):
    """1.1.1 - La ley de Coulomb: dos cargas se sienten sin tocarse, y la
    fuerza cae con el cuadrado de la distancia.

    Primero la pareja de cargas con sus flechas; despues la curva F(r) con
    los dos puntos medidos (1 m y 2 m) que hacen visible el 1/4. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La fuerza que empieza todo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: dos cargas que se sienten a distancia ---------------
        izq = carga(signo=+1)
        der = carga(signo=+1)
        izq.move_to(LEFT * 1.6 + DOWN * 0.3)
        der.move_to(RIGHT * 1.6 + DOWN * 0.3)
        f_izq = Arrow(izq.punto(), izq.punto() + LEFT * 1.1, buff=0.2,
                      color=C_CALCULO, stroke_width=4.0, tip_length=0.18)
        f_der = Arrow(der.punto(), der.punto() + RIGHT * 1.1, buff=0.2,
                      color=C_CALCULO, stroke_width=4.0, tip_length=0.18)

        self.play(FadeIn(izq, scale=1.4), FadeIn(der, scale=1.4),
                  run_time=0.7)
        rot.mostrar(pie_curso("Dos cargas se empujan sin tocarse. Todo "
                              "este curso sale de esa rareza."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        self.play(GrowArrow(f_izq), GrowArrow(f_der), run_time=0.7)
        rot.mostrar(formula_pie(r"F = k\,\frac{q_1\,q_2}{r^2}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la curva de la fuerza -------------------------------
        rot.mostrar(pie_curso("Con dos cargas de un microculombio, la "
                              "fuerza se puede dibujar."), zona="abajo",
                    run_time=0.5)
        curva = haz_curvas(
            [lambda r: coulomb(Q_PAREJA, Q_PAREJA, r) * 1000.0],
            (0.5, 3.0), [C_CALCULO], ancho=6.0, alto=2.9,
            etiqueta_x="distancia (m)", etiqueta_y="fuerza (mN)")
        curva.move_to(DOWN * 0.25)
        self.play(FadeOut(izq), FadeOut(der), FadeOut(f_izq),
                  FadeOut(f_der), FadeIn(curva.ejes), run_time=0.7)
        self.play(Create(curva.curva(0)), run_time=1.6)
        self.wait(2.8)

        # --- momento: el punto de 1 m -------------------------------------
        p1 = Dot(curva.punto_de(0, 1.0), radius=0.07, color=C_E)
        tag1 = tag_hud(f"{F_1M * 1000:.1f} mN a 1 m", font_size=17,
                       color=C_E)
        tag1.next_to(p1, UR, buff=0.14)
        rot.mostrar(pie_curso("A un metro: nueve milinewtons. Poca cosa, "
                              "pero medible."), zona="abajo", run_time=0.5)
        self.play(FadeIn(p1, scale=1.6), FadeIn(tag1, shift=0.1 * RIGHT),
                  run_time=0.6)
        self.wait(4.4)

        # --- momento: el doble de distancia -------------------------------
        p2 = Dot(curva.punto_de(0, 2.0), radius=0.07, color=C_CALCULO)
        tag2 = tag_hud(f"{F_2M * 1000:.1f} mN a 2 m", font_size=17)
        tag2.next_to(p2, UR, buff=0.14)
        # El pie va ANTES de la animacion que ilustra: el espectador debe
        # saber que esta mirando cuando aparece el punto.
        rot.mostrar(pie_curso("Al doble de distancia, la fuerza cae a la "
                              "cuarta parte. Ese es el cuadrado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(p2, scale=1.6), FadeIn(tag2, shift=0.1 * RIGHT),
                  run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("La misma ley del cuadrado gobernará la "
                              "señal de un satélite a 36 000 km."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Pero ¿qué hay entre las dos cargas? Ahí "
                              "empieza lo interesante."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
