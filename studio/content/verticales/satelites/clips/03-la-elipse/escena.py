class Clip(Scene):
    """03 · La elipse — areas iguales en tiempos iguales.

    La orbita no tiene por que ser un circulo. Se dibuja una elipse de
    verdad (Kepler resuelto por Newton-Raphson) con el planeta en el FOCO, y
    el satelite la recorre en tiempo real: se lanza abajo y se arrastra
    arriba. Despues, la segunda ley MEDIDA: la misma fraccion de periodo
    barre la misma area en los dos extremos, aunque una sea larga y estrecha
    y la otra corta y ancha.

    Las cifras salen de `satelites.elipse_kepler` y `satelites.areas_barridas`
    durante el render. El muestreo es en TIEMPOS iguales, no en angulos: por
    eso los puntos se apelotonan arriba solos.
    """

    A_KM = 25000.0
    EXC = 0.65
    MUESTRAS = 1440
    VENTANA = 0.06                    # fraccion de periodo de cada sector
    APOGEO_EN = 3.60                  # a que altura de escena cae el apogeo

    def construct(self):
        orb = sa.elipse_kepler(self.A_KM, self.EXC, muestras=self.MUESTRAS + 1)
        pts_km = orb["puntos"][:-1]
        n = len(pts_km)
        medido = sa.areas_barridas(self.A_KM, self.EXC, ventana=self.VENTANA,
                                   muestras=self.MUESTRAS)

        # Girar -90 grados deja el perigeo abajo (pegado al planeta) y el
        # apogeo arriba: es lo que aprovecha una pantalla en columna.
        r_apo = self.A_KM * (1 + self.EXC)
        r_peri = self.A_KM * (1 - self.EXC)
        escala = self.APOGEO_EN / r_apo
        # El conjunto va de -r_peri a +r_apo; se centra ese tramo en la
        # zona de dibujo en vez de centrar el foco, que lo dejaria alto.
        y_foco = Y_ESCENA - (self.APOGEO_EN - r_peri * escala) / 2.0
        foco = np.array([0.0, y_foco, 0.0])

        def a_escena(p):
            p = np.atleast_2d(np.asarray(p, dtype=np.float64))
            girado = np.column_stack([p[:, 1], -p[:, 0]])
            xy = girado * escala
            return np.column_stack([xy[:, 0] + foco[0], xy[:, 1] + foco[1],
                                    np.zeros(len(xy))])

        pts = a_escena(pts_km)
        r_tierra = sa.R_TIERRA_KM * escala

        marca = hud_pieza("03 . la elipse")
        tierra = globo(r_tierra, y=foco[1], relleno=0.55)
        tierra.set_z_index(20)
        curva = poli(pts[:, :2], color=C_EJE, grosor=2.6, opacidad=1.0)
        curva.add_points_as_corners([pts[0]])

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(Create(curva), run_time=1.6)
        self.play(GrowFromCenter(tierra), run_time=0.7)
        self.wait(0.4)

        # --- el satelite la recorre a su ritmo real ------------------
        sat = Dot(radius=0.10, color=C_SAT).set_z_index(30)
        sat.move_to(pts[0])
        estela = TracedPath(sat.get_center, stroke_color=C_SAT,
                            stroke_width=3.4, stroke_opacity=0.9)
        estela.set_z_index(15)
        # UN solo pie vivo en cada momento: `vivos` es lo que esta en
        # pantalla. En el primer render se relevaron etiqueta y numero pero
        # no el sub, y "km / s" se quedo debajo de los dos rotulos
        # siguientes ("MISKM / SIEMPO" en el frame). El relevo se hace
        # SIEMPRE sobre lo que de verdad esta puesto.
        pie = medida(f"{medido['v_perigeo_km_s']:.2f}", "abajo", "km / s",
                     color=C_MEDIDO, color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.add(estela)
        self.play(FadeIn(sat, scale=1.8), *[FadeIn(m) for m in vivos],
                  run_time=0.55)

        def recorrer(mob, alpha):
            mob.move_to(pts[int(round(alpha * (n - 1)))])

        self.play(UpdateFromAlphaFunc(sat, recorrer), run_time=6.5,
                  rate_func=linear)
        arriba = medida(f"{medido['v_apogeo_km_s']:.2f}", "arriba", "km / s",
                        color=C_MEDIDO, color_sub=C_EXTERNO)
        nuevos = [arriba.etiqueta, arriba.numero, arriba.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.28)
        vivos = nuevos
        self.play(UpdateFromAlphaFunc(sat, recorrer), run_time=6.5,
                  rate_func=linear)
        self.remove(estela)
        self.play(FadeOut(sat), run_time=0.4)

        # --- los puntos, uno por cada tramo IGUAL de tiempo ----------
        paso = n // 48
        marcas = VGroup(*[Dot(pts[k], radius=0.05, color=C_SAT,
                              fill_opacity=0.9).set_z_index(15)
                          for k in range(0, n, paso)])
        cociente = medida(f"{medido['cociente_v']:.2f}", "veces",
                          "mas rapido abajo", color=C_MEDIDO,
                          color_sub=C_EXTERNO)
        nuevos = [cociente.etiqueta, cociente.numero, cociente.sub]
        self.play(LaggedStart(*[FadeIn(m, scale=1.6) for m in marcas],
                              lag_ratio=0.014), run_time=2.0)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.28)
        vivos = nuevos
        self.wait(2.2)

        # --- los dos sectores: misma area en el mismo tiempo ---------
        ancho = max(3, int(self.VENTANA * n))
        idx_peri = np.roll(np.arange(n), ancho // 2)[:ancho]
        k = n // 2
        idx_apo = np.arange(k - ancho // 2, k - ancho // 2 + ancho)
        sector_peri = Polygon(foco, *pts[idx_peri], stroke_width=1.6,
                              stroke_color=C_SAT, fill_color=C_SAT,
                              fill_opacity=0.55)
        sector_apo = Polygon(foco, *pts[idx_apo], stroke_width=1.6,
                             stroke_color=C_ENLACE, fill_color=C_ENLACE,
                             fill_opacity=0.65)
        # ENCIMA del planeta, no debajo: el area se barre desde el FOCO, que
        # es el centro de la Tierra, asi que el sector del perigeo incluye
        # de verdad el trozo que ocupa el disco. Debajo se veia solo una
        # uña de ambar asomando y la igualdad no se leia.
        for s in (sector_peri, sector_apo):
            s.set_z_index(30)
        areas = medida(f"{medido['cociente_areas']:.3f}", "areas iguales",
                       "mismo tiempo", color=C_MEDIDO, color_sub=C_ENLACE)
        nuevos = [areas.etiqueta, areas.numero, areas.sub]
        self.play(FadeOut(marcas), run_time=0.4)
        self.play(FadeIn(sector_peri), run_time=0.9)
        self.wait(0.7)
        self.play(FadeIn(sector_apo), run_time=0.9)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(4.0)

        fundido_final(self, run_time=0.9, cola=0.5)
