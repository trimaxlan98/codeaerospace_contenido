class Clip3(Scene):
    """4.1.3 - Barrer lambda: la rejilla de A - lambda I se aplasta justo al
    pasar por 1 y por 3, y ahi una flecha cae al cero. Esos son los ceros de
    det(A - lambda I). (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        # (el titulo va en Rajdhani, que no trae lambda: la formula del
        # storyboard aparece en MathTex, en el pie y sobre la curva)
        titulo = titulo_curso("Encontrarlos sin adivinar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la pregunta -------------------------------------------
        pl = plano_leccion()
        v3 = vector(pl, V_CAE_3, color=C_PROPIO, grosor=5.5)
        v1 = vector(pl, V_CAE_1, color=C_PROPIO, grosor=5.5)
        panel = panel_derecha(matriz_columnas(A_PROPIA, font_size=38))
        self.play(FadeIn(pl), run_time=0.8)
        # (las flechas ya estan en fucsia desde el clip 2: el pie no puede
        # decir "no se ven" mientras se ven; lo que falta es CALCULARLAS)
        rot.mostrar(pie_curso("Estas dos ya las conocemos de vista. Falta "
                              "saber calcularlas."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(v3.flecha), GrowArrow(v1.flecha), run_time=0.9)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.8)

        # --- momento: la condicion ------------------------------------------
        rot.mostrar(formula_pie(r"A\vec v = \lambda\vec v \quad "
                                r"\Longleftrightarrow \quad "
                                r"(A - \lambda I)\,\vec v = \vec 0"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: empezamos a restar (lambda = 0) -----------------------
        rot.mostrar(pie_curso("Restamos a la diagonal y miramos qué le pasa "
                              "al determinante."), zona="abajo", run_time=0.5)
        caja = self._caja(PARADAS[0], A_MENOS[0])
        self.play(*pl.anim_matriz(A_MENOS[0], v3, v1), run_time=1.4)
        self.play(FadeIn(caja), run_time=0.4)
        self.wait(2.6)

        # --- momento: en lambda = 1 el plano cae sobre una recta ------------
        # OJO: v3 y v1 conservan sus coords de partida a proposito. Como
        # anim_matriz quiere la matriz TOTAL desde la identidad, no se
        # reasignan entre pasos (si no, el destino seria M2 @ M1 @ v).
        rot.mostrar(pie_curso("En uno, el plano entero cae sobre una recta: "
                              "una flecha llega al cero."),
                    zona="abajo", run_time=0.5)
        caja_2 = self._caja(PARADAS[1], A_MENOS[1])
        self.play(FadeOut(caja), *pl.anim_matriz(A_MENOS[1], v3, v1),
                  run_time=1.6)
        muere_1 = self._cae(pl, V_CAE_1)
        self.play(FadeIn(caja_2), FadeIn(muere_1), run_time=0.5)
        self.play(Flash(pl.p(0, 0), color=C_PROPIO, line_length=0.18,
                        num_lines=12, flash_radius=0.34), run_time=0.6)
        self.wait(2.2)

        # --- momento: seguimos hasta lambda = 3 -----------------------------
        # El Transform interpola las dos matrices, y eso es exactamente
        # barrer lambda de 1 a 3: la rejilla se abre y se vuelve a aplastar.
        rot.mostrar(pie_curso("Seguimos hasta tres: se abre, y se vuelve a "
                              "aplastar. Cae la otra."),
                    zona="abajo", run_time=0.5)
        caja_3 = self._caja(PARADAS[2], A_MENOS[2])
        self.play(FadeOut(caja_2), FadeOut(muere_1),
                  *pl.anim_matriz(A_MENOS[2], v3, v1), run_time=2.0)
        muere_3 = self._cae(pl, V_CAE_3)
        self.play(FadeIn(caja_3), FadeIn(muere_3), run_time=0.5)
        self.play(Flash(pl.p(0, 0), color=C_PROPIO, line_length=0.18,
                        num_lines=12, flash_radius=0.34), run_time=0.6)
        self.wait(2.0)

        # --- momento: la curva del determinante -----------------------------
        rot.mostrar(pie_curso("Ese determinante, en función de lo que "
                              "restamos, es una curva."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pl), FadeOut(v3), FadeOut(v1), FadeOut(caja_3),
                  FadeOut(muere_3), FadeOut(panel), run_time=0.6)

        def det_de(lam):
            return determinante(A_PROPIA - lam * np.eye(2))

        # (sin etiqueta_x: el rotulo de la libreria cae en la punta del eje,
        # a un pelo de la marca de lambda = 3; el eje se nombra en el titulo)
        curva = grafica(det_de, RANGO_LAMBDA, RANGO_DET, ancho=6.8, alto=3.1,
                        color=C_J)
        curva.move_to(UP * 0.12)
        rotulo = MathTex(r"\det(A - \lambda I)\ \text{frente a}\ \lambda",
                         font_size=34, color=C_J)
        rotulo.next_to(curva, UP, buff=0.22)
        self.play(FadeIn(curva), FadeIn(rotulo), run_time=1.0)

        ceros = VGroup()
        for lam, lado in ((LAMBDAS[1], DOWN + LEFT),
                          (LAMBDAS[0], DOWN + RIGHT)):
            punto = Dot(curva.punto_de(lam), radius=0.08, color=C_PROPIO)
            marca = MathTex(r"\lambda = " + fmt(lam, 0), font_size=28,
                            color=C_PROPIO)
            marca.next_to(punto, lado, buff=0.12)
            ceros.add(punto, marca)
        # La moraleja va bajo la curva, no en el pie: el pie lo ocupa la
        # ecuacion caracteristica y las dos ideas tienen que verse juntas.
        # (Rajdhani no trae lambda, por eso "esos dos numeros" y no la letra.)
        nota = VGroup(
            Text("Donde la curva vale cero, el plano se aplasta:",
                 font_size=22, color=C_TENUE),
            Text("esos dos números son los valores propios.",
                 font_size=22, color=C_TENUE)).arrange(DOWN, buff=0.12)
        nota.next_to(curva, DOWN, buff=0.28)
        self.play(FadeIn(ceros), FadeIn(nota), run_time=0.8)
        self.wait(2.6)

        # --- momento: la ecuacion caracteristica ----------------------------
        rot.mostrar(formula_pie(r"\lambda^2" + self._signo(POLI_CARAC[1])
                                + r"\lambda" + self._signo(POLI_CARAC[2])
                                + r" = (\lambda - " + fmt(LAMBDAS[1], 0)
                                + r")(\lambda - " + fmt(LAMBDAS[0], 0) + ")"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

    # -- la cifra de lambda, la matriz A - lambda I y su determinante -------
    def _caja(self, lam, m):
        cifra = MathTex(r"\lambda = " + fmt(lam, 0), font_size=30, color=C_J)
        resta = matriz_columnas(m, font_size=30)
        det = tag_hud("det = " + fmt(determinante(m)), font_size=19)
        g = VGroup(cifra, resta, det).arrange(DOWN, buff=0.2)
        caja = _con_fondo(g, buff=0.16, opacidad=0.82)
        caja.to_corner(UL, buff=0.5).shift(DOWN * 0.85)
        return caja

    # -- la flecha que muere en el cero -------------------------------------
    def _cae(self, pl, coords):
        """Donde ESTABA la flecha (fantasma a trazos) y el punto gordo del
        cero al que ha llegado. Sin esto, la flecha anulada es un pixel en el
        origen y el 'llega al cero' del pie no se ve en pantalla."""
        fantasma = DashedVMobject(
            Line(pl.p(0, 0), pl.p(coords), color=C_PROPIO, stroke_width=5.0),
            num_dashes=9)
        fantasma.set_stroke(opacity=0.5)
        punto = Dot(pl.p(0, 0), radius=0.13, color=C_PROPIO)
        return VGroup(fantasma, punto)

    # -- signo explicito de un coeficiente calculado ------------------------
    def _signo(self, c):
        return (" - " if c < 0 else " + ") + fmt(abs(c), 0)
