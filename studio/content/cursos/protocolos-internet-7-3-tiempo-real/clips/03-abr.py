class Clip3(Scene):
    """7.3.3 - Sobre una traza real de ancho de banda, el video
    adaptativo baja de calidad y no se atasca; a calidad fija, sobre la
    MISMA traza, se atasca. Por que prefiere borroso a parado. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("ABR: escoger calidad")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el adaptativo decide cada segmento --------------------
        rot.mostrar(pie_curso("Sobre una traza real de ancho de banda, "
                              "el video decide su calidad cada 4 "
                              "segundos."),
                    zona="abajo", run_time=0.5)
        s = sierra(ABR_TRAZA_MBPS, ancho=7.4, alto=2.6, color=C_PAQUETE,
                   media=True, etiqueta="calidad elegida (Mb/s)")
        s.move_to(UP * 0.75)
        et_media = tag_hud("media %s Mb/s" % fmt(s.valor_medio, 2),
                           font_size=15, color=C_CIFRA)
        et_media.next_to(s.media, RIGHT, buff=0.10).shift(UP * 0.10)
        self.play(FadeIn(s.ejes), run_time=0.4)
        self.play(Create(s.curva), run_time=2.2)
        self.play(Create(s.media), FadeIn(et_media), run_time=0.6)
        et_resumen = tag_hud("%d segmentos   %d cambios de calidad"
                             % (ABR_N, ABR["cambios"]), font_size=19)
        et_resumen.next_to(s, DOWN, buff=0.32)
        self.play(FadeIn(et_resumen), run_time=0.5)
        self.wait(3.6)

        # --- momento: nunca se atasca -----------------------------------------
        rot.mostrar(pie_curso("Y no se atasca: baja de calidad antes de "
                              "vaciar el bufer del reproductor."),
                    zona="abajo", run_time=0.5)
        filas = [["%d" % (i + 1), "%s Mb/s" % fmt(ABR["decisiones"][i][
                  "ancho"], 2), "%s Mb/s" % fmt(ABR["decisiones"][i][
                  "mbps"], 1)] for i in range(8, 14)]
        t = tabla(["segmento", "ancho medido", "calidad elegida"], filas,
                 anchos=[1.5, 2.0, 2.0], alto=0.38, fs=15)
        t.move_to(DOWN * 0.55)
        for i in range(6):
            t.celda(i, 2).set_color(C_CIFRA)
        self.play(FadeOut(s), FadeOut(et_media), FadeOut(et_resumen),
                  run_time=0.4)
        self.play(FadeIn(t), run_time=0.7)
        et_cero = tag_hud("0 atascos en los %d segmentos" % ABR_N,
                          font_size=21, color=C_OK)
        et_cero.next_to(t, DOWN, buff=0.30)
        self.play(FadeIn(et_cero, shift=0.12 * UP), run_time=0.5)
        self.wait(3.4)

        # --- momento: a calidad fija, se atasca --------------------------------
        rot.mostrar(pie_curso("A calidad FIJA, sobre la MISMA traza, la "
                              "historia es otra."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(t), FadeOut(et_cero), run_time=0.5)

        def fila_atascos(etiqueta, n_atascos, color):
            marca = tag_hud(etiqueta, font_size=18, color=C_EJE)
            cuad = VGroup(*[ficha("", lado=0.17, color=color)
                           for _ in range(n_atascos)])
            cuad.arrange(RIGHT, buff=0.05)
            cifra = tag_hud("%d atascos" % n_atascos, font_size=18,
                            color=color)
            fila = VGroup(marca, cuad, cifra).arrange(RIGHT, buff=0.24)
            return fila

        f15 = fila_atascos("1.5 Mb/s", AF_15["atascos"], C_PERDIDA)
        f30 = fila_atascos("3.0 Mb/s", AF_30["atascos"], C_PERDIDA)
        f60 = fila_atascos("6.0 Mb/s", AF_60["atascos"], C_PERDIDA)
        filas_atasco = VGroup(f15, f30, f60).arrange(
            DOWN, buff=0.36, aligned_edge=LEFT)
        filas_atasco.move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(f, shift=0.15 * UP)
                                for f in filas_atasco], lag_ratio=0.35),
                  run_time=1.8)
        self.wait(4.2)

        # --- momento: por que no es magia --------------------------------------
        rot.mostrar(pie_curso("No es magia: el adaptativo no se atasca "
                              "PORQUE cambia de calidad. Prefiere "
                              "borroso a parado."),
                    zona="abajo", run_time=0.5)
        et_final = tag_hud("adaptativo: 0 atascos, media %s Mb/s"
                           % fmt(ABR["calidad_media"], 2), font_size=20,
                           color=C_OK)
        et_final.next_to(filas_atasco, DOWN, buff=0.40)
        self.play(FadeIn(et_final, shift=0.12 * UP), run_time=0.5)
        self.wait(6.5)
