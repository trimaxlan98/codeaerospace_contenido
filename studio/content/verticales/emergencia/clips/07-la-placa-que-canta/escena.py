class Clip(Scene):
    """07 . La placa que canta - Chladni: la arena dibuja las lineas nodales.

    El fotograma es `chladni.simular` (40 000 granos de arena sobre una
    placa cuadrada) con CUATRO modos crecientes: (1,2) -> (2,3) -> (2,5) ->
    (5,7) (el tercer salto se cambio de (3,5) a (2,5) a proposito: mas
    salto visual entre modo y modo). La arena ya migra en el primer
    segundo (entra el HUD sobre ese movimiento, nunca antes). Las tres
    reglas se encienden sobre el modo 1 con un marco ambar que traza el
    borde de la placa (`px_a_escena` + `poli`) y se apaga antes del modo 2.

    Arco de la cifra: el pie muestra la frecuencia relativa del modo
    ("1.0X", "2.6X", ...) en cian, etiqueta "frecuencia", sub "veces la
    primera"; en cada cambio de modo se releva SOLO el numero (`relevo`).
    En el primer cambio (cuando la arena brinca y vuelve a organizarse) la
    pelicula va a camara lenta antes y despues del salto. En el tercer
    modo la camara hace zoom 1.5x al centro de la placa
    (`em.zoom_hacia`), se sostiene en el modo 4 y se abre otra vez. Al
    final, un `cambiar()` reemplaza el panel entero por la fraccion de
    arena sobre el nodo del ULTIMO modo (la cifra que de verdad importa:
    baja al subir la frecuencia).
    """

    ZOOM = 1.5

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) --------------------
        r = em.chladni.simular(semilla=1, pasos=800, res=(360, 640),
                                modos=((1, 2), (2, 3), (2, 5), (5, 7)))
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        H, W = F.shape[1], F.shape[2]
        cambios = extra["frames_cambio_modo"]          # [0, 200, 400, 600]
        frel = extra["frecuencia_relativa"]             # p.ej. 1.0 2.6 5.8 14.8
        x0, y0, lado = extra["placa_px"]
        cx_placa = (x0 + lado / 2.0) / W
        cy_placa = (y0 + lado / 2.0) / H
        pct_final = cifras["frac_nodos_final_pct"]

        peli = pelicula(F)
        self.add(peli.mob)

        # El contraste del HUD sobre el patron lo pone el velo del
        # style_block (velos_de_contraste), comun a todo el curso.

        marca = hud_pieza("07 . placa canta")
        regs = reglas(["LA PLACA VIBRA", "LA ARENA HUYE", "DEL MOVIMIENTO"])

        def avanzar(run_time, desde, hasta, *otras, encuadre=None):
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                     encuadre=encuadre), *otras,
                      run_time=run_time)

        # --- 1. gancho: la arena ya migra; entra el HUD -----------------
        avanzar(0.6, 0, 20, FadeIn(marca, shift=DOWN * 0.16))

        # --- 2. las reglas se encienden mientras el modo 1 respira ------
        pts_px = np.array([[x0, y0], [x0 + lado, y0],
                           [x0 + lado, y0 + lado], [x0, y0 + lado],
                           [x0, y0]])
        marco = poli(px_a_escena(pts_px, peli.mob, W, H), color=C_REGLA,
                    grosor=2.0)
        marco.set_z_index(50)

        margen = 15                                     # runway a la camara lenta
        seg = (cambios[1] - margen - 20) // 3            # 55 frames por regla
        r1, r2, r3 = 20 + seg, 20 + 2 * seg, 20 + 3 * seg

        avanzar((r1 - 20) / 30.0, 20, r1, FadeIn(regs[0], shift=RIGHT * 0.15),
                Create(marco))
        self.wait(0.12)
        avanzar((r2 - r1) / 30.0, r1, r2,
                FadeIn(regs[1], shift=RIGHT * 0.15))
        self.wait(0.12)
        avanzar((r3 - r2) / 30.0, r2, r3,
                FadeIn(regs[2], shift=RIGHT * 0.15), FadeOut(marco))
        self.wait(0.12)

        # --- 3. entra el pie de cifra: frecuencia relativa del modo 1 ---
        pie = medida(f"{frel[0]:.1f}X", "frecuencia", "veces la primera")
        cambiar(self, regs, pie)

        # --- 4. camara lenta en el PRIMER cambio (la arena brinca) ------
        avanzar(1.4, r3, cambios[1])
        numero = relevo(self, pie.numero, cifra(f"{frel[1]:.1f}X"))
        avanzar(2.0, cambios[1], cambios[1] + 30)

        # --- 5. el modo 2 respira; segundo cambio, a ritmo normal -------
        avanzar((cambios[2] - 10 - (cambios[1] + 30)) / 30.0,
                cambios[1] + 30, cambios[2] - 10)
        avanzar(10 / 30.0, cambios[2] - 10, cambios[2])
        numero = relevo(self, numero, cifra(f"{frel[2]:.1f}X"))

        # --- 6. zoom 1.5x al centro de la placa durante el TERCER modo --
        acercar = em.zoom_hacia(cx_placa, cy_placa, self.ZOOM)
        avanzar(5.5, cambios[2], cambios[3], encuadre=acercar)
        numero = relevo(self, numero, cifra(f"{frel[3]:.1f}X"))

        # --- 7. se sostiene el acercamiento en el modo 4 y se abre ------
        def quieto(frac, W_, H_):
            return cx_placa, cy_placa, self.ZOOM
        avanzar(10 / 3.0, cambios[3], cambios[3] + 100, encuadre=quieto)
        alejar = em.zoom_hacia(cx_placa, cy_placa, 1.0, desde=self.ZOOM)
        avanzar(2.2, cambios[3] + 100, cambios[3] + 160, encuadre=alejar)
        avanzar(0.9, cambios[3] + 160, cambios[3] + 185)

        # --- 8. remate: la fraccion de arena en el nodo del ultimo modo -
        final = medida(f"{pct_final:.0f}%", "arena en el nodo",
                       "ultimo modo")
        cambiar(self, [pie.etiqueta, numero, pie.sub], final)
        self.wait(0.9)

        cerrar_pieza(self)
