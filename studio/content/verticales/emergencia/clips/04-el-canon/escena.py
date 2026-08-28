class Clip(Scene):
    """04 . El canon - el canon de Gosper dispara planeadores (B3/S23).

    El fotograma entero es Life (`vida.simular`, pixel duro con
    `nearest=True`): el canon de Gosper, arriba a la izquierda, ya dispara
    desde el primer frame. Se encienden las tres reglas (nace/vive/muere)
    mientras la poblacion sigue su curso; en el nacimiento del planeador
    seguido (frame 138) la pelicula va a camara lenta con
    `ritmo_por_tramos` (la ventana lenta cae en los frames 130-150); luego
    la camara se pega a ese planeador (`seguir`, zoom 2.0) y lo acompana
    mientras cruza en diagonal y baja, y se abre de nuevo cuando sale. La
    cifra pasa de periodo (30 pasos, cian) a planeadores por minuto (30.0)
    y a planeadores emitidos (22): las tres medidas sobre esta misma
    corrida. El periodo teorico del canon (30, literatura) se cita en gris.

    Estructura como el molde 01: medir antes de dibujar; pelicula de fondo
    desde el primer frame; HUD de pieza; reglas; pie de cifra con relevos
    limpios (nunca dos a la vez); camara y ritmo con intencion;
    cerrar_pieza.
    """

    ZOOM = 2.0

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.vida.simular(semilla=1, pasos=700, res=(270, 480), celda=3,
                            pasos_por_s=15.0)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        pos_seguido = np.asarray(extra["pos_planeador_seguido"],
                                 dtype=np.float64)
        # frame_nacimiento_seguido = 138 con estos parametros (deterministico:
        # el canon no depende de la semilla); la ventana lenta 130-150 lo
        # envuelve por ambos lados.
        k_nace = int(extra["frame_nacimiento_seguido"])

        peli = pelicula(F, nearest=True)
        self.add(peli.mob)

        marca = hud_pieza("04 . el canon")
        regs = reglas(["NACE CON 3", "VIVE CON 2 O 3", "MUERE SI NO"])

        periodo_txt = f"{cifras['periodo_canon_pasos']:.0f}"
        pormin_txt = f"{cifras['planeadores_por_minuto']:.1f}"
        emit_txt = str(int(cifras["planeadores_emitidos"]))

        pie_periodo = medida(periodo_txt, "periodo", "pasos")
        pie_pormin = medida(pormin_txt, "por minuto", "planeadores")
        pie_emit = medida(emit_txt, "emitidos", "planeadores")
        nota = nota_externa("teoria 30")
        nota.move_to(UP * -1.85)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None):
            """Un tramo de pelicula con, opcionalmente, otras animaciones a
            la vez (nunca un fundido cruzado: fuera y dentro van en tramos
            distintos)."""
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                     ritmo=ritmo, encuadre=encuadre),
                      *otras, run_time=run_time)

        # --- 1. el canon ya dispara; entra el HUD de pieza -----------
        self.play(FadeIn(marca, shift=DOWN * 0.16),
                  peli.animacion(0.6, desde=0, hasta=30), run_time=0.6)

        # --- 2. las tres reglas, una a una ----------------------------
        tramo(0.6, 30, 55, FadeIn(regs[0], shift=RIGHT * 0.15))
        tramo(0.6, 55, 80, FadeIn(regs[1], shift=RIGHT * 0.15))
        tramo(0.55, 80, 100, FadeIn(regs[2], shift=RIGHT * 0.15))

        # --- 3. nace un planeador: camara lenta (ritmo_por_tramos) ----
        # tramo A (100->138): normal hasta el 130, luego entra en lento.
        ritmo_a = em.ritmo_por_tramos([(0, 0), (0.30, (130 - 100) / 38.0),
                                    (1, 1)])
        tramo(1.8, 100, k_nace, FadeIn(pie_periodo), ritmo=ritmo_a)
        # tramo B (138->170): sigue lento hasta el 150, luego recupera ritmo.
        ritmo_b = em.ritmo_por_tramos([(0, 0), (0.60, (150 - k_nace) / 32.0),
                                    (1, 1)])
        tramo(1.4, k_nace, 170, FadeIn(nota), ritmo=ritmo_b)

        # --- 4. la camara se pega al planeador seguido (zoom 2.0) -----
        sig = em.seguir(pos_seguido, self.ZOOM)

        def acercar(frac, W_, H_):
            k = 170 + frac * (230 - 170)
            cx, cy, _ = sig(k / (T - 1), W_, H_)
            return cx, cy, 1.0 + (self.ZOOM - 1.0) * frac
        tramo(2.0, 170, 230, FadeOut(nota), encuadre=acercar)

        def pegado(f0, f1):
            def enc(frac, W_, H_):
                k = f0 + frac * (f1 - f0)
                return sig(k / (T - 1), W_, H_)
            return enc

        tramo(9.0, 230, 424, encuadre=pegado(230, 424))
        # relevo periodo -> por minuto: fuera y dentro en tramos distintos.
        tramo(0.3, 424, 433, FadeOut(pie_periodo), encuadre=pegado(424, 433))
        tramo(0.36, 433, 445, FadeIn(pie_pormin), encuadre=pegado(433, 445))
        tramo(9.0, 445, 639, encuadre=pegado(445, 639))

        # --- 5. baja y sale por debajo: la camara se abre --------------
        f2, f3 = 639, T - 1

        def abrir(frac, W_, H_):
            k = f2 + frac * (f3 - f2)
            cx, cy, _ = sig(k / (T - 1), W_, H_)
            z = self.ZOOM + (1.0 - self.ZOOM) * frac
            return cx + (0.5 - cx) * frac, cy + (0.5 - cy) * frac, z
        tramo(2.5, f2, f3, encuadre=abrir)

        # --- 6. cifra final: planeadores emitidos ----------------------
        self.play(FadeOut(pie_pormin), run_time=0.3)
        self.play(FadeIn(pie_emit), run_time=0.36)
        self.wait(2.0)

        cerrar_pieza(self)
