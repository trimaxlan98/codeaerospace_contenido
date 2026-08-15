class Clip1(Scene):
    """1 - Una regla de 633 nanometros. Un laser HeNe emite una onda
    ambar que avanza; una llave marca un periodo (632.8 nm) y se rotula
    la frecuencia f = c/lambda = 473.8 THz. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Una regla de 633 nanómetros"),
                    zona="arriba", run_time=0.6)

        onda = onda_regla(n_periodos=6, ancho=9.0, amplitud=0.85,
                          fase=0.0, color=C_ONDA, etiqueta="lambda",
                          con_llave=True)
        laser = Dot(onda.eje.get_left() + LEFT * 0.45, radius=0.13,
                   color=C_HAZ)
        halo = Dot(laser.get_center(), radius=0.26, color=C_HAZ)
        halo.set_fill(C_HAZ, opacity=0.25)
        halo.set_stroke(width=0)

        # --- momento 1: la onda nace y avanza --------------------------------
        rot.mostrar(pie_curso("Un láser de helio-neón emite una onda: "
                              "632.8 nanómetros de cresta a cresta."),
                    zona="abajo")
        self.play(FadeIn(halo), FadeIn(laser), run_time=0.5)
        self.play(Create(onda.eje), run_time=0.4)
        self.play(Create(onda.curva), run_time=1.3)
        fase_t = ValueTracker(0.0)
        avance = lambda o: o.a_fase(fase_t.get_value())
        onda.add_updater(avance)
        self.play(fase_t.animate.set_value(4 * math.pi), run_time=2.0,
                  rate_func=linear)
        onda.remove_updater(avance)
        self.wait(3.5)

        # --- momento 2: la llave de una lambda --------------------------------
        rot.mostrar(pie_curso("Cada cresta es una marca. La luz trae su "
                              "propia regla."), zona="abajo")
        brace = onda.llave_lambda[0]
        lam_tag = tag_hud(f"lambda = {LAMBDA_HENE * 1e9:.1f} nm",
                          font_size=17)
        lam_tag.next_to(brace, DOWN, buff=0.12)
        self.play(FadeIn(brace, shift=0.10 * UP), run_time=0.5)
        self.play(FadeIn(lam_tag), run_time=0.4)
        self.wait(6.0)

        # --- momento 3: la frecuencia ------------------------------------------
        rot.mostrar(pie_curso("Y las marcas pasan a un ritmo fijo: la "
                              "frecuencia."), zona="abajo")
        f_formula = MathTex(r"f = c/\lambda", font_size=32, color=C_ACENTO)
        f_tag = tag_hud(f"f = {F_HENE_THZ:.1f} THz", font_size=17)
        f_grupo = VGroup(f_formula, f_tag).arrange(DOWN, buff=0.16)
        f_grupo.move_to(RIGHT * 3.1 + DOWN * 1.35)
        self.play(FadeIn(f_grupo, shift=0.10 * UP), run_time=0.6)
        self.wait(6.0)

        # --- cierre ---------------------------------------------------------------
        rot.mostrar(pie_curso("Medir con luz es contar marcas de 633 "
                              "nanómetros."), zona="abajo")
        self.wait(6.0)
