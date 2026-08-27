class Clip1(Scene):
    """4.1.1 - z^-1 es una muestra de retraso: al sustituirlo en la
    ecuacion en diferencias aparece el polinomio H(z), y sus coeficientes
    son la propia respuesta al impulso. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("De la suma a z"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- la linea de retardos -----------------------------------------
        bx = bloque("x[n]", ancho=1.4, alto=0.7, color=C_SENAL, tamano=20)
        b1 = bloque("retraso", ancho=1.5, alto=0.7, color=C_MUESTRA,
                   tamano=18)
        b2 = bloque("retraso", ancho=1.5, alto=0.7, color=C_MUESTRA,
                   tamano=18)
        fila = VGroup(bx, b1, b2).arrange(RIGHT, buff=1.0)
        fila.move_to(UP * 2.05)
        c1 = conectar(bx, b1)
        c2 = conectar(b1, b2)
        et_x1 = tag_junto(b1, "x[n-1]", direccion=DOWN, font_size=18,
                          color=C_TENUE)
        et_x2 = tag_junto(b2, "x[n-2]", direccion=DOWN, font_size=18,
                          color=C_TENUE)
        self.play(FadeIn(bx), run_time=0.5)
        self.play(Create(c1), FadeIn(b1), FadeIn(et_x1), run_time=0.8)
        self.play(Create(c2), FadeIn(b2), FadeIn(et_x2), run_time=0.8)
        self.play(flujo([c1, c2]), run_time=1.3)
        self.wait(0.8)

        rot.mostrar(formula_pie(
            r"y[n] = x[n] - 1.6\,x[n-1] + 0.9\,x[n-2]"),
            zona="abajo", run_time=0.6)
        self.wait(5.0)

        # --- sustituir cada retardo por z^-1 -------------------------------
        z1 = Text("z^-1", font=FUENTE_HUD, font_size=18, color=WHITE)
        z1.move_to(b1[1].get_center())
        z2 = Text("z^-1", font=FUENTE_HUD, font_size=18, color=WHITE)
        z2.move_to(b2[1].get_center())
        self.play(Transform(b1[1], z1), Transform(b2[1], z2),
                  Indicate(b1[0], color=C_CALCULO),
                  Indicate(b2[0], color=C_CALCULO), run_time=1.2)
        rot.mostrar(formula_pie(r"H(z) = 1 - 1.6\,z^{-1} + 0.9\,z^{-2}"),
                    zona="abajo", run_time=0.6)
        self.wait(5.0)

        # --- H_FIR: la respuesta al impulso son los propios coeficientes --
        sec = Secuencia(H_FIR, 0, ancho=7.4, alto=2.0, color=C_MUESTRA)
        sec.move_to(DOWN * 0.35)
        et_h = tag_hud("h[n]", font_size=18, color=C_MUESTRA)
        et_h.next_to(sec, UP, buff=0.18)
        self.play(FadeIn(sec.ejes), FadeIn(et_h), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i))
                               for i in range(len(H_FIR))], lag_ratio=0.09),
                  LaggedStart(*[FadeIn(sec.punto(i))
                               for i in range(len(H_FIR))], lag_ratio=0.09),
                  run_time=2.0)
        marca = VGroup(*[sec.marcar(i, color=C_CALCULO) for i in range(3)])
        self.play(FadeIn(marca), run_time=0.6)
        self.wait(8.5)
