class Clip3(Scene):
    """3 - Las cuatro familias. Grid 2x2 de bloques (METALES, CERAMICOS,
    POLIMEROS, COMPUESTOS) en violeta salvo COMPUESTOS en cian; un pie
    narrativo por familia y su bloque pulsa con Indicate mientras el pie
    sigue en pantalla, en relevo. Cierra con COMPUESTOS resaltado.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: HUD y titulo -------------------------------------------
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Las cuatro familias")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.0)

        # --- momento: el grid 2x2 aparece -------------------------------------
        metales = bloque("METALES", ancho=2.5, color=C_FAM,
                         color_texto=C_TITULO)
        ceramicos = bloque("CERÁMICOS", ancho=2.5, color=C_FAM,
                           color_texto=C_TITULO)
        polimeros = bloque("POLÍMEROS", ancho=2.5, color=C_FAM,
                           color_texto=C_TITULO)
        compuestos = bloque("COMPUESTOS", ancho=2.5, color=C_MAT,
                            color_texto=C_TITULO)

        metales.move_to(np.array([-2.2, 0.7, 0.0]))
        ceramicos.move_to(np.array([2.2, 0.7, 0.0]))
        polimeros.move_to(np.array([-2.2, -1.0, 0.0]))
        compuestos.move_to(np.array([2.2, -1.0, 0.0]))

        grid = VGroup(metales, ceramicos, polimeros, compuestos)
        self.play(LaggedStart(*[FadeIn(b, shift=0.15 * UP) for b in grid],
                              lag_ratio=0.15), run_time=1.4)
        self.wait(1.0)

        # --- momento: metales, ductiles y confiables --------------------------
        rot.mostrar(pie_curso("Metales: dúctiles y confiables — se doblan "
                              "antes de romper."), zona="abajo",
                   run_time=0.5)
        self.wait(0.5)
        self.play(Indicate(metales, color=C_FAM, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.7)

        # --- momento: ceramicos, durisimos y fragiles ---------------------------
        rot.mostrar(pie_curso("Cerámicos: durísimos y frágiles — aguantan "
                              "calor, no perdonan golpes."), zona="abajo",
                   run_time=0.5)
        self.wait(0.5)
        self.play(Indicate(ceramicos, color=C_FAM, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.7)

        # --- momento: polimeros, ligeros y flexibles ----------------------------
        rot.mostrar(pie_curso("Polímeros: ligeros y flexibles — hasta que "
                              "sube la temperatura."), zona="abajo",
                   run_time=0.5)
        self.wait(0.5)
        self.play(Indicate(polimeros, color=C_FAM, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.7)

        # --- momento: compuestos, lo mejor de dos mundos ------------------------
        rot.mostrar(pie_curso("Compuestos: fibras rígidas en matriz "
                              "ligera. Lo mejor de dos mundos."),
                   zona="abajo", run_time=0.5)
        self.wait(0.5)
        self.play(Indicate(compuestos, color=C_MAT, scale_factor=1.15),
                  run_time=0.9)
        self.wait(3.7)

        # --- momento: cierre, la mision elige con cual casarse ------------------
        rot.mostrar(pie_curso("Cuatro caracteres. La misión elige con "
                              "cuál casarse."), zona="abajo", run_time=0.5)
        self.play(Indicate(compuestos, color=C_MAT, scale_factor=1.2),
                  run_time=1.0)
        self.wait(5.5)
