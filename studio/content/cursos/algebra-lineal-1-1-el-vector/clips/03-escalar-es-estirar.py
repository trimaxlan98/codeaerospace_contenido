class Clip3(Scene):
    """1.1.3 - Multiplicar por un escalar estira, encoge o da la vuelta a la
    flecha sin sacarla de su recta: todos los multiplos viven en el span. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Escalar es estirar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion(vivo=False)
        u = vector(pl, U_ESC, color=C_VEC, nombre=r"\vec u")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Multiplicar un vector por un número no lo "
                              "gira: lo estira."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(u.flecha), FadeIn(u.etiqueta), run_time=0.9)
        self.wait(3.6)

        cifra = tag_hud("x " + fmt(1.0), font_size=20)
        cifra.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(FadeIn(cifra), run_time=0.3)

        fantasmas = VGroup()
        movil = u   # el objeto animado; se reasigna tras cada Transform

        def estirar(k, nombre, pie):
            nonlocal movil, cifra
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            destino = movil.con_coords(k * U_ESC, nombre=nombre)
            nueva_cifra = tag_hud("x " + fmt(k), font_size=20)
            nueva_cifra.move_to(cifra)
            self.play(Transform(movil, destino), Transform(cifra, nueva_cifra),
                      run_time=1.3)
            fantasma = flecha_libre(pl, (0, 0), k * U_ESC, color=C_VEC,
                                    opacidad=0.35)
            fantasmas.add(fantasma)
            self.add(fantasma)
            self.wait(3.4)

        estirar(ESCALARES[0], r"2\vec u",
                "Por dos: el doble de largo, la misma dirección.")
        estirar(ESCALARES[1], r"\tfrac{1}{2}\vec u",
                "Por un medio: se encoge, pero sigue en su carril.")
        estirar(ESCALARES[2], r"-1.5\,\vec u",
                "Un escalar negativo le da la vuelta: mismo carril, "
                "sentido contrario.")

        # --- momento: la recta de todos los multiplos ----------------------
        rot.mostrar(pie_curso("Todos los múltiplos de u viven en una sola "
                              "recta. Recuérdala: se llama span."),
                    zona="abajo", run_time=0.5)
        recta_u = span_recta(pl, U_ESC, color=C_IMG, opacidad=0.55)
        self.play(Create(recta_u), run_time=1.2)
        self.play(FadeOut(fantasmas), run_time=0.3)
        # El multiplo actual (-1.5u) ya lleva su etiqueta en la flecha: solo
        # se marca el punto, sin tag, para no encimarlo.
        for k, nombre in ((ESCALARES[0], "2u"), (ESCALARES[1], "u/2"),
                          (ESCALARES[2], None)):
            self.add(flecha_libre(pl, (0, 0), k * U_ESC, color=C_VEC,
                                  opacidad=0.4))
            punto = pl.punto(k * U_ESC, color=C_IMG, radio=0.06)
            anims = [FadeIn(punto)]
            if nombre is not None:
                t = tag_hud(nombre, font_size=15, color=C_IMG)
                t.next_to(punto, DOWN, buff=0.14)
                anims.append(FadeIn(t))
            self.play(*anims, run_time=0.35)
        self.wait(3.6)

        rot.mostrar(pie_curso("Estirar y sumar: con esas dos operaciones "
                              "se construye TODO lo que sigue."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
