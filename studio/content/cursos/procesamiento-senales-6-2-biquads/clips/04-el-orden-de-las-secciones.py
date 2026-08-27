class Clip4(Scene):
    """6.2.4 - Dentro de la cascada todavia hay que elegir que seccion va
    primero: la mas cerca del circulo, la ultima. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("El orden importa"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        colores = [C_SENAL, C_SALIDA, C_BANDA, C_APREND, C_IDEAL]
        pares = [np.roots([1.0, fila[4], fila[5]]) for fila in SOS]
        radios = [float(abs(par[0])) for par in pares]
        # Pico de cada seccion suelta, medido sobre su propia |H|.
        picos = [float(respuesta_frec(SOS[k][:3], SOS[k][3:], 2048)[1].max())
                 for k in range(N_BIQUADS)]

        def picos_acumulados(orden):
            """El pico de la cascada PARCIAL tras cada seccion: lo que ve
            la seccion siguiente, y lo que puede desbordar."""
            b, a = np.array([1.0]), np.array([1.0])
            salida = []
            for k in orden:
                b = np.convolve(b, SOS[k][:3])
                a = np.convolve(a, SOS[k][3:])
                salida.append(float(respuesta_frec(b, a, 2048)[1].max()))
            return salida

        i_caliente = int(np.argmax([abs(np.roots([1.0, f[4], f[5]])[0])
                                    for f in SOS]))
        orden_bueno = list(range(N_BIQUADS))          # radio creciente
        orden_malo = ([i_caliente]                    # la caliente, primera
                      + [i for i in range(N_BIQUADS) if i != i_caliente])
        acum_bueno = picos_acumulados(orden_bueno)
        acum_malo = picos_acumulados(orden_malo)
        peor_bueno, peor_malo = max(acum_bueno), max(acum_malo)

        # --- las cinco secciones, por radio creciente ---------------------
        ranuras = [np.array([-5.0 + 2.5 * i, 1.85, 0.0])
                   for i in range(N_BIQUADS)]
        cajas = VGroup()
        for i in range(N_BIQUADS):
            c = bloque(f"{radios[i]:.4f}", ancho=2.0, alto=0.70,
                       color=colores[i], color_texto=colores[i], tamano=24)
            c.move_to(ranuras[i])
            cajas.add(c)
        flechas = VGroup(*[conectar(cajas[i], cajas[i + 1], color=C_DATO,
                                    grosor=2.2, margen=0.08)
                           for i in range(N_BIQUADS - 1)])
        for f in flechas:
            f.tip.scale(2.0)
        self.play(LaggedStart(*[FadeIn(c) for c in cajas], lag_ratio=0.14),
                  run_time=1.4)
        self.play(LaggedStart(*[Create(f) for f in flechas],
                              lag_ratio=0.18), run_time=0.8)
        rot.mostrar(cifra_pie("radio de cada seccion"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        # --- la que mas amplifica -----------------------------------------
        self.play(Indicate(cajas[i_caliente], scale_factor=1.12,
                           color=colores[i_caliente]), run_time=0.8)
        self.play(cajas[i_caliente][0].animate.set_stroke(width=5.0),
                  run_time=0.4)
        rot.mostrar(cifra_pie(f"r {radios[i_caliente]:.4f}: pico "
                              f"{picos[i_caliente]:+.2f} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(1.8)

        # --- lo que ve cada etapa: el pico acumulado ----------------------
        Y0, Y1, ALTO = -130.0, 80.0, 2.6
        bar = barras(acum_bueno, ancho=6.0, alto=ALTO, color=C_CALCULO,
                     rango_y=(Y0, Y1))
        bar.move_to(np.array([-1.5, -1.35, 0.0]))
        base = bar.barra(0).get_bottom()[1]

        def y_db(v):
            return base + (v - Y0) / (Y1 - Y0) * ALTO

        izq, der = bar.get_left()[0], bar.get_right()[0]
        linea0 = DashedLine(np.array([izq, y_db(0.0), 0.0]),
                            np.array([der, y_db(0.0), 0.0]), color=C_RUIDO,
                            stroke_width=1.8, dash_length=0.08)
        et_0 = tag_hud("0 dB", font_size=19, color=C_RUIDO)
        et_0.next_to(linea0.get_end(), RIGHT, buff=0.14)
        et_bar = tag_hud("tras cada seccion", font_size=18, color=C_DATO)
        et_bar.next_to(bar, DOWN, buff=0.20)
        self.play(FadeIn(bar.ejes), FadeIn(et_bar), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(b) for b in bar.barras],
                              lag_ratio=0.18), run_time=1.6)
        self.play(Create(linea0), FadeIn(et_0), run_time=0.6)
        rot.mostrar(cifra_pie(f"pico acumulado {peor_bueno:+.2f} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- al reves: la caliente, primero -------------------------------
        # La caliente viaja por DEBAJO de la fila: si las cinco cajas se
        # cruzasen por el mismo carril, medio segundo hay cinco encimadas.
        VIA = 0.95
        caliente = cajas[i_caliente]
        rot.mostrar(cifra_pie(f"primero r {radios[i_caliente]:.4f}"),
                    zona="abajo", run_time=0.5)
        self.play(caliente.animate.move_to(
            np.array([ranuras[i_caliente][0], VIA, 0.0])), run_time=0.45)
        self.play(caliente.animate.move_to(
                      np.array([ranuras[0][0], VIA, 0.0])),
                  *[cajas[i].animate.move_to(ranuras[i + 1])
                    for i in range(N_BIQUADS) if i != i_caliente],
                  run_time=1.1)
        self.play(caliente.animate.move_to(ranuras[0]), run_time=0.45)
        self.wait(1.2)

        gem = bar.con_valores(acum_malo)
        for i, v in enumerate(acum_malo):
            if v > 0.0:
                gem.barra(i).set_color(C_RUIDO)
        rot.mostrar(cifra_pie(f"pico acumulado {peor_malo:+.2f} dB"),
                    zona="abajo", run_time=0.5)
        self.play(Transform(bar.barras, gem.barras), run_time=1.3)
        self.wait(2.2)

        panel = panel_cifras((f"por radio {peor_bueno:+.2f} dB", C_CALCULO),
                             (f"caliente primero {peor_malo:+.2f} dB", C_RUIDO),
                             desplazar=DOWN * 1.95)
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.2)

        # --- y de vuelta al orden que no desborda -------------------------
        vuelta = bar.con_valores(acum_bueno)
        rot.mostrar(cifra_pie(f"por radio {peor_bueno:+.2f} dB"),
                    zona="abajo", run_time=0.5)
        self.play(caliente.animate.move_to(
            np.array([ranuras[0][0], VIA, 0.0])), run_time=0.45)
        self.play(caliente.animate.move_to(
                      np.array([ranuras[i_caliente][0], VIA, 0.0])),
                  *[cajas[i].animate.move_to(ranuras[i])
                    for i in range(N_BIQUADS) if i != i_caliente],
                  Transform(bar.barras, vuelta.barras), run_time=1.2)
        self.play(caliente.animate.move_to(ranuras[i_caliente]),
                  run_time=0.45)
        self.wait(2.0)

        cierre_leccion(self, rot, "Un filtro no es su ecuacion.",
                       "Es como se calcula.",
                       cajas, flechas, bar, linea0, et_0, et_bar, panel)
