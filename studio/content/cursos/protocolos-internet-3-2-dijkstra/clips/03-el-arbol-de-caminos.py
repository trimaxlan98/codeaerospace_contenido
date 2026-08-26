class Clip3(Scene):
    """3.2.3 - El arbol de caminos minimos que sale de Dijkstra: un
    camino y su costo medido a cada destino. Cambia un costo de enlace
    y el arbol se redibuja distinto (medido, no supuesto). (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El arbol de caminos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_RED, RED, costos=True)

        # --- momento: el arbol de caminos minimos ---------------------------
        rot.mostrar(pie_curso("Dijkstra no da un camino: da un arbol. El "
                              "mas barato de A a cada uno de los otros "
                              "cinco."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.1)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_OK, width=4.4) for a, b in ARBOL_DIJ],
                  *[topo.nodo(n).forma.animate.set_stroke(C_OK, width=3.4)
                    for n in ORDEN_DIJ], run_time=1.0)
        self.wait(5.0)

        # --- momento: un costo por destino -----------------------------------
        rot.mostrar(pie_curso("Cada rama del arbol trae su costo: la "
                              "distancia medida desde A."),
                    zona="abajo", run_time=0.5)
        mis_lineas = [tag_hud("%s    %d" % (d, int(DIJ["dist"][d])),
                             font_size=22) for d in DESTINOS]
        panel = panel_derecha(*mis_lineas)
        self.play(FadeIn(panel[0]), run_time=0.3)
        for i, d in enumerate(DESTINOS):
            self.play(Indicate(topo.nodo(d).forma, color=C_CIFRA,
                               scale_factor=1.15),
                      FadeIn(mis_lineas[i], shift=0.12 * LEFT), run_time=0.5)
        self.wait(3.0)

        # --- momento: cambia un costo, cambia el arbol -----------------------
        rot.mostrar(pie_curso("Se baja el costo de A a C, de 5 a 1: el "
                              "arbol entero se recalcula."),
                    zona="abajo", run_time=0.5)
        enlace_ac = topo.enlace("A", "C")
        nuevo_costo = tag_hud("1", font_size=13, color=C_CALCULO)
        nuevo_costo.move_to(enlace_ac.etiqueta)
        self.play(ReplacementTransform(enlace_ac.etiqueta, nuevo_costo),
                  run_time=0.4)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_RED, width=2.4) for (a, b) in RED],
                  *[topo.nodo(n).forma.animate.set_stroke(C_RED, width=2.6)
                    for n in ORDEN_DIJ], run_time=0.5)
        self.play(*[topo.enlace(a, b).linea.animate.set_stroke(
            C_OK, width=4.4) for a, b in ARBOL_DIJ2],
                  *[topo.nodo(n).forma.animate.set_stroke(C_OK, width=3.4)
                    for n in DIJ2["orden"]], run_time=1.0)
        self.wait(2.0)

        rot.mostrar(pie_curso("B sigue costando 2. C, D, E y F llegan "
                              "mas baratos por el nuevo atajo."),
                    zona="abajo", run_time=0.5)
        for i, d in enumerate(DESTINOS):
            nuevo = tag_hud("%s    %d" % (d, int(DIJ2["dist"][d])),
                           font_size=22)
            nuevo.move_to(mis_lineas[i], aligned_edge=LEFT)
            self.play(ReplacementTransform(mis_lineas[i], nuevo),
                      run_time=0.3)
            mis_lineas[i] = nuevo
        self.wait(8.0)
