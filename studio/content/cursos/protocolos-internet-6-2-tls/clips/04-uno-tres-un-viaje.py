class Clip4(Scene):
    """6.2.4 - 1.3 en un viaje: las tres barras de tls_viajes comparadas
    con la MISMA escala (1.2 = 2 RTT, 1.3 = 1 RTT, reanudado = 0 RTT) y la
    letra chica del 0-RTT, que la propia libreria devuelve. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        rot.mostrar(titulo_curso("1.3: un viaje"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        X0, ALTO_B = -2.4, 0.46
        YS = (1.75, 0.55, -0.65)

        def fila(i):
            """La barra i: tramo azul de TCP + tramo fucsia de TLS, a la
            misma escala en las tres. Todo sale de BARRAS_TLS."""
            nombre, tls_rtt, total_rtt, ms = BARRAS_TLS[i]
            y = YS[i]
            etq = tag_hud(nombre, font_size=18, color=C_TENUE)
            etq.move_to(np.array([-2.62, y, 0.0]), aligned_edge=RIGHT)
            w_tcp = TCP_RTTS * UNIDAD_RTT
            s_tcp = Rectangle(width=w_tcp, height=ALTO_B, stroke_color=C_RED,
                              stroke_width=2.2, fill_color=C_RED,
                              fill_opacity=0.26)
            s_tcp.move_to(np.array([X0 + w_tcp / 2.0, y, 0.0]))
            t_tcp = tag_hud("TCP", font_size=15, color=C_RED)
            t_tcp.move_to(s_tcp.get_center())
            segs = VGroup(s_tcp)
            dentro = VGroup(t_tcp)
            if tls_rtt > 0:
                w_tls = tls_rtt * UNIDAD_RTT
                s_tls = Rectangle(width=w_tls, height=ALTO_B,
                                  stroke_color=C_CLAVE, stroke_width=2.2,
                                  fill_color=C_CLAVE, fill_opacity=0.26)
                s_tls.move_to(np.array([X0 + w_tcp + w_tls / 2.0, y, 0.0]))
                t_tls = tag_hud("%s RTT" % fmt(tls_rtt, 0), font_size=15,
                                color=C_CLAVE)
                t_tls.move_to(s_tls.get_center())
                segs.add(s_tls)
                dentro.add(t_tls)
            cifra = tag_hud("%s RTT = %3s ms" % (fmt(total_rtt, 0),
                                                 fmt(ms, 0)),
                            font_size=18, color=C_CIFRA)
            cifra.next_to(segs, RIGHT, buff=0.28)
            return etq, segs, dentro, cifra

        f1, f2, f3 = fila(0), fila(1), fila(2)
        todo = VGroup(*[m for f in (f1, f2, f3) for m in f])

        # --- momento: lo que costaba TLS 1.2 ------------------------------
        rot.mostrar(pie_curso("TLS 1.2 pedia dos viajes propios, encima "
                              "del viaje que ya cuesta TCP."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(f1[0]), *[GrowFromEdge(s, LEFT) for s in f1[1]],
                  run_time=0.8)
        self.play(FadeIn(f1[2]), FadeIn(f1[3]), run_time=0.4)
        self.wait(3.4)

        # --- momento: 1.3 recorta un viaje --------------------------------
        rot.mostrar(pie_curso("TLS 1.3 recorta su apreton a un solo viaje: "
                              "%s ms menos antes de pedir nada."
                              % fmt(AHORRO_13_MS, 0)),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(f2[0]), *[GrowFromEdge(s, LEFT) for s in f2[1]],
                  run_time=0.8)
        self.play(FadeIn(f2[2]), FadeIn(f2[3]), run_time=0.4)
        self.wait(3.4)

        # --- momento: reanudar, cero viajes de TLS ------------------------
        rot.mostrar(pie_curso("Si ya hablaste antes con el sitio, puedes "
                              "reanudar: cero viajes de TLS."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(f3[0]), *[GrowFromEdge(s, LEFT) for s in f3[1]],
                  run_time=0.8)
        self.play(FadeIn(f3[2]), FadeIn(f3[3]), run_time=0.4)
        cero = tag_hud("TLS:  %s viajes" % fmt(TLS13R["rtt"], 0),
                       font_size=17, color=C_CLAVE)
        cero.next_to(f3[3], RIGHT, buff=0.40)
        self.play(FadeIn(cero), run_time=0.4)
        self.wait(3.0)

        # --- momento: la letra chica del 0-RTT ----------------------------
        rot.mostrar(pie_curso("Pero ese viaje ahorrado no es gratis, y "
                              "conviene decirlo entero."),
                    zona="abajo", run_time=0.5)
        marco = SurroundingRectangle(cero, color=C_PERDIDA, buff=0.14,
                                     stroke_width=2.4)
        aviso = tag_hud(AVISO_0RTT, font_size=18, color=C_PERDIDA)
        aviso.move_to(DOWN * 1.90)
        self.play(Create(marco), run_time=0.5)
        self.play(FadeIn(aviso), run_time=0.5)
        self.wait(4.2)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "El candado no lo pone el sitio.",
            "Lo pone una cadena de firmas que decidiste creer.",
            "Siguiente: HTTP/2 y QUIC, el fin de la fila india.",
            todo, cero, marco, aviso, espera=4.6)
