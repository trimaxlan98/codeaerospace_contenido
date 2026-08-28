class Clip3(Scene):
    """7.3.3 - La convolucion por bloques con FFT (overlap-add) da
    exactamente lo mismo que la directa: error 3.3e-16, no una
    aproximacion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 07"))
        rot.mostrar(titulo_curso("La convolucion rapida"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la señal larga, como curva (no tallos) --------------------------
        t = np.arange(len(X_LARGA))
        on = onda(t, X_LARGA, ancho=10.2, alto=2.0, color=C_SENAL)
        on.move_to(UP * 1.55)
        et_on = tag_hud(f"{len(X_LARGA)} muestras", font_size=18,
                        color=C_TENUE)
        et_on.next_to(on, UP, buff=0.22)
        self.play(Create(on.curva), FadeIn(on.ejes), FadeIn(et_on),
                  run_time=1.8)
        self.wait(1.6)

        # --- partir en bloques de 64 -----------------------------------------
        L = 64
        cortes = list(range(L, len(X_LARGA), L))
        lineas = VGroup(*[on.vertical_en(c, color=C_MUESTRA)
                          for c in cortes])
        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.08),
                  run_time=2.0)
        rot.mostrar(cifra_pie(f"bloques de {L}"), zona="abajo",
                    run_time=0.45)
        self.wait(2.4)

        # --- un bloque y la cola que se solapa con el siguiente --------------
        i0 = 128
        x_i0 = on.en(i0, 0)[0]
        x_i1 = on.en(i0 + L, 0)[0]
        x_i2 = on.en(i0 + L + N_TAPS - 1, 0)[0]
        y_base = on.en(0, 0)[1]
        ventana = Rectangle(width=x_i1 - x_i0, height=on.alto,
                            stroke_width=1.2, stroke_color=C_CALCULO,
                            fill_color=C_CALCULO, fill_opacity=0.16)
        ventana.move_to(np.array([(x_i0 + x_i1) / 2, y_base, 0]))
        et_v = tag_junto(ventana, "bloque", direccion=DOWN, color=C_CALCULO)
        self.play(FadeIn(ventana), FadeIn(et_v), run_time=0.7)
        self.wait(1.8)

        cola = Rectangle(width=x_i2 - x_i1, height=on.alto * 0.6,
                         stroke_width=1.0, stroke_color=C_SALIDA,
                         fill_color=C_SALIDA, fill_opacity=0.22)
        cola.move_to(np.array([(x_i1 + x_i2) / 2, y_base, 0]))
        et_c = tag_junto(cola, "cola suma", direccion=DOWN, color=C_SALIDA)
        self.play(FadeIn(cola), FadeIn(et_c), run_time=0.7)
        self.wait(2.4)
        self.play(FadeOut(ventana), FadeOut(et_v), FadeOut(cola),
                  FadeOut(et_c), FadeOut(lineas), FadeOut(on), FadeOut(et_on),
                  run_time=0.6)

        # --- las dos salidas, superpuestas: son la MISMA ---------------------
        tc = np.arange(len(Y_DIRECTA))
        base = onda(tc, Y_DIRECTA, ancho=10.2, alto=2.4, color=C_IDEAL)
        base.move_to(DOWN * 0.35)
        et_base = tag_hud("directa", font_size=17, color=C_IDEAL)
        et_base.next_to(base, UP, buff=0.20).align_to(base, LEFT)
        self.play(Create(base.curva), FadeIn(base.ejes), FadeIn(et_base),
                  run_time=1.6)
        self.wait(1.4)

        oa = base.curva_de(tc, Y_OA, color=C_CALCULO, grosor=3.4)
        et_oa = tag_hud("overlap-add", font_size=17, color=C_CALCULO)
        et_oa.next_to(et_base, RIGHT, buff=0.5)
        self.play(Create(oa), FadeIn(et_oa), run_time=1.6)
        rot.mostrar(cifra_pie(f"error {ERR_OA:.1e}"), zona="abajo",
                    run_time=0.5)
        self.wait(9.4)
