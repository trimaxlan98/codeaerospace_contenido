class Clip2(Scene):
    """3.2.2 - La desigualdad que acota a toda politica desplegable ya estaba
    publicada: es el ultimo eslabon de la jerarquia de Oliehoek, Spaan y
    Vlassis (2008). La tesis la cita; lo propio es el USO. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("La envolvente ya existia"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # la escalera de cotas: cada peldano ve un poco mas
        pelda = [(r"Q^{*}", "descentralizado", C_ADAPTA), (r"Q_{BG}", "retardo de 1 paso", C_ENLACE),
                 (r"Q_{POMDP}", "observacion conjunta", C_OK), (r"Q_{MDP}", "estado completo", C_PRIV)]
        g = VGroup()
        for i, (s, d, col) in enumerate(pelda):
            y = -1.8 + i * 1.15
            barra = Rectangle(width=2.0 + 1.1 * i, height=0.62, stroke_color=col, stroke_width=3,
                              fill_color=col, fill_opacity=0.15).move_to([-2.4 + 0.55 * i, y, 0])
            m = MathTex(s, color=col, font_size=40).move_to(barra)
            e = tag_hud(d, font_size=17, color=col).next_to(barra, RIGHT, buff=0.3)
            g.add(VGroup(barra, m, e))
        for k, p in enumerate(g):
            self.play(FadeIn(p, shift=UP * 0.2), run_time=0.8)
            if k < len(g) - 1:
                le = MathTex(r"\le", color=CODE_INK, font_size=40).move_to(
                    (g[k][0].get_top() + np.array([0, 0.27, 0])))
                self.play(FadeIn(le), run_time=0.3)
            self.wait(1.4)
        rot.mostrar(dato_pie("Oliehoek, Spaan, Vlassis 2008"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie("JAIR 32, Teorema 5.1"), zona="abajo", run_time=0.5)
        self.wait(3.2)
        # la tesis: la desigualdad es importada; el piso de falsabilidad, propio
        marco = SurroundingRectangle(VGroup(g[0], g[3]), color=CODE_INK, buff=0.25)
        self.play(Create(marco), run_time=0.8)
        rot.mostrar(formula_pie(r"J(\pi) \le V^{\star}_{\mathrm{priv}} \;\; \forall\, \pi \in \Pi_{\mathrm{dec}}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
        rot.mostrar(dato_pie("lo propio es el uso"), zona="abajo", run_time=0.5)
        self.wait(3.6)
