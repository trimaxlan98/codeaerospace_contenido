class Clip2(Scene):
    """4.2.2 - Cada byte tiene un numero: el receptor reordena lo que
    llega revuelto y confirma con un ACK acumulado; cuando falta un
    segmento, aparecen los ACK duplicados. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Secuencia y ACK")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los bytes se numeran ---------------------------------
        rot.mostrar(pie_curso("TCP no manda bytes sueltos: numera cada "
                              "segmento para poder ordenarlos despues."),
                    zona="abajo", run_time=0.5)
        segs = []
        for seq in SEQS:
            p = paquete([("seq", 1.0, str(seq)), ("datos", 1.3, "1460 B")],
                       ancho=1.85, alto=0.56, fs=13)
            p.iluminar("seq", C_CIFRA)
            segs.append(p)
        fila_env = VGroup(*segs).arrange(RIGHT, buff=0.30)
        fila_env.move_to(UP * 1.55)
        x_grid = [s.get_center()[0] for s in segs]
        et_env = tag_hud("enviados en orden", font_size=17)
        et_env.next_to(fila_env, UP, buff=0.16)
        self.play(FadeIn(et_env), LaggedStart(
            *[FadeIn(s, shift=0.15 * DOWN) for s in segs], lag_ratio=0.25),
            run_time=1.3)
        self.wait(2.2)

        # --- momento: llegan desordenados -----------------------------
        rot.mostrar(pie_curso("Pero la red no promete orden: pueden llegar "
                              "revueltos."),
                    zona="abajo", run_time=0.5)
        y_lleg = 0.35
        anims = []
        for pos, idx in enumerate(ORDEN_LLEGADA):
            anims.append(segs[idx].animate.move_to(
                [x_grid[pos], y_lleg, 0]))
        self.play(FadeOut(et_env), run_time=0.3)
        self.play(LaggedStart(*anims, lag_ratio=0.3), run_time=1.6)
        et_lleg = tag_hud("llegan asi", font_size=17)
        et_lleg.next_to(fila_env, UP, buff=0.20)
        self.play(FadeIn(et_lleg), run_time=0.4)
        self.wait(2.2)

        # --- momento: el receptor reordena -----------------------------
        rot.mostrar(pie_curso("El receptor los guarda y los reordena por "
                              "su numero de secuencia."),
                    zona="abajo", run_time=0.5)
        y_ord = -0.85
        anims = [segs[idx].animate.move_to([x_grid[idx], y_ord, 0])
                for idx in range(len(segs))]
        self.play(FadeOut(et_lleg), run_time=0.3)
        self.play(LaggedStart(*anims, lag_ratio=0.3), run_time=1.6)
        et_ord = tag_hud("el receptor los ordena", font_size=17)
        et_ord.next_to(fila_env, UP, buff=0.20)
        ack1 = tag_hud("ACK acumulado = %d  (todo confirmado)"
                       % ACK_TRAS_REORDEN, font_size=19, color=C_CIFRA)
        ack1.move_to(DOWN * 1.85)
        self.play(FadeIn(et_ord), run_time=0.3)
        self.play(FadeIn(ack1), run_time=0.5)
        self.wait(3.2)

        # --- momento: se pierde uno y aparecen los duplicados --------------
        rot.mostrar(pie_curso("Si uno se pierde de verdad, el hueco no "
                              "avanza: el receptor repite el mismo ACK."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(fila_env), FadeOut(et_ord), FadeOut(ack1),
                  run_time=0.5)

        tokens = [ficha(str(s), lado=0.62, fs=14, color=C_PAQUETE)
                 for s in SEQS_2]
        fila2 = VGroup(*tokens).arrange(RIGHT, buff=0.45)
        fila2.move_to(UP * 0.9)
        self.play(LaggedStart(*[FadeIn(t, shift=0.15 * DOWN)
                                for t in tokens], lag_ratio=0.3),
                  run_time=1.1)
        self.wait(0.6)

        ack2 = tag_hud("ACK = %d" % SEQS_2[0], font_size=19, color=C_CIFRA)
        ack2.move_to(DOWN * 0.35)
        self.play(tokens[0].animate.set_color(C_OK), FadeIn(ack2),
                  run_time=0.6)
        self.wait(0.5)

        perdido = tokens[IDX_PERDIDO]
        self.play(perdido.animate.set_color(C_PERDIDA), run_time=0.4)
        self.play(perdido.animate.shift(DOWN * 0.5).set_opacity(0.0),
                  run_time=0.7)
        ack3 = tag_hud("ACK = %d  (el hueco)" % ACK_DUP, font_size=19,
                      color=C_CIFRA)
        ack3.move_to(DOWN * 0.35)
        self.play(FadeOut(ack2), FadeIn(ack3), run_time=0.4)
        ack2 = ack3
        self.wait(1.0)

        contador = tag_hud("0 ACK duplicados", font_size=19,
                          color=C_PERDIDA)
        contador.move_to(DOWN * 1.2)
        self.play(FadeIn(contador), run_time=0.3)
        for n, idx in enumerate(range(IDX_PERDIDO + 1, len(SEQS_2)),
                                start=1):
            self.play(tokens[idx].animate.set_color(C_RED), run_time=0.4)
            nuevo_c = tag_hud("%d ACK duplicado%s"
                             % (n, "" if n == 1 else "s"), font_size=19,
                             color=C_PERDIDA)
            nuevo_c.move_to(DOWN * 1.2)
            self.play(FadeOut(contador), FadeIn(nuevo_c), run_time=0.4)
            contador = nuevo_c
            self.wait(0.9)

        self.wait(2.5)
