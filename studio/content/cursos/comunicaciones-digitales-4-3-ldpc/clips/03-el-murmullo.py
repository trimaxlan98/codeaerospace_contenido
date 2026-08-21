class Clip3(Scene):
    """4.3.3 - El murmullo (bit-flipping): las iteraciones de
    ldpc_decodificar en pantalla, con el peso del sindrome bajando
    6 -> 3 -> 0 y el grafo quedando verde. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El murmullo que corrige")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        g = grafo_ldpc(H_LDPC, X_ERROR, S_ERROR, ancho=ANCHO_GRAFO,
                       alto=ALTO_GRAFO)
        g.move_to(POS_GRAFO)

        # el diario de iteraciones sale ENTERO de ldpc_decodificar
        textos = []
        for k, (_, s, v) in enumerate(PASOS_LDPC):
            fin = "" if v is None else f"   volteo b{v}"
            textos.append(f"it {k}   peso s = {int(s.sum())}{fin}")
        lineas = VGroup(*[tag_hud(t, font_size=16,
                                  color=C_COD if p == 0 else C_CIFRA)
                          for t, p in zip(textos, PESOS_S)])
        lineas.arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        cab = tag_hud("bit-flipping", font_size=15, color=C_TENUE)
        panel = panel_derecha(cab, lineas, buff=0.26)
        fondo = panel[0]

        def cuenta_bajo(i, cuentas):
            t = tag_hud(f"{int(cuentas[i])} de {PESO_COL}", font_size=17)
            t.next_to(g.bit(i), DOWN, buff=0.22)
            return t

        # --- momento: la regla tonta que basta ----------------------------
        rot.mostrar(pie_curso("La regla del murmullo es tonta: voltear el "
                              "bit al que mas comprobaciones acusan."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(g), FadeIn(fondo), FadeIn(cab), run_time=0.9)
        self.play(FadeIn(lineas[0]), run_time=0.4)
        self.wait(4.4)

        # --- iteracion 1: cae el bit mas acusado --------------------------
        rot.mostrar(pie_curso(f"Primera iteracion: el bit {VOLTEOS[0]} "
                              f"lleva las tres acusaciones. Se voltea."),
                    zona="abajo", run_time=0.5)
        c0 = cuenta_bajo(VOLTEOS[0], CUENTAS_0)
        self.play(FadeIn(c0), Indicate(g.bit(VOLTEOS[0]), color=C_RUIDO,
                                       scale_factor=1.5), run_time=0.9)
        g1 = g.con_estado(PASOS_LDPC[1][0], PASOS_LDPC[1][1])
        self.play(Transform(g, g1), FadeOut(c0), run_time=1.2)
        self.play(FadeIn(lineas[1]), run_time=0.4)
        self.wait(4.0)

        # --- iteracion 2: el que queda ------------------------------------
        rot.mostrar(pie_curso(f"Se vuelve a contar. Ahora solo el bit "
                              f"{VOLTEOS[1]} sigue acusado por sus tres."),
                    zona="abajo", run_time=0.5)
        cuentas_1 = H_LDPC.T @ PASOS_LDPC[1][1]
        c1 = cuenta_bajo(VOLTEOS[1], cuentas_1)
        self.play(FadeIn(c1), Indicate(g.bit(VOLTEOS[1]), color=C_RUIDO,
                                       scale_factor=1.5), run_time=0.9)
        g2 = g.con_estado(PASOS_LDPC[2][0], PASOS_LDPC[2][1])
        self.play(Transform(g, g2), FadeOut(c1), run_time=1.2)
        self.play(FadeIn(lineas[2]), run_time=0.4)
        self.wait(3.8)

        # --- el sindrome en cero ------------------------------------------
        rot.mostrar(pie_curso(f"Peso {PESOS_S[0]}, {PESOS_S[1]}, "
                              f"{PESOS_S[-1]}: las nueve vuelven a dar "
                              f"par. Los dos errores, corregidos."),
                    zona="abajo", run_time=0.5)
        self.play(destello(g.checks, color=C_COD), run_time=1.2)
        self.wait(4.6)

        # --- lo que nadie sabia -------------------------------------------
        rot.mostrar(pie_curso("Ninguna comprobacion conocia el mensaje: "
                              "solo su vecindario. Entre todas, lo "
                              "reconstruyeron."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
