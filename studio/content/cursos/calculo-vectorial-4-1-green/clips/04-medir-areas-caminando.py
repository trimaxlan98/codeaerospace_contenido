class Clip4(Scene):
    """4.1.4 - El planimetro: con F = (-y/2, x/2) el rotacional vale 1, de
    modo que el lado de dentro de Green ES el area. La circulacion por el
    circulo da pi*r^2 y por el rectangulo su area. Cierre. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Medir áreas caminando")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el escenario, corrido a la izquierda para el panel -----------
        # (mismo encuadre que el clip 3: la malla acaba en x = 1.85 de
        # pantalla y el panel empieza en ~3.1, asi no se pisan.)
        pl = plano_leccion(centro=CENTRO_PLANO + LEFT * 1.9)
        self.play(FadeIn(pl), run_time=0.8)

        # --- momento: un campo que gira igual en todas partes -------------
        rot.mostrar(pie_curso("Otro campo. Este gira lo MISMO en todos los "
                              "puntos."), zona="abajo", run_time=0.5)
        campo = campo_flechas(pl, F_AREA, paso=1.0, escala=0.55,
                              x0=-2.5, x1=2.5, y0=-1.5, y1=1.5,
                              opacidad=0.55)
        self.play(LaggedStart(*[FadeIn(f, scale=0.5) for f in campo.flechas],
                              lag_ratio=0.05), run_time=1.5)
        rd = rueda(pl, (0.0, 0.0), radio=0.30)
        # Placa OPACA: la fila de flechas y = 0.5 pasa justo por donde cae
        # el rotulo y con el 0.82 de fabrica se transparentaba encima.
        eti = _con_fondo(tag_hud(f"rot F = {fmt(ROT_A)}", font_size=19),
                         buff=0.16, opacidad=1.0)
        eti.next_to(rd, UP, buff=0.20)
        self.play(FadeIn(rd, scale=0.6), FadeIn(eti), run_time=0.6)
        self.play(Rotate(rd.aspas, angle=ROT_A / 2 * 2.6,
                         about_point=rd.centro()),
                  run_time=2.6, rate_func=linear)

        # La ruedecita se retira ANTES de tocar el campo: `campo.animate`
        # vuelve a meter el VGroup entero en la escena y lo deja ENCIMA de
        # lo anterior, asi que las flechas cruzarian la placa del rotulo.
        self.play(FadeOut(rd), FadeOut(eti), run_time=0.45)

        # --- momento: si el rotacional es 1, lo de dentro es el area ------
        rot.mostrar(formula_pie(r"\oint_{\partial R}\mathbf{F}\cdot d\mathbf{r}"
                                r"\;=\;\iint_R 1\, dA\;=\;\mathrm{area}(R)",
                                font_size=34), zona="abajo", run_time=0.5)

        # El circulo de radio R_CIRC y el panel de la cuenta.
        circ = camino(pl, CURVA_CIRC, color=C_REGION, grosor=4.0, flechas=4)
        self.play(campo.animate.fade(0.35), run_time=0.4)
        self.play(Create(circ.trazo), FadeIn(circ.marcas), run_time=1.2)

        eti_cir = MathTex(r"\oint \mathbf{F}\cdot d\mathbf{r}",
                          font_size=32, color=C_REGION)
        num = DecimalNumber(0.0, num_decimal_places=2, color=C_RES,
                            font_size=34)
        fila = VGroup(eti_cir, num).arrange(RIGHT, buff=0.28)
        cmp_cir = MathTex(rf"\pi r^2 = {fmt(AREA_CIRC, 2)}",
                          font_size=30, color=C_CIFRA)
        cmp_reg = MathTex(rf"\mathrm{{area}}(R) = {fmt(AREA_REG, 2)}",
                          font_size=30, color=C_CIFRA)
        panel = panel_derecha(fila, cmp_cir, cmp_reg, buff=0.30)
        # Las dos comparaciones nacen apagadas: el fondo ya reserva su
        # sitio, asi el panel no da un salto cuando aparecen.
        cmp_cir.set_opacity(0.0)
        cmp_reg.set_opacity(0.0)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        # 2.5 s: con menos, la formula del teorema no llega a los 5 s
        # en pantalla que pide el contrato.
        self.wait(2.5)

        # --- momento: caminar el circulo suma su area ---------------------
        rot.mostrar(pie_curso("Recorramos un círculo sumando F·dr. El "
                              "contador va midiendo."), zona="abajo",
                    run_time=0.5)
        ts_cir, val_cir = tabla_acumulada(F_AREA, CURVA_CIRC)
        tc = ValueTracker(1e-3)
        andar = always_redraw(lambda: Dot(pl.p(CURVA_CIRC(tc.get_value())),
                                          radius=0.10, color=C_VEC))
        traza = always_redraw(lambda: VMobject(
            stroke_color=C_VEC, stroke_width=5.0).set_points_as_corners(
                [pl.p(CURVA_CIRC(u))
                 for u in np.linspace(0.0, tc.get_value(), 120)]))
        num.add_updater(lambda m: m.set_value(
            float(np.interp(tc.get_value(), ts_cir, val_cir))))
        num.add_updater(lambda m: m.next_to(eti_cir, RIGHT, buff=0.28))
        self.add(traza, andar)
        self.play(tc.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        num.clear_updaters()
        self.wait(0.8)
        self.play(cmp_cir.animate.set_opacity(1.0),
                  Indicate(num, color=C_RES, scale_factor=1.12),
                  run_time=0.9)
        self.wait(1.2)

        # --- momento: y con el rectangulo, su area ------------------------
        rot.mostrar(pie_curso("Otra figura, misma regla: el paseo devuelve "
                              "el área encerrada."), zona="abajo",
                    run_time=0.5)
        traza.clear_updaters()
        andar.clear_updaters()
        reg = region_rect(pl, X0, X1, Y0, Y1, flechas=6)
        self.play(FadeOut(traza), FadeOut(andar), FadeOut(circ),
                  run_time=0.5)
        self.play(FadeIn(reg), run_time=0.8)
        num.set_value(0.0)
        num.next_to(eti_cir, RIGHT, buff=0.28)

        ts_reg, val_reg = tabla_acumulada(F_AREA, reg.curva)
        tr = ValueTracker(1e-3)
        andar2 = always_redraw(lambda: Dot(pl.p(reg.curva(tr.get_value())),
                                           radius=0.10, color=C_VEC))
        traza2 = always_redraw(lambda: VMobject(
            stroke_color=C_VEC, stroke_width=5.0).set_points_as_corners(
                [pl.p(reg.curva(u))
                 for u in np.linspace(0.0, tr.get_value(), 120)]))
        num.add_updater(lambda m: m.set_value(
            float(np.interp(tr.get_value(), ts_reg, val_reg))))
        num.add_updater(lambda m: m.next_to(eti_cir, RIGHT, buff=0.28))
        self.add(traza2, andar2)
        self.play(tr.animate.set_value(1.0), run_time=3.6, rate_func=linear)
        num.clear_updaters()
        self.wait(0.7)
        self.play(cmp_reg.animate.set_opacity(1.0),
                  Indicate(num, color=C_RES, scale_factor=1.12),
                  run_time=0.9)
        self.wait(1.0)

        # --- momento: el planimetro ---------------------------------------
        rot.mostrar(pie_curso("Los planímetros mecánicos miden áreas así: "
                              "recorriendo el contorno."), zona="abajo",
                    run_time=0.5)
        traza2.clear_updaters()
        andar2.clear_updaters()
        self.wait(4.2)

        # --- cierre --------------------------------------------------------
        cierre_leccion(self, rot,
                       "Lo de dentro se cancela.",
                       "El borde lo cuenta todo.",
                       "Siguiente lección: el flujo y el teorema de la "
                       "divergencia.",
                       pl, campo, reg, traza2, andar2, panel,
                       espera=4.0)
