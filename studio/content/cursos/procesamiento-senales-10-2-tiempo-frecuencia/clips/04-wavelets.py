class Clip4(Scene):
    """10.2.4 - La otra manera: en vez de una ventana fija, una que se
    encoge al subir de frecuencia. Los tres niveles de Haar, alineados
    por TIEMPO, cada uno con la mitad de coeficientes. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Wavelets"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        ancho = 8.6
        desp = LEFT * 0.7
        alturas = (UP * 1.88, UP * 0.36, DOWN * 1.16)
        radios = (0.006, 0.010, 0.016)
        grosores = (1.0, 1.2, 1.5)
        # Misma caja de valores para los tres: si cada nivel se autoescala,
        # la comparacion de amplitudes miente.
        m = float(max(np.max(np.abs(d)) for d in DETALLES)) * 1.15

        niveles, etiquetas = [], []
        for i, d in enumerate(DETALLES):
            sec = Secuencia(d, 0, (-m, m), ancho=ancho, alto=1.05,
                            color=C_MUESTRA, radio=radios[i],
                            grosor=grosores[i], eje_y=False)
            sec.move_to(alturas[i] + desp)
            et = tag_hud(f"{LARGOS_DET[i]} coef", font_size=19,
                         color=C_MUESTRA)
            et.next_to(sec, LEFT, buff=0.22)
            niveles.append(sec)
            etiquetas.append(et)

        for i, sec in enumerate(niveles):
            self.play(FadeIn(sec), FadeIn(etiquetas[i]), run_time=0.9)
            rot.mostrar(
                cifra_pie(f"nivel {i + 1}: {LARGOS_DET[i]} coeficientes"),
                zona="abajo", run_time=0.5)
            self.wait(1.7)

        # --- el mismo instante en los tres: se alinean por TIEMPO ---------
        verticales = VGroup(*[
            niveles[i].vertical_en(POS_GOLPE / N_TF * LARGOS_DET[i],
                                   color=C_CALCULO)
            for i in range(len(niveles))])
        self.play(LaggedStart(*[Create(v) for v in verticales],
                              lag_ratio=0.35), run_time=1.2)
        rot.mostrar(cifra_pie(f"golpe en n = {POS_GOLPE}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        # --- 32 coeficientes: cuanto tiempo abarcan en cada nivel ---------
        m_coef = 32
        ventanas = VGroup()
        for i, sec in enumerate(niveles):
            a = int(0.08 * LARGOS_DET[i])
            ventanas.add(sec.ventana(a, a + m_coef - 1, color=C_SALIDA,
                                     opacidad=0.22))
        et_v = tag_hud(f"{m_coef} coeficientes", font_size=19,
                       color=C_SALIDA)
        et_v.next_to(ventanas[0], UP, buff=0.14)
        self.play(LaggedStart(*[Create(v) for v in ventanas],
                              lag_ratio=0.4), FadeIn(et_v), run_time=1.5)
        rot.mostrar(cifra_pie("la ventana se encoge", color=C_SALIDA),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras(
            *[(f"{LARGOS_DET[i]}  E {fmt(ENERGIA_DET[i], 1)}", C_CALCULO)
              for i in range(len(DETALLES))])
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)

        cierre_leccion(self, rot, "No hay ventana buena.",
                       "Hay ventana elegida.",
                       *niveles, *etiquetas, verticales, ventanas, et_v,
                       panel)
