class Clip2(Scene):
    """7.3.2 - El jitter medido (RFC 3550) y el bufer de reproduccion: un
    bufer chico corta, uno grande retrasa. El compromiso completo, con
    las dos cifras a la vista. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Jitter y el bufer")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las llegadas no son regulares -------------------------
        rot.mostrar(pie_curso("Los paquetes deberian llegar cada 20 ms. "
                              "En la practica, el hueco entre uno y otro "
                              "baila."),
                    zona="abajo", run_time=0.5)
        g = grafica(HUECOS, (0, JITTER["n"] - 1), (0, 46.0), ancho=7.4,
                    alto=2.6, color=C_PAQUETE, muestras=JITTER["n"],
                    etiqueta_y="ms entre llegadas")
        g.move_to(UP * 0.75)
        ref = g.horizontal_en(RTP_PASO_MS, color=C_EJE)
        et_ref = tag_hud("20 ms esperados", font_size=15, color=C_EJE)
        et_ref.next_to(ref, LEFT, buff=0.14)
        self.play(FadeIn(g.ejes), run_time=0.4)
        self.play(Create(ref), FadeIn(et_ref), run_time=0.5)
        self.play(Create(g.curva), run_time=2.0)
        self.wait(1.0)

        # --- momento: el jitter medido ---------------------------------------
        rot.mostrar(pie_curso("Esa irregularidad se mide con la formula "
                              "de RFC 3550: el jitter."),
                    zona="abajo", run_time=0.5)
        et_jitter = tag_hud("jitter medido: %s ms" % fmt(
            JITTER["jitter_ms"], 2), font_size=23, color=C_CIFRA)
        et_jitter.next_to(g, DOWN, buff=0.35)
        self.play(FadeIn(et_jitter, shift=0.12 * UP), run_time=0.5)
        self.wait(3.0)

        # --- momento: el bufer, chico o grande ---------------------------------
        rot.mostrar(pie_curso("Un bufer de reproduccion absorbe ese "
                              "baile, guardando un poco antes de sonar."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(g), FadeOut(ref), FadeOut(et_ref),
                  FadeOut(et_jitter), run_time=0.5)
        chico = cola(capacidad=CAP_10, ocupacion=CAP_10, lado=0.42,
                     etiqueta="bufer de 10 ms")
        chico.move_to(LEFT * 3.0 + UP * 0.9)
        grande = cola(capacidad=CAP_120, ocupacion=CAP_120, lado=0.42,
                      etiqueta="bufer de 120 ms")
        grande.move_to(RIGHT * 2.0 + UP * 0.9)
        self.play(FadeIn(chico), run_time=0.6)
        self.play(FadeIn(grande), run_time=0.6)
        self.wait(2.6)

        # --- momento: bufer chico -> se corta -----------------------------
        rot.mostrar(pie_curso("Con el bufer chico casi no hay margen: la "
                              "voz se corta."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(grande), run_time=0.4)
        self.play(chico.animate.move_to(UP * 1.35), run_time=0.5)
        s10 = sierra(list(BUFER_10["ocupacion"]), perdidas=CORTES_10,
                     ancho=6.6, alto=2.1, color=C_COLA, media=False,
                     etiqueta="ocupacion del bufer (10 ms)")
        s10.move_to(DOWN * 0.65)
        self.play(FadeIn(s10.ejes), Create(s10.curva), run_time=1.4)
        self.play(LaggedStart(*[FadeIn(m, scale=1.8) for m in s10.marcas],
                              lag_ratio=0.4), run_time=0.8)
        et10 = VGroup(
            tag_hud("%d cortes" % BUFER_10["cortes"], font_size=20,
                    color=C_PERDIDA),
            tag_hud("  ->  retardo medio", font_size=20, color=C_EJE),
            tag_hud("%s ms" % fmt(BUFER_10["retardo_medio_ms"], 1),
                    font_size=20, color=C_COLA),
        ).arrange(RIGHT, buff=0.10)
        et10.next_to(s10, DOWN, buff=0.28)
        self.play(FadeIn(et10), run_time=0.5)
        self.wait(3.0)

        # --- momento: bufer grande -> se retrasa / el compromiso -----------
        rot.mostrar(pie_curso("Con 120 ms casi no hay cortes... pero se "
                              "paga en retardo. Ese es el compromiso "
                              "completo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(chico), FadeOut(s10), FadeOut(et10), run_time=0.5)
        s120 = sierra(list(BUFER_120["ocupacion"]), perdidas=(),
                      ancho=6.6, alto=2.1, color=C_COLA, media=False,
                      etiqueta="ocupacion del bufer (120 ms)")
        s120.move_to(UP * 0.55)
        self.play(FadeIn(s120.ejes), Create(s120.curva), run_time=1.4)
        filas = [
            ["10 ms", str(BUFER_10["cortes"]),
             "%s ms" % fmt(BUFER_10["retardo_medio_ms"], 1)],
            ["40 ms", str(BUFER_40["cortes"]),
             "%s ms" % fmt(BUFER_40["retardo_medio_ms"], 1)],
            ["120 ms", str(BUFER_120["cortes"]),
             "%s ms" % fmt(BUFER_120["retardo_medio_ms"], 1)],
        ]
        t = tabla(["bufer", "cortes", "retardo medio"], filas,
                 anchos=[1.7, 1.5, 2.3], alto=0.42, fs=16)
        # `Tabla` pinta la fila entera de un color: repintar por celda para
        # que cortes vaya en rojo y retardo en naranja (el color dice el
        # papel), sin tocar la estructura (repintar no rompe gemelas).
        for i in range(3):
            t.celda(i, 1).set_color(C_PERDIDA)
            t.celda(i, 2).set_color(C_COLA)
        t.next_to(s120, DOWN, buff=0.32)
        self.play(FadeIn(t), run_time=0.6)
        self.wait(4.6)
