class Clip8(Scene):
    """8 - El horizonte. El caos pone fecha de caducidad a la prediccion:
    segundos, dos semanas, cinco millones de años. Recapitulacion y
    cierre de la tesis. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El horizonte")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: fecha de caducidad ----------------------------------
        rot.mostrar(pie_curso("El caos no prohíbe predecir: pone fecha de "
                              "caducidad."), zona="abajo", run_time=0.5)
        barra = Line(LEFT * 5.4, RIGHT * 5.4, stroke_width=2.4,
                     color=C_EJE)
        barra.move_to(UP * 0.75)
        etiqueta_barra = tag_hud("horizonte de predicción (escala log)",
                                 font_size=14, color=C_TENUE)
        etiqueta_barra.next_to(barra, UP, buff=0.65)
        self.play(Create(barra), FadeIn(etiqueta_barra), run_time=0.9)
        self.wait(2.8)

        # --- momento: tres horizontes -------------------------------------
        rot.mostrar(pie_curso("Segundos para un péndulo; dos semanas para "
                              "el clima; cinco millones de años para las "
                              "órbitas."), zona="abajo", run_time=0.5)
        logs = [math.log10(s) for _, s in HORIZONTES]
        lo, hi = min(logs) - 1.2, max(logs) + 1.2
        marcas = VGroup()
        rotulos_t = ("~10 s", "~2 semanas", "~5 M años")
        for (nombre, seg), rot_t in zip(HORIZONTES, rotulos_t):
            fx = (math.log10(seg) - lo) / (hi - lo) - 0.5
            x = barra.get_center() + RIGHT * fx * barra.get_length()
            punto = Dot(x, radius=0.07, color=C_GEMELO)
            palo = Line(x, x + DOWN * 0.28, stroke_width=1.8, color=C_EJE)
            nom = Text(nombre, font_size=18, color=C_TENUE)
            nom.next_to(palo, DOWN, buff=0.10)
            cifra = tag_hud(rot_t, font_size=15)
            cifra.next_to(nom, DOWN, buff=0.12)
            grupo = VGroup(punto, palo, nom, cifra)
            marcas.add(grupo)
            self.play(FadeIn(grupo, shift=0.15 * DOWN), run_time=0.8)
            self.wait(0.7)
        self.wait(2.2)

        # --- momento: la recapitulacion -----------------------------------
        rot.mostrar(pie_curso("Determinista no significa predecible."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(barra), FadeOut(etiqueta_barra),
                  FadeOut(marcas), run_time=0.7)
        minis = Group(
            cobweb(R_CAOS, pasos=10, lado=1.35),
            imagen_bifurcacion(res=(360, 240), alto_escena=1.5),
            curva_lorenz(trayectoria_lorenz(n=4000), alto=1.5,
                         grosor=1.2),
            mapa_retorno(orbita_logistica(4.0, 0.2, 90), lado=1.35,
                         radio=0.02),
        )
        minis.arrange(RIGHT, buff=0.85).move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(m, shift=0.18 * UP) for m in minis],
                              lag_ratio=0.22), run_time=2.0)
        self.wait(3.6)

        # --- momento: cierre del curso ------------------------------------
        rot.limpiar("arriba", run_time=0.4)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(minis), run_time=0.7)
        cierre = VGroup(
            titulo_marca("Determinista no significa predecible.",
                         font_size=38),
            Text("El caos es orden que no se deja predecir.",
                 font_size=26, color=C_GEMELO),
        ).arrange(DOWN, buff=0.4)
        cierre.move_to(UP * 0.2)
        self.play(Write(cierre[0]), run_time=1.4)
        self.play(FadeIn(cierre[1], shift=0.18 * UP), run_time=0.8)
        self.wait(5.8)
