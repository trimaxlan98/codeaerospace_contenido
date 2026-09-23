class Clip1(Scene):
    """2.3.1 - Para decidir aunque f replicas mientan hacen falta n >= 3f+1:
    dos quorums cualesquiera comparten al menos una replica honesta. Y dos
    replicas de mas no compran nada: n = 6 tolera lo mismo que n = 4.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Tres f mas uno"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        def anillo(n, c, r=1.5, traidores=()):
            g = VGroup()
            for i in range(n):
                a = PI / 2 - 2 * PI * i / n
                col = C_NO if i in traidores else CODE_INK
                g.add(Dot(c + r * np.array([np.cos(a), np.sin(a), 0]), radius=0.2, color=col))
            return g

        c4 = np.array([-3.2, -0.1, 0])
        r4 = anillo(4, c4, traidores=(3,))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in r4], lag_ratio=0.15), run_time=1.0)
        e4 = tag_hud(f"n = {Q4['n']}  f = {Q4['f']}", font_size=20, color=CODE_INK)
        e4.next_to(r4, DOWN, buff=0.45)
        self.play(FadeIn(e4), run_time=0.4)
        self.wait(1.8)
        # dos quorums de 3: se tocan en al menos f+1 = 2 replicas
        qa = SurroundingRectangle(VGroup(r4[0], r4[1], r4[2]), buff=0.18, color=C_ENLACE,
                                  corner_radius=0.3)
        qb = SurroundingRectangle(VGroup(r4[1], r4[2], r4[3]), buff=0.3, color=C_ADAPTA,
                                  corner_radius=0.3)
        self.play(Create(qa), run_time=0.7)
        self.play(Create(qb), run_time=0.7)
        self.play(Indicate(r4[1], color=C_OK), Indicate(r4[2], color=C_OK), run_time=1.2)
        rot.mostrar(cifra_pie(f"quorum = {Q4['quorum']} de {Q4['n']}"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(formula_pie(r"n \ge 3f + 1"), zona="abajo", run_time=0.5)
        self.wait(3.2)

        # n = 6: dos replicas de mas, el mismo f
        c6 = np.array([3.2, -0.1, 0])
        r6 = anillo(6, c6, traidores=(5,))
        self.play(LaggedStart(*[GrowFromCenter(d) for d in r6], lag_ratio=0.1), run_time=1.0)
        e6 = tag_hud(f"n = {Q6['n']}  f = {Q6['f']}", font_size=20, color=CODE_INK)
        e6.next_to(r6, DOWN, buff=0.45)
        self.play(FadeIn(e6), run_time=0.4)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"n = {Q6['n']}: tolera f = {Q6['f']}"), zona="abajo", run_time=0.5)
        self.wait(3.4)
        rot.mostrar(cifra_pie(f"quorum {Q6['quorum']}, no {Q6['quorum_2f1']}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        rot.mostrar(cifra_pie(f"n = {Q7['n']}: f = {Q7['f']}"), zona="abajo", run_time=0.5)
        self.wait(3.2)
