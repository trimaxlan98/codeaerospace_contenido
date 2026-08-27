class Clip3(Scene):
    """2.1.3 - Retardar la entrada 7 muestras retarda la salida 7: la
    forma no cambia, solo el sitio. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Invarianza en el tiempo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        w = 0.34
        x0 = -4.5

        def alinear(seq):
            actual = seq.en(0, 0)[0]
            seq.shift(RIGHT * (x0 - actual))
            return seq

        secx1 = Secuencia(X1, 0, ancho=w * len(X1), alto=0.85,
                          color=C_SENAL)
        alinear(secx1).shift(UP * 2.35)
        secxr = Secuencia(X_RETARDADA, 0, ancho=w * len(X_RETARDADA),
                          alto=0.85, color=C_SENAL)
        alinear(secxr).shift(UP * 1.15)
        et_x1 = tag_junto(secx1, "x1", LEFT, buff=0.18, font_size=19,
                          color=C_SENAL)
        et_xr = tag_junto(secxr, "retardada", LEFT, buff=0.18,
                          font_size=19, color=C_SENAL)

        self.play(FadeIn(secx1.ejes), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(secx1.tallo(i)) for i in
                                range(len(X1))], lag_ratio=0.06),
                  LaggedStart(*[FadeIn(secx1.punto(i)) for i in
                                range(len(X1))], lag_ratio=0.06),
                  FadeIn(et_x1), run_time=1.1)
        self.wait(1.0)
        self.play(FadeIn(secxr.ejes), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(secxr.tallo(i)) for i in
                                range(len(X_RETARDADA))], lag_ratio=0.05),
                  LaggedStart(*[FadeIn(secxr.punto(i)) for i in
                                range(len(X_RETARDADA))], lag_ratio=0.05),
                  FadeIn(et_xr), run_time=1.3)
        self.wait(2.2)

        grupo_x = VGroup(secx1, secxr, et_x1, et_xr)
        self.play(FadeOut(grupo_x), run_time=0.8)

        secy1 = Secuencia(Y1, 0, ancho=w * len(Y1), alto=1.3,
                          color=C_SALIDA)
        alinear(secy1).shift(UP * 0.55)
        secyr = Secuencia(Y_RETARDADA, 0, ancho=w * len(Y_RETARDADA),
                          alto=1.3, color=C_SALIDA)
        alinear(secyr).shift(DOWN * 1.55)
        et_y1 = tag_junto(secy1, "y1", LEFT, buff=0.18, font_size=19,
                          color=C_SALIDA)
        et_yr = tag_junto(secyr, "retardada", LEFT, buff=0.18,
                          font_size=19, color=C_SALIDA)

        self.play(FadeIn(secy1.ejes), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(secy1.tallo(i)) for i in
                                range(len(Y1))], lag_ratio=0.045),
                  LaggedStart(*[FadeIn(secy1.punto(i)) for i in
                                range(len(Y1))], lag_ratio=0.045),
                  FadeIn(et_y1), run_time=1.5)
        self.wait(1.4)
        self.play(FadeIn(secyr.ejes), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(secyr.tallo(i)) for i in
                                range(len(Y_RETARDADA))], lag_ratio=0.04),
                  LaggedStart(*[FadeIn(secyr.punto(i)) for i in
                                range(len(Y_RETARDADA))], lag_ratio=0.04),
                  FadeIn(et_yr), run_time=1.7)
        self.wait(2.4)

        i1 = int(np.argmax(np.abs(Y1)))
        i2 = int(np.argmax(np.abs(Y_RETARDADA)))
        m1 = secy1.marcar(i1, color=C_CALCULO)
        m2 = secyr.marcar(i2, color=C_CALCULO)
        self.play(Create(m1), run_time=0.7)
        self.wait(0.7)
        self.play(Create(m2), run_time=0.7)
        self.wait(0.7)
        flecha = Arrow(m1.get_center(), m2.get_center(), color=C_CALCULO,
                       buff=0.18, stroke_width=2.6)
        self.play(Create(flecha), run_time=1.0)
        self.wait(1.0)
        panel = panel_cifras(f"y1 pico n = {i1}",
                             f"retardada pico n = {i2}")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"desplazamiento = {fmt(DESPLAZAMIENTO, 0)}"),
                    zona="abajo", run_time=0.5)
        self.wait(5.6)
