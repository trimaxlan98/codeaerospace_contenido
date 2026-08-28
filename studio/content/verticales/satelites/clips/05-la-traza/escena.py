class Clip(Scene):
    """05 · La traza — la Tierra no espera.

    El punto que el satelite tiene justo debajo dibuja una sinusoide sobre
    el mapa. Y no cierra: cuando termina la vuelta, el planeta se ha girado
    debajo, asi que la siguiente pasada cae 23.94 grados mas al oeste. Tres
    vueltas y tres cruces del ecuador repartidos exactamente por ese hueco.

    Las cifras las da `satelites.corrimiento_traza`; la traza sale de
    `subsatelites_walker` con la rotacion terrestre metida, y se parte en el
    antimeridiano con `traza_terrestre` (sin partirla, la polilinea cruza la
    pantalla de lado a lado).
    """

    ALTURA_KM = 550.0
    RES_MAPA = (720, 360)
    VUELTAS = 3
    FRAMES = 240

    def construct(self):
        co = sa.corrimiento_traza(self.ALTURA_KM)
        per = sa.periodo_orbital(self.ALTURA_KM)["segundos"]
        lonlat = sa.subsatelites_walker(self.FRAMES, 1, 1, 53.0,
                                        self.ALTURA_KM,
                                        vueltas=self.VUELTAS,
                                        duracion_s=self.VUELTAS * per)[:, 0, :]

        marca = hud_pieza("05 . la traza")
        mapa = sa.imagen_mapa(self.RES_MAPA, alto_escena=2.88)
        mapa.move_to(UP * Y_ESCENA)

        # Los cruces del ecuador hacia el norte: es donde se mide el hueco.
        lat = lonlat[:, 1]
        cruces = [k for k in range(1, len(lat))
                  if lat[k - 1] < 0.0 <= lat[k]][:self.VUELTAS]

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(mapa), run_time=0.9)

        pie = medida(f"{co['vueltas_por_dia']:.2f}", "vueltas al dia",
                     f"una cada {co['periodo_min']:.1f} min", color=C_MEDIDO,
                     color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)

        por_vuelta = self.FRAMES // self.VUELTAS
        trazos, ticks = [], []
        for v in range(self.VUELTAS):
            tramo = lonlat[v * por_vuelta: (v + 1) * por_vuelta + 1]
            trazo = sa.traza_terrestre(tramo, mapa, color=C_SAT, ancho=2.8,
                                       opacidad=0.95)
            for viejo in trazos:
                viejo.set_stroke(opacity=0.35)
            self.play(Create(trazo), run_time=4.2, rate_func=linear)
            trazos.append(trazo)
            if v < len(cruces):
                p = sa.puntos_en_mapa(mapa, [[lonlat[cruces[v], 0], 0.0]])[0]
                tick = Line(p + DOWN * 0.30, p + UP * 0.30,
                            stroke_color=C_PERDIDO, stroke_width=3.2)
                tick.set_z_index(10)
                self.play(GrowFromCenter(tick), run_time=0.4)
                ticks.append(tick)
            self.wait(0.9)

        # --- el hueco entre dos pasadas -----------------------------
        if len(ticks) >= 2:
            hueco = DoubleArrow(ticks[0].get_center(),
                                ticks[1].get_center(), buff=0.0,
                                stroke_color=C_PERDIDO, stroke_width=3.0,
                                tip_length=0.16, color=C_PERDIDO)
            hueco.set_z_index(10)
            self.play(Create(hueco), run_time=0.8)
        grados = medida(f"{co['grados_por_vuelta']:.2f}", "grados al oeste",
                        "en cada vuelta", color=C_MEDIDO, color_sub=C_PERDIDO)
        nuevos = [grados.etiqueta, grados.numero, grados.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.8)

        km = medida(f"{co['km_ecuador']:.0f}", "km de ecuador",
                    "en 95.5 minutos", color=C_MEDIDO, color_sub=C_PERDIDO)
        nuevos = [km.etiqueta, km.numero, km.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(4.9)

        fundido_final(self, run_time=0.9, cola=0.5)
