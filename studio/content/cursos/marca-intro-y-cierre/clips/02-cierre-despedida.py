class Clip2(Scene):
    """Cierre "Despedida": el wordmark CO.DE ACADEMY entra con calma, se
    subraya con el degradado de marca, el pie invita a seguir explorando
    y, tras un ultimo parpadeo del punto ambar (la firma del canal), todo
    funde a fondo limpio."""

    def construct(self):
        # --- Piezas -----------------------------------------------------
        grupo, co, punto, de = wordmark(88)
        acad = academy(28)
        bloque = VGroup(grupo, acad).arrange(DOWN, buff=0.32)
        bloque.move_to(ORIGIN)

        linea = subrayado(grupo)
        pie = Text("Sigue explorando.", font_size=26, color=C_TENUE)
        pie.next_to(bloque, DOWN, buff=1.1)

        # --- 1) Entrada (0-2 s) ------------------------------------------
        # Fondo limpio y quieto, luego el bloque (wordmark + academy)
        # entra junto con FadeIn suave y una leve escala 0.96 -> 1.
        self.wait(0.6)
        self.play(FadeIn(bloque, scale=0.96), run_time=1.2, rate_func=smooth)
        self.wait(0.3)

        # --- 2) Subrayado y pie (2-4.5 s) ---------------------------------
        self.play(Create(linea), run_time=1.0, rate_func=smooth)
        self.play(FadeIn(pie, shift=UP * 0.1), run_time=0.6, rate_func=smooth)
        self.wait(1.2)

        # --- 3) La firma (4.5-7 s) -----------------------------------------
        # El pie desvanece; el punto ambar parpadea dos veces como cursor
        # (todo lo demas queda quieto).
        self.play(FadeOut(pie), run_time=0.5)
        for _ in range(2):
            self.play(punto.animate.set_opacity(0), run_time=0.2, rate_func=linear)
            self.play(punto.animate.set_opacity(1), run_time=0.2, rate_func=linear)
        self.wait(0.6)

        # --- 4) Fundido (7-9 s) ---------------------------------------------
        self.play(FadeOut(bloque), FadeOut(linea), run_time=1.0, rate_func=smooth)
        self.wait(1.2)
