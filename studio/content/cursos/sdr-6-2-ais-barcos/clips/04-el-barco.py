class Clip4(Scene):
    """6.2.4 - El resultado de S.cadena_ais(): CRC valido y la tarjeta del
    barco (verde) con MMSI, posicion, velocidad y rumbo, todo leido del
    dict decodificado (no a mano). Barco ficticio. Cierre de la leccion.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El barco"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        lat_txt = f"{abs(AIS['lat']):.4f} {'N' if AIS['lat'] >= 0 else 'S'}"
        lon_txt = f"{abs(AIS['lon']):.4f} {'O' if AIS['lon'] < 0 else 'E'}"
        sog_txt = f"{AIS['sog']:.1f} nudos"
        cog_txt = f"{AIS['cog']:.1f} grados"

        def campo(etiqueta, texto_valor, font_size=30):
            val = tag_hud(texto_valor, font_size=font_size, color=C_OK)
            et = tag_junto(val, etiqueta, UP, buff=0.14, font_size=19,
                          color=C_TENUE)
            return VGroup(et, val)

        c_mmsi = campo("mmsi", str(AIS["mmsi"]))
        c_pos = campo("posicion", f"{lat_txt}\n{lon_txt}", font_size=26)
        c_sog = campo("velocidad", sog_txt)
        c_cog = campo("rumbo", cog_txt)

        col_izq = VGroup(c_mmsi, c_sog).arrange(DOWN, buff=0.85,
                                                aligned_edge=LEFT)
        col_der = VGroup(c_pos, c_cog).arrange(DOWN, buff=0.85,
                                               aligned_edge=LEFT)
        campos = VGroup(col_izq, col_der).arrange(RIGHT, buff=2.4,
                                                  aligned_edge=UP)
        campos.move_to(UP * 0.15)

        tarjeta = RoundedRectangle(corner_radius=0.28,
                                   width=campos.width + 1.3,
                                   height=campos.height + 1.1,
                                   stroke_color=C_OK, stroke_width=2.6,
                                   fill_color=C_OK, fill_opacity=0.06)
        tarjeta.move_to(campos)

        self.play(Create(tarjeta), run_time=0.9)
        self.wait(0.5)

        crc_txt = "CRC valido" if AIS["crc_ok"] else "CRC invalido"
        crc_color = C_OK if AIS["crc_ok"] else C_RUIDO
        rot.mostrar(cifra_pie(crc_txt, color=crc_color), zona="abajo",
                    run_time=0.5)
        self.wait(2.2)

        self.play(FadeIn(c_mmsi, shift=UP * 0.12), run_time=0.6)
        self.wait(1.3)
        self.play(FadeIn(c_pos, shift=UP * 0.12), run_time=0.6)
        self.wait(1.3)
        self.play(FadeIn(c_sog, shift=UP * 0.12), run_time=0.6)
        self.wait(1.3)
        self.play(FadeIn(c_cog, shift=UP * 0.12), run_time=0.6)
        self.wait(2.0)

        rot.mostrar(dato_pie("barco ficticio"), zona="abajo", run_time=0.5)
        self.wait(7.0)

        cierre_leccion(self, rot, "Los barcos se anuncian solos.",
                       "Cualquiera puede escucharlos.", tarjeta, col_izq,
                       col_der, espera=6.0)
