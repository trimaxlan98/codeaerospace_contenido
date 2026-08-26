class Clip4(Scene):
    """7.2.4 - Prioridad: sin colas separadas la voz sufre; con colas
    separadas la voz recupera su latencia de reposo y la descarga, que es
    bulk, sigue igual de encolada sin que le importe. Cierre de la
    leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Prioridad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los dos flujos comparten una sola cola ------------------
        rot.mostrar(pie_curso("Una videollamada y una descarga compiten "
                              "por la misma cola del router."),
                    zona="abajo", run_time=0.5)
        r1 = nodo("host", "voz", 0.42)
        r1.move_to(LEFT * 3.6 + UP * 0.85)
        r2 = nodo("host", "descarga", 0.42)
        r2.move_to(LEFT * 3.6 + DOWN * 0.55)
        q = cola(capacidad=CAP_COLA1, ocupacion=CAP_COLA1, lado=0.40,
                 etiqueta="una sola cola")
        q.move_to(UP * 0.15)
        srv = nodo("servidor", "internet", 0.46)
        srv.move_to(RIGHT * 3.6 + UP * 0.15)
        e1 = enlace(r1.centro(), q.get_left(), color=C_RED)
        e2 = enlace(r2.centro(), q.get_left(), color=C_RED)
        e3 = enlace(q.get_right(), srv.centro(), color=C_RED)
        self.play(FadeIn(r1), FadeIn(r2), FadeIn(q), FadeIn(srv),
                  FadeIn(e1), FadeIn(e2), FadeIn(e3), run_time=0.9)
        pkt_voz = ficha("voz", lado=0.34, color=C_CIFRA)
        pkt_voz.move_to(r1.centro())
        self.play(pkt_voz.animate.move_to(q.get_center()), run_time=0.6)
        self.wait(1.2)

        # --- momento: sin separar, la voz espera detras de la descarga -------
        rot.mostrar(pie_curso("Sin colas separadas, la voz espera detras "
                              "de la descarga: el ping sube %s ms." %
                              fmt(PING_DELTA_MS, 1)),
                    zona="abajo", run_time=0.5)
        et_sin = tag_hud("voz SIN prioridad: %s ms" %
                         fmt(PING_CARGADO["media"], 1), font_size=20,
                         color=C_PERDIDA)
        et_sin.next_to(q, DOWN, buff=1.1)
        self.play(FadeIn(et_sin), run_time=0.5)
        self.wait(4.6)

        # --- momento: con colas separadas, la voz pasa primero ---------------
        rot.mostrar(pie_curso("Con colas separadas, la voz pasa primero: "
                              "recupera su latencia de reposo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pkt_voz), FadeOut(q), FadeOut(et_sin),
                  FadeOut(r1), FadeOut(r2), FadeOut(srv),
                  FadeOut(e1), FadeOut(e2), FadeOut(e3), run_time=0.5)
        q_voz = cola(capacidad=2, ocupacion=0, lado=0.42,
                    etiqueta="cola de voz (prioridad)")
        q_voz.move_to(UP * 1.35)
        et_voz = tag_hud("voz CON prioridad: %s ms" %
                         fmt(PING_REPOSO["media"], 1), font_size=19,
                         color=C_OK)
        et_voz.next_to(q_voz, DOWN, buff=0.28)
        q_desc = cola(capacidad=CAP_COLA1, ocupacion=CAP_COLA1, lado=0.42,
                     etiqueta="cola de la descarga")
        q_desc.move_to(DOWN * 0.55)
        et_desc = tag_hud("descarga (bulk): %s ms  (no le importa)" %
                          fmt(BB_1000["espera_ms"], 1), font_size=19,
                          color=C_TENUE)
        et_desc.next_to(q_desc, DOWN, buff=0.28)
        self.play(FadeIn(q_voz), FadeIn(et_voz), run_time=0.6)
        self.play(FadeIn(q_desc), FadeIn(et_desc), run_time=0.6)
        self.wait(8.0)

        # --- cierre de la leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "El bufer no te regala tiempo.",
            "Te lo cobra en latencia.",
            "Siguiente: tiempo real, voz, video y jitter.",
            q_voz, et_voz, q_desc, et_desc,
            espera=4.8)
