class Clip3(Scene):
    """3 - No existe el "ahora". Tres procesos, mensajes, y la pregunta
    sin respuesta: cual fue primero. Lamport 1978: no midas el tiempo,
    cuenta causas. Los relojes se CALCULAN, no se escriben. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("No existe el «ahora»")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: tres maquinas, tres relojes ---------------------------
        rot.mostrar(pie_curso("Tres máquinas, cada una con su reloj — y "
                              "ninguno de acuerdo con nadie."),
                    zona="abajo", run_time=0.5)
        dl = diagrama_lamport()
        dl.shift(np.array([-1.4, 0.25, 0.0]) - dl.get_center())
        nombres = VGroup(*[
            tag_junto(dl.lineas[p], n, DOWN, buff=0.14, font_size=17)
            for p, n in enumerate(("A", "B", "C"))])
        self.play(LaggedStart(*[Create(l) for l in dl.lineas],
                              lag_ratio=0.2), FadeIn(nombres),
                  run_time=1.2)
        eventos = [dl.evento(p, i) for p in range(3) for i in range(3)]
        self.play(LaggedStart(*[FadeIn(e, scale=0.4) for e in eventos],
                              lag_ratio=0.08), run_time=1.2)
        self.wait(1.6)

        # --- momento: la pregunta sin respuesta -----------------------------
        rot.mostrar(pie_curso("Un clic en A, un clic en C: ¿cuál fue "
                              "primero? Sin reloj común, no hay "
                              "respuesta."), zona="abajo", run_time=0.5)
        aro_a = Circle(radius=0.17, stroke_width=2.6, color=C_FALLO)
        aro_a.move_to(dl.evento(0, 1).get_center())
        aro_c = aro_a.copy().move_to(dl.evento(2, 1).get_center())
        self.play(Create(aro_a), Create(aro_c), run_time=0.8)
        self.wait(3.0)
        self.play(FadeOut(aro_a), FadeOut(aro_c), run_time=0.4)

        # --- momento: los mensajes ------------------------------------------
        rot.mostrar(pie_curso("Lamport, 1978: no midas el tiempo — "
                              "cuenta causas. Los mensajes las llevan."),
                    zona="abajo", run_time=0.5)
        for flecha in dl.flechas:
            self.play(Create(flecha), run_time=0.7)
        self.wait(1.5)

        # --- momento: los relojes logicos -----------------------------------
        rot.mostrar(pie_curso("Cada evento cuenta: local, +1; al "
                              "recibir, el máximo más uno. La causa "
                              "siempre numera menos."), zona="abajo",
                    run_time=0.5)
        cifras = VGroup()
        for p in range(3):
            for i in range(3):
                c = tag_hud(f"{dl.reloj(p, i)}", font_size=16,
                            color=C_TIEMPO)
                c.next_to(dl.evento(p, i), UP + LEFT, buff=0.07)
                cifras.add(c)
        self.play(LaggedStart(*[FadeIn(c, scale=0.5) for c in cifras],
                              lag_ratio=0.1), run_time=2.2)
        # la causa numera menos: el mensaje B->C en accion
        self.play(Indicate(dl.evento(1, 1), color=C_MENSAJE),
                  Indicate(dl.evento(2, 1), color=C_MENSAJE),
                  run_time=1.0)
        self.wait(2.2)

        # --- momento: la honestidad -----------------------------------------
        rot.mostrar(pie_curso("Y los que no se tocan quedan "
                              "concurrentes: el orden total no existe — "
                              "se construye uno."), zona="abajo",
                    run_time=0.5)
        aro_a2 = Circle(radius=0.17, stroke_width=2.6, color=C_TIEMPO)
        aro_a2.move_to(dl.evento(0, 1).get_center())
        aro_c2 = aro_a2.copy().move_to(dl.evento(2, 1).get_center())
        etiq = tag_hud("concurrentes", font_size=15, color=C_TIEMPO)
        etiq.next_to(dl, RIGHT, buff=0.55)
        etiq.shift(UP * 0.3)
        self.play(Create(aro_a2), Create(aro_c2), FadeIn(etiq),
                  run_time=0.9)
        self.wait(6.3)
