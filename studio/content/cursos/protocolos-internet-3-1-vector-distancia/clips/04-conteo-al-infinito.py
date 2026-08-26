class Clip4(Scene):
    """3.1.4 - El patologico de verdad. Se cambia a una CADENA (y el pie lo
    dice): es la unica topologia donde el corte deja el destino
    inalcanzable y el conteo ocurre. Las series son las MEDIDAS por
    `conteo_al_infinito`: C 16,3,5,5,7,7... hasta el 16 de RIP en 14
    rondas; con horizonte dividido, 2. Cierre de la leccion. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Conteo al infinito")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        a_corte, b_corte = CORTE_CAD

        def tags_costos(t):
            """El costo de cada router escrito sobre su propia cabeza:
            ancho FIJO (dos digitos) para que las gemelas tengan los
            mismos glifos y el Transform no deje cifras a medio morfar."""
            g = VGroup()
            for n in NODOS_CAD:
                c = int(t[n][0])
                if n == DESTINO_CAD:
                    col = C_OK
                elif c >= INFINITO_RIP:
                    col = C_PERDIDA
                else:
                    col = C_CIFRA
                et = tag_hud("%02d" % c, font_size=26, color=col)
                et.move_to(np.array([POS_CADENA[n][0], 1.55, 0.0]))
                g.add(et)
            return g

        # --- momento: cambiamos de red, y se dice ---------------------------
        rot.mostrar(pie_curso("Cambiamos de red a proposito: una cadena de "
                              "cuatro, todos los cables a %d."
                              % int(ARISTAS_CADENA[("A", "B")])),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_CADENA, ARISTAS_CADENA, {DESTINO_CAD: "servidor"},
                         costos=True, tam=0.46, fs=15)
        topo.nodo(DESTINO_CAD).forma.set_stroke(C_OK, width=3.4)
        tab = tabla_rutas(BF_CAD_TABLA, nodos=NODOS_CAD, destino=DESTINO_CAD,
                          tope=None, centro=POS_TABLA_CAD)
        et_tab = tag_hud("tabla de rutas hacia %s" % DESTINO_CAD,
                         font_size=19, color=C_EJE)
        et_tab.move_to(np.array([3.55, 1.62, 0.0]))
        tags = tags_costos(BF_CAD_TABLA)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=0.9)
        self.play(FadeIn(tab), FadeIn(et_tab), FadeIn(tags), run_time=0.9)
        self.wait(3.6)

        # --- momento: el corte que deja el destino inalcanzable -------------
        rot.mostrar(pie_curso("Se corta el ultimo cable. %s se queda sin "
                              "ruta y escribe %d: el \"no llego\" de RIP."
                              % (CI_HUERFANO, INFINITO_RIP)),
                    zona="abajo", run_time=0.5)
        roto = topo.enlace(a_corte, b_corte)
        cruz = VGroup(
            Line(LEFT * 0.17 + DOWN * 0.17, RIGHT * 0.17 + UP * 0.17,
                 color=C_PERDIDA, stroke_width=4.0),
            Line(LEFT * 0.17 + UP * 0.17, RIGHT * 0.17 + DOWN * 0.17,
                 color=C_PERDIDA, stroke_width=4.0))
        cruz.move_to(roto.punto_en(0.5))
        self.play(FadeOut(roto.etiqueta),
                  roto.linea.animate.set_stroke(C_PERDIDA, width=2.0,
                                                opacity=0.35),
                  run_time=0.5)
        self.play(Create(cruz), run_time=0.4)
        cnt = contador_ronda(0, centro=POS_RONDA_CAD)
        nueva = tabla_rutas(CI_HIST[0], nodos=NODOS_CAD, destino=DESTINO_CAD,
                            tope=None, centro=POS_TABLA_CAD)
        self.play(Succession(
            AnimationGroup(Transform(tab, nueva),
                           Transform(tags, tags_costos(CI_HIST[0])),
                           FadeIn(cnt), run_time=0.55),
            Wait(0.05)))
        self.wait(3.4)

        # --- momento: la primera mentira ------------------------------------
        rot.mostrar(pie_curso("Pero %s no se ha enterado y sigue anunciando "
                              "que llega en %d. %s se lo cree: %d."
                              % ("B", RUMOR_B, CI_HUERFANO, RUMOR_C)),
                    zona="abajo", run_time=0.5)
        nueva = tabla_rutas(CI_HIST[1], nodos=NODOS_CAD, destino=DESTINO_CAD,
                            tope=None, centro=POS_TABLA_CAD)
        ncnt = contador_ronda(1, centro=POS_RONDA_CAD)
        self.play(Succession(
            AnimationGroup(Transform(tab, nueva),
                           Transform(tags, tags_costos(CI_HIST[1])),
                           Transform(cnt, ncnt), run_time=0.45),
            Wait(0.10)))
        self.play(Indicate(tab.fila(NODOS_CAD.index(CI_HUERFANO)),
                           color=C_CIFRA, scale_factor=1.12), run_time=0.6)
        self.wait(3.5)

        # --- momento: la subida real, ronda a ronda -------------------------
        rot.mostrar(pie_curso("Se creen mutuamente. El costo sube de dos en "
                              "dos y nadie sospecha nada."),
                    zona="abajo", run_time=0.5)
        for k in range(2, CI_RONDAS + 1):
            nueva = tabla_rutas(CI_HIST[k], nodos=NODOS_CAD,
                                destino=DESTINO_CAD, tope=None,
                                centro=POS_TABLA_CAD)
            ncnt = contador_ronda(k, centro=POS_RONDA_CAD)
            self.play(Succession(
                AnimationGroup(Transform(tab, nueva),
                               Transform(tags, tags_costos(CI_HIST[k])),
                               Transform(cnt, ncnt), run_time=0.30),
                Wait(0.04)))
        self.wait(2.9)

        # --- momento: el freno ----------------------------------------------
        rot.mostrar(pie_curso("El freno es no devolverle el rumor a quien te "
                              "lo conto. Se llama horizonte dividido."),
                    zona="abajo", run_time=0.5)
        reset = tabla_rutas(CI_HD_HIST[0], nodos=NODOS_CAD,
                            destino=DESTINO_CAD, tope=None,
                            centro=POS_TABLA_CAD)
        self.play(Transform(tab, reset),
                  Transform(tags, tags_costos(CI_HD_HIST[0])),
                  Transform(cnt, contador_ronda(0, centro=POS_RONDA_CAD)),
                  run_time=0.5)
        for k in (1, 2):
            nueva = tabla_rutas(CI_HD_HIST[k], nodos=NODOS_CAD,
                                destino=DESTINO_CAD, tope=None,
                                centro=POS_TABLA_CAD)
            self.play(Succession(
                AnimationGroup(
                    Transform(tab, nueva),
                    Transform(tags, tags_costos(CI_HD_HIST[k])),
                    Transform(cnt, contador_ronda(k,
                                                  centro=POS_RONDA_CAD)),
                    run_time=0.45),
                Wait(0.08)))
        cifras = VGroup(
            tag_hud("repitiendo el rumor:   %d rondas hasta el %d"
                    % (CI_RONDAS, INFINITO_RIP), font_size=20,
                    color=C_PERDIDA),
            tag_hud("horizonte dividido:     %d rondas"
                    % CI_HD_RONDAS, font_size=20, color=C_OK),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(np.array([-3.15, -1.75, 0.0]))
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=0.9)
        self.wait(3.3)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(
            self, rot,
            "Si solo repites lo que te dicen,",
            "tardas mucho en enterarte de una mala noticia.",
            "Siguiente: el mapa completo.",
            cifras, tab, et_tab, cnt, tags, topo, cruz, espera=3.8)
