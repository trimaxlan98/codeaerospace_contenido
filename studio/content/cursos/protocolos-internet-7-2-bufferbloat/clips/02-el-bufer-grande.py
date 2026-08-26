class Clip2(Scene):
    """7.2.2 - El mismo enlace de 20 Mb/s con tres tamanos de bufer: 8,
    100 y 1000 paquetes. Con el grande casi no se pierde nada... y la
    latencia sube de 4.8 ms a 600 ms (MEDIDO). El ping bajo descarga,
    como demostracion domestica. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El bufer grande que empeora")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mismo enlace, tres bufers ---------------------------
        rot.mostrar(pie_curso("El mismo enlace de 20 Mb/s, con tres "
                              "tamanos de bufer distintos."),
                    zona="abajo", run_time=0.5)
        et_enlace = tag_hud("enlace: %s Mb/s" % fmt(ENLACE_MBPS, 0),
                            font_size=18, color=C_COLA)
        et_enlace.to_edge(UP, buff=1.3)
        self.play(FadeIn(et_enlace), run_time=0.4)

        q8 = cola(capacidad=8, ocupacion=8, lado=0.50,
                 etiqueta="bufer = 8 paquetes")
        q8.move_to(UP * 0.2)
        lat8 = tag_hud("latencia = %s ms" % fmt(BB_8["espera_ms"], 1),
                      font_size=22, color=C_OK)
        lat8.next_to(q8, DOWN, buff=0.35)
        self.play(FadeIn(q8), FadeIn(lat8), run_time=0.8)
        self.wait(2.6)

        self.play(FadeOut(q8), FadeOut(lat8), run_time=0.4)
        q100 = cola(capacidad=20, ocupacion=20, lado=0.225,
                    etiqueta="bufer = 100 paquetes (1 casilla = 5)")
        q100.move_to(UP * 0.2)
        lat100 = tag_hud("latencia = %s ms" % fmt(BB_100["espera_ms"], 1),
                         font_size=22, color=C_CIFRA)
        lat100.next_to(q100, DOWN, buff=0.35)
        self.play(FadeIn(q100), FadeIn(lat100), run_time=0.8)
        self.wait(2.4)

        self.play(FadeOut(q100), FadeOut(lat100), run_time=0.4)
        q1000 = cola(capacidad=25, ocupacion=25, lado=0.18,
                    etiqueta="bufer = 1000 paquetes (1 casilla = 40)")
        q1000.move_to(UP * 0.2)
        lat1000 = tag_hud("latencia = %s ms" % fmt(BB_1000["espera_ms"], 1),
                          font_size=22, color=C_PERDIDA)
        lat1000.next_to(q1000, DOWN, buff=0.35)
        self.play(FadeIn(q1000), FadeIn(lat1000), run_time=0.8)
        self.wait(2.8)

        # --- momento: la tabla resumen ---------------------------------------
        rot.mostrar(pie_curso("El mismo enlace, la misma capacidad: solo "
                              "cambia cuanto le dejas guardar."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(q1000), FadeOut(lat1000), FadeOut(et_enlace),
                  run_time=0.4)
        t = tabla(
            ["bufer (paquetes)", "latencia"],
            [["8", "%s ms" % fmt(BB_8["espera_ms"], 1)],
             ["100", "%s ms" % fmt(BB_100["espera_ms"], 1)],
             ["1000", "%s ms" % fmt(BB_1000["espera_ms"], 1)]],
            anchos=[2.6, 2.0], alto=0.48, fs=18)
        t.move_to(UP * 0.2)
        self.play(FadeIn(t), run_time=0.8)
        self.wait(4.2)

        # --- momento: la demostracion domestica (ping) ------------------------
        rot.mostrar(pie_curso("Por eso tu videollamada se corta cuando "
                              "alguien descarga: el mismo enlace, con la "
                              "cola llena."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(t), run_time=0.4)
        casa = nodo("host", "tu", 0.5)
        casa.move_to(LEFT * 3.2 + UP * 0.2)
        internet = nodo("nube", "internet", 0.6)
        internet.move_to(RIGHT * 3.2 + UP * 0.2)
        cable = enlace(casa.centro(), internet.centro(), color=C_RED)
        self.play(FadeIn(casa), FadeIn(internet), FadeIn(cable),
                  run_time=0.7)
        pkt = ficha("ping", lado=0.4, color=C_PAQUETE)
        pkt.move_to(casa.centro())
        self.play(FadeIn(pkt), run_time=0.3)
        self.play(pkt.animate.move_to(internet.centro() + UP * 0.5),
                  run_time=0.5)
        self.play(pkt.animate.move_to(casa.centro() + UP * 0.5),
                  run_time=0.5)

        cifras_ping = VGroup(
            tag_hud("ping en reposo:       %s ms" %
                    fmt(PING_REPOSO["media"], 1), font_size=20, color=C_OK),
            tag_hud("ping con carga 0.85:  %s ms" %
                    fmt(PING_CARGADO["media"], 1), font_size=20,
                    color=C_PERDIDA),
            tag_hud("diferencia:           +%s ms" %
                    fmt(PING_DELTA_MS, 1), font_size=20, color=C_CIFRA),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        cifras_ping.next_to(cable, DOWN, buff=0.6)
        self.play(LaggedStart(*[FadeIn(c) for c in cifras_ping],
                              lag_ratio=0.3), run_time=1.2)
        self.wait(6.0)
