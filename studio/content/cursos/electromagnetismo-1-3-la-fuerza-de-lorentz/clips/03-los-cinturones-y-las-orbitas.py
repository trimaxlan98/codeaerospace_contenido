class Clip3(Scene):
    """1.3.3 - Los cinturones de Van Allen y las orbitas de trabajo:
    LEO pasa por debajo, los GPS viven dentro del exterior (electronica
    endurecida) y GEO se asoma justo al borde. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Los cinturones y las órbitas")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la Tierra y sus botellas llenas ---------------------
        mor = mapa_orbitas()
        mor.move_to(LEFT * 1.6 + DOWN * 0.35)
        rot.mostrar(pie_curso("Las botellas llenas alrededor de la "
                              "Tierra tienen nombre: Van Allen."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mor.tierra, scale=1.3), run_time=0.6)
        self.wait(4.4)

        rot.mostrar(pie_curso("Dos cinturones de partículas atrapadas: "
                              "protones dentro, electrones fuera."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mor.cinturon(0)), run_time=0.7)
        self.play(FadeIn(mor.cinturon(1)), run_time=0.7)
        self.wait(4.4)

        # --- momento: las tres orbitas, una a una -------------------------
        leyenda = VGroup(
            tag_hud(f"LEO  {H_LEO / 1e3:.0f} km"),
            tag_hud(f"GPS  {H_GPS / 1e3:.0f} km"),
            tag_hud(f"GEO  {H_GEO / 1e3:.0f} km"),
            tag_hud(f"1 vuelta = {mor.periodo_horas('GEO'):.1f} h"))
        leyenda.arrange(DOWN, aligned_edge=LEFT, buff=0.34)
        leyenda.move_to(RIGHT * 4.35 + UP * 0.3)

        rot.mostrar(pie_curso("La estación y los enjambres LEO vuelan "
                              "POR DEBAJO de todo eso."),
                    zona="abajo", run_time=0.5)
        self.play(Create(mor.orbita("LEO")),
                  FadeIn(leyenda[0], shift=0.15 * RIGHT), run_time=0.9)
        self.wait(4.4)

        rot.mostrar(pie_curso("Los GPS viven DENTRO del cinturón "
                              "exterior: electrónica endurecida."),
                    zona="abajo", run_time=0.5)
        self.play(Create(mor.orbita("GPS")),
                  FadeIn(leyenda[1], shift=0.15 * RIGHT), run_time=0.9)
        self.wait(4.6)

        rot.mostrar(pie_curso("Los geoestacionarios se asoman justo al "
                              "borde de fuera."),
                    zona="abajo", run_time=0.5)
        self.play(Create(mor.orbita("GEO")),
                  FadeIn(leyenda[2], shift=0.15 * RIGHT), run_time=0.9)
        self.wait(4.4)

        # --- momento: la cifra de GEO -------------------------------------
        rot.mostrar(pie_curso("A esa altura la vuelta dura lo que el "
                              "día: el satélite no se mueve de tu cielo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(leyenda[3], shift=0.15 * RIGHT), run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("Órbitas elegidas esquivando cinturones. "
                              "Falta ver la carga que llevan a bordo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
