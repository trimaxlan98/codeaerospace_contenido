class Clip3(Scene):
    """2.1.3 - Sin explorar no se aprende: con eps = 0 la tabla se queda con
    la primera accion que probo. La tesis explora con eps que decae 0.999
    por episodio hasta un piso de 0.05. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Explorar para aprender"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # dos agentes: el que explora y el que no, sobre el estado visible
        c = Cuadro((-5.6, -0.6, -1.9, 2.2), (0, 600), (0, 90))
        self.play(Create(c.suelo()), run_time=0.4)
        k = np.arange(len(QJ["Q"]))
        cols = [C_ENLACE, C_PRIV, C_OK]
        con = VGroup(*[c.serie(k, QJ["Q"][:, 0, a], cols[a], 3) for a in range(3)])
        sin = VGroup(*[c.serie(k, QJ0["Q"][:, 0, a], cols[a], 3) for a in range(3)])
        et = VGroup(*[tag_hud(ACC[a], font_size=17, color=cols[a]) for a in range(3)])
        et.arrange(RIGHT, buff=0.4).next_to(c.p(0, 90), UP, buff=0.1).align_to(c.p(0, 90), LEFT)
        e_sin = tag_hud("eps = 0", font_size=19, color=C_NO).next_to(c.p(600, 6), UP, buff=0.1).align_to(c.p(600, 6), RIGHT)
        self.play(FadeIn(et), FadeIn(e_sin), *[Create(m) for m in sin], run_time=2.4)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"sin explorar: solo {ACC[int(QJ0['Q'][-1][0].argmax())]}"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)
        e_con = tag_hud("eps = 0.2", font_size=19, color=C_OK).move_to(e_sin)
        self.play(FadeOut(sin), Transform(e_sin, e_con), *[Create(m) for m in con], run_time=2.4)
        self.wait(1.4)

        # el programa de exploracion de la tesis
        n = CURVA["episodios"]
        ce = Cuadro((0.6, 6.2, -1.9, 2.2), (0, n), (0, 1))
        ep = np.arange(n + 1)
        eps = np.maximum(CURVA["eps_decay"] ** ep, CURVA["eps_min"])
        self.play(Create(ce.suelo()), run_time=0.4)
        te = tag_hud("eps de QMIX", font_size=17, color=C_ADAPTA).next_to(ce.p(0, 1), UP, buff=0.1)
        te.align_to(ce.p(0, 1), LEFT)
        self.play(FadeIn(te), Create(ce.serie(ep[::10], eps[::10], C_ADAPTA, 4)), run_time=2.2)
        piso = ce.raya(CURVA["eps_min"], C_TENUE)
        self.play(Create(piso), run_time=0.5)
        rot.mostrar(dato_pie(f"eps x {CURVA['eps_decay']} por episodio"), zona="abajo", run_time=0.5)
        self.wait(3.2)
        rot.mostrar(cifra_pie(f"piso {CURVA['eps_min']} en {EPS_K} episodios"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
        self.wait(2.6)
