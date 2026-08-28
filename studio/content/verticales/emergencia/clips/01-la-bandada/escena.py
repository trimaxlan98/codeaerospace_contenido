class Clip(Scene):
    """01 · La bandada — tres reglas, 2500 agentes, ningun jefe.

    MOLDE del curso. El fotograma entero es la simulacion (`bandada.simular`,
    boids con rejilla espacial): del ruido nace una bandada que ondula. El
    HUD enciende las tres reglas una a una mientras los agentes ya se mueven;
    la cifra es la polarizacion del enjambre (0 = cada uno a lo suyo, 1 =
    todos al mismo rumbo) frame a frame; en el instante en que cruza 0.8 la
    pelicula va a camara lenta, y despues la camara se pega al agente ambar
    (zoom 2.2) para ver la ola desde dentro, y vuelve a abrirse al final.

    Estructura que copian las demas piezas: medir antes de dibujar; la
    pelicula como fondo desde el primer frame; HUD de pieza; reglas; pie de
    cifra en sus tres renglones con contador pre-renderizado; camara y ritmo
    con intencion; cerrar_pieza.
    """

    ZOOM = 2.2

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.bandada.simular(semilla=1, pasos=900, res=(360, 640))
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        pol = np.asarray(extra["polarizacion"], dtype=np.float64)
        seguido = np.asarray(extra["seguido"], dtype=np.float64)
        umbral = int(cifras["frame_umbral_0_8"])
        if umbral < 200 or umbral > 500:
            umbral = 300

        peli = pelicula(F)
        self.add(peli.mob)

        marca = hud_pieza("01 . la bandada")
        regs = reglas(["1 . separarse", "2 . alinearse", "3 . juntarse"])

        # El contador: un Text por centesima, pre-renderizado; se cambia
        # con become DENTRO de la animacion (nunca always_redraw con Text).
        pie = medida("0.00", "polarizacion", f"{cifras['agentes']} agentes",
                     color_sub=C_VIVO)
        cache = {}

        def texto_pol(k):
            v = round(float(pol[min(k, T - 1)]), 2)
            if v not in cache:
                t = cifra(f"{v:.2f}")
                t.move_to(UP * Y_NUMERO)
                cache[v] = t
            return cache[v]

        contador = VGroup(pie.numero)
        contador.set_z_index(800)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None,
                  rate_func=None):
            """Un tramo de pelicula (frames desde->hasta) con el contador
            vivo y, opcionalmente, otras animaciones a la vez."""
            def cuenta(_m, alpha):
                f = ritmo(alpha) if ritmo else alpha
                k = int(round(desde + f * (hasta - desde)))
                contador[0].become(texto_pol(k))
            anims = [peli.animacion(run_time, desde=desde, hasta=hasta,
                                    ritmo=ritmo, encuadre=encuadre,
                                    rate_func=rate_func),
                     UpdateFromAlphaFunc(contador, cuenta, run_time=run_time,
                                         rate_func=linear)]
            self.play(*anims, *otras, run_time=run_time)

        # --- 1. el ruido ya se mueve; entran HUD y reglas -------------
        self.add(contador)
        pie.remove(pie.numero)
        self.play(FadeIn(marca, shift=DOWN * 0.16),
                  FadeIn(pie.etiqueta), FadeIn(pie.sub),
                  peli.animacion(0.6, desde=0, hasta=18), run_time=0.6)
        tramo(1.4, 18, 60)
        for i, et in enumerate(regs):
            a, b = 60 + i * 40, 100 + i * 40
            tramo(1.35, a, b, FadeIn(et, shift=RIGHT * 0.15))
        # frames 180 -> umbral-15 a ritmo real
        tramo(max(0.8, (umbral - 15 - 180) / 30.0), 180, umbral - 15)

        # --- 2. camara lenta en el instante en que cruza 0.8 ---------
        tramo(3.0, umbral - 15, umbral + 15)
        self.wait(0.2)

        # --- 3. la camara se pega al agente ambar --------------------
        # Zoom geometrico de 1 a ZOOM en 2.5 s siguiendo al agente; luego
        # seguimiento puro; luego se abre otra vez.
        sig = em.seguir(seguido, self.ZOOM)
        f0, f1 = umbral + 15, min(umbral + 15 + 75, T - 200)

        def acercar(frac, W_, H_):
            k = f0 + frac * (f1 - f0)
            cx, cy, _ = sig(k / (T - 1), W_, H_)
            return cx, cy, 1.0 + (self.ZOOM - 1.0) * frac
        tramo(2.5, f0, f1, encuadre=acercar)

        f2 = min(f1 + 240, T - 120)

        def pegado(frac, W_, H_):
            k = f1 + frac * (f2 - f1)
            return sig(k / (T - 1), W_, H_)
        tramo((f2 - f1) / 30.0, f1, f2, encuadre=pegado)

        f3 = min(f2 + 90, T - 1)

        def abrir(frac, W_, H_):
            k = f2 + frac * (f3 - f2)
            cx, cy, _ = sig(k / (T - 1), W_, H_)
            z = self.ZOOM + (1.0 - self.ZOOM) * frac
            return cx + (0.5 - cx) * frac, cy + (0.5 - cy) * frac, z
        tramo(3.0, f2, f3, encuadre=abrir)

        # --- 4. la bandada entera, y la cifra final ------------------
        resto = (T - 1 - f3) / 30.0
        if resto > 0.3:
            tramo(resto, f3, T - 1)
        self.wait(1.2)

        cerrar_pieza(self)
