class Clip(Scene):
    """04 · La huella — lo poco que ve uno.

    Dos imagenes. Primero de perfil: el satelite a 550 km, los dos rayos que
    rozan el suelo con 10 grados de elevacion y el trozo de planeta que
    queda dentro. Despues, esa misma tapa sobre el mapa del mundo, para que
    se vea de que tamaño es en realidad: 1664 km de radio y el 1.70 % de la
    Tierra.

    El angulo, el radio y la fraccion los calculan `angulo_cobertura`,
    `radio_huella_km` y `fraccion_visible`. La fraccion se saca de la ESFERA
    —(1 - cos psi)/2— y no contando celdas del mapa plano, que infla los
    casquetes cerca de los polos.
    """

    ALTURA_KM = 550.0
    EL_MIN = 10.0
    R_GLOBO = 1.95
    RES_MAPA = (720, 360)

    def construct(self):
        psi = sa.angulo_cobertura(self.ALTURA_KM, self.EL_MIN)
        radio_km = sa.radio_huella_km(self.ALTURA_KM, self.EL_MIN)
        frac = sa.fraccion_visible(self.ALTURA_KM, self.EL_MIN)

        marca = hud_pieza("04 . la huella")
        y_globo = 1.55
        tierra = globo(self.R_GLOBO, y=y_globo, relleno=0.45)
        centro = tierra.get_center()
        r_orb = self.R_GLOBO * (1.0 + self.ALTURA_KM / sa.R_TIERRA_KM)
        p_sat = centro + UP * r_orb
        sat = Dot(p_sat, radius=0.095, color=C_SAT)

        def en_globo(grados):
            a = np.radians(90.0 + grados)
            return centro + self.R_GLOBO * np.array([np.cos(a), np.sin(a), 0])

        borde_izq, borde_der = en_globo(psi), en_globo(-psi)
        rayo_izq = Line(p_sat, borde_izq, stroke_color=C_ENLACE,
                        stroke_width=2.2, stroke_opacity=0.9)
        rayo_der = Line(p_sat, borde_der, stroke_color=C_ENLACE,
                        stroke_width=2.2, stroke_opacity=0.9)
        tapa = Arc(radius=self.R_GLOBO, start_angle=np.radians(90.0 - psi),
                   angle=np.radians(2 * psi), stroke_color=C_ENLACE,
                   stroke_width=6.0, arc_center=centro)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(Create(tierra), run_time=0.9)
        self.play(FadeIn(sat, scale=1.9), run_time=0.5)
        self.wait(0.5)
        self.play(Create(rayo_izq), Create(rayo_der), run_time=1.0)
        self.play(Create(tapa), run_time=0.9)

        pie = medida(f"{psi:.2f}", "grados de tapa", "10 de elevacion",
                     color=C_MEDIDO, color_sub=C_ENLACE)
        self.play(FadeIn(pie.etiqueta), FadeIn(pie.sub),
                  FadeIn(pie.numero, scale=1.06), run_time=0.55)
        self.wait(2.3)

        km = medida(f"{radio_km:.0f}", "km de radio", "sobre el suelo",
                    color=C_MEDIDO, color_sub=C_ENLACE)
        cambiar(self, [pie.etiqueta, pie.numero, pie.sub],
                [km.etiqueta, km.numero, km.sub], salida=0.24, entrada=0.30)
        self.play(tapa.animate.set_stroke(width=9.0), run_time=0.5,
                  rate_func=there_and_back)
        self.wait(2.1)

        # --- la misma tapa, sobre el mapa del mundo ------------------
        paleta = dict(sa.COLORES_MAPA)
        paleta["cobertura"] = C_ENLACE          # el cian esta reservado a
        paleta["solape"] = C_SAT                # las cifras medidas
        base = sa.mapa_tierra(self.RES_MAPA, reticula=True)
        conteo = sa.conteo_cobertura(self.RES_MAPA, [[10.0, 22.0]], psi)
        pintado = sa.colorear_cobertura(base, conteo, colores=paleta,
                                        alpha1=0.62)
        mapa = ImageMobject(np.ascontiguousarray(pintado))
        mapa.set_resampling_algorithm(3)
        # El mapa es 2:1, asi que ancho = 2 x alto: alto 2.88 da 5.76 de
        # ancho, justo la zona segura. (Con 2.88/2 salio a la mitad y el
        # mundo entero cabia en un sello.)
        mapa.height = 2.88
        mapa.move_to(UP * y_globo)

        por_ciento = medida(f"{100 * frac:.2f}", "por ciento", "de la tierra",
                            color=C_MEDIDO, color_sub=C_ENLACE)
        self.play(FadeOut(tierra), FadeOut(sat), FadeOut(rayo_izq),
                  FadeOut(rayo_der), FadeOut(tapa), run_time=0.7)
        self.play(FadeIn(mapa), run_time=0.9)
        cambiar(self, [km.etiqueta, km.numero, km.sub],
                [por_ciento.etiqueta, por_ciento.numero, por_ciento.sub],
                salida=0.24, entrada=0.30)
        self.wait(3.0)

        # --- y esa tapa no se queda quieta --------------------------
        # Se precalculan los frames y se intercambia el pixel_array, como
        # hace `animar_cobertura`; aqui a mano porque esa funcion pinta con
        # el cian de COLORES_MAPA y el cian esta reservado a las cifras.
        n_frames = 44
        trazas = sa.subsatelites_walker(n_frames, 1, 1, 53.0, self.ALTURA_KM,
                                        vueltas=0.55,
                                        duracion_s=0.55 * sa.periodo_orbital(
                                            self.ALTURA_KM)["segundos"])
        lote = [np.ascontiguousarray(
            sa.colorear_cobertura(base,
                                  sa.conteo_cobertura(self.RES_MAPA,
                                                      trazas[k], psi),
                                  colores=paleta, alpha1=0.62))
            for k in range(n_frames)]

        def barrer(mob, alpha):
            mob.pixel_array = lote[int(round(alpha * (n_frames - 1)))]

        vel = medida(f"{sa.velocidad_circular(self.ALTURA_KM):.2f}",
                     "km por segundo", "y se lleva la tapa", color=C_MEDIDO,
                     color_sub=C_ENLACE)
        cambiar(self, [por_ciento.etiqueta, por_ciento.numero,
                       por_ciento.sub],
                [vel.etiqueta, vel.numero, vel.sub], salida=0.24,
                entrada=0.30)
        self.play(UpdateFromAlphaFunc(mapa, barrer), run_time=8.5,
                  rate_func=linear)
        self.wait(4.4)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.9)
        self.remove(*self.mobjects)
        self.wait(0.5)
