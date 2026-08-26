class Clip3(Scene):
    """8.3.3 - Una imagen de 8 MB del rover al centro de control: tres
    tramos medidos, y 12.5 de los 15.1 minutos son solo luz. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Un archivo a Marte")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el primer tramo, el corto ---------------------------
        rot.mostrar(pie_curso("Una imagen de %s MB sale de un rover. Tres "
                              "tramos, tres tecnologias distintas."
                              % fmt(VIAJE_MB, 0)),
                    zona="abajo", run_time=0.5)
        eventos = [{"de": de, "a": a,
                    "texto": "%s  %s" % (t["enlace"], tasa(t["mbps"]))}
                   for t, (de, a) in zip(TRAMOS, ACTORES_PARES)]
        esc = escalera(ACTORES_VIAJE, eventos, ancho=8.0, alto=2.7, fs=15,
                       mostrar_tiempo=False)
        esc.shift(RIGHT * 0.45 + UP * 0.30)
        # `Escalera` rotula el tiempo en ms; aqui el eje son MINUTOS, asi
        # que las marcas se ponen a mano en la misma columna.
        marcas = VGroup(*[
            tag_hud("%s min" % fmt(ACUM_MIN[k], 1), font_size=17)
            for k in range(len(TRAMOS))])
        for k, m in enumerate(marcas):
            m.move_to(np.array([X_MARCAS, esc.flecha(k).get_start()[1], 0.0]))
        self.play(FadeIn(esc.vidas), FadeIn(esc.actores), run_time=0.9)
        self.play(Create(esc.paso(0)), FadeIn(marcas[0]), run_time=0.8)
        self.wait(4.8)

        # --- momento: el salto largo --------------------------------------
        rot.mostrar(pie_curso("El salto largo: banda X, y %s millones de "
                              "kilometros de por medio."
                              % fmt(MKM_VIAJE, 0)),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(1)), FadeIn(marcas[1]), run_time=0.8)
        et_lento = tag_hud("el tramo lento del viaje:  %s" % LENTO,
                           font_size=19, color=C_COLA)
        et_lento.move_to(np.array([-1.55, -1.95, 0.0]))
        self.play(FadeIn(et_lento), run_time=0.5)
        self.wait(4.6)

        # --- momento: el tramo terrestre no se nota ------------------------
        rot.mostrar(pie_curso("El ultimo tramo es de casa: por fibra, la "
                              "imagen entera no llega ni a un decimo de "
                              "segundo."),
                    zona="abajo", run_time=0.5)
        self.play(Create(esc.paso(2)), FadeIn(marcas[2]), run_time=0.8)
        et_total = tag_hud("total: %s min" % fmt(VIAJE_MIN, 1), font_size=21,
                           color=C_PAQUETE)
        et_total.next_to(esc.flecha(2), DOWN, buff=0.42)
        self.play(FadeIn(et_total), run_time=0.5)
        self.wait(4.8)

        # --- momento: donde se fue el tiempo -------------------------------
        rot.mostrar(pie_curso("El cuello de botella no es el cable lento: "
                              "son doce minutos y medio de pura luz."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(esc), FadeOut(marcas), FadeOut(et_total),
                  FadeOut(et_lento), run_time=0.7)
        w_tx = ANCHO_BARRA * VIAJE_TX_PCT / 100.0
        w_luz = ANCHO_BARRA * VIAJE_LUZ_PCT / 100.0
        s_tx = Rectangle(width=w_tx, height=0.56, stroke_color=C_COLA,
                         stroke_width=2.2, fill_color=C_COLA,
                         fill_opacity=0.35)
        s_luz = Rectangle(width=w_luz, height=0.56, stroke_color=C_CIFRA,
                          stroke_width=2.2, fill_color=C_CIFRA,
                          fill_opacity=0.20)
        barra = VGroup(s_tx, s_luz).arrange(RIGHT, buff=0.0)
        barra.move_to(UP * 0.85)
        et_tx = VGroup(
            tag_hud("transmitir", font_size=17, color=C_COLA),
            tag_hud("%s %%" % fmt(VIAJE_TX_PCT, 1), font_size=17,
                    color=C_COLA),
        ).arrange(DOWN, buff=0.10)
        et_tx.next_to(s_tx, DOWN, buff=0.26)
        et_luz = VGroup(
            tag_hud("luz en camino", font_size=17),
            tag_hud("%s min  =  %s %%" % (fmt(VIAJE_LUZ_MIN, 1),
                                          fmt(VIAJE_LUZ_PCT, 1)),
                    font_size=17),
        ).arrange(DOWN, buff=0.10)
        et_luz.next_to(s_luz, DOWN, buff=0.26)
        et_arriba = tag_hud("los %s min del viaje, de punta a punta"
                            % fmt(VIAJE_MIN, 1), font_size=19,
                            color=C_PAQUETE)
        et_arriba.next_to(barra, UP, buff=0.30)
        self.play(FadeIn(barra), FadeIn(et_arriba), run_time=0.8)
        self.play(FadeIn(et_tx), FadeIn(et_luz), run_time=0.6)
        self.wait(2.6)
        et_contra = tag_hud("y si la banda X fuera instantanea:  %s min"
                            % fmt(SIN_CUELLO_MIN, 1), font_size=20,
                            color=C_TENUE)
        et_contra.move_to(DOWN * 1.72)
        self.play(FadeIn(et_contra, shift=0.12 * UP), run_time=0.6)
        self.wait(4.8)
