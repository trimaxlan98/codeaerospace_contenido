class Clip3(Scene):
    """5.2.3 - Sobre el mismo operador Lookup llegan dos flujos: el que el
    optimizador creia (~8 filas, flecha violeta delgada) y el que en
    realidad entra (149,970 filas, flecha cian gruesa). El error es enorme
    (~18,900 veces). El contador ambar sube hasta las lecturas reales:
    450,173. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso(f"Llegan {S.miles(C1)}"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el mismo operador: dos flujos muy distintos ---------------------
        op = S.operador("Lookup", color=C_TITULO, ancho=2.6, alto=0.95,
                        font_size=26)
        op.move_to(RIGHT * 0.9 + UP * 1.7)
        self.play(FadeIn(op, shift=UP * 0.15), run_time=0.6)
        self.wait(0.6)

        punto_arriba = op.get_left() + UP * 0.75
        punto_abajo = op.get_left() + DOWN * 0.75
        f_est = S.flecha_plan(punto_arriba + LEFT * 4.7, punto_arriba,
                              round(ESTIMADO), color=C_CREE)
        f_real = S.flecha_plan(punto_abajo + LEFT * 4.7, punto_abajo,
                               C1, color=C_CALCULO)

        self.play(Create(f_est), run_time=0.8)
        cif_est = tag_hud(f"~{round(ESTIMADO)} filas", font_size=19,
                          color=C_CALCULO)
        cif_est.next_to(f_est, UP, buff=0.2).align_to(f_est, LEFT)
        tag_est = tag_junto(f_est, "lo que creia", DOWN, buff=0.16,
                            color=C_CREE)
        self.play(FadeIn(cif_est), FadeIn(tag_est), run_time=0.5)
        self.wait(1.8)

        self.play(Create(f_real), run_time=0.9)
        cif_real = tag_hud(f"{S.miles(C1)} filas", font_size=19,
                           color=C_CALCULO)
        cif_real.next_to(f_real, DOWN, buff=0.2).align_to(f_real, LEFT)
        tag_real = tag_junto(f_real, "lo que llego", DOWN, buff=0.55,
                             color=C_CALCULO)
        tag_real.align_to(f_real, LEFT)
        self.play(FadeIn(cif_real), FadeIn(tag_real), run_time=0.5)
        self.wait(2.2)

        cif_error = cifra_pie(f"~{S.miles(ERROR_REDONDO)}x de error")
        rot.mostrar(cif_error, zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el contador de lecturas reales, subiendo -------------------------
        cont = Contador(0, rotulo="lecturas reales", font_size=64, digitos=6)
        cont.move_to(RIGHT * 0.9 + DOWN * 1.75)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(0.6)
        cont.anim(self, VARLOC, run_time=4.0,
                 extra=[op.caja.animate.set_stroke(C_TITULO, width=3.6)])
        self.wait(13.0)
