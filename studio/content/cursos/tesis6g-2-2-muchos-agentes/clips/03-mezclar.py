class Clip3(Scene):
    """2.2.3 - Tres maneras de mezclar dos Q individuales en Q_tot: la suma
    (VDN), una monotona no lineal (la idea de QMIX) y una no monotona. Solo
    las monotonas garantizan que el maximo de cada uno sea el maximo del
    equipo. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Mezclar sin romper"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # cortes a Q2 fija: Q_tot contra Q1. Monotona = TODAS las curvas suben.
        q = np.linspace(-1, 1, 80)
        cortes = [(-0.8, C_ENLACE), (0.0, C_PRIV), (0.8, C_ADAPTA)]
        tipos = [("vdn", "VDN: suma"), ("qmix", "monotona"), ("roto", "no monotona")]
        xs = [-4.4, 0.0, 4.4]
        rango = {}
        for t, _ in tipos:
            vals = np.concatenate([T6.mezcla(q, np.full_like(q, c), t) for c, _ in cortes])
            rango[t] = (vals.min() - 0.1, vals.max() + 0.1)
        grupo = VGroup()
        for (t, nombre), x in zip(tipos, xs):
            cu = Cuadro((x - 1.7, x + 1.7, -1.3, 1.6), (-1, 1), rango[t])
            base = cu.suelo()
            ejey = Line(cu.p(-1, rango[t][0]), cu.p(-1, rango[t][1]), stroke_color=C_TENUE, stroke_width=2)
            curvas = VGroup(*[cu.serie(q, T6.mezcla(q, np.full_like(q, c), t), col, 4, esquinas=False)
                              for c, col in cortes])
            e = tag_hud(nombre, font_size=18, color=CODE_INK).next_to(cu.p(0, rango[t][1]), UP, buff=0.2)
            ex = MathTex(r"Q_1", color=C_TENUE, font_size=30).next_to(cu.p(1, rango[t][0]), DOWN, buff=0.1)
            ey = MathTex(r"Q_{\mathrm{tot}}", color=C_TENUE, font_size=28).next_to(cu.p(-1, rango[t][1]), LEFT, buff=0.1)
            g = VGroup(base, ejey, curvas, e, ex, ey)
            grupo.add(g)
            self.play(Create(base), Create(ejey), FadeIn(e), FadeIn(ex), FadeIn(ey), run_time=0.6)
            self.play(LaggedStart(*[Create(c) for c in curvas], lag_ratio=0.3), run_time=1.6)
            self.wait(1.8)
        ley = VGroup(*[MathTex(rf"Q_2 = {c:+.1f}", color=col, font_size=28) for c, col in cortes])
        ley.arrange(RIGHT, buff=0.6).move_to([0, 2.45, 0])
        self.play(FadeIn(ley), run_time=0.5)
        rot.mostrar(dato_pie("cortes a Q2 fija"), zona="abajo", run_time=0.5)
        self.wait(3.6)

        # la prueba: 500 casos al azar, ¿el maximo de cada uno da el conjunto?
        veredictos = VGroup()
        for (t, _), x in zip(tipos, xs):
            f = IGM_FALLOS[t]
            col = C_OK if f == 0 else C_NO
            v = tag_hud(f"IGM falla {f}/500", font_size=18, color=col).move_to([x, -1.95, 0])
            veredictos.add(v)
        self.play(LaggedStart(*[FadeIn(v, shift=UP * 0.1) for v in veredictos], lag_ratio=0.4),
                  run_time=1.6)
        tacha = Cross(grupo[2][2], stroke_color=C_NO, stroke_width=6)
        self.play(Create(tacha), run_time=0.6)
        rot.mostrar(formula_pie(r"\arg\max_a Q_{\mathrm{tot}} = (\arg\max Q_1,\ \arg\max Q_2)"),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)
        self.wait(1.6)
        self.wait(1.4)
