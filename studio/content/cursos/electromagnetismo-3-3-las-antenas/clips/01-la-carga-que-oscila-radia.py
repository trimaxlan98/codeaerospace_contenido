class Clip1(Scene):
    """3.3.1 - La carga que oscila radia: el dipolo del modulo 1, por fin
    alimentado. Acelerar cargas suelta frentes separados exactamente una
    longitud de onda; a media onda la antena resuena. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La carga que oscila radia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el dipolo del 1.1, ahora con generador ---------------
        dra = dipolo_radiante(largo_brazo=0.3, n_frentes=3, lam=1.2)
        # Las cargas del dibujo se recolocan SOBRE los brazos de esta
        # escala (la pieza las deja en la escala por defecto).
        for punto, y in zip(dra.cargas, (0.26, 0.40, -0.26, -0.40)):
            punto.move_to((0.0, y, 0.0))
        dra.move_to(DOWN * 0.1)
        self.play(FadeIn(dra.brazos, scale=1.2), FadeIn(dra.alimentacion),
                  run_time=0.7)
        rot.mostrar(pie_curso("El dipolo del módulo 1, con un generador "
                              "al centro. Hoy, por fin, se mueve."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: las cargas oscilan -----------------------------------
        rot.mostrar(pie_curso("La corriente alterna sacude las cargas "
                              "millones de veces por segundo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(dra.cargas, scale=1.5), run_time=0.5)
        arriba, abajo = dra.cargas[:2], dra.cargas[2:]
        self.play(*[p.animate(rate_func=there_and_back).shift(UP * 0.07)
                    for p in arriba],
                  *[p.animate(rate_func=there_and_back).shift(DOWN * 0.07)
                    for p in abajo], run_time=1.3)
        self.play(*[p.animate(rate_func=there_and_back).shift(DOWN * 0.07)
                    for p in arriba],
                  *[p.animate(rate_func=there_and_back).shift(UP * 0.07)
                    for p in abajo], run_time=1.3)
        self.wait(1.8)

        # --- momento: los frentes se sueltan -------------------------------
        rot.mostrar(pie_curso("Cada aceleración sacude al campo, y la "
                              "sacudida se suelta: la antena RADIA."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(dra.frente(0), scale=0.5), run_time=0.7)
        self.play(FadeIn(dra.frente(1), scale=0.75), run_time=0.7)
        self.play(FadeIn(dra.frente(2), scale=0.85), run_time=0.7)
        self.wait(2.6)

        # --- momento: la separacion es exactamente lambda ------------------
        rot.mostrar(pie_curso("Entre frente y frente hay exactamente una "
                              "longitud de onda."), zona="abajo",
                    run_time=0.5)
        seg = Line(dra.frente(0).get_right(), dra.frente(1).get_right())
        b_lam = Brace(seg, DOWN, color=C_CALCULO)
        et_lam = MathTex(r"\lambda", font_size=30, color=C_CALCULO)
        et_lam.next_to(b_lam, DOWN, buff=0.10)
        self.play(FadeIn(b_lam), FadeIn(et_lam), run_time=0.6)
        self.wait(4.4)

        # --- momento: la resonancia de media onda --------------------------
        rot.mostrar(pie_curso("Con cada brazo de un cuarto de onda, la "
                              "antena RESUENA: traga potencia a gusto."),
                    zona="abajo", run_time=0.5)
        b_cuarto = Brace(dra.brazos[0], RIGHT, color=C_CALCULO)
        et_cuarto = MathTex(r"\lambda/4", font_size=26, color=C_CALCULO)
        et_cuarto.next_to(b_cuarto, RIGHT, buff=0.10)
        self.play(FadeIn(b_cuarto), FadeIn(et_cuarto), run_time=0.6)
        self.wait(4.4)

        # --- momento: la cifra de la FM ------------------------------------
        rot.mostrar(pie_curso("En la radio FM ese dipolo mide metro y "
                              "medio: la antena clásica del tejado."),
                    zona="abajo", run_time=0.5)
        tag_fm = tag_hud(f"{F_FM / 1e6:.0f} MHz -> dipolo de "
                         f"{LARGO_DIPOLO_FM:.1f} m", font_size=17)
        tag_fm.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(tag_fm, shift=0.1 * LEFT), run_time=0.6)
        self.wait(4.4)

        rot.mostrar(pie_curso("Acelerar cargas radia. Toda antena es una "
                              "manera de acelerarlas con intención."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
