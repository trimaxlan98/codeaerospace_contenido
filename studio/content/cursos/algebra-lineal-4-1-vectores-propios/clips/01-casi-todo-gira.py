class Clip1(Scene):
    """4.1.1 - Una transformacion saca de su recta a casi todas las
    direcciones; dos se quedan exactamente donde estaban. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Casi todo gira")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un abanico de direcciones -----------------------------
        pl = plano_leccion()
        abanico = [vector(pl, c, color=C_VEC, grosor=4.0, punta_len=0.18)
                   for c in ABANICO]
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un abanico de direcciones sobre la rejilla. "
                              "Ocho flechas, ocho rumbos."),
                    zona="abajo", run_time=0.5)
        self.play(*[GrowArrow(v.flecha) for v in abanico], run_time=1.0)
        self.wait(3.8)

        # --- momento: la matriz que las va a mover --------------------------
        rot.mostrar(pie_curso(
            "Esta matriz manda î a (" + fmt(A_PROPIA[0, 0], 0) + ", "
            + fmt(A_PROPIA[1, 0], 0) + ") y ĵ a (" + fmt(A_PROPIA[0, 1], 0)
            + ", " + fmt(A_PROPIA[1, 1], 0) + ")."),
            zona="abajo", run_time=0.5)
        mat = matriz_columnas(A_PROPIA, font_size=40)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.0)

        # --- momento: la rejilla se deforma y arrastra a las flechas --------
        rot.mostrar(pie_curso("Aplicada al plano entero: mira cómo se "
                              "deforma la rejilla."),
                    zona="abajo", run_time=0.5)
        self.play(*pl.anim_matriz(A_PROPIA, *abanico), run_time=2.0)
        self.wait(3.0)

        # --- momento: casi todas salieron de su carril ----------------------
        rot.mostrar(pie_curso("Casi todas cambiaron de rumbo: esta se salió "
                              "de su recta."), zona="abajo", run_time=0.5)
        # (el abanico[5] va a 110 grados: su recta de partida es oblicua y
        # no se confunde con los ejes del plano, como pasaria con 0 o 90)
        carril = span_recta(pl, ABANICO[5], color=C_TENUE, opacidad=0.75,
                            grosor=3.0)
        self.play(Create(carril), run_time=0.8)
        self.play(Indicate(abanico[5], color=C_VEC, scale_factor=1.06),
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: las dos que no giraron --------------------------------
        rot.mostrar(pie_curso("Menos dos. Estas siguen en su recta: solo "
                              "cambió su largo."), zona="abajo", run_time=0.5)
        self.play(FadeOut(carril), run_time=0.3)
        rectas = VGroup(span_recta(pl, DIR_ESTIRA, color=C_PROPIO,
                                   opacidad=0.6),
                        span_recta(pl, DIR_QUIETA, color=C_PROPIO,
                                   opacidad=0.6))
        self.play(Create(rectas), run_time=1.2)
        # Ojo: los mobjects del abanico conservan sus coords de partida (el
        # Transform de anim_matriz no las toca), asi que A @ coords es justo
        # donde estan ahora en pantalla. Se re-crean gruesas y en fucsia
        # (con_matriz hereda el grosor, y aqui interesa que resalten).
        propios = [vector(pl, A_PROPIA @ abanico[k].coords, color=C_PROPIO,
                          grosor=6.5, punta_len=0.24)
                   for k in INDICES_PROPIOS]
        self.play(*[Transform(abanico[k], nuevo)
                    for k, nuevo in zip(INDICES_PROPIOS, propios)],
                  run_time=0.9)
        self.wait(3.4)

        rot.mostrar(pie_curso("Se llaman direcciones propias. Son el "
                              "esqueleto de la transformación."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
