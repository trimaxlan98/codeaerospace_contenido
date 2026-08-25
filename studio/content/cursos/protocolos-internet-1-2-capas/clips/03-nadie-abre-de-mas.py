class Clip3(Scene):
    """1.2.3 - El paquete cruza un switch (lee solo la capa de enlace) y un
    router (abre hasta la capa de red y PARA): las capas superiores se ven
    selladas todo el camino. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("En el camino nadie abre de mas")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # El camino ocupa la franja ALTA y la pila que se abre crece hacia
        # abajo, en el hueco: asi la pila cabe a tamano legible (fs 14, sin
        # escalar el VGroup) y el frame no queda vacio por arriba.
        pos = {"A": (-5.3, 1.35), "SW": (-1.8, 1.35), "R1": (1.8, 1.35),
               "B": (5.3, 1.35)}
        aristas = {("A", "SW"): None, ("SW", "R1"): None, ("R1", "B"): None}
        tipos = {"A": "host", "SW": "switch", "R1": "router", "B": "host"}
        Y_PILA = -0.80

        def sobre(k):
            """El paquete viaja POR ENCIMA del cable: si se posa sobre el
            aparato lo tapa (y tapa su etiqueta)."""
            return topo.punto(k) + UP * 0.60

        def mini_pila(k, aparato):
            """La pila del aparato que abre, anclada BAJO ese aparato."""
            p = pila_abierta(CAPAS_DESDE_FUERA, k, datos=DATOS_CHICO,
                             ancho=2.9, alto=0.48, fs=14)
            p.move_to(np.array([topo.punto(aparato)[0], Y_PILA, 0.0]))
            return p

        # --- momento: el camino tiene aparatos --------------------------
        rot.mostrar(pie_curso("El paquete no va directo: cruza aparatos en "
                              "el camino, y ninguno necesita verlo entero."),
                    zona="abajo", run_time=0.5)
        topo = topologia(pos, aristas, tipos, costos=False)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        viajero = VGroup(
            Rectangle(width=0.94, height=0.48, stroke_color=C_PAQUETE,
                      stroke_width=2.4, fill_color=C_PAQUETE,
                      fill_opacity=0.20),
            tag_hud("DATO", font_size=15, color=C_PAQUETE))
        viajero[1].move_to(viajero[0].get_center())
        viajero.move_to(sobre("A"))
        self.play(FadeIn(viajero, scale=1.3), run_time=0.5)
        self.wait(4.4)

        # --- momento: el switch solo lee la capa de enlace ---------------
        rot.mostrar(pie_curso("El switch solo lee la capa de enlace: la "
                              "direccion Ethernet, nada mas."),
                    zona="abajo", run_time=0.5)
        self.play(viajero.animate.move_to(sobre("SW")), run_time=1.1)
        mini = mini_pila(1, "SW")
        guia = DashedLine(topo.nodo("SW").forma.get_bottom() + DOWN * 0.28,
                          mini.get_top() + UP * 0.06,
                          color=C_EJE, stroke_width=1.6)
        self.play(Create(guia), run_time=0.4)
        self.play(FadeIn(mini), run_time=0.7)
        et_sella = tag_hud("las demas capas siguen selladas", font_size=17,
                           color=C_CAPA)
        et_sella.next_to(mini, RIGHT, buff=0.45)
        self.play(FadeIn(et_sella), run_time=0.4)
        self.wait(4.3)

        # --- momento: el router abre una capa mas y PARA ------------------
        rot.mostrar(pie_curso("El router abre una capa mas, la de red, para "
                              "decidir el siguiente salto. Y ahi para."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(guia), FadeOut(et_sella), run_time=0.35)
        self.play(viajero.animate.move_to(sobre("R1")), run_time=1.1)
        siguiente = mini_pila(2, "R1")
        guia = DashedLine(topo.nodo("R1").forma.get_bottom() + DOWN * 0.28,
                          siguiente.get_top() + UP * 0.06,
                          color=C_EJE, stroke_width=1.6)
        self.play(Transform(mini, siguiente), Create(guia), run_time=1.0)
        et_para = tag_hud("no sigue subiendo", font_size=17, color=C_CAPA)
        et_para.next_to(siguiente, RIGHT, buff=0.45)
        self.play(FadeIn(et_para), run_time=0.4)
        self.wait(4.4)

        # --- momento: cierre del clip -------------------------------------
        rot.mostrar(pie_curso("El router no sabe que pediste, y no le "
                              "importa."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(guia), FadeOut(mini), FadeOut(et_para),
                  run_time=0.6)
        self.play(viajero.animate.move_to(sobre("B")), run_time=1.1)
        # El recuento cualitativo de la leccion: cuantas capas abre cada
        # uno. Deja el tercio inferior ocupado en el estado final.
        resumen = VGroup(
            tag_hud("switch    abre 1 capa    (enlace)", font_size=21,
                    color=C_CAPA),
            tag_hud("router    abre 2 capas   (enlace, red)", font_size=21,
                    color=C_CAPA),
            tag_hud("el destino  abre las 4", font_size=21, color=C_PAQUETE),
        ).arrange(DOWN, buff=0.28, aligned_edge=LEFT)
        resumen.move_to(DOWN * 0.85)
        self.play(LaggedStart(*[FadeIn(r, shift=0.12 * UP) for r in resumen],
                              lag_ratio=0.35), run_time=1.5)
        self.wait(4.2)
