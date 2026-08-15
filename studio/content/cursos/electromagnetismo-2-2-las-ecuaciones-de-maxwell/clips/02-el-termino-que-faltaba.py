class Clip2(Scene):
    """2.2.2 - El condensador rompe la ley de Ampere: la corriente se
    corta en el hueco y el lazo da dos respuestas segun la superficie que
    elijas. Maxwell tapa el agujero: entre las placas el campo electrico
    CRECE, y un campo que crece cuenta como corriente. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El término que faltaba")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        con = condensador_ampere()
        # Etiquetas de mobiliario en Space Mono (tag_hud): solo ASCII, de
        # ahi "Ampere" sin acento.
        tag_i = tag_hud("corriente", font_size=17, color=C_CARGA)
        tag_i.next_to(con.flechas_i[0], UP, buff=0.18)
        tag_lazo = tag_hud("lazo de Ampere", font_size=17, color=C_B)
        tag_lazo.next_to(con.lazo, UP, buff=0.16)
        tag_e = tag_hud("E entre placas", font_size=17, color=C_E)
        tag_e.next_to(con.placas, DOWN, buff=0.55)

        # --- momento: la corriente que se corta ---------------------------
        rot.mostrar(pie_curso("La corriente llega a la placa... y se "
                              "corta. Entre las placas no hay hilo."),
                    zona="abajo", run_time=0.5)
        self.play(Create(con.cables), Create(con.placas), run_time=0.8)
        self.play(GrowArrow(con.flechas_i[0]), GrowArrow(con.flechas_i[1]),
                  FadeIn(tag_i), run_time=0.7)
        self.wait(4.6)

        # --- momento: el lazo a caballo del hueco -------------------------
        rot.mostrar(pie_curso("Ampère mide el campo magnético rodeando la "
                              "corriente con un lazo."), zona="abajo",
                    run_time=0.5)
        self.play(Create(con.lazo), FadeIn(tag_lazo), run_time=0.9)
        self.wait(4.6)

        rot.mostrar(pie_curso("Pero este lazo abarca el hueco: por un lado "
                              "pasa corriente, por el otro no. Paradoja."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        # --- momento: el campo que crece ----------------------------------
        # ReplacementTransform + reasignar la variable: la version antigua
        # de las flechas deja de existir en la escena.
        campo_e = con.e_a(0.2)
        rot.mostrar(pie_curso("Maxwell mira dentro del hueco: ahí el campo "
                              "eléctrico está CRECIENDO."), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(campo_e), FadeIn(tag_e), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("Y un campo eléctrico que crece cuenta como "
                              "corriente: la corriente de desplazamiento."),
                    zona="abajo", run_time=0.5)
        crecido = con.e_a(1.0)
        self.play(ReplacementTransform(campo_e, crecido), run_time=1.4)
        campo_e = crecido
        self.wait(4.6)

        # --- momento: la ley completa -------------------------------------
        # MathTex partido en argumentos: el recuadro va sobre el sumando
        # nuevo, no sobre indices de glifo.
        ley = MathTex(r"\oint \vec B\cdot d\vec l", "=", r"\mu_0 I", "+",
                      r"\mu_0\varepsilon_0\,\frac{d\Phi_E}{dt}",
                      font_size=34, color=C_B)
        ley[2].set_color(C_CARGA)
        ley[4].set_color(C_E)
        ley.to_edge(DOWN, buff=MARGEN_PIE)
        marco = SurroundingRectangle(ley[4], color=C_E, buff=0.11,
                                     stroke_width=2.0)
        rot.mostrar(VGroup(ley, marco), zona="abajo", run_time=0.5)
        self.wait(4.8)
