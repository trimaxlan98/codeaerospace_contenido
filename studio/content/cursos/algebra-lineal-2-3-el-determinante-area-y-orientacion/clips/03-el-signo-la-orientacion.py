class Clip3(Scene):
    """2.3.3 - El determinante trae signo: una reflexion intercambia i y j,
    conserva el tamaño del area y voltea el plano. Al voltearse, la rejilla
    pasa un instante por area cero. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El signo: la orientación")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la orientacion de partida -----------------------------
        pl = plano_leccion(unidad=UNIDAD_3)
        i_hat = vector(pl, (1, 0), color=C_I, nombre=r"\hat{\imath}",
                       etiqueta_dir=DOWN)
        j_hat = vector(pl, (0, 1), color=C_J, nombre=r"\hat{\jmath}",
                       etiqueta_dir=LEFT)
        cuadrado = paralelogramo(pl, np.eye(2))
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("î va a la derecha y ĵ hacia arriba: de î a ĵ "
                              "se gira a la izquierda."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(i_hat.flecha), GrowArrow(j_hat.flecha),
                  run_time=0.7)
        self.play(FadeIn(i_hat.etiqueta), FadeIn(j_hat.etiqueta),
                  FadeIn(cuadrado), run_time=0.6)
        cifra = self._cifra("area = " + fmt(cuadrado.area), 0)
        self.play(FadeIn(cifra), run_time=0.4)
        # El giro de i a j, dibujado: el mismo arco cambiara de sentido.
        curva = self._giro(pl, ida=True)
        tag_giro = tag_hud("i -> j", font_size=18, color=C_TENUE)
        # Pegado a la esquina lejana del cuadrado (no flotando en el vacio ni
        # encima del arco): el rotulo nombra la curva sin taparla.
        tag_giro.next_to(cuadrado, UR, buff=0.14)
        self.play(Create(curva), FadeIn(tag_giro), run_time=0.7)
        self.wait(3.6)

        # --- momento: la matriz que las intercambia -------------------------
        rot.mostrar(pie_curso("Esta matriz los intercambia: î se va arriba "
                              "y ĵ a la derecha."), zona="abajo",
                    run_time=0.5)
        mat = matriz_columnas(M_REFLEJA, font_size=40)
        panel = panel_derecha(mat)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.play(Indicate(mat.columna(0), color=C_I, scale_factor=1.08),
                  run_time=0.7)
        self.play(Indicate(mat.columna(1), color=C_J, scale_factor=1.08),
                  run_time=0.7)
        self.wait(3.0)

        # --- momento: el volteo (pasa por area cero) ------------------------
        rot.mostrar(pie_curso("Al voltearse, la rejilla pasa un instante "
                              "por área cero. Míralo."), zona="abajo",
                    run_time=0.5)
        # Las etiquetas cambian de lado con el destino (con_matriz conserva
        # etiqueta_dir y dejaria la de ĵ encima de su propia flecha).
        i_fin = vector(pl, M_REFLEJA @ i_hat.coords, color=C_I,
                       nombre=r"\hat{\imath}", etiqueta_dir=LEFT)
        j_fin = vector(pl, M_REFLEJA @ j_hat.coords, color=C_J,
                       nombre=r"\hat{\jmath}", etiqueta_dir=DOWN)
        volteado = paralelogramo(pl, M_REFLEJA)
        # La cifra se apaga mientras dura el volteo: durante la animacion el
        # area no es ni la de antes ni la de despues (no se miente en pantalla).
        self.play(*pl.anim_matriz(M_REFLEJA, run_time=2.6),
                  Transform(i_hat, i_fin, run_time=2.6),
                  Transform(j_hat, j_fin, run_time=2.6),
                  Transform(cuadrado, volteado, run_time=2.6),
                  Transform(curva, self._giro(pl, ida=False), run_time=2.6),
                  FadeOut(cifra, run_time=0.6))
        # El AREA es el tamaño (siempre positivo); el SIGNO vive en el det.
        # Si aqui se pintara volteado.area (que trae signo) el HUD diria
        # "area = -1.0" y contradiria el pie "misma area que antes".
        cifra = self._cifra("area = " + fmt(abs(volteado.area)), 0)
        cifra_det = self._cifra("det = " + fmt(DET_REFLEJA), 1)
        self.play(FadeIn(cifra), FadeIn(cifra_det), run_time=0.6)
        self.wait(3.4)

        # --- momento: mismo tamaño, signo contrario -------------------------
        rot.mostrar(pie_curso("Misma área que antes, pero el determinante "
                              "salió negativo."), zona="abajo", run_time=0.5)
        self.play(Indicate(cuadrado, color=C_AREA, scale_factor=1.05),
                  Indicate(cifra_det, color=C_AREA, scale_factor=1.06),
                  run_time=0.9)
        self.wait(4.2)

        # --- momento: qué dice el signo -------------------------------------
        rot.mostrar(pie_curso("El signo dice la orientación: ahora de î a ĵ "
                              "se gira a la derecha."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(curva, color=C_TITULO, scale_factor=1.08),
                  run_time=0.9)
        self.play(Indicate(i_hat, color=C_I, scale_factor=1.05),
                  Indicate(j_hat, color=C_J, scale_factor=1.05),
                  run_time=0.9)
        self.wait(3.6)

        rot.mostrar(pie_curso("¿Y si el área llega a cero y se queda ahí? "
                              "Siguiente clip."), zona="abajo", run_time=0.5)
        self.wait(3.6)

    # -- el arco que va de i a j (o de j a i tras el volteo) ----------------
    def _giro(self, pl, ida=True):
        a, b = pl.p(0.77, 0.21), pl.p(0.21, 0.77)
        desde, hasta = (a, b) if ida else (b, a)
        angulo = (TAU / 6) if ida else (-TAU / 6)
        return CurvedArrow(desde, hasta, angle=angulo, color=C_TENUE,
                           stroke_width=3.0, tip_length=0.18)

    # -- cifra bajo el HUD, con fondo (la rejilla pasa por debajo) ----------
    def _cifra(self, texto, fila=0):
        g = _con_fondo(tag_hud(texto, font_size=20), buff=0.13, opacidad=0.82)
        g.to_corner(UL, buff=0.5).shift(DOWN * (0.66 + 0.46 * fila))
        return g
