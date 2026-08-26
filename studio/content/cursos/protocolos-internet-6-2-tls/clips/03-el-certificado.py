class Clip3(Scene):
    """6.2.3 - El certificado y su cadena: raiz -> intermedia -> sitio con
    firmas RSA de verdad. Verificar es comparar DOS numeros; al alterar un
    byte, 2840 deja de ser 60 y la firma falla. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        rot.mostrar(titulo_curso("El certificado y su cadena"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        YS = (1.80, 0.15, -1.50)          # una fila por eslabon
        arb = arbol([[ESL[0]["quien"]], [ESL[1]["quien"]], [ESL[2]["quien"]]],
                    ancho=2.0, alto=3.30, fs=15, color=C_CLAVE,
                    color_marca=C_OK)
        arb.shift(LEFT * 4.0 + UP * 0.15)

        juguete = tag_hud("RSA de juguete:   e = %d    n = %d"
                          % (RSA_E, RSA_N), font_size=17, color=C_CIFRA)
        juguete.move_to(RIGHT * 2.7 + UP * 2.52)

        def par(i, hash_val, abre_val, color=C_CIFRA):
            """Las dos cifras que hay que comparar, alineadas."""
            a = tag_hud("hash del cuerpo    %4d" % hash_val,
                        font_size=17, color=color)
            a.move_to(np.array([-2.6, YS[i] + 0.24, 0.0]), aligned_edge=LEFT)
            b = tag_hud("al abrir la firma  %4d" % abre_val,
                        font_size=17, color=C_CIFRA)
            b.move_to(np.array([-2.6, YS[i] - 0.24, 0.0]), aligned_edge=LEFT)
            return a, b

        def veredicto(i, texto, color):
            t = tag_hud(texto, font_size=17, color=color)
            t.move_to(np.array([0.85, YS[i], 0.0]), aligned_edge=LEFT)
            return t

        # --- momento: la cadena, no el sitio ------------------------------
        rot.mostrar(pie_curso("El sitio no te pide que le creas: te ensena "
                              "una cadena de firmas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(arb), run_time=1.0)
        self.play(FadeIn(juguete), run_time=0.5)
        self.wait(3.2)

        # --- momento: cada eslabon firma al siguiente ---------------------
        rot.mostrar(pie_curso("Cada eslabon firma el hash del siguiente "
                              "con su clave privada."),
                    zona="abajo", run_time=0.5)
        h0, f0 = par(0, ESL[0]["hash"], CERT_ABRE[0])
        h1, f1 = par(1, ESL[1]["hash"], CERT_ABRE[1])
        self.play(FadeIn(h0), FadeIn(f0), FadeIn(h1), FadeIn(f1),
                  run_time=0.6)
        self.play(Transform(arb, arb.con_marcados([(0, 0), (1, 0)])),
                  run_time=0.5)
        v0, v1 = veredicto(0, "coinciden", C_OK), veredicto(1, "coinciden",
                                                            C_OK)
        self.play(FadeIn(v0), FadeIn(v1), run_time=0.4)
        self.wait(3.4)

        # --- momento: verificar es comparar dos numeros -------------------
        rot.mostrar(pie_curso("Verificar es abrir la firma con la clave "
                              "publica y comparar dos numeros."),
                    zona="abajo", run_time=0.5)
        cuerpo = tag_hud("cuerpo:  %s" % ESL[2]["cuerpo"], font_size=17,
                         color=C_EJE)
        cuerpo.move_to(np.array([-2.6, YS[2] + 0.72, 0.0]), aligned_edge=LEFT)
        h2, f2 = par(2, ESL[2]["hash"], CERT_ABRE[2])
        self.play(FadeIn(cuerpo), FadeIn(h2), FadeIn(f2), run_time=0.6)
        self.play(Transform(arb, arb.con_marcados([(0, 0), (1, 0), (2, 0)])),
                  run_time=0.5)
        v2 = veredicto(2, "coinciden", C_OK)
        self.play(FadeIn(v2), run_time=0.4)
        val = tag_hud("cadena valida", font_size=22, color=C_OK)
        val.move_to(RIGHT * 4.0 + DOWN * 2.35)
        caja = SurroundingRectangle(val, color=C_OK, buff=0.18,
                                    stroke_width=2.2)
        val_g = VGroup(caja, val)
        self.play(FadeIn(val_g), run_time=0.5)
        self.wait(3.6)

        # --- momento: se altera un byte -----------------------------------
        rot.mostrar(pie_curso("Se cambia un solo byte del certificado del "
                              "sitio: el cuerpo ya no es el mismo."),
                    zona="abajo", run_time=0.5)
        cuerpo_mal = tag_hud("cuerpo:  %s   (un byte de mas)"
                             % ESL_MAL["cuerpo"], font_size=17,
                             color=C_PERDIDA)
        cuerpo_mal.move_to(np.array([-2.6, YS[2] + 0.72, 0.0]),
                           aligned_edge=LEFT)
        h2_mal = tag_hud("hash del cuerpo    %4d" % CERT_HASH_MAL,
                         font_size=17, color=C_PERDIDA)
        h2_mal.move_to(np.array([-2.6, YS[2] + 0.24, 0.0]), aligned_edge=LEFT)
        v2_mal = veredicto(2, "NO coinciden", C_PERDIDA)
        self.play(FadeOut(cuerpo), FadeOut(h2), FadeOut(v2),
                  FadeOut(val_g), run_time=0.5)
        self.play(FadeIn(cuerpo_mal), FadeIn(h2_mal), run_time=0.5)
        self.wait(4.2)

        # --- momento: la firma no falla porque si -------------------------
        rot.mostrar(pie_curso("La firma no fallo porque si: fallo porque "
                              "%d y %d dejaron de coincidir."
                              % (CERT_HASH_MAL, CERT_ABRE_MAL)),
                    zona="abajo", run_time=0.5)
        mal = tag_hud("cadena NO valida", font_size=22, color=C_PERDIDA)
        mal.move_to(RIGHT * 4.0 + DOWN * 2.35)
        caja_mal = SurroundingRectangle(mal, color=C_PERDIDA, buff=0.18,
                                        stroke_width=2.4)
        self.play(FadeIn(v2_mal), FadeIn(VGroup(caja_mal, mal)),
                  arb.nodo(2, 0).animate.set_stroke(C_PERDIDA, width=3.6),
                  run_time=0.6)
        self.wait(4.4)
