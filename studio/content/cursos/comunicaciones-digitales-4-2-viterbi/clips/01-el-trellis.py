class Clip1(Scene):
    """4.2.1 - El trellis: la rejilla con los 256 caminos posibles del
    codificador, y el unico que dibujo el mensaje verdadero. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El trellis: todos los caminos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tr = trellis(pasos=PASOS, ancho=8.6, alto=2.8)
        tr.move_to(DOWN * 0.35)

        def medio(t, s0, s1):
            return (tr.nodo(t, s0) + tr.nodo(t + 1, s1)) / 2.0

        # --- momento: los cuatro estados, repetidos en el tiempo ----------
        rot.mostrar(pie_curso("El codificador con memoria solo puede estar "
                              "en cuatro estados: 00, 01, 10 y 11."),
                    zona="abajo", run_time=0.5)
        et_tiempo = tag_junto(tr, "tiempo", direccion=DOWN, buff=0.26)
        self.play(FadeIn(tr), run_time=0.9)
        self.play(FadeIn(et_tiempo), run_time=0.4)
        self.wait(4.2)

        # --- momento: dos ramas por nodo ----------------------------------
        rot.mostrar(pie_curso("Cada bit que entra lo empuja a otro estado: "
                              "de cada nodo salen dos ramas."),
                    zona="abajo", run_time=0.5)
        ram_0 = tr.rama(0, 0, destino_rama(0, 0), color=C_SENAL, grosor=2.6)
        ram_1 = tr.rama(0, 0, destino_rama(0, 1), color=C_SENAL, grosor=2.6)
        et_0 = tag_hud("bit 0", font_size=17, color=C_BIT)
        et_0.next_to(medio(0, 0, destino_rama(0, 0)), UP, buff=0.12)
        et_1 = tag_hud("bit 1", font_size=17, color=C_BIT)
        # la rama del bit 1 BAJA hacia la derecha: la etiqueta va arriba a
        # la derecha del punto medio, en el hueco entre las dos ramas.
        et_1.move_to(medio(0, 0, destino_rama(0, 1)) + RIGHT * 0.52
                     + UP * 0.30)
        self.play(Create(ram_0), Create(ram_1), run_time=1.1)
        self.play(FadeIn(et_0), FadeIn(et_1), run_time=0.5)
        panel = panel_derecha(tag_hud(f"K = {CONV_K}"),
                              tag_hud(f"G = {CONV_G} octal"),
                              tag_hud(f"tasa {CONV_TASA}"), buff=0.22)
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(3.4)

        # --- momento: la rejilla entera -----------------------------------
        rot.mostrar(pie_curso(f"Con ocho bits hay {N_CAMINOS} caminos "
                              f"posibles. Todos caben en esta rejilla."),
                    zona="abajo", run_time=0.5)
        ramas = tr.todas_ramas(color=C_REJILLA, grosor=1.2, opacidad=0.55)
        columnas = [VGroup(*[ramas[idx_rama(t, s, b)]
                             for s, b, _s2, _sal in RAMAS_CONV])
                    for t in range(PASOS)]
        self.play(LaggedStart(*[Create(c) for c in columnas],
                              lag_ratio=0.35), run_time=2.8)
        self.wait(2.6)

        # --- momento: el camino verdadero ---------------------------------
        rot.mostrar(pie_curso("El mensaje verdadero es UNO de ellos: el "
                              "camino que el codificador recorrio."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(MENSAJE, lado=0.5)
        tren.move_to(UP * 2.15)
        et_tren = tag_junto(tren, "el mensaje, 8 bits", direccion=LEFT,
                            buff=0.28)
        self.play(FadeOut(ram_0), FadeOut(ram_1), FadeOut(et_0),
                  FadeOut(et_1), FadeIn(tren), FadeIn(et_tren),
                  run_time=0.8)
        camino = tr.camino(ESTADOS, color=C_BIT, grosor=3.4)
        self.play(Create(camino), run_time=2.4)
        self.wait(2.4)

        # --- momento: el problema -----------------------------------------
        rot.mostrar(pie_curso("El receptor no ve el camino: ve la señal. "
                              "Decodificar es encontrarlo."),
                    zona="abajo", run_time=0.5)
        self.play(camino.animate.set_stroke(opacity=0.25), run_time=0.8)
        self.wait(4.8)
