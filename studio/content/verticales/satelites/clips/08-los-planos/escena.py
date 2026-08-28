class Clip(Scene):
    """08 · Los planos — por que no llega a los polos.

    La constelacion por dentro: no es una nube, son planos orbitales con el
    nodo repartido y las fases escalonadas. Y ahi esta el limite del clip
    anterior: con 53 grados de inclinacion, ningun satelite pasa nunca por
    encima de los 53, y ni con su huella se llega al polo. Hace falta subir
    la inclinacion por encima de 75.03 grados; Iridium, por eso, va a 86.4.

    La geometria la dibuja `satelites.ConstelacionWalker` (planos con su
    RAAN, proyeccion ortografica y oclusion tras la Tierra). Las cifras,
    `angulo_cobertura`, `latitud_maxima_cubierta` y `fraccion_cubierta`.
    """

    ALTURA_KM = 550.0
    EL_MIN = 10.0
    INCL_A = 53.0                     # la de siempre
    INCL_B = 86.4                     # la de Iridium (dato externo)
    RES_MAPA = (480, 240)

    def _constelacion(self, inclinacion, giro=0.0):
        return sa.ConstelacionWalker(
            planos=6, sats_por_plano=11, inclinacion_deg=inclinacion,
            altitud_km=self.ALTURA_KM, frames=200, vueltas=0.30,
            tilt_deg=24.0, giro_deg=giro, escala=1.95, radio_sat=0.055,
            color_tierra="#14352c", color_orbita=C_EJE, color_sat=C_SAT)

    def _polar(self, inclinacion):
        """Fraccion de la CALOTA polar (de 70 grados para arriba) cubierta."""
        psi = sa.angulo_cobertura(self.ALTURA_KM, self.EL_MIN)
        lonlat = sa.subsatelites_walker(2, 6, 11, inclinacion, self.ALTURA_KM,
                                        vueltas=0.0)[0]
        conteo = sa.conteo_cobertura(self.RES_MAPA, lonlat, psi)
        filas = int(self.RES_MAPA[1] * (90.0 - 70.0) / 180.0)
        return sa.fraccion_cubierta(conteo[:filas])

    def construct(self):
        psi = sa.angulo_cobertura(self.ALTURA_KM, self.EL_MIN)
        incl_min = 90.0 - psi
        lm = sa.latitud_maxima_cubierta(self.INCL_A, self.ALTURA_KM,
                                        self.EL_MIN)
        polar_a, polar_b = self._polar(self.INCL_A), self._polar(self.INCL_B)

        marca = hud_pieza("08 . los planos")
        cons = self._constelacion(self.INCL_A)
        cons.move_to(UP * Y_ESCENA)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(cons.tierra, scale=0.85), run_time=0.8)
        self.play(LaggedStart(*[Create(o) for o in cons.orbitas],
                              lag_ratio=0.18), run_time=2.2)
        self.play(LaggedStart(*[FadeIn(s, scale=1.8) for s in cons.sats],
                              lag_ratio=0.012), run_time=1.2)

        pie = medida(f"{self.INCL_A:.0f}", "grados de plano",
                     "un dato de diseno", color=C_EXTERNO,
                     color_sub=C_EXTERNO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.play(sa.AnimarWalker(cons), run_time=5.5)

        # --- el techo: por encima de esa latitud, nada ---------------
        techo = medida(f"{lm['lat_max_deg']:.1f}", "grados de techo",
                       "plano mas huella", color=C_MEDIDO, color_sub=C_SAT)
        nuevos = [techo.etiqueta, techo.numero, techo.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.play(sa.AnimarWalker(cons), run_time=3.5)

        # --- cuanto haria falta -------------------------------------
        falta = medida(f"{incl_min:.2f}", "grados hacen falta",
                       "para tocar el polo", color=C_MEDIDO, color_sub=C_SAT)
        nuevos = [falta.etiqueta, falta.numero, falta.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.2)

        # --- y por eso Iridium se pone casi vertical ----------------
        cons_b = self._constelacion(self.INCL_B)
        cons_b.move_to(UP * Y_ESCENA)
        iridium = medida(f"{100 * polar_b:.0f}", "por ciento del polo",
                         f"a {self.INCL_B} grados", color=C_MEDIDO,
                         color_sub=C_EXTERNO)
        nuevos = [iridium.etiqueta, iridium.numero, iridium.sub]
        self.play(FadeOut(cons.orbitas), FadeOut(cons.sats), run_time=0.5)
        self.play(LaggedStart(*[Create(o) for o in cons_b.orbitas],
                              lag_ratio=0.14), run_time=1.6)
        self.add(cons_b.sats)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.play(sa.AnimarWalker(cons_b), run_time=4.5)
        self.wait(2.8)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.9)
        self.remove(*self.mobjects)
        self.wait(0.5)
