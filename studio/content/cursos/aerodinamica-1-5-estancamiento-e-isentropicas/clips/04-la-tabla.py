class Clip4(Scene):
    """1.5.4 - Uso de tablas de flujo isentropico y de calculadoras en linea.

    La tabla no se transcribe: se genera con las mismas funciones que
    dibujaron las curvas. Se lee una fila entera y se deja la ultima columna
    apuntando al modulo 2. Cierre de la leccion Y del modulo 1. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La tabla")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tabla = tabla_isentropica(machs=MACHS_TABLA, font_size=18)
        tabla.move_to(UP * 0.20)

        self.play(FadeIn(tabla.cabecera), Create(tabla.regla), run_time=0.9)
        rot.mostrar(pie_curso("Nadie calcula esto a mano dos veces. Se "
                              "tabula."), zona="abajo", run_time=0.5)
        self.wait(1.2)
        self.play(LaggedStart(*[FadeIn(f, shift=0.10 * UP)
                                for f in tabla.filas], lag_ratio=0.28),
                  run_time=1.6)
        self.wait(2.8)

        rot.mostrar(pie_curso("Entras por el Mach y sales con las tres "
                              "razones."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- momento: leer una fila ---------------------------------------
        # El resaltado lo construye la pieza sobre la fila real, y las cifras
        # del pie salen de `tabla.valor`: leer la tabla y contarla no pueden
        # dar cosas distintas.
        franja = tabla.resaltar(FILA_LECTURA, color=C_TRANS)
        self.play(FadeIn(franja), run_time=0.6)
        rot.mostrar(pie_curso(f"A Mach {tabla.valor(FILA_LECTURA, 0):g} la "
                              f"temperatura cae al "
                              f"{tabla.valor(FILA_LECTURA, 1) * 100:.0f} % y "
                              f"la presión al "
                              f"{tabla.valor(FILA_LECTURA, 2) * 100:.0f} %."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: la columna que aun no significa nada -----------------
        self.play(Indicate(tabla.columna(4), color=C_SUPER, scale_factor=1.12),
                  run_time=1.0)
        rot.mostrar(pie_curso("La última columna todavía no significa nada "
                              "para ti."), zona="abajo", run_time=0.5)
        self.wait(4.4)

        rot.mostrar(pie_curso("En el módulo 2 será la que dimensione la "
                              "tobera de un cohete."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- cierre de la leccion y del modulo 1 ---------------------------
        self.play(FadeOut(VGroup(tabla, franja)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Ya tienes el idioma.", font_size=38,
                         color=C_TITULO),
            titulo_marca("Ahora toca romper el aire.", font_size=38,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.2)
