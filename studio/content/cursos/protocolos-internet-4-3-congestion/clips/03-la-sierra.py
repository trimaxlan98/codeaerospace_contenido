class Clip3(Scene):
    """4.3.3 - AIMD: sumar uno por RTT, partir por la mitad al perder. La
    sierra de TCP Reno con las tres perdidas marcadas en rojo, los cortes
    MEDIDOS y la media MEDIDA sobre la ventana dibujada. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La sierra")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la forma de TCP -------------------------------------
        rot.mostrar(pie_curso("Asi se ve una conexion TCP que dura: no una "
                              "linea, una sierra."),
                    zona="abajo", run_time=0.5)
        s = sierra(RENO_TRAZA, perdidas=RENO_PERDIDAS, ancho=7.4, alto=2.50,
                   color=C_PAQUETE, y_max=Y_MAX_SIERRA, media=True,
                   etiqueta="cwnd (segmentos) a lo largo de %d RTT"
                            % RENO_RTTS)
        s.move_to(UP * 0.95)
        self.play(FadeIn(s.ejes), FadeIn(s.etiqueta), run_time=0.6)
        self.play(Create(s.curva), run_time=2.8)
        self.wait(2.8)

        # --- momento: sumar uno -------------------------------------------
        rot.mostrar(pie_curso("Mientras nada se pierde, suma UN segmento "
                              "por cada ida y vuelta. Sin prisa."),
                    zona="abajo", run_time=0.5)
        i0, i1 = RENO_PERDIDAS[0] + 3, RENO_PERDIDAS[1] - 1
        rampa = Line(s.punto(i0), s.punto(i1), color=C_OK, stroke_width=5.0)
        et_mas = tag_hud("+1 por RTT", font_size=20, color=C_OK)
        et_mas.move_to(s.punto((i0 + i1) // 2) + UP * 0.44)
        self.play(Create(rampa), run_time=1.0)
        self.play(FadeIn(et_mas), run_time=0.4)
        self.wait(4.6)

        # --- momento: partir por la mitad ---------------------------------
        rot.mostrar(pie_curso("Y en cuanto se pierde un paquete, parte la "
                              "ventana por la mitad. Sin discutir."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(rampa), FadeOut(et_mas), run_time=0.4)
        caidas = VGroup(*[
            Arrow(s.punto(p), s.punto(p + 1), buff=0.0, color=C_PERDIDA,
                  stroke_width=3.0, max_tip_length_to_length_ratio=0.28)
            for p in RENO_PERDIDAS])
        self.play(LaggedStart(*[FadeIn(m, scale=1.8) for m in s.marcas],
                              lag_ratio=0.30), run_time=0.9)
        self.play(LaggedStart(*[GrowArrow(a) for a in caidas],
                              lag_ratio=0.30), run_time=0.9)
        t_cortes = tabla(
            ["RTT", "cwnd antes", "cwnd despues"],
            [[str(int(r)), fmt(a, 1), fmt(d, 1)] for r, a, d in RENO_CORTES],
            anchos=[1.5, 2.3, 2.5], alto=0.42, fs=17)
        t_cortes.move_to(DOWN * 1.70)
        self.play(FadeIn(t_cortes), run_time=0.6)
        self.wait(4.6)

        # --- momento: la media medida -------------------------------------
        rot.mostrar(pie_curso("El emisor casi nunca usa su pico: usa el "
                              "promedio de la sierra."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(t_cortes), run_time=0.4)
        self.play(Create(s.media), run_time=0.8)
        cifras = VGroup(
            tag_hud("pico de la ventana          %d segmentos"
                    % int(RENO_PICO), font_size=20, color=C_PAQUETE),
            tag_hud("media MEDIDA en estos %d RTT  %s segmentos"
                    % (RENO_RTTS, fmt(RENO_MEDIA, 2)), font_size=20),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.move_to(DOWN * 1.80)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.0)
        self.wait(5.4)
