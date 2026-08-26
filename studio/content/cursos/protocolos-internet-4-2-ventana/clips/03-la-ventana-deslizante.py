class Clip3(Scene):
    """4.2.3 - Mandar de uno en uno da un throughput ridiculo; ventana()
    y bdp() muestran cuanto hace falta en vuelo para llenar el enlace.
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La ventana deslizante")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        BAR_W, BAR_H, BAR_Y = 7.4, 0.62, 0.95
        marco = Rectangle(width=BAR_W, height=BAR_H, stroke_color=C_RED,
                          stroke_width=2.2, fill_color=C_RED,
                          fill_opacity=0.04)
        marco.move_to(UP * BAR_Y)
        et_marco = tag_hud("enlace: 100 Mb/s   RTT: 40 ms", font_size=18,
                          color=C_RED)
        et_marco.next_to(marco, UP, buff=0.18)
        izq_x = marco.get_left()[0]

        def relleno(pct):
            w = max(BAR_W * pct / 100.0, 0.02)
            r = Rectangle(width=w, height=BAR_H * 0.78, stroke_width=0,
                         fill_color=C_OK, fill_opacity=0.55)
            r.move_to([izq_x + w / 2.0, BAR_Y, 0])
            return r

        # --- momento: el BDP dice cuanto cabe en vuelo ---------------------
        rot.mostrar(pie_curso("Un enlace de 100 Mb/s con 40 ms de RTT puede "
                              "tener mucho dato viajando a la vez."),
                    zona="abajo", run_time=0.5)
        barra = relleno(0.0)
        self.play(FadeIn(marco), FadeIn(et_marco), run_time=0.7)
        self.play(FadeIn(barra), run_time=0.3)
        bdp_txt = tag_hud(
            "BDP = %d bytes (%s kB) = %d segmentos de 1460 B en vuelo"
            % (int(BDP_40["bytes"]), fmt(BDP_40["kb"], 0),
               int(round(BDP_40["segmentos_1460"]))),
            font_size=18, color=C_CIFRA)
        bdp_txt.move_to(DOWN * 0.55)
        self.play(FadeIn(bdp_txt), run_time=0.5)
        self.wait(3.6)

        # --- momento: W = 1 ------------------------------------------------
        rot.mostrar(pie_curso("Con ventana de un segmento, mandas uno y "
                              "esperas su ACK antes del siguiente."),
                    zona="abajo", run_time=0.5)
        tok1 = ficha("1", lado=0.42, fs=13, color=C_PAQUETE)
        tok1.next_to(marco, DOWN, buff=0.55).align_to(marco, LEFT)
        cifra1 = tag_hud("W=%d  ->  %s Mb/s  (%s %% del enlace)"
                         % (V1["w"], fmt(V1["mbps_real"], 2),
                            fmt(V1["pct_capacidad"], 1)),
                         font_size=18, color=C_CIFRA)
        cifra1.move_to(DOWN * 1.75)
        self.play(FadeIn(tok1), run_time=0.4)
        self.play(Transform(barra, relleno(V1["pct_capacidad"])),
                  FadeOut(bdp_txt), FadeIn(cifra1), run_time=0.7)
        self.wait(3.6)

        # --- momento: W = 10 -------------------------------------------
        rot.mostrar(pie_curso("Con diez en vuelo el uso crece, pero el "
                              "enlace sigue casi vacio."),
                    zona="abajo", run_time=0.5)
        toks10 = VGroup(*[ficha(str(i + 1), lado=0.30, fs=10,
                                color=C_PAQUETE) for i in range(10)])
        toks10.arrange(RIGHT, buff=0.08)
        toks10.next_to(marco, DOWN, buff=0.55).align_to(marco, LEFT)
        cifra10 = tag_hud("W=%d  ->  %s Mb/s  (%s %% del enlace)"
                          % (V10["w"], fmt(V10["mbps_real"], 2),
                             fmt(V10["pct_capacidad"], 1)),
                          font_size=18, color=C_CIFRA)
        cifra10.move_to(DOWN * 1.75)
        self.play(FadeOut(tok1), FadeIn(toks10), run_time=0.4)
        self.play(Transform(barra, relleno(V10["pct_capacidad"])),
                  FadeOut(cifra1), FadeIn(cifra10), run_time=0.7)
        self.wait(3.4)

        # --- momento: W = 100, ya no caben cuadritos ------------------------
        rot.mostrar(pie_curso("A partir de aqui ya no caben los cuadritos "
                              "en pantalla: medimos el area, no los "
                              "contamos."),
                    zona="abajo", run_time=0.5)
        cifra100 = tag_hud("W=%d  ->  %s Mb/s  (%s %% del enlace)"
                           % (V100["w"], fmt(V100["mbps_real"], 2),
                              fmt(V100["pct_capacidad"], 1)),
                           font_size=18, color=C_CIFRA)
        cifra100.move_to(DOWN * 1.75)
        self.play(FadeOut(toks10), run_time=0.3)
        self.play(Transform(barra, relleno(V100["pct_capacidad"])),
                  FadeOut(cifra10), FadeIn(cifra100), run_time=0.8)
        self.wait(3.6)

        # --- momento: el BDP marca donde se llena -------------------------
        rot.mostrar(pie_curso("El BDP ya lo habia dicho: con %d segmentos "
                              "en vuelo, el enlace por fin se llena."
                              % W_LLENA),
                    zona="abajo", run_time=0.5)
        cifra343 = tag_hud("W=%d  ->  %s Mb/s  (limitado por %s)"
                           % (V343["w"], fmt(V343["mbps_real"], 1),
                              V343["limitado_por"]),
                           font_size=18, color=C_CIFRA)
        cifra343.move_to(DOWN * 1.75)
        self.play(Transform(barra, relleno(V343["pct_capacidad"])),
                  FadeOut(cifra100), FadeIn(cifra343), run_time=0.9)
        self.wait(5.2)
