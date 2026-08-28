class Clip(Scene):
    """14 · El mundo en una regla — las trece simulaciones del curso, vivas a
    la vez.

    El cierre del arco. En el render se corren los TRECE simuladores del
    paquete `emergencia` (mas baratos que en su pieza: menos pasos, menos
    agentes, menos granos), cada pila se encoge a una celda de 90x160 px por
    media de bloques y se SUELTA (`del`) antes de simular la siguiente, y las
    trece celdas se montan con `em.mosaico` en una rejilla 5x3. Ese mosaico es
    el fondo: trece mundos corriendo a la vez en el mismo fotograma.

    Arco: las celdas se encienden de una en una (tapas del color del fondo que
    se apagan, un tick por celda); cuando estan las trece entran las dos
    reglas que son la moraleja del curso; la camara se mete a zoom 2.5 en
    cuatro celdas (la placa, la pila, los pendulos, las galaxias) y cada una
    trae SU cifra medida en ESTE render; vuelve al mosaico entero y remata con
    las reglas HUD que ha usado el curso, contadas sobre el codigo de las
    trece piezas.

    Toda cifra en pantalla sale de la corrida barata que se VE, no de la
    corrida larga de la pieza original: la estadistica se mide sobre la
    ventana dibujada.
    """

    COLUMNAS, FILAS = 5, 3
    # Trece celdas no llenan ninguna rejilla: las dos ranuras que sobran van
    # a las esquinas de la fila de abajo, para que el hueco se lea como
    # composicion y no como una celda que falta.
    RANURAS = (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 13)
    CW, CH = 90, 160          # celda de la pila (9:16 exacto)
    T = 480                   # frames del mosaico
    ZOOM = 2.5
    T_FILM = 34.8             # segundos de pelicula (sin el cierre)

    def pedidos(self):
        """Los trece simuladores en el orden del curso (la celda i es el clip
        i+1), con los parametros RECORTADOS a proposito: el presupuesto de
        esta pieza son las trece simulaciones juntas, no una."""
        res = (270, 480)
        return [
            ("bandada", dict(semilla=1, pasos=260, res=res, agentes=2500)),
            ("moho", dict(semilla=1, pasos=240, res=res, n_agentes=40000)),
            ("arena", dict(N=121, granos=18000, pasos=260, res=res)),
            ("vida", dict(semilla=1, pasos=480, res=res)),
            ("turing", dict(semilla=1, pasos=240, res=(90, 160),
                            pasos_por_frame=40)),
            ("ondas", dict(semilla=1, pasos=340, res=res, escala=1)),
            ("chladni", dict(semilla=1, pasos=320, res=res, granos=20000)),
            ("ising", dict(semilla=1, pasos=400, res=res, celda=3)),
            ("pendulos", dict(semilla=1, pasos=320, res=res, n=120, bandas=12,
                              barras=(0, 60, 119), decaimiento=0.93)),
            ("cuencas", dict(semilla=1, pasos=300, res=res, subpasos=20)),
            ("epiciclos", dict(semilla=1, pasos=480, res=res)),
            ("rio", dict(semilla=1, res=res, frames=300)),
            ("galaxias", dict(semilla=1, res=res, frames=450, pasos=4,
                              n_a=1400, n_b=1100)),
        ]

    def encoger(self, F):
        """Pila (N,H,W,3) -> celda (T,160,90,3).

        Media de bloques, no vecino mas cercano: una decimacion cruda de una
        textura fina (la malla de Ising, los filamentos del moho) se convierte
        en ruido. Y remuestreo en el tiempo a `T` frames. Por trozos de 60
        frames para no tener nunca la pila entera convertida a entero ancho.
        """
        fy, fx = F.shape[1] // self.CH, F.shape[2] // self.CW
        idx = np.linspace(0, len(F) - 1, self.T).round().astype(np.int64)
        out = np.empty((self.T, self.CH, self.CW, 3), dtype=np.uint8)
        for a in range(0, self.T, 60):
            b = min(a + 60, self.T)
            blk = F[idx[a:b]].astype(np.uint16)
            blk = blk.reshape(b - a, self.CH, fy, self.CW, fx,
                              3).sum(axis=(2, 4))
            out[a:b] = (blk // (fx * fy)).astype(np.uint8)
        return out

    def contar_reglas(self):
        """Las reglas HUD que ha usado el curso, contadas sobre el codigo.

        La cifra final de esta pieza no la calcula un simulador: se cuenta
        aqui, en el render, abriendo las trece piezas y contando las etiquetas
        de su `reglas([...])`. Si una pieza no las declara asi, cuenta 3, que
        es el numero del molde.
        """
        base = "/workspace/studio/content/verticales/emergencia/clips"
        try:
            dirs = sorted(os.listdir(base))
        except OSError:
            dirs = []
        total = 0
        for i in range(1, 14):
            n = 0
            for d in dirs:
                if not d.startswith(f"{i:02d}-"):
                    continue
                try:
                    with open(os.path.join(base, d, "escena.py")) as fh:
                        txt = fh.read()
                except OSError:
                    continue
                j = txt.find("reglas([")
                if j >= 0:
                    trozo = txt[j:txt.find("]", j)]
                    n = trozo.count('"') // 2 + trozo.count("'") // 2
            total += n if n else 3
        return total

    def construct(self):
        # --- 1. las trece simulaciones, soltando cada pila -------------
        celdas, cif = [], {}
        for nombre, kw in self.pedidos():
            r = getattr(em, nombre).simular(**kw)
            celdas.append(self.encoger(r["frames"]))
            cif[nombre] = r["cifras"]
            del r

        W_MOS, H_MOS = self.CW * self.COLUMNAS, self.CH * self.FILAS
        hueco = np.empty((1, self.CH, self.CW, 3), dtype=np.uint8)
        hueco[:] = em.hex_a_rgb(em.C_FONDO).astype(np.uint8)
        rejilla = [hueco] * (self.COLUMNAS * self.FILAS)
        for i, ranura in enumerate(self.RANURAS):
            rejilla[ranura] = celdas[i]
        mos = em.mosaico(rejilla, self.COLUMNAS, W_MOS, H_MOS, borde=0)
        del celdas, rejilla

        # Una linea de fondo entre celdas: sin ella dos celdas brillantes
        # (la mandala y el laberinto) se tocan y se leen como una sola.
        fondo = em.hex_a_rgb(em.C_FONDO).astype(np.uint8)
        for c in range(1, self.COLUMNAS):
            mos[:, :, c * self.CW - 1:c * self.CW + 1] = fondo
        for f in range(1, self.FILAS):
            mos[:, f * self.CH - 1:f * self.CH + 1, :] = fondo

        total_reglas = self.contar_reglas()

        # --- 2. el mosaico como fondo, a todo el ancho -----------------
        # Cuelga del borde de arriba: asi el pie de cifra cae DEBAJO de la
        # imagen, sobre fondo limpio, que es donde mejor se lee un numero.
        alto = FMT.ancho * H_MOS / W_MOS
        peli = pelicula(mos, y=FMT.alto / 2 - alto / 2, alto=alto)
        self.add(peli.mob)

        ancho_celda = FMT.ancho / self.COLUMNAS
        alto_celda = alto / self.FILAS

        def centro_celda(i):
            """Centro de la celda i, en fraccion 0-1 de la pila."""
            fila, col = divmod(i, self.COLUMNAS)
            return (col + 0.5) / self.COLUMNAS, (fila + 0.5) / self.FILAS

        def sitio(i):
            fila, col = divmod(i, self.COLUMNAS)
            return np.array([-FMT.ancho / 2 + (col + 0.5) * ancho_celda,
                             FMT.alto / 2 - (fila + 0.5) * alto_celda, 0.0])

        # Tapas del color del fondo de la pila: cada celda arranca apagada.
        tapas = []
        for ranura in self.RANURAS:
            t = Rectangle(width=ancho_celda, height=alto_celda, stroke_width=0,
                          fill_color=em.C_FONDO, fill_opacity=1.0)
            t.move_to(sitio(ranura))
            t.set_z_index(-400)
            tapas.append(t)
        self.add(*tapas)

        marca = hud_pieza("14 . el mosaico")
        regs = reglas(["reglas simples", "mundos enteros"])

        # --- 3. las cifras del recorrido (medidas en ESTA corrida) -----
        # (ranura de la celda, pie de cifra). Las cuatro caen en las columnas
        # 1-3: en las de los extremos el recorte topa con el borde de la pila
        # y la celda se queda descentrada.
        pies = [
            (self.RANURAS[6],
             medida(f"{cif['chladni']['frac_nodos_final_pct']:.1f} %",
                    "arena en el nodo", "la placa que canta")),
            (self.RANURAS[2],
             medida(f"{int(cif['arena']['avalancha_mayor'])}",
                    "avalancha mayor", "la pila de arena")),
            (self.RANURAS[12],
             medida(f"{cif['galaxias']['A_capturadas_por_B_pct']:.1f} %",
                    "particulas robadas", "dos galaxias")),
            # los pendulos van los ULTIMOS a proposito: su abanico se abre en
            # el ultimo tercio de su corrida, que es donde cae esta parada.
            (self.RANURAS[8],
             medida(f"{cif['pendulos']['t_separacion_1rad']:.2f}",
                    "segundos a 1 rad", "120 pendulos")),
        ]
        final = medida(str(total_reglas), "reglas en total", "13 mundos")

        # --- 4. camara: el frac del encuadre va suavizado --------------
        # (el de la pelicula NO: un rate_func no lineal cambiaria la
        # velocidad de las trece simulaciones a la vez, y se nota)
        def suave(f):
            return f * f * (3.0 - 2.0 * f)

        def acercar(i):
            cx, cy = centro_celda(i)

            def encuadre(frac, W, H):
                s = suave(frac)
                return (0.5 + (cx - 0.5) * s, 0.5 + (cy - 0.5) * s,
                        self.ZOOM ** s)
            return encuadre

        def quieto(i):
            cx, cy = centro_celda(i)
            return lambda frac, W, H: (cx, cy, self.ZOOM)

        def viajar(a, b):
            ax, ay = centro_celda(a)
            bx, by = centro_celda(b)

            def encuadre(frac, W, H):
                s = suave(frac)
                return ax + (bx - ax) * s, ay + (by - ay) * s, self.ZOOM
            return encuadre

        def abrir(i):
            cx, cy = centro_celda(i)

            def encuadre(frac, W, H):
                s = suave(frac)
                return (cx + (0.5 - cx) * s, cy + (0.5 - cy) * s,
                        self.ZOOM ** (1.0 - s))
            return encuadre

        # --- 5. el reloj: la pelicula avanza con el tiempo del clip ----
        reloj = [0.0]

        def frame(t):
            return int(round(min(max(t / self.T_FILM, 0.0), 1.0)
                             * (self.T - 1)))

        def tramo(dt, *otras, encuadre=None):
            t0 = reloj[0]
            self.play(peli.animacion(dt, desde=frame(t0), hasta=frame(t0 + dt),
                                     encuadre=encuadre),
                      *otras, run_time=dt)
            reloj[0] = t0 + dt

        # --- 6. las celdas se encienden de una en una ------------------
        tramo(0.60, FadeOut(tapas[0]), FadeIn(marca, shift=DOWN * 0.16))
        for t in tapas[1:]:
            tramo(0.66, FadeOut(t))

        # --- 7. las trece a la vez, y la moraleja en el HUD ------------
        tramo(1.0, FadeIn(regs[0], shift=RIGHT * 0.15))
        tramo(1.0, FadeIn(regs[1], shift=RIGHT * 0.15))
        tramo(1.2)

        # --- 8. el recorrido: cuatro celdas a zoom 2.5 -----------------
        # El rotulo viejo se apaga ANTES de que entre el nuevo (nada
        # encimado), y las dos mitades del relevo llevan pelicula: un
        # fundido con el mosaico congelado se ve como un tiron.
        i0, pie0 = pies[0]
        tramo(1.8, FadeIn(pie0), encuadre=acercar(i0))
        tramo(2.2, encuadre=quieto(i0))
        antes = (i0, pie0)
        for i, pie in pies[1:]:
            tramo(0.5, FadeOut(antes[1]), encuadre=quieto(antes[0]))
            tramo(1.3, FadeIn(pie), encuadre=viajar(antes[0], i))
            tramo(2.2, encuadre=quieto(i))
            antes = (i, pie)
        tramo(2.0, FadeOut(antes[1]), encuadre=abrir(antes[0]))

        # --- 9. el mosaico entero y la cuenta de reglas ----------------
        tramo(1.2)
        tramo(1.3, FadeIn(final, shift=UP * 0.12))
        tramo(2.6)

        cerrar_pieza(self)
