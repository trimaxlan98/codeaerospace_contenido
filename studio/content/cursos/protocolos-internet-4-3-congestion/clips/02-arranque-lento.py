class Clip2(Scene):
    """4.3.2 - Arranque lento: cwnd se DUPLICA cada RTT hasta el umbral y
    luego sube de uno en uno. 4 RTT exponenciales MEDIDOS antes de pasar a
    lineal. Sondear sin creerse dueno del enlace. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Arranque lento")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: nadie sabe cuanto cabe ------------------------------
        rot.mostrar(pie_curso("Nadie le dice a TCP cuanto cabe en el camino. "
                              "Empieza con un segmento y pregunta."),
                    zona="abajo", run_time=0.5)
        s = sierra(SLOW_TRAZA, perdidas=(), ancho=6.6, alto=2.55,
                   color=C_PAQUETE, media=False,
                   etiqueta="cwnd (segmentos) frente a RTT")
        s.move_to(UP * 0.72)
        self.play(FadeIn(s.ejes), FadeIn(s.etiqueta), run_time=0.6)
        self.play(Create(s.curva), run_time=2.4)
        self.wait(2.4)

        # --- momento: duplicar cada RTT -----------------------------------
        rot.mostrar(pie_curso("Cada vez que llega un acuse, la ventana se "
                              "DUPLICA. Uno, dos, cuatro, ocho..."),
                    zona="abajo", run_time=0.5)
        puntos = VGroup()
        valores = VGroup()
        for i in range(SLOW_EXP + 1):
            p = Dot(s.punto(i), radius=0.07, color=C_CIFRA)
            v = tag_hud("%d" % int(SLOW_TRAZA[i]), font_size=19)
            v.next_to(p, UP if i else RIGHT, buff=0.14)
            puntos.add(p)
            valores.add(v)
        self.play(LaggedStart(*[AnimationGroup(FadeIn(p, scale=1.5),
                                               FadeIn(v))
                                for p, v in zip(puntos, valores)],
                              lag_ratio=0.42), run_time=2.0)
        et_exp = tag_hud("x2 por RTT:  solo %d RTT para pasar de %d a %d "
                         "segmentos"
                         % (SLOW_EXP, int(SLOW_TRAZA[0]),
                            int(SLOW_SSTHRESH)), font_size=21)
        et_exp.move_to(DOWN * 1.72)
        self.play(FadeIn(et_exp), run_time=0.5)
        self.wait(4.4)

        # --- momento: el umbral y la fase lineal --------------------------
        rot.mostrar(pie_curso("Al llegar al umbral deja de duplicar: a "
                              "partir de ahi sube de uno en uno."),
                    zona="abajo", run_time=0.5)
        y_um = s.punto(SLOW_EXP)[1]
        x0, x1 = s.punto(0)[0], s.punto(len(SLOW_TRAZA) - 1)[0]
        umbral = DashedLine(np.array([x0, y_um, 0.0]),
                            np.array([x1, y_um, 0.0]),
                            color=C_COLA, stroke_width=1.8, dash_length=0.10)
        # Rotulo CORTO: "umbral (ssthresh) = 16" llega hasta el punto
        # donde la curva cruza la linea y pisa su valor.
        et_um = tag_hud("ssthresh = %d" % int(SLOW_SSTHRESH),
                        font_size=18, color=C_COLA)
        # A la IZQUIERDA y ARRIBA de la linea: a la derecha la cruzan la
        # curva y los puntos de la fase lineal.
        et_um.next_to(umbral, UP, buff=0.10).shift(LEFT * 2.3)
        self.play(FadeOut(et_exp), run_time=0.3)
        self.play(Create(umbral), FadeIn(et_um), run_time=0.7)
        lineales = VGroup(*[Dot(s.punto(i), radius=0.06, color=C_OK)
                            for i in range(SLOW_EXP + 1, len(SLOW_TRAZA))])
        self.play(LaggedStart(*[FadeIn(p, scale=1.4) for p in lineales],
                              lag_ratio=0.16), run_time=1.1)
        et_lin = tag_hud("+1 por RTT:  %s"
                         % "  ".join("%d" % int(v) for v in SLOW_LINEAL),
                         font_size=21, color=C_OK)
        et_lin.move_to(DOWN * 1.72)
        self.play(FadeIn(et_lin), run_time=0.5)
        self.wait(4.6)

        # --- momento: el tubo que hay que llenar --------------------------
        rot.mostrar(pie_curso("Duplicar no es lento: es la unica forma de "
                              "encontrar el techo sin tumbarlo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_lin), run_time=0.3)
        et_tubo = tag_hud("el tubo de %s Mb/s con %s ms de ida y vuelta "
                          "son %d segmentos en vuelo"
                          % (fmt(TUBO_MBPS, 0), fmt(TUBO_RTT, 0), TUBO_SEG),
                          font_size=20)
        et_tubo.move_to(DOWN * 1.62)
        self.play(FadeIn(et_tubo), run_time=0.5)
        self.wait(5.6)
