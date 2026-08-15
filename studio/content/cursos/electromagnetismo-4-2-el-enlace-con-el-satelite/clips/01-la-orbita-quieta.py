class Clip1(Scene):
    """4.2.1 - La orbita quieta: pedir que la vuelta dure un dia SIDERAL
    fija el radio en 42 164 km. Nadie eligio los 35 786 km de altura: los
    eligio la gravedad. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La órbita quieta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la Tierra y su cielo vacio --------------------------
        mor = mapa_orbitas(radio_tierra=R_MAPA, con_cinturones=False)
        mor.move_to(LEFT * 2.9 + DOWN * 0.15)
        rot.mostrar(pie_curso("El plato del balcón no se mueve nunca. "
                              "Alguien tuvo que aparcar ahí arriba."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mor.tierra, scale=1.3), run_time=0.6)
        self.wait(4.6)

        # --- momento: las tres orbitas de trabajo, a escala ---------------
        leyenda = VGroup(
            tag_hud(f"LEO      {H_LEO / 1e3:,.0f} km".replace(",", " ")),
            tag_hud(f"GPS     {H_GPS / 1e3:,.0f} km".replace(",", " ")),
            tag_hud(f"GEO     {ALT_GEO / 1e3:,.0f} km".replace(",", " ")),
            tag_hud(f"radio   {R_GEO / 1e3:,.0f} km".replace(",", " ")),
            tag_hud(f"vuelta  {mor.periodo_horas('GEO'):.1f} h"))
        leyenda.arrange(DOWN, aligned_edge=LEFT, buff=0.36)
        leyenda.move_to(RIGHT * 3.9 + UP * 0.15)

        rot.mostrar(pie_curso("Estas son las alturas de trabajo, "
                              "dibujadas a escala de verdad."),
                    zona="abajo", run_time=0.5)
        self.play(Create(mor.orbita("LEO")),
                  FadeIn(leyenda[0], shift=0.15 * RIGHT), run_time=0.8)
        self.play(Create(mor.orbita("GPS")),
                  FadeIn(leyenda[1], shift=0.15 * RIGHT), run_time=0.9)
        self.wait(4.4)

        # --- momento: la peticion que fija el radio ------------------------
        rot.mostrar(pie_curso("Cuanto más alto, más lenta la vuelta. ¿Y "
                              "si pedimos que dure exactamente un día?"),
                    zona="abajo", run_time=0.5)
        self.play(Create(mor.orbita("GEO")),
                  FadeIn(leyenda[2], shift=0.15 * RIGHT), run_time=1.0)
        self.wait(4.6)

        rot.mostrar(formula_pie(r"r = \left(\frac{\mu\,T^{2}}"
                                r"{4\pi^{2}}\right)^{1/3}"),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(leyenda[3], shift=0.15 * RIGHT), run_time=0.5)
        self.wait(4.4)

        # --- momento: el dia sideral, no el solar --------------------------
        rot.mostrar(pie_curso("Ojo: el día SIDERAL, el de las estrellas. "
                              "Casi cuatro minutos más corto."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(leyenda[4], shift=0.15 * RIGHT), run_time=0.5)
        self.wait(4.6)

        # --- momento: el satelite aparcado ---------------------------------
        sat_pt = mor.punto_orbita("GEO", 35.0)
        centro = mor.tierra.get_center()
        sat = Dot(sat_pt, radius=0.09, color=C_CARGA)
        enlace = DashedLine(centro + normalize(sat_pt - centro) * R_MAPA,
                            sat_pt, stroke_width=1.8, color=C_ONDA,
                            dash_length=0.09)
        rot.mostrar(pie_curso("Ahí queda: quieto sobre el mismo punto del "
                              "ecuador. Por eso tu antena no se mueve."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(sat, scale=1.6), Create(enlace), run_time=0.7)
        self.wait(4.8)
