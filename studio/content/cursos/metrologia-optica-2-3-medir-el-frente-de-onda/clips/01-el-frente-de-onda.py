class Clip1(Scene):
    """1 - El frente de onda. La superficie de fase constante llega PLANA
    de una estrella; una lente imperfecta o la atmosfera la tuercen
    (desenfoque + coma) y esa aberracion no es mas que un mapa de fase
    sobre la pupila, con un RMS de 0.55 ondas MEDIDO por la libreria
    (`frente_onda(...).rms_ondas()`). La deformacion va exagerada y se
    rotula. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("El frente de onda"), zona="arriba",
                    run_time=0.6)

        # Las dos aberraciones clasicas de una lente: un desenfoque y una
        # coma. El RMS sale MEDIDO de la pieza, no escrito a mano.
        COEFS = {"desenfoque": 0.45, "coma": 0.32}

        # La pupila vive en la banda central: centro en y = -0.25 y radio
        # 1.42, asi que las lineas no suben de +1.4 (el titulo empieza en
        # +2.95) ni bajan de -1.7 (ahi arrancan los tags).
        frente = frente_onda(None, radio=1.42, escala_ondas=0.105)
        frente.remove(frente.lectura)      # el RMS entra despues, como tag
        frente.shift(DOWN * 0.25 - frente.pupila.get_center())

        # --- momento: de una estrella, el frente llega plano ---------------
        rot.mostrar(pie_curso("El frente de onda es la superficie de fase "
                              "constante: de una estrella llega plano."),
                    zona="abajo")
        self.play(Create(frente.pupila), run_time=0.7)
        self.play(LaggedStart(*[Create(l) for l in frente.lineas],
                              lag_ratio=0.12), run_time=1.7)
        # Consolidar el grupo: manim saca del nivel superior a las partes
        # que ya estaban sueltas, asi que el Transform de despues no deja
        # fantasmas.
        self.add(frente)
        t_plano = tag_hud("frente plano", font_size=17, color=C_ONDA)
        t_plano.next_to(frente.pupila, DOWN, buff=0.30)
        self.play(FadeIn(t_plano), run_time=0.4)
        self.wait(4.2)

        # --- momento: la lente y la atmosfera lo tuercen -------------------
        rot.mostrar(pie_curso("Una lente imperfecta o la atmósfera lo "
                              "tuercen: eso es una aberración."),
                    zona="abajo")
        torcido = frente.con_coeficientes(COEFS)
        torcido.remove(torcido.lectura)    # la gemela tiene que casar 1 a 1
        self.play(FadeOut(t_plano), run_time=0.3)
        self.play(Transform(frente, torcido), run_time=2.0)
        t_aber = tag_hud("desenfoque + coma", font_size=17, color=C_ONDA)
        t_aber.next_to(frente.pupila, DOWN, buff=0.30)
        t_esc = tag_hud("deformacion exagerada", font_size=13, color=C_TENUE)
        t_esc.next_to(t_aber, DOWN, buff=0.14)
        self.play(FadeIn(t_aber), FadeIn(t_esc), run_time=0.5)
        self.wait(4.4)

        # --- momento: la aberracion es un mapa de fase --------------------
        rot.mostrar(pie_curso("La aberración es un mapa de fase sobre la "
                              "pupila."), zona="abajo")
        t_rms = tag_hud(f"rms = {torcido.rms_ondas():.2f} lambda",
                        font_size=19)
        t_rms.next_to(frente, UP, buff=0.32)
        self.play(FadeIn(t_rms, shift=0.10 * DOWN), run_time=0.5)
        self.play(Indicate(frente.pupila, color=C_MEDIDA, scale_factor=1.04),
                  run_time=1.0)
        self.wait(4.8)

        # --- cierre --------------------------------------------------------
        rot.mostrar(pie_curso("Antes de corregir un frente hay que medirlo."),
                    zona="abajo")
        self.wait(6.0)
