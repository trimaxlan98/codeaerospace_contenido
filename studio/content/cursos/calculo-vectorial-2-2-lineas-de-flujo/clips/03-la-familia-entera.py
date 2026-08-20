class Clip3(Scene):
    """2.2.3 - Sueltas MUCHAS particulas a la vez, no una: la familia de
    lineas de flujo retrata el remolino amortiguado mejor que las
    flechas solas — todas caen en espiral al centro. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La familia entera")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: otro campo, un remolino que se apaga ------------------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_REMOLINO, paso=0.9, escala=0.4)
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Otro campo: un remolino que se va "
                              "apagando hacia el centro."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(campo), run_time=1.0)
        self.wait(2.6)

        # --- momento: muchas semillas a la vez -------------------------------------
        rot.mostrar(pie_curso("Ahora no sueltes una partícula: suelta "
                              "MUCHAS, repartidas alrededor."), zona="abajo",
                    run_time=0.5)
        semillas = VGroup(*[Dot(pl.p(np.array(s)), radius=0.07, color=C_VEC)
                            for s in SEMILLAS_REMOLINO])
        self.play(LaggedStart(*[FadeIn(s, scale=0.5) for s in semillas],
                              lag_ratio=0.15), run_time=1.6)
        self.wait(1.6)

        # --- momento: cada una traza su linea de flujo ------------------------------
        rot.mostrar(pie_curso("Cada una sigue su propia línea de "
                              "flujo, tangente al campo local."),
                    zona="abajo", run_time=0.5)
        lineas = [linea_flujo(pl, CAMPO_REMOLINO, s, T=T_REMOLINO)
                 for s in SEMILLAS_REMOLINO]
        anims = [AnimationGroup(Create(lf), MoveAlongPath(dot, lf))
                for lf, dot in zip(lineas, semillas)]
        self.play(LaggedStart(*anims, lag_ratio=0.12), run_time=5.6,
                  rate_func=linear)
        self.wait(1.8)

        # --- momento: todas caen en espiral al centro -------------------------------
        rot.mostrar(pie_curso("Todas caen en espiral hacia el mismo "
                              "centro: el remolino se amortigua."),
                    zona="abajo", run_time=0.5)
        centro = Dot(pl.p(np.array([0.0, 0.0])), radius=0.08, color=C_RES)
        self.play(FadeIn(centro, scale=0.6), run_time=0.6)
        self.wait(4.0)

        # --- momento: el retrato completo ------------------------------------------
        rot.mostrar(pie_curso("La familia de líneas retrata el campo "
                              "mejor que las flechas solas."), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
