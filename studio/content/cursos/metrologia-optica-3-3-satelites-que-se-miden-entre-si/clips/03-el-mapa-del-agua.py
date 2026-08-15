class Clip3(Scene):
    """3 - El mapa del agua. De las distancias entre los dos satelites, mes
    a mes, sale un mapa de anomalias de gravedad: cian donde falta masa
    (acuiferos que se vacian, hielo que adelgaza) y ambar donde sobra. El
    mapa es sintetico; lo real es el mecanismo. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El mapa del agua"),
                    zona="arriba", run_time=0.6)

        # Mapa grande (6.80 x 3.85) centrado en y = -0.10: ocupa la banda
        # central entera y deja la fila de -2.36 para leyenda y honestidad.
        # `rotular=False`: las tres regiones se rotulan una a una.
        mapa = mapa_gravedad(ancho=6.80, alto=3.85, rotular=False)
        mapa.move_to(DOWN * 0.10)

        def marca(nombre, texto, color, direccion, largo=1.05):
            """Anillo sobre la region + flecha corta + rotulo por fuera."""
            p = mapa.region(nombre)
            anillo = Circle(radius=0.26, stroke_width=2.2, color=color)
            anillo.set_stroke(opacity=0.9)
            anillo.move_to(p)
            flecha = Arrow(p + direccion * (0.30 + largo),
                           p + direccion * 0.32, buff=0.0, stroke_width=2.6,
                           color=color, max_tip_length_to_length_ratio=0.22)
            rotulo = tag_hud(texto, font_size=16, color=color)
            rotulo.next_to(flecha.get_start(), direccion, buff=0.14)
            return VGroup(anillo, flecha, rotulo)

        # --- momento: de las distancias sale un mapa -------------------
        rot.mostrar(pie_curso("De esas distancias, mes a mes, sale un mapa "
                              "de la gravedad de la Tierra."), zona="abajo")
        self.play(FadeIn(mapa), run_time=1.1)
        barrido = Line(mapa.get_corner(UL), mapa.get_corner(DL),
                       stroke_width=3.0, color=C_MEDIDA)
        barrido.set_stroke(opacity=0.55)
        self.play(FadeIn(barrido), run_time=0.3)
        self.play(barrido.animate.shift(RIGHT * mapa.width), run_time=2.1,
                  rate_func=linear)
        self.play(FadeOut(barrido), run_time=0.3)

        def muestra(color, texto):
            s = Square(side_length=0.20, stroke_width=0.0)
            s.set_fill(color, opacity=0.85)
            t = tag_hud(texto, font_size=14, color=C_TENUE)
            return VGroup(s, t).arrange(RIGHT, buff=0.12)

        leyenda = VGroup(muestra(C_MEDIDA, "falta masa"),
                         muestra(C_ONDA, "sobra masa"))
        leyenda.arrange(RIGHT, buff=0.60)
        leyenda.move_to(np.array([-1.65, -2.36, 0.0]))
        sintetico = tag_hud("mapa sintetico", font_size=13, color=C_TENUE)
        sintetico.move_to(np.array([2.35, -2.36, 0.0]))
        self.play(FadeIn(leyenda), FadeIn(sintetico), run_time=0.6)
        self.wait(3.6)

        # --- momento: donde sobra agua y donde falta hielo -------------
        rot.mostrar(pie_curso("Donde hay agua de más, la gravedad sube; "
                              "donde el hielo se derrite, baja."),
                    zona="abajo")
        m_acu = marca("acuifero", "acuifero", C_MEDIDA, LEFT)
        m_hie = marca("hielo", "hielo", C_MEDIDA, RIGHT)
        self.play(Create(m_acu[0]), GrowArrow(m_acu[1]), FadeIn(m_acu[2]),
                  run_time=0.8)
        self.play(Create(m_hie[0]), GrowArrow(m_hie[1]), FadeIn(m_hie[2]),
                  run_time=0.8)
        self.wait(4.6)

        # --- momento: se pesan desde la orbita -------------------------
        rot.mostrar(pie_curso("Acuíferos que se vacían, glaciares que "
                              "adelgazan: se pesan desde la órbita."),
                    zona="abajo")
        m_cue = marca("cuenca", "cuenca", C_ONDA, UP, largo=0.90)
        self.play(Create(m_cue[0]), GrowArrow(m_cue[1]), FadeIn(m_cue[2]),
                  run_time=0.8)
        self.play(Flash(m_acu[0], color=C_MEDIDA, line_length=0.16,
                        num_lines=14, flash_radius=0.48),
                  Flash(m_hie[0], color=C_MEDIDA, line_length=0.16,
                        num_lines=14, flash_radius=0.48), run_time=1.0)
        self.wait(4.4)

        # --- cierre ----------------------------------------------------
        rot.mostrar(pie_curso("Un mapa del agua hecho con luz entre dos "
                              "satélites."), zona="abajo")
        self.wait(6.2)
