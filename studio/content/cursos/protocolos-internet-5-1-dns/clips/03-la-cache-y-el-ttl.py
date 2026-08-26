class Clip3(Scene):
    """5.1.3 - cache_dns real: la segunda consulta se responde en un solo
    viaje, y la tasa de acierto medida crece con el TTL a cambio de tardar
    mas en poder cambiar de servidor. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La cache y el TTL")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la segunda vez no hace falta preguntar ---------------
        rot.mostrar(pie_curso("La segunda vez que alguien pregunta por el "
                              "mismo nombre, el resolutor ya la tiene a "
                              "mano."),
                    zona="abajo", run_time=0.5)
        sin_cache = tag_hud("sin cache:  %d viajes  ->  %s ms"
                            % (VIAJES_DNS, fmt(TOTAL_DNS_MS, 0)),
                            font_size=22)
        con_cache = tag_hud("con cache:  %d viaje   ->  %s ms"
                            % (VIAJES_CACHE, fmt(TOTAL_CACHE_MS, 0)),
                            font_size=22, color=C_OK)
        comp = VGroup(sin_cache, con_cache).arrange(DOWN, buff=0.32,
                                                     aligned_edge=LEFT)
        comp.move_to(UP * 0.55)
        self.play(FadeIn(sin_cache, shift=0.12 * UP), run_time=0.5)
        self.wait(1.8)
        self.play(FadeIn(con_cache, shift=0.12 * UP), run_time=0.5)
        self.wait(2.8)

        # --- momento: cuanto mas rapido ------------------------------------
        rot.mostrar(pie_curso("Sesenta y ocho veces mas rapido: toda la "
                              "diferencia entre una web que abre y una que "
                              "se piensa."),
                    zona="abajo", run_time=0.5)
        acel = tag_hud("%sx mas rapido" % fmt(ACELERACION_CACHE, 1),
                       font_size=30)
        acel.next_to(comp, DOWN, buff=0.45)
        self.play(FadeIn(acel, scale=1.15), run_time=0.6)
        self.wait(5.6)

        # --- momento: el TTL decide cuanto dura la suerte -------------------
        rot.mostrar(pie_curso("Cuanto dura esa suerte lo decide el TTL: la "
                              "tasa de acierto medida sobre una traza de "
                              "consultas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(comp), FadeOut(acel), run_time=0.4)
        filas = [["%d s" % ttl, "%s %%" % fmt(TASA_TTL[ttl], 1)]
                 for ttl in TTLS]
        tab = tabla(["TTL", "tasa de acierto"], filas,
                   anchos=[2.6, 3.8], alto=0.55, fs=17,
                   resaltar=2, resaltable=True)
        tab.move_to(UP * 0.25)
        self.play(FadeIn(tab), run_time=0.7)
        self.wait(6.0)

        # --- momento cierre del clip: el precio del TTL largo ---------------
        rot.mostrar(pie_curso("Un TTL largo acierta mas, pero cuando "
                              "expira el ciclo entero vuelve a empezar: es "
                              "el precio de poder mudarte de servidor."),
                    zona="abajo", run_time=0.5)
        self.wait(7.2)
