class Clip4(Scene):
    """8.1.4 - Rutear la malla. 24 satelites, 42 enlaces opticos y el MISMO
    dijkstra del modulo 3: 6 saltos a Londres. Cuando la constelacion se
    mueve, la misma tabla da otra ruta de 4. Cierre de la leccion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Rutear la malla")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la constelacion como grafo --------------------------
        rot.mostrar(pie_curso("Cada satelite habla por laser con el de "
                              "delante, el de atras y los planos vecinos."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_MALLA, MALLA["aristas"], TIPOS_MALLA,
                         costos=False, tam=0.34, fs=11)
        topo.shift(UP * 0.10)
        # Veinticuatro rotulos "S0-0" no se leen y tapan las aristas: se
        # quitan y se etiqueta a mano solo lo que importa.
        for k in POS_MALLA:
            n = topo.nodo(k)
            if n.etiqueta is not None:
                n.remove(n.etiqueta)
        et_malla = tag_hud("%d satelites, %d planos de %d, %d enlaces "
                           "opticos" % (MALLA_N, MALLA_PLANOS,
                                        MALLA_POR_PLANO, MALLA_ENLACES),
                           font_size=20)
        et_malla.move_to(np.array([0.0, 2.42, 0.0]))
        self.play(FadeIn(topo.enlaces), run_time=1.2)
        self.play(FadeIn(topo.nodos), run_time=0.6)
        self.play(FadeIn(et_malla), run_time=0.5)
        self.wait(3.8)

        # --- momento: el mismo Dijkstra del modulo 3 ----------------------
        rot.mostrar(pie_curso("El mismo Dijkstra del modulo 3, sin cambiarle "
                              "una linea, sobre este grafo."),
                    zona="abajo", run_time=0.5)
        et_orig = tag_hud("desde CDMX", font_size=18, color=C_EJE)
        et_orig.move_to(topo.punto(ORIGEN_MALLA) + np.array([-0.10, 0.50, 0]))
        et_dest = tag_hud("a Londres", font_size=18, color=C_EJE)
        et_dest.move_to(topo.punto(DESTINO_A) + np.array([0.00, -0.48, 0]))
        self.play(FadeIn(et_orig), FadeIn(et_dest), run_time=0.5)
        topo.resaltar_camino(RUTA_A, color=C_PAQUETE, grosor=4.6)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_PAQUETE, width=4.6)
            for a, b in zip(RUTA_A[:-1], RUTA_A[1:])], run_time=1.0)
        puntos = [topo.punto(k) for k in RUTA_A]
        puntos[-1] = puntos[-2] + (puntos[-1] - puntos[-2]) * 0.66
        senda = VMobject()
        senda.set_points_as_corners(puntos)
        pkt = ficha("", lado=0.24, color=C_PAQUETE)
        pkt.move_to(puntos[0])
        self.play(FadeIn(pkt, scale=1.4), run_time=0.3)
        self.play(MoveAlongPath(pkt, senda), run_time=1.6)
        et_ruta = tag_hud("Dijkstra: %d saltos, coste %s"
                          % (SALTOS_A, fmt(COSTE_A, 1)), font_size=21)
        et_ruta2 = tag_hud("ahora %d saltos, coste %s"
                           % (SALTOS_B, fmt(COSTE_B, 1)), font_size=21)
        VGroup(et_ruta, et_ruta2).arrange(RIGHT, buff=0.70).move_to(
            np.array([0.0, -2.45, 0.0]))
        self.play(FadeIn(et_ruta), run_time=0.5)
        self.wait(3.4)

        # --- momento: la constelacion se mueve ----------------------------
        rot.mostrar(pie_curso("Diez minutos despues, a Londres lo ve otro "
                              "satelite. Misma tabla, otra ruta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pkt), run_time=0.3)
        apagar_camino(topo, RUTA_A)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_RED, width=2.4)
            for a, b in zip(RUTA_A[:-1], RUTA_A[1:])] +
            [et_ruta.animate.set_color(C_EJE)], run_time=0.6)
        et_dest2 = tag_hud("a Londres", font_size=18, color=C_EJE)
        et_dest2.move_to(topo.punto(DESTINO_B) + np.array([0.10, 0.52, 0]))
        self.play(FadeOut(et_dest), run_time=0.35)
        self.play(FadeIn(et_dest2), run_time=0.35)
        topo.resaltar_camino(RUTA_B, color=C_PAQUETE, grosor=4.6)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_PAQUETE, width=4.6)
            for a, b in zip(RUTA_B[:-1], RUTA_B[1:])], run_time=1.0)
        self.play(FadeIn(et_ruta2), run_time=0.5)
        self.wait(3.4)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "Los mismos protocolos, un poco mas arriba.",
            "Y de pronto la luz es lenta.",
            "Siguiente: la red que tolera la desconexion.",
            topo, et_malla, et_orig, et_dest2, et_ruta, et_ruta2,
            espera=4.4)
