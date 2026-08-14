class Clip5(Scene):
    """5 - Las rayas del gato. Gray-Scott en vivo: el ruido se organiza en
    manchas; dos perillas lo vuelven rayas; y el gato sentado se viste con
    el campo recien calculado. Leopardo y atigrado, misma ecuacion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Las rayas del gato")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: dos quimicos que se persiguen -----------------------
        rot.mostrar(pie_curso("1952: Alan Turing propone que dos químicos "
                              "que se persiguen pueden pintar la piel."),
                    zona="abajo", run_time=0.5)
        centro_campo = UP * 0.35
        cuadros = secuencia_turing(*TURING_MANCHAS, cuadros=7,
                                   pasos=TURING_PASOS)
        f_m, k_m = TURING_MANCHAS
        params = tag_hud(f"F {f_m:.4f}   K {k_m:.4f}", font_size=15,
                         color=C_QUIMICA)
        params.move_to(RIGHT * 4.35 + UP * 2.6)
        rot.mostrar(params, zona="params", run_time=0.4)

        previo = None
        for campo, pausa in zip(cuadros[:2], (2.2, 1.6)):
            img = imagen_turing(campo, alto_escena=4.3)
            img.move_to(centro_campo)
            if previo is None:
                self.play(FadeIn(img), run_time=0.6)
            else:
                self.add(img)
                self.remove(previo)
            previo = img
            self.wait(pausa)

        # --- momento: donde el freno no alcanza, nace una mancha ----------
        rot.mostrar(pie_curso("Uno activa, el otro frena: donde el freno "
                              "no alcanza, nace una mancha."), zona="abajo",
                    run_time=0.5)
        for campo in cuadros[2:]:
            img = imagen_turing(campo, alto_escena=4.3)
            img.move_to(centro_campo)
            self.add(img)
            self.remove(previo)
            previo = img
            self.wait(0.72)
        self.wait(2.4)

        # --- momento: dos perillas separan al leopardo de la cebra --------
        rot.mostrar(pie_curso("Dos perillas separan al leopardo de la "
                              "cebra."), zona="abajo", run_time=0.5)
        f_r, k_r = TURING_RAYAS
        params_r = tag_hud(f"F {f_r:.4f}   K {k_r:.4f}", font_size=15,
                           color=C_QUIMICA)
        params_r.move_to(RIGHT * 4.35 + UP * 2.6)
        rot.mostrar(params_r, zona="params", run_time=0.4)
        campo_rayas = campo_turing(*TURING_RAYAS, pasos=TURING_PASOS)
        rayas = imagen_turing(campo_rayas, alto_escena=4.3)
        rayas.move_to(centro_campo)
        self.play(FadeIn(rayas), run_time=0.9)
        self.remove(previo)
        self.wait(3.6)

        # --- momento: el gato trae puesta la solucion ---------------------
        rot.mostrar(pie_curso("Tu gato trae puesta la solución de una "
                              "ecuación."), zona="abajo", run_time=0.5)
        self.play(FadeOut(rayas), run_time=0.6)

        gato_r = gato_sentado(escala=1.32)
        gato_r.move_to(LEFT * 2.3 + UP * 0.15)
        pelaje_r = imagen_turing(campo_rayas, color_fondo=C_PELAJE,
                                 color_tinta=C_TINTA, silueta=gato_r)
        atigrado = Group(gato_r, pelaje_r)

        campo_manchas = cuadros[-1]
        gato_m = gato_sentado(escala=1.32)
        gato_m.move_to(RIGHT * 2.3 + UP * 0.15)
        pelaje_m = imagen_turing(campo_manchas, color_fondo=C_PELAJE,
                                 color_tinta=C_TINTA, silueta=gato_m)
        moteado = Group(gato_m, pelaje_m).flip()
        moteado.move_to(RIGHT * 2.3 + UP * 0.15)

        etiqueta_r = tag_junto(gato_r, "atigrado", DOWN, buff=0.30,
                               font_size=18)
        etiqueta_m = tag_junto(moteado, "moteado", DOWN, buff=0.30,
                               font_size=18)
        self.play(FadeIn(atigrado, shift=0.2 * UP), FadeIn(etiqueta_r),
                  run_time=1.0)
        self.play(FadeIn(moteado, shift=0.2 * UP), FadeIn(etiqueta_m),
                  run_time=1.0)
        self.wait(6.4)
