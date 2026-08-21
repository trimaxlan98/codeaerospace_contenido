class Clip3(Scene):
    """4.1.3 - Los dos lados de Green, medidos por separado: la circulacion
    caminando el borde y la integral doble barriendo el interior. Las dos
    cuentas dan 8.00. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La comprobación")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el escenario, corrido a la izquierda para el panel -----------
        pl = plano_leccion(centro=CENTRO_PLANO + LEFT * 1.9)
        self.play(FadeIn(pl), run_time=0.8)
        campo = campo_flechas(pl, F_GREEN, paso=1.0, escala=0.55,
                              x0=-2.5, x1=2.5, y0=-1.5, y1=1.5,
                              opacidad=0.34)
        reg = region_rect(pl, X0, X1, Y0, Y1, flechas=6)

        # Los dos lados, medidos con la libreria (nada escrito a mano).
        lado_borde = circulacion(F_GREEN, reg.curva)
        ts_borde, val_borde = tabla_acumulada(F_GREEN, reg.curva)
        xs_dentro, val_dentro = tabla_barrido(
            lambda p: rot_num(F_GREEN, p), X0, X1, Y0, Y1)

        rot.mostrar(pie_curso("Green promete que dos cuentas muy distintas "
                              "dan el mismo número."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(campo), FadeIn(reg), run_time=1.0)

        eti_borde = MathTex(r"\oint_{\partial R} \mathbf{F}\cdot d\mathbf{r}",
                            font_size=32, color=C_REGION)
        num_borde = DecimalNumber(0.0, num_decimal_places=2, color=C_RES,
                                  font_size=34)
        fila_borde = VGroup(eti_borde, num_borde).arrange(RIGHT, buff=0.28)
        eti_dentro = MathTex(r"\iint_R (\nabla\times\mathbf{F})\, dA",
                             font_size=32, color=C_CIFRA)
        num_dentro = DecimalNumber(0.0, num_decimal_places=2, color=C_RES,
                                   font_size=34)
        fila_dentro = VGroup(eti_dentro, num_dentro).arrange(RIGHT, buff=0.28)
        igualdad = MathTex(f"{fmt(lado_borde, 2)} = {fmt(val_dentro[-1], 2)}",
                           font_size=44, color=C_RES)
        panel = panel_derecha(fila_borde, fila_dentro, igualdad, buff=0.32)
        igualdad.set_opacity(0.0)      # se enciende cuando ya esta medido
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.2)

        # --- cuenta uno: caminar el borde ---------------------------------
        rot.mostrar(pie_curso("Cuenta uno: caminar el BORDE sumando F·dr "
                              "paso a paso."), zona="abajo", run_time=0.5)
        tr = ValueTracker(1e-3)
        andar = always_redraw(lambda: Dot(pl.p(reg.curva(tr.get_value())),
                                          radius=0.10, color=C_VEC))
        traza = always_redraw(lambda: VMobject(
            stroke_color=C_VEC, stroke_width=5.0).set_points_as_corners(
                [pl.p(reg.curva(u))
                 for u in np.linspace(0.0, tr.get_value(), 90)]))
        num_borde.add_updater(lambda m: m.set_value(
            float(np.interp(tr.get_value(), ts_borde, val_borde))))
        num_borde.add_updater(
            lambda m: m.next_to(eti_borde, RIGHT, buff=0.28))
        self.add(traza, andar)
        self.play(tr.animate.set_value(1.0), run_time=5.0, rate_func=linear)
        self.wait(1.2)
        num_borde.clear_updaters()
        self.play(Indicate(num_borde, color=C_RES, scale_factor=1.15),
                  run_time=0.8)
        self.wait(1.4)

        # --- cuenta dos: barrer el interior -------------------------------
        rot.mostrar(pie_curso("Cuenta dos: barrer el INTERIOR sumando el "
                              "rotacional, sin pisar el borde."),
                    zona="abajo", run_time=0.5)
        traza.clear_updaters()
        andar.clear_updaters()
        self.play(FadeOut(traza), FadeOut(andar), run_time=0.5)
        sx = ValueTracker(X0 + 1e-3)
        cortina = always_redraw(lambda: Polygon(
            pl.p(X0, Y0), pl.p(sx.get_value(), Y0),
            pl.p(sx.get_value(), Y1), pl.p(X0, Y1),
            stroke_width=0, fill_color=C_CIFRA, fill_opacity=0.35))
        filo = always_redraw(lambda: Line(
            pl.p(sx.get_value(), Y0), pl.p(sx.get_value(), Y1),
            color=C_CIFRA, stroke_width=4.0))
        num_dentro.add_updater(lambda m: m.set_value(
            float(np.interp(sx.get_value(), xs_dentro, val_dentro))))
        num_dentro.add_updater(
            lambda m: m.next_to(eti_dentro, RIGHT, buff=0.28))
        self.add(cortina, filo)
        self.play(sx.animate.set_value(X1), run_time=5.0, rate_func=linear)
        self.wait(1.2)
        num_dentro.clear_updaters()
        self.play(Indicate(num_dentro, color=C_RES, scale_factor=1.15),
                  run_time=0.8)
        self.wait(1.4)

        # --- el veredicto -------------------------------------------------
        rot.mostrar(pie_curso("El mismo número por los dos caminos: el "
                              "teorema, comprobado."), zona="abajo",
                    run_time=0.5)
        cortina.clear_updaters()
        filo.clear_updaters()
        self.play(igualdad.animate.set_opacity(1.0), run_time=0.8)
        self.wait(5.0)
