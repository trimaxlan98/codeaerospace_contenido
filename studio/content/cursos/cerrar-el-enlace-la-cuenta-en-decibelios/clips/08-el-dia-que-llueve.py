class Clip8(Scene):
    """8 - El día que llueve. La barra de margen se queda sin nada cuando
    entra la tormenta, la escalera de MODCOD baja dos peldaños y el enlace
    sobrevive degradado. Cierre del curso. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))

        titulo = titulo_curso("El día que llueve")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: lo que sobra en un dia bueno ------------------------
        margen = barra_margen(margen_db=6.0, tope_db=12.0, alto=2.2,
                              ancho=0.46)
        margen.move_to(LEFT * 4.2 + DOWN * 0.1)
        escalera = escalera_modcod(list(MODCODS), ancho=4.2, alto=2.6)
        escalera.move_to(RIGHT * 1.5 + DOWN * 0.15)

        self.play(FadeIn(margen, shift=0.15 * UP), run_time=0.9)
        self.wait(0.6)

        rot.mostrar(pie_curso("El enlace no se diseña para el buen día: se "
                              "diseña para el malo."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        self.play(FadeIn(escalera, shift=0.15 * LEFT), run_time=1.0)
        self.play(escalera.mover_a(3), run_time=0.7)
        self.wait(2.6)

        # --- momento: la tormenta se lo come ------------------------------
        rot.mostrar(pie_curso("Ocho decibelios de lluvia se comen el margen "
                              "entero."), zona="abajo", run_time=0.5)
        self.play(margen.comer(8.0), run_time=1.4)
        self.wait(4.6)

        # --- momento: bajar un peldaño en vez de caerse -------------------
        # "de peldaño" y no "un peldaño": el marcador baja dos.
        rot.mostrar(pie_curso("El enlace no se corta: baja de peldaño y "
                              "sigue."), zona="abajo", run_time=0.5)
        self.play(escalera.mover_a(1), run_time=1.1)
        self.wait(1.4)

        # Bajar de MODCOD devuelve margen: el enlace pide menos SNR, y la
        # diferencia entre los dos peldaños es exactamente lo que recupera.
        recuperado = MODCODS[3][1] - MODCODS[1][1]
        self.play(margen.devolver(recuperado), run_time=1.2)
        self.wait(2.0)

        perdida = VGroup(
            Text(f"{escalera.bits_hz(3):.2f}", font=FUENTE_HUD, font_size=22,
                 color=C_TENUE),
            Text("→", font=FUENTE_HUD, font_size=22, color=C_TENUE),
            Text(f"{escalera.bits_hz(1):.2f} b/s/Hz", font=FUENTE_HUD,
                 font_size=22, color=C_MARGEN),
        ).arrange(RIGHT, buff=0.20)
        perdida.next_to(escalera, UP, buff=0.34)
        self.play(FadeIn(perdida, shift=0.1 * UP), run_time=0.6)

        rot.mostrar(pie_curso("Menos bits, pero imagen. Eso es degradar con "
                              "elegancia."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: cierre del curso ------------------------------------
        self.play(FadeOut(VGroup(margen, escalera, perdida)), run_time=0.9)
        rot.limpiar("arriba", run_time=0.4)

        cierre = VGroup(
            titulo_marca("Cerrar el enlace no es tener suerte.",
                         font_size=32),
            Text("Es haber hecho la cuenta.", font_size=26, color=C_MARGEN),
        ).arrange(DOWN, buff=0.30)
        cierre.move_to(UP * 0.25)

        self.play(Write(cierre[0]), run_time=1.4)
        self.play(FadeIn(cierre[1], shift=0.15 * UP), run_time=0.8)
        self.wait(5.6)
