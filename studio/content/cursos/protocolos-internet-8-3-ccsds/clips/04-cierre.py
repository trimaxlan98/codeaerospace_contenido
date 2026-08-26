class Clip4(Scene):
    """8.3.4 - El cierre de la familia: los veinticuatro temas en una sola
    linea, de un cable de casa al suelo de Marte, y lo que de verdad
    sobrevive del Internet terrestre. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La red que nadie manda, tampoco alla")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el curso entero en una linea -------------------------
        rot.mostrar(pie_curso("Veinticuatro lecciones caben en esta linea. "
                              "Empezaron en el cable de la izquierda."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_LINEA, ARISTAS_LINEA, TIPOS_LINEA, costos=False,
                         tam=0.46, fs=14)
        topo.shift(UP * 1.55)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        self.wait(4.6)

        # --- momento: el mismo paquete, hasta el final ---------------------
        rot.mostrar(pie_curso("Y es el mismo paquete de siempre: se trocea, "
                              "se rotula, hace cola y sale de casa."),
                    zona="abajo", run_time=0.5)
        # El paquete viaja POR ENCIMA del cable: posado sobre un aparato lo
        # taparia a el y a su etiqueta.
        puntos = [topo.punto(k) + UP * 0.55 for k in CAMINO_LINEA]
        ruta = VMobject()
        ruta.set_points_as_corners(puntos)
        f = ficha("8 MB", lado=0.52, fs=15)
        f.move_to(puntos[0])
        self.play(FadeIn(f, scale=1.3), run_time=0.4)
        self.play(MoveAlongPath(f, ruta), run_time=2.6, rate_func=linear)
        self.play(topo.nodo("Rover").forma.animate.set_stroke(C_OK,
                                                              width=3.6),
                  run_time=0.4)
        et_escala = tag_hud("la escala miente: de la antena al orbitador "
                            "hay %s millones de km" % fmt(MKM_VIAJE, 0),
                            font_size=16, color=C_TENUE)
        et_escala.move_to(UP * 0.52)
        self.play(FadeIn(et_escala), run_time=0.5)
        self.wait(3.6)

        # --- momento: lo que sobrevive -------------------------------------
        rot.mostrar(pie_curso("De todo el Internet de casa, esto es lo que "
                              "aguanta a esa distancia."),
                    zona="abajo", run_time=0.5)
        col_nom = VGroup(*[tag_hud(n, font_size=17, color=C_TITULO)
                           for n, _ in PRINCIPIOS])
        col_nom.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        col_exp = VGroup(*[tag_hud(e, font_size=17, color=C_TENUE)
                           for _, e in PRINCIPIOS])
        col_exp.arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        for a, b in zip(col_nom, col_exp):
            b.move_to(np.array([0.0, a.get_center()[1], 0.0]))
            b.align_to(col_nom, LEFT)
            b.shift(RIGHT * 2.95)
        lista = VGroup(col_nom, col_exp)
        lista.move_to(DOWN * 1.32)
        filas = [VGroup(col_nom[k], col_exp[k])
                 for k in range(len(PRINCIPIOS))]
        self.play(LaggedStart(*[FadeIn(l, shift=0.12 * UP) for l in filas],
                              lag_ratio=0.50), run_time=2.2)
        self.wait(5.0)

        # --- cierre de la leccion, del modulo y del curso -------------------
        cierre_leccion(
            self, rot,
            "Internet no es un cable.",
            "Es un acuerdo que sigue funcionando lejos de casa.",
            "Fin del curso: 24 lecciones, de un cable de casa a %s "
            "millones de kilometros." % fmt(MKM_VIAJE, 0),
            lista, topo, f, et_escala, espera=5.2)
