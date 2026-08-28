class Clip(Scene):
    """05 · Manchas y rayas — la misma quimica, otra regla.

    Gray-Scott (`em.turing.simular`, malla 270x480 ENTERA, una celda = un
    pixel): de una unica semilla central nace un frente de manchas que
    crece desde el primer segundo (ritmo rapido en los primeros 200
    frames, normal despues). Al llegar la fase de manchas a su limite
    (frame 400) se cuentan 186 manchas; ahi mismo la regla (f, k) se
    releva por la de rayas/laberinto (HUD ambar "f 0.030 k 0.057") y la
    camara entra en camara lenta (400-470) mientras el patron YA formado
    se reorganiza en dedos y laberinto, sin volver a empezar. Zoom
    moderado (1.6x) al centro para ver el detalle; la longitud de onda
    medida por el pico del espectro radial baja de 15.3 a 13.3 px: misma
    quimica, otra regla.

    Estructura heredada del molde: medir antes de dibujar (una sola
    llamada a `simular`, cara ~45 s); la pelicula como fondo desde el
    primer frame; HUD de pieza; reglas que se relevan con `cambiar()`;
    pie de cifra en sus tres renglones; camara y ritmo con intencion;
    `cerrar_pieza`.
    """

    ZOOM = 1.6

    def construct(self):
        # --- lo que se mide (antes de dibujar nada; simular() UNA vez) --
        r = em.turing.simular()
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        frame_cambio = int(extra["frame_cambio"])             # 400
        frame_fin = int(extra["frame_fin_transicion"])         # 460
        fk = np.asarray(extra["fk_por_frame"], dtype=np.float64)
        f_final, k_final = fk[min(frame_fin + 10, T - 1)]
        n_manchas = str(int(cifras["n_manchas"]))
        lam_manchas = f"{cifras['lambda_manchas_px']:.1f}"
        lam_rayas = f"{cifras['lambda_rayas_px']:.1f}"

        peli = pelicula(F)
        self.add(peli.mob)

        marca = hud_pieza("05 . manchas-rayas")
        regs = reglas(["1 . A SE GASTA", "2 . B SE COPIA",
                       "3 . AMBOS SE MUEVEN"])
        regla_cambio = hud(f"f {f_final:.3f} k {k_final:.3f}",
                           font_size=17, color=C_REGLA)
        regla_cambio.move_to(regs[0].get_center())

        def tramo(run_time, desde, hasta, *otras, encuadre=None):
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                      encuadre=encuadre),
                      *otras, run_time=run_time)

        # --- 1. la semilla ya crece desde el primer segundo -----------
        self.play(FadeIn(marca, shift=DOWN * 0.16),
                  peli.animacion(0.7, desde=0, hasta=40), run_time=0.7)
        tramo(1.6, 40, 200)                       # ritmo rapido

        # --- 2. ritmo normal; las reglas se encienden una a una -------
        for i, et in enumerate(regs):
            a, b = 200 + i * 60, 260 + i * 60
            tramo(2.6, a, b, FadeIn(et, shift=RIGHT * 0.15))
        tramo(1.1, 380, frame_cambio - 1)

        # --- 3. cifra 1: manchas al final de la fase 1 -----------------
        pie1 = medida(n_manchas, "manchas")
        self.play(FadeIn(pie1), run_time=0.4)
        self.wait(0.6)

        # --- 4. la regla se releva; camara lenta 400 -> 470 ------------
        cambiar(self, [*regs, pie1], regla_cambio)
        tramo(6.5, frame_cambio, frame_fin + 10)

        # --- 5. avance rapido con zoom moderado al centro --------------
        pie2 = medida(lam_manchas, "longitud de onda", "pixeles")
        self.play(FadeIn(pie2), run_time=0.4)
        tramo(2.8, frame_fin + 10, 620,
              encuadre=em.zoom_hacia(0.5, 0.5, self.ZOOM))
        tramo(1.4, 620, 680,
              encuadre=em.zoom_hacia(0.5, 0.5, self.ZOOM, desde=self.ZOOM))

        # --- 6. la longitud de onda del laberinto ya formado -----------
        relevo(self, pie2.numero, cifra(lam_rayas))

        tramo(3.0, 680, 750,
              encuadre=em.zoom_hacia(0.5, 0.5, 1.0, desde=self.ZOOM))
        tramo(1.6, 750, T - 1)
        self.wait(1.2)

        cerrar_pieza(self)
