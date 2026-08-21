class Clip1(Scene):
    """2.1.1 - La portadora vacia: un coseno puro (onda) y su punto quieto
    en plano_iq. Las dos vistas conviven, todavia sin mensaje. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La portadora vacía")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el coseno puro ---------------------------------------
        rot.mostrar(pie_curso("Una portadora es un coseno puro: amplitud y "
                              "frecuencia fijas, nada mas."),
                    zona="abajo", run_time=0.5)
        on = onda(T_VACIA, Y_VACIA, rango_y=(-1.15, 1.15), ancho=6.2, alto=2.5)
        on.move_to(LEFT * 3.3 + DOWN * 0.35)
        self.play(FadeIn(on.ejes), run_time=0.6)
        self.play(Create(on.curva), run_time=2.2)
        cifra_f = tag_hud(f"f = {fmt(F_PORT, 0)} Hz", font_size=19,
                          color=C_SENAL)
        cifra_f.next_to(on.en(on.x0, on.y1), UP, buff=0.16)
        cifra_f.shift(RIGHT * cifra_f.width / 2)
        self.play(FadeIn(cifra_f), run_time=0.4)
        self.wait(2.0)

        # --- momento: un ciclo, siempre el mismo -----------------------------
        rot.mostrar(pie_curso("Cada ciclo dura lo mismo que el anterior: "
                              "nada cambia de un vuelco a otro."),
                    zona="abajo", run_time=0.5)
        tramo_t = Line(on.en(0.0, on.y0), on.en(PERIODO_PORT, on.y0),
                       color=C_EJE, stroke_width=1.6)
        et_periodo = llave(tramo_t, texto=f"T = {fmt(PERIODO_PORT, 2)} s",
                           direccion=DOWN, font_size=17, color=C_SENAL)
        self.play(FadeIn(et_periodo), run_time=0.6)
        self.wait(3.4)

        # --- momento: todavia no dice nada -----------------------------------
        rot.mostrar(pie_curso("Todavía no dice nada: es forma, no mensaje."),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- momento: el mismo coseno, visto en el plano IQ ------------------
        rot.mostrar(pie_curso("La misma portadora, vista en el plano I/Q, "
                              "es un solo punto: quieto."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.05, alcance=1.7)
        piq.move_to(RIGHT * 3.6 + DOWN * 0.3)
        self.play(FadeIn(piq), run_time=0.7)
        punto = piq.punto(PUNTOS_BPSK[0], color=C_SENAL, radio=0.085)
        et_punto = tag_junto(punto, "sin bits", direccion=DOWN, buff=0.16)
        self.play(FadeIn(punto, scale=0.4), FadeIn(et_punto), run_time=0.6)
        self.wait(4.2)

        # --- momento: dos vistas, la misma cosa -------------------------------
        rot.mostrar(formula_pie(r"s(t) = \cos(2\pi f t + \varphi)"),
                    zona="abajo", run_time=0.5)
        self.wait(7.5)
