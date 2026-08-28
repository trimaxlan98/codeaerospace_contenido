class Clip(Scene):
    """10 · La malla — el atajo por arriba.

    Un paquete de Nueva York a Londres. Por fibra recorre el cable, que ni
    va recto ni lleva la luz a su velocidad: 7802 km a dos tercios de c.
    Por la malla sube, salta de satelite en satelite por el vacio y baja:
    mas kilometros (6977 contra los 5573 del gran circulo) y aun asi llega
    antes.

    El camino lo resuelve `satelites.ruta_malla` con Dijkstra sobre los
    saltos REALES, descartando los que rozarian la atmosfera. El rodeo del
    cable (1.4x) y los 2c/3 son SUPUESTOS de ingenieria, no medidas: por eso
    la cifra de la fibra va en gris.
    """

    ALTURA_KM = 550.0
    RES_MAPA = (720, 360)
    NY = (-74.0, 40.7)
    LONDRES = (-0.1, 51.5)

    def construct(self):
        lonlat = sa.subsatelites_walker(2, 18, 12, 53.0, self.ALTURA_KM,
                                        vueltas=0.0)[0]
        ruta = sa.ruta_malla(self.NY, self.LONDRES, lonlat, self.ALTURA_KM,
                             elevacion_min_deg=20.0, isl_max_km=5000.0)
        fibra = sa.latencia_fibra(self.NY, self.LONDRES)

        marca = hud_pieza("10 . la malla")
        mapa = sa.imagen_mapa(self.RES_MAPA, alto_escena=2.88)
        mapa.move_to(UP * (Y_ESCENA + 0.30))

        def en_mapa(lonlat_):
            return sa.puntos_en_mapa(mapa, lonlat_)

        # El gran circulo de verdad (slerp entre los dos vectores unitarios),
        # no una recta sobre el mapa plano: en equirrectangular la recta NO
        # es el camino corto y se veria una ruta que nadie recorre.
        def gran_circulo(a, b, n=60):
            va, vb = [np.array([np.cos(np.radians(p[1])) * np.cos(np.radians(p[0])),
                                np.cos(np.radians(p[1])) * np.sin(np.radians(p[0])),
                                np.sin(np.radians(p[1]))]) for p in (a, b)]
            om = np.arccos(np.clip(va @ vb, -1, 1))
            s = np.linspace(0, 1, n)[:, None]
            v = (np.sin((1 - s) * om) * va + np.sin(s * om) * vb) / np.sin(om)
            return np.column_stack([np.degrees(np.arctan2(v[:, 1], v[:, 0])),
                                    np.degrees(np.arcsin(np.clip(v[:, 2], -1, 1)))])

        p_ny, p_ld = en_mapa([self.NY])[0], en_mapa([self.LONDRES])[0]
        ciudad_a = Dot(p_ny, radius=0.075, color=C_TIERRA).set_z_index(20)
        ciudad_b = Dot(p_ld, radius=0.075, color=C_TIERRA).set_z_index(20)
        cable = poli(en_mapa(gran_circulo(self.NY, self.LONDRES))[:, :2],
                     color=C_EXTERNO, grosor=2.6, opacidad=0.85, suave=True)
        cable.set_z_index(12)

        enjambre = VGroup(*[Dot(p, radius=0.030, color=C_SAT,
                                fill_opacity=0.55)
                            for p in en_mapa(lonlat)]).set_z_index(14)

        saltos_pts = np.vstack([[p_ny], en_mapa(ruta["lonlat_saltos"]),
                                [p_ld]])
        tramos = VGroup(*[Line(saltos_pts[k], saltos_pts[k + 1],
                               stroke_color=C_ENLACE, stroke_width=4.4)
                          for k in range(len(saltos_pts) - 1)]).set_z_index(18)
        nodos = VGroup(*[Dot(p, radius=0.070, color=C_ENLACE)
                         for p in saltos_pts[1:-1]]).set_z_index(19)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(mapa), run_time=0.9)
        self.play(FadeIn(ciudad_a, scale=1.8), FadeIn(ciudad_b, scale=1.8),
                  run_time=0.6)

        # --- por el cable -------------------------------------------
        pie = medida(f"{fibra['latencia_ms']:.1f}", "ms por fibra",
                     "1.4 de rodeo, 2c/3", color=C_EXTERNO,
                     color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(Create(cable), run_time=1.6)
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.wait(2.6)

        # --- por arriba ---------------------------------------------
        self.play(LaggedStart(*[FadeIn(d, scale=1.6) for d in enjambre],
                              lag_ratio=0.004), run_time=1.6)
        saltos = medida(f"{ruta['saltos']}", "saltos", "y ninguno toca aire",
                        color=C_MEDIDO, color_sub=C_ENLACE)
        nuevos = [saltos.etiqueta, saltos.numero, saltos.sub]
        self.play(LaggedStart(*[Create(x) for x in tramos], lag_ratio=0.55),
                  run_time=2.4)
        self.play(FadeIn(nodos, scale=1.5), run_time=0.5)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(2.4)

        km = medida(f"{ruta['km']:.0f}", "km por la malla",
                    f"recto son {fibra['gran_circulo_km']:.0f}",
                    color=C_MEDIDO, color_sub=C_EXTERNO)
        nuevos = [km.etiqueta, km.numero, km.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(2.8)

        # --- mas camino y aun asi antes ------------------------------
        ms = medida(f"{ruta['latencia_ms']:.1f}", "ms por la malla",
                    f"contra {fibra['latencia_ms']:.0f} de fibra",
                    color=C_MEDIDO, color_sub=C_EXTERNO)
        nuevos = [ms.etiqueta, ms.numero, ms.sub]
        self.play(cable.animate.set_stroke(opacity=0.30),
                  tramos.animate.set_stroke(width=5.4), run_time=0.7)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(2.8)

        # --- mas kilometros y aun asi antes: las dos latencias -------
        escala_b = 2.30 / fibra["latencia_ms"]
        y_base = 0.20
        x_a, x_b = -1.35, 1.35
        alto_a = ruta["latencia_ms"] * escala_b
        alto_b = fibra["latencia_ms"] * escala_b
        rot_a = hud("por arriba", font_size=18, color=C_ENLACE)
        rot_b = hud("por cable", font_size=18, color=C_EXTERNO)
        rot_a.move_to([x_a, y_base + alto_b + 0.40, 0])
        rot_b.move_to([x_b, y_base + alto_b + 0.40, 0])
        barra_a = Rectangle(width=0.70, height=alto_a, stroke_width=0,
                            fill_color=C_ENLACE, fill_opacity=0.85)
        barra_b = Rectangle(width=0.70, height=alto_b, stroke_width=0,
                            fill_color=C_EXTERNO, fill_opacity=0.70)
        barra_a.move_to([x_a, y_base + alto_a / 2, 0])
        barra_b.move_to([x_b, y_base + alto_b / 2, 0])
        ventaja = medida(f"{fibra['latencia_ms'] - ruta['latencia_ms']:.1f}",
                         "ms de ventaja", "y mas camino", color=C_MEDIDO,
                         color_sub=C_ENLACE)
        nuevos = [ventaja.etiqueta, ventaja.numero, ventaja.sub]
        self.play(FadeOut(mapa), FadeOut(enjambre), FadeOut(cable),
                  FadeOut(tramos), FadeOut(nodos), FadeOut(ciudad_a),
                  FadeOut(ciudad_b), run_time=0.8)
        self.play(FadeIn(rot_a), FadeIn(rot_b), run_time=0.45)
        for barra, alto, x in ((barra_a, alto_a, x_a), (barra_b, alto_b, x_b)):
            barra.save_state()
            barra.stretch_to_fit_height(0.02)
            barra.move_to([x, y_base + 0.01, 0])
        self.add(barra_a, barra_b)
        self.play(Restore(barra_a), Restore(barra_b), run_time=1.5,
                  rate_func=rate_functions.ease_out_cubic)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(3.7)

        fundido_final(self, run_time=0.9, cola=0.5)
