class Clip4(Scene):
    """3.1.4 - La fibra: el canal terrestre. 0.2 dB/km parece poco hasta
    multiplicar por Marte; vive de amplificar cada ~80 km y en el vacio no
    hay donde ponerlos. Cierre de leccion. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La fibra: el canal terrestre")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el cable, 0.2 dB por kilometro -------------------------
        rot.mostrar(pie_curso("Bajo el mar, un hilo de vidrio: 0.2 dB por "
                              "kilometro. En una ciudad, no se nota."),
                    zona="abajo", run_time=0.5)
        cable = Line(LEFT * 4.6, RIGHT * 4.6, color=C_SENAL, stroke_width=4.0)
        cable.move_to(UP * 0.9)
        et_cable = tag_hud(f"{fmt(FIBRA_DB_KM, 1)} dB/km", font_size=19,
                           color=C_CIFRA)
        et_cable.next_to(cable, UP, buff=0.2)
        self.play(Create(cable), FadeIn(et_cable), run_time=1.2)
        self.wait(2.6)

        # --- momento: la regla de tres a Marte -------------------------------
        rot.mostrar(pie_curso("Multiplica esos 0.2 dB/km por la distancia "
                              "a Marte..."),
                    zona="abajo", run_time=0.5)
        cuenta = tag_hud(f"{fmt(FIBRA_DB_KM, 1)} dB/km x "
                         f"{fmt(D_MARTE, 0)} km = "
                         f"{fmt_exp(FIBRA_A_MARTE_DB, 1)} dB",
                         font_size=19, color=C_CIFRA)
        cuenta.next_to(cable, DOWN, buff=0.55)
        self.play(FadeIn(cuenta, shift=0.15 * UP), run_time=0.8)
        self.wait(2.6)

        rot.mostrar(pie_curso("...frente a los 278 dB que cuesta el mismo "
                              "viaje por radio: la fibra no llega al "
                              "espacio."),
                    zona="abajo", run_time=0.5)
        cifra_radio = tag_hud(f"radio a Marte = {fmt(FSPL_MARTE, 1)} dB",
                              font_size=19, color=C_BANDA)
        cifra_radio.next_to(cuenta, DOWN, buff=0.3)
        self.play(FadeIn(cifra_radio, shift=0.15 * UP), run_time=0.6)
        self.wait(3.0)

        # --- momento: por que la fibra si funciona en la Tierra ---------------
        rot.mostrar(pie_curso("La fibra no muere del kilometraje: vive de "
                              "amplificar. Cada 80 km, un relevo repone "
                              "16 dB."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cuenta), FadeOut(cifra_radio), run_time=0.5)
        amplis = VGroup()
        for frac in np.linspace(0.06, 0.94, 5):
            a = Triangle(color=C_COD, fill_color=C_COD, fill_opacity=0.85,
                        stroke_width=1.4).scale(0.14)
            a.move_to(cable.point_from_proportion(frac))
            amplis.add(a)
        et_ampli = tag_hud(f"cada {fmt(AMPLI_KM, 0)} km: "
                           f"+{fmt(TRAMO_DB, 1)} dB", font_size=18,
                           color=C_COD)
        et_ampli.next_to(cable, DOWN, buff=0.4)
        self.play(LaggedStart(*[FadeIn(a, scale=0.4) for a in amplis],
                              lag_ratio=0.15), FadeIn(et_ampli), run_time=1.4)
        self.wait(2.8)

        # --- momento: el vacio no tiene donde ponerlos -------------------------
        rot.mostrar(pie_curso("En el vacio no hay donde clavar un relevo: "
                              "por eso la Tierra habla por fibra y el "
                              "espacio por radio."),
                    zona="abajo", run_time=0.5)
        enl = enlace_tierra(dist=3.0, radio_tierra=0.4, curva=0.26)
        enl.move_to(DOWN * 2.35 + LEFT * 0.2)
        cruz = VGroup(
            Line(UL * 0.09, DR * 0.09, color=C_RUIDO, stroke_width=3.0),
            Line(UR * 0.09, DL * 0.09, color=C_RUIDO, stroke_width=3.0))
        cruz.move_to(enl.camino.point_from_proportion(0.5))
        self.play(FadeIn(enl), run_time=0.8)
        self.play(FadeIn(cruz, scale=0.5), run_time=0.5)
        self.wait(2.8)

        # --- cierre de leccion -----------------------------------------------
        cierre_leccion(
            self, rot,
            "En la Tierra, la luz viaja acompañada.",
            "En el espacio, la señal va sola.",
            "Siguiente leccion: Doppler, la frecuencia que se corre.",
            cable, et_cable, amplis, et_ampli, enl, cruz)
