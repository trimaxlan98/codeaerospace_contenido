class Clip3(Scene):
    """3 - ζ: el carácter del sistema. Un único número, el amortiguamiento,
    resume el temperamento de la respuesta: casi cero es un baile eterno,
    0.7 el compromiso clásico, y demasiado alto es lento como un trámite.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo ------------------------------------------
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("ζ: el carácter del sistema")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: la respuesta subamortiguada, casi sin freno ------------
        resp = respuesta_escalon(zeta=0.056, wn=2.24)
        resp.move_to(np.array([0.0, -0.1, 0.0]))
        self.play(Create(resp.ejes), FadeIn(resp.etiquetas),
                  Create(resp.linea_ref), Create(resp.curva), run_time=1.3)

        rot.mostrar(pie_curso("Un solo número resume el temperamento: el "
                              "amortiguamiento."), zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: zeta = 0.056, el numero detras del bamboleo ------------
        rot.mostrar(formula_pie(r"\zeta = 0.056"), zona="abajo",
                   run_time=0.45)
        self.wait(1.6)

        rot.mostrar(pie_curso("Casi cero: 84% de sobreimpulso y medio "
                              "minuto de bamboleo."), zona="abajo",
                   run_time=0.45)
        self.wait(4.6)

        # --- momento: transform a zeta = 0.7, el compromiso clasico -----------
        # El pie cambia ANTES del transform que ilustra.
        rot.mostrar(pie_curso("En 0.7, el clásico compromiso: rápido y "
                              "casi sin pasarse."), zona="abajo",
                   run_time=0.45)
        resp07 = respuesta_escalon(zeta=0.7, wn=2.24)
        resp07.move_to(resp.get_center())
        self.play(ReplacementTransform(resp, resp07), run_time=1.0)
        resp = resp07
        self.wait(3.6)

        rot.mostrar(formula_pie(r"\zeta = 0.7"), zona="abajo", run_time=0.45)
        self.wait(1.6)

        # --- momento: transform a zeta = 1.6, sobreamortiguado ----------------
        # El pie cambia ANTES del transform que ilustra.
        rot.mostrar(pie_curso("Demasiado amortiguado: seguro... pero lento "
                              "como un trámite."), zona="abajo",
                   run_time=0.45)
        resp16 = respuesta_escalon(zeta=1.6, wn=2.24)
        resp16.move_to(resp.get_center())
        self.play(ReplacementTransform(resp, resp16), run_time=1.0)
        resp = resp16
        self.wait(3.6)

        rot.mostrar(formula_pie(r"\zeta = 1.6"), zona="abajo", run_time=0.45)
        self.wait(1.6)

        # --- momento: cierre ---------------------------------------------------
        rot.mostrar(pie_curso("El arte está en elegir cuánto freno."),
                   zona="abajo", run_time=0.45)
        self.wait(4.6)
