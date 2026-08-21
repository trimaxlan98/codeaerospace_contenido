def _firmado(x, dec=2):
    """La misma cifra de `fmt`, con el signo siempre escrito."""
    s = fmt(x, dec)
    return s if s.startswith("-") else "+" + s


class Clip3(Scene):
    """1.2.3 - El coseno alzado (beta = 0.35): sus colas valen CERO
    MEDIDO en el instante de los demas simbolos. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El pulso de Nyquist")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: del pulso torpe al pulso que se calla ---------------
        rot.mostrar(pie_curso("El problema no era el canal: era la forma "
                              "del pulso. Y la forma se elige."),
                    zona="abajo", run_time=0.5)
        on = onda(T_PULSO, H_LENTO, rango_y=RANGO_PULSO, ancho=8.4,
                  alto=2.9, color=C_SENAL)
        on.move_to(DOWN * 0.35)
        ticks = VGroup(*[tag_hud(f"t = {k}", font_size=16, color=C_TENUE)
                         .move_to(on.en(k, RANGO_PULSO[0]) + DOWN * 0.24)
                         for k in (-3, -2, -1, 0, 1, 2, 3)])
        self.play(FadeIn(on.ejes), FadeIn(ticks), run_time=0.7)
        self.play(Create(on.curva), run_time=1.4)
        et_torpe = tag_hud("el pulso torpe", font_size=18, color=C_TENUE)
        et_torpe.next_to(on.en(0.5, 1.30), UP, buff=0.18)
        self.play(FadeIn(et_torpe), run_time=0.5)
        self.wait(2.9)

        # --- momento: el coseno alzado ------------------------------------
        rot.mostrar(pie_curso("Este es el coseno alzado: sube, baja… y "
                              "sigue ondulando a los dos lados."),
                    zona="abajo", run_time=0.5)
        gemela = on.con_serie(H_RC, color=C_SENAL)
        et_rc = tag_hud("el coseno alzado", font_size=18, color=C_SENAL)
        et_rc.next_to(on.en(0.0, 1.30), UP, buff=0.18)
        self.play(FadeOut(et_torpe), Transform(on.curva, gemela.curva),
                  run_time=1.6)
        self.play(FadeIn(et_rc), run_time=0.5)
        self.wait(3.6)

        # --- momento: las colas valen CERO en los vecinos -----------------
        rot.mostrar(pie_curso("Y sus colas valen cero EXACTAMENTE donde "
                              "deciden los demás símbolos."),
                    zona="abajo", run_time=0.5)
        guias = VGroup(*[on.vertical_en(k, color=C_CIFRA) for k in K_CEROS])
        ceros = VGroup(*[Dot(on.en(k, v), radius=0.07, color=C_CIFRA)
                         for k, v in zip(K_CEROS, RC_CEROS)])
        self.play(LaggedStart(*[Create(g) for g in guias], lag_ratio=0.18),
                  run_time=1.4)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in ceros],
                              lag_ratio=0.18), run_time=1.2)
        filas = VGroup(
            tag_hud("la cola en", font_size=17, color=C_TENUE),
            *[tag_hud(f"t = {k}  {fmt(v, 2)}", font_size=20)
              for k, v in zip((1, 2, 3), RC_K[1:])]
        ).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        panel = panel_derecha(filas, buff=0.3)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(3.4)

        # --- momento: los mismos tres simbolos, ahora limpios -------------
        rot.mostrar(pie_curso("Los mismos tres símbolos de antes, ahora con "
                              "este pulso."),
                    zona="abajo", run_time=0.5)
        tren = onda(T_TREN, Y_RC, rango_y=RANGO_TREN, ancho=8.6, alto=2.9,
                    color=C_SENAL)
        tren.move_to(DOWN * 0.35)
        ticks2 = VGroup(*[tag_hud(f"t = {k}", font_size=16, color=C_TENUE)
                          .move_to(tren.en(k, RANGO_TREN[0]) + DOWN * 0.24)
                          for k in K_DECISION])
        guias2 = VGroup(*[tren.vertical_en(k, color=C_CIFRA)
                          for k in K_DECISION])
        lecturas = VGroup(*[Dot(tren.en(k, v), radius=0.075, color=C_CIFRA)
                            for k, v in zip(K_DECISION, DEC_RC)])
        filas2 = VGroup(
            tag_hud("el receptor lee", font_size=17, color=C_TENUE),
            *[tag_hud(f"t = {k}  {_firmado(v)}", font_size=20)
              for k, v in zip(K_DECISION, DEC_RC)]
        ).arrange(DOWN, buff=0.13, aligned_edge=LEFT)
        panel2 = panel_derecha(filas2, buff=0.3)
        self.play(FadeOut(on), FadeOut(ticks), FadeOut(et_rc),
                  FadeOut(guias), FadeOut(ceros), FadeOut(panel),
                  run_time=0.8)
        self.play(FadeIn(tren.ejes), FadeIn(ticks2), run_time=0.5)
        self.play(Create(tren.curva), run_time=1.6)
        self.play(Create(guias2), FadeIn(lecturas), FadeIn(panel2),
                  run_time=1.0)
        self.wait(3.2)

        # --- momento: interferir sin estorbar -----------------------------
        rot.mostrar(pie_curso("Cada pulso sigue invadiendo a los vecinos: "
                              "lo que ya no hace es estorbarlos."),
                    zona="abajo", run_time=0.5)
        self.play(LaggedStart(*[Indicate(d, color=C_CIFRA,
                                         scale_factor=1.6)
                                for d in lecturas], lag_ratio=0.3),
                  run_time=1.4)
        self.wait(3.6)

        # --- momento: beta = 0.35, el pulso de la TV por satelite ---------
        rot.mostrar(formula_pie(r"\beta = 0.35"), zona="abajo",
                    run_time=0.5)
        et_dvb = _con_fondo(
            tag_hud("el pulso de DVB-S2", font_size=20, color=C_TENUE),
            buff=0.14, opacidad=0.9)
        et_dvb.move_to(LEFT * 3.6 + UP * 2.0)
        self.play(FadeIn(et_dvb), run_time=0.6)
        self.wait(4.5)
