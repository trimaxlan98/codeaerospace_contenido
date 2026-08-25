class Clip2(Scene):
    """2.2.2 - Cuatro /24 vecinos comparten los primeros 22 bits; solo los
    dos siguientes cambian. Por eso una sola fila /22 basta para las
    cuatro: `agregar_rutas` cuenta las filas que se ahorran. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("CIDR: agrupar para no ahogarse")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: cuatro redes, cuatro filas ---------------------------
        rot.mostrar(pie_curso("Cuatro redes vecinas: cada una llegaria "
                              "con su propia fila en la tabla."),
                    zona="abajo", run_time=0.5)
        barras = VGroup(*[barra_bits(ip.split("/")[0], 24, ancho=6.0,
                                     alto=0.30, fs=9, mostrar_texto=False)
                          for ip in RUTAS_AGREGAR])
        barras.arrange(DOWN, buff=0.34)
        barras.move_to(UP * 0.55)
        etiquetas = VGroup(*[tag_hud(ip, font_size=15, color=C_EJE)
                             for ip in RUTAS_AGREGAR])
        for et, b in zip(etiquetas, barras):
            et.next_to(b, LEFT, buff=0.28)
        self.play(LaggedStart(*[FadeIn(VGroup(b, e))
                                for b, e in zip(barras, etiquetas)],
                              lag_ratio=0.22), run_time=1.4)
        self.wait(4.6)

        # --- momento: los primeros 22 bits son iguales ---------------------
        rot.mostrar(pie_curso("Los primeros 22 bits son identicos en las "
                              "cuatro. Ahi no hay nada que decidir."),
                    zona="abajo", run_time=0.5)
        gemelas = [b.con_prefijo(22) for b in barras]
        self.play(*[Transform(b, g) for b, g in zip(barras, gemelas)],
                  run_time=1.6)
        self.wait(4.2)

        # --- momento: solo dos bits libres -----------------------------
        rot.mostrar(pie_curso("Solo los dos bits siguientes cambian: eso "
                              "es lo unico que las distingue."),
                    zona="abajo", run_time=0.5)
        self.play(*[Indicate(b.celda(22), color=C_CIFRA, scale_factor=1.4)
                    for b in barras],
                  *[Indicate(b.celda(23), color=C_CIFRA, scale_factor=1.4)
                    for b in barras],
                  run_time=1.4)
        self.wait(3.6)

        # --- momento: se pliegan en una sola fila ---------------------------
        rot.mostrar(pie_curso("`agregar_rutas` pliega las cuatro filas en "
                              "una sola: /22 cubre a las cuatro."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(barras), FadeOut(etiquetas), run_time=0.5)
        unida = barra_bits(CIDR_UNIDA["red"], 22, ancho=6.6, alto=0.36,
                           fs=12)
        unida.move_to(UP * 0.55)
        self.play(FadeIn(unida), run_time=0.9)
        cifras = VGroup(
            tag_hud("filas antes -> despues   %d -> %d"
                    % (AGREGADO["filas_antes"], AGREGADO["filas_despues"]),
                    font_size=20),
            tag_hud("ahorro                   %d filas"
                    % AGREGADO["ahorro"], font_size=20, color=C_OK),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.next_to(unida, DOWN, buff=1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.3), run_time=1.1)
        self.wait(6.5)
