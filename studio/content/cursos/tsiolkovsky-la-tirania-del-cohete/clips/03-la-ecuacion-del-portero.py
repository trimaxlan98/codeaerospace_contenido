class Clip3(Scene):
    """3 - La ecuacion del portero. Tsiolkovsky, 1903: la ecuacion sola
    en pantalla y sus tres terminos encendidos uno a uno con su tag —
    lo que quieres (cian), lo que tu quimica da (ambar), lo que te cobra
    (rojo). Cierra con la cifra a LEO. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La ecuación del portero")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: 1903, la ecuacion aparece -----------------------------
        rot.mostrar(pie_curso("1903. Un maestro de escuela sordo escribe "
                              "la ecuación que decide quién sube."),
                    zona="abajo", run_time=0.5)
        ecuacion = MathTex(r"\Delta v", "=", r"v_e",
                           r"\ln\!\frac{m_0}{m_f}", font_size=64,
                           color=C_TITULO)
        ecuacion.move_to(UP * 0.15)
        self.play(Write(ecuacion), run_time=2.6)
        self.wait(2.6)

        # --- momento: lo que quieres (delta v) ------------------------------
        rot.mostrar(pie_curso("A la izquierda, lo que quieres: la "
                              "velocidad que hay que ganar."),
                    zona="abajo", run_time=0.5)
        tag_dv = tag_junto(ecuacion, "lo que quieres", UP, buff=0.34,
                           font_size=20, color=C_CARGA)
        tag_dv.set_x(ecuacion[0].get_center()[0])
        self.play(Indicate(ecuacion[0], color=C_CARGA, scale_factor=1.18),
                  run_time=0.9)
        self.play(ecuacion[0].animate.set_color(C_CARGA),
                  FadeIn(tag_dv, shift=0.12 * UP), run_time=0.5)
        self.wait(3.5)

        # --- momento: lo que tu quimica da (v_e) ----------------------------
        rot.mostrar(pie_curso("En el centro, lo que tu química da: la "
                              "velocidad a la que sale el gas."),
                    zona="abajo", run_time=0.5)
        tag_ve = tag_junto(ecuacion, "lo que tu química da", DOWN,
                           buff=0.34, font_size=20, color=C_PROPELENTE)
        tag_ve.set_x(ecuacion[2].get_center()[0])
        self.play(Indicate(ecuacion[2], color=C_PROPELENTE,
                           scale_factor=1.18), run_time=0.9)
        self.play(ecuacion[2].animate.set_color(C_PROPELENTE),
                  FadeIn(tag_ve, shift=0.12 * UP), run_time=0.5)
        self.wait(3.5)

        # --- momento: lo que te cobra (el logaritmo) ------------------------
        rot.mostrar(pie_curso("Y al final, lo que te cobra: el logaritmo "
                              "de cuánto pesabas entre cuánto quedas."),
                    zona="abajo", run_time=0.5)
        tag_log = tag_junto(ecuacion, "lo que te cobra", UP, buff=0.34,
                            font_size=20, color=C_MUERTO)
        tag_log.set_x(ecuacion[3].get_center()[0])
        self.play(Indicate(ecuacion[3], color=C_MUERTO, scale_factor=1.12),
                  run_time=0.9)
        self.play(ecuacion[3].animate.set_color(C_MUERTO),
                  FadeIn(tag_log, shift=0.12 * UP), run_time=0.5)
        self.wait(3.5)

        # --- momento: el portero y su tarifa --------------------------------
        rot.mostrar(pie_curso("Es el portero de la órbita: nadie sube sin "
                              "pagarle."), zona="abajo", run_time=0.5)
        cifra = tag_hud(f"a LEO: m0/mf = {RAZON_QUIMICO:.1f}", font_size=20)
        cifra.next_to(tag_ve, DOWN, buff=0.42)
        cifra.set_x(ecuacion.get_center()[0])
        self.play(FadeIn(cifra, shift=0.14 * UP), run_time=0.6)
        self.wait(5.6)
