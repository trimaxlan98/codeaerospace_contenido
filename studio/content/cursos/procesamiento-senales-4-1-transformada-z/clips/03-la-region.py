class Clip3(Scene):
    """4.1.3 - La suma no converge para cualquier z: para el resonador
    en r=0.70 converge FUERA de ese circulo, donde h[n] decae. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Donde converge"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        r0 = RADIOS[0]
        _, polos0, _ = zpk(*RES[r0])
        pz = plano_z([], polos0, unidad=1.6, alcance=1.85)
        pz.move_to(LEFT * 3.2 + DOWN * 0.2)
        self.play(FadeIn(pz.ejes), run_time=0.5)
        self.play(Create(pz.circulo), run_time=1.3)
        self.wait(0.8)

        borde = Circle(radius=r0 * pz.unidad, color=C_TENUE,
                       stroke_width=2.0)
        borde.move_to(pz.en(0))
        self.play(Create(borde), run_time=1.2)
        self.play(FadeIn(pz.polos), run_time=0.9)
        self.wait(1.0)

        # --- sombrear la region de convergencia (fuera del polo) ----------
        roc = Annulus(inner_radius=r0 * pz.unidad,
                      outer_radius=pz.alcance * pz.unidad,
                      color=C_SALIDA, fill_opacity=0.22, stroke_width=0)
        roc.move_to(pz.en(0))
        roc.set_z_index(-5)
        et_roc = tag_hud("converge", font_size=18, color=C_SALIDA)
        et_roc.move_to(pz.en(1.15 + 1.05j))
        self.play(FadeIn(roc), FadeIn(et_roc), run_time=1.3)
        self.wait(4.5)

        # --- la respuesta al impulso que lo justifica: decae -------------
        sec = Secuencia(H_RES[r0], 0, (-1.2, 1.2), ancho=6.0, alto=2.4,
                        color=C_MUESTRA)
        sec.move_to(RIGHT * 3.0 + DOWN * 0.2)
        et_h = tag_hud("h[n]", font_size=18, color=C_MUESTRA)
        et_h.next_to(sec, UP, buff=0.18)
        self.play(FadeIn(sec), FadeIn(et_h), run_time=1.4)
        self.wait(3.0)

        rot.mostrar(cifra_pie(f"suma h = {fmt(SUMA_H_RES[r0], 1)}"),
                    zona="abajo", run_time=0.6)
        self.wait(11.5)
