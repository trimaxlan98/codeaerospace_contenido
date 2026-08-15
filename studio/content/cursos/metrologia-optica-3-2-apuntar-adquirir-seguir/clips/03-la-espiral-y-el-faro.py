class Clip3(Scene):
    """3 - La espiral y el faro. Nadie sabe donde esta el otro: una region de
    incertidumbre. El haz la barre en espiral (72 pasos, cada vuelta pegada a
    la anterior) hasta que en el paso 46 -MEDIDO recorriendo la espiral- cubre
    el faro del otro satelite, que responde. Simulacion determinista: pura
    geometria, sin ruido de apuntado ni deriva orbital. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("La espiral y el faro"), zona="arriba",
                    run_time=0.6)

        # La pieza mide 5.2 x 5.4: escalada a 0.78 deja sitio al titulo y al
        # pie, y corrida a la izquierda deja libre la columna de cifras.
        esp = espiral_adquisicion()
        esp.scale(0.78)
        esp.move_to(LEFT * 1.55 + DOWN * 0.05)
        # Nace con la espiral COMPLETA: se retrocede al paso 0 y se apagan la
        # traza, el haz y el rotulo (el faro entra tenue: aun no lo han visto).
        esp.a_paso(0)
        esp.haz.set_opacity(0.0)
        esp.traza.set_opacity(0.0)
        esp.puntos_vista.set_opacity(0.0)
        esp.rotulo.set_opacity(0.0)
        esp.faro.set_opacity(0.30)

        def cifra(texto, y, color=None, font_size=16):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(np.array([1.55, y, 0.0]), aligned_edge=LEFT)
            return t

        # --- momento: la region de incertidumbre -------------------------------
        rot.mostrar(pie_curso("Al principio ninguno sabe exactamente dónde "
                              "está el otro: una región de incertidumbre."),
                    zona="abajo")
        self.play(FadeIn(esp), run_time=0.9)
        et_region = tag_junto(esp.region, "región de incertidumbre", UP,
                              buff=0.18, font_size=18)
        self.play(FadeIn(et_region), run_time=0.4)
        self.wait(4.3)

        # --- momento: el barrido ------------------------------------------------
        rot.mostrar(pie_curso("Uno barre la región en espiral con un haz "
                              "ancho, esperando que el otro lo vea."),
                    zona="abajo")
        self.play(esp.haz.animate.set_stroke(opacity=1.0).set_fill(
            opacity=0.18), run_time=0.4)
        # `a_paso` MUTA (recorta la traza y rehace el rotulo): ValueTracker, y
        # el updater se limpia al terminar el barrido. Se para UN paso antes
        # del encuentro para que el faro se encienda en su momento.
        k_enc = esp.k_encuentro
        paso = ValueTracker(0.0)
        esp.traza.set_stroke(opacity=1.0)
        def _barrer(m):
            # El renderer congela la lista de mobjects "en movimiento" al
            # empezar el play: el rotulo que `a_paso` SUSTITUYE se seguiria
            # dibujando encima del nuevo. Se apaga al relevarlo.
            viejo = m.rotulo
            m.a_paso(int(paso.get_value()))
            viejo.set_opacity(0.0)

        esp.add_updater(_barrer)
        self.play(paso.animate.set_value(k_enc - 1), run_time=5.0,
                  rate_func=linear)
        esp.clear_updaters()
        esp.a_paso(k_enc - 1)
        self.wait(1.4)

        # --- momento: la espiral no deja huecos ---------------------------------
        rot.mostrar(pie_curso("Cada vuelta se pega a la anterior: el haz no "
                              "deja huecos por donde escaparse."),
                    zona="abajo")
        t_pasos = cifra(f"{esp.n_puntos - 1} pasos de barrido", 1.30)
        t_sim = cifra("simulacion", 0.62, color=C_TENUE, font_size=14)
        self.play(FadeIn(t_pasos), FadeIn(t_sim), run_time=0.5)
        self.wait(4.7)

        # --- momento: el faro responde -------------------------------------------
        rot.mostrar(pie_curso("Cuando el faro lo ilumina, el otro responde: "
                              "los dos se han encontrado."), zona="abajo")
        esp.a_paso(k_enc)
        self.play(esp.faro.animate.set_opacity(1.0),
                  Flash(esp.faro, color=C_OBJETO, line_length=0.22,
                        num_lines=16, flash_radius=0.42), run_time=0.9)
        vuelta = Line(esp.faro[0].get_center(), esp.punto(0),
                      stroke_width=2.4, color=C_OBJETO)
        vuelta.set_stroke(opacity=0.85)
        self.play(Create(vuelta), run_time=0.8)
        t_enc = cifra(f"encuentro en el paso {k_enc}", -0.10, color=C_OBJETO)
        self.play(FadeIn(t_enc), run_time=0.4)
        self.wait(3.6)

        # --- cierre ----------------------------------------------------------------
        rot.mostrar(pie_curso("Adquirir es un ritual de segundos que decide "
                              "todo el enlace."), zona="abajo")
        self.wait(5.0)
