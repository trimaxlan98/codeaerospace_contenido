class Clip(Scene):
    """14 · Sobre tu cabeza — el cierre.

    Se apaga el mapa y queda el cielo de un patio cualquiera. Con la
    constelacion de 240 que hemos venido usando, sobre tu horizonte hay
    cuatro. Pero ahi arriba ya no hay 240: hay miles. Y como cada uno ve el
    1.696 % de la Tierra, la cuenta sale sola.

    Las posiciones y la cuenta las da `satelites.sobre_el_horizonte` (con
    `azimut` y `ventana_visibilidad`); la extrapolacion a una constelacion
    de miles se hace con `fraccion_visible`. El numero de satelites que hay
    de verdad hoy es un DATO EXTERNO y va en gris: lo que se calcula aqui es
    lo que implica.
    """

    ALTURA_KM = 550.0
    EL_MIN = 10.0
    LAT, LON = 19.43, -99.13
    PLANOS, POR_PLANO = 24, 10
    FLOTA_HOY = 6000                  # dato externo, declarado en pantalla
    R_BOVEDA = 2.45

    def construct(self):
        cielo_ = sa.sobre_el_horizonte(self.LAT, self.LON, self.PLANOS,
                                       self.POR_PLANO, self.ALTURA_KM, 53.0,
                                       self.EL_MIN)
        frac = sa.fraccion_visible(self.ALTURA_KM, self.EL_MIN)
        estimado = self.FLOTA_HOY * frac
        centro = UP * (Y_ESCENA + 0.35)

        def cielo(az_deg, el_deg):
            r = self.R_BOVEDA * (1.0 - np.clip(el_deg, 0.0, 90.0) / 90.0)
            a = np.radians(90.0 - az_deg)
            return centro + r * np.array([np.cos(a), np.sin(a), 0.0])

        marca = hud_pieza("14 . sobre ti")
        aros = VGroup()
        for grados, ancho in ((0.0, 2.6), (30.0, 1.4), (60.0, 1.4)):
            aro = Circle(radius=self.R_BOVEDA * (1.0 - grados / 90.0),
                         stroke_color=C_EJE, stroke_width=ancho,
                         stroke_opacity=0.9 if grados == 0 else 0.5)
            aro.move_to(centro)
            aros.add(aro)
        yo = Dot(centro, radius=0.075, color=C_TIERRA)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(Create(aros[0]), FadeIn(yo, scale=1.7), run_time=0.9)
        self.play(Create(aros[1]), Create(aros[2]), run_time=0.7)
        self.wait(1.0)

        # --- los que hay ahora mismo, con 240 arriba ----------------
        visibles = VGroup(*[Dot(cielo(a, e), radius=0.085, color=C_SAT)
                            for a, e in zip(cielo_["azimuts"],
                                            cielo_["elevaciones"])])
        pie = medida(f"{cielo_['n_visibles']}", "sobre tu horizonte",
                     f"de {cielo_['n_total']} arriba", color=C_MEDIDO,
                     color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(LaggedStart(*[FadeIn(d, scale=2.2) for d in visibles],
                              lag_ratio=0.30), run_time=2.2)
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.wait(3.2)

        # --- cada uno ve muy poco, y de ahi sale la cuenta ----------
        parte = medida(f"{100 * frac:.3f}", "por ciento cada uno",
                       "y por eso son 4", color=C_MEDIDO, color_sub=C_ENLACE)
        nuevos = [parte.etiqueta, parte.numero, parte.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.4)

        # --- pero arriba ya no hay 240 ------------------------------
        rng = np.random.default_rng(27)
        n_extra = int(round(estimado)) - len(visibles)
        el_extra = np.degrees(np.arcsin(rng.uniform(
            np.sin(np.radians(self.EL_MIN)), 1.0, n_extra)))
        az_extra = rng.uniform(0.0, 360.0, n_extra)
        muchos = VGroup(*[Dot(cielo(a, e), radius=0.075, color=C_SAT,
                              fill_opacity=0.9)
                          for a, e in zip(az_extra, el_extra)])
        flota = nota_externa(f"hoy hay unos {self.FLOTA_HOY}", font_size=16)
        flota.move_to(UP * (centro[1] - self.R_BOVEDA - 0.55))
        cuantos = medida(f"{estimado:.0f}", "sobre tu horizonte",
                         "ahora mismo", color=C_MEDIDO, color_sub=C_SAT)
        nuevos = [cuantos.etiqueta, cuantos.numero, cuantos.sub]
        self.play(FadeIn(flota), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(d, scale=2.0) for d in muchos],
                              lag_ratio=0.006), run_time=3.8)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(2.4)

        # --- y siguen ahi cuando dejas de mirar ---------------------
        todos = VGroup(*visibles, *muchos)
        self.play(todos.animate.set_opacity(0.45), run_time=1.6)
        self.play(todos.animate.set_opacity(1.0), run_time=1.6)
        self.wait(4.6)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=1.3)
        self.remove(*self.mobjects)
        self.wait(0.5)
