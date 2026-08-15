class Clip1(Scene):
    """1.3.1 - La fuerza de Lorentz no empuja: desvia. Siempre
    perpendicular a la velocidad, no puede dar ni quitar energia; solo
    curva el camino en el circulo de Larmor. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La fuerza que no empuja: desvía")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el campo que sale del papel -------------------------
        gir = giro_larmor()
        gir.move_to(DOWN * 0.3 + LEFT * 1.1)
        rot.mostrar(pie_curso("Cada punto verde es campo magnético "
                              "saliendo de la pantalla, hacia ti."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(gir.fondo, lag_ratio=0.02), run_time=1.0)
        self.wait(4.4)

        # --- momento: entra el electron y aparece el circulo --------------
        rot.mostrar(formula_pie(r"\vec F = q\,\vec v \times \vec B"),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(gir.particula, scale=1.5), run_time=0.6)
        self.play(Create(gir.trayectoria), run_time=1.4)
        self.wait(2.8)

        rot.mostrar(pie_curso("Un electrón que cruza ese campo no frena "
                              "ni acelera: se tuerce en un círculo."),
                    zona="abajo", run_time=0.5)
        self.play(MoveAlongPath(gir.particula, gir.trayectoria),
                  run_time=3.2, rate_func=linear)
        self.wait(1.4)

        # --- momento: v tangente, F siempre al centro ---------------------
        rot.mostrar(pie_curso("La velocidad va tangente; la fuerza, "
                              "SIEMPRE al centro, perpendicular a v."),
                    zona="abajo", run_time=0.5)
        # 90/180/270: la particula descansa en 0 grados, asi ninguna
        # flecha le cae encima.
        flechas = VGroup()
        for ang in (90, 180, 270):
            flechas.add(gir.flecha_v(ang), gir.flecha_f(ang))
        et_v = MathTex(r"\vec v", font_size=30, color=C_CARGA)
        et_v.next_to(gir.flecha_v(90).get_end(), UP, buff=0.12)
        et_f = MathTex(r"\vec F", font_size=30, color=C_CALCULO)
        et_f.next_to(gir.flecha_f(90), LEFT, buff=0.14)
        self.play(LaggedStart(*[GrowArrow(f) for f in flechas],
                              lag_ratio=0.15), run_time=1.6)
        self.play(FadeIn(et_v), FadeIn(et_f), run_time=0.4)
        self.wait(4.2)

        rot.mostrar(pie_curso("Perpendicular no trabaja: no puede dar ni "
                              "quitar energía. Solo desvía."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: las cifras del giro ---------------------------------
        rot.mostrar(pie_curso("Con números de la Tierra, esa fuerza "
                              "diminuta cierra el círculo en un metro."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(
            tag_hud(f"v = {V_ELECTRON / 1e3:.0f} km/s", color=C_CARGA),
            tag_hud(f"B = {B_SUPERFICIE * 1e6:.0f} uT", color=C_B),
            tag_hud(f"radio = {gir.numeros['radio_m']:.2f} m"),
            tag_hud(f"giro a {gir.numeros['frecuencia_hz'] / 1e6:.1f} MHz"))
        cifras.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        cifras.move_to(RIGHT * 4.55 + DOWN * 0.3)
        self.play(LaggedStart(*[FadeIn(c, shift=0.15 * RIGHT)
                                for c in cifras], lag_ratio=0.25),
                  run_time=1.2)
        self.wait(4.4)

        rot.mostrar(pie_curso("Ese giro es una correa: la partícula "
                              "queda atada a su línea de campo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
