class Clip3(Scene):
    """3.1.3 - Se corta el cable barato por el que pasaban los cinco
    caminos. La red se repara sola, pero por rumores de rumores: A y C se
    creen mutuamente y el costo sube de dos en dos durante siete rondas.
    Todas las cifras salen de `conteo_al_infinito`. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Se cae un enlace")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        a_clave, b_clave = ENLACE_CLAVE

        # --- momento: todo cuelga de un solo cable -------------------------
        rot.mostrar(pie_curso("La red ya convergio. Y los cinco caminos "
                              "pasan por el mismo cable: %s-%s, el que "
                              "cuesta %d." % (a_clave, b_clave,
                                              int(ARISTAS_RED[ENLACE_CLAVE]))),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_RED, ARISTAS_RED, TIPOS_RED, costos=True,
                         tam=0.46, fs=15)
        topo.etiquetas_a(ETIQUETAS_RED)
        topo.nodo(DESTINO).forma.set_stroke(C_OK, width=3.4)
        tab = tabla_rutas(BF["tabla"])
        et_tab = tag_hud("tabla de rutas hacia %s" % DESTINO,
                         font_size=19, color=C_EJE)
        et_tab.move_to(np.array([3.55, 2.25, 0.0]))
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=0.9)
        self.play(FadeIn(tab), FadeIn(et_tab), run_time=0.7)
        clave = topo.enlace(a_clave, b_clave).linea.copy().set_stroke(
            C_PAQUETE, width=5.6)
        self.play(Create(clave), run_time=0.6)
        self.wait(4.0)

        # --- momento: el corte ---------------------------------------------
        rot.mostrar(pie_curso("Se corta. %s se queda sin ruta y lo dice: "
                              "no llego. Volvemos a contar rondas."
                              % a_clave),
                    zona="abajo", run_time=0.5)
        roto = topo.enlace(a_clave, b_clave)
        cruz = VGroup(
            Line(LEFT * 0.17 + DOWN * 0.17, RIGHT * 0.17 + UP * 0.17,
                 color=C_PERDIDA, stroke_width=4.0),
            Line(LEFT * 0.17 + UP * 0.17, RIGHT * 0.17 + DOWN * 0.17,
                 color=C_PERDIDA, stroke_width=4.0))
        cruz.move_to(roto.punto_en(0.5))
        self.play(FadeOut(clave), FadeOut(roto.etiqueta),
                  roto.linea.animate.set_stroke(C_PERDIDA, width=2.0,
                                                opacity=0.35),
                  run_time=0.5)
        self.play(Create(cruz), run_time=0.4)
        cnt = contador_ronda(0)
        nueva = tabla_rutas(CAIDA_HIST[0])
        self.play(Succession(
            AnimationGroup(Transform(tab, nueva), FadeIn(cnt), run_time=0.5),
            Wait(0.10)))
        self.play(Indicate(tab.fila(NODOS.index(a_clave)),
                           color=C_PERDIDA, scale_factor=1.12), run_time=0.6)
        self.wait(3.9)

        # --- momento: los demas siguen contando lo de antes ----------------
        rot.mostrar(pie_curso("%s recupera su propio cable a %s: %d. Pero %s "
                              "se cree la ruta vieja de %s y anuncia %d."
                              % ("D", DESTINO, int(CAIDA_HIST[1]["D"][0]),
                                 "C", "A", int(CAIDA_HIST[1]["C"][0]))),
                    zona="abajo", run_time=0.5)
        nueva = tabla_rutas(CAIDA_HIST[1])
        ncnt = contador_ronda(1)
        self.play(Succession(
            AnimationGroup(Transform(tab, nueva), Transform(cnt, ncnt),
                           run_time=0.45),
            Wait(0.10)))
        self.play(*[Indicate(tab.fila(NODOS.index(n)), color=C_CIFRA,
                             scale_factor=1.12) for n in ("C", "D", "E")],
                  run_time=0.65)
        self.wait(4.0)

        # --- momento: rumores de rumores -----------------------------------
        rot.mostrar(pie_curso("Y aqui empieza lo feo: %s y %s se creen "
                              "mutuamente y el costo sube de %d en %d cada "
                              "dos rondas." % ("A", "C", PASO_RUMOR,
                                               PASO_RUMOR)),
                    zona="abajo", run_time=0.5)
        for k in range(2, CAIDA_RONDAS + 1):
            nueva = tabla_rutas(CAIDA_HIST[k])
            ncnt = contador_ronda(k)
            self.play(Succession(
                AnimationGroup(Transform(tab, nueva), Transform(cnt, ncnt),
                               run_time=0.42),
                Wait(0.08)))
        self.wait(3.9)

        # --- momento: lo que costo repararse -------------------------------
        rot.mostrar(pie_curso("Se reparo sola, pero tarde. Y el camino "
                              "nuevo da la vuelta entera."),
                    zona="abajo", run_time=0.5)
        tramos = VGroup(*[topo.enlace(a, b).linea.copy().set_stroke(
            C_PAQUETE, width=5.4)
            for a, b in zip(CAMINO_DESPUES[:-1], CAMINO_DESPUES[1:])])
        self.play(LaggedStart(*[Create(t) for t in tramos], lag_ratio=0.45),
                  run_time=1.3)
        # las dos cifras van a lados distintos: apiladas bajo la topologia
        # el bloque de dos lineas se come el hueco entre los rotulos de
        # nodo (y = -2.0) y el pie (y = -2.9).
        et_cam = tag_hud("%s   costo %d  (antes %d)"
                         % (" > ".join(CAMINO_DESPUES), int(COSTO_DESPUES),
                            int(COSTO_ANTES)), font_size=21, color=C_PAQUETE)
        et_cam.move_to(np.array([-3.20, -2.52, 0.0]))
        et_rondas = tag_hud("%d rondas para digerir un cable roto"
                            % CAIDA_RONDAS, font_size=18)
        et_rondas.move_to(np.array([3.55, -2.30, 0.0]))
        self.play(FadeIn(et_cam, shift=0.12 * UP),
                  FadeIn(et_rondas, shift=0.12 * UP), run_time=1.0)
        self.wait(4.4)
