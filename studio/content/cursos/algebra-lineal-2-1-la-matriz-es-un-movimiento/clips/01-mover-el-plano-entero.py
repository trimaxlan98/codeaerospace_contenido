class Clip1(Scene):
    """2.1.1 - Una transformacion lineal mueve el plano ENTERO: la rejilla
    viva se deforma de forma continua sobre la fija, las rectas siguen
    rectas y paralelas, y el origen se queda clavado. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Mover el plano entero")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano, con su rejilla viva y su rejilla fija ------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.9)
        rot.mostrar(pie_curso("Hasta ahora movíamos flechas. Ahora movemos "
                              "el plano entero."), zona="abajo", run_time=0.5)
        origen = Dot(pl.p(0, 0), radius=0.085, color=C_TITULO)
        self.play(FadeIn(origen, scale=0.4), run_time=0.4)
        self.wait(4.8)

        # --- momento: dos rectas paralelas de testigo ----------------------
        # La libreria no trae un segmento del plano que sepa transformarse
        # (solo `recta`, que es y = m x + b y no se mueve), asi que aqui se
        # construyen a mano los dos extremos y sus imagenes bajo M.
        def segmento(centro, matriz=IDENTIDAD, opacidad=1.0):
            a = matriz @ (centro - RECTA_DIR)
            b = matriz @ (centro + RECTA_DIR)
            return Line(pl.p(a), pl.p(b), color=C_VEC, stroke_width=5.5,
                        stroke_opacity=opacidad)

        rot.mostrar(pie_curso("Dos rectas paralelas, para vigilarlas mientras "
                              "el plano se mueve."), zona="abajo",
                    run_time=0.5)
        r1 = segmento(RECTA_C1)
        r2 = segmento(RECTA_C2)
        self.play(Create(r1), Create(r2), run_time=0.9)
        self.wait(4.6)

        # --- momento: el movimiento ----------------------------------------
        rot.mostrar(pie_curso("Se deforma todo a la vez: las rectas siguen "
                              "rectas, y siguen paralelas."), zona="abajo",
                    run_time=0.5)
        self.wait(1.4)
        self.play(*pl.anim_matriz(M_LECCION),
                  Transform(r1, segmento(RECTA_C1, M_LECCION)),
                  Transform(r2, segmento(RECTA_C2, M_LECCION)),
                  run_time=2.2)
        self.wait(4.4)

        rot.mostrar(pie_curso("Ni se curvan ni se cruzan: giran y se abren, "
                              "las dos igual."), zona="abajo", run_time=0.5)
        self.play(Indicate(r1, color=C_VEC, scale_factor=1.06),
                  Indicate(r2, color=C_VEC, scale_factor=1.06), run_time=0.9)
        self.wait(4.4)

        # --- momento: el punto que no se mueve ------------------------------
        rot.mostrar(pie_curso("Y hay un punto que no se mueve nunca: el "
                              "origen."), zona="abajo", run_time=0.5)
        self.play(Indicate(origen, color=C_TITULO, scale_factor=2.2),
                  run_time=1.0)
        self.wait(4.2)

        rot.mostrar(pie_curso("Eso es una transformación lineal. ¿Cómo se "
                              "resume tanto movimiento?"), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)
