class Clip4(Scene):
    """2.1.4 - El mismo tono debil (-125.0 dBm, gris) en 2 kHz: con el LNA
    en la antena la SNR medida es 14.9 dB; con el LNA en el escritorio (el
    cable primero) baja a 12.0 dB. Cierre de la leccion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El LNA en la antena"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        ancho_cad = 7.6
        cad_a = S.Cadena(("ANTENA", "LNA", "CABLE", "RECEPTOR"),
                         ancho_total=ancho_cad, alto=0.68, tamano=17)
        cad_a.move_to(LEFT * 2.3 + UP * 1.75)
        cad_b = S.Cadena(("ANTENA", "CABLE", "LNA", "RECEPTOR"),
                         ancho_total=ancho_cad, alto=0.68, tamano=17)
        cad_b.move_to(LEFT * 2.3 + UP * -1.3)

        etq_a = tag_dato("LNA en la antena", font_size=19)
        etq_a.next_to(cad_a, UP, buff=0.22).align_to(cad_a, LEFT)
        etq_b = tag_dato("LNA en el escritorio", font_size=19)
        etq_b.next_to(cad_b, UP, buff=0.22).align_to(cad_b, LEFT)
        p_debil = tag_dato(f"{fmt(P_DEBIL, 1)} dBm", font_size=17)
        p_debil.next_to(cad_a.bloques[0], DOWN, buff=0.14)

        self.play(FadeIn(etq_a), FadeIn(cad_a), run_time=1.0)
        self.play(FadeIn(p_debil), run_time=0.5)
        self.wait(2.0)
        self.play(FadeIn(etq_b), FadeIn(cad_b), run_time=1.0)
        self.wait(2.2)
        self.wait(1.6)

        max_snr = 15.0
        largo_max = 3.0

        def barra_snr(cadena, valor):
            largo = max(largo_max * valor / max_snr, 0.05)
            y = cadena.get_center()[1]
            x0 = cadena.bloques[-1].get_right()[0] + 0.35
            r = Rectangle(width=largo, height=0.42, stroke_width=0,
                         fill_color=C_CALCULO, fill_opacity=0.85)
            r.move_to(np.array([x0 + largo / 2, y, 0.0]))
            return r

        barra_a = barra_snr(cad_a, SNR_ANT)
        cif_a = tag_hud(f"{fmt(SNR_ANT, 1)} dB", font_size=20)
        cif_a.next_to(barra_a, RIGHT, buff=0.18)
        self.play(GrowFromEdge(barra_a, LEFT), FadeIn(cif_a), run_time=1.0)
        rot.mostrar(cifra_pie(f"SNR: {fmt(SNR_ANT, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        barra_b = barra_snr(cad_b, SNR_ESC)
        cif_b = tag_hud(f"{fmt(SNR_ESC, 1)} dB", font_size=20)
        cif_b.next_to(barra_b, RIGHT, buff=0.18)
        self.play(GrowFromEdge(barra_b, LEFT), FadeIn(cif_b), run_time=1.0)
        rot.mostrar(cifra_pie(f"SNR: {fmt(SNR_ESC, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.6)

        cierre_leccion(self, rot, "El ruido lo pone el primer eslabon.",
                       "Amplifica antes de perder.", cad_a, cad_b, etq_a,
                       etq_b, p_debil, barra_a, cif_a, barra_b, cif_b,
                       espera=6.5)
