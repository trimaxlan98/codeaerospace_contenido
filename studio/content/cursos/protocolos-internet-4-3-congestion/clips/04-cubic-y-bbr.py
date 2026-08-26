class Clip4(Scene):
    """4.3.4 - CUBIC y BBR. La trampa de este clip: en una ventana corta la
    MEDIA de CUBIC es MENOR que la de Reno, y compararlas diria que CUBIC es
    peor. Lo que de verdad los separa es el tiempo en volver a llenar el
    tubo tras una perdida: Reno depende del RTT y CUBIC no. A RTT corto gana
    Reno; a RTT largo gana CUBIC. Cierre de la leccion. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("CUBIC y BBR")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las dos sierras, misma escala -----------------------
        rot.mostrar(pie_curso("Reno y CUBIC, con las mismas tres perdidas "
                              "y la misma escala."),
                    zona="abajo", run_time=0.5)
        s_reno = sierra(RENO_TRAZA, perdidas=RENO_PERDIDAS, ancho=5.6,
                        alto=2.05, color=C_PAQUETE, y_max=Y_MAX_SIERRA,
                        media=True, etiqueta="TCP Reno")
        s_reno.move_to(UP * 1.20 + LEFT * 3.35)
        s_cub = sierra(CUBIC_TRAZA, perdidas=RENO_PERDIDAS, ancho=5.6,
                       alto=2.05, color=C_CAPA, y_max=Y_MAX_SIERRA,
                       media=True, etiqueta="CUBIC (el de Linux)")
        s_cub.move_to(UP * 1.20 + RIGHT * 3.35)
        self.play(FadeIn(s_reno.ejes), FadeIn(s_reno.etiqueta),
                  FadeIn(s_cub.ejes), FadeIn(s_cub.etiqueta), run_time=0.5)
        self.play(Create(s_reno.curva), Create(s_cub.curva), run_time=1.8)
        self.play(FadeIn(s_reno.marcas, scale=1.6),
                  FadeIn(s_cub.marcas, scale=1.6), run_time=0.7)
        self.wait(1.8)

        # --- momento: la media engana ---------------------------------------
        rot.mostrar(pie_curso("En esta ventana corta la media de CUBIC es "
                              "MENOR. Compararlas aqui seria mentir."),
                    zona="abajo", run_time=0.5)
        self.play(Create(s_reno.media), Create(s_cub.media), run_time=0.6)
        m_reno = tag_hud("media  %s" % fmt(RENO_MEDIA, 2), font_size=20,
                         color=C_PAQUETE)
        m_reno.next_to(s_reno.ejes, DOWN, buff=0.26)
        m_cub = tag_hud("media  %s" % fmt(CUBIC_MEDIA, 2), font_size=20,
                        color=C_CAPA)
        m_cub.next_to(s_cub.ejes, DOWN, buff=0.26)
        self.play(FadeIn(m_reno), FadeIn(m_cub), run_time=0.6)
        self.wait(3.4)

        # --- momento: lo que de verdad los separa -------------------------
        rot.mostrar(pie_curso("Lo que los separa es otra cosa: cuanto "
                              "tardan en volver a llenar el tubo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(s_reno.ejes), FadeOut(s_reno.etiqueta),
                  FadeOut(s_reno.curva), FadeOut(s_reno.marcas),
                  FadeOut(s_reno.media), FadeOut(m_reno),
                  FadeOut(s_cub.ejes), FadeOut(s_cub.etiqueta),
                  FadeOut(s_cub.curva), FadeOut(s_cub.marcas),
                  FadeOut(s_cub.media), FadeOut(m_cub), run_time=0.6)
        cap = tag_hud("volver a llenar una ventana de %d segmentos tras "
                      "una perdida" % TUBO_SEG, font_size=19, color=C_EJE)
        cap.move_to(UP * 1.72)
        t_rec = tabla(
            ["RTT", "Reno", "CUBIC", "recupera antes"],
            [[fmt(r["rtt_ms"], 0) + " ms", fmt(r["reno_s"], 1) + " s",
              fmt(r["cubic_s"], 2) + " s", GANADOR(r)] for r in RECUP],
            anchos=[1.7, 1.9, 1.9, 3.1], alto=0.46, fs=18)
        t_rec.move_to(UP * 0.32)
        self.play(FadeIn(cap), run_time=0.4)
        self.play(FadeIn(t_rec), run_time=0.7)
        self.wait(3.9)

        # --- momento: por que ----------------------------------------------
        rot.mostrar(pie_curso("Reno sube un segmento por RTT: su reloj es "
                              "el RTT. El de CUBIC son segundos."),
                    zona="abajo", run_time=0.5)
        razon = VGroup(
            tag_hud("Reno   %d RTT de +1 segmento  ->  con RTT largo, eterno"
                    % int(RECUP_RENO_RTTS), font_size=19, color=C_PAQUETE),
            tag_hud("CUBIC  %s s  ->  la misma cifra con cualquier RTT"
                    % fmt(RECUP_CUBIC_S, 2), font_size=19, color=C_CAPA),
            tag_hud("por eso a %s ms Reno es MAS RAPIDO y a %s ms pierde "
                    "por %sx" % (fmt(RTTS_COMPARADOS[0], 0),
                                 fmt(RTTS_COMPARADOS[2], 0),
                                 fmt(RECUP[2]["veces"], 1)),
                    font_size=19),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        razon.move_to(DOWN * 1.72)
        self.play(LaggedStart(*[FadeIn(t, shift=0.12 * UP) for t in razon],
                              lag_ratio=0.32), run_time=1.2)
        self.wait(3.7)

        # --- momento: BBR --------------------------------------------------
        rot.mostrar(pie_curso("Y hay un tercer camino: medir el cuello de "
                              "botella en vez de esperar la perdida."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(razon), run_time=0.4)
        bbr = VGroup(
            tag_hud("BBR estima el ancho de banda y el RTT minimo del "
                    "camino", font_size=19, color=C_OK),
            tag_hud("y manda a ese ritmo: la perdida deja de ser la senal",
                    font_size=19, color=C_OK),
            tag_hud("(esta libreria no lo simula: no se le pone cifra)",
                    font_size=17, color=C_EJE),
        ).arrange(DOWN, buff=0.24)
        bbr.move_to(DOWN * 1.72)
        self.play(LaggedStart(*[FadeIn(t, shift=0.12 * UP) for t in bbr],
                              lag_ratio=0.32), run_time=1.2)
        self.wait(3.5)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "Nadie obliga a tu computadora a frenar.",
            "Frena porque, si no, no funciona para nadie.",
            "Cierra el modulo 4. En el 8, el RTT sera de cientos de ms.",
            bbr, t_rec, cap, espera=4.0)
