class Clip1(Scene):
    """1 - Un tanque con alas de nada. La silueta a proporciones REALES:
    la altura de cada franja es su fraccion de masa, asi que el propelente
    (93.2 %) se come el cohete entero y la carga util queda en una raya
    cian de 3.9 %. No es mala ingenieria: es un logaritmo. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Un tanque con alas de nada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Geometria del clip: la silueta a la izquierda (base en y = -1.42,
        # punta en 2.08) y una columna fija de cifras a la derecha, unida a
        # cada zona por una guia. Las dos franjas de arriba son delgadisimas
        # y estan pegadas: sus cifras NO se colocan con next_to sobre ellas,
        # van en la columna con separacion propia. Todo en la banda central.
        sil = silueta_cohete(FRAC_PROP, FRAC_ESTRUCTURA_SIL, FRAC_CARGA_SIL,
                             alto=3.5)
        sil.shift(LEFT * 2.2 + UP * 0.33)
        col_x = 0.30

        def cifra(texto, y, font_size, color):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(np.array([0.0, y, 0.0]))
            t.align_to(np.array([col_x, 0.0, 0.0]), LEFT)
            return t

        def guia(nombre, tag):
            z = sil.zona(nombre)
            ini = np.array([z.get_right()[0] + 0.07, z.get_center()[1], 0.0])
            fin = np.array([tag.get_left()[0] - 0.14, tag.get_center()[1],
                            0.0])
            return Line(ini, fin, stroke_width=1.6, color=C_EJE)

        t_prop = cifra(f"propelente  {FRAC_PROP * 100:.1f} %",
                       0.21, 22, C_PROPELENTE)
        t_estr = cifra(f"estructura  {FRAC_ESTRUCTURA_SIL * 100:.1f} %",
                       1.15, 22, C_ESTRUCTURA)
        t_carga = cifra(f"carga útil  {FRAC_CARGA_SIL * 100:.1f} %",
                        2.05, 26, C_CARGA)
        g_prop, g_estr, g_carga = (guia("propelente", t_prop),
                                   guia("estructura", t_estr),
                                   guia("carga", t_carga))

        # --- momento: la pregunta ------------------------------------------
        rot.mostrar(pie_curso("¿Por qué un cohete es casi todo tanque?"),
                    zona="abajo", run_time=0.5)

        self.play(Create(sil.contorno), run_time=1.4)
        llama = llama_escape(n=16, ancho=0.5, largo=0.7)
        llama.shift(sil.zona("propelente").get_bottom())
        self.play(FadeIn(llama, shift=0.12 * DOWN), run_time=0.5)
        self.wait(1.5)
        self.play(FadeOut(llama, shift=0.18 * DOWN), run_time=0.6)
        self.wait(1.4)

        # --- momento: la masa, apilada a escala ----------------------------
        rot.mostrar(pie_curso("La altura de cada franja es su fracción de "
                              "masa."), zona="abajo", run_time=0.5)
        self.play(FadeIn(sil.zona("propelente"), shift=0.14 * UP),
                  Create(g_prop), FadeIn(t_prop, shift=0.14 * RIGHT),
                  run_time=0.9)
        self.wait(4.45)

        # --- momento: lo que queda arriba ----------------------------------
        rot.mostrar(pie_curso("Arriba, dos rayas: los tanques… y lo que "
                              "viaja."), zona="abajo", run_time=0.5)
        self.play(FadeIn(sil.zona("estructura")), Create(g_estr),
                  FadeIn(t_estr, shift=0.14 * RIGHT), run_time=0.75)
        self.wait(1.3)
        self.play(FadeIn(sil.zona("carga")), Create(g_carga),
                  FadeIn(t_carga, shift=0.14 * RIGHT), run_time=0.8)
        self.wait(2.5)

        # --- momento: el remate --------------------------------------------
        rot.mostrar(pie_curso("Todo esto… para esto."), zona="abajo",
                    run_time=0.5)
        self.play(Circumscribe(sil.zona("carga"), color=C_CARGA, buff=0.07),
                  run_time=1.0)
        self.play(Flash(sil.zona("carga"), color=C_CARGA, line_length=0.20,
                        num_lines=12, flash_radius=0.55), run_time=0.6)
        self.wait(3.45)

        # --- cierre: no es mala ingenieria ---------------------------------
        rot.mostrar(pie_curso("¿Mala ingeniería? No: es un logaritmo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
