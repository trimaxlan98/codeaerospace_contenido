class Clip(Scene):
    """09 · Doscientos pendulos — 200 pendulos dobles RK4, una escalera de
    1e-6 rad de diferencia en el angulo de arriba y nada mas.

    Al principio los 200 se ven como UNO: la separacion angular maxima
    entre dos cualesquiera arranca en 0. En el frame 270 (segundo 8.975 de
    la corrida) esa separacion cruza 1 rad — el abanico se abre delante de
    la camara, que hace zoom lento al pivote (1.0 -> 1.6) exactamente ahi
    (frames 240-300 a camara lenta). Se pasa rapido por el ultimo tercio
    (300-449), ya con el abanico disperso, y cierra el exponente de
    Lyapunov medido sobre la propia corrida.
    """

    ZOOM = 1.6

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) --------------------
        r = em.pendulos.simular(semilla=1, pasos=450, res=(360, 640))
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        sep = np.asarray(extra["separacion_max"], dtype=np.float64)
        f_sep = int(extra["frame_separacion_1rad"])
        cx_frac = float(extra["pivote_px"][0]) / F.shape[2]
        cy_frac = float(extra["pivote_px"][1]) / F.shape[1]

        peli = pelicula(F)
        self.add(peli.mob)

        marca = hud_pieza("09 . pendulos")
        regs = reglas(["200 PENDULOS", "IGUALES", "SALVO 0.000001"])

        pie = medida(f"{sep[0]:.3f}", "separacion", "radianes")
        cache = {}

        def texto_sep(k):
            v = round(float(sep[min(k, T - 1)]), 3)
            if v not in cache:
                t = cifra(f"{v:.3f}")
                t.move_to(UP * Y_NUMERO)
                cache[v] = t
            return cache[v]

        contador = VGroup(pie.numero)
        contador.set_z_index(800)

        def avanzar(run_time, desde, hasta, *otras, encuadre=None):
            """Un tramo de pelicula con el contador de separacion vivo."""
            def cuenta(_m, alpha):
                k = int(round(desde + alpha * (hasta - desde)))
                contador[0].become(texto_sep(k))
            anims = [peli.animacion(run_time, desde=desde, hasta=hasta,
                                    encuadre=encuadre),
                     UpdateFromAlphaFunc(contador, cuenta, run_time=run_time,
                                         rate_func=linear)]
            self.play(*anims, *otras, run_time=run_time)

        # --- 1. el pendulo ya oscila; entran el HUD, las reglas, el pie -
        self.add(contador)
        pie.remove(pie.numero)
        self.play(FadeIn(marca, shift=DOWN * 0.16),
                  FadeIn(pie.etiqueta), FadeIn(pie.sub),
                  peli.animacion(0.6, desde=0, hasta=14), run_time=0.6)
        borde = 14
        for et in regs:
            a, b = borde, borde + 24
            avanzar(1.5, a, b, FadeIn(et, shift=RIGHT * 0.15))
            borde = b
        # el resto del primer tramo, a un ritmo algo mas lento que el real
        avanzar(8.0, borde, 240)
        self.wait(0.2)

        # --- 2. camara lenta 240 -> 300: el abanico se abre -------------
        def zoom_pivote(desde, hasta):
            def enc(_frac, W, H):
                k = desde + _frac * (hasta - desde)
                t = min(max((k - 240) / 60.0, 0.0), 1.0)
                z = self.ZOOM ** t
                return cx_frac, cy_frac, z
            return enc

        avanzar(4.8, 240, f_sep, encuadre=zoom_pivote(240, f_sep))
        nuevo_sub = relevo(self, pie.sub,
                           hud(f"en {cifras['t_separacion_1rad']:.2f} s",
                               font_size=18, color=C_REGLA))
        pie.sub = nuevo_sub
        avanzar(4.8, f_sep, 300, encuadre=zoom_pivote(f_sep, 300))
        self.wait(0.3)

        # --- 3. rapido por el ultimo tercio: el abanico ya disperso -----
        def zoom_vuelta(frac, _W, _H):
            t = 1.0 - frac
            return cx_frac, cy_frac, self.ZOOM ** t
        avanzar(1.7, 300, T - 1, encuadre=zoom_vuelta)
        self.wait(0.4)

        # --- 4. el lyapunov medido sobre la propia corrida --------------
        lyap = medida(f"{cifras['lyapunov_medido']:.2f}", "lyapunov",
                      "por segundo")
        cambiar(self, [pie.etiqueta, contador[0], pie.sub], lyap)
        self.wait(2.0)

        duplica = medida(f"{cifras['t_duplicar_error']:.2f}", "duplica en",
                         "segundos")
        cambiar(self, lyap, duplica)
        self.wait(1.8)

        cerrar_pieza(self)
