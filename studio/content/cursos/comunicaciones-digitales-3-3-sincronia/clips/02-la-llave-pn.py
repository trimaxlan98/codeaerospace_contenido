class Clip2(Scene):
    """3.3.2 - La llave: una m-secuencia de 31 chips cuya autocorrelacion
    vale 31 en fase y EXACTAMENTE -1 en cualquier otra. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La llave que solo se parece a sí misma")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los 31 chips ----------------------------------------
        rot.mostrar(pie_curso("El preámbulo no es cualquier cosa: son 31 "
                              "chips fijos, conocidos por los dos lados."),
                    zona="abajo", run_time=0.5)
        on_pn = onda(T_PN, Y_PN, rango_y=(-1.6, 1.6), ancho=9.6, alto=1.5,
                     color=C_BIT)
        on_pn.move_to(UP * 1.62)
        et_pn = tag_hud(f"{N_CHIPS} chips, +1 / -1", font_size=20,
                        color=C_BIT)
        et_pn.next_to(on_pn, UP, buff=0.12)
        self.play(FadeIn(on_pn.ejes), FadeIn(et_pn), run_time=0.6)
        self.play(Create(on_pn.curva), run_time=2.0)
        self.wait(3.0)

        # --- momento: la misma secuencia, en bits -------------------------
        rot.mostrar(pie_curso("Salen de un registro de 5 bits que recorre "
                              "sus 31 estados y vuelve a empezar."),
                    zona="abajo", run_time=0.5)
        tren = tren_bits(BITS_PN, lado=0.28)
        tren.move_to(UP * 0.15)
        et_tren = tag_junto(tren, "la misma secuencia, en bits",
                            direccion=DOWN, buff=0.18)
        self.play(LaggedStart(*[FadeIn(c) for c in tren.celdas],
                              lag_ratio=0.02), run_time=1.2)
        self.play(FadeIn(tren.digitos), FadeIn(et_tren), run_time=0.6)
        self.wait(4.0)

        # --- momento: desplazarla 7 chips ---------------------------------
        rot.mostrar(pie_curso("Desplázala 7 chips y multiplícala consigo "
                              "misma: los productos se cancelan casi todos."),
                    zona="abajo", run_time=0.5)
        on_rot = onda(T_PN_ROT, Y_PN_ROT, rango_y=(-1.6, 1.6), ancho=9.6,
                      alto=1.5, color=C_BIT)
        on_rot.move_to(DOWN * 0.35)
        on_rot.curva.set_stroke(opacity=0.6, width=2.2)
        et_rot = tag_junto(on_rot, f"la misma, corrida {K_MUESTRA} chips",
                           direccion=DOWN, buff=0.16)
        self.play(FadeOut(tren), FadeOut(et_tren), run_time=0.5)
        self.play(FadeIn(on_rot.ejes), Create(on_rot.curva),
                  FadeIn(et_rot), run_time=1.6)
        cuenta = tag_hud(f"R[{K_MUESTRA}] = {fmt(R_MUESTRA, 0)}",
                         font_size=26)
        cuenta.move_to(DOWN * 2.15)
        self.play(FadeIn(cuenta, shift=0.12 * UP), run_time=0.6)
        self.wait(3.4)

        # --- momento: la autocorrelacion entera ---------------------------
        rot.mostrar(pie_curso("Los 31 desplazamientos, medidos: en fase "
                              "suma 31; fuera, exactamente -1."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(on_pn.ejes), FadeOut(on_pn.curva),
                  FadeOut(et_pn), FadeOut(on_rot.ejes),
                  FadeOut(on_rot.curva), FadeOut(et_rot),
                  FadeOut(cuenta), run_time=0.7)
        ks = np.arange(N_CHIPS, dtype=float)
        on_r = onda(ks, R_AUTO, rango_y=(-6.0, 34.0), ancho=9.0, alto=3.4)
        on_r.move_to(DOWN * 0.15)
        barras = on_r.muestras(ks, R_AUTO, color=C_CIFRA, radio=0.045)
        piso = on_r.horizontal_en(R_FUERA, color=C_TENUE)
        et_k = tag_junto(on_r, "desplazamiento k", direccion=DOWN,
                         buff=0.16)
        self.play(FadeIn(on_r.ejes), FadeIn(et_k), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(b) for b in barras],
                              lag_ratio=0.05), run_time=2.0)
        self.play(Create(piso), run_time=0.6)
        et_pico = tag_hud(f"R[0] = {fmt(R_PICO, 0)}", font_size=24)
        et_pico.next_to(on_r.en(0.0, R_PICO), RIGHT, buff=0.22)
        et_piso = tag_hud(f"R[k != 0] = {fmt(R_FUERA, 0)}", font_size=22)
        et_piso.next_to(on_r.en(float(N_CHIPS - 1), R_FUERA), UR,
                        buff=0.14)
        et_piso.shift(LEFT * et_piso.width * 0.55)
        self.play(FadeIn(et_pico), FadeIn(et_piso), run_time=0.6)
        self.wait(4.6)
