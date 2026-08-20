class Clip2(Scene):
    """3.1.2 - La misma cajita sobre tres campos: positiva en el radial
    (fuente), negativa en el radial invertido (sumidero), cero en el
    rotor puro (neutro). (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Fuente, sumidero, neutro")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        def fila_historial(texto, color, fila):
            t = tag_hud(texto, font_size=17, color=color)
            t.to_corner(UR, buff=0.55).shift(DOWN * (0.5 + fila * 0.42))
            return _con_fondo(t, buff=0.1, opacidad=0.78)

        # --- momento: la cajita en el campo radial (fuente) -----------------
        pl = plano_leccion()
        campo = campo_flechas(pl, CAMPO_FUENTE, paso=1.0, escala=0.4,
                              opacidad=0.55)
        self.play(FadeIn(pl), FadeIn(campo), run_time=0.9)
        rot.mostrar(pie_curso("La misma cajita, tres campos: primero el "
                              "radial que ya conocemos."), zona="abajo",
                    run_time=0.5)
        cj = caja_conteo(pl, CAMPO_FUENTE, P_TRIO, lado=LADO_CAJA)
        self.play(FadeIn(cj), run_time=0.8)
        d0 = div_num(CAMPO_FUENTE, P_TRIO)
        fila0 = fila_historial(f"FUENTE    div = +{fmt(d0)}", C_RES, 0)
        self.play(FadeIn(fila0, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        # --- momento: el radial invertido (sumidero) -------------------------
        rot.mostrar(pie_curso("Invirtamos el campo: las mismas flechas, "
                              "ahora apuntando hacia adentro."),
                    zona="abajo", run_time=0.5)
        campo_b = campo.con_campo(CAMPO_SUMIDERO)
        self.play(Transform(campo, campo_b), run_time=1.3)
        cj_b = caja_conteo(pl, CAMPO_SUMIDERO, P_TRIO, lado=LADO_CAJA)
        self.play(FadeOut(cj), FadeIn(cj_b), run_time=0.8)
        d1 = div_num(CAMPO_SUMIDERO, P_TRIO)
        fila1 = fila_historial(f"SUMIDERO  div = {fmt(d1)}", C_VEC, 1)
        self.play(FadeIn(fila1, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.8)

        # --- momento: el rotor puro (neutro) ----------------------------------
        rot.mostrar(pie_curso("Y el rotor puro: gira, pero no hincha ni "
                              "vacía la caja."), zona="abajo", run_time=0.5)
        campo_c = campo.con_campo(CAMPO_NEUTRO)
        self.play(Transform(campo, campo_c), run_time=1.3)
        cj_c = caja_conteo(pl, CAMPO_NEUTRO, P_TRIO, lado=LADO_CAJA)
        self.play(FadeOut(cj_b), FadeIn(cj_c), run_time=0.8)
        d2 = div_num(CAMPO_NEUTRO, P_TRIO)
        fila2 = fila_historial(f"NEUTRO    div = {fmt(d2)}", C_CALCULO, 2)
        self.play(FadeIn(fila2, shift=0.15 * LEFT), run_time=0.6)
        self.wait(4.0)

        # --- momento: el veredicto ---------------------------------------------
        rot.mostrar(pie_curso("Positivo, negativo o cero: la divergencia "
                              "es el veredicto de la cajita."), zona="abajo",
                    run_time=0.5)
        self.play(Indicate(VGroup(fila0, fila1, fila2), scale_factor=1.03),
                  run_time=0.9)
        self.wait(4.4)
