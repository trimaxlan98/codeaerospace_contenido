class Clip(Scene):
    """12 · El trafico no esta repartido — la mayor parte del rato, sobre agua.

    La constelacion no sabe donde vive la gente: sigue su orbita. Y como el
    71 % del planeta es mar, el 70.7 % del tiempo-satelite se pasa sobre
    agua. Cada punto que se enciende en verde esta sobre tierra firme; los
    naranjas, sobre el oceano, con toda su capacidad apuntando a nada.

    La cuenta la hace `satelites.tiempo_sobre_mar` con la mascara de
    continentes de la propia libreria (poligonos incluidos en el modulo, no
    datos externos), muestreando 32 instantes de una orbita.
    """

    ALTURA_KM = 550.0
    RES_MAPA = (720, 360)
    RES_MASCARA = (480, 240)
    PLANOS, POR_PLANO = 12, 10
    INSTANTES = 32

    def construct(self):
        cuenta = sa.tiempo_sobre_mar(self.PLANOS, self.POR_PLANO,
                                     self.ALTURA_KM, 53.0, self.INSTANTES,
                                     self.RES_MASCARA)
        mask = sa.mascara_tierra(self.RES_MASCARA)
        res_y, res_x = mask.shape

        marca = hud_pieza("12 . sobre el agua")
        mapa = sa.imagen_mapa(self.RES_MAPA, alto_escena=2.88)
        mapa.move_to(UP * (Y_ESCENA + 0.30))

        def en_tierra(lonlat):
            ix = np.clip(((lonlat[:, 0] + 180.0) / 360.0
                          * (res_x - 1)).astype(int), 0, res_x - 1)
            iy = np.clip(((90.0 - lonlat[:, 1]) / 180.0
                          * (res_y - 1)).astype(int), 0, res_y - 1)
            return mask[iy, ix]

        instantes = []
        for k in range(self.INSTANTES):
            ll = sa.subsatelites_walker(2, self.PLANOS, self.POR_PLANO, 53.0,
                                        self.ALTURA_KM, vueltas=0.0,
                                        fase0=k / self.INSTANTES)[0]
            instantes.append((sa.puntos_en_mapa(mapa, ll), en_tierra(ll)))

        puntos, tierra0 = instantes[0]
        enjambre = VGroup(*[Dot(p, radius=0.045,
                                color=C_TIERRA if t else C_PERDIDO,
                                fill_opacity=0.95 if t else 0.55)
                            for p, t in zip(puntos, tierra0)]).set_z_index(14)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(mapa), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(d, scale=1.6) for d in enjambre],
                              lag_ratio=0.006), run_time=1.8)

        n_tierra = int(tierra0.sum())
        pie = medida(f"{n_tierra}", "sobre tierra",
                     f"de {len(tierra0)} arriba", color=C_MEDIDO,
                     color_sub=C_TIERRA)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.wait(2.2)

        # --- y ahora, una orbita entera ------------------------------
        def mover(_g, alpha):
            k = int(round(alpha * (self.INSTANTES - 1)))
            pts, ten = instantes[k]
            for dot, p, t in zip(enjambre, pts, ten):
                dot.move_to(p)
                dot.set_color(C_TIERRA if t else C_PERDIDO)
                dot.set_opacity(0.95 if t else 0.55)

        girar = medida(f"{100 * cuenta['fraccion_tierra']:.1f}", "por ciento",
                       "en tierra firme", color=C_MEDIDO,
                       color_sub=C_TIERRA)
        nuevos = [girar.etiqueta, girar.numero, girar.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.play(UpdateFromAlphaFunc(enjambre, mover), run_time=11.0,
                  rate_func=linear)
        self.wait(1.4)

        # --- el reverso: lo que se riega en el mar -------------------
        mar = medida(f"{100 * cuenta['fraccion_mar']:.1f}", "por ciento",
                     "apuntando al mar", color=C_MEDIDO, color_sub=C_PERDIDO)
        nuevos = [mar.etiqueta, mar.numero, mar.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.4)

        # --- y ni siquiera es constante ------------------------------
        cuentas = [int(ten.sum()) for _, ten in instantes]
        vaiven = medida(f"{max(cuentas)}", "como mucho",
                        f"y a veces {min(cuentas)}", color=C_MEDIDO,
                        color_sub=C_TIERRA)
        nuevos = [vaiven.etiqueta, vaiven.numero, vaiven.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(5.40)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.9)
        self.remove(*self.mobjects)
        self.wait(0.5)
