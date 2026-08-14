class Clip6(Scene):
    """6 - Elegir un lider. Eleccion al estilo Raft, sembrada y
    reproducida tal cual: lider, muerte, empate, nuevo termino. Todos
    los votos salen de rondas_eleccion(), no del guion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Elegir un líder")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        rondas = rondas_eleccion(SEMILLA_ELECCION)
        mayoria = N_QUORUM // 2 + 1
        centro = np.array([-1.1, 0.35, 0.0])
        radio = 1.55

        def pos(i):
            ang = 0.25 * TAU - TAU * i / N_QUORUM
            return centro + radio * np.array([math.cos(ang),
                                              math.sin(ang), 0.0])

        # --- momento: cinco iguales ----------------------------------------
        rot.mostrar(pie_curso("Cinco nodos iguales. Nadie manda… hasta "
                              "que alguien se harta de esperar."),
                    zona="abajo", run_time=0.5)
        nodos = VGroup(*[Dot(pos(i), radius=0.16, color=C_NODO)
                         for i in range(N_QUORUM)])
        etiquetas = VGroup(*[
            tag_hud(f"{i}", font_size=13,
                    color=C_TENUE).move_to(pos(i) * 1.0
                                           + (pos(i) - centro) * 0.28)
            for i in range(N_QUORUM)])
        self.play(LaggedStart(*[FadeIn(n, scale=0.4) for n in nodos],
                              lag_ratio=0.12), FadeIn(etiquetas),
                  run_time=1.2)
        tag_termino = tag_hud(f"término {rondas[0]['termino']}",
                              font_size=17, color=C_MENSAJE)
        tag_termino.move_to(np.array([4.3, 2.0, 0.0]))
        self.play(FadeIn(tag_termino), run_time=0.5)
        self.wait(1.0)

        # --- momento: primera eleccion -------------------------------------
        rot.mostrar(pie_curso("El de timeout más corto se candidatea y "
                              "pide votos: con mayoría de 3, hay "
                              "líder."), zona="abajo", run_time=0.5)
        r1 = rondas[0]
        lider1 = r1["lider"]
        self.play(Flash(nodos[lider1], color=C_MENSAJE,
                        flash_radius=0.34), run_time=0.6)
        flechas1 = VGroup(*[
            Arrow(pos(v), pos(c), buff=0.22, stroke_width=2.6,
                  color=C_MENSAJE, max_tip_length_to_length_ratio=0.14)
            for v, c in r1["votos"].items() if v != c])
        self.play(LaggedStart(*[Create(f) for f in flechas1],
                              lag_ratio=0.2), run_time=1.4)
        corona1 = corona()
        corona1.next_to(nodos[lider1], UP, buff=0.08)
        votos1 = sum(1 for c in r1["votos"].values() if c == lider1)
        tag_votos = tag_hud(f"{votos1} de {N_QUORUM} votos: líder",
                            font_size=15, color=C_OK)
        tag_votos.move_to(np.array([4.3, 1.4, 0.0]))
        self.play(FadeIn(corona1, shift=0.12 * DOWN), FadeIn(tag_votos),
                  run_time=0.7)
        self.wait(1.9)

        # --- momento: el lider muere y el empate ---------------------------
        rot.mostrar(pie_curso("El líder muere. Timeouts corren… y dos "
                              "despiertan a la vez: los votos se "
                              "parten."), zona="abajo", run_time=0.5)
        r2 = rondas[1]
        self.play(nodos[lider1].animate.set_color(C_FALLO),
                  FadeOut(corona1), FadeOut(flechas1),
                  FadeOut(tag_votos), run_time=0.9)
        nuevo_termino = tag_hud(f"término {r2['termino']}", font_size=17,
                                color=C_MENSAJE)
        nuevo_termino.move_to(tag_termino.get_center())
        self.play(Transform(tag_termino, nuevo_termino), run_time=0.5)
        self.play(*[Flash(nodos[c], color=C_MENSAJE, flash_radius=0.34)
                    for c in r2["candidatos"]], run_time=0.7)
        flechas2 = VGroup(*[
            Arrow(pos(v), pos(c), buff=0.22, stroke_width=2.6,
                  color=C_MENSAJE, max_tip_length_to_length_ratio=0.14)
            for v, c in r2["votos"].items() if v != c])
        self.play(LaggedStart(*[Create(f) for f in flechas2],
                              lag_ratio=0.2), run_time=1.2)
        conteo2 = sorted((sum(1 for x in r2["votos"].values() if x == c)
                          for c in r2["candidatos"]), reverse=True)
        tag_empate = tag_hud(
            "-".join(str(k) for k in conteo2)
            + f": nadie llega a {mayoria}", font_size=15, color=C_FALLO)
        tag_empate.move_to(np.array([4.3, 1.4, 0.0]))
        self.play(FadeIn(tag_empate), run_time=0.5)
        self.wait(2.3)

        # --- momento: el nuevo termino -------------------------------------
        rot.mostrar(pie_curso("Sin mayoría no hay líder: timeouts "
                              "nuevos al azar y otro término. Esta vez "
                              "sí."), zona="abajo", run_time=0.5)
        r3 = rondas[-1]
        lider3 = r3["lider"]
        self.play(FadeOut(flechas2), FadeOut(tag_empate), run_time=0.5)
        tercer_termino = tag_hud(f"término {r3['termino']}",
                                 font_size=17, color=C_MENSAJE)
        tercer_termino.move_to(tag_termino.get_center())
        self.play(Transform(tag_termino, tercer_termino), run_time=0.5)
        self.play(Flash(nodos[lider3], color=C_MENSAJE,
                        flash_radius=0.34), run_time=0.6)
        flechas3 = VGroup(*[
            Arrow(pos(v), pos(c), buff=0.38, stroke_width=2.6,
                  color=C_MENSAJE, max_tip_length_to_length_ratio=0.14)
            for v, c in r3["votos"].items() if v != c])
        self.play(LaggedStart(*[Create(f) for f in flechas3],
                              lag_ratio=0.2), run_time=1.1)
        corona3 = corona()
        # hacia AFUERA del pentagono: ahi no llegan flechas
        afuera = pos(lider3) - centro
        afuera = afuera / np.linalg.norm(afuera)
        corona3.next_to(nodos[lider3], afuera, buff=0.10)
        votos3 = sum(1 for c in r3["votos"].values() if c == lider3)
        tag_final = tag_hud(f"{votos3} votos: líder nuevo", font_size=15,
                            color=C_OK)
        tag_final.move_to(np.array([4.3, 1.4, 0.0]))
        self.play(FadeIn(corona3, shift=0.12 * DOWN), FadeIn(tag_final),
                  run_time=0.7)
        self.play(flechas3.animate.set_opacity(0.3), run_time=0.5)
        self.wait(1.9)

        # --- momento: el cierre --------------------------------------------
        rot.mostrar(pie_curso("Un líder electo y términos numerados: "
                              "así se gobierna sin rey — y sin reloj."),
                    zona="abajo", run_time=0.5)
        self.wait(5.8)
