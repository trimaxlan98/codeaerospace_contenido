class Clip1(Scene):
    """6.2.1 - El apreton: la escalera de TLS 1.2 ENCIMA de la de TCP, con
    los RTT contados y SUMADOS antes del primer byte de HTTP. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        rot.mostrar(titulo_curso("El apreton"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        esc = escalera(["cliente", "servidor"], EVENTOS_TLS12, ancho=4.6,
                       alto=4.3, fs=17)
        esc.shift(LEFT * 2.25 + UP * 0.05)

        cab = tag_hud("antes del 1er byte de HTTP", font_size=16,
                      color=C_TENUE)
        l_tcp = tag_hud("TCP        %s RTT = %3s ms"
                        % (fmt(TCP_RTTS, 0), fmt(TCP_ANTES_MS, 0)),
                        font_size=18, color=C_RED)
        l_tls = tag_hud("TLS 1.2    %s RTT = %3s ms"
                        % (fmt(TLS12["rtt"], 0),
                           fmt(TLS12["rtt"] * RTT_MS, 0)),
                        font_size=18, color=C_CLAVE)
        raya = Line(LEFT * 1.9, RIGHT * 1.9, color=C_EJE, stroke_width=1.6)
        l_tot = tag_hud("total      %s RTT = %3s ms"
                        % (fmt(APRETON_12, 0), fmt(MS_12, 0)),
                        font_size=18, color=C_CIFRA)
        panel = VGroup(cab, l_tcp, l_tls, raya, l_tot)
        panel.arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        panel.move_to(RIGHT * 4.12 + UP * 0.55)

        # --- momento: primero hay que estar conectado ---------------------
        rot.mostrar(pie_curso("Antes de cifrar nada hay que estar "
                              "conectado: eso ya cuesta un viaje."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(esc.actores), Create(esc.vidas), run_time=0.9)
        for k in IDX_TCP:
            self.play(Create(esc.paso(k)), run_time=0.5)
        self.wait(2.6)

        # --- momento: encima empieza OTRO apreton -------------------------
        rot.mostrar(pie_curso("Sobre esa conexion recien empieza el "
                              "apreton de TLS: el sitio manda su "
                              "certificado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cab), FadeIn(l_tcp), run_time=0.5)
        for k in IDX_TLS_1:
            self.play(Create(esc.paso(k)), run_time=0.55)
        self.wait(3.2)

        # --- momento: el segundo viaje de TLS 1.2 -------------------------
        rot.mostrar(pie_curso("Segundo viaje: se acuerda la clave y cada "
                              "lado firma lo que oyo con un Finished."),
                    zona="abajo", run_time=0.5)
        for k in IDX_TLS_2:
            self.play(Create(esc.paso(k)), run_time=0.55)
        self.play(FadeIn(l_tls), run_time=0.5)
        self.wait(3.4)

        # --- momento: recien ahi viaja el primer byte de HTTP -------------
        rot.mostrar(pie_curso("Recien ahora viaja el primer byte de HTTP, "
                              "y los viajes no se solapan: se suman."),
                    zona="abajo", run_time=0.5)
        for k in IDX_HTTP:
            self.play(Create(esc.paso(k)), run_time=0.6)
        self.play(Create(raya), FadeIn(l_tot), run_time=0.6)
        self.wait(4.0)

        # --- momento: el precio del candado -------------------------------
        rot.mostrar(pie_curso("%s ms de ida y vuelta antes de pedir la "
                              "pagina. Por eso existe TLS 1.3."
                              % fmt(MS_12, 0)),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(l_tot, color=C_CIFRA, scale_factor=1.12),
                  run_time=0.8)
        self.wait(4.2)
