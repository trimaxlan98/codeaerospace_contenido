class Clip3(Scene):
    """2.3.3 - La polarizacion: hacia donde apunta E visto de frente.

    Vertical, horizontal y circular con la misma pieza; la lectura satelital
    es el reuso de frecuencia (dos programas en la MISMA frecuencia) y el
    GPS circular para sobrevivir a los giros de la ionosfera. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La polarización")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        pol = traza_polarizacion("v", fase=0.9)
        pol.move_to(UP * 0.15)
        etiqueta = tag_hud("polarizacion vertical", font_size=19,
                           color=C_ONDA)
        etiqueta.next_to(pol, DOWN, buff=0.30)

        # --- momento: la onda vista de frente --------------------------------
        rot.mostrar(pie_curso("Mira la onda de frente, viniendo hacia ti. "
                              "¿Hacia dónde apunta el campo eléctrico?"),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(pol), FadeIn(etiqueta), run_time=0.7)
        self.wait(4.6)

        # --- momento: el vaiven vertical --------------------------------------
        rot.mostrar(pie_curso("Vertical: el vector sube y baja siempre "
                              "sobre la misma línea."), zona="abajo",
                    run_time=0.5)
        for fase in (1.6, 2.7, 4.3):
            nueva = pol.con_fase(fase)
            self.play(ReplacementTransform(pol, nueva), run_time=0.7,
                      rate_func=linear)
            pol = nueva
        self.wait(2.0)

        # --- momento: la horizontal --------------------------------------------
        nueva = traza_polarizacion("h", fase=0.9)
        nueva.move_to(pol.get_center())
        et_h = tag_hud("polarizacion horizontal", font_size=19,
                       color=C_ONDA)
        et_h.next_to(nueva, DOWN, buff=0.30)
        rot.mostrar(pie_curso("Gírala noventa grados y tienes la "
                              "horizontal: la MISMA frecuencia, otra "
                              "orientación."), zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(pol, nueva),
                  ReplacementTransform(etiqueta, et_h), run_time=0.9)
        pol, etiqueta = nueva, et_h
        for fase in (1.6, 4.3):
            nueva = pol.con_fase(fase)
            self.play(ReplacementTransform(pol, nueva), run_time=0.7,
                      rate_func=linear)
            pol = nueva
        self.wait(2.0)

        # --- momento: la circular ----------------------------------------------
        nueva = traza_polarizacion("circular", fase=0.9)
        nueva.move_to(pol.get_center())
        et_c = tag_hud("polarizacion circular", font_size=19, color=C_ONDA)
        et_c.next_to(nueva, DOWN, buff=0.30)
        rot.mostrar(pie_curso("Y si las dos van a la vez, desfasadas un "
                              "cuarto de vuelta, el vector gira."),
                    zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(pol, nueva),
                  ReplacementTransform(etiqueta, et_c), run_time=0.9)
        pol, etiqueta = nueva, et_c
        for fase in (2.5, 4.1, 5.7):
            nueva = pol.con_fase(fase)
            self.play(ReplacementTransform(pol, nueva), run_time=0.7,
                      rate_func=linear)
            pol = nueva
        self.wait(2.0)

        # --- momento: dos programas en la misma frecuencia ---------------------
        filas = VGroup(
            tag_hud(f"{F_KU / 1e9:.0f} GHz   V   ->  programa A",
                    font_size=18, color=C_ONDA),
            tag_hud(f"{F_KU / 1e9:.0f} GHz   H   ->  programa B",
                    font_size=18, color=C_ONDA),
            tag_hud("misma frecuencia, doble capacidad", font_size=18))
        filas.arrange(DOWN, buff=0.36, aligned_edge=LEFT)
        filas.move_to(RIGHT * 2.6 + UP * 0.15)
        rot.mostrar(pie_curso("Un satélite emite dos señales en la misma "
                              "frecuencia: una V y otra H. El plato separa "
                              "cada una."), zona="abajo", run_time=0.5)
        self.play(VGroup(pol, etiqueta).animate.move_to(LEFT * 3.5
                                                        + UP * 0.15),
                  run_time=0.8)
        self.play(FadeIn(filas[0]), FadeIn(filas[1]), run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("Eso es reúso de frecuencia: el mismo trozo "
                              "de espectro, el doble de capacidad."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(filas[2], shift=0.12 * UP), run_time=0.6)
        self.wait(4.6)

        rot.mostrar(pie_curso("Y el GPS emite circular a propósito: así "
                              "sobrevive a los giros que le impone la "
                              "ionosfera."), zona="abajo", run_time=0.5)
        self.wait(4.8)
