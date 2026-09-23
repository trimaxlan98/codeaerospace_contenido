class Clip3(Scene):
    """2.3.3 - La propuesta 5G-PBFT de la tesis: agrupar la constelacion en
    grupos de 10 que deciden dentro y propagan entre ellos. El trafico por
    decision pasa de cuadratico a casi lineal. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Decidir por grupos"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        lx = np.log10(NS)
        c = Cuadro((-5.2, 4.2, -1.85, 2.2), (lx[0], lx[-1]), (1.5, 6.6))
        self.play(Create(c.suelo()), run_time=0.4)
        ticks = VGroup(*[tag_hud(str(n), font_size=16, color=C_TENUE)
                         .next_to(c.p(np.log10(n), 1.5), DOWN, buff=0.12) for n in NS])
        e_x = tag_hud("satelites", font_size=16, color=C_TENUE).next_to(ticks, DOWN, buff=0.1)
        e_y = tag_hud("mensajes (log)", font_size=16, color=C_TENUE).next_to(c.p(lx[0], 6.6), UP, buff=0.1)
        e_y.align_to(c.p(lx[0], 0), LEFT)
        self.play(FadeIn(ticks), FadeIn(e_x), FadeIn(e_y), run_time=0.6)
        self.wait(1.2)
        plano = c.serie(lx, np.log10([g["plano"] for g in GRUPOS]), C_NO, 4)
        grupos = c.serie(lx, np.log10([g["grupos"] for g in GRUPOS]), C_OK, 4)
        e_p = tag_hud("PBFT plano", font_size=18, color=C_NO).next_to(plano.get_end(), RIGHT, buff=0.15)
        e_g = tag_hud("grupos de 10", font_size=18, color=C_OK).next_to(grupos.get_end(), RIGHT, buff=0.15)
        self.play(Create(plano), run_time=1.8)
        self.play(FadeIn(e_p), run_time=0.4)
        self.wait(3.0)
        self.play(Create(grupos), run_time=1.8)
        self.play(FadeIn(e_g), run_time=0.4)
        self.wait(1.6)
        brecha = DashedLine(c.p(lx[-1], np.log10(G1000["grupos"])), c.p(lx[-1], np.log10(G1000["plano"])),
                            dash_length=0.1, stroke_color=CODE_INK, stroke_width=2)
        self.play(Create(brecha), run_time=0.6)
        rot.mostrar(cifra_pie(f"{G1000['plano']:,} -> {G1000['grupos']:,}".replace(",", " ")),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)
        rot.mostrar(cifra_pie(f"ahorro = {fmt(100 * G1000['ahorro'], 2)} %"), zona="abajo", run_time=0.5)
        self.wait(4.0)
        rot.mostrar(dato_pie("coste: latencia entre grupos"), zona="abajo", run_time=0.5)
        self.wait(4.0)
        self.wait(1.6)
