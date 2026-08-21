class Clip4(Scene):
    """6.2.4 - El veredicto CONTADO: error de simbolo medido a 4, 6, 8 y
    10 dB; a 10 dB la aprendida rompe 27 simbolos de cien mil contra los
    299 de la 8-PSK. Cierre de leccion. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("¿Mejor? Cuéntalo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la 8-PSK, contada -----------------------------------
        rot.mostrar(pie_curso("Cien mil símbolos por punto, contados uno a "
                              "uno. Primero la 8-PSK del manual."),
                    zona="abajo", run_time=0.5)
        cb = curva_ber(x0=2.0, x1=12.0, exp_min=4, ancho=5.7, alto=3.2)
        cb.move_to(LEFT * 1.7 + UP * 0.3)
        et_y = tag_junto(cb, "error de símbolo", direccion=UP, buff=0.2,
                         font_size=19)
        self.play(FadeIn(cb), FadeIn(et_y), run_time=0.9)
        pts_a = cb.puntos_medidos(PARES_PSK8, color=C_BIT, radio=0.065)
        lin_a = poli_ber(cb, PARES_PSK8, C_BIT)
        self.play(Create(lin_a), run_time=1.3)
        self.play(FadeIn(pts_a, scale=0.6), run_time=0.5)
        et_lin_a = tag_hud("8-PSK", font_size=19, color=C_BIT)
        et_lin_a.next_to(cb.en(PARES_PSK8[0][0], PARES_PSK8[0][1]), UR,
                         buff=0.1)
        self.play(FadeIn(et_lin_a), run_time=0.4)
        self.wait(2.8)

        # --- momento: la aprendida, contada -------------------------------
        rot.mostrar(pie_curso("La misma cuenta, mismo ruido y misma "
                              "energía, con la constelación aprendida."),
                    zona="abajo", run_time=0.5)
        pts_b = cb.puntos_medidos(PARES_AE, color=C_IA, radio=0.065)
        lin_b = poli_ber(cb, PARES_AE, C_IA)
        self.play(Create(lin_b), run_time=1.3)
        self.play(FadeIn(pts_b, scale=0.6), run_time=0.5)
        et_lin_b = tag_hud("aprendida", font_size=19, color=C_IA)
        et_lin_b.next_to(cb.en(PARES_AE[-1][0], PARES_AE[-1][1]), RIGHT,
                         buff=0.12)
        self.play(FadeIn(et_lin_b), run_time=0.4)
        self.wait(3.1)

        # --- momento: el veredicto a 10 dB --------------------------------
        rot.mostrar(pie_curso("A diez decibelios la distancia entre las "
                              "dos se lee en el eje."),
                    zona="abajo", run_time=0.5)
        vert = cb.vertical_en(EBN0_SER, color=C_EJE)
        self.play(Create(vert), run_time=0.8)
        lin1 = tag_hud(f"8-PSK      SER = {fmt(SER_PSK8, 4)}",
                       font_size=18, color=C_BIT)
        lin2 = tag_hud(f"aprendida  SER = {fmt(SER_AE, 4)}",
                       font_size=18, color=C_IA)
        lin3 = tag_hud(f"{ERR_PSK8} rotos  vs  {ERR_AE}", font_size=18)
        col = VGroup(lin1, lin2, lin3).arrange(DOWN, buff=0.24,
                                               aligned_edge=LEFT)
        pan = panel_derecha(col)
        self.play(FadeIn(pan), run_time=0.7)
        self.wait(4.0)

        # --- momento: la ganancia MEDIDA ----------------------------------
        rot.mostrar(pie_curso("Menos símbolos rotos sin gastar un vatio "
                              "más ni un hercio más."),
                    zona="abajo", run_time=0.5)
        et_razon = tag_hud(f"{fmt(RAZON_SER, 1)}x menos errores",
                           font_size=22, color=C_COD)
        et_razon.next_to(pan, DOWN, buff=0.4)
        self.play(FadeIn(et_razon, shift=0.14 * UP), run_time=0.6)
        self.play(Indicate(col[2], color=C_COD, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.8)

        # --- momento: donde la ventaja crece ------------------------------
        rot.mostrar(pie_curso("Y este era un canal fácil: con "
                              "amplificadores saturados o fibra no lineal, "
                              "la ventaja crece."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "Cien años dibujando constelaciones.",
            "La red dibujó la suya en mil pasos.",
            "El 6G y el espacio profundo lo investigan hoy.",
            cb, et_y, pts_a, lin_a, et_lin_a, pts_b, lin_b, et_lin_b,
            vert, pan, et_razon)
