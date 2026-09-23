class Clip4(Scene):
    """1.2.4 - Un canal de espectro se degrada y rota cada 80 pasos, y NADIE
    lo observa. La interferencia de quien lo usa lo delata: sube hasta
    saturar y cae a la mitad en menos de dos pasos. Cierre. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El canal que no se ve"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        n = len(CANAL)
        t = np.arange(n)
        ca = Cuadro((-5.0, 6.2, 0.75, 2.35), (0, n - 1), (-0.2, 1.2))
        cb = Cuadro((-5.0, 6.2, -2.2, -0.2), (0, n - 1), (0, 1))
        # el estado oculto: que canal esta degradado, dibujado APAGADO
        est = ca.serie(t, CANAL.astype(float), C_TENUE, 3)
        et_c0 = tag_hud("canal 0", font_size=17, color=C_TENUE).next_to(ca.p(0, 0), LEFT, buff=0.12)
        et_c1 = tag_hud("canal 1", font_size=17, color=C_TENUE).next_to(ca.p(0, 1), LEFT, buff=0.12)
        oculto = DashedVMobject(est.copy(), num_dashes=60)
        self.play(FadeIn(et_c0), FadeIn(et_c1), Create(oculto), run_time=2.0)
        et_o = tag_hud("no observable", font_size=19, color=C_TENUE)
        et_o.next_to(ca.p(n - 1, 1.2), UP, buff=0.05).align_to(ca.p(n - 1, 1.2), RIGHT)
        self.play(FadeIn(et_o), run_time=0.5)
        self.wait(1.6)
        rot.mostrar(dato_pie(f"rota cada {E['canal_periodo']} pasos"), zona="abajo", run_time=0.5)
        self.wait(3.0)

        # lo que SI se observa: la interferencia de un agente fijo en el canal 0
        self.play(Create(cb.suelo()), run_time=0.5)
        et_i = tag_hud("interferencia propia", font_size=18, color=C_ADAPTA)
        et_i.next_to(cb.p(0, 1), UP, buff=0.08).align_to(cb.p(0, 1), LEFT)
        si = cb.serie(t, INTERF, C_ADAPTA, 4)
        self.play(FadeIn(et_i), Create(si), run_time=4.0, rate_func=linear)
        self.wait(1.4)
        franjas = cb.franjas(t, CANAL == 0, C_NO, 0.14)
        self.play(FadeIn(franjas), run_time=0.8)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"vida media = {fmt(VIDA_MEDIA, 1)} pasos"), zona="abajo",
                    run_time=0.5)
        self.wait(3.8)
        rot.mostrar(formula_pie(rf"I_{{t+1}} = {E['decaimiento']}\,I_t + 0.35\,[\mathrm{{degradado}}]"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "Tres ritmos que no coinciden.",
                       "Adaptarse puede pagar.",
                       oculto, et_c0, et_c1, et_o, si, franjas, et_i)
