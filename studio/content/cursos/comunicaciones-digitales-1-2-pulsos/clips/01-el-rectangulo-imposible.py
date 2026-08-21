class Clip1(Scene):
    """1.2.1 - Un simbolo quiere ser un rectangulo; el canal de banda
    limitada lo devuelve redondeado, tarde y con cola. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El rectángulo imposible")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el pulso ideal --------------------------------------
        rot.mostrar(pie_curso("Un símbolo quiere ser un rectángulo: arriba "
                              "de golpe, abajo de golpe."),
                    zona="abajo", run_time=0.5)
        on = onda(T_PULSO, H_RECT, rango_y=RANGO_PULSO, ancho=8.4, alto=2.9,
                  color=C_BIT)
        on.move_to(DOWN * 0.35)
        ticks = VGroup(*[tag_hud(f"t = {k}", font_size=16, color=C_TENUE)
                         .move_to(on.en(k, RANGO_PULSO[0]) + DOWN * 0.24)
                         for k in (-1, 0, 1, 2)])
        self.play(FadeIn(on.ejes), FadeIn(ticks), run_time=0.7)
        self.play(Create(on.curva), run_time=1.5)
        et_ideal = tag_hud("el simbolo, tal como se pide", font_size=18,
                           color=C_BIT)
        et_ideal.next_to(on.en(0.0, 1.30), UP, buff=0.18)
        self.play(FadeIn(et_ideal), run_time=0.5)
        self.wait(3.6)

        # --- momento: el canal redondea la esquina ------------------------
        rot.mostrar(pie_curso("Pero el canal solo deja pasar un puñado de "
                              "frecuencias, y sin ellas no hay esquinas."),
                    zona="abajo", run_time=0.5)
        canal = bloque("canal de banda limitada", ancho=3.5, alto=0.72,
                       color=C_SENAL, color_texto=C_TENUE, tamano=19)
        canal.move_to(UP * 2.05 + LEFT * 4.6)
        self.play(FadeIn(canal), run_time=0.5)
        self.wait(1.6)
        gemela = on.con_serie(H_LENTO, color=C_SENAL)
        self.play(FadeOut(et_ideal),
                  Transform(on.curva, gemela.curva),
                  destello(canal[0], color=C_SENAL), run_time=1.8)
        et_real = tag_hud("el simbolo, tal como llega", font_size=18,
                          color=C_SENAL)
        et_real.next_to(on.en(0.5, 1.30), UP, buff=0.18)
        self.play(FadeIn(et_real), run_time=0.5)
        self.wait(3.4)

        # --- momento: llega tarde y no se va ------------------------------
        rot.mostrar(pie_curso("Llega redondeado, llega tarde… y todavía "
                              "está sonando un símbolo después."),
                    zona="abajo", run_time=0.5)
        g0 = on.vertical_en(0.0, color=C_CIFRA)
        g1 = on.vertical_en(1.0, color=C_CIFRA)
        p0 = Dot(on.en(0.0, LENTO_K[0]), radius=0.075, color=C_CIFRA)
        p1 = Dot(on.en(1.0, LENTO_K[1]), radius=0.075, color=C_CIFRA)
        self.play(Create(g0), Create(g1), run_time=0.8)
        self.play(FadeIn(p0, scale=0.5), FadeIn(p1, scale=0.5), run_time=0.6)
        panel = panel_derecha(
            tag_hud("en su instante", font_size=17, color=C_TENUE),
            tag_hud(f"h(0) = {fmt(LENTO_K[0], 2)}", font_size=21),
            tag_hud("un simbolo despues", font_size=17, color=C_TENUE),
            tag_hud(f"h(1) = {fmt(LENTO_K[1], 2)}", font_size=21),
            buff=0.16)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.2)

        # --- momento: el resto que sobra ----------------------------------
        rot.mostrar(pie_curso("Ese resto no desaparece: cae justo donde el "
                              "vecino tiene que decidir."),
                    zona="abajo", run_time=0.5)
        cola = Line(on.en(1.0, 0.0), on.en(1.0, LENTO_K[1]),
                    color=C_RUIDO, stroke_width=6)
        et_cola = tag_hud("la cola", font_size=19, color=C_RUIDO)
        et_cola.next_to(p1, RIGHT, buff=0.22)
        self.play(Create(cola), FadeIn(et_cola), run_time=0.9)
        self.play(Indicate(p1, color=C_RUIDO, scale_factor=1.6),
                  run_time=0.9)
        self.wait(4.6)
