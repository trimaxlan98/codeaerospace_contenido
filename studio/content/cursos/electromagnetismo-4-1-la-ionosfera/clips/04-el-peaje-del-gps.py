class Clip4(Scene):
    """4.1.4 - El peaje del GPS: el mismo techo que refleja la HF frena
    un poquito las portadoras que sí lo cruzan. El retardo depende de
    la frecuencia, así que DOS frecuencias delatan el TEC y el receptor
    se cobra el peaje de vuelta. Cierra la lección. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El peaje del GPS")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el peaje que nadie ve -----------------------------------
        rot.mostrar(pie_curso("La señal del GPS cruza la ionosfera, "
                              "pero no gratis: sale un poco retrasada."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        bar = barras_retardo(tec=TEC_GPS)
        bar.move_to(DOWN * 0.3)
        self.play(FadeIn(bar.suelo), run_time=0.4)
        self.wait(0.4)

        # --- momento: L1 --------------------------------------------------------
        rot.mostrar(pie_curso("A cincuenta TECU, un día tranquilo, L1 "
                              "arrastra ocho metros de camino extra."),
                    zona="abajo", run_time=0.5)
        tag_l1 = tag_hud(f"L1: {RETARDO_L1:.1f} m", font_size=17)
        tag_l1.next_to(bar.barra(0), UP, buff=0.14)
        self.play(GrowFromEdge(bar.barra(0), DOWN), FadeIn(bar.etiquetas[0]),
                  FadeIn(tag_l1, shift=0.1 * DOWN), run_time=1.0)
        self.wait(4.4)

        # --- momento: L2 --------------------------------------------------------
        rot.mostrar(pie_curso("L2 va más lenta: paga trece metros y "
                              "medio. Más grave, más retardo."),
                    zona="abajo", run_time=0.5)
        tag_l2 = tag_hud(f"L2: {RETARDO_L2:.1f} m", font_size=17)
        tag_l2.next_to(bar.barra(1), UP, buff=0.14)
        self.play(GrowFromEdge(bar.barra(1), DOWN), FadeIn(bar.etiquetas[1]),
                  FadeIn(tag_l2, shift=0.1 * DOWN), run_time=1.0)
        self.wait(4.4)

        rot.mostrar(formula_pie(r"d \propto \frac{TEC}{f^2}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: el truco de las dos monedas -----------------------------
        rot.mostrar(pie_curso("El truco: el retardo depende de la "
                              "frecuencia. De la diferencia entre las "
                              "barras, el receptor despeja el TEC y "
                              "cancela el peaje él solo."), zona="abajo",
                    run_time=0.5)
        llave_dif = llave(VGroup(tag_l1, tag_l2),
                          "delata el TEC", direccion=UP, font_size=18)
        self.play(FadeIn(llave_dif), run_time=0.8)
        self.wait(4.8)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(bar), FadeOut(tag_l1), FadeOut(tag_l2),
                  FadeOut(llave_dif), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("La ionosfera cobra peaje.", font_size=40,
                      color=C_TITULO)
        linea2 = Text("El GPS paga con dos monedas.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("El techo eléctrico ya es tuyo: ahora hay "
                              "que llegar hasta el satélite mismo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)
