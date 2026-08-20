class Clip3(Scene):
    """3.3.3 - El paisaje que hay detras del campo: el potencial. El
    trabajo de A a B es la diferencia de nivel, 4.00 - 0.00. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El potencial")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el paisaje escondido --------------------------------
        pl = plano_leccion(unidad=0.82, centro=UP * 0.1)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Detrás de este campo hay un paisaje: su "
                              "potencial."), zona="abajo", run_time=0.5)
        mapa = curvas_nivel(pl, POT, niveles=NIVELES_PHI, x0=X0_MAPA,
                            x1=X1_MAPA, y0=Y0_MAPA, y1=Y1_MAPA, n=110)
        panel = panel_derecha(MathTex(r"\varphi(x,\, y) = x^{2} y",
                                      font_size=34, color=C_TITULO))
        self.play(LaggedStart(*[Create(c) for c in mapa.curvas],
                              lag_ratio=0.22), run_time=2.4)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(2.4)

        # --- momento: el campo es perpendicular a los niveles -------------
        rot.mostrar(pie_curso("El campo es el gradiente de ese paisaje: "
                              "cruza cada nivel en perpendicular."),
                    zona="abajo", run_time=0.5)
        campo = campo_flechas(pl, CAMPO, paso=1.0, escala=0.7,
                              x0=-2.5, x1=2.5, y0=-2.5, y1=2.5,
                              magnitud_max=MAG_REF, opacidad=0.9)
        self.play(LaggedStart(*[FadeIn(f, scale=0.6) for f in campo.flechas],
                              lag_ratio=0.03), run_time=1.4)
        self.wait(3.4)

        # --- momento: la altura del potencial en A y en B -----------------
        rot.mostrar(pie_curso("A está en el nivel cero; B, en el nivel "
                              "cuatro. Esa es toda la historia."),
                    zona="abajo", run_time=0.5)
        pa = Dot(pl.p(A_PT), radius=0.09, color=C_GRAD)
        pb = Dot(pl.p(B_PT), radius=0.09, color=C_GRAD)
        eta = MathTex(r"\varphi(A) = " + fmt(PHI_A, 2), font_size=28,
                      color=C_GRAD)
        eta.next_to(pa, DL, buff=0.16)
        eta = _con_fondo(eta, buff=0.10, opacidad=0.85)
        etb = MathTex(r"\varphi(B) = " + fmt(PHI_B, 2), font_size=28,
                      color=C_GRAD)
        etb.next_to(pb, UR, buff=0.16)
        etb = _con_fondo(etb, buff=0.10, opacidad=0.85)
        self.play(FadeIn(pa, scale=0.4), FadeIn(pb, scale=0.4), run_time=0.5)
        self.play(FadeIn(eta), FadeIn(etb), run_time=0.7)
        self.wait(3.4)

        # --- momento: subir de nivel con el altimetro del potencial -------
        rot.mostrar(pie_curso("Caminemos de A a B leyendo el potencial: "
                              "sube de cero a cuatro."),
                    zona="abajo", run_time=0.5)
        self.play(panel.animate.shift(DOWN * 3.3), run_time=0.6)
        marcador = MathTex(r"\varphi =", font_size=34, color=C_CALCULO)
        altura = DecimalNumber(PHI_A, num_decimal_places=2, color=C_CALCULO,
                               font_size=34)
        medidor = VGroup(marcador, altura).arrange(RIGHT, buff=0.18)
        medidor.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        t = ValueTracker(0.0)
        altura.add_updater(lambda d: d.set_value(
            float(POT(R_RECTA(t.get_value())))))
        altura.add_updater(lambda d: d.next_to(marcador, RIGHT, buff=0.18))
        viajero = Dot(pl.p(A_PT), radius=0.10, color=C_VEC)
        viajero.add_updater(lambda d: d.move_to(pl.p(R_RECTA(
            t.get_value()))))
        ruta = camino(pl, R_RECTA, color=C_VEC, grosor=3.4, n=200)
        self.play(FadeIn(medidor), run_time=0.5)
        self.play(Create(ruta.trazo), FadeIn(viajero, scale=0.5),
                  run_time=0.6)
        self.play(t.animate.set_value(1.0), run_time=4.0, rate_func=linear)
        altura.clear_updaters()
        viajero.clear_updaters()
        self.wait(1.0)

        # --- momento: el teorema fundamental ------------------------------
        rot.mostrar(formula_pie(r"\int_A^B \nabla\varphi \cdot d\vec r = "
                                r"\varphi(B) - \varphi(A)", font_size=32),
                    zona="abajo", run_time=0.5)
        f1 = MathTex(r"\int_A^B \vec F \cdot d\vec r = " + fmt(TRABAJOS[0], 2),
                     font_size=30, color=C_RES)
        f1.to_corner(UR, buff=0.6).shift(DOWN * 1.5)
        f2 = MathTex(r"\varphi(B) - \varphi(A) = " + fmt(DELTA_PHI, 2),
                     font_size=30, color=C_RES)
        f2.to_corner(UR, buff=0.6).shift(DOWN * 2.45)
        cuentas = VGroup(_con_fondo(f1, buff=0.10, opacidad=0.85),
                         _con_fondo(f2, buff=0.10, opacidad=0.85))
        self.play(FadeIn(cuentas[0], shift=0.12 * LEFT), run_time=0.45)
        self.play(FadeIn(cuentas[1], shift=0.12 * LEFT), run_time=0.45)
        self.wait(3.6)

        # --- momento: el trabajo es una resta de alturas ------------------
        rot.mostrar(pie_curso("El trabajo no es una suma de tramos: es una "
                              "resta de alturas."), zona="abajo",
                    run_time=0.5)
        self.play(FadeOut(viajero), run_time=0.4)
        self.play(Indicate(cuentas, color=C_RES, scale_factor=1.05),
                  run_time=0.9)
        self.wait(4.0)
