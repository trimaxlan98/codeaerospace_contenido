class Clip2(Scene):
    """3.1.2 - Bellman-Ford distribuido, ronda a ronda y con las cifras
    MEDIDAS: el rumor avanza un salto por ronda, D descubre que dar la
    vuelta le sale mas barato y en 3 rondas la tabla deja de cambiar. El
    camino optimo no lo diseno nadie. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El rumor converge")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la ronda cero ---------------------------------------
        rot.mostrar(pie_curso("Todos arrancan igual de ignorantes. Solo %s "
                              "sabe llegar a %s." % (DESTINO, DESTINO)),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_RED, ARISTAS_RED, TIPOS_RED, costos=True,
                         tam=0.46, fs=15)
        topo.nodo(DESTINO).forma.set_stroke(C_OK, width=3.4)
        tab = tabla_rutas(BF_HIST[0])
        et_tab = tag_hud("tabla de rutas hacia %s" % DESTINO,
                         font_size=19, color=C_EJE)
        et_tab.move_to(np.array([3.55, 2.25, 0.0]))
        cnt = contador_ronda(0)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        self.play(FadeIn(tab), FadeIn(et_tab), FadeIn(cnt), run_time=0.8)
        self.wait(4.4)

        def ronda(k, filas_a_marcar):
            """Una ronda: la tabla nueva es gemela de la vieja (misma
            estructura, `filas_max` + `resaltable`), asi que el Transform
            no rompe glifos. Corto y con Wait detras: si no, los digitos
            se quedan a medio morfar."""
            nueva = tabla_rutas(BF_HIST[k])
            ncnt = contador_ronda(k)
            self.play(Succession(
                AnimationGroup(Transform(tab, nueva), Transform(cnt, ncnt),
                               run_time=0.45),
                Wait(0.10)))
            self.play(*[Indicate(tab.fila(i), color=C_CIFRA,
                                 scale_factor=1.12)
                        for i in filas_a_marcar], run_time=0.65)

        # --- momento: ronda 1, los vecinos de F ---------------------------
        rot.mostrar(pie_curso("Ronda uno: los dos vecinos de %s le oyen. "
                              "%s anota %d, %s anota %d."
                              % (DESTINO, "E", int(BF_HIST[1]["E"][0]),
                                 "D", int(BF_HIST[1]["D"][0]))),
                    zona="abajo", run_time=0.5)
        ronda(1, [NODOS.index("D"), NODOS.index("E")])
        self.wait(4.4)

        # --- momento: ronda 2, el rodeo barato -----------------------------
        rot.mostrar(pie_curso("Ronda dos: %s se entera de que dar la vuelta "
                              "por %s cuesta %d, menos que su propio cable "
                              "de %d." % ("D", "E", int(BF_HIST[2]["D"][0]),
                                          int(ARISTAS_RED[("D", "F")]))),
                    zona="abajo", run_time=0.5)
        ronda(2, [NODOS.index("B"), NODOS.index("C"), NODOS.index("D")])
        self.wait(4.4)

        # --- momento: ronda 3, converge ------------------------------------
        rot.mostrar(pie_curso("Ronda tres: %s ya sabe llegar, y %s corrige "
                              "%d por %d. A la cuarta, nada cambia."
                              % ("A", "B", int(BF_HIST[2]["B"][0]),
                                 int(BF_HIST[3]["B"][0]))),
                    zona="abajo", run_time=0.5)
        ronda(3, [NODOS.index("A"), NODOS.index("B")])
        et_conv = tag_hud("converge en %d rondas" % BF_RONDAS,
                          font_size=21, color=C_CIFRA)
        et_conv.move_to(np.array([-3.20, -2.52, 0.0]))
        self.play(FadeIn(et_conv), run_time=0.45)
        self.wait(4.2)

        # --- momento: el camino que nadie diseno ---------------------------
        rot.mostrar(pie_curso("Nadie calculo ese camino entero: cada router "
                              "solo eligio a un vecino."),
                    zona="abajo", run_time=0.5)
        tramos = VGroup(*[topo.enlace(a, b).linea.copy().set_stroke(
            C_PAQUETE, width=5.4)
            for a, b in zip(CAMINO_OPT[:-1], CAMINO_OPT[1:])])
        self.play(LaggedStart(*[Create(t) for t in tramos], lag_ratio=0.45),
                  run_time=1.5)
        et_cam = tag_hud("%s   costo %d" % (" > ".join(CAMINO_OPT),
                                            int(COSTO_OPT)),
                         font_size=21, color=C_PAQUETE)
        et_cam.move_to(np.array([-3.20, -2.52, 0.0]))
        marcada = tabla_rutas(BF_HIST[3], resaltar=NODOS.index("A"))
        self.play(FadeOut(et_conv), run_time=0.3)
        self.play(FadeIn(et_cam), Transform(tab, marcada), run_time=0.55)
        self.wait(4.8)
