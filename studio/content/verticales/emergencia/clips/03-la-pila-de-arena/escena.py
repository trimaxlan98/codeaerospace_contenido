class Clip(Scene):
    """03 · La pila de arena — tres reglas y una mandala fractal.

    El fotograma entero es `arena.simular()`: la pila abeliana de
    Bak-Tang-Wiesenfeld. Cae un grano SIEMPRE en la misma celda del centro;
    toda celda con 4 reparte uno a cada vecino. Nadie coordina nada y la
    pila se organiza sola en una mandala, con avalanchas que no tienen
    tamaño tipico.

    Arco: la mandala ya crece en el primer segundo (gancho) mientras el
    contador de granos sube a miles; zoom 2.0 al centro en la mitad para
    ver la textura de celda; camara lenta EN el frame de la avalancha mayor
    (argmax de `avalancha_max_por_frame`) con su cifra ya en pantalla; y al
    final, la distribucion log-log dibujada con vectores encima de la
    mandala apagada: la recta que dice que no hay tamaño tipico.
    """

    ZOOM = 2.0

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        # UNA sola llamada: ~65 s en el contenedor (medido en el modulo).
        r = em.arena.simular()
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        gpf = np.asarray(extra["granos_por_frame"], dtype=np.int64)
        avmax = np.asarray(extra["avalancha_max_por_frame"], dtype=np.int64)
        kmax = int(np.argmax(avmax))
        W_PX, H_PX = extra["res"]
        cx_f = float(extra["centro_px"][0]) / W_PX
        cy_f = float(extra["centro_px"][1]) / H_PX

        peli = pelicula(F, nearest=True)      # automata: pixel duro
        self.add(peli.mob)

        # El pie de cifra se lee gracias al velo de contraste del
        # style_block (uno para todo el curso): aqui hace falta de
        # verdad, porque la mandala termina midiendo el ancho ENTERO
        # del lienzo (radio 83 de 89 celdas) en violeta claro y le pasa
        # por encima a los tres renglones.

        marca = hud_pieza("03 . la arena")
        regs = reglas(["un grano al centro", "4 granos: se caen",
                       "uno a cada vecino"])

        def sep(v):
            """50000 -> '50 000': seis caracteres, no seis digitos pegados."""
            return f"{int(v):,}".replace(",", " ")

        # El contador de granos: a fs 84 porque "50 000" son 6 caracteres y
        # a fs 104 se come la zona segura (el guardian `cabe` lo aborta).
        pie = medida(sep(gpf[0]), "granos", "en el centro", font_size=84)
        cache = {}

        def texto_granos(k):
            v = int(gpf[min(max(k, 0), T - 1)])
            v = int(round(v / 200.0)) * 200      # paso de 200: menos Text
            if v not in cache:
                t = cifra(sep(v), font_size=84)
                t.move_to(UP * Y_NUMERO)
                cache[v] = t
            return cache[v]

        contador = VGroup(pie.numero)
        contador.set_z_index(800)
        pie.remove(pie.numero)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None,
                  contar=True):
            """Un tramo de pelicula con el contador vivo (become DENTRO de
            UpdateFromAlphaFunc) y, a la vez, otras animaciones."""
            anims = [peli.animacion(run_time, desde=desde, hasta=hasta,
                                    ritmo=ritmo, encuadre=encuadre)]
            if contar:
                def cuenta(_m, alpha):
                    f = ritmo(alpha) if ritmo else alpha
                    k = int(round(desde + f * (hasta - desde)))
                    contador[0].become(texto_granos(k))
                anims.append(UpdateFromAlphaFunc(contador, cuenta,
                                                 run_time=run_time,
                                                 rate_func=linear))
            self.play(*anims, *otras, run_time=run_time)

        # --- 1. gancho: la mandala ya crece ---------------------------
        self.play(FadeIn(marca, shift=DOWN * 0.16),
                  FadeIn(pie.etiqueta), FadeIn(pie.sub), FadeIn(contador),
                  peli.animacion(0.7, desde=0, hasta=26), run_time=0.7)

        # --- 2. las tres reglas, una a una, sin parar la pila ---------
        foco = Circle(radius=0.34, stroke_color=C_REGLA, stroke_width=2.4)
        foco.move_to(px_a_escena([extra["centro_px"]], peli.mob,
                                 W_PX, H_PX)[0])
        foco.set_z_index(700)
        for i, et in enumerate(regs):
            a, b = 26 + i * 52, 78 + i * 52
            otras = [FadeIn(et, shift=RIGHT * 0.15)]
            if i == 0:
                otras.append(FadeIn(foco, scale=2.2))
            tramo(1.4, a, b, *otras)

        # --- 3. ritmo normal: la mandala se abre ---------------------
        tramo(3.4, 182, 300, FadeOut(foco, scale=1.8))

        # --- 4. zoom 2.0 al centro: la textura de celda ---------------
        # Las reglas se retiran AQUI: dos lineas mas y la mandala (que ya
        # roza el ancho del lienzo) se las habria comido.
        tramo(2.6, 300, 366, FadeOut(regs, shift=UP * 0.12),
              encuadre=em.zoom_hacia(cx_f, cy_f, self.ZOOM))
        tramo(3.0, 366, 436,
              encuadre=lambda f, W_, H_: (cx_f, cy_f, self.ZOOM))
        tramo(2.4, 436, 496,
              encuadre=em.zoom_hacia(cx_f, cy_f, 1.0, desde=self.ZOOM))

        # --- 5. el relevo del pie, con la pelicula en marcha ----------
        # La cifra de la avalancha entra ANTES del derrumbe para que este
        # en pantalla cuando ocurre; nada se encima ni un frame (sale una
        # y entra la otra en dos tramos consecutivos).
        fb = min(max(kmax + 14, 540), T - 1)
        fa = max(500, fb - 26)
        pie2 = medida(sep(cifras["avalancha_mayor"]), "avalancha mayor",
                      "celdas", font_size=84)

        tramo(max(0.8, (fa - 14 - 496) / 55.0), 496, fa - 14)
        tramo(0.45, fa - 14, fa - 7,
              FadeOut(contador, scale=0.92),
              FadeOut(pie.etiqueta, scale=0.92),
              FadeOut(pie.sub, scale=0.92), contar=False)
        tramo(0.50, fa - 7, fa, FadeIn(pie2, scale=1.06), contar=False)

        # --- 6. camara lenta EN la avalancha mayor -------------------
        tramo(3.6, fa, fb, contar=False)
        if fb < T - 1:
            tramo(max(0.5, (T - 1 - fb) / 60.0), fb, T - 1, contar=False)
        self.wait(0.8)

        # --- 7. la ley de potencias, en vectores ---------------------
        self.play(peli.mob.animate.set_opacity(0.20), run_time=0.7)

        hist = extra["histograma"]
        cen = np.asarray(hist["centros"], dtype=np.float64)
        den = np.asarray(hist["densidad"], dtype=np.float64)
        ok = np.asarray(hist["mascara_ajuste"], dtype=bool)
        m_r, b_r = hist["recta"]
        vis = den > 0
        lx = np.log10(cen[vis])
        ly = np.log10(den[vis])
        ANCHO_G, ALTO_G, CY_G = 4.0, 2.6, 2.05
        gx0, gx1 = float(lx.min()), float(lx.max())
        gy0, gy1 = float(ly.min()), float(ly.max())

        def P(x, y):
            u = (x - gx0) / max(gx1 - gx0, 1e-9)
            v = (y - gy0) / max(gy1 - gy0, 1e-9)
            return np.array([(u - 0.5) * ANCHO_G,
                             CY_G + (v - 0.5) * ALTO_G, 0.0])

        ex, ey = ANCHO_G / 2 + 0.30, ALTO_G / 2 + 0.30
        eje = VGroup(Line([-ex, CY_G - ey, 0], [-ex, CY_G + ey, 0]),
                     Line([-ex, CY_G - ey, 0], [ex, CY_G - ey, 0]))
        eje.set_stroke(color=C_EJE, width=2.4)
        eje.set_z_index(600)

        puntos = VGroup(*[Dot(P(x, y), radius=0.050, color=C_MEDIDO)
                          for x, y in zip(lx, ly)])
        puntos.set_z_index(650)

        lxo = np.log10(cen[ok & vis])
        xa, xb = float(lxo.min()), float(lxo.max())
        pa, pb = P(xa, m_r * xa + b_r), P(xb, m_r * xb + b_r)
        recta = poli(np.array([[pa[0], pa[1]], [pb[0], pb[1]]]),
                     color=C_REGLA, grosor=4.6)
        recta.set_z_index(640)

        self.play(Create(eje), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(d, scale=0.4) for d in puntos],
                              lag_ratio=0.06), run_time=1.7)
        self.play(Create(recta), run_time=0.9)

        pie3 = medida(f"{cifras['exponente_tau_medido']:.2f}", "exponente",
                      "ley de potencias")
        cambiar(self, [pie2], [pie3])
        self.wait(1.7)

        cerrar_pieza(self)
