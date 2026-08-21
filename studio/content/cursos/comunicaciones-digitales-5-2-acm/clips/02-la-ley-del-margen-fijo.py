class Clip2(Scene):
    """5.2.2 - La ley del margen fijo: disenar para el peor caso deja el
    enlace SIEMPRE en QPSK 1/2; la diferencia con lo que el canal de
    verdad permitiria se sombrea y se MIDE en porcentaje. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La ley del margen fijo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un solo modcod, para siempre --------------------------
        rot.mostrar(pie_curso("Disenar para el peor caso es elegir UN "
                              "modcod y no tocarlo nunca: el mas lento, "
                              "el que casi siempre cierra."),
                    zona="abajo", run_time=0.5)
        tasa = onda(T_LLUVIA, TASA_FIJA_SERIE, rango_y=(0.0, TASA_TECHO),
                   ancho=8.6, alto=3.2, color=C_BIT)
        tasa.move_to(DOWN * 0.2)
        self.play(FadeIn(tasa.ejes), run_time=0.5)
        fija = tasa.curva_de(T_LLUVIA, TASA_FIJA_SERIE, color=C_BIT,
                             grosor=3.2)
        et_fija = tag_hud(f"{MODCOD_NOMBRES[0]} = {fmt(TASA_FIJA, 2)} "
                          "bit/simb, sin cambiar de plan", font_size=16,
                          color=C_BIT)
        # Encima de TODA la caja de ejes (nunca cruzada por techo/desperdicio,
        # que ocupan toda la franja horizontal de la lluvia).
        et_fija.move_to(UP * 1.75)
        self.play(Create(fija), FadeIn(et_fija), run_time=1.6)
        self.wait(5.0)

        # --- momento: lo que el canal de verdad permitiria -------------------
        rot.mostrar(pie_curso("Pero el mismo clima, cuando ayuda, "
                              "dejaria mandar mucho mas que eso."),
                    zona="abajo", run_time=0.5)
        techo = tasa.curva_de(T_LLUVIA, TASA_ELEGIDA, color=C_TECHO,
                              grosor=2.6)
        et_techo = tag_hud("lo que el canal permite", font_size=16,
                           color=C_TECHO)
        et_techo.next_to(tasa.en(T_LLUVIA[210], TASA_ELEGIDA[210]), UP,
                         buff=0.18)
        self.play(Create(techo), run_time=1.8)
        self.play(FadeIn(et_techo), run_time=0.4)
        self.wait(4.8)

        # --- momento: la diferencia, sombreada -------------------------------
        rot.mostrar(pie_curso("La diferencia entre lo que se manda y lo "
                              "que se podria mandar es capacidad tirada "
                              "a la basura."), zona="abajo", run_time=0.5)
        borde = ([tasa.en(t, y) for t, y in zip(T_LLUVIA, TASA_ELEGIDA)]
                + [tasa.en(t, TASA_FIJA_SERIE[i])
                   for i, t in reversed(list(enumerate(T_LLUVIA)))])
        desperdicio = Polygon(*borde, stroke_width=0, fill_color=C_BANDA,
                              fill_opacity=0.22)
        self.play(FadeIn(desperdicio), FadeOut(et_techo), run_time=1.0)
        self.wait(4.6)

        # --- momento: la cuenta, medida ---------------------------------------
        rot.mostrar(pie_curso("Medido en el propio array: el diseno fijo "
                              "desperdicia mas de la mitad de lo que el "
                              "canal ofrecia."), zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"desperdicio = {fmt(DESPERDICIO_PCT, 0)} %",
                   color=C_BANDA))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(6.0)
