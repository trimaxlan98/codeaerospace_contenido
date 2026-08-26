class Clip4(Scene):
    """2.2.4 - Cuando dos filas coinciden con el mismo destino, gana la
    mas especifica: el prefijo mas largo. Basta un bit del destino para
    que esa fila deje de aplicar y la decision cambie. Cierre de la
    leccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El prefijo mas largo gana")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        fila_16 = TABLA_RUTAS[IDX_B]
        fila_24 = TABLA_RUTAS[IDX_A]
        bits_16 = cidr(fila_16[0])["bits"]
        bits_24 = cidr(fila_24[0])["bits"]

        # --- momento: dos filas, un destino ------------------------------
        rot.mostrar(pie_curso("El destino %s coincide con dos filas: "
                              "una /16 y una /24." % IP_A),
                    zona="abajo", run_time=0.5)
        barra = barra_bits(IP_A, 24, ancho=6.2, alto=0.32, fs=10)
        barra.move_to(UP * 1.65)
        tab = tabla(["Prefijo", "Bits", "Salto"],
                   [(fila_16[0], str(bits_16), fila_16[1]),
                    (fila_24[0], str(bits_24), fila_24[1])],
                   anchos=[3.0, 1.0, 1.2], alto=0.5, fs=18)
        tab.move_to(DOWN * 0.55)
        self.play(FadeIn(barra), run_time=0.8)
        self.wait(1.0)
        self.play(FadeIn(tab), run_time=0.9)
        self.wait(2.6)

        # --- momento: gana el prefijo mas largo -------------------------
        rot.mostrar(pie_curso("No hay empate: gana la fila con MAS bits "
                              "de prefijo, la mas especifica."),
                    zona="abajo", run_time=0.5)
        ganadora = tab.con_filas(
            [(fila_16[0], str(bits_16), fila_16[1]),
             (fila_24[0], str(bits_24), fila_24[1])], resaltar=1)
        self.play(Transform(tab, ganadora), run_time=0.6)
        self.wait(3.2)

        # --- momento: el bit frontera -------------------------------------
        rot.mostrar(pie_curso("El bit 24 es la frontera exacta de esa "
                              "subred /24."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(barra.celda(23), color=C_PERDIDA,
                           scale_factor=1.6), run_time=1.1)
        self.wait(2.4)

        # --- momento: se cambia ese bit -------------------------------------
        rot.mostrar(pie_curso("Basta cambiarlo para salir de la subred "
                              "/24: el destino ahora es %s." % IP_D),
                    zona="abajo", run_time=0.5)
        barra_d = barra.con_prefijo(24, valor=IP_D)
        self.play(Transform(barra, barra_d), run_time=1.3)
        self.wait(2.0)

        # --- momento: la decision cambia de salida --------------------------
        rot.mostrar(pie_curso("La fila /24 ya no aplica. Ahora la mas "
                              "especifica que queda es /16, por %s."
                              % RES_D["siguiente"]),
                    zona="abajo", run_time=0.5)
        ganadora_d = tab.con_filas(
            [(fila_16[0], str(bits_16), fila_16[1]),
             (fila_24[0], str(bits_24), fila_24[1])], resaltar=0)
        tacha = Line(tab.fila(1).get_left() + LEFT * 0.12,
                    tab.fila(1).get_right() + RIGHT * 0.12,
                    color=C_PERDIDA, stroke_width=3.2)
        tacha.move_to(tab.fila(1).get_center())
        self.play(Transform(tab, ganadora_d), FadeIn(tacha), run_time=0.8)
        cifras = VGroup(
            tag_hud("coincide con  %d filas" % RES_D["n_coinciden"],
                    font_size=20),
            tag_hud("gana          %s  por  %s"
                    % (RES_D["elegida"], RES_D["siguiente"]),
                    font_size=20, color=C_CIFRA),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.next_to(tab, DOWN, buff=0.45)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.3), run_time=1.0)
        self.wait(3.6)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "Un router no conoce el mundo.",
            "Conoce el trozo de mundo que le toca.",
            "Siguiente: IPv6, el espacio que no se acaba.",
            barra, tab, tacha, cifras, espera=4.4)
