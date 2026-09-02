# 00 · Intro — la marca de la casa, sobre el lienzo.
#
# La primera version construia el wordmark en MINUSCULAS y con un `Dot`
# redondo entre las dos silabas. Salia "co·de": un punto flotando a media
# altura, que se lee como un separador y no como la marca. El wordmark de
# la casa es "CO.DE" en MAYUSCULAS con un PUNTO TIPOGRAFICO, y un punto se
# apoya en la linea de base — de ahi que el anterior se viera chueco.
#
# Aqui se usa la misma construccion que
# `studio/content/cursos/marca-intro-y-cierre/style_block.py::wordmark()`:
# CO y DE en tinta, el punto en ambar, los tres alineados por el borde
# INFERIOR (las mayusculas y el punto comparten linea de base, asi que
# igualar los bordes de abajo ES alinearlos tipograficamente).
#
# La coreografia tambien es la de la marca: CO y DE se ensamblan, el punto
# llega al final como un cursor y parpadea dos veces, ACADEMY entra con
# tracking amplio y un subrayado remata. Lo que NO viene es la reticula HUD
# ni las escuadras de esquina: son la identidad de CONSOLA y aqui
# contradirian el estilo. El fondo liso hace ese trabajo.
class Clip(Scene):

    def construct(self):
        Y_MARCA = 1.05

        # --- el wordmark, construido como manda la marca ---------------
        co = Text("CO", font=lz.FUENTE_DISPLAY, weight="SEMIBOLD",
                  font_size=104, color=TINTA)
        punto = Text(".", font=lz.FUENTE_DISPLAY, weight="BOLD",
                     font_size=104, color=AMBAR)
        de = Text("DE", font=lz.FUENTE_DISPLAY, weight="SEMIBOLD",
                  font_size=104, color=TINTA)
        marca = VGroup(co, punto, de).arrange(buff=0.10, aligned_edge=DOWN)
        marca.move_to([0, Y_MARCA, 0])
        lz.cabe(marca, "wordmark")

        academy = Text("A C A D E M Y", font=lz.FUENTE_DISPLAY,
                       weight="MEDIUM", font_size=34, color=APAGADO)
        academy.next_to(marca, DOWN, buff=0.42)
        lz.cabe(academy, "academy")

        raya = Line(marca.get_corner(DL), marca.get_corner(DR),
                    stroke_width=4.0, color=AMBAR)
        raya.shift(DOWN * 0.26)

        # --- el curso --------------------------------------------------
        titulo = lz.titulo_display("ESP32", font_size=112)
        bajada = lz.espaciado("el chip por dentro", font_size=30,
                              color=AMBAR, tracking=0.34)
        titulo.move_to([0, -1.35, 0])
        bajada.next_to(titulo, DOWN, buff=0.42)
        lz.cabe(titulo, "titulo del curso")

        # --- 1. CO y DE se ensamblan -----------------------------------
        self.wait(0.6)
        self.play(FadeIn(co, shift=RIGHT * 0.60),
                  FadeIn(de, shift=LEFT * 0.60),
                  run_time=1.1, rate_func=smooth)

        # --- 2. el punto llega el ultimo, y parpadea como un cursor ----
        self.play(FadeIn(punto, shift=DOWN * 0.40), run_time=0.5,
                  rate_func=rate_functions.ease_out_cubic)
        for _ in range(2):
            punto.set_opacity(0.0)
            self.wait(0.17)
            punto.set_opacity(1.0)
            self.wait(0.16)
        self.wait(0.2)

        # --- 3. ACADEMY y el subrayado ---------------------------------
        self.play(FadeIn(academy, lag_ratio=0.08, shift=UP * 0.12),
                  run_time=0.9)
        self.play(Create(raya), run_time=0.6)
        self.wait(0.7)

        # --- 4. la marca se aparta y entra el curso --------------------
        bloque = VGroup(marca, academy, raya)
        self.play(bloque.animate.scale(0.46).move_to([0, 2.75, 0]),
                  run_time=1.0, rate_func=smooth)
        self.play(FadeIn(titulo, shift=UP * 0.22), run_time=0.9)
        self.play(FadeIn(bajada, lag_ratio=0.06), run_time=0.7)
        self.wait(1.9)

        # --- 5. de vuelta al azul limpio -------------------------------
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.0)
        self.remove(*self.mobjects)
        self.wait(0.5)
