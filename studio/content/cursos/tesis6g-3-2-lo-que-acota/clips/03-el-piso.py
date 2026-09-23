class Clip3(Scene):
    """3.2.3 - El piso de falsabilidad, la aportacion propia de la tesis
    (Teorema 4.7.1): si el entorno no premia adaptarse (MA = 0), ninguna
    politica adaptativa le gana a la estatica, y comparar algoritmos ahi no
    informa nada. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El piso de falsabilidad"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = Cuadro((-6.2, 1.6, -2.3, 2.3), (0, 1), (0.3, 1.25))
        ops = VGroup(*[c.serie(PLANO["t"], PLANO["R"][i], C_TENUE, 2.5) for i in range(3)])
        self.play(Create(c.suelo()), run_time=0.4)
        self.play(*[Create(o) for o in ops], run_time=2.0, rate_func=linear)
        est = c.serie(PLANO["t"], PLANO["estatica"], C_ESTATICA, 6)
        e_est = tag_hud("mejor estatica", font_size=18, color=C_ESTATICA).next_to(c.p(1, PLANO["estatica"][-1]), RIGHT, buff=0.2)
        self.play(ops.animate.set_stroke(opacity=0.4), Create(est), FadeIn(e_est), run_time=1.6)
        rot.mostrar(dato_pie("una opcion domina siempre"), zona="abajo", run_time=0.5)
        self.wait(3.0)
        env = DashedVMobject(c.serie(PLANO["t"], PLANO["envolvente"], C_PRIV, 6), num_dashes=60)
        e_env = tag_hud("oraculo", font_size=18, color=C_PRIV).next_to(e_est, UP, buff=0.2).align_to(e_est, LEFT)
        self.play(Create(env), FadeIn(e_env), run_time=2.0, rate_func=linear)
        rot.mostrar(cifra_pie(f"MA = {fmt(PLANO['MA'], 3)}"), zona="abajo", run_time=0.5)
        self.wait(3.2)
        ad = c.serie(PLANO["t"], ADAPT, C_ADAPTA, 5)
        e_ad = tag_hud("adaptativa", font_size=18, color=C_ADAPTA).next_to(e_est, DOWN, buff=0.2).align_to(e_est, LEFT)
        self.play(Create(ad), FadeIn(e_ad), run_time=2.4, rate_func=linear)
        rot.mostrar(cifra_pie(f"adaptativa: {fmt(100 * (ADAPT.mean() / PLANO['V_est'] - 1), 1)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(formula_pie(r"\mathrm{MA} = 0 \;\Rightarrow\; J(\pi) \le V^{\star}_{\mathrm{est}}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(dato_pie("Teorema 4.7.1 de la tesis"), zona="abajo", run_time=0.5)
        self.wait(3.4)
