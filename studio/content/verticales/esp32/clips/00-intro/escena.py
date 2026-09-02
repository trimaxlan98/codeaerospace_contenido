# 00 · Intro — la marca, en el idioma del lienzo.
#
# Las intros de los tres verticales anteriores son de consola: reticula que
# se enciende con un escaneo, escuadras HUD, wordmark que se ensambla. Esa
# intro delante de este curso mentiria sobre lo que viene despues.
#
# Aqui la apertura es una sola idea: el punto ambar de la marca es lo
# primero que existe, y de el nace todo lo demas. Nada de rejillas, nada de
# barridos. Empieza y termina en azul limpio.
class Clip(Scene):

    def construct(self):
        punto = Dot([0, 0.8, 0], radius=0.075, color=AMBAR)

        co = lz.titulo_display("co", font_size=92)
        de = lz.titulo_display("de", font_size=92)
        aca = lz.espaciado("academy", font_size=34, color=APAGADO,
                           tracking=0.42)
        # El wordmark se aprieta contra el punto MIDIENDO, no a ojo: en
        # el primer render "co . de" salio con medio centimetro de aire a
        # cada lado y se leia como tres palabras sueltas.
        sep = punto.width / 2 + 0.15
        marca = VGroup(co, de)
        co.move_to([0, 0.8, 0]).shift(LEFT * (sep + co.width / 2))
        de.move_to([0, 0.8, 0]).shift(RIGHT * (sep + de.width / 2))
        aca.next_to(marca, DOWN, buff=0.42)
        lz.cabe(marca, "wordmark")
        lz.cabe(aca, "academy")

        titulo = lz.titulo_display("ESP32", font_size=112)
        bajada = lz.espaciado("el chip por dentro", font_size=30,
                              color=AMBAR, tracking=0.34)
        titulo.move_to([0, -0.55, 0])
        bajada.next_to(titulo, DOWN, buff=0.42)
        lz.cabe(titulo, "titulo del curso")

        filete = lz.filete(ancho=1.1, color=AMBAR, grosor=3.0)
        filete.next_to(bajada, DOWN, buff=0.52)

        # --- 1. primero existe el punto -------------------------------
        self.wait(0.6)
        self.play(GrowFromCenter(punto), run_time=0.7)
        self.wait(0.5)

        # --- 2. y de el nace el nombre --------------------------------
        self.play(punto.animate.move_to([0, 0.8, 0]),
                  FadeIn(co, shift=RIGHT * 0.55),
                  FadeIn(de, shift=LEFT * 0.55),
                  run_time=1.1, rate_func=smooth)
        self.play(FadeIn(aca, lag_ratio=0.10, shift=UP * 0.12), run_time=0.9)
        self.wait(0.7)

        # --- 3. la marca se aparta y entra el curso -------------------
        bloque = VGroup(punto, co, de, aca)
        self.play(bloque.animate.scale(0.42).move_to([0, 2.55, 0]),
                  run_time=1.0, rate_func=smooth)
        self.play(FadeIn(titulo, shift=UP * 0.22), run_time=0.9)
        self.play(FadeIn(bajada, lag_ratio=0.06), Create(filete),
                  run_time=0.8)
        self.wait(2.0)

        # --- 4. de vuelta al azul limpio ------------------------------
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
        self.remove(*self.mobjects)
        self.wait(0.5)
