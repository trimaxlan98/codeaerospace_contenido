class Clip(Scene):
    """15 · Cierre — la despedida de la marca, en 9:16.

    El wordmark se enciende, el degradado ambar-naranja lo subraya, y el
    punto se queda parpadeando como el cursor de una consola que sigue
    encendida. Termina en negro total para que el montaje pueda cortar
    ahi sin nada colgando.
    """

    marca_chica = False
    esquinas = False
    velos = False

    def construct(self):
        wm, co, punto, de = wordmark(84)
        aca = academy(27)
        aca.next_to(wm, DOWN, buff=0.32)
        bloque = VGroup(wm, aca)
        bloque.move_to(UP * 1.35)
        raya = subrayado_marca(bloque, margen=0.34, grosor=3.4)

        pie = Text("Sigue explorando.", weight="MEDIUM", font_size=30,
                   color=CODE_MUTED)
        pie.next_to(raya, DOWN, buff=0.58)

        firma = hud("co.de academy", font_size=15)
        firma.move_to(DOWN * 3.3)

        self.wait(0.4)
        self.play(FadeIn(co, shift=RIGHT * 0.4), FadeIn(de, shift=LEFT * 0.4),
                  FadeIn(punto, shift=DOWN * 0.3),
                  LaggedStart(*[FadeIn(l, shift=UP * 0.1) for l in aca],
                              lag_ratio=0.07),
                  run_time=1.4)
        self.play(Create(raya), run_time=1.1)
        self.play(FadeIn(pie, shift=UP * 0.16), run_time=0.8)
        self.play(FadeIn(firma, shift=UP * 0.12), run_time=0.6)
        self.wait(0.5)

        # el punto se queda parpadeando: la consola sigue encendida
        for _ in range(2):
            punto.set_fill(opacity=0.0)
            self.wait(0.20)
            punto.set_fill(opacity=1.0)
            self.wait(0.22)
        self.play(punto.animate.scale(1.25).set_color("#ffd48a"),
                  run_time=0.7, rate_func=there_and_back)
        self.wait(0.9)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.2)
        self.remove(*self.mobjects)
        self.wait(0.5)
