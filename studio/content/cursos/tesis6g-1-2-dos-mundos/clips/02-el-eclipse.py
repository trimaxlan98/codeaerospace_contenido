class Clip2(Scene):
    """1.2.2 - La visibilidad de cada satelite sube y baja con la orbita;
    por debajo de 0.35 el enlace por espectro se desploma al 10 %. Cada
    satelite pasa asi 25 de cada 60 pasos. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El eclipse"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        t = np.arange(PASOS)
        c1 = Cuadro((-6.0, 6.0, 0.35, 2.55), (0, PASOS - 1), (0, 1))
        c2 = Cuadro((-6.0, 6.0, -2.35, -0.15), (0, PASOS - 1), (0, 1))
        e1 = tag_junto(Dot(c1.p(0, 1)), "satelite 1", LEFT, buff=0.15, font_size=22)
        e2 = tag_junto(Dot(c2.p(0, 1)), "satelite 2", LEFT, buff=0.15, font_size=22)
        e1.next_to(c1.p(0, 1.12), RIGHT, buff=0.0)
        e2.next_to(c2.p(0, 1.12), RIGHT, buff=0.0)
        self.play(Create(c1.suelo()), Create(c2.suelo()), FadeIn(e1), FadeIn(e2), run_time=0.8)
        v1 = c1.serie(t, VIS[0], C_ADAPTA, 4, esquinas=False)
        v2 = c2.serie(t, VIS[1], C_ADAPTA, 4, esquinas=False)
        self.play(Create(v1), Create(v2), run_time=3.6, rate_func=linear)
        self.wait(2.6)

        u1 = c1.raya(E["eclipse_umbral"], C_NO)
        u2 = c2.raya(E["eclipse_umbral"], C_NO)
        et_u = tag_hud(f"umbral {fmt(E['eclipse_umbral'], 2)}", font_size=18, color=C_NO)
        et_u.next_to(c1.p(15, E["eclipse_umbral"]), UP, buff=0.08)
        self.play(Create(u1), Create(u2), FadeIn(et_u), run_time=0.9)
        self.wait(1.8)
        f1 = c1.franjas(t, ECL[0], C_NO, 0.16)
        f2 = c2.franjas(t, ECL[1], C_NO, 0.16)
        self.play(FadeIn(f1), FadeIn(f2), run_time=1.0)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"eclipse = {fmt(100 * FRAC_ECL, 1)} % del tiempo"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)
        rot.mostrar(dato_pie(f"en eclipse x {fmt(E['eclipse_factor'], 2)}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)

        # los dos a la vez: la franja comun
        comun = c2.franjas(t, ECL.all(axis=0), C_NO, 0.42)
        self.play(FadeIn(comun), run_time=0.8)
        rot.mostrar(cifra_pie(f"ambos a la vez = {fmt(100 * FRAC_AMBOS, 1)} %"),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)
