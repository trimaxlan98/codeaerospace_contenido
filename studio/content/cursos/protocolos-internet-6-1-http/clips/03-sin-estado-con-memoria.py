class Clip3(Scene):
    """6.1.3 - HTTP no recuerda nada entre peticiones; la cookie y la
    cache condicional le devuelven la memoria, con el ahorro MEDIDO.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Sin estado, con memoria")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: HTTP no recuerda nada ------------------------------------
        rot.mostrar(pie_curso("Cada peticion HTTP llega sin pasado: el "
                              "servidor no sabe que ya hablaste con el."),
                    zona="abajo", run_time=0.5)
        nav = nodo("host", "Navegador", 0.42)
        srv = nodo("servidor", "Servidor", 0.42)
        nav.move_to(LEFT * 4.3 + UP * 0.9)
        srv.move_to(RIGHT * 4.3 + UP * 0.9)
        # La ficha viaja POR ENCIMA de los aparatos, nunca sobre ellos
        # (si termina en el centro del nodo se le monta encima).
        camino = Line(nav.centro() + UP * 0.62, srv.centro() + UP * 0.62)
        self.play(FadeIn(nav), FadeIn(srv), run_time=0.6)

        def viaje():
            f = ficha("GET", lado=0.46)
            f.move_to(camino.get_start())
            self.play(MoveAlongPath(f, camino), run_time=0.9)
            resp = tag_hud("200 OK  ·  %d B" % BYTES_TOTAL, font_size=17,
                          color=C_OK)
            resp.next_to(srv, DOWN, buff=0.30)
            self.play(FadeOut(f), FadeIn(resp), run_time=0.4)
            return resp

        r1 = viaje()
        self.wait(1.6)
        self.play(FadeOut(r1), run_time=0.3)
        r2 = viaje()
        et_otra = tag_hud("otra vez desde cero: sin memoria de la anterior",
                         font_size=18, color=C_TENUE)
        if et_otra.width > config.frame_width - 2.6:
            et_otra.scale_to_fit_width(config.frame_width - 2.6)
        et_otra.move_to(DOWN * 0.15)
        self.play(FadeIn(et_otra), run_time=0.4)
        self.wait(3.4)

        # --- momento: la cookie devuelve memoria --------------------------------
        rot.mostrar(pie_curso("La cookie es memoria prestada: el "
                              "servidor la manda una vez y el navegador "
                              "la reenvia siempre."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(r2), FadeOut(et_otra), FadeOut(nav), FadeOut(srv),
                  run_time=0.4)
        lin_set = tag_hud('Set-Cookie: sesion=9f3a1c', font_size=17,
                          color=C_CAPA)
        lin_use = tag_hud('Cookie: sesion=9f3a1c', font_size=17,
                          color=C_PAQUETE)
        cab = VGroup(lin_set, lin_use).arrange(DOWN, buff=0.22,
                                               aligned_edge=LEFT)
        cab.move_to(LEFT * 0.7 + UP * 0.2)
        et_set = tag_hud("el servidor la fija", font_size=15, color=C_EJE)
        et_set.next_to(lin_set, RIGHT, buff=0.35)
        et_use = tag_hud("el navegador la repite", font_size=15,
                         color=C_EJE)
        et_use.next_to(lin_use, RIGHT, buff=0.35)
        self.play(FadeIn(lin_set), FadeIn(et_set), run_time=0.6)
        self.play(FadeIn(lin_use), FadeIn(et_use), run_time=0.6)
        self.wait(4.6)

        # --- momento: la cache condicional --------------------------------------
        rot.mostrar(pie_curso("La cache tambien es memoria: si ya tienes "
                              "la pagina, solo preguntas si cambio."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cab), FadeOut(et_set), FadeOut(et_use),
                  run_time=0.5)
        pk_full = paquete([("Cabecera", BYTES_PROTOCOLO,
                          "%d B" % BYTES_PROTOCOLO),
                         ("Carga util", BYTES_CUERPO,
                          "%d B" % BYTES_CUERPO)],
                        ancho=8.6, alto=0.72, color=C_CAPA,
                        color_carga=C_PAQUETE)
        pk_full.move_to(UP * 1.35)
        et_full = tag_hud("respuesta completa: %d B" % CACHE_COMPLETO,
                         font_size=18)
        et_full.next_to(pk_full, UP, buff=0.20)
        self.play(FadeIn(pk_full), FadeIn(et_full), run_time=0.7)
        self.wait(2.2)

        ancho_304 = 8.6 * CACHE_304 / CACHE_COMPLETO
        pk_304 = paquete([("If-None-Match", BYTES_PETICION,
                         "%d B" % BYTES_PETICION),
                        ("carga 304", CACHE_CABECERA_304,
                         "%d B" % CACHE_CABECERA_304)],
                       ancho=ancho_304, alto=0.72, color=C_CAPA,
                       color_carga=C_OK)
        pk_304.move_to(DOWN * 0.55).align_to(pk_full, LEFT)
        et_304 = tag_hud("304 Not Modified: %d B" % CACHE_304, font_size=18,
                        color=C_OK)
        et_304.next_to(pk_304, DOWN, buff=0.20)
        self.play(FadeIn(pk_304), FadeIn(et_304), run_time=0.7)
        self.wait(3.4)

        # --- momento: el ahorro medido -----------------------------------------
        rot.mostrar(pie_curso("Lo que no viaja, no cuesta: %d bytes "
                              "ahorrados, el %s %% menos."
                              % (CACHE_AHORRO, fmt(CACHE_AHORRO_PCT, 1))),
                    zona="abajo", run_time=0.5)
        et_ahorro = tag_hud("ahorro: %d B  (%s %%)"
                           % (CACHE_AHORRO, fmt(CACHE_AHORRO_PCT, 1)),
                           font_size=24, color=C_CIFRA)
        et_ahorro.move_to(DOWN * 2.15)
        self.play(FadeIn(et_ahorro, shift=0.14 * UP), run_time=0.6)
        self.wait(5.0)
