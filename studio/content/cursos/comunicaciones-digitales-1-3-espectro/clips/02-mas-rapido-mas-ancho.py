class Clip2(Scene):
    """1.3.2 - La MISMA secuencia de bits a sps=8 y sps=4 (mismo fs=8):
    duplicar la velocidad de simbolos casi duplica el ancho al 90%,
    medido con ancho_banda sobre las dos PSD. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Más rápido = más ancho")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la onda lenta ------------------------------------------
        rot.mostrar(pie_curso("La misma secuencia de bits, a una "
                              "velocidad de símbolos."),
                    zona="abajo", run_time=0.5)
        on = onda(T_VIS_1, Y_VIS_1, rango_y=(-1.3, 1.3), ancho=7.0, alto=1.7,
                 color=C_SENAL)
        on.move_to(UP * 1.6)
        rs1 = tag_hud(f"Rs = {fmt(RS_1, 1)} simb/s", font_size=17,
                     color=C_BIT)
        rs1.next_to(on, LEFT, buff=0.18)
        self.play(FadeIn(on), FadeIn(rs1), run_time=1.0)
        self.wait(3.4)

        # --- momento: el doble de veloz ---------------------------------------
        rot.mostrar(pie_curso("Ahora el DOBLE de veloz: los mismos bits "
                              "caben en la mitad del tiempo."),
                    zona="abajo", run_time=0.5)
        on2 = onda(T_VIS_2, Y_VIS_2, rango_y=(-1.3, 1.3), ancho=7.0,
                  alto=1.7, color=C_SENAL)
        on2.move_to(UP * 1.6)
        rs2 = tag_hud(f"Rs = {fmt(RS_2, 1)} simb/s", font_size=17,
                     color=C_BIT)
        rs2.next_to(on2, LEFT, buff=0.18)
        self.play(FadeOut(on), FadeOut(rs1), run_time=0.5)
        self.play(FadeIn(on2), FadeIn(rs2), run_time=0.9)
        self.wait(3.2)

        # --- momento: la primera PSD, con su ancho medido ----------------------
        rot.mostrar(pie_curso("Volvamos a la más lenta: en frecuencia, "
                              "ocupa este ancho medido."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(on2), FadeOut(rs2), run_time=0.5)
        self.play(FadeIn(on), FadeIn(rs1), run_time=0.7)
        esp = espectro_area(F_1, P_1_DB, piso_db=-40.0, ancho=7.0, alto=2.0,
                            color=C_BANDA)
        esp.move_to(DOWN * 1.55)
        marca1 = esp.marca_f(BW_1_90, color=C_CIFRA)
        cifra1 = tag_hud(f"BW(90%) = {fmt(BW_1_90, 2)}", font_size=18)
        cifra1.next_to(marca1, UP, buff=0.1)
        self.play(FadeIn(esp), run_time=0.7)
        self.play(Create(marca1), FadeIn(cifra1), run_time=0.9)
        self.wait(2.6)

        # --- momento: el lobulo se ensancha -------------------------------------
        rot.mostrar(pie_curso("Al doblar la velocidad, el lóbulo se "
                              "ensancha: mira cuánto crece el ancho "
                              "medido."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(on), FadeOut(rs1), run_time=0.5)
        self.play(FadeIn(on2), FadeIn(rs2), run_time=0.7)
        esp2 = esp.con_psd(P_2_DB, color=C_BANDA)
        self.play(FadeOut(marca1), FadeOut(cifra1),
                  Transform(esp.curva, esp2.curva),
                  Transform(esp.area, esp2.area), run_time=1.8)
        marca2 = esp.marca_f(BW_2_90, color=C_CIFRA)
        cifra2 = tag_hud(f"BW(90%) = {fmt(BW_2_90, 2)}", font_size=18)
        cifra2.next_to(marca2, UP, buff=0.1)
        self.play(Create(marca2), FadeIn(cifra2), run_time=0.9)
        self.wait(3.6)

        # --- momento: casi el doble, medido -------------------------------------
        rot.mostrar(pie_curso("Casi el doble: el tiempo y la frecuencia "
                              "se compran uno al otro."),
                    zona="abajo", run_time=0.5)
        razon = tag_hud(f"{fmt(BW_2_90, 2)} / {fmt(BW_1_90, 2)} = "
                        f"x{fmt(RATIO_ANCHO, 2)}", font_size=20,
                        color=C_CIFRA)
        razon.next_to(esp, RIGHT, buff=0.3)
        self.play(FadeIn(razon, shift=0.15 * UP), run_time=0.6)
        self.wait(6.0)
