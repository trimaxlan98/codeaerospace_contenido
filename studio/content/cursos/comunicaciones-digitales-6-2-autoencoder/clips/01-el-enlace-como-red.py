class Clip1(Scene):
    """6.2.1 - El enlace entero como UNA red: codificador, canal con
    ruido y decodificador entrenados extremo a extremo; la perdida es
    una cota del propio error. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El enlace como una sola red")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: las dos mitades del enlace --------------------------
        rot.mostrar(pie_curso("Un enlace tiene dos mitades: la que elige "
                              "el punto y la que lo adivina."),
                    zona="abajo", run_time=0.5)

        mensaje = tren_bits([1, 0, 1], lado=0.44)
        cod = perceptron_mini(ocultas=6, salidas=2, ancho=1.9, alto=2.1)
        canal = bloque("canal", ancho=1.5, alto=0.95, color=C_SENAL,
                       color_texto=C_SENAL, tamano=21)
        dec = perceptron_mini(ocultas=6, salidas=8, ancho=1.9, alto=2.4)
        recibido = tren_bits([1, 0, 1], lado=0.44)
        cadena = VGroup(mensaje, cod, canal, dec, recibido)
        cadena.arrange(RIGHT, buff=0.62)
        cadena.move_to(UP * 0.08)

        flechas = VGroup(conectar(mensaje, cod, color=C_EJE),
                         conectar(cod, canal, color=C_EJE),
                         conectar(canal, dec, color=C_EJE),
                         conectar(dec, recibido, color=C_EJE))
        self.play(FadeIn(cadena), FadeIn(flechas), run_time=1.1)

        et_cod = tag_junto(cod, "codificador", direccion=DOWN, buff=0.22)
        et_dec = tag_junto(dec, "decodificador", direccion=DOWN, buff=0.22)
        et_msg = tag_junto(mensaje, "3 bits", direccion=DOWN, buff=0.22,
                           color=C_BIT)
        et_rec = tag_junto(recibido, "3 bits", direccion=DOWN, buff=0.22,
                           color=C_BIT)
        et_iq = tag_junto(cod.capas[2], "I, Q", direccion=UP, buff=0.14,
                          font_size=16, color=C_CIFRA)
        self.play(FadeIn(et_cod), FadeIn(et_dec), FadeIn(et_msg),
                  FadeIn(et_rec), FadeIn(et_iq), run_time=0.7)
        self.wait(4.1)

        # --- momento: las dos mitades son redes ---------------------------
        rot.mostrar(pie_curso("Y las dos pueden ser redes: una dibuja la "
                              "constelación, la otra decide cuál era."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(cod.capas[1], color=C_IA, scale_factor=1.25),
                  run_time=0.9)
        self.play(Indicate(dec.capas[1], color=C_IA, scale_factor=1.25),
                  run_time=0.9)
        et_sal = tag_junto(dec.capas[2], "1 de 8", direccion=UP, buff=0.14,
                           font_size=16, color=C_COD)
        self.play(FadeIn(et_sal), run_time=0.5)
        self.wait(3.6)

        # --- momento: en medio, el canal ----------------------------------
        rot.mostrar(pie_curso("En medio está el canal. El ruido no se "
                              "aprende: se sufre."),
                    zona="abajo", run_time=0.5)
        # el ruido llueve sobre el canal: dispersion fija, nunca al azar
        motas = ((-0.52, 0.16), (-0.22, 0.42), (0.06, 0.12),
                 (0.34, 0.38), (0.58, 0.10), (-0.36, 0.02), (0.20, 0.56))
        base = canal.get_top() + UP * 0.16
        chispas = VGroup(*[Dot(base + np.array([dx, dy, 0.0]), radius=0.045,
                               color=C_RUIDO) for dx, dy in motas])
        et_ruido = tag_junto(canal, "+ ruido", direccion=DOWN, buff=0.16,
                             font_size=17, color=C_RUIDO)
        self.play(FadeIn(chispas, scale=0.4), FadeIn(et_ruido),
                  run_time=0.7)
        self.play(flujo(list(flechas), color=C_BIT, por_conexion=0.5),
                  run_time=2.0)
        self.wait(3.4)

        # --- momento: extremo a extremo -----------------------------------
        rot.mostrar(pie_curso("Se entrena TODO junto, de extremo a "
                              "extremo: la pérdida es una cota del propio "
                              "error."),
                    zona="abajo", run_time=0.5)
        br = llave(VGroup(cod, canal, dec, et_cod, et_dec, et_ruido),
                   "una sola red", direccion=DOWN, font_size=21, color=C_IA)
        self.play(FadeIn(br), run_time=0.8)
        self.wait(4.6)

        # --- momento: la perdida que se minimiza --------------------------
        # La formula va ARRIBA (la franja libre entre titulo y esquema):
        # abajo chocaria con la etiqueta de la llave.
        rot.mostrar(pie_curso("Y bajar esa cota es, literalmente, separar "
                              "los puntos en el plano."),
                    zona="abajo", run_time=0.5)
        form = MathTex(
            r"\mathcal{L}=\sum_{i\neq j} e^{-d_{ij}^{2}/8\sigma^{2}}",
            font_size=40, color=C_CALCULO)
        form.move_to(UP * 2.25)
        self.play(FadeIn(_con_fondo(form, buff=0.16), shift=0.12 * DOWN),
                  run_time=0.7)
        self.wait(5.2)
