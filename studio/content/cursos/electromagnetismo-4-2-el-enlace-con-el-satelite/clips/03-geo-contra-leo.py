class Clip3(Scene):
    """4.2.3 - GEO contra LEO: la misma antena, la misma potencia, y 65
    veces menos distancia. Toda la ventaja de LEO es geometria. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("GEO contra LEO")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: las dos alturas, a escala ----------------------------
        mor = mapa_orbitas(radio_tierra=R_MAPA, con_cinturones=False,
                           orbitas=(("LEO", H_LEO), ("GEO", H_GEO)))
        mor.move_to(LEFT * 3.9 + DOWN * 0.15)
        sat_geo = Dot(mor.punto_orbita("GEO", 40.0), radius=0.09,
                      color=C_CARGA)
        sat_leo = Dot(mor.punto_orbita("LEO", 115.0), radius=0.07,
                      color=C_CARGA)
        rot.mostrar(pie_curso("Las dos alturas donde vive la satcom, "
                              "dibujadas a la misma escala."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(mor.tierra, scale=1.3), run_time=0.6)
        self.play(Create(mor.orbita("LEO")), Create(mor.orbita("GEO")),
                  FadeIn(sat_leo), FadeIn(sat_geo), run_time=1.1)
        self.wait(4.4)

        # --- la tabla: una columna por orbita ------------------------------
        def celda(texto, x, y, color=None, font_size=19):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(RIGHT * x + UP * y)
            return t

        y_cab, y_1, y_2, y_3 = 1.95, 1.15, 0.40, -0.35
        cabecera = VGroup(celda("GEO", 3.3, y_cab, C_TENUE),
                          celda("LEO", 5.9, y_cab, C_TENUE))
        fila_d = VGroup(
            celda("distancia", 0.6, y_1, C_TENUE, 18),
            celda(f"{H_GEO / 1e3:,.0f} km".replace(",", " "), 3.3, y_1),
            celda(f"{H_LEO / 1e3:.0f} km", 5.9, y_1))
        fila_p = VGroup(
            celda("reparto 12 GHz", 0.6, y_2, C_TENUE, 18),
            celda(f"{FSPL_GEO:.1f} dB", 3.3, y_2),
            celda(f"{FSPL_LEO:.1f} dB", 5.9, y_2))
        fila_t = VGroup(
            celda("ida y vuelta", 0.6, y_3, C_TENUE, 18),
            celda(f"{LAT_GEO_MS:.0f} ms", 3.3, y_3),
            celda(f"{LAT_LEO_MS:.1f} ms", 5.9, y_3))
        linea_a = celda(f"{RAZON_DIST:.0f} x mas lejos", 3.3, -1.35)
        linea_b = celda(f"{VENTAJA_LEO_DB:.1f} dB  =  "
                        f"{VENTAJA_LEO_X:,.0f} x mas potencia"
                        .replace(",", " "), 3.3, -2.0)

        rot.mostrar(pie_curso("GEO está sesenta y cinco veces más lejos "
                              "que un satélite de constelación."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cabecera), FadeIn(fila_d, shift=0.12 * RIGHT),
                  FadeIn(linea_a), run_time=0.8)
        self.wait(4.4)

        # --- momento: lo que cuesta esa distancia --------------------------
        rot.mostrar(pie_curso("Se paga en señal: treinta y seis "
                              "decibelios, cuatro mil veces menos potencia."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fila_p, shift=0.12 * RIGHT),
                  FadeIn(linea_b, shift=0.12 * RIGHT), run_time=0.8)
        self.wait(4.6)

        # --- momento: y el tiempo ------------------------------------------
        rot.mostrar(pie_curso("Y en el reloj: un cuarto de segundo de ida "
                              "y vuelta. Por eso una llamada por GEO se pisa."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(fila_t, shift=0.12 * RIGHT), run_time=0.7)
        self.wait(4.6)

        rot.mostrar(pie_curso("GEO cubre un tercio del planeta sin "
                              "moverse. LEO gana el enlace..."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        rot.mostrar(pie_curso("...pero hay que llenar el cielo de "
                              "satélites, y perseguirlos uno a uno."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
