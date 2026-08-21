class Clip2(Scene):
    """4.1.2 - registro_conv (K=3, G=(7,5)): un bit real entra y las dos
    salidas se calculan con los XOR sobre bit y memoria; el bit recorre
    el registro con Transforms entre gemelas con_bit(). (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El registro que recuerda")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el registro vacio -------------------------------------
        rot.mostrar(pie_curso("Este registro guarda los dos bits "
                              "anteriores, en dos memorias."),
                    zona="abajo", run_time=0.5)
        reg = registro_conv(lado=0.72)
        reg.move_to(UP * 0.9)
        et_mem = tag_junto(VGroup(reg.cajas[1], reg.cajas[2]), "memoria",
                           direccion=UP, buff=0.18)
        panel_k = panel_derecha(
            tag_hud(f"K = {fmt(K_CONV, 0)}", font_size=18),
            tag_hud(f"G = {G_CONV}", font_size=18),
            tag_hud(f"tasa = {TASA_CONV}", font_size=18))
        self.play(FadeIn(reg), FadeIn(et_mem), FadeIn(panel_k), run_time=1.0)
        self.wait(5.0)

        # --- momento: entra el primer bit real -------------------------------
        rot.mostrar(pie_curso("Entra el primer bit real: la memoria "
                              "calcula dos salidas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_mem), run_time=0.4)
        reg1 = reg.con_bit(BITS_MENSAJE[0], ESTADOS_CONV[0])
        self.play(Transform(reg, reg1), run_time=1.1)
        o1_0, o2_0 = SALIDA_CONV[0], SALIDA_CONV[1]
        cifra_o1 = tag_hud(f"o1 = {fmt(o1_0, 0)}", font_size=18,
                           color=C_BIT)
        cifra_o1.next_to(reg.salidas[0], DOWN, buff=0.12)
        cifra_o2 = tag_hud(f"o2 = {fmt(o2_0, 0)}", font_size=18,
                           color=C_COD)
        cifra_o2.next_to(reg.salidas[1], DOWN, buff=0.12)
        self.play(FadeIn(cifra_o1), FadeIn(cifra_o2), run_time=0.6)
        self.wait(5.0)

        # --- momento: el segundo bit recorre el registro ----------------------
        rot.mostrar(pie_curso("El siguiente bit entra y el anterior pasa "
                              "a la memoria: el registro RECUERDA."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifra_o1), FadeOut(cifra_o2), run_time=0.4)
        reg2 = reg.con_bit(BITS_MENSAJE[1], ESTADOS_CONV[1])
        self.play(Transform(reg, reg2), run_time=1.3)
        o1_1, o2_1 = SALIDA_CONV[2], SALIDA_CONV[3]
        cifra_o1b = tag_hud(f"o1 = {fmt(o1_1, 0)}", font_size=18,
                            color=C_BIT)
        cifra_o1b.next_to(reg.salidas[0], DOWN, buff=0.12)
        cifra_o2b = tag_hud(f"o2 = {fmt(o2_1, 0)}", font_size=18,
                            color=C_COD)
        cifra_o2b.next_to(reg.salidas[1], DOWN, buff=0.12)
        self.play(FadeIn(cifra_o1b), FadeIn(cifra_o2b), run_time=0.6)
        self.wait(5.0)

        # --- momento: dos bits por cada uno que entra --------------------------
        rot.mostrar(pie_curso("Dos bits salen por cada bit que entra: "
                              "el costo que compra la memoria."),
                    zona="abajo", run_time=0.5)
        salida_parcial = tren_bits(SALIDA_CONV[0:4], lado=0.42, color=C_COD)
        salida_parcial.move_to(DOWN * 2.3)
        et_salida = tag_junto(salida_parcial, "la salida, en verde",
                              direccion=DOWN, buff=0.16)
        self.play(FadeIn(salida_parcial), FadeIn(et_salida), run_time=0.9)
        self.wait(6.5)
