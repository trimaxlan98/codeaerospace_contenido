class Clip(Scene):
    """13 · La red aprende — apuntar donde hace falta.

    Un satelite no ilumina todo lo que ve: reparte unos pocos haces. Si los
    reparte a ciegas, la mayoria cae donde no hay nadie. Si mira la demanda
    y mueve cada haz a la celda que mas sube el total, sirve siete veces
    mas con los MISMOS haces.

    Honestidad: la matriz de demanda es SINTETICA (`demanda_por_celda`, con
    semilla fija) y se dice en pantalla, en gris. Lo que se mide de verdad
    es la MEJORA de un asignador sobre otro con la misma demanda y la
    cobertura REAL del enjambre, la que sale de `conteo_cobertura`.
    """

    ALTURA_KM = 550.0
    EL_MIN = 10.0
    RES = (96, 48)
    PLANOS, POR_PLANO = 12, 10
    HACES = 8

    def construct(self):
        psi = sa.angulo_cobertura(self.ALTURA_KM, self.EL_MIN)
        demanda = sa.demanda_por_celda(self.RES, semilla=11)
        lonlat = sa.subsatelites_walker(2, self.PLANOS, self.POR_PLANO, 53.0,
                                        self.ALTURA_KM, vueltas=0.0)[0]
        conteo = sa.conteo_cobertura(self.RES, lonlat, psi)
        fijo = sa.asignar_haces(conteo, demanda, self.HACES, modo="fijo")
        apre = sa.asignar_haces(conteo, demanda, self.HACES, modo="aprendido")

        marca = hud_pieza("13 . la red aprende")
        mapa = sa.heatmap_q(demanda, alto_escena=2.88,
                            paleta=[(0.0, "#0a1428"),
                                    (0.45, "#2a2352"),
                                    (0.80, "#5b3fb5"),
                                    (1.0, C_ENLACE)])
        mapa.move_to(UP * (Y_ESCENA + 0.30))
        ancho, alto = mapa.width, mapa.height
        res_y, res_x = demanda.shape

        def celda_a_escena(rc):
            rc = np.atleast_2d(np.asarray(rc, dtype=np.float64))
            x = mapa.get_center()[0] + (rc[:, 1] / (res_x - 1) - 0.5) * ancho
            y = mapa.get_center()[1] + (0.5 - rc[:, 0] / (res_y - 1)) * alto
            return np.column_stack([x, y, np.zeros(len(rc))])

        def haces(celdas, color):
            return VGroup(*[Circle(radius=0.115, stroke_color=color,
                                   stroke_width=3.0, fill_color=color,
                                   fill_opacity=0.22).move_to(p)
                            for p in celda_a_escena(celdas)]).set_z_index(20)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(FadeIn(mapa), run_time=0.9)
        aviso = nota_externa("demanda simulada", font_size=16)
        aviso.move_to(UP * (mapa.get_bottom()[1] - 0.38))
        self.play(FadeIn(aviso), run_time=0.5)
        self.wait(1.2)

        # --- a ciegas -----------------------------------------------
        ciegos = haces(apre["celdas_inicio"], C_PERDIDO)
        pie = medida(f"{100 * fijo['servida']:.2f}", "por ciento",
                     "repartiendo a ojo", color=C_MEDIDO,
                     color_sub=C_PERDIDO)
        vivos = [pie.etiqueta, pie.numero, pie.sub]
        self.play(LaggedStart(*[GrowFromCenter(h) for h in ciegos],
                              lag_ratio=0.06), run_time=1.6)
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.wait(2.6)

        # --- y aprendiendo ------------------------------------------
        # Cada paso del ascenso mueve UN haz: se anima el recorrido de la
        # curva de mejora, que es la que mide la libreria.
        finales = celda_a_escena(apre["celdas"])
        curva = apre["curva"]
        pasos = len(curva) - 1
        iniciales = np.array([h.get_center() for h in ciegos])
        objetivo = finales[:len(ciegos)]
        cifra_viva = pie.numero

        def aprender(grupo, alpha):
            for i, h in enumerate(grupo):
                cuando = i / max(1, len(grupo))
                a = np.clip((alpha - cuando * 0.55) / 0.45, 0.0, 1.0)
                h.move_to(iniciales[i] * (1 - a) + objetivo[i] * a)
                h.set_stroke(color=interpolate_color(
                    ManimColor(C_PERDIDO), ManimColor(C_TIERRA), a))

        self.play(UpdateFromAlphaFunc(ciegos, aprender), run_time=7.0,
                  rate_func=smooth)
        listo = medida(f"{100 * apre['servida']:.2f}", "por ciento",
                       f"tras {pasos} movimientos", color=C_MEDIDO,
                       color_sub=C_MEDIDO)
        nuevos = [listo.etiqueta, listo.numero, listo.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.6)

        # --- lo que de verdad se mide: la mejora --------------------
        mejora = medida(f"{apre['servida'] / fijo['servida']:.2f}",
                        "veces mas", "los mismos haces", color=C_MEDIDO,
                        color_sub=C_SAT)
        nuevos = [mejora.etiqueta, mejora.numero, mejora.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.2)

        # --- y hasta donde se puede llegar --------------------------
        # `modo="demanda"` es el reparto perfecto: el que elige de una vez
        # las mejores celdas visibles. Que el aprendido lo alcance es el
        # resultado, y hay que enseñarlo, no esconderlo.
        techo = sa.asignar_haces(conteo, demanda, self.HACES, modo="demanda")
        margen = techo["servida"] - apre["servida"]
        cierre = medida(f"{100 * techo['servida']:.2f}", "es el techo",
                        f"y le falta {100 * margen:.2f}", color=C_MEDIDO,
                        color_sub=C_SAT)
        nuevos = [cierre.etiqueta, cierre.numero, cierre.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(5.50)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.9)
        self.remove(*self.mobjects)
        self.wait(0.5)
