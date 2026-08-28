class Clip(Scene):
    """09 · El relevo — la llamada no se corta.

    Desde un punto del suelo, cada satelite sube, culmina y se pone en unos
    minutos. Lo que hace que la conexion no se caiga es que, antes de que
    uno se ponga, otro ya esta suficientemente alto: el enlace SALTA. Aqui
    se ve la envolvente —el satelite mas alto en cada instante— y cada
    salto marcado.

    Y la cifra honesta: con 66 satelites y una mascara de 25 grados, sobre
    esta estacion no hay servicio el 71 % del tiempo. Por eso las
    constelaciones de hoy se cuentan por miles y no por decenas.

    Todo lo mide `satelites.relevos`, que mira instante a instante cual es
    el satelite mas alto y cuenta los cambios.
    """

    LAT, LON = 19.43, -99.13
    EL_MIN = 25.0
    DURACION_S = 5400.0               # 90 minutos
    ANCHO, ALTO = 5.60, 3.60

    def _marco(self, y):
        marco = Rectangle(width=self.ANCHO, height=self.ALTO, stroke_width=0)
        marco.move_to(UP * y)
        return marco

    def construct(self):
        r66 = sa.relevos(self.LAT, self.LON, planos=6, por_plano=11,
                         altitud_km=550.0, elevacion_min_deg=self.EL_MIN,
                         duracion_s=self.DURACION_S, muestras=420)
        y_c = Y_ESCENA + 0.55
        marco = self._marco(y_c)
        x0, y0 = marco.get_corner(DL)[0], marco.get_corner(DL)[1]

        def punto(t_s, el):
            return np.array([x0 + self.ANCHO * t_s / self.DURACION_S,
                             y0 + self.ALTO * np.clip(el, 0, 90) / 90.0, 0.0])

        marca = hud_pieza("09 . el relevo")
        suelo = Line(punto(0, 0), punto(self.DURACION_S, 0),
                     stroke_color=C_EJE, stroke_width=2.2)
        umbral = DashedVMobject(
            Line(punto(0, self.EL_MIN), punto(self.DURACION_S, self.EL_MIN),
                 stroke_color=C_PERDIDO, stroke_width=2.0), num_dashes=48)

        # Una curva por satelite que llegue a asomar sobre el horizonte.
        t = r66["t_s"]
        curvas = VGroup()
        for k in range(r66["elevaciones"].shape[1]):
            e = r66["elevaciones"][:, k]
            if e.max() < 2.0:
                continue
            visible = e > 0.0
            pts = [punto(tt, ee) for tt, ee in zip(t[visible], e[visible])]
            if len(pts) < 2:
                continue
            curvas.add(poli(np.array(pts)[:, :2], color=C_EJE, grosor=2.0,
                            opacidad=0.85))

        envolvente = poli(np.array([punto(tt, ee) for tt, ee
                                    in zip(t, np.clip(r66["el_max"], 0, 90))
                                    ])[:, :2], color=C_SAT, grosor=3.4)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(Create(suelo), run_time=0.6)
        self.play(LaggedStart(*[Create(c) for c in curvas], lag_ratio=0.05),
                  run_time=3.4)
        self.wait(0.4)
        self.play(Create(envolvente), run_time=2.6)
        self.play(Create(umbral), run_time=0.9)

        # --- cada cambio de satelite es un salto --------------------
        serv = r66["servidor"]
        saltos = [k for k in range(1, len(serv)) if serv[k] != serv[k - 1]]
        ticks = VGroup(*[Line(punto(t[k], 0) + DOWN * 0.14,
                              punto(t[k], 0) + UP * 0.30,
                              stroke_color=C_MEDIDO, stroke_width=2.4)
                         for k in saltos])
        pie = medida(f"{r66['relevos']}", "saltos", "en 90 minutos",
                     color=C_MEDIDO, color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(LaggedStart(*[GrowFromCenter(x) for x in ticks],
                              lag_ratio=0.10), run_time=1.8)
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.wait(2.4)

        cada = medida(f"{r66['intervalo_medio_s'] / 60:.2f}", "minutos",
                      "entre salto y salto", color=C_MEDIDO,
                      color_sub=C_EXTERNO)
        nuevos = [cada.etiqueta, cada.numero, cada.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(2.6)

        # --- lo que no se cuenta en los folletos --------------------
        hueco = medida(f"{100 * r66['fraccion_sin_servicio']:.0f}",
                       "por ciento", "sin nadie arriba", color=C_MEDIDO,
                       color_sub=C_PERDIDO)
        nuevos = [hueco.etiqueta, hueco.numero, hueco.sub]
        bajo = Rectangle(width=self.ANCHO,
                         height=self.ALTO * self.EL_MIN / 90.0,
                         stroke_width=0, fill_color=C_PERDIDO,
                         fill_opacity=0.16)
        bajo.move_to(punto(self.DURACION_S / 2, self.EL_MIN / 2))
        self.play(FadeIn(bajo), run_time=0.6)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.2)

        # --- y por eso hoy se cuentan por miles ---------------------
        r240 = sa.relevos(self.LAT, self.LON, planos=24, por_plano=10,
                          altitud_km=550.0, elevacion_min_deg=self.EL_MIN,
                          duracion_s=self.DURACION_S, muestras=420)
        env240 = poli(np.array([punto(tt, ee) for tt, ee
                                in zip(r240["t_s"],
                                       np.clip(r240["el_max"], 0, 90))
                                ])[:, :2], color=C_SAT, grosor=3.4)
        lleno = medida(f"{100 * r240['fraccion_sin_servicio']:.0f}",
                       "por ciento", f"con {r240['n_satelites']} arriba",
                       color=C_MEDIDO, color_sub=C_TIERRA)
        nuevos = [lleno.etiqueta, lleno.numero, lleno.sub]
        self.play(FadeOut(envolvente), FadeOut(ticks), FadeOut(curvas),
                  run_time=0.6)
        self.play(Create(env240), run_time=2.4)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(4.6)

        fundido_final(self, run_time=0.9, cola=0.5)
