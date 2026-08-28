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
    el B cruza esa banda—, y el contraste lo pone el velo del style_block
    (`velos_de_contraste`, comun al curso); (2) las reglas se
    apagan cuando se abre la camara, o las colas de marea las cruzan de
    estrellas y no se leen.
    """

    ZOOM = 1.6
    PASO_TRAZA = 3          # 1 punto de la trayectoria cada 3 frames
    N_A = 2200              # particulas del disco A (las primeras de la pila)
    # El contraste del pie sobre los discos lo pone velos_de_contraste()
    # del style_block (comun a todo el curso).
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
        # los cuatro cortes del encuentro cuelgan del pericentro MEDIDO, no
        # de numeros a mano: si la libreria cambia el dt, la camara lenta
        # sigue cayendo donde pasa la cosa.
        f_cierra = peri - 41        # 345: la camara empieza a cerrarse
        f_lenta = peri - 11         # 375: entra la camara lenta
        f_sale = peri + 14          # 400: sale de la camara lenta
        f_abre = peri + 92          # 478: la camara ya esta abierta del todo

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
        tramo(4.2, 202, f_cierra - 15)
        vivos.remove(pinta_puente)
        tramo(0.5, f_cierra - 15, f_cierra, FadeOut(puente))

        # --- 4. camara lenta en el pericentro, zoom al punto medio ---
        def acercar(frac, W_, H_):
            cx, cy = medio(int(round(f_cierra + frac * (f_lenta - f_cierra))))
            return (0.5 + (cx - 0.5) * frac, 0.5 + (cy - 0.5) * frac,
                    1.0 + (self.ZOOM - 1.0) * frac)
        tramo(2.0, f_cierra, f_lenta, encuadre=acercar)

        def quieto(frac, W_, H_):
            cx, cy = medio(int(round(f_lenta + frac * (f_sale - f_lenta))))
            return cx, cy, self.ZOOM
        # 25 frames en 3.2 s: ~8 fps, el pericentro a un cuarto de velocidad
        tramo(3.2, f_lenta, f_sale, encuadre=quieto)

        # --- 5. se abre y salen los brazos de marea -----------------
        def abrir(frac, W_, H_):
            cx, cy = medio(int(round(f_sale + frac * (f_abre - f_sale))))
            return (cx + (0.5 - cx) * frac, cy + (0.5 - cy) * frac,
                    self.ZOOM + (1.0 - self.ZOOM) * frac)
        tramo(2.6, f_sale, f_abre, encuadre=abrir,
              ritmo=em.ritmo_por_tramos([(0, 0), (0.3, 0.10), (1, 1)]))

        # --- 6. las reglas ya hicieron su trabajo; los brazos, no ---
        tramo(0.5, f_abre, f_abre + 15, FadeOut(regs, scale=0.94))

        # --- 7. las trayectorias de los nucleos, tenues -------------
        self.add(rastro)
        vivos.append(pinta_rastro)
        tramo(5.1, f_abre + 15, 700, rev=(0.0, 1.0))

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
