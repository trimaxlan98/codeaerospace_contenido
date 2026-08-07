class Clip5(Scene):
    """5 - PID: resorte, amortiguador y memoria. El PID hecho analogo
    fisico: el resorte proporcional que tira mas fuerte cuanto mas lejos
    esta, el amortiguador derivativo que frena antes de llegar, y la
    memoria integral que borra lo que falta. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo --------------------------------------------------
        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("PID: resorte, amortiguador y memoria")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(0.4)

        # --- momento: el sistema y su respuesta oscilante -----------------
        mr = masa_resorte(ancho=2.8).scale(0.8)
        mr.move_to((-3.1, -0.1, 0.0))
        resp = respuesta_escalon(zeta=0.056, wn=2.24, ancho=4.6, alto=2.2)
        resp.move_to((2.7, -0.1, 0.0))
        self.play(FadeIn(mr), Create(resp.ejes), FadeIn(resp.etiquetas),
                  Create(resp.linea_ref), run_time=0.6)
        self.play(Create(resp.curva), run_time=0.6)

        # --- momento: P es un resorte, tira mas fuerte cuanto mas lejos ---
        rot.mostrar(pie_curso("P es un resorte: tira más fuerte cuanto "
                              "más lejos estás."), zona="abajo")
        self.play(Indicate(mr.resorte, color=C_CTRL, scale_factor=1.18),
                  run_time=0.6)
        self.wait(4.0)

        # --- momento: pero un resorte solo... oscila -----------------------
        rot.mostrar(pie_curso("Pero un resorte solo... oscila."),
                    zona="abajo")
        self.play(Indicate(resp.curva, color=C_MAL, scale_factor=1.05),
                  run_time=0.6)
        self.wait(4.0)

        # --- momento: D es el amortiguador, frena antes de llegar (pie ANTES) --
        rot.mostrar(pie_curso("D es el amortiguador: frena antes de "
                              "llegar. El bamboleo muere."), zona="abajo")
        self.play(Indicate(mr.amortiguador, color=C_CTRL, scale_factor=1.18),
                  run_time=0.6)
        calmada = respuesta_escalon(zeta=0.7, wn=2.24, ancho=4.6, alto=2.2)
        calmada.move_to(resp.get_center())
        self.play(ReplacementTransform(resp, calmada), run_time=0.9)
        self.wait(3.4)

        # --- momento: I es la memoria, acumula hasta borrar el resto ------
        rot.mostrar(pie_curso("I es la memoria: acumula lo que falta "
                              "hasta borrarlo del todo."), zona="abajo")
        self.wait(4.6)

        # --- momento: cierre narrativo ---------------------------------------
        rot.mostrar(pie_curso("Tres perillas. Con eso se apunta una "
                              "antena de media tonelada."), zona="abajo")
        self.wait(4.6)

        # --- momento: la formula PID queda escrita en el pie -----------------
        rot.mostrar(formula_pie(r"u = k_p e + k_i \int e + k_d \dot{e}"),
                    zona="abajo")
        self.wait(5.2)
