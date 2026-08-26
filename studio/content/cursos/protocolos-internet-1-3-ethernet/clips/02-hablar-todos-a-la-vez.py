class Clip2(Scene):
    """1.3.2 - CSMA/CD sobre un cable compartido: escuchar, chocar, esperar
    lo que diga el sorteo del backoff. Se anima la historia REAL de
    `csma_cd(3, semilla=5)`: 7 ranuras, 2 colisiones. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Hablar todos a la vez")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el cable compartido ---------------------------------
        rot.mostrar(pie_curso("Un solo cable para todos. Antes de hablar, "
                              "cada uno escucha si hay alguien hablando."),
                    zona="abajo", run_time=0.5)
        cable = Line(np.array([CABLE_X[0], CABLE_Y, 0.0]),
                     np.array([CABLE_X[1], CABLE_Y, 0.0]),
                     color=C_RED, stroke_width=3.4)
        et_cable = tag_hud("el mismo cable para los tres", font_size=17,
                           color=C_EJE)
        et_cable.next_to(cable, UP, buff=0.16)
        ests, stubs = VGroup(), VGroup()
        for i, x in enumerate(X_ESTACION):
            n = nodo("host", ESTACIONES[i], 0.55)
            n.move_to(np.array([x, EST_Y, 0.0]))
            ests.add(n)
            stubs.add(DashedLine(np.array([x, EST_Y + 0.30, 0.0]),
                                 np.array([x, CABLE_Y, 0.0]),
                                 color=C_RED, stroke_width=2.0))
        self.play(Create(cable), FadeIn(et_cable), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(n) for n in ests], lag_ratio=0.25),
                  FadeIn(stubs), run_time=1.0)

        reglas = VGroup(*[Square(0.66, stroke_color=C_EJE, stroke_width=1.8,
                                 fill_opacity=0.0)
                          for _ in range(CSMA_RANURAS)])
        reglas.arrange(RIGHT, buff=0.16)
        reglas.move_to(np.array([0.0, RANURA_Y, 0.0]))
        nums = VGroup(*[tag_hud(str(r), font_size=15, color=C_EJE)
                        .next_to(reglas[r], DOWN, buff=0.13)
                        for r in range(CSMA_RANURAS)])
        et_regla = tag_hud("ranuras", font_size=16, color=C_EJE)
        et_regla.next_to(reglas, LEFT, buff=0.28)
        self.play(FadeIn(reglas), FadeIn(nums), FadeIn(et_regla),
                  run_time=0.6)
        self.wait(2.8)

        # --- utiles de la simulacion --------------------------------------
        tags = {}

        def marcar(r, color, opac):
            self.play(reglas[r].animate.set_stroke(color, width=2.8)
                      .set_fill(color, opacity=opac), run_time=0.25)

        def subir(idxs, color):
            ds = VGroup(*[Dot(np.array([X_ESTACION[i], EST_Y + 0.32, 0.0]),
                              radius=0.10, color=color) for i in idxs])
            self.add(ds)
            self.play(*[d.animate.move_to(
                np.array([X_ESTACION[i], CABLE_Y, 0.0]))
                for d, i in zip(ds, idxs)], run_time=0.40)
            return ds

        def quitar_tag(i):
            if i in tags:
                self.play(FadeOut(tags.pop(i)), run_time=0.2)

        def colision(r, ev):
            marcar(r, C_PERDIDA, 0.32)
            for i in list(ev["estaciones"]):
                quitar_tag(i)
            ds = subir(ev["estaciones"], C_PAQUETE)
            choque = tag_hud("COLISION", font_size=21, color=C_PERDIDA)
            choque.move_to(np.array([0.0, CABLE_Y + 0.42, 0.0]))
            self.play(ds.animate.set_color(C_PERDIDA),
                      cable.animate.set_stroke(C_PERDIDA, width=5.2),
                      FadeIn(choque, scale=1.3), run_time=0.35)
            self.play(FadeOut(choque), FadeOut(ds),
                      cable.animate.set_stroke(C_RED, width=3.4),
                      run_time=0.35)
            nuevos = VGroup()
            for i, e in sorted(ev.get("esperas", {}).items()):
                t = tag_hud("espera %d" % e, font_size=17, color=C_COLA)
                t.move_to(np.array([X_ESTACION[i], ESPERA_Y, 0.0]))
                tags[i] = t
                nuevos.add(t)
            self.play(LaggedStart(*[FadeIn(t, shift=0.10 * UP)
                                    for t in nuevos], lag_ratio=0.25),
                      run_time=0.55)

        def transmite(r, ev):
            i = ev["estaciones"][0]
            marcar(r, C_OK, 0.28)
            quitar_tag(i)
            ds = subir([i], C_PAQUETE)
            izq = Dot(np.array([X_ESTACION[i], CABLE_Y, 0.0]), radius=0.09,
                      color=C_OK)
            der = izq.copy()
            self.add(izq, der)
            self.play(izq.animate.move_to(
                np.array([CABLE_X[0], CABLE_Y, 0.0])),
                der.animate.move_to(np.array([CABLE_X[1], CABLE_Y, 0.0])),
                ds.animate.set_color(C_OK), run_time=0.55)
            self.play(FadeOut(izq), FadeOut(der), FadeOut(ds), run_time=0.25)

        def ranura(r):
            ev = csma_evento(r)
            if ev is None:
                marcar(r, C_COLA, 0.14)
            elif ev["evento"] == "colision":
                colision(r, ev)
            else:
                transmite(r, ev)

        # --- momento: las tres a la vez -> colision ------------------------
        rot.mostrar(pie_curso("Las tres callan, las tres oyen silencio y "
                              "las tres hablan a la vez: se estropean."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_cable), run_time=0.3)
        ranura(0)
        self.wait(3.8)

        # --- momento: el sorteo del backoff -------------------------------
        rot.mostrar(pie_curso("Cada una espera un numero de ranuras "
                              "sorteado. Si vuelven a coincidir, chocan."),
                    zona="abajo", run_time=0.5)
        for r in (1, 2, 3):
            ranura(r)
        self.wait(3.6)

        # --- momento: el sorteo se ensancha y todas pasan ------------------
        rot.mostrar(pie_curso("Tras cada choque el sorteo se ensancha: se "
                              "separan solas y acaban pasando todas."),
                    zona="abajo", run_time=0.5)
        for r in (4, 5, 6):
            ranura(r)
        et_cuenta = tag_hud("%d estaciones  ->  %d colisiones contadas en "
                            "%d ranuras" % (CSMA_N, CSMA_COLISIONES,
                                            CSMA_RANURAS),
                            font_size=21, color=C_PERDIDA)
        et_cuenta.move_to(np.array([0.0, CONTEO_Y, 0.0]))
        self.play(FadeIn(et_cuenta), run_time=0.5)
        self.wait(4.6)
