class Clip3(Scene):
    """6.2.3 - La 8-PSK del manual contra la aprendida, lado a lado: la
    MISMA energia media (1.000) y una distancia minima mayor (0.926
    contra 0.765). (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La constelación que nadie dibujó")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        piq_a = plano_iq(unidad=0.92, alcance=1.55)
        piq_a.move_to(LEFT * 3.5 + UP * 0.55)
        piq_b = plano_iq(unidad=0.92, alcance=1.55)
        piq_b.move_to(RIGHT * 3.5 + UP * 0.55)

        # --- momento: la del manual ---------------------------------------
        rot.mostrar(pie_curso("Cien años de constelaciones dan esta: ocho "
                              "fases repartidas en un círculo."),
                    zona="abajo", run_time=0.5)
        pts_a = piq_a.puntos(P_PSK8, color=C_BIT, radio=0.08)
        et_a = tag_junto(piq_a, "8-PSK del manual", direccion=UP, buff=0.18,
                         font_size=20, color=C_BIT)
        self.play(FadeIn(piq_a), FadeIn(et_a), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in pts_a],
                              lag_ratio=0.09), run_time=1.5)
        self.wait(3.4)

        # --- momento: la que salio del gradiente --------------------------
        rot.mostrar(pie_curso("Esta salió del gradiente: siete puntos en "
                              "el borde y uno en el centro."),
                    zona="abajo", run_time=0.5)
        pts_b = piq_b.puntos(Z_FIN, color=C_IA, radio=0.08)
        et_b = tag_junto(piq_b, "aprendida en 250 pasos", direccion=UP,
                         buff=0.18, font_size=20, color=C_IA)
        self.play(FadeIn(piq_b), FadeIn(et_b), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(d, scale=0.5) for d in pts_b],
                              lag_ratio=0.09), run_time=1.5)
        self.wait(3.4)

        # --- momento: la energia igualada ---------------------------------
        rot.mostrar(pie_curso("Para compararlas hay que igualar la energía "
                              "media. Las dos valen exactamente uno."),
                    zona="abajo", run_time=0.5)
        e_a = tag_hud(f"E media = {fmt(E_PSK8, 3)}", font_size=20,
                      color=C_BANDA)
        e_a.next_to(piq_a, DOWN, buff=0.32)
        e_b = tag_hud(f"E media = {fmt(E_AE, 3)}", font_size=20,
                      color=C_BANDA)
        e_b.next_to(piq_b, DOWN, buff=0.32)
        self.play(FadeIn(e_a), FadeIn(e_b), run_time=0.7)
        self.wait(4.8)

        # --- momento: la distancia minima ---------------------------------
        rot.mostrar(pie_curso("Con la misma energía, la aprendida separa "
                              "más sus símbolos."),
                    zona="abajo", run_time=0.5)
        i_a, j_a = PAR_PSK8
        seg_a = Line(piq_a.p(P_PSK8[i_a]), piq_a.p(P_PSK8[j_a]),
                     color=C_CIFRA, stroke_width=3.0)
        i_b, j_b = PAR_AE
        seg_b = Line(piq_b.p(Z_FIN[i_b]), piq_b.p(Z_FIN[j_b]),
                     color=C_CIFRA, stroke_width=3.0)
        d_a = tag_hud(f"d_min = {fmt(D_PSK8, 3)}", font_size=21)
        d_a.next_to(e_a, DOWN, buff=0.2)
        d_b = tag_hud(f"d_min = {fmt(D_FIN, 3)}", font_size=21)
        d_b.next_to(e_b, DOWN, buff=0.2)
        self.play(Create(seg_a), Create(seg_b), run_time=1.0)
        self.play(FadeIn(d_a), FadeIn(d_b), run_time=0.6)
        self.wait(4.0)

        # --- momento: la eligio el canal ----------------------------------
        rot.mostrar(pie_curso("Nadie la dibujó en una pizarra. La eligió "
                              "este canal."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(pts_b, color=C_IA, scale_factor=1.18),
                  run_time=1.0)
        self.wait(4.6)
