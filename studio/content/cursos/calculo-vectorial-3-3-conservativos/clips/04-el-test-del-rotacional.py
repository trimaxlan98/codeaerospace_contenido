class Clip4(Scene):
    """3.3.4 - El test rapido: rot(grad phi) = 0 medido en tres puntos,
    frente al 2.00 del rotor; y la gravedad, cuya orbita no cobra peaje.
    Cierre de la leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El test del rotacional")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: hace falta un test rapido ---------------------------
        pl = plano_leccion(centro=UP * 0.1)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Probar todos los caminos es imposible. "
                              "Hace falta un test local."),
                    zona="abajo", run_time=0.5)
        campo = campo_flechas(pl, CAMPO, paso=1.0, escala=0.7,
                              x0=-3.5, x1=3.5, y0=-2.5, y1=2.5,
                              magnitud_max=MAG_REF, opacidad=0.75)
        self.play(FadeIn(campo), run_time=1.2)
        self.wait(3.0)

        # --- momento: la ruedecita no gira en ningun punto ----------------
        rot.mostrar(pie_curso("Soltemos la ruedecita en tres puntos del "
                              "campo gradiente: no gira en ninguno."),
                    zona="abajo", run_time=0.5)
        ruedas = VGroup()
        marcas = VGroup()
        for i, p in enumerate(P_TEST):
            rd = rueda(pl, p, radio=0.40)
            tg = tag_hud(f"rot = {fmt(ROT_GRAD[i], 2)}", font_size=17,
                         color=C_RES)
            tg.next_to(rd, UP, buff=0.12)
            ruedas.add(rd)
            marcas.add(_con_fondo(tg, buff=0.08, opacidad=0.85))
        self.play(LaggedStart(*[FadeIn(r, scale=0.5) for r in ruedas],
                              lag_ratio=0.35), run_time=1.5)
        self.play(LaggedStart(*[FadeIn(m) for m in marcas], lag_ratio=0.3),
                  run_time=0.8)
        self.play(*[Rotate(r.aspas, angle=ROT_GRAD[i] / 2 * 2.2,
                           about_point=r.centro())
                    for i, r in enumerate(ruedas)], run_time=2.2)
        self.wait(0.4)

        # --- momento: en el rotor, la misma ruedecita no para -------------
        rot.mostrar(pie_curso("En un campo que gira, la misma ruedecita "
                              "no para."), zona="abajo", run_time=0.5)
        self.play(FadeOut(campo), FadeOut(ruedas), FadeOut(marcas),
                  run_time=0.7)
        giro = campo_flechas(pl, campo_rotor, paso=1.0, escala=0.7,
                             x0=-3.5, x1=3.5, y0=-2.5, y1=2.5,
                             magnitud_max=3.5, opacidad=0.85)
        rd = rueda(pl, P_ROTOR, radio=0.52)
        tg = tag_hud(f"rot = {fmt(ROT_ROTOR, 2)}", font_size=19, color=C_RES)
        tg.next_to(rd, UP, buff=0.16)
        tg = _con_fondo(tg, buff=0.08, opacidad=0.85)
        self.play(FadeIn(giro), run_time=1.0)
        self.play(FadeIn(rd, scale=0.5), FadeIn(tg), run_time=0.7)
        self.play(Rotate(rd.aspas, angle=ROT_ROTOR / 2 * 3.0,
                         about_point=rd.centro()), run_time=3.0,
                  rate_func=linear)
        self.wait(0.4)

        # --- momento: el test, en formula ---------------------------------
        rot.mostrar(formula_pie(r"\nabla \times (\nabla \varphi) = 0"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: la gravedad tambien es un gradiente ------------------
        rot.mostrar(pie_curso("La gravedad pasa el test: también es el "
                              "gradiente de un potencial."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(giro), FadeOut(rd), FadeOut(tg), run_time=0.7)
        peso = campo_flechas(pl, campo_gravedad, paso=1.0, escala=0.7,
                             x0=-2.5, x1=2.5, y0=-2.5, y1=2.5,
                             magnitud_max=1.5, opacidad=0.9)
        planeta = Dot(pl.p((0.0, 0.0)), radius=0.13, color=C_GRAD)
        orbita = camino(pl, ORBITA, color=C_VEC, grosor=3.2, n=320,
                        flechas=3)
        self.play(FadeIn(peso), FadeIn(planeta, scale=0.5), run_time=1.0)
        self.play(Create(orbita.trazo), FadeIn(orbita.marcas), run_time=0.7)
        self.wait(2.2)

        # --- momento: la orbita no cobra peaje ----------------------------
        rot.mostrar(pie_curso("Una órbita entera alrededor del planeta: el "
                              "contador no se mueve."), zona="abajo",
                    run_time=0.5)
        marcador = tag_hud("orbita W =", font_size=20)
        contador = DecimalNumber(0.0, num_decimal_places=2, color=C_CALCULO,
                                 font_size=34)
        medidor = VGroup(marcador, contador).arrange(RIGHT, buff=0.18)
        medidor.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        t = ValueTracker(0.0)
        contador.add_updater(lambda d: d.set_value(
            float(np.interp(t.get_value(), TS_ORB, S_ORB))))
        contador.add_updater(lambda d: d.next_to(marcador, RIGHT, buff=0.18))
        satelite = Dot(pl.p(ORBITA(0.0)), radius=0.10, color=C_VEC)
        satelite.add_updater(lambda d: d.move_to(pl.p(ORBITA(
            t.get_value()))))
        self.play(FadeIn(medidor), FadeIn(satelite, scale=0.5), run_time=0.5)
        self.play(t.animate.set_value(1.0), run_time=3.2, rate_func=linear)
        contador.clear_updaters()
        satelite.clear_updaters()
        c1 = MathTex(r"\oint \vec F \cdot d\vec r = " + fmt(W_ORBITA, 2),
                     font_size=30, color=C_RES)
        c1.to_corner(UR, buff=0.6).shift(DOWN * 1.5)
        c2 = MathTex(r"\max\,|\nabla \varphi - \vec F| = "
                     + fmt(ERR_POT_GRAV, 2), font_size=26, color=C_RES)
        c2.to_corner(UR, buff=0.6).shift(DOWN * 2.4)
        cuentas = VGroup(_con_fondo(c1, buff=0.10, opacidad=0.85),
                         _con_fondo(c2, buff=0.10, opacidad=0.85))
        self.play(FadeIn(cuentas[0], shift=0.12 * LEFT), run_time=0.45)
        self.play(FadeIn(cuentas[1], shift=0.12 * LEFT), run_time=0.45)
        self.wait(1.0)

        # --- cierre -------------------------------------------------------
        cierre_leccion(self, rot,
                       "Si el campo es un gradiente, el camino da igual.",
                       "Solo cuentan los extremos.",
                       "Siguiente lección: el teorema de Green.",
                       pl, peso, planeta, orbita, satelite, medidor, cuentas,
                       espera=3.8)
