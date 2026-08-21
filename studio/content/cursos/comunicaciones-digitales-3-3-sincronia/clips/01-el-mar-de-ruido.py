class Clip1(Scene):
    """3.3.1 - El mar de ruido: 140 muestras de voltaje con 31 chips de
    mensaje enterrados a 0 dB. A simple vista, nada. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El mar de ruido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la antena solo oye voltaje --------------------------
        rot.mostrar(pie_curso("La antena no oye un mensaje: oye voltaje, "
                              "muestra tras muestra."),
                    zona="abajo", run_time=0.5)
        on = onda(T_RX, RX, rango_y=(-3.3, 3.3), ancho=11.0, alto=2.6)
        on.move_to(UP * 0.35)
        self.play(FadeIn(on.ejes), run_time=0.6)
        self.play(Create(on.curva), run_time=2.6)
        self.wait(2.6)

        # --- momento: el mensaje esta ahi, sin decir donde ----------------
        rot.mostrar(pie_curso("En algún lugar de estas muestras hay un "
                              "preámbulo de 31 chips. Nadie dice dónde."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(
            tag_hud(f"{N_TOTAL} muestras recibidas", font_size=20),
            tag_hud(f"preambulo = {N_CHIPS} chips", font_size=20,
                    color=C_BIT),
            tag_hud(f"SNR por chip = {fmt(SNR_CHIP_DB, 0)} dB",
                    font_size=20),
        ).arrange(DOWN, buff=0.16, aligned_edge=LEFT)
        cifras.next_to(on, DOWN, buff=0.24)
        cifras.set_x(0.0)
        self.play(FadeIn(cifras, shift=0.12 * UP), run_time=0.7)
        self.wait(4.6)

        # --- momento: probar ventana por ventana --------------------------
        rot.mostrar(pie_curso("Cero decibelios: el chip y el ruido pesan "
                              "lo mismo. Solo quedan las ventanas."),
                    zona="abajo", run_time=0.5)
        paso = float(on.en(1.0, 0.0)[0] - on.en(0.0, 0.0)[0])
        alto_v = float(on.en(0.0, 3.3)[1] - on.en(0.0, -3.3)[1])

        def ventana(k, color=C_TENUE):
            r = Rectangle(width=N_CHIPS * paso, height=alto_v,
                          color=color, stroke_width=2.0)
            r.set_fill(color, opacity=0.06)
            r.move_to(on.en(k + (N_CHIPS - 1) / 2.0, 0.0))
            return r

        v1 = ventana(6)
        q1 = tag_junto(v1, "¿aquí?", direccion=UP, buff=0.08, font_size=20)
        self.play(FadeOut(cifras), FadeIn(v1), FadeIn(q1), run_time=0.7)
        for k in (58, 96):
            v2 = ventana(k)
            self.play(Transform(v1, v2),
                      q1.animate.next_to(v2, UP, buff=0.08), run_time=1.0)
            self.wait(0.7)
        self.wait(2.0)

        # --- momento: la energia no distingue -----------------------------
        rot.mostrar(pie_curso("¿La ventana más fuerte? El ruido también "
                              "pesa: la más fuerte no es el mensaje."),
                    zona="abajo", run_time=0.5)
        vE = ventana(K_ENERGIA, color=C_BANDA)
        etE = tag_hud(f"ventana k = {K_ENERGIA}: energia = "
                      f"{fmt(E_MAX, 1)}", font_size=20, color=C_BANDA)
        etE.next_to(on, DOWN, buff=0.3)
        self.play(FadeOut(q1), Transform(v1, vE), FadeIn(etE),
                  run_time=1.0)
        self.wait(4.4)

        # --- momento: a simple vista, nada --------------------------------
        rot.mostrar(pie_curso("A simple vista no hay nada. Y aun así, el "
                              "mensaje está ahí."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(v1), FadeOut(etE), run_time=0.6)
        self.wait(5.2)
