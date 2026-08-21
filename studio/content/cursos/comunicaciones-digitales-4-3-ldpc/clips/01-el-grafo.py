class Clip1(Scene):
    """4.3.1 - El grafo: 12 bits abajo, 9 comprobaciones arriba. Cada
    check exige paridad par a sus 4 vecinos; H es ese vecindario escrito
    como matriz. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Un código es un vecindario")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        g = grafo_ldpc(H_LDPC, ancho=ANCHO_GRAFO, alto=ALTO_GRAFO)
        g.move_to(POS_GRAFO)

        # --- momento: los bits, solos, no dicen nada ----------------------
        rot.mostrar(pie_curso("Doce bits llegan de la sonda. Por si solo, "
                              "ninguno sabe si es el que salio."),
                    zona="abajo", run_time=0.5)
        et_bits = tag_junto(g.bits, f"{N_BITS} bits", direccion=DOWN,
                            buff=0.22)
        self.play(LaggedStart(*[FadeIn(b, scale=0.6) for b in g.bits],
                              lag_ratio=0.08), run_time=1.6)
        self.play(FadeIn(et_bits), run_time=0.4)
        self.wait(4.2)

        # --- momento: las comprobaciones y sus vecinos --------------------
        rot.mostrar(pie_curso("Arriba, nueve comprobaciones. Cada una "
                              "vigila a cuatro bits; cada bit tiene tres "
                              "vigilantes."),
                    zona="abajo", run_time=0.5)
        et_checks = tag_junto(g.checks, f"{N_CHECKS} comprobaciones",
                              direccion=UP, buff=0.2)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in g.checks],
                              lag_ratio=0.08), FadeIn(et_checks),
                  run_time=1.4)
        self.play(LaggedStart(*[Create(a) for a in g.aristas],
                              lag_ratio=0.02), run_time=1.8)
        self.wait(4.0)

        # --- momento: lo que exige UNA comprobacion -----------------------
        rot.mostrar(pie_curso("Lo que exige una comprobacion es simple: "
                              "que sus cuatro bits sumen par."),
                    zona="abajo", run_time=0.5)
        aristas_d = VGroup(*[g.arista(CHECK_DEMO, i) for i in BITS_CHECK])
        self.play(g.check(CHECK_DEMO).animate.set_stroke(color=C_COD,
                                                         width=3.4),
                  *[a.animate.set_stroke(color=C_COD, width=2.4,
                                         opacity=1.0)
                    for a in aristas_d],
                  *[g.bit(i).animate.set_stroke(color=C_COD, width=2.8)
                    for i in BITS_CHECK],
                  run_time=1.3)
        self.wait(3.4)

        rot.mostrar(formula_pie(
            r"b_{%d} + b_{%d} + b_{%d} + b_{%d} \equiv 0 \pmod 2"
            % tuple(BITS_CHECK)), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: el vecindario escrito como matriz -------------------
        rot.mostrar(pie_curso("Ese vecindario se escribe como una matriz "
                              "H: una fila por comprobacion, un uno por "
                              "vecino."),
                    zona="abajo", run_time=0.5)
        cabecera = tag_hud(f"H : {N_CHECKS} checks x {N_BITS} bits",
                           font_size=16, color=C_TENUE)
        filas = VGroup(*[tag_hud(t, font_size=14, color=C_COD)
                         for t in FILAS_H_TXT])
        filas.arrange(DOWN, buff=0.07)
        if filas.width > 2.75:
            filas.scale_to_fit_width(2.75)
        pesos = VGroup(
            tag_hud(f"columnas de peso {PESO_COL}", font_size=15),
            tag_hud(f"filas de peso {PESO_FIL}", font_size=15),
        ).arrange(DOWN, buff=0.12)
        panel = panel_derecha(cabecera, filas, pesos, buff=0.22)
        self.play(FadeIn(panel, shift=0.2 * LEFT), run_time=0.9)
        self.play(Indicate(filas[CHECK_DEMO], color=C_COD, scale_factor=1.1),
                  run_time=0.9)
        self.wait(4.8)
