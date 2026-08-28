class Clip1(Scene):
    """8.3.1 - Pasar de 8000 a 6000 Hz es multiplicar por 3/4: interpolar
    por L, filtrar, diezmar por M. Las dos senales se alinean por TIEMPO,
    no por indice: tienen distinto numero de muestras. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("L sobre M"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la cadena de tres pasos --------------------------------------
        b1 = bloque("interpolar", ancho=2.4, alto=0.82, color=C_MUESTRA,
                    tamano=26)
        b2 = bloque("filtrar", ancho=2.4, alto=0.82, color=C_CALCULO,
                    tamano=26)
        b3 = bloque("diezmar", ancho=2.4, alto=0.82, color=C_SALIDA,
                    tamano=26)
        cadena = VGroup(b1, b2, b3).arrange(RIGHT, buff=1.05)
        cadena.move_to(UP * 2.35)
        cx1 = conectar(b1, b2)
        cx2 = conectar(b2, b3)
        et1 = tag_hud(f"x {L_R}", font_size=21, color=C_MUESTRA)
        et1.next_to(b1, DOWN, buff=0.15)
        et3 = tag_hud(f"/ {M_R}", font_size=21, color=C_SALIDA)
        et3.next_to(b3, DOWN, buff=0.15)
        self.play(LaggedStart(FadeIn(b1), FadeIn(b2), FadeIn(b3),
                              lag_ratio=0.4), run_time=1.4)
        self.play(Create(cx1), Create(cx2), run_time=0.7)
        self.play(FadeIn(et1), FadeIn(et3), run_time=0.5)
        rot.mostrar(cifra_pie(f"L = {L_R}   M = {M_R}"), zona="abajo",
                    run_time=0.5)
        self.play(flujo([cx1, cx2]), run_time=1.2)
        self.wait(1.4)

        # --- la entrada y la salida, en CARRILES ALINEADOS POR TIEMPO -----
        # 48 muestras a 8000 Hz y 36 a 6000 Hz duran lo mismo (6 ms): por
        # eso las dos cajas llevan el MISMO ancho y distinto numero de
        # tallos. El desfase de 8 muestras es el retardo del FIR.
        n_x, n_y = 48, 36
        sec_x = Secuencia(X_R[:n_x], 0, (-1.35, 1.35), ancho=8.8, alto=1.4,
                          color=C_MUESTRA, radio=0.036)
        sec_x.move_to(UP * 0.42)
        et_x = tag_hud(f"{FS_R:.0f} Hz   {len(X_R)}", font_size=19,
                       color=C_MUESTRA)
        et_x.next_to(sec_x, UP, buff=0.10).align_to(sec_x, LEFT)
        sec_y = Secuencia(Y_R[8:8 + n_y], 0, (-1.35, 1.35), ancho=8.8,
                          alto=1.4, color=C_SALIDA, radio=0.036)
        sec_y.move_to(DOWN * 1.72)
        et_y = tag_hud(f"{FS_SALIDA:.0f} Hz   {len(Y_R)}", font_size=19,
                       color=C_SALIDA)
        et_y.next_to(sec_y, UP, buff=0.10).align_to(sec_y, LEFT)

        self.play(FadeIn(sec_x), FadeIn(et_x), run_time=0.9)
        self.wait(1.1)

        # --- que hace cada caja, con su cuenta ----------------------------
        for caja, texto in ((b1, f"x {L_R}: {len(X_R) * L_R} muestras"),
                            (b2, f"filtra a {FS_R * L_R:.0f} Hz"),
                            (b3, f"/ {M_R}: {len(Y_R)} muestras")):
            rot.mostrar(cifra_pie(texto), zona="abajo", run_time=0.45)
            self.play(Indicate(caja, scale_factor=1.08, color=C_CALCULO),
                      run_time=0.8)
            self.wait(1.6)

        rot.mostrar(cifra_pie(f"{len(X_R)} entran {len(Y_R)} salen"),
                    zona="abajo", run_time=0.45)
        self.play(FadeIn(sec_y), FadeIn(et_y), run_time=0.9)
        self.wait(2.2)

        # --- el mismo instante en las dos: alineadas por tiempo -----------
        marcas = VGroup()
        for n_a, n_b in ((11.5, 8.5), (23.5, 17.5), (35.5, 26.5)):
            x_a = sec_x.en(n_a, 0.0)[0]
            marcas.add(DashedLine(np.array([x_a, sec_x.en(0, 1.35)[1], 0.0]),
                                  np.array([x_a, sec_y.en(0, -1.35)[1], 0.0]),
                                  color=C_CALCULO, stroke_width=1.5,
                                  dash_length=0.09))
            assert abs(x_a - sec_y.en(n_b, 0.0)[0]) < 1e-9
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.3),
                  run_time=1.1)
        rot.mostrar(cifra_pie("mismo tiempo   otro indice"), zona="abajo",
                    run_time=0.45)
        self.wait(3.0)

        self.play(flujo([cx1, cx2]), run_time=1.2)
        rot.mostrar(formula_pie(rf"f_s' = \frac{{{L_R}}}{{{M_R}}}\, f_s "
                                rf"= {FS_SALIDA:.0f}\ \mathrm{{Hz}}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
