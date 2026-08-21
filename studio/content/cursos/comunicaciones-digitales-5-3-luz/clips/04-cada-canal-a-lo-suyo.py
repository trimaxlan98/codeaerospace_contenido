class Clip4(Scene):
    """5.3.4 - Cada canal a lo suyo: tabla comparada canal / alcance /
    dB por km / uso (fibra, radio, laser espacial) en `tag_hud`,
    reutilizando ATEN_FIBRA_DB_KM, TRAMO_AMPLI_KM y DSOC_DIST_MKM.
    Cierre de la leccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cada canal a lo suyo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        def celda(texto, x, y, color=None, font_size=18):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(RIGHT * x + UP * y)
            return t

        y_cab, y_fibra, y_radio, y_laser = 1.55, 0.75, 0.0, -0.75
        x_canal, x_alcance, x_dbkm, x_uso = -4.6, -1.5, 1.1, 3.9

        cabecera = VGroup(
            celda("canal", x_canal, y_cab, C_TENUE),
            celda("alcance", x_alcance, y_cab, C_TENUE),
            celda("dB/km", x_dbkm, y_cab, C_TENUE),
            celda("uso", x_uso, y_cab, C_TENUE))

        fila_fibra = VGroup(
            celda("fibra", x_canal, y_fibra, C_SENAL),
            celda(f"repetida c/{fmt(TRAMO_AMPLI_KM, 0)} km",
                 x_alcance, y_fibra, font_size=15),
            celda(fmt(ATEN_FIBRA_DB_KM, 1), x_dbkm, y_fibra),
            celda("submarino, troncal", x_uso, y_fibra, C_TENUE,
                 font_size=15))

        fila_radio = VGroup(
            celda("radio", x_canal, y_radio, C_SENAL),
            celda("cualquier punto visible", x_alcance, y_radio, C_TENUE,
                 font_size=14),
            celda("varia (FSPL)", x_dbkm, y_radio, C_TENUE, font_size=15),
            celda("satelite y movil", x_uso, y_radio, C_TENUE,
                 font_size=15))

        fila_laser = VGroup(
            celda("laser espacial", x_canal, y_laser, C_SENAL,
                 font_size=15),
            celda(f"{fmt(DSOC_DIST_MKM, 0)} M km (DSOC)",
                 x_alcance, y_laser, font_size=14),
            celda("~0 (vacio)", x_dbkm, y_laser, C_TENUE, font_size=15),
            celda("espacio profundo", x_uso, y_laser, C_TENUE,
                 font_size=15))

        # --- momento: el precio de cada canal ------------------------------
        rot.mostrar(pie_curso("Cada canal paga un precio distinto: "
                              "alcance, pérdida, quién lo usa."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cabecera), run_time=0.8)
        self.wait(4.6)

        # --- momento: la fibra, casi sin perdida ---------------------------
        rot.mostrar(pie_curso("La fibra: enterrada, repetida, casi sin "
                              "pérdida."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fila_fibra, shift=0.12 * RIGHT), run_time=0.8)
        self.wait(4.6)

        # --- momento: la radio, devorada por la distancia ------------------
        rot.mostrar(pie_curso("La radio: sin cable que tender, pero la "
                              "distancia la devora."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fila_radio, shift=0.12 * RIGHT), run_time=0.8)
        self.wait(4.6)

        # --- momento: el laser espacial, casi vacio -------------------------
        rot.mostrar(pie_curso("El láser espacial: casi vacío, pero hay "
                              "que apuntar con precisión."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fila_laser, shift=0.12 * RIGHT), run_time=0.8)
        self.wait(4.8)

        # --- cierre de leccion -----------------------------------------------
        cierre_leccion(
            self, rot,
            "No hay un canal mejor.",
            "Hay un canal para cada silencio.",
            "Siguiente leccion: el demodulador que aprende.",
            cabecera, fila_fibra, fila_radio, fila_laser)
