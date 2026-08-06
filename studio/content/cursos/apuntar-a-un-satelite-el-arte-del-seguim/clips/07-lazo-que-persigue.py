class Clip7(Scene):
    """7 - El lazo que persigue. La antena real siempre llega un poco
    tarde a la referencia que dicta el propagador: un resorte
    proporcional cierra casi toda la brecha y una memoria integral
    borra el rezago que queda. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo --------------------------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("El lazo que persigue")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.4)

        # --- momento: solo la referencia, ambar ------------------------------
        seg = curvas_seguimiento(retraso=0.16)
        seg.move_to(0.1 * DOWN)
        self.play(Create(seg.ejes), FadeIn(seg.etiquetas), Create(seg.ref),
                  run_time=1.0)
        rot.mostrar(pie_curso("El propagador dicta dónde debería estar la "
                              "antena en cada instante."), zona="abajo")
        self.wait(5.0)

        # --- momento: la antena real, siempre un poco tarde -------------------
        self.play(Create(seg.ant), run_time=0.7)
        rot.mostrar(pie_curso("La antena real siempre llega un poco "
                              "tarde."), zona="abajo")
        self.wait(5.0)

        # --- momento: la flecha del error --------------------------------------
        p_ref, p_ant = seg.brecha_en(0.62)
        flecha = Arrow(p_ant, p_ref, color=C_PELIGRO, buff=0.05,
                       stroke_width=4, max_tip_length_to_length_ratio=0.4)
        tag = tag_junto(flecha, "error", direccion=RIGHT, color=C_PELIGRO)
        self.play(GrowArrow(flecha), FadeIn(tag), run_time=0.45)
        rot.mostrar(pie_curso("Esa brecha es el error de seguimiento: el "
                              "número que el lazo quiere matar."),
                    zona="abajo")
        self.wait(5.0)

        # --- momento: el resorte proporcional acerca (retraso 0.16 -> 0.05) --
        # La flecha vieja se desvanece y el pie cambia ANTES del transform.
        self.play(FadeOut(flecha), FadeOut(tag), run_time=0.25)
        rot.mostrar(pie_curso("Un resorte proporcional acerca..."),
                    zona="abajo")
        seg2 = curvas_seguimiento(retraso=0.05)
        seg2.move_to(seg.get_center())
        self.play(ReplacementTransform(seg, seg2), run_time=0.9)

        p_ref2, p_ant2 = seg2.brecha_en(0.62)
        flecha2 = Arrow(p_ant2, p_ref2, color=C_PELIGRO, buff=0.05,
                        stroke_width=4, max_tip_length_to_length_ratio=0.4)
        tag2 = tag_junto(flecha2, "error", direccion=RIGHT, color=C_PELIGRO)
        self.play(GrowArrow(flecha2), FadeIn(tag2), run_time=0.4)
        self.wait(4.6)

        # --- momento: la memoria integral borra el rezago, enganchado ---------
        # Ultimo paso: retraso=0.0, ya no hay flecha; la antena pasa a verde.
        self.play(FadeOut(flecha2), FadeOut(tag2), run_time=0.25)
        rot.mostrar(pie_curso("...y la memoria integral borra el rezago. "
                              "Enganchado."), zona="abajo")
        seg3 = curvas_seguimiento(retraso=0.0)
        seg3.move_to(seg2.get_center())
        seg3.ant.set_color(C_OK)
        self.play(ReplacementTransform(seg2, seg3), run_time=0.9)
        self.wait(4.6)

        # --- momento: cierre -----------------------------------------------
        rot.mostrar(pie_curso("Domar ese lazo a fondo es otro curso: aquí "
                              "basta ver que persigue."), zona="abajo")
        self.wait(5.0)
