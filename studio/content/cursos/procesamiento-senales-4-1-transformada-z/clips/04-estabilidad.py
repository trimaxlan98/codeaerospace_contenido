class Clip4(Scene):
    """4.1.4 - Deslizar el par de polos hacia afuera del circulo unidad:
    la cola de h[n] pasa de morir a estallar. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("La frontera"), zona="arriba",
                    run_time=0.6)
        self.wait(0.7)

        r0 = RADIOS[0]
        _, polos0, _ = zpk(*RES[r0])
        pz = plano_z([], polos0, unidad=1.5, alcance=1.65)
        pz.move_to(LEFT * 3.3 + UP * 0.35)
        self.play(FadeIn(pz.ejes), Create(pz.circulo), run_time=1.2)
        self.play(FadeIn(pz.polos), run_time=0.9)
        self.wait(1.0)

        sec = Secuencia(H_RES[r0], 0, (-65, 65), ancho=6.2, alto=2.7,
                        color=C_MUESTRA)
        sec.move_to(RIGHT * 2.9 + UP * 0.35)
        et_h = tag_hud("h[n]", font_size=18, color=C_MUESTRA)
        et_h.next_to(sec, UP, buff=0.18)
        self.play(FadeIn(sec), FadeIn(et_h), run_time=0.6)
        self.wait(0.6)

        panel = panel_cifras((f"r = {fmt(r0, 2)}", C_CALCULO),
                             (f"cola = {fmt(COLA[r0], 1)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(3.2)

        # --- deslizar el polo hacia afuera: 0.92 y luego 1.05 --------------
        for r in RADIOS[1:]:
            _, polos_r, _ = zpk(*RES[r])
            pz2 = pz.con_pz([], polos_r)
            sec2 = sec.con_valores(H_RES[r])
            panel2 = panel_cifras((f"r = {fmt(r, 2)}", C_CALCULO),
                                  (f"cola = {fmt(COLA[r], 1)}", C_CALCULO))
            self.play(Transform(pz, pz2), Transform(sec, sec2),
                      Transform(panel, panel2), run_time=2.3)
            self.wait(3.6)

        cierre_leccion(self, rot, "El circulo unidad no es un dibujo.",
                       "Es la frontera de lo estable.",
                       pz, sec, et_h, panel, espera=5.0)
