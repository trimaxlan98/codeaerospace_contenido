class Clip1(Scene):
    """7.1.1 - Q15: 16 bits con signo para el rango [-1, 1). El 1.0 no
    existe, y el paso es lo mas fino que se puede decir. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("El formato"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la recta de los numeros que SI existen -----------------------
        recta = Line(LEFT * 5.4, RIGHT * 5.4, color=C_EJE, stroke_width=2.0)
        recta.move_to(UP * 0.55)
        et_min = tag_hud("-1.0", font_size=19, color=C_TENUE)
        et_min.next_to(recta.get_start(), DOWN, buff=0.24)
        et_cero = tag_hud("0", font_size=19, color=C_TENUE)
        et_cero.next_to(recta.get_center(), DOWN, buff=0.24)
        et_max = tag_hud(f"{fmt(MAYOR, 5)}", font_size=19, color=C_CALCULO)
        et_max.next_to(recta.get_end(), DOWN, buff=0.24)
        self.play(Create(recta), FadeIn(et_min), FadeIn(et_cero), run_time=1.0)
        self.wait(1.0)

        # --- el tope: 1.0 NO esta -----------------------------------------
        tope = Line(recta.get_end() + UP * 0.2, recta.get_end() + DOWN * 0.2,
                    color=C_CALCULO, stroke_width=3.0)
        uno = Line(recta.get_end() + RIGHT * 0.34 + UP * 0.2,
                   recta.get_end() + RIGHT * 0.34 + DOWN * 0.2,
                   color=C_RUIDO, stroke_width=3.0)
        et_uno = tag_hud("1.0", font_size=19, color=C_RUIDO)
        et_uno.next_to(uno, UP, buff=0.16)
        self.play(Create(tope), FadeIn(et_max), run_time=0.7)
        self.wait(1.4)
        self.play(Create(uno), FadeIn(et_uno), run_time=0.7)
        cruz = VGroup(
            Line(uno.get_center() + np.array([-0.16, -0.16, 0]),
                 uno.get_center() + np.array([0.16, 0.16, 0]),
                 color=C_RUIDO, stroke_width=3.0),
            Line(uno.get_center() + np.array([-0.16, 0.16, 0]),
                 uno.get_center() + np.array([0.16, -0.16, 0]),
                 color=C_RUIDO, stroke_width=3.0))
        self.play(Create(cruz), run_time=0.6)
        rot.mostrar(cifra_pie(f"el tope es {fmt(MAYOR, 5)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        # --- el paso: los escalones que hay entre medias ------------------
        marcas = VGroup(*[Line(recta.point_from_proportion(p) + UP * 0.10,
                               recta.point_from_proportion(p) + DOWN * 0.10,
                               color=C_MUESTRA, stroke_width=1.4)
                          for p in np.linspace(0.02, 0.98, 33)])
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.02),
                  run_time=1.6)
        rot.mostrar(cifra_pie(f"{NIVELES} niveles"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras(f"bits = {BITS_Q}",
                             f"niveles = {NIVELES}",
                             (f"paso = {PASO_Q:.3e}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)

        # --- lo que eso vale sobre la señal -------------------------------
        rot.mostrar(cifra_pie(f"error max = {ERR_MAX:.2e}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"x_{Q} = \frac{\mathrm{round}(x \cdot 2^{15})}"
                                r"{2^{15}}"), zona="abajo", run_time=0.5)
        self.wait(6.4)
