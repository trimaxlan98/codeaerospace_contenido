class Clip2(Scene):
    """1.4.2 - Sin verlo, se puede creer: un filtro de dos hipotesis sobre
    'mi canal esta degradado' alimentado por la interferencia propia. La
    creencia sigue al estado oculto con unos pasos de retraso. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Creer sin ver"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        n = len(CANAL)
        t = np.arange(n)
        ca = Cuadro((-5.0, 6.2, 1.55, 2.55), (0, n - 1), (0, 1))
        cb = Cuadro((-5.0, 6.2, 0.0, 0.9), (0, n - 1), (0, 1))
        cc = Cuadro((-5.0, 6.2, -2.4, -0.55), (0, n - 1), (0, 1))
        verdad = DashedVMobject(ca.serie(t, (CANAL == 0).astype(float), C_TENUE, 3), num_dashes=60)
        e_v = tag_hud("oculto", font_size=17, color=C_TENUE).next_to(ca.p(0, 0.5), LEFT, buff=0.15)
        self.play(Create(verdad), FadeIn(e_v), run_time=1.6)
        self.wait(1.4)

        # lo que se observa: senal ruidosa de "interferencia alta"
        puntos = VGroup(*[Dot(cb.p(k, Y_OBS[k]), radius=0.035, color=C_ADAPTA) for k in t])
        e_o = tag_hud("observado", font_size=17, color=C_ADAPTA).next_to(cb.p(0, 0.5), LEFT, buff=0.15)
        self.play(FadeIn(e_o), LaggedStart(*[FadeIn(p) for p in puntos], lag_ratio=0.004),
                  run_time=2.6)
        self.wait(1.6)
        rot.mostrar(dato_pie("el sensor se equivoca 15 %"), zona="abajo", run_time=0.5)
        self.wait(2.8)

        # la creencia
        self.play(Create(cc.suelo()), run_time=0.4)
        media = cc.raya(0.5, C_TENUE, dash=0.08, ancho=1.5)
        e_c = tag_hud("creencia", font_size=17, color=C_CALCULO).next_to(cc.p(0, 0.5), LEFT, buff=0.15)
        curva = cc.serie(t, CREENCIA, C_CALCULO, 4)
        self.play(Create(media), FadeIn(e_c), run_time=0.5)
        self.play(Create(curva), run_time=4.0, rate_func=linear)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"acierta = {fmt(100 * ACIERTO, 1)} % del tiempo"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)
        rot.mostrar(cifra_pie(f"tarda {RETRASOS[0]} y {RETRASOS[1]} pasos"), zona="abajo",
                    run_time=0.5)
        self.wait(5.6)
