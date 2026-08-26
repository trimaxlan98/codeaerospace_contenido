class Clip1(Scene):
    """3.2.1 - Inundar el mapa: cada router anuncia SUS enlaces a TODOS
    sus vecinos, ronda a ronda, hasta que los seis acaban con la misma
    base de datos: 4 rondas, 16 mensajes, contados por `inundacion`.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Inundar el mapa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_RED, RED, costos=False)

        # --- momento: nadie ve el mapa completo ---------------------------
        rot.mostrar(pie_curso("Cada router solo conoce sus propios "
                              "enlaces. Nadie ve el mapa completo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.3)
        self.wait(4.4)

        contador = tag_hud("ronda 0  ·  mensajes 0", font_size=22)
        contador.to_corner(UR, buff=0.55).shift(DOWN * 0.5)

        def marcador(ronda, mensajes):
            t = tag_hud("ronda %d  ·  mensajes %d" % (ronda, mensajes),
                       font_size=22)
            t.move_to(contador)
            return t

        def disparar_ronda(envios):
            fichas, anims = VGroup(), []
            for (a, b) in envios:
                m = mensaje()
                m.move_to(topo.punto(a))
                fichas.add(m)
                anims.append(MoveAlongPath(m, salto(topo, a, b)))
            self.play(*anims, run_time=0.55)
            self.play(FadeOut(fichas), run_time=0.25)

        def encender(nombres, color=C_OK):
            if nombres:
                self.play(*[topo.nodo(n).forma.animate.set_stroke(
                    color, width=3.4) for n in nombres], run_time=0.35)

        # --- momento: la primera ronda -------------------------------------
        rot.mostrar(pie_curso("Ronda 1: A anuncia sus enlaces a sus "
                              "vecinos directos, B y C."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(contador), run_time=0.4)
        disparar_ronda(RONDAS_ENVIOS[0])
        self.play(Transform(contador, marcador(1, len(RONDAS_ENVIOS[0]))),
                  run_time=0.3)
        encender(INUN["rondas"][0]["nuevos"])
        self.wait(2.6)

        # --- momento: el aviso salta otra vez, y otra -----------------------
        rot.mostrar(pie_curso("Y el aviso salta otra vez: cada router "
                              "reenvia a TODOS sus vecinos, hasta al que "
                              "ya lo sabe."),
                    zona="abajo", run_time=0.5)
        acumulado = len(RONDAS_ENVIOS[0])
        for i in (1, 2):
            disparar_ronda(RONDAS_ENVIOS[i])
            acumulado += len(RONDAS_ENVIOS[i])
            self.play(Transform(contador, marcador(i + 1, acumulado)),
                      run_time=0.3)
            encender(INUN["rondas"][i]["nuevos"])
        self.wait(2.4)

        # --- momento: para, y las bases de datos son identicas -------------
        rot.mostrar(pie_curso("Nadie tiene nada nuevo que anunciar: la "
                              "inundacion se detiene. Las seis bases de "
                              "datos son identicas."),
                    zona="abajo", run_time=0.5)
        disparar_ronda(RONDAS_ENVIOS[3])
        acumulado += len(RONDAS_ENVIOS[3])
        self.play(Transform(contador, marcador(4, acumulado)), run_time=0.3)
        self.wait(1.0)
        self.play(FadeOut(topo), FadeOut(contador), run_time=0.6)

        filas = [[n, str(N_ENLACES)] for n in ORDEN_DIJ]
        t = tabla(["Router", "Enlaces en su mapa"], filas,
                 anchos=[1.7, 2.9], alto=0.42, fs=17, color=C_CALCULO)
        t.move_to(RIGHT * 2.3 + UP * 0.15)
        cifras = VGroup(
            tag_hud("rondas    %d" % INUN["n_rondas"], font_size=26),
            tag_hud("mensajes  %d" % INUN["mensajes"], font_size=26),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.move_to(LEFT * 3.6 + UP * 0.15)
        self.play(FadeIn(t), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.0)
        self.wait(6.4)
