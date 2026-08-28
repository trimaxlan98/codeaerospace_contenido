class Clip(Scene):
    """07 · Uno no basta — la cuenta de la cobertura.

    El mapa se va pintando: uno solo tapa el 1.7 %; seis, el 8; veinticuatro,
    el 37; sesenta y seis, tres cuartas partes; con doscientos cuarenta ya
    casi no quedan huecos. La cifra sube con la imagen, y las dos salen del
    MISMO instante: se pinta la constelacion y se mide esa misma foto.

    El porcentaje se pesa por cos(lat) (`fraccion_cubierta`): contar celdas
    del mapa equirrectangular a secas infla los casquetes polares y da un
    numero que no es el de la esfera.
    """

    ALTURA_KM = 550.0
    EL_MIN = 10.0
    RES_MAPA = (720, 360)
    CONFIGS = ((1, 1), (2, 3), (4, 6), (6, 11), (12, 20))

    def construct(self):
        psi = sa.angulo_cobertura(self.ALTURA_KM, self.EL_MIN)
        paleta = dict(sa.COLORES_MAPA)
        paleta["cobertura"] = C_ENLACE       # el cian es de las cifras
        paleta["solape"] = C_SAT
        base = sa.mapa_tierra(self.RES_MAPA, reticula=True)

        # Se pinta y se mide la MISMA foto: si la cifra viniera de un
        # promedio sobre varios instantes y la imagen de uno solo, el
        # espectador estaria viendo un mapa y leyendo otro numero.
        pintados, fracciones, enes = [], [], []
        for planos, por_plano in self.CONFIGS:
            lonlat = sa.subsatelites_walker(2, planos, por_plano, 53.0,
                                            self.ALTURA_KM, vueltas=0.0)[0]
            conteo = sa.conteo_cobertura(self.RES_MAPA, lonlat, psi)
            pintados.append(np.ascontiguousarray(
                sa.colorear_cobertura(base, conteo, colores=paleta,
                                      alpha1=0.60, alpha2=0.80)))
            fracciones.append(sa.fraccion_cubierta(conteo))
            enes.append(planos * por_plano)

        marca = hud_pieza("07 . uno no basta")
        mapa = ImageMobject(pintados[0])
        mapa.set_resampling_algorithm(3)
        mapa.height = 2.88
        mapa.move_to(UP * Y_ESCENA)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(mapa), run_time=0.9)

        pie = medida(f"{100 * fracciones[0]:.2f}", "por ciento",
                     f"{enes[0]} satelite", color=C_MEDIDO,
                     color_sub=C_ENLACE)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.wait(2.4)

        for k in range(1, len(self.CONFIGS)):
            nuevo = medida(f"{100 * fracciones[k]:.2f}", "por ciento",
                           f"{enes[k]} satelites", color=C_MEDIDO,
                           color_sub=C_ENLACE)
            nuevos = [nuevo.etiqueta, nuevo.numero, nuevo.sub]
            self.play(FadeOut(mapa, scale=0.98), run_time=0.28)
            mapa.pixel_array = pintados[k]
            self.play(FadeIn(mapa, scale=1.02), run_time=0.34)
            cambiar(self, vivos, nuevos, salida=0.22, entrada=0.28)
            vivos = nuevos
            self.wait(2.6 if k < len(self.CONFIGS) - 1 else 0.6)

        # --- lo que NO se cierra: los polos --------------------------
        lm = sa.latitud_maxima_cubierta(53.0, self.ALTURA_KM, self.EL_MIN)
        y_lim = mapa.get_center()[1] + (lm["lat_max_deg"] / 180.0) * mapa.height
        raya_n = Line([-mapa.width / 2, y_lim, 0], [mapa.width / 2, y_lim, 0],
                      stroke_color=C_PERDIDO, stroke_width=2.6)
        raya_s = raya_n.copy().shift(DOWN * 2 * (y_lim - mapa.get_center()[1]))
        for r in (raya_n, raya_s):
            r.set_z_index(10)
        limite = medida(f"{lm['lat_max_deg']:.0f}", "grados de latitud",
                        "y mas arriba, nada", color=C_MEDIDO,
                        color_sub=C_PERDIDO)
        nuevos = [limite.etiqueta, limite.numero, limite.sub]
        self.play(Create(raya_n), Create(raya_s), run_time=0.8)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.4)

        # --- y donde se pisan es donde se puede relevar --------------
        lonlat = sa.subsatelites_walker(2, *self.CONFIGS[-1], 53.0,
                                        self.ALTURA_KM, vueltas=0.0)[0]
        conteo = sa.conteo_cobertura(self.RES_MAPA, lonlat, psi)
        dos = sa.fraccion_cubierta(conteo, minimo=2)
        solape = medida(f"{100 * dos:.1f}", "con dos o mas", "y ahi hay relevo",
                        color=C_MEDIDO, color_sub=C_SAT)
        nuevos = [solape.etiqueta, solape.numero, solape.sub]
        self.play(FadeOut(raya_n), FadeOut(raya_s), run_time=0.5)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(5.3)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.9)
        self.remove(*self.mobjects)
        self.wait(0.5)
