def _firmado(x, dec=2):
    """La misma cifra de `fmt`, con el signo siempre escrito."""
    s = fmt(x, dec)
    return s if s.startswith("-") else "+" + s


class Clip2(Scene):
    """1.2.2 - Tres simbolos con el pulso torpe: en el instante del
    tercero sus vecinos todavia suenan y el bit se lee al reves. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El eco sobre el vecino")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        on = onda(T_TREN, np.zeros_like(T_TREN), rango_y=RANGO_TREN,
                  ancho=8.6, alto=3.0, color=C_SENAL)
        on.move_to(DOWN * 0.45)
        on.remove(on.curva)

        # --- momento: los tres simbolos que se quieren mandar -------------
        rot.mostrar(pie_curso("Tres símbolos seguidos: más uno, más uno, "
                              "menos uno."),
                    zona="abajo", run_time=0.5)
        tks = np.array(K_DECISION, dtype=float)
        palos = on.muestras(tks, np.array(AMPLITUDES, dtype=float),
                            color=C_BIT, radio=0.07)
        etiquetas = VGroup()
        for k, a in zip(K_DECISION, AMPLITUDES):
            e = tag_hud(_firmado(a, 0), font_size=20, color=C_BIT)
            e.next_to(on.en(k, a), UP if a > 0 else DOWN, buff=0.16)
            etiquetas.add(e)
        ticks = VGroup(*[tag_hud(f"t = {k}", font_size=16, color=C_TENUE)
                         .move_to(on.en(k, RANGO_TREN[0]) + DOWN * 0.24)
                         for k in K_DECISION])
        self.play(FadeIn(on.ejes), FadeIn(ticks), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(m) for m in palos], lag_ratio=0.25),
                  run_time=1.3)
        self.play(FadeIn(etiquetas), run_time=0.5)
        self.wait(3.6)

        # --- momento: cada simbolo manda su pulso torpe -------------------
        rot.mostrar(pie_curso("Cada símbolo sale como el pulso torpe del "
                              "canal, y cada pulso arrastra su cola."),
                    zona="abajo", run_time=0.5)
        ecos = VGroup(*[on.curva_de(T_TREN, y, color=C_BIT, grosor=2.2)
                        for y in ECOS_LENTO])
        for e in ecos:
            e.set_stroke(opacity=0.75)
        self.play(LaggedStart(*[Create(e) for e in ecos], lag_ratio=0.45),
                  run_time=2.6)
        self.wait(4.0)

        # --- momento: el receptor solo ve la suma -------------------------
        rot.mostrar(pie_curso("Pero el receptor no ve tres pulsos: ve UNA "
                              "suma, y decide en un instante."),
                    zona="abajo", run_time=0.5)
        suma = on.curva_de(T_TREN, Y_LENTO, color=C_SENAL, grosor=3.0)
        self.play(ecos.animate.set_stroke(opacity=0.28),
                  FadeOut(palos), FadeOut(etiquetas), run_time=0.8)
        self.play(Create(suma), run_time=2.0)
        guia = on.vertical_en(3.0, color=C_CIFRA)
        self.play(Create(guia), run_time=0.7)
        self.wait(3.6)

        # --- momento: la cuenta en el instante del tercero ----------------
        rot.mostrar(pie_curso("En el instante del tercero, sus dos vecinos "
                              "todavía están sonando."),
                    zona="abajo", run_time=0.5)
        filas = VGroup(
            tag_hud("en t = 3:", font_size=17, color=C_TENUE),
            tag_hud(f"suyo   {_firmado(APORTES_EN_3[2])}", font_size=20,
                    color=C_BIT),
            tag_hud(f"vecino {_firmado(APORTES_EN_3[1])}", font_size=20,
                    color=C_RUIDO),
            tag_hud(f"lejano {_firmado(APORTES_EN_3[0])}", font_size=20,
                    color=C_RUIDO),
            tag_hud(f"suma   {_firmado(DEC_LENTO[2])}", font_size=20),
        ).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        panel = panel_derecha(filas, buff=0.3)
        p_solo = Dot(on.en(3.0, APORTES_EN_3[2]), radius=0.075, color=C_BIT)
        p_suma = Dot(on.en(3.0, DEC_LENTO[2]), radius=0.085, color=C_RUIDO)
        subida = Arrow(on.en(3.0, APORTES_EN_3[2]), on.en(3.0, DEC_LENTO[2]),
                       buff=0.06, color=C_RUIDO, stroke_width=4,
                       max_tip_length_to_length_ratio=0.22)
        self.play(FadeIn(p_solo, scale=0.5), FadeIn(panel), run_time=0.8)
        self.play(GrowArrow(subida), FadeIn(p_suma, scale=0.5), run_time=1.2)
        self.wait(4.4)

        # --- momento: el bit se lee al reves ------------------------------
        rot.mostrar(pie_curso("Se envió un menos uno y llega un más nueve "
                              "centésimas: el vecino ha mentido."),
                    zona="abajo", run_time=0.5)
        umbral = on.horizontal_en(0.0, color=C_RUIDO)
        # el veredicto NO puede caer sobre las curvas: va con fondo, en el
        # hueco de arriba a la derecha (la cola ya esta pegada al eje ahi).
        veredicto = _con_fondo(
            tag_hud(f"decide +1, era {_firmado(AMPLITUDES[2], 0)}",
                    font_size=21, color=C_RUIDO), buff=0.14, opacidad=0.9)
        veredicto.move_to(on.en(3.9, 1.15))
        self.play(Create(umbral), run_time=0.7)
        self.play(FadeIn(veredicto), Indicate(p_suma, color=C_RUIDO,
                                              scale_factor=1.7),
                  run_time=1.0)
        self.wait(4.6)
