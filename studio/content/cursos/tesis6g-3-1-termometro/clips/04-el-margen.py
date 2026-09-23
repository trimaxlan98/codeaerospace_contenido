class Clip4(Scene):
    """3.1.4 - La definicion que sostiene la tesis: el Margen Adaptativo es
    lo que paga quien ve todo y elige en cada instante, frente a la mejor
    opcion fija, en unidades de esa mejor opcion fija. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El margen adaptativo"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        c = Cuadro((-6.2, 1.6, -2.3, 2.3), (0, 1), (0.3, 1.25))
        opciones = VGroup(*[c.serie(CM["t"], CM["R"][i], C_TENUE, 2.5) for i in range(3)])
        self.play(Create(c.suelo()), run_time=0.4)
        self.play(*[Create(o) for o in opciones], run_time=2.2, rate_func=linear)
        rot.mostrar(dato_pie("tres opciones que cambian"), zona="abajo", run_time=0.5)
        self.wait(2.2)
        est = c.serie(CM["t"], CM["estatica"], C_ESTATICA, 6)
        e_est = tag_hud("mejor estatica", font_size=18, color=C_ESTATICA).next_to(c.p(1, CM["estatica"][-1]), RIGHT, buff=0.2)
        self.play(opciones.animate.set_stroke(opacity=0.4), Create(est), run_time=2.0)
        self.play(FadeIn(e_est), run_time=0.4)
        self.wait(2.0)
        env = c.serie(CM["t"], CM["envolvente"], C_PRIV, 6)
        e_env = tag_hud("oraculo", font_size=18, color=C_PRIV).next_to(e_est, UP, buff=0.2).align_to(e_est, LEFT)
        self.play(Create(env), run_time=2.4, rate_func=linear)
        self.play(FadeIn(e_env), run_time=0.4)
        self.wait(1.6)
        arriba = [c.p(t, v) for t, v in zip(CM["t"], CM["envolvente"])]
        abajo = [c.p(t, v) for t, v in zip(CM["t"], CM["estatica"])][::-1]
        hueco = Polygon(*arriba, *abajo, stroke_width=0, fill_color=C_PRIV, fill_opacity=0.28)
        hueco.set_z_index(-1)
        self.play(FadeIn(hueco), run_time=1.0)
        rot.mostrar(formula_pie(r"\mathrm{MA} = \frac{V^{\star}_{\mathrm{priv}} - V^{\star}_{\mathrm{est}}}{V^{\star}_{\mathrm{est}}}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(cifra_pie(f"MA de este dibujo = {fmt(CM['MA'], 3)}"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        cierre_leccion(self, rot, "Primero medir el termometro.",
                       "Despues comparar algoritmos.",
                       opciones, est, env, hueco, e_est, e_env, c.suelo())
