class Clip4(Scene):
    """4 - Sumar dos ondas. Dos ondas en fase se refuerzan, en oposicion
    se cancelan; entre medias la suma delata la fase: eso es lo que se
    mide. Cierra con la frase doble del hilo. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Sumar dos ondas"), zona="arriba",
                    run_time=0.6)

        suma = suma_ondas(fase=0.0, ancho=5.2, n_periodos=3, amplitud=0.34)

        # --- momento 1: en fase se refuerzan --------------------------------------
        rot.mostrar(pie_curso("Dos ondas de la misma luz se suman punto "
                              "a punto."), zona="abajo")
        self.play(FadeIn(suma), run_time=1.0)
        tag_refuerza = tag_hud("en fase: se refuerzan", font_size=17)
        tag_refuerza.next_to(suma.ejes[2], RIGHT, buff=0.3)
        self.play(FadeIn(tag_refuerza), run_time=0.4)
        self.wait(5.5)

        # --- momento 2: en oposicion se cancelan ------------------------------------
        rot.mostrar(pie_curso("Si una llega media longitud de onda "
                              "tarde, se cancelan."), zona="abajo")
        self.play(FadeOut(tag_refuerza), run_time=0.3)
        fase_t = ValueTracker(0.0)
        avanza = lambda o: o.a_fase(fase_t.get_value())
        suma.add_updater(avanza)
        self.play(fase_t.animate.set_value(math.pi), run_time=1.5,
                  rate_func=linear)
        suma.remove_updater(avanza)
        tag_cancela = tag_hud("en oposicion: se cancelan", font_size=17)
        tag_cancela.next_to(suma.ejes[2], RIGHT, buff=0.3)
        self.play(FadeIn(tag_cancela), run_time=0.4)
        self.wait(4.5)

        # --- momento 3: la suma delata la fase ---------------------------------------
        rot.mostrar(pie_curso("Entre medias, la suma delata la fase: "
                              "eso es lo que se mide."), zona="abajo")
        self.play(FadeOut(tag_cancela), run_time=0.3)
        avanza2 = lambda o: o.a_fase(fase_t.get_value())
        suma.add_updater(avanza2)
        self.play(fase_t.animate.set_value(math.pi + 2 * math.pi),
                  run_time=4.5, rate_func=linear)
        suma.remove_updater(avanza2)
        self.wait(2.0)

        # --- cierre a pantalla limpia -------------------------------------------------
        rot.limpiar(run_time=0.4)
        self.play(FadeOut(modulo), FadeOut(suma), run_time=0.6)
        frase1 = Text("La luz no se mide con la luz.", font_size=40,
                      color=C_TITULO)
        frase2 = Text("Se mide con su fase.", font_size=44, color=C_ONDA)
        grupo_final = VGroup(frase1, frase2).arrange(DOWN, buff=0.4)
        grupo_final.move_to(ORIGIN)
        self.play(FadeIn(grupo_final, shift=0.15 * UP), run_time=0.8)
        self.wait(6.5)
