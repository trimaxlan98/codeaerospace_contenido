class Clip2(Scene):
    """2 - Empujar tirando masa. En el vacio no hay contra que apoyarse: el
    unico empuje posible es tirar masa. El patinador lanza tres bolas y
    retrocede 0.769 m/s con la primera; cada bola sale mas lenta en el
    hielo y el queda mas rapido, porque pesa menos. Un cohete es eso, con
    gas a 3.5 km/s. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Empujar tirando masa")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # Geometria del clip: el hielo bajo el eje (y = -0.45) y largo para
        # que las bolas lanzadas sigan sobre el al final; el patinador acaba
        # en x = +1.72 y sus cifras se apilan encima de el, ya en su sitio
        # final. Todo en la banda central.
        pat = patinador(metros_a_escena=0.32, largo=13.0)
        pat.shift(DOWN * 0.45)

        # --- momento: no hay contra que empujar ----------------------------
        rot.mostrar(pie_curso("En el espacio no hay nada contra qué "
                              "empujar."), zona="abajo", run_time=0.5)
        self.play(Create(pat.hielo), run_time=0.9)
        t_hielo = tag_junto(pat.hielo, "hielo sin fricción", DOWN, buff=0.24,
                            font_size=16)
        self.play(FadeIn(pat.cuerpo, scale=0.6), FadeIn(t_hielo),
                  run_time=0.7)
        self.wait(5.0)

        # --- momento: lanzar masa y retroceder -----------------------------
        rot.mostrar(pie_curso("Solo puedes tirar masa hacia atrás… y "
                              "retroceder."), zona="abajo", run_time=0.5)
        # el grupo entero pasa a la escena para animarlo con .en(t) sin que
        # el hielo y el cuerpo se dibujen dos veces
        self.remove(pat.hielo, pat.cuerpo)
        self.add(pat)
        self.play(UpdateFromAlphaFunc(pat, lambda m, a: m.en(4.4 * a)),
                  run_time=5.5, rate_func=linear)

        t_retro = tag_hud(f"retroceso  {pat.retroceso():.3f} m/s",
                          font_size=21, color=C_PROPELENTE)
        t_retro.next_to(pat.cuerpo, UP, buff=0.34)
        self.play(FadeIn(t_retro, shift=0.14 * UP), run_time=0.7)
        self.wait(1.4)

        # --- momento: la honestidad del momento conservado -----------------
        rot.mostrar(pie_curso("Cada bola sale más lenta… y él, cada vez más "
                              "rápido."), zona="abajo", run_time=0.5)
        self.play(Indicate(pat.bolas[1], color=C_PROPELENTE,
                           scale_factor=1.9),
                  Indicate(pat.bolas[2], color=C_PROPELENTE,
                           scale_factor=1.9), run_time=1.0)
        t_vfin = tag_hud(f"tras 3 bolas  {pat.velocidad_final():.3f} m/s",
                         font_size=21, color=C_CARGA)
        t_vfin.next_to(t_retro, UP, buff=0.30)
        self.play(FadeIn(t_vfin, shift=0.14 * UP), run_time=0.7)
        self.wait(4.2)

        # --- momento: el puente al cohete ----------------------------------
        rot.mostrar(pie_curso("Un cohete es un patinador que lanza su peso "
                              "en gas."), zona="abajo", run_time=0.5)
        ve = MathTex(rf"v_e = {VE_QUIMICO / 1000:.1f}\ \text{{km/s}}",
                     font_size=42, color=C_PROPELENTE)
        ve.move_to(LEFT * 3.55 + UP * 1.62)
        pie_ve = tag_junto(ve, "velocidad del gas", DOWN, buff=0.20,
                           font_size=17)
        self.play(FadeIn(ve, scale=0.6), FadeIn(pie_ve), run_time=0.8)
        self.wait(6.0)
