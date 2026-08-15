class Clip3(Scene):
    """2.1.3 - El alternador: una espira que gira dentro de un campo fijo
    escribe, sola, la primera senoide. Dos vueltas completan la onda; el
    pico sale de N B A omega. Toda la red electrica nace de este giro.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El alternador: nace la senoide")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la espira quieta dentro del campo ---------------------
        alt = alternador(n=N_ALTERNADOR, b=B_ALTERNADOR,
                         area=AREA_ALTERNADOR, hz=HZ_ALTERNADOR)
        self.play(FadeIn(alt), run_time=0.7)
        rot.mostrar(pie_curso("Dentro de un campo fijo, gira una "
                              "espira. Nada más que eso."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: primera vuelta: la curva nace -------------------------
        rot.mostrar(pie_curso("Gírala una vuelta completa. Mira cómo "
                              "nace la curva, sola."), zona="abajo",
                    run_time=0.5)
        senoide = None
        for i, ang in enumerate(np.linspace(60.0, 360.0, 6)):
            nueva_espira = alt.espira_a(ang)
            nueva_senoide = alt.senoide_hasta(ang)
            if senoide is None:
                self.play(ReplacementTransform(alt.espira, nueva_espira),
                          Create(nueva_senoide), run_time=0.5)
            else:
                self.play(ReplacementTransform(alt.espira, nueva_espira),
                          ReplacementTransform(senoide, nueva_senoide),
                          run_time=0.38)
            alt.espira = nueva_espira
            senoide = nueva_senoide
        self.wait(2.2)

        # --- momento: segunda vuelta: la onda se completa --------------------
        rot.mostrar(pie_curso("Sigue girando: dos vueltas completan la "
                              "onda entera."), zona="abajo", run_time=0.5)
        for ang in np.linspace(420.0, 720.0, 6):
            nueva_espira = alt.espira_a(ang)
            nueva_senoide = alt.senoide_hasta(ang)
            self.play(ReplacementTransform(alt.espira, nueva_espira),
                      ReplacementTransform(senoide, nueva_senoide),
                      run_time=0.38)
            alt.espira = nueva_espira
            senoide = nueva_senoide
        self.wait(2.2)

        rot.mostrar(pie_curso("Sube, cruza cero, baja, cruza cero: una "
                              "senoide perfecta, sin trucos."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: el pico calculado --------------------------------------
        rot.mostrar(pie_curso("Con 100 vueltas, 0.1 T y 100 cm² a 50 "
                              "Hz, el pico se puede calcular."),
                    zona="abajo", run_time=0.5)
        tag = tag_hud(f"pico = {alt.fem_pico():.1f} V", font_size=18)
        tag.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(tag, shift=0.1 * DOWN), run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("Toda la red eléctrica de tu casa nace de "
                              "esta espira, girando."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)
