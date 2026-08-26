class Clip3(Scene):
    """7.2.3 - CoDel: descartar temprano y poco mantiene la cola CORTA.
    Recorta 600 ms a 4.8 ms (125 veces mejor), quedandose con el 0.8 % de
    la cola. Es preferible perder un paquete que esconder medio segundo.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("AQM: descartar a tiempo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el bufer grande del clip anterior -----------------------
        rot.mostrar(pie_curso("El mismo bufer de 1000 paquetes: 600 ms "
                              "de latencia escondida."),
                    zona="abajo", run_time=0.5)
        et_enlace = tag_hud("enlace: %s Mb/s" % fmt(ENLACE_MBPS, 0),
                            font_size=18, color=C_COLA)
        et_enlace.to_edge(UP, buff=1.3)
        q_grande = cola(capacidad=25, ocupacion=25, lado=0.18,
                       etiqueta="sin AQM: 1000 paquetes (1 casilla = 40)")
        q_grande.move_to(UP * 0.2)
        lat_grande = tag_hud(
            "latencia = %s ms" % fmt(CODEL_1000["sin_aqm"]["espera_ms"], 1),
            font_size=22, color=C_PERDIDA)
        lat_grande.next_to(q_grande, DOWN, buff=0.35)
        self.play(FadeIn(et_enlace), FadeIn(q_grande), FadeIn(lat_grande),
                  run_time=0.8)
        self.wait(4.5)

        # --- momento: CoDel recorta la cola -----------------------------------
        rot.mostrar(pie_curso("CoDel descarta a tiempo para mantener la "
                              "cola corta: la recorta a %d paquetes." %
                              CODEL_1000["pkts_objetivo"]),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(q_grande), FadeOut(lat_grande), run_time=0.4)
        q_chica = cola(capacidad=CODEL_1000["pkts_objetivo"],
                      ocupacion=CODEL_1000["pkts_objetivo"], lado=0.50,
                      etiqueta="con CoDel: %d paquetes" %
                      CODEL_1000["pkts_objetivo"])
        q_chica.move_to(UP * 0.2)
        lat_chica = tag_hud(
            "latencia = %s ms" % fmt(CODEL_1000["con_aqm"]["espera_ms"], 1),
            font_size=22, color=C_OK)
        lat_chica.next_to(q_chica, DOWN, buff=0.35)
        self.play(FadeIn(q_chica), FadeIn(lat_chica), run_time=0.8)
        self.wait(4.2)

        # --- momento: la tabla y el veredicto -----------------------------------
        rot.mostrar(pie_curso("%sx mejor, quedandose solo con el %s%% de "
                              "la cola." % (fmt(CODEL_1000["veces_mejor"], 0),
                                           fmt(CODEL_PCT_QUEDA, 1))),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_enlace), FadeOut(lat_chica), run_time=0.4)
        t = tabla(
            ["", "cola", "latencia"],
            [["sin AQM", "1000",
              "%s ms" % fmt(CODEL_1000["sin_aqm"]["espera_ms"], 1)],
             ["con CoDel", str(CODEL_1000["pkts_objetivo"]),
              "%s ms" % fmt(CODEL_1000["con_aqm"]["espera_ms"], 1)]],
            anchos=[2.1, 1.5, 2.0], alto=0.48, fs=17)
        t.next_to(q_chica, DOWN, buff=0.7)
        self.play(FadeIn(t), run_time=0.8)
        self.wait(4.6)

        rot.mostrar(pie_curso("Es preferible perder un paquete que "
                              "esconder medio segundo."),
                    zona="abajo", run_time=0.5)
        self.wait(8.5)
