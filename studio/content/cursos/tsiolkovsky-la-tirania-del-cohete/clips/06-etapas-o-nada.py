class Clip6(Scene):
    """6 - Etapas o nada. La cuenta completa con estructura: una sola
    etapa da carga util NEGATIVA (la barra roja cuelga del eje); soltar
    masa muerta a mitad de camino cambia el signo. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 06")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Etapas o nada")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la cuenta completa -----------------------------------
        rot.mostrar(pie_curso("Ahora en serio: los tanques y los motores "
                              "también pesan."), zona="abajo", run_time=0.5)
        barras = barras_carga((CARGA_SSTO * 100, CARGA_2ET * 100,
                               CARGA_3ET * 100))
        barras.shift(np.array([0.0, 0.35, 0.0])
                     - barras.eje.get_center())
        self.play(Create(barras.eje), run_time=0.7)

        y_eje = barras.eje.get_center()[1]
        nombres = VGroup()
        for i, texto in enumerate(("1 etapa", "2 etapas", "3 etapas")):
            n = Text(texto, font_size=17, color=C_TENUE)
            n.set_opacity(0.85)
            x = barras.barra(i).get_center()[0]
            n.move_to(np.array([x, y_eje - 1.40, 0.0]))
            nombres.add(n)
        modelo = tag_hud(
            f"modelo: ε = {EPS_ESTRUCTURA:.0%} · "
            f"ve = {VE_QUIMICO/1000:.1f} km/s · "
            f"Δv = {DV_LEO_KMS:.1f} km/s", font_size=13, color=C_TENUE)
        modelo.move_to(np.array([3.4, 2.35, 0.0]))
        self.play(FadeIn(nombres[0]), FadeIn(modelo), run_time=0.6)
        self.wait(2.2)

        # --- momento: el SSTO imposible ------------------------------------
        rot.mostrar(pie_curso("Una sola etapa: la ecuación da carga útil "
                              "NEGATIVA. No hay cohete que la cumpla."),
                    zona="abajo", run_time=0.5)
        self.play(GrowFromEdge(barras.barra(0), UP), run_time=0.9)
        cifra_ssto = tag_hud(f"{CARGA_SSTO*100:+.1f} %", font_size=17,
                             color=C_MUERTO)
        cifra_ssto.next_to(barras.tope(0), DOWN, buff=0.14)
        veredicto = Text("imposible", font_size=17, color=C_MUERTO)
        veredicto.next_to(cifra_ssto, DOWN, buff=0.12)
        self.play(FadeIn(cifra_ssto, shift=0.12 * DOWN),
                  FadeIn(veredicto), run_time=0.7)
        self.wait(3.4)

        # --- momento: soltar masa muerta -----------------------------------
        rot.mostrar(pie_curso("Suelta el tanque vacío a mitad de camino "
                              "y la cuenta cambia de signo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(nombres[1]), run_time=0.4)
        self.play(GrowFromEdge(barras.barra(1), DOWN), run_time=0.9)
        cifra_2 = tag_hud(f"{CARGA_2ET*100:+.1f} %", font_size=17)
        cifra_2.next_to(barras.tope(1), UP, buff=0.14)
        self.play(FadeIn(cifra_2, shift=0.12 * UP), run_time=0.6)
        self.wait(3.0)

        # --- momento: la tercera etapa rinde menos -------------------------
        self.play(FadeIn(nombres[2]), run_time=0.4)
        self.play(GrowFromEdge(barras.barra(2), DOWN), run_time=0.8)
        cifra_3 = tag_hud(f"{CARGA_3ET*100:+.1f} %", font_size=17)
        cifra_3.next_to(barras.tope(2), UP, buff=0.14)
        self.play(FadeIn(cifra_3, shift=0.12 * UP), run_time=0.6)
        rot.mostrar(pie_curso("La tercera ya casi no paga: cada etapa "
                              "extra rinde menos que la anterior."),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)

        # --- momento: el cierre --------------------------------------------
        rot.mostrar(pie_curso("Por eso todo cohete que has visto es una "
                              "torre de etapas que se van soltando."),
                    zona="abajo", run_time=0.5)
        self.wait(5.8)
