class Clip4(Scene):
    """4 - Picometros entre tres naves. LISA: triangulo de 2.5 millones de
    km (8.3 s de luz) donde una onda gravitacional estira un brazo y
    encoge otro. 1 pm en 2.5e6 km son 4e-22: la medida mas fina jamas
    intentada. Cierra la familia: la luz, de regla del taller a regla del
    universo. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Picómetros entre tres naves"),
                    zona="arriba", run_time=0.6)

        # 6.56 x 4.62 al 0.92 -> 6.04 x 4.25, centrado en y = -0.25.
        # `rotulo_brazo` ya trae "2.5 millones km" y "8.3 s de luz"; la
        # onda y el rotulo del delta entran en el momento 2.
        lisa = triangulo_lisa(h=0.0, lado=4.2)
        lisa.scale(0.92).move_to(DOWN * 0.25)
        lisa.remove(lisa.onda, lisa.rotulo_delta, lisa.brazos,
                    lisa.rotulo_brazo)

        def estirar(amplitud, ciclos, t, fase0=0.0):
            """Oscila h como una onda que pasa: h(a) = A sen(f0 + 2 pi n a).

            Los tramos SIEMPRE acaban en una cresta (no en el cruce por
            cero): el rotulo de la pieza escribe la h con `:.1e` y en el
            cruce el float residual saldria como "4.4e-37".
            """
            self.play(UpdateFromAlphaFunc(
                lisa, lambda m, a: m.a_estiramiento(
                    amplitud * math.sin(fase0 + TAU * ciclos * a))),
                run_time=t, rate_func=linear)

        # --- momento: tres naves en triangulo --------------------------
        rot.mostrar(pie_curso("LISA: tres naves en triángulo, brazos de 2.5 "
                              "millones de kilómetros."), zona="abajo")
        self.play(FadeIn(lisa, shift=0.12 * UP), run_time=0.8)
        lisa.add(lisa.brazos)
        self.play(Create(lisa.brazos), run_time=1.1)
        lisa.add(lisa.rotulo_brazo)
        self.play(FadeIn(lisa.rotulo_brazo), run_time=0.6)
        self.wait(3.4)

        # --- momento: la onda estira un brazo --------------------------
        rot.mostrar(pie_curso("Una onda gravitacional estira un brazo y "
                              "encoge otro: picómetros."), zona="abajo")
        lisa.add(lisa.onda)
        lisa.a_estiramiento(0.0)        # repone el rotulo del delta en h = 0
        self.play(FadeIn(lisa.onda, shift=np.array([0.55, -0.40, 0.0])),
                  FadeIn(lisa.rotulo_delta), run_time=0.8)
        # Columna izquierda: los tags se alinean por su borde DERECHO en
        # x = -3.10, libre a esa altura (lo mas saliente del triangulo por
        # ahi son los arcos de la onda, en x = -2.48).
        aviso = tag_hud("estiramiento exagerado", font_size=13, color=C_TENUE)
        aviso.move_to(np.array([-3.10, 1.45, 0.0]), aligned_edge=RIGHT)
        self.play(FadeIn(aviso), run_time=0.45)
        estirar(1.2e-21, 1.25, 4.6)     # acaba en la cresta: +3.00 pm
        self.wait(1.6)

        # --- momento: la cifra -----------------------------------------
        rot.mostrar(pie_curso("Un picómetro en 2.5 millones de kilómetros: "
                              "la medida más fina jamás intentada."),
                    zona="abajo")
        cifras = VGroup(
            tag_hud(f"1 pm / 2.5e6 km = {SENS_LISA:.0e}", font_size=15,
                    color=C_MEDIDA),
            tag_hud("orden de magnitud;", font_size=13, color=C_TENUE),
            tag_hud("lanzamiento ~2035", font_size=13, color=C_TENUE),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        cifras.move_to(np.array([-3.10, 0.25, 0.0]), aligned_edge=RIGHT)
        self.play(FadeIn(cifras), run_time=0.6)
        estirar(1.2e-21, 1.0, 3.0, fase0=PI / 2)   # sigue desde la cresta
        self.wait(2.6)

        # --- cierre a pantalla limpia ----------------------------------
        rot.limpiar(run_time=0.45)
        self.play(FadeOut(lisa), FadeOut(aviso), FadeOut(cifras),
                  run_time=0.7)
        frase_1 = Text("La luz fue la regla del taller.", font_size=36,
                       color=C_ONDA)
        frase_2 = Text("Ahora es la regla del universo.", font_size=36,
                       color=C_ONDA)
        cierre = VGroup(frase_1, frase_2).arrange(DOWN, buff=0.50)
        cierre.move_to(ORIGIN)
        self.play(FadeIn(frase_1, shift=0.14 * UP), run_time=0.9)
        self.wait(1.5)
        self.play(FadeIn(frase_2, shift=0.14 * UP), run_time=0.9)
        self.wait(5.0)
