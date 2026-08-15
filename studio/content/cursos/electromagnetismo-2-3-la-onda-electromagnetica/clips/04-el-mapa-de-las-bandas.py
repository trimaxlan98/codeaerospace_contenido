class Clip4(Scene):
    """2.3.4 - El mapa de las bandas: la regla logaritmica de HF a Ka, con
    cuatro usos colgados de su frecuencia y su longitud de onda.

    Cada uso vive donde su fisica lo deja: el tamaño de la onda decide el
    tamaño de la antena. Cierra la leccion y el modulo 2. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El mapa de las bandas")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        ban = banda_espectro_em()
        ban.move_to(UP * 0.65)

        def marcador(f, texto, altura):
            """Punto sobre la banda con su guia y su etiqueta debajo."""
            p = ban.punto_de(f)
            punto = Dot(p, radius=0.075, color=C_CALCULO)
            guia = Line(p + DOWN * 0.72, p + DOWN * altura,
                        stroke_width=1.5, color=C_EJE)
            tag = tag_hud(texto, font_size=19)
            tag.next_to(guia, DOWN, buff=0.14)
            return VGroup(punto, guia, tag)

        # --- momento: la regla entera -----------------------------------------
        rot.mostrar(pie_curso("Todo el espectro de radio en una regla "
                              "logarítmica: de la onda corta a la banda "
                              "Ka."), zona="abajo", run_time=0.5)
        self.play(Create(ban.eje), FadeIn(ban.zonas), FadeIn(ban.nombres),
                  FadeIn(ban.marcas), run_time=1.6)
        self.wait(4.6)

        # --- momento: la FM del coche ------------------------------------------
        m_fm = marcador(F_FM, f"FM  {ban.lambda_texto(F_FM)}", 1.30)
        rot.mostrar(pie_curso("La FM del coche, a cien megahercios: tres "
                              "metros de onda. Por eso su antena es un "
                              "látigo."), zona="abajo", run_time=0.5)
        self.play(FadeIn(m_fm), run_time=0.6)
        self.wait(4.4)

        # --- momento: el GPS ----------------------------------------------------
        m_gps = marcador(F_GPS, f"GPS L1  {ban.lambda_texto(F_GPS)}", 2.05)
        rot.mostrar(pie_curso("El GPS vive en banda L: diecinueve "
                              "centímetros. Ya cabe dentro de un móvil."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(m_gps), run_time=0.6)
        self.wait(4.4)

        # --- momento: el plato de balcon ----------------------------------------
        m_ku = marcador(F_KU, f"Ku  {ban.lambda_texto(F_KU)}", 1.30)
        rot.mostrar(pie_curso("Tu plato de balcón escucha en Ku: "
                              "veinticinco milímetros. El plato es enorme "
                              "comparado con eso."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(m_ku), run_time=0.6)
        self.wait(4.4)

        # --- momento: la banda ancha --------------------------------------------
        m_ka = marcador(F_KA, f"Ka  {ban.lambda_texto(F_KA)}", 2.05)
        rot.mostrar(pie_curso("Y la banda ancha satelital sube a Ka: diez "
                              "milímetros. Más capacidad, y más lluvia "
                              "encima."), zona="abajo", run_time=0.5)
        self.play(FadeIn(m_ka), run_time=0.6)
        self.wait(4.4)

        # --- cierre de la leccion y del modulo ------------------------------------
        self.play(FadeOut(ban), FadeOut(m_fm), FadeOut(m_gps),
                  FadeOut(m_ku), FadeOut(m_ka), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("Ya tienes la onda.", font_size=40, color=C_TITULO)
        linea2 = Text("Ahora hay que llevarla a su antena.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.45)
        linea2.move_to(DOWN * 0.45)
        rot.mostrar(pie_curso("Cada uso vive donde su física lo deja: el "
                              "tamaño de la onda manda."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)
