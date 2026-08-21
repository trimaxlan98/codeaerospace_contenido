class Clip4(Scene):
    """4.3.4 - E y B perpendiculares, sosteniéndose el uno al otro y
    avanzando; c sale de mu0 y eps0 (299 792 458 m/s). Cierre de la
    leccion y de la familia. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La onda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el vacio, sin cargas ni corrientes -----------------
        esp = espacio_leccion(unidad=0.9, alcance=3, centro=DOWN * 0.2)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("Vacío: ni cargas ni cables. Solo las dos "
                              "leyes del rotacional."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        # --- momento: la onda, E contra B --------------------------------
        rot.mostrar(pie_curso("E y B, perpendiculares entre sí y "
                              "perpendiculares al avance."), zona="abajo",
                    run_time=0.5)
        onda = onda_em(esp, fase=FASES[0], **ONDA)
        fila_e = VGroup(Line(ORIGIN, RIGHT * 0.36, color=C_GRAD,
                             stroke_width=4.0),
                        tag_hud("E", font_size=21, color=C_GRAD))
        fila_e.arrange(RIGHT, buff=0.14)
        fila_b = VGroup(Line(ORIGIN, RIGHT * 0.36, color=C_CIFRA,
                             stroke_width=4.0),
                        tag_hud("B", font_size=21, color=C_CIFRA))
        fila_b.arrange(RIGHT, buff=0.14)
        leyenda = VGroup(fila_e, fila_b).arrange(DOWN, buff=0.14,
                                                 aligned_edge=LEFT)
        leyenda = _con_fondo(leyenda, buff=0.14, opacidad=0.92)
        leyenda.to_corner(UL, buff=0.5).shift(DOWN * 0.98)
        self.play(FadeIn(onda), run_time=1.3)
        self.play(FadeIn(leyenda, shift=0.15 * RIGHT), run_time=0.5)
        self.play(Indicate(onda.E, color=C_GRAD, scale_factor=1.05),
                  run_time=0.8)
        self.play(Indicate(onda.B, color=C_CIFRA, scale_factor=1.05),
                  run_time=0.8)
        self.wait(1.8)

        # --- momento: el paquete avanza ----------------------------------
        rot.mostrar(pie_curso("Cada uno alimenta al otro, y el paquete "
                              "entero avanza."), zona="abajo", run_time=0.5)
        for f in FASES[1:]:
            self.play(Transform(onda, onda.con_fase(f)), run_time=1.5,
                      rate_func=linear)
        self.wait(0.8)

        # --- momento: la velocidad no se elige ---------------------------
        rot.mostrar(pie_curso("Su velocidad no se elige: sale de dos "
                              "constantes del laboratorio."), zona="abajo",
                    run_time=0.5)
        cifra_c = tag_hud(f"{C_LUZ_TXT} m/s", font_size=20, color=C_RES)
        dato_c = VGroup(
            MathTex(r"c = \dfrac{1}{\sqrt{\mu_0\,\varepsilon_0}}",
                    font_size=34, color=C_CALCULO), cifra_c)
        dato_c.arrange(DOWN, buff=0.18)
        panel_c = _con_fondo(dato_c, buff=0.16, opacidad=0.92)
        panel_c.to_corner(UR, buff=0.5).shift(DOWN * 0.9)
        self.play(FadeIn(panel_c, shift=0.15 * LEFT), run_time=0.7)
        # Indicate SOLO sobre la cifra (si toca el _con_fondo, el fondo se
        # tine de verde y el rotulo deja de leerse).
        self.play(Indicate(cifra_c, color=C_RES, scale_factor=1.08),
                  run_time=0.9)
        self.wait(2.8)

        rot.mostrar(pie_curso("La señal que baja del satélite es "
                              "exactamente esto."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion y de la familia ------------------------
        cierre_leccion(self, rot,
                       "Cuatro renglones de nabla.",
                       "Toda la luz, toda la radio.",
                       "Fin de la familia Cálculo vectorial.",
                       esp, onda, leyenda, panel_c)
