class Clip2(Scene):
    """3.2.2 - Dijkstra paso a paso: con el mapa completo, el conjunto de
    fijados crece y las distancias tentativas bajan, en el orden REAL
    que devuelve `dijkstra`: A, B, C, D, E, F. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Dijkstra paso a paso")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_RED, RED, costos=True)

        def etiqueta_dist(n, texto, color):
            t = tag_hud(texto, font_size=17, color=color)
            t.next_to(topo.nodo(n), UP, buff=0.22)
            return t

        # --- momento: el mapa completo, distancias por confirmar -----------
        rot.mostrar(pie_curso("Con el mapa completo, cada router calcula "
                              "el camino mas corto por su cuenta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.2)
        tags = {}
        for n in ORDEN_DIJ:
            inicial = n == "A"
            tags[n] = etiqueta_dist(
                n, "0" if inicial else "inf",
                C_CALCULO if inicial else C_TENUE)
        self.play(*[FadeIn(t) for t in tags.values()], run_time=0.6)
        self.wait(6.3)

        # --- momento: el conjunto de fijados crece ---------------------------
        rot.mostrar(pie_curso("El siguiente en fijarse es siempre el que "
                              "tiene la distancia tentativa mas baja."),
                    zona="abajo", run_time=0.5)
        orden_txt = tag_hud("orden:  A", font_size=20)
        orden_txt.to_edge(UP, buff=1.12)
        self.play(FadeIn(orden_txt), run_time=0.4)
        self.play(topo.nodo("A").forma.animate.set_stroke(C_OK, width=3.4),
                  run_time=0.3)
        fijados = ["A"]
        for paso in DIJ["pasos"]:
            n = paso["fija"]
            if n != "A":
                self.play(topo.nodo(n).forma.animate.set_stroke(
                    C_OK, width=3.4), run_time=0.3)
                fijados.append(n)
                nuevo_orden = tag_hud("orden:  " + ", ".join(fijados),
                                     font_size=20)
                nuevo_orden.move_to(orden_txt, aligned_edge=LEFT)
                self.play(ReplacementTransform(orden_txt, nuevo_orden),
                          run_time=0.3)
                orden_txt = nuevo_orden
            if paso["bajaron"]:
                anims = []
                for v, d in paso["bajaron"].items():
                    nuevo = etiqueta_dist(v, str(int(d)), C_CALCULO)
                    anims.append(ReplacementTransform(tags[v], nuevo))
                    tags[v] = nuevo
                self.play(*anims, run_time=0.35)
            self.wait(0.6)
        self.wait(0.6)

        # --- momento: un camino concreto, con su costo ----------------------
        rot.mostrar(pie_curso("Y el orden trae el costo definitivo: de A "
                              "a F, el camino mas barato cuesta 9."),
                    zona="abajo", run_time=0.5)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_PAQUETE, width=4.4)
            for a, b in zip(CAMINO_AF[:-1], CAMINO_AF[1:])], run_time=0.8)
        et_camino = tag_hud("A -> B -> D -> F   =   9", font_size=24,
                           color=C_CALCULO)
        et_camino.move_to(DOWN * 2.6)
        self.play(FadeIn(et_camino, shift=0.12 * UP), run_time=0.5)
        self.wait(7.6)
