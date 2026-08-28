class Clip(Scene):
    """13 · Dos galaxias — 4000 estrellas, dos nucleos, solo gravedad.

    El fotograma entero es `emergencia.galaxias.simular` (Toomre restringido,
    900 frames): dos discos que ya se acercan desde el primer segundo. La
    cifra viva es la distancia entre los nucleos, medida frame a frame sobre
    lo que se ve, y mientras dura la aproximacion un puente cian une los dos
    nucleos para enseñar QUE se esta midiendo. En el pericentro (frame 386,
    el minimo de `distancia_nucleos`) la camara baja a ~8 frames por segundo
    y hace zoom 1.6 al punto medio entre los nucleos; despues se abre otra
    vez y aparecen los brazos y las colas de marea, con la trayectoria de
    cada nucleo dibujada con `poli` tenue (verde A, ambar B). Remate: la
    deriva de energia del integrador y el trasvase de estrellas de una
    galaxia a la otra, las dos calculadas en este render.

    Ningun trazo vectorial se dibuja mientras la camara esta recortando: el
    `recortar` de la pelicula cambia la escala de la imagen pero no la del
    mobject, asi que un `poli` sobre `px_a_escena` solo cuadra a zoom 1.

    Dos decisiones de legibilidad, tomadas mirando el render y no a ojo: (1)
    los discos pasan POR ENCIMA del pie de cifra —el A nace abajo y al final
    el B cruza esa banda—, asi que la pieza lleva un velo en degradado sobre
    el tercio inferior, entre la pelicula y el texto; (2) las reglas se
    apagan cuando se abre la camara, o las colas de marea las cruzan de
    estrellas y no se leen.
    """

    ZOOM = 1.6
    PASO_TRAZA = 3          # 1 punto de la trayectoria cada 3 frames
    N_A = 2200              # particulas del disco A (las primeras de la pila)
    VELO = (-1.00, -2.45, 0.85)   # (y donde nace, y donde ya es plena, opacidad)

    def velo(self, n=64):
        """Degradado NEGRO sobre el tercio inferior, entre la pelicula y el
        texto: el pie de cifra vive ahi y los dos discos le pasan por encima
        (el A nace abajo, el B acaba abajo). Sube de 0 a plena opacidad
        entre `VELO[0]` y `VELO[1]` —justo encima del renglon de la
        etiqueta— y de ahi al suelo va lleno.

        Dos cosas medidas en el render, no supuestas:
          - el velo va en NEGRO, no en `CODE_BG`: el fondo del video sale
            a un valor medio de 6 y el `#0b0f14` de marca a 15, asi que un
            velo del color del fondo ACLARA la banda en vez de oscurecerla
            (se vio como un rectangulo gris sobre el disco);
          - va en 64 franjas y no como un `ImageMobject` RGBA: el
            ImageMobject no se coloco donde se le pidio (quedo centrado
            arriba y con la rampa aplastada), y con 64 franjas el escalon
            de alfa es de 0.013 y no se ve.
        """
        y0, y1, opac = self.VELO
        suelo = -FMT.alto / 2
        h = (y0 - y1) / n
        g = VGroup()
        for i in range(n):
            r = Rectangle(width=FMT.ancho, height=h * 1.03, stroke_width=0.0,
                          fill_color="#000000",
                          fill_opacity=opac * (i + 0.5) / n)
            r.move_to(np.array([0.0, y0 - (i + 0.5) * h, 0.0]))
            g.add(r)
        base = Rectangle(width=FMT.ancho, height=y1 - suelo, stroke_width=0.0,
                         fill_color="#000000", fill_opacity=opac)
        base.move_to(np.array([0.0, (y1 + suelo) / 2, 0.0]))
        g.add(base)
        g.set_z_index(700)
        return g

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.galaxias.simular(semilla=1, pasos=2, res=(270, 480),
                                frames=900, n_a=self.N_A, n_b=1800)
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        T = len(F)
        H_px, W_px = F.shape[1], F.shape[2]
        dist = np.asarray(extra["distancia_nucleos"], dtype=np.float64)
        na = np.asarray(extra["nucleo_a_px"], dtype=np.float64)
        nb = np.asarray(extra["nucleo_b_px"], dtype=np.float64)
        peri = int(cifras["frame_pericentro"])
        if not 250 < peri < T - 250:
            peri = int(np.argmin(dist))

        # deriva del integrador y trasvase de estrellas, de ESTE render
        deriva = float(cifras["deriva_energia_nucleos_pct"])
        txt_deriva = f"{deriva:.4f}"
        if txt_deriva == "0.0000":
            txt_deriva = f"{deriva:.0e}".replace("e-0", "e-")
        clase = np.asarray(extra["clase_final"])
        cambian = int((clase[:self.N_A] == 1).sum()
                      + (clase[self.N_A:] == 0).sum())
        pct_cambian = 100.0 * cambian / clase.size

        peli = pelicula(F)
        self.add(peli.mob)
        self.add(self.velo())

        marca = hud_pieza("13 . galaxias")
        regs = reglas(["4000 estrellas", "dos nucleos", "solo gravedad"])

        # --- el pie de cifra: la distancia entre nucleos, viva --------
        pie = medida(f"{dist[0]:.0f}", "entre nucleos", "unidades")
        contador = VGroup(pie.numero)
        contador.set_z_index(800)
        pie.remove(pie.numero)
        cache = {}

        def texto_d(k):
            v = int(round(dist[min(k, T - 1)]))
            if v not in cache:
                t = cifra(str(v))
                t.move_to(UP * Y_NUMERO)
                cache[v] = t
            return cache[v]

        # --- enfasis vectorial (solo valido a zoom 1) ----------------
        puente = VMobject()             # lo que mide el contador
        puente.set_z_index(20)
        rastro = VGroup(VMobject(), VMobject())   # por donde paso cada nucleo
        rastro.set_z_index(10)

        def pinta_puente(k, _rev):
            pts = px_a_escena(np.stack([na[k], nb[k]]), peli.mob, W_px, H_px)
            puente.become(poli(pts, color=C_MEDIDO, grosor=2.0,
                               opacidad=0.55))
            puente.set_z_index(20)

        def pinta_rastro(k, rev):
            m = max(4, int(round(rev * k)) + 1)
            idx = np.arange(0, min(m, T), self.PASO_TRAZA)
            for j, (tr, col) in enumerate(((na, C_VIVO), (nb, C_REGLA))):
                pts = px_a_escena(tr[idx], peli.mob, W_px, H_px)
                rastro[j].become(poli(pts, color=col, grosor=2.2,
                                      opacidad=0.34))
            rastro.set_z_index(10)

        vivos = []
        motor = Dot(radius=0.001, fill_opacity=0.0, stroke_opacity=0.0)
        self.add(motor)

        def tramo(rt, desde, hasta, *otras, ritmo=None, encuadre=None,
                  rev=None, contar=True):
            """Un tramo de pelicula con el contador y los trazos vivos."""
            def paso(_m, alpha):
                f = ritmo(alpha) if ritmo else alpha
                k = int(round(desde + f * (hasta - desde)))
                if contar:
                    contador[0].become(texto_d(k))
                    contador[0].set_z_index(800)
                x = 1.0 if rev is None else rev[0] + (rev[1] - rev[0]) * f
                for fn in vivos:
                    fn(k, x)
            anims = [peli.animacion(rt, desde=desde, hasta=hasta, ritmo=ritmo,
                                    encuadre=encuadre),
                     UpdateFromAlphaFunc(motor, paso, run_time=rt,
                                         rate_func=linear)]
            self.play(*anims, *otras, run_time=rt)

        def medio(k):
            """Punto medio entre los dos nucleos, en fraccion del frame."""
            p = 0.5 * (na[k] + nb[k])
            return p[0] / W_px, p[1] / H_px

        # --- 1. los dos discos YA se acercan; entra el HUD -----------
        self.add(contador)
        tramo(1.0, 0, 30, FadeIn(marca, shift=DOWN * 0.16))
        tramo(1.35, 30, 70, FadeIn(pie.etiqueta), FadeIn(pie.sub))

        # --- 2. las tres reglas, una a una --------------------------
        for i, et in enumerate(regs):
            a = 70 + i * 40
            tramo(1.3, a, a + 40, FadeIn(et, shift=RIGHT * 0.15))

        # --- 3. la aproximacion, con el puente que mide -------------
        pinta_puente(196, 1.0)
        tramo(0.45, 190, 202, Create(puente))
        vivos.append(pinta_puente)
        tramo(4.2, 202, 330)
        vivos.remove(pinta_puente)
        tramo(0.5, 330, 345, FadeOut(puente))

        # --- 4. camara lenta en el pericentro, zoom al punto medio ---
        def acercar(frac, W_, H_):
            cx, cy = medio(int(round(345 + frac * 30)))
            return (0.5 + (cx - 0.5) * frac, 0.5 + (cy - 0.5) * frac,
                    1.0 + (self.ZOOM - 1.0) * frac)
        tramo(2.0, 345, 375, encuadre=acercar)

        def quieto(frac, W_, H_):
            cx, cy = medio(int(round(375 + frac * 25)))
            return cx, cy, self.ZOOM
        tramo(3.2, 375, 400, encuadre=quieto)     # el frame 386 cae aqui

        # --- 5. se abre y salen los brazos de marea -----------------
        def abrir(frac, W_, H_):
            cx, cy = medio(int(round(400 + frac * 78)))
            return (cx + (0.5 - cx) * frac, cy + (0.5 - cy) * frac,
                    self.ZOOM + (1.0 - self.ZOOM) * frac)
        tramo(2.6, 400, 478, encuadre=abrir,
              ritmo=em.ritmo_por_tramos([(0, 0), (0.3, 0.10), (1, 1)]))

        # --- 6. las reglas ya hicieron su trabajo; los brazos, no ---
        tramo(0.5, 478, 493, FadeOut(regs, scale=0.94))

        # --- 7. las trayectorias de los nucleos, tenues -------------
        self.add(rastro)
        vivos.append(pinta_rastro)
        tramo(5.1, 493, 700, rev=(0.0, 1.0))

        # --- 8. remate 1: la energia que el integrador conserva -----
        energia = medida(txt_deriva, "deriva de energia", "por ciento")
        tramo(0.35, 700, 712, FadeOut(contador, scale=0.92),
              FadeOut(pie.etiqueta, scale=0.92), FadeOut(pie.sub, scale=0.92),
              contar=False)
        tramo(0.45, 712, 730, FadeIn(energia, scale=1.06), contar=False)
        tramo(3.6, 730, 840, contar=False)

        # --- 9. remate 2: las estrellas que cambian de galaxia ------
        trasvase = medida(f"{pct_cambian:.1f}", "cambian de galaxia",
                          "de 4000 estrellas")
        tramo(0.35, 840, 852, FadeOut(energia, scale=0.92), contar=False)
        tramo(0.45, 852, 870, FadeIn(trasvase, scale=1.06), contar=False)
        tramo(2.4, 870, T - 1, contar=False)
        self.wait(1.1)

        cerrar_pieza(self)
