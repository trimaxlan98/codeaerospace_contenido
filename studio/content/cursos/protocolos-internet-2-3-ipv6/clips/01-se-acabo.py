class Clip1(Scene):
    """2.3.1 - 32 bits parecian un oceano en 1981. Se acabaron: el pool
    libre de cada registro regional se agoto, uno por uno, entre 2011 y
    2020. 4294 millones de direcciones para 8100 millones de personas.
    (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("2^32 se acabo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la formula ------------------------------------------
        rot.mostrar(pie_curso("La direccion IPv4 tiene 32 bits. En 1981 "
                              "parecian un oceano."),
                    zona="abajo", run_time=0.5)
        formula = MathTex(r"2^{32} = " + TOTAL_32_TXT.replace(" ", r"\,"),
                          font_size=42, color=C_CIFRA)
        formula.move_to(UP * 1.6)
        self.play(FadeIn(formula, shift=0.2 * UP), run_time=0.9)
        self.wait(6.2)

        # --- momento: la cronologia real del agotamiento -------------------
        rot.mostrar(pie_curso("El pool libre no se acabo de golpe: se "
                              "agoto registro por registro."),
                    zona="abajo", run_time=0.5)
        barra = Rectangle(width=9.6, height=0.62, stroke_color=C_RED,
                          stroke_width=2.2, fill_color=C_RED,
                          fill_opacity=0.05)
        barra.move_to(DOWN * 0.55)
        self.play(FadeIn(barra), run_time=0.5)

        n = len(AGOTAMIENTO_IPV4)
        w = barra.width / n
        fills, marcas = VGroup(), VGroup()
        for i, (rir, anio) in enumerate(AGOTAMIENTO_IPV4):
            x0 = barra.get_left()[0] + w * i
            relleno = Rectangle(width=w, height=barra.height,
                                stroke_width=0.0, fill_color=C_PERDIDA,
                                fill_opacity=0.55)
            relleno.move_to(np.array([x0 + w / 2.0, barra.get_center()[1],
                                      0.0]))
            etq = VGroup(tag_hud(rir, font_size=12, color=C_PERDIDA),
                        tag_hud(str(anio), font_size=12,
                               color=C_PERDIDA)).arrange(DOWN, buff=0.04)
            if etq.width > w * 0.92:
                etq.scale(w * 0.92 / etq.width)
            etq.next_to(relleno, UP, buff=0.14)
            fills.add(relleno)
            marcas.add(etq)
        self.play(LaggedStart(*[
            AnimationGroup(FadeIn(f), FadeIn(e))
            for f, e in zip(fills, marcas)], lag_ratio=0.55), run_time=3.4)
        self.wait(2.2)

        # --- momento: 8100 millones de personas -----------------------------
        rot.mostrar(pie_curso("8100 millones de personas. Menos de una "
                              "direccion por cabeza."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(formula), FadeOut(barra), FadeOut(fills),
                  FadeOut(marcas), run_time=0.6)
        cifras = VGroup(
            tag_hud("%s direcciones" % TOTAL_32_TXT, font_size=24,
                   color=C_EJE),
            tag_hud("%s personas" % POBLACION_TXT, font_size=24,
                   color=C_EJE),
            tag_hud("%s direcciones por persona" % POR_PERSONA_32,
                   font_size=30, color=C_CIFRA),
        ).arrange(DOWN, buff=0.34)
        cifras.move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(c, shift=0.14 * UP) for c in cifras],
                              lag_ratio=0.4), run_time=1.8)
        self.wait(3.2)

        # --- cierre del clip: la razon --------------------------------------
        rot.mostrar(pie_curso("La direccion era de 32 bits porque nadie "
                              "imagino esto."),
                    zona="abajo", run_time=0.5)
        self.wait(7.0)
