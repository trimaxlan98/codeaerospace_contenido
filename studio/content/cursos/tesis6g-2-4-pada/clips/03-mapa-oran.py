class Clip3(Scene):
    """2.4.3 - PADA no inventa protocolos: se apoya en los que O-RAN ya
    tiene. El entrenamiento centralizado cae en el non-RT RIC y la ejecucion
    en el near-RT RIC: CTDE es la particion que O-RAN ya induce. Y el pase
    LEO cabe justo en el lazo near-RT. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("El mapa sobre O-RAN"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        def caja(w, h, col, texto, sub):
            r = RoundedRectangle(corner_radius=0.15, width=w, height=h, stroke_color=col, stroke_width=3)
            t = tag_hud(texto, font_size=19, color=col)
            s = tag_hud(sub, font_size=15, color=C_DATO)
            VGroup(t, s).arrange(DOWN, buff=0.08).move_to(r)
            return VGroup(r, t, s)
        smo = caja(4.6, 1.2, C_ADAPTA, "non-RT RIC", "rApps, > 1 s").move_to([-3.2, 1.55, 0])
        nrt = caja(4.6, 1.2, C_ENLACE, "near-RT RIC", "xApps, 10 ms - 1 s").move_to([-3.2, -0.35, 0])
        e2 = caja(4.6, 1.0, CODE_INK, "nodos E2", "la red").move_to([-3.2, -2.05, 0])
        a1 = Arrow(smo.get_bottom(), nrt.get_top(), buff=0.06, stroke_width=4, color=C_ADAPTA)
        ae2 = DoubleArrow(nrt.get_bottom(), e2.get_top(), buff=0.06, stroke_width=4, color=C_ENLACE,
                          tip_length=0.18)
        la1 = tag_hud("A1", font_size=18, color=C_ADAPTA).next_to(a1, LEFT, buff=0.12)
        le2 = tag_hud("E2", font_size=18, color=C_ENLACE).next_to(ae2, LEFT, buff=0.12)
        self.play(FadeIn(e2), run_time=0.5)
        self.play(FadeIn(nrt), GrowArrow(ae2), FadeIn(le2), run_time=0.8)
        self.play(FadeIn(smo), GrowArrow(a1), FadeIn(la1), run_time=0.8)
        rot.mostrar(dato_pie("O-RAN WG1 y WG3"), zona="abajo", run_time=0.5)
        self.wait(2.6)

        # los modulos de PADA, colocados donde la tesis los ancla
        pada = [("Analisis", smo, "R1 y Y1"), ("Decision", a1, "A1 politicas"),
                ("Percepcion", ae2, "E2 REPORT"), ("Accion", ae2, "E2 CONTROL")]
        xs_d = [1.6, 1.6, 1.6, 1.6]
        ys_d = [1.55, 0.6, -0.95, -1.85]
        etqs = VGroup()
        for (nm, destino, via), x, y in zip(pada, xs_d, ys_d):
            t = VGroup(tag_hud(nm, font_size=19, color=CODE_INK), tag_hud(via, font_size=15, color=C_DATO))
            t.arrange(DOWN, buff=0.06).move_to([x, y, 0])
            f = Arrow(t.get_left(), destino.get_right(), buff=0.12, stroke_width=2.5, color=C_TENUE,
                      max_tip_length_to_length_ratio=0.12)
            self.play(FadeIn(t, shift=LEFT * 0.1), GrowArrow(f), run_time=0.7)
            etqs.add(t, f)
            self.wait(0.9)
        rot.mostrar(dato_pie("CTDE: entrenar arriba, ejecutar abajo"), zona="abajo", run_time=0.5)
        self.wait(3.8)
        rot.mostrar(cifra_pie(f"RTT LEO {fmt(RTT_CENIT, 1)}-{fmt(RTT_BORDE, 1)} ms"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)
        rot.mostrar(dato_pie("no hay interfaz inter-RIC"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        self.wait(2.2)
