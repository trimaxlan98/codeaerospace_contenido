class Clip1(Scene):
    """3.1.1 - Ningun router ve la red: solo conoce a sus vecinos y lo que
    cuesta llegar a ellos. La tabla de rutas arranca vacia y el protocolo
    entero cabe en una frase: contarle tu tabla a los de al lado. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Nadie ve el mapa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la red que nosotros vemos y ellos no ----------------
        rot.mostrar(pie_curso("Seis routers, ocho cables, y un costo "
                              "escrito en cada uno."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_RED, ARISTAS_RED, TIPOS_RED, costos=True,
                         tam=0.46, fs=15)
        topo.etiquetas_a(ETIQUETAS_RED)
        self.play(FadeIn(topo.enlaces), run_time=0.9)
        self.play(FadeIn(topo.nodos), run_time=0.7)
        et_dest = tag_hud("destino: %s" % DESTINO, font_size=19, color=C_OK)
        et_dest.next_to(topo.nodo(DESTINO).forma, RIGHT, buff=0.30)
        self.play(FadeIn(et_dest), run_time=0.4)
        self.wait(4.4)

        # --- momento: lo unico que sabe un router -------------------------
        rot.mostrar(pie_curso("Este mapa lo ves tu. El router %s no: solo "
                              "sabe quien hay al otro lado de sus cables."
                              % YO),
                    zona="abajo", run_time=0.5)
        cerca = VGroup(*[topo.enlace(YO, v).linea.copy().set_stroke(
            C_PAQUETE, width=5.2) for v, _ in VECINOS_YO])
        aro = Circle(radius=0.44, color=C_PAQUETE, stroke_width=3.2)
        aro.move_to(topo.punto(YO))
        self.play(Create(aro), run_time=0.4)
        self.play(LaggedStart(*[Create(t) for t in cerca], lag_ratio=0.40),
                  run_time=1.2)
        tab_v = tabla(["vecino", "costo"],
                      [[v, "%d" % int(c)] for v, c in VECINOS_YO],
                      anchos=[1.55, 1.35], alto=0.46, fs=19)
        tab_v.move_to(np.array([3.55, 0.45, 0.0]))
        for i in range(len(VECINOS_YO)):
            tab_v.celda(i, 0).set_color(C_RED)
            tab_v.celda(i, 1).set_color(C_CIFRA)
        et_v = tag_hud("lo que sabe %s" % YO, font_size=19, color=C_EJE)
        et_v.next_to(tab_v, UP, buff=0.42)
        self.play(FadeIn(tab_v), FadeIn(et_v), run_time=0.7)
        self.wait(4.6)

        # --- momento: la tabla de rutas arranca vacia ----------------------
        rot.mostrar(pie_curso("De %s no sabe nada. Al arrancar, nadie sabe "
                              "llegar: solo %s sabe que %s es %s."
                              % (DESTINO, DESTINO, DESTINO, DESTINO)),
                    zona="abajo", run_time=0.5)
        # el rotulo "destino" se va con la tabla de vecinos: si se queda,
        # se mete por debajo del borde izquierdo de la tabla de rutas. El
        # destino sigue marcado, pero en verde sobre el propio nodo.
        self.play(FadeOut(tab_v), FadeOut(et_v), FadeOut(aro),
                  FadeOut(cerca), FadeOut(et_dest),
                  topo.nodo(DESTINO).forma.animate.set_stroke(C_OK,
                                                              width=3.4),
                  run_time=0.5)
        tab = tabla_rutas(BF_HIST[0])
        et_tab = tag_hud("tabla de rutas hacia %s" % DESTINO,
                         font_size=19, color=C_EJE)
        et_tab.move_to(np.array([3.55, 2.25, 0.0]))
        self.play(FadeIn(et_tab), run_time=0.35)
        self.play(FadeIn(tab), run_time=0.8)
        self.wait(4.8)

        # --- momento: el protocolo entero en una frase ---------------------
        rot.mostrar(pie_curso("Cada treinta segundos, cada router le manda "
                              "su tabla entera a sus vecinos. Eso es todo."),
                    zona="abajo", run_time=0.5)
        et_anuncio = tag_hud("\"estas son mis rutas\"", font_size=20,
                             color=C_PAQUETE)
        et_anuncio.move_to(np.array([-3.20, -2.52, 0.0]))
        self.play(FadeIn(et_anuncio), run_time=0.4)

        def onda(invertida):
            """Un pulso ambar recorriendo cada cable: el anuncio viajando.

            No es una ficha sobre el cable a proposito: una ficha taparia
            los rotulos de costo, que van a +0.26 de la linea."""
            anims = []
            for (a, b) in ARISTAS_RED:
                desde, hasta = (b, a) if invertida else (a, b)
                linea = Line(topo.punto(desde), topo.punto(hasta),
                             color=C_PAQUETE, stroke_width=5.0)
                anims.append(ShowPassingFlash(linea, time_width=0.45))
            return anims

        self.play(LaggedStart(*onda(False), lag_ratio=0.10), run_time=1.7)
        self.play(LaggedStart(*onda(True), lag_ratio=0.10), run_time=1.7)
        self.wait(4.6)
