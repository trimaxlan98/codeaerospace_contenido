class Clip2(Scene):
    """2.1.2 - El mejor esfuerzo: el datagrama cruza cinco redes distintas
    y IP se permite tres fracasos legales. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El mejor esfuerzo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_CAMINO, ARISTAS_CAMINO, TIPOS_CAMINO,
                         costos=True, tam=0.46, fs=14)
        topo.move_to(UP * 1.35)
        # El ultimo tramo es la bandeja de llegada: ahi paran las fichas,
        # en tres carriles que no tocan ni los nodos ni sus rotulos.
        buzon = topo.enlace("R4", "B").punto_en(0.55)
        carril = {1: 0.60, 2: 0.0, 3: -0.80}
        # Los rotulos de medio viven a +0.26 de la linea:
        # cualquier ficha que viaje sobre el cable los pisa.
        # Han dicho lo suyo en el primer momento; a partir de
        # ahi se apagan y el cable queda libre para el trafico.
        medios = VGroup(*[e.etiqueta for e in topo.enlaces
                          if e.etiqueta is not None])

        def hasta_buzon(desde, alto=0.0):
            v = VMobject()
            v.set_points_as_corners(
                [topo.punto(k) + UP * alto for k in desde] +
                [buzon + UP * alto])
            return v

        # --- momento: cinco redes, ninguna promesa ------------------------
        rot.mostrar(pie_curso("El mismo datagrama cruza cinco redes "
                              "distintas, y ninguna le prometio nada."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        p = ficha("1", lado=0.34)
        p.move_to(topo.punto("A"))
        self.add(p)
        self.play(MoveAlongPath(p, ruta_de(topo, CAMINO)), run_time=2.2)
        et_ok = tag_hud("esta vez llego. IP no promete que la proxima "
                        "tambien", font_size=20, color=C_OK)
        et_ok.move_to(DOWN * 0.55)
        self.play(FadeOut(p),
                  topo.nodo("B").forma.animate.set_stroke(C_OK, width=3.6),
                  FadeIn(et_ok), run_time=0.6)
        self.wait(2.6)

        # --- fracaso 1: perder --------------------------------------------
        self.play(FadeOut(et_ok), medios.animate.set_opacity(0.0),
                  topo.nodo("B").forma.animate.set_stroke(C_RED, width=2.4),
                  run_time=0.4)
        rot.mostrar(pie_curso("Fracaso legal numero uno: perderlo. El router "
                              "se queda sin sitio y lo tira."),
                    zona="abajo", run_time=0.5)
        et_f1 = tag_hud(FRACASOS[0], font_size=26, color=C_PERDIDA)
        et_f1.move_to(DOWN * 0.35)
        self.play(FadeIn(et_f1), run_time=0.35)
        p = ficha("1", lado=0.34)
        p.move_to(topo.punto("A"))
        self.add(p)
        self.play(MoveAlongPath(p, ruta_de(topo, ["A", "R1", "R2"])),
                  run_time=1.2)
        self.play(p.animate.move_to(topo.enlace("R2", "R3").punto_en(0.62)),
                  run_time=0.35)
        self.play(p.animate.set_color(C_PERDIDA), run_time=0.25)
        self.play(p.animate.shift(DOWN * 1.05).set_opacity(0.0),
                  run_time=0.7)
        self.remove(p)
        et_1 = tag_hud("y nadie te avisa: el emisor no se entera",
                       font_size=20, color=C_PERDIDA)
        et_1.move_to(DOWN * 1.25)
        self.play(FadeIn(et_1), run_time=0.4)
        self.wait(2.4)

        # --- fracaso 2: duplicar ------------------------------------------
        self.play(FadeOut(et_f1), FadeOut(et_1), run_time=0.3)
        rot.mostrar(pie_curso("Fracaso legal numero dos: entregarlo dos "
                              "veces. Una copia que se creia perdida."),
                    zona="abajo", run_time=0.5)
        et_f2 = tag_hud(FRACASOS[1], font_size=26, color=C_PAQUETE)
        et_f2.move_to(DOWN * 0.35)
        self.play(FadeIn(et_f2), run_time=0.35)
        a = ficha("2", lado=0.34)
        a.move_to(topo.punto("A"))
        self.add(a)
        self.play(MoveAlongPath(a, ruta_de(topo, ["A", "R1", "R2"])),
                  run_time=1.1)
        b = a.copy()
        self.add(b)
        self.play(MoveAlongPath(a, hasta_buzon(["R2", "R3", "R4"])),
                  MoveAlongPath(b, hasta_buzon(["R2", "R3", "R4"],
                                               carril[1])),
                  run_time=1.3)
        et_2 = tag_hud("el mismo datagrama, dos veces: IP no las distingue",
                       font_size=20, color=C_PAQUETE)
        et_2.move_to(DOWN * 1.25)
        self.play(FadeIn(et_2), run_time=0.4)
        self.wait(2.4)

        # --- fracaso 3: desordenar ----------------------------------------
        self.play(FadeOut(a), FadeOut(b), FadeOut(et_2), FadeOut(et_f2),
                  run_time=0.35)
        rot.mostrar(pie_curso("Fracaso legal numero tres: entregarlos en "
                              "desorden. Cada uno espero en colas distintas."),
                    zona="abajo", run_time=0.5)
        et_f3 = tag_hud(FRACASOS[2], font_size=26, color=C_COLA)
        et_f3.move_to(DOWN * 0.35)
        self.play(FadeIn(et_f3), run_time=0.35)
        tiempos = {1: 2.5, 2: 1.4, 3: 1.95}     # el que menos espera, llega
        viajeros = {}
        for k in ORDEN_SALIDA:
            f = ficha(str(k), lado=0.34)
            f.move_to(topo.punto("A") + UP * carril[k])
            viajeros[k] = f
            self.add(f)
        self.play(*[MoveAlongPath(viajeros[k], hasta_buzon(CAMINO[:-1],
                                                           carril[k]),
                                  run_time=tiempos[k])
                    for k in ORDEN_SALIDA])
        ordenes = VGroup(
            tag_hud("orden de salida    %s"
                    % "  ".join(str(k) for k in ORDEN_SALIDA), font_size=21),
            tag_hud("orden de llegada   %s"
                    % "  ".join(str(k) for k in ORDEN_LLEGADA),
                    font_size=21, color=C_COLA),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        ordenes.move_to(DOWN * 1.45)
        self.play(LaggedStart(*[FadeIn(o, shift=0.10 * UP) for o in ordenes],
                              lag_ratio=0.4), run_time=1.0)
        self.wait(2.4)

        # --- momento: la promesa que si hace ------------------------------
        rot.mostrar(pie_curso("IP no promete entregar; promete intentarlo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)
