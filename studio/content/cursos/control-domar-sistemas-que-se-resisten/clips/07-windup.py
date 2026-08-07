class Clip7(Scene):
    """7 - Windup: la memoria que se emborracha. El actuador satura, el
    integrador sigue acumulando y trae un sobregiro tardio; anti-windup
    congela la memoria y llega limpio. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Windup: la memoria que se emborracha")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.6)

        # --- momento: la curva sin anti-windup se dibuja ------------------
        w = curva_windup(con_antiwindup=False)
        w.move_to(0.1 * DOWN)
        self.play(Create(w.ejes), Create(w.etiquetas), run_time=0.5)
        self.play(Create(w.linea_ref), run_time=0.4)
        self.play(Create(w.curva), run_time=1.3)
        rot.mostrar(pie_curso("Ningún motor da par infinito: cuando el "
                              "mando satura, la antena ya no acelera "
                              "más."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el exceso se revela y pulsa, la memoria se emborracha
        self.play(Create(w.exceso), run_time=0.6)
        self.play(Indicate(w.exceso, color=C_MAL, scale_factor=1.15),
                  run_time=0.8)
        rot.mostrar(pie_curso("Pero el integrador sigue acumulando... y "
                              "al llegar, trae un sobregiro enorme y "
                              "tardío."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: el remedio, anti-windup (pie ANTES del transform) ---
        w2 = curva_windup(con_antiwindup=True)
        w2.move_to(w.get_center())
        rot.mostrar(pie_curso("El remedio son tres líneas de código: "
                              "congelar la memoria mientras el actuador "
                              "esté al tope."), zona="abajo", run_time=0.5)
        self.play(ReplacementTransform(w, w2), run_time=1.1)
        self.wait(3.8)

        # --- momento: llega limpio, se marca el clamping -------------------
        rot.mostrar(pie_curso("Anti-windup: llega limpio."), zona="abajo",
                    run_time=0.5)
        clamping = etiqueta_hud("CLAMPING", color=C_OK)
        clamping.next_to(w2, UP, buff=0.3)
        self.play(FadeIn(clamping, shift=0.15 * UP), run_time=0.6)
        self.wait(4.4)

        # --- momento: cierre ------------------------------------------------
        rot.mostrar(pie_curso("La diferencia entre reenganchar el "
                              "satélite o perderlo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)
