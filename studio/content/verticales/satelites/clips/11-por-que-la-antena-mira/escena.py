class Clip(Scene):
    """11 · Por que la antena mira — la energia se reparte.

    Lo que sale del satelite no se pierde: se REPARTE. La misma potencia
    sobre una esfera que no para de crecer, y la antena de abajo solo recoge
    el trocito que le toca. La cuenta tiene nombre —perdida de espacio
    libre— y es la razon de que una parabolica sea grande y mire fijo.

    Desde 550 km son 168.84 dB. Desde la orbita geoestacionaria, 205.11.
    Treinta y seis decibelios de diferencia: **cuatro mil doscientas veces
    menos señal** en la misma antena. Las tres cifras las da
    `satelites.fspl_db` durante el render.
    """

    F_GHZ = 12.0
    LEO_KM = 550.0
    GEO_KM = 35786.0

    def construct(self):
        db_leo = sa.fspl_db(self.LEO_KM, self.F_GHZ)
        db_geo = sa.fspl_db(self.GEO_KM, self.F_GHZ)
        veces = 10.0 ** ((db_geo - db_leo) / 10.0)

        marca = hud_pieza("11 . la antena mira")
        y_sat, y_ant = 3.55, -0.75
        sat = Dot([0, y_sat, 0], radius=0.095, color=C_SAT)
        plato = Arc(radius=0.42, start_angle=PI * 0.18, angle=PI * 0.64,
                    stroke_color=C_TIERRA, stroke_width=4.0)
        plato.move_to([0, y_ant, 0])
        base = Line([0, y_ant - 0.42, 0], [0, y_ant - 0.02, 0],
                    stroke_color=C_TIERRA, stroke_width=3.0)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(sat, scale=1.9), run_time=0.5)
        self.play(Create(plato), Create(base), run_time=0.7)
        self.wait(0.4)

        # --- la misma energia sobre una esfera que crece ------------
        def frente(radio, opacidad):
            c = Circle(radius=radio, stroke_color=C_ENLACE, stroke_width=3.0,
                       stroke_opacity=opacidad)
            c.move_to([0, y_sat, 0])
            return c

        ondas = VGroup(*[frente(0.30, 0.9) for _ in range(4)])
        self.add(ondas)

        def expandir(grupo, alpha):
            for i, onda in enumerate(grupo):
                fase = (alpha * 2.0 + i / len(grupo)) % 1.0
                r = 0.30 + fase * 4.10
                onda.become(frente(r, 0.9 * (1.0 - fase) ** 1.4))

        pie = medida(f"{db_leo:.2f}", "decibelios", "a 550 km",
                     color=C_MEDIDO, color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(UpdateFromAlphaFunc(ondas, expandir), run_time=4.0,
                  rate_func=linear)
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.play(UpdateFromAlphaFunc(ondas, expandir), run_time=3.0,
                  rate_func=linear)
        self.wait(1.6)

        # --- y ahora el mismo satelite, 65 veces mas lejos -----------
        # El salto de escala NO se dibuja a escala (35786 km no caben en una
        # pantalla junto a 550): el satelite se encoge y se declara con la
        # distancia. Lo que SI es exacto es la cifra.
        geo = medida(f"{db_geo:.2f}", "decibelios", "a 35786 km",
                     color=C_MEDIDO, color_sub=C_EXTERNO)
        nuevos = [geo.etiqueta, geo.numero, geo.sub]
        self.play(sat.animate.scale(0.45).set_opacity(0.55),
                  ondas.animate.set_stroke(opacity=0.22), run_time=1.2)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(2.6)

        # --- lo que significan 36 decibelios ------------------------
        cuantas = medida(f"{veces:.0f}", "veces menos", "en la misma antena",
                         color=C_MEDIDO, color_sub=C_ENLACE)
        nuevos = [cuantas.etiqueta, cuantas.numero, cuantas.sub]
        resta = medida(f"{db_geo - db_leo:.2f}", "decibelios mas",
                       "solo la distancia", color=C_MEDIDO,
                       color_sub=C_ENLACE)
        cambiar(self, vivos, [resta.etiqueta, resta.numero, resta.sub],
                salida=0.24, entrada=0.30)
        vivos = [resta.etiqueta, resta.numero, resta.sub]
        self.wait(2.8)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.play(plato.animate.set_stroke(width=6.5), run_time=0.6,
                  rate_func=there_and_back)
        self.wait(2.8)

        # --- y que hace falta para recuperarlos ---------------------
        # La ganancia de una parabolica va con el CUADRADO del diametro,
        # asi que recuperar 4234 veces pide una antena raiz(4234) = 65
        # veces mas ancha. Por eso las de GEO son platos y las de LEO,
        # cajas del tamaño de una pizza.
        ancha = np.sqrt(veces)
        plato_grande = Arc(radius=0.42 * 2.6, start_angle=PI * 0.18,
                           angle=PI * 0.64, stroke_color=C_TIERRA,
                           stroke_width=4.0)
        plato_grande.move_to([0, y_ant + 0.15, 0])
        diametro = medida(f"{ancha:.0f}", "veces mas ancha",
                          "para recuperarlas", color=C_MEDIDO,
                          color_sub=C_TIERRA)
        nuevos = [diametro.etiqueta, diametro.numero, diametro.sub]
        self.play(FadeOut(sat), FadeOut(ondas), run_time=0.5)
        self.play(Transform(plato, plato_grande), run_time=1.4)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(3.2)

        fundido_final(self, run_time=0.9, cola=0.5)
