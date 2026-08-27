class Clip2(Scene):
    """2.1.2 - La linealidad: T{a*x1+b*x2} = a*T{x1}+b*T{x2}, comprobada
    con error de punto flotante. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Linealidad"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        sx1 = Secuencia(X1, 0, ancho=9.4, alto=0.85, color=C_SENAL)
        sx1.move_to(UP * 2.45)
        sy1 = Secuencia(Y1, 0, ancho=9.4, alto=0.85, color=C_SALIDA)
        sy1.move_to(UP * 1.25)
        sx2 = Secuencia(X2, 0, ancho=9.4, alto=0.85, color=C_SENAL)
        sx2.move_to(DOWN * 0.35)
        sy2 = Secuencia(Y2, 0, ancho=9.4, alto=0.85, color=C_SALIDA)
        sy2.move_to(DOWN * 1.55)

        et_x1 = tag_junto(sx1, "x1", LEFT, buff=0.20, font_size=18,
                          color=C_SENAL)
        et_y1 = tag_junto(sy1, "y1", LEFT, buff=0.20, font_size=18,
                          color=C_SALIDA)
        et_x2 = tag_junto(sx2, "x2", LEFT, buff=0.20, font_size=18,
                          color=C_SENAL)
        et_y2 = tag_junto(sy2, "y2", LEFT, buff=0.20, font_size=18,
                          color=C_SALIDA)

        self.play(FadeIn(sx1), FadeIn(et_x1), run_time=0.8)
        self.play(FadeIn(sy1), FadeIn(et_y1), run_time=0.8)
        self.wait(0.7)
        self.play(FadeIn(sx2), FadeIn(et_x2), run_time=0.8)
        self.play(FadeIn(sy2), FadeIn(et_y2), run_time=0.8)
        self.wait(2.2)

        grupo = VGroup(sx1, sy1, sx2, sy2, et_x1, et_y1, et_x2, et_y2)
        self.play(FadeOut(grupo), run_time=0.8)

        sxm = Secuencia(X_MEZCLA, 0, ancho=9.4, alto=1.15, color=C_SENAL)
        sxm.move_to(UP * 1.75)
        et_xm = tag_junto(sxm, "mezcla", LEFT, buff=0.20, font_size=18,
                          color=C_SENAL)
        panel_coef = panel_cifras(f"a = {fmt(A_LIN, 1)}",
                                  f"b = {fmt(B_LIN, 1)}")
        self.play(FadeIn(sxm), FadeIn(et_xm), FadeIn(panel_coef),
                  run_time=1.1)
        self.wait(2.4)

        sym = Secuencia(Y_MEZCLA, 0, ancho=9.4, alto=1.7, color=C_SALIDA)
        sym.move_to(DOWN * 1.20)
        et_ym = tag_junto(sym, "salida", LEFT, buff=0.20, font_size=18,
                          color=C_SALIDA)
        self.play(FadeIn(sym.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sym.tallo(i)) for i in
                                range(len(Y_MEZCLA))], lag_ratio=0.05),
                  LaggedStart(*[FadeIn(sym.punto(i)) for i in
                                range(len(Y_MEZCLA))], lag_ratio=0.05),
                  FadeIn(et_ym), run_time=1.8)
        self.wait(2.2)

        sap = sym.con_valores(Y_APARTE, color=C_IDEAL)
        marcas = VGroup(*[sap.marcar(i, color=C_IDEAL) for i in
                          range(len(Y_APARTE))])
        et_ap = tag_junto(sap, "por separado", UP, buff=0.16,
                          font_size=18, color=C_IDEAL)
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.05),
                  FadeIn(et_ap), run_time=2.0)
        self.wait(3.0)

        rot.mostrar(formula_pie(
            r"T\{a\,x_1 + b\,x_2\} = a\,T\{x_1\} + b\,T\{x_2\}"),
            zona="abajo", run_time=0.5)
        self.wait(3.8)

        rot.mostrar(cifra_pie(f"error max = {ERR_LINEAL:.1e}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
