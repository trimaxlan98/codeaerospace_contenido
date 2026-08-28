class Clip(Scene):
    """02 · El moho — 60 000 agentes sin cerebro tienden una red.

    El fotograma entero es `em.moho.simular()` (Physarum de Jones sobre diez
    puntos de comida): cada agente huele la estela en tres puntos, gira hacia
    el olor mas fuerte, avanza y deposita. De ahi sale una malla que se
    engrosa y se PODA sola.

    Arco, medido en este render antes de escribirlo:
      - la malla ya esta tendida desde el primer segundo (arranca en el
        frame 36: los frames 0-30 son el lavado de la normalizacion
        monotona, no estructura);
      - camara lenta en la PODA, que es donde el esqueleto adelgaza mas
        deprisa (medido adelgazando frames sueltos: 8223 px de malla en el
        70, 7467 en el 170, 6876 en el 220, 4916 en el 749; el tramo
        170-280 es el de mayor caida);
      - zoom 1.6 a la ventana con MAS bifurcaciones del esqueleto,
        localizada en el render con una imagen integral (921 de las 1928
        bifurcaciones caen dentro);
      - las diez comidas se marcan con anillos ambar vectoriales sobre
        `extra["comida"]`;
      - al final se enciende en cian `extra["caminos"]` — la mascara (H,W)
        de los caminos que MIDEN `red_px` — como una segunda pelicula opaca
        sobre el ultimo frame (convertirla a mobjects serian miles de
        trazos), y encima el arbol minimo euclideo en gris.

    Cifras, las dos de `cifras` de ESTE render: "950 px" (red_px = 950.16)
    y "1.18" (red_vs_arbol = 1.1784) sobre 10 comidas conectadas de 10.
    """

    ZOOM = 1.6
    F0 = 36                 # primer frame con estructura (0-30 = lavado)

    @staticmethod
    def halo(mob, w=7.0):
        """Contorno oscuro DETRAS de la letra.

        Segunda linea de defensa sobre los `velos_de_contraste` del bloque
        de estilo: la malla verde brilla casi tanto como la tinta y aqui el
        pie de cifra cae ADEMAS sobre la red cian. Sin halo, en el primer
        render "2 . GIRAR AL RASTRO" desaparecia a la altura de "AL". El
        trazo va de fondo para que no engorde el glifo.
        """
        mob.set_stroke(color=CODE_BG, width=w, opacity=0.95, background=True)
        return mob

    def construct(self):
        # --- lo que se mide (antes de dibujar nada) ------------------
        r = em.moho.simular()          # 60000 agentes, 10 comidas, semilla 1
        F, cifras, extra = r["frames"], r["cifras"], r["extra"]
        W, H = extra["res"]
        T = len(F)
        comida = np.asarray(extra["comida"], dtype=np.float64)
        segmentos = np.asarray(extra["mst_segmentos"], dtype=np.float64)
        red_px = int(round(cifras["red_px"]))
        veces = cifras["red_vs_arbol"]
        unidas = cifras["comidas_conectadas"]

        # --- la ventana del zoom: donde MAS se bifurca el esqueleto --
        # Bifurcacion = pixel de esqueleto con 3 o mas vecinos. La ventana
        # que se busca es exactamente la que se va a ver (W/ZOOM x H/ZOOM),
        # asi que el centro que sale es honesto con lo que se encuadra.
        esq = np.asarray(extra["esqueleto"])
        p = np.zeros((H + 2, W + 2), dtype=bool)
        p[1:-1, 1:-1] = esq
        vecinos = (p[0:-2, 1:-1].astype(np.int8) + p[0:-2, 2:] + p[1:-1, 2:]
                   + p[2:, 2:] + p[2:, 1:-1] + p[2:, 0:-2] + p[1:-1, 0:-2]
                   + p[0:-2, 0:-2])
        bif = (esq & (vecinos >= 3)).astype(np.int32)
        zw = int(round(W / self.ZOOM))
        zh = int(round(zw * H / W))
        ii = np.pad(np.cumsum(np.cumsum(bif, axis=0), axis=1),
                    ((1, 0), (1, 0)))
        mejor, bx, by = -1, 0, 0
        for y0 in range(0, H - zh + 1, 2):
            for x0 in range(0, W - zw + 1, 2):
                v = (ii[y0 + zh, x0 + zw] - ii[y0, x0 + zw]
                     - ii[y0 + zh, x0] + ii[y0, x0])
                if v > mejor:
                    mejor, bx, by = v, x0, y0
        ZX, ZY = (bx + zw / 2) / W, (by + zh / 2) / H

        # --- la capa cian: los caminos medidos, encendiendose --------
        # Segunda pila opaca construida sobre el ULTIMO frame: el cian
        # brota del centro hacia fuera y deja el mapa de la red que
        # produjo `red_px`. Va a z=-490: encima de la pelicula (-500) y
        # DEBAJO de los velos de contraste del style_block (-450), o el
        # pie de cifra se quedaria sin suelo justo al entrar la cifra.
        cam = np.asarray(extra["caminos"], dtype=bool)
        q = np.zeros((H + 2, W + 2), dtype=bool)
        q[1:-1, 1:-1] = cam
        gordo = (q[0:-2, 1:-1] | q[2:, 1:-1] | q[1:-1, 0:-2] | q[1:-1, 2:]
                 | q[1:-1, 1:-1])
        yy, xx = np.mgrid[0:H, 0:W]
        d = np.hypot((xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2))
        d /= d.max()
        base = F[T - 1].astype(np.float32)
        rgb_cian = em.hex_a_rgb(C_MEDIDO)
        N_CIAN = 34
        pila = np.empty((N_CIAN, H, W, 3), dtype=np.uint8)
        for i in range(N_CIAN):
            a = i / (N_CIAN - 1)
            enc = gordo & (d <= a * 1.25)
            mezcla = base * 0.18 + rgb_cian[None, None, :] * (0.55 + 0.45 * a)
            pila[i] = np.where(enc[..., None], np.clip(mezcla, 0, 255),
                               base).astype(np.uint8)

        # --- puesta en escena ---------------------------------------
        peli = pelicula(F)
        peli.mostrar(self.F0)
        self.add(peli.mob)

        marca = self.halo(hud_pieza("02 . el moho"))
        regs = self.halo(reglas(["1 . oler adelante", "2 . girar al rastro",
                                 "3 . dejar rastro"]))

        nodos = VGroup()
        for c in px_a_escena(comida, peli.mob, W, H):
            nodos.add(Circle(radius=0.30, stroke_color=C_REGLA,
                             stroke_width=3.0, stroke_opacity=0.95)
                      .move_to(c))
        nodos.set_z_index(60)

        arbol = VGroup()
        for x0, y0, x1, y1 in segmentos:
            a, b = px_a_escena(np.array([[x0, y0], [x1, y1]]), peli.mob, W, H)
            arbol.add(Line(a, b, stroke_color=C_EXTERNO, stroke_width=3.0))
        arbol.set_z_index(50)

        peli_cian = pelicula(pila, z=-490)
        peli_cian.mostrar(0)

        def tramo(run_time, desde, hasta, *otras, ritmo=None, encuadre=None):
            # SIN run_time a nivel de play: cada animacion de encima
            # conserva el suyo (un FadeIn estirado a 3 s se lee como un
            # rotulo que no acaba de entrar).
            self.play(peli.animacion(run_time, desde=desde, hasta=hasta,
                                     ritmo=ritmo, encuadre=encuadre),
                      *otras)

        # --- 1. la malla ya esta tendida (gancho) --------------------
        # 104 frames en 1.5 s: el ojo entra con la malla ya moviendose.
        tramo(1.5, self.F0, 140,
              FadeIn(marca, shift=DOWN * 0.16, run_time=0.7))

        # --- 2. las tres reglas, sobre la poda a camara lenta --------
        # 140->170 casi a ritmo real; 170->280 es el tramo donde el
        # esqueleto adelgaza mas deprisa: ahi se baja a ~18 frames/s.
        tramo(1.4, 140, 170,
              FadeIn(regs[0], shift=RIGHT * 0.15, run_time=0.55))
        tramo(3.0, 170, 225,
              FadeIn(regs[1], shift=RIGHT * 0.15, run_time=0.55))
        tramo(3.0, 225, 280,
              FadeIn(regs[2], shift=RIGHT * 0.15, run_time=0.55))

        # --- 3. se recupera el ritmo y la camara entra --------------
        tramo(1.6, 280, 360)
        tramo(2.6, 360, 420, encuadre=em.zoom_hacia(ZX, ZY, self.ZOOM))
        tramo(2.6, 420, 480, encuadre=lambda frac, w, h: (ZX, ZY, self.ZOOM))
        tramo(2.2, 480, 540,
              encuadre=lambda frac, w, h: (ZX, ZY, self.ZOOM ** (1.0 - frac)))

        # --- 4. las diez comidas, marcadas --------------------------
        tramo(2.6, 540, 620,
              LaggedStart(*[GrowFromCenter(n) for n in nodos],
                          lag_ratio=0.12, run_time=2.0))
        tramo(3.4, 620, T - 1)

        # --- 5. la red medida, en cian ------------------------------
        pie = self.halo(medida(f"{red_px} px", "longitud de la red",
                               f"{unidas} comidas unidas"))
        self.add(peli_cian.mob)
        self.play(peli_cian.animacion(2.0, desde=0, hasta=N_CIAN - 1),
                  FadeIn(pie.etiqueta, run_time=0.9),
                  FadeIn(pie.numero, run_time=0.9),
                  FadeIn(pie.sub, run_time=0.9),
                  FadeOut(regs, run_time=0.8))

        # --- 6. y el arbol minimo con el que se compara -------------
        self.play(LaggedStart(*[Create(s) for s in arbol],
                              lag_ratio=0.12, run_time=1.9))
        self.wait(0.9)

        # --- 7. la cifra ---------------------------------------------
        remate = self.halo(medida(f"{veces:.2f}", "red / arbol minimo",
                                  f"{unidas} comidas unidas"))
        cambiar(self, [pie.numero, pie.etiqueta],
                [remate.numero, remate.etiqueta])
        self.wait(2.6)

        cerrar_pieza(self)
