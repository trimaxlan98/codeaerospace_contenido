class Clip4(Scene):
    """2.2.4 - El precio de deslizar: cada salida cuesta tantas
    multiplicaciones como muestras solapen. N x M MACs. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Lo que cuesta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        solapes = [len(p["k"]) for p in PASOS]
        b1 = Barras(solapes, ancho=6.4, alto=2.0, color=C_CALCULO)
        b1.move_to(DOWN * 0.9)
        et_b = tag_junto(b1, "MAC por salida", DOWN, buff=0.18,
                         font_size=20, color=C_CALCULO)

        pos_cont = UP * 2.30
        cont = tag_hud("MAC = 000", font_size=30)
        cont.move_to(pos_cont)
        self.play(FadeIn(b1.ejes), FadeIn(et_b), FadeIn(cont), run_time=0.8)

        # --- el contador sube salida a salida --------------------------------
        acumulado = 0
        for n in range(N_SALIDA):
            acumulado += solapes[n]
            nuevo = tag_hud(f"MAC = {acumulado:03d}", font_size=30)
            nuevo.move_to(pos_cont)
            self.play(FadeIn(b1.barra(n), shift=0.12 * UP),
                      Succession(Wait(0.55),
                                 Transform(cont, nuevo, run_time=0.02)),
                      run_time=0.95)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"{MACS_CORTO} MAC medidos"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"N \times M"), zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- el mismo dibujo, en tamano real ---------------------------------
        solapes_l = [len(p["k"])
                     for p in pasos_convolucion(X_LARGO, H_LARGO)]
        b2 = Barras(solapes_l, ancho=9.6, alto=2.0, color=C_CALCULO)
        b2.move_to(DOWN * 0.9)
        cont_l = tag_hud(f"MAC = {MACS_LARGO:03d}", font_size=30)
        cont_l.move_to(pos_cont)

        self.play(FadeOut(b1.barras), FadeOut(b1.ejes), run_time=0.5)
        self.play(FadeIn(b2),
                  Succession(Wait(0.5),
                             Transform(cont, cont_l, run_time=0.02)),
                  run_time=1.4)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"{MACS_LARGO} MAC medidos"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras(f"N = {N_LARGO}", f"M = {M_LARGO}",
                             f"salida = {SALIDA_LARGO}",
                             (f"{MACS_LARGO} MAC", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)

        cierre_leccion(self, rot, "Filtrar es deslizar y sumar.",
                       "Lo demas es hacerlo rapido.",
                       b2, panel, cont, et_b)
