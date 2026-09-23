class Clip4(Scene):
    """2.1.4 - La curva de entrenamiento real de QMIX en la tesis (G2b,
    semilla 42, 5000 episodios): empieza muy por debajo de la mejor
    estatica, la cruza y se queda entre ella y el oraculo. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("La curva de verdad"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        n = CURVA["episodios"]
        c = Cuadro((-5.4, 6.0, -2.3, 2.3), (0, n), (0, 14000))
        self.play(Create(c.suelo()), run_time=0.4)
        crudo = c.serie(np.arange(n)[::5], CURVA["recompensas"][::5], C_TENUE, 1.2)
        crudo.set_stroke(opacity=0.35)
        xm = np.arange(len(CURVA["media"])) + CURVA["suavizado"] // 2
        media = c.serie(xm[::5], CURVA["media"][::5], C_ADAPTA, 4)
        e_ep = tag_hud(f"{n} episodios", font_size=17, color=C_TENUE)
        e_ep.next_to(c.p(n, 0), DOWN, buff=0.12).align_to(c.p(n, 0), RIGHT)
        self.play(FadeIn(e_ep), Create(crudo), run_time=3.0, rate_func=linear)
        self.play(Create(media), run_time=2.4, rate_func=linear)
        e_q = tag_hud("QMIX", font_size=19, color=C_ADAPTA).next_to(media.get_end(), UP, buff=0.12)
        self.play(FadeIn(e_q), run_time=0.4)
        self.wait(2.6)

        est = c.raya(G42["estatica"], C_ESTATICA, ancho=3)
        orc = c.raya(G42["oraculo"], C_PRIV, ancho=3)
        e_est = tag_hud("mejor estatica", font_size=17, color=C_ESTATICA)
        e_est.next_to(c.p(0, G42["estatica"]), DOWN, buff=0.08).align_to(c.p(0, 0), LEFT).shift(RIGHT * 0.1)
        e_orc = tag_hud("oraculo", font_size=17, color=C_PRIV)
        e_orc.next_to(c.p(0, G42["oraculo"]), UP, buff=0.08).align_to(c.p(0, 0), LEFT).shift(RIGHT * 0.1)
        self.play(Create(est), FadeIn(e_est), run_time=0.8)
        self.wait(1.2)
        self.play(Create(orc), FadeIn(e_orc), run_time=0.8)
        rot.mostrar(dato_pie("G2b, semilla 42"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie(f"evaluado: +{fmt(100 * G42['mejora'], 1)} % sobre la estatica"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        cierre_leccion(self, rot, "Un numero por paso.",
                       "Y mucha paciencia.",
                       crudo, media, e_q, est, orc, e_est, e_orc, e_ep)
