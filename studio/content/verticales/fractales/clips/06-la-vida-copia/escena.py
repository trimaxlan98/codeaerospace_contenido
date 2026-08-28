class Clip(Scene):
    """06 · La vida copia — por que un arbol es asi.

    Leonardo lo anoto en un cuaderno: el tronco de un arbol y la suma de sus
    ramas tienen la MISMA seccion. Con dos hijas por rama, eso obliga a que
    cada hija tenga el grosor de la madre dividido por raiz de dos, y de ahi
    sale todo lo demas.

    El arbol crece ocho generaciones y la cifra de la seccion total no se
    mueve: **1.000**, generacion tras generacion. La longitud total, en
    cambio, se multiplica por **52.2**. Al final el tronco se parte en 2, 4,
    8... 256 baldosas que juntas ocupan EXACTAMENTE el mismo cuadrado: la
    regla de Leonardo, dibujada. (Baldosas y no circulos a proposito: 256
    circulos en rejilla ocupan un envoltorio mas grande que el original
    —el empaquetado deja un 22 % de aire— y la imagen diria lo contrario
    de lo que dice la cifra. Partiendo un cuadrado alternando lado, el
    envoltorio es el mismo hasta el pixel.)

    Todo lo calcula `arbol_davinci` en este render.
    """

    NIVELES = 8
    ANGULO = 30.0
    ANGULOS = (16.0, 30.0, 46.0, 62.0)
    ALTO = 5.1
    Y_BASE = -1.45

    def construct(self):
        arbol = fr.arbol_davinci(self.NIVELES, angulo_deg=self.ANGULO)
        pts = np.array([p for capa in arbol["ramas"]
                        for (a, b, _) in capa for p in (a, b)])
        escala = self.ALTO / (pts[:, 1].max() - pts[:, 1].min())

        hud_top = hud_pieza("06 . la vida copia")
        etiqueta = hud("seccion total", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        numero = cifra(f"{arbol['seccion_relativa'][0]:.3f}", font_size=104)
        numero.move_to(UP * Y_NUMERO)
        sub = hud("1 rama", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)

        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        # =============================================================
        # 1. El arbol crece y la seccion NO se mueve
        # =============================================================
        capas = self._capas(arbol, escala)
        self.play(Create(capas[0]), FadeIn(etiqueta), FadeIn(numero),
                  FadeIn(sub), run_time=1.0)
        for g in range(1, self.NIVELES + 1):
            sub_nuevo = hud(f"{2 ** g} ramas", font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            self.remove(sub)
            self.add(sub_nuevo)
            sub = sub_nuevo
            self.play(Create(capas[g], lag_ratio=0.04), run_time=0.62)
        self.wait(1.1)
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(1.3)

        # =============================================================
        # 2. Lo que si crecio: la longitud
        # =============================================================
        et_largo = hud("longitud total", font_size=20, color=CODE_MUTED)
        et_largo.move_to(UP * Y_ETIQUETA)
        num_largo = cifra(f"{arbol['largo_total'][-1]:.1f}", font_size=104)
        num_largo.move_to(UP * Y_NUMERO)
        sub_largo = hud("x el tronco", font_size=18, color=C_REGLA)
        sub_largo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_largo, num_largo, sub_largo])
        self.wait(2.8)

        # =============================================================
        # 3. El mismo programa, otro angulo, otro cuerpo
        # =============================================================
        et_sec = hud("seccion total", font_size=20, color=CODE_MUTED)
        et_sec.move_to(UP * Y_ETIQUETA)
        num_sec = cifra("1.000", font_size=104)
        num_sec.move_to(UP * Y_NUMERO)
        sub_sec = hud("a cualquier angulo", font_size=18, color=C_REGLA)
        sub_sec.move_to(UP * Y_SUB)
        cambiar(self, [et_largo, num_largo, sub_largo],
                [et_sec, num_sec, sub_sec])

        actual = VGroup(*capas)
        for ang in self.ANGULOS:
            otro = fr.arbol_davinci(self.NIVELES, angulo_deg=ang)
            nuevo = VGroup(*self._capas(otro, escala))
            self.play(FadeOut(actual), run_time=0.35)
            self.play(FadeIn(nuevo), run_time=0.45)
            actual = nuevo
            self.wait(0.85)
        self.wait(0.6)

        # =============================================================
        # 4. La regla de Leonardo, dibujada: un disco = 256 discos
        # =============================================================
        self.play(FadeOut(actual), run_time=0.6)
        baldosas = None
        for k in range(self.NIVELES + 1):
            nuevos = self._baldosas(k)
            sub_nuevo = hud(f"{2 ** k} " + ("rama" if k == 0 else "ramas"),
                            font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            self.remove(sub_sec)
            self.add(sub_nuevo)
            sub_sec = sub_nuevo
            if baldosas is None:
                self.play(FadeIn(nuevos, scale=1.2), run_time=0.7)
            else:
                # Sin cruce: las dos rejillas en el mismo sitio a la vez se
                # leen como una tercera rejilla que no existe.
                self.remove(baldosas)
                self.play(FadeIn(nuevos), run_time=0.5)
            baldosas = nuevos
        self.wait(2.9)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, baldosas, et_sec, num_sec,
                                         sub_sec)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _capas(self, arbol, escala):
        """Una VGroup por generacion, con el grosor que manda la regla.

        La escala se pasa desde fuera (la del arbol de 30 grados) para que
        al cambiar el angulo el arbol crezca o se abra de verdad, en vez de
        re-encuadrarse y parecer siempre igual de grande.
        """
        pts = np.array([p for capa in arbol["ramas"]
                        for (a, b, _) in capa for p in (a, b)])
        cx = (pts[:, 0].min() + pts[:, 0].max()) / 2.0
        y0 = pts[:, 1].min()

        def punto(p):
            return np.array([(p[0] - cx) * escala,
                             (p[1] - y0) * escala + self.Y_BASE, 0.0])

        capas = []
        for g, capa in enumerate(arbol["ramas"]):
            t = g / max(self.NIVELES, 1)
            color = interpolate_color(ManimColor(C_REGLA),
                                      ManimColor(C_VIDA), t)
            vg = VGroup(*[
                Line(punto(a), punto(b),
                     stroke_width=max(1.1, gro * escala * 34.0), color=color)
                for a, b, gro in capa])
            capas.append(vg)
        return capas

    def _baldosas(self, k):
        """2**k baldosas que TESELAN el cuadrado del tronco, sin huecos.

        Partiendo alternando lado (primero a lo ancho, luego a lo alto), el
        envoltorio es exactamente el mismo cuadrado en las nueve etapas: lo
        que se ve es que la seccion no se pierde ni se gana, solo se
        reparte. Con circulos no saldria: el empaquetado dejaria aire y el
        montoncito de 256 se veria MAS grande que el tronco.
        """
        lado = 3.4
        cols = 2 ** math.ceil(k / 2)
        filas = 2 ** (k // 2)
        w = lado / cols
        h = lado / filas
        g = VGroup()
        for fila in range(filas):
            for col in range(cols):
                x = -lado / 2 + w * (col + 0.5)
                y = lado / 2 - h * (fila + 0.5)
                g.add(Rectangle(width=w, height=h,
                                stroke_width=max(0.7, 2.2 * min(w, h)),
                                stroke_color=C_REGLA, fill_color=C_REGLA,
                                fill_opacity=0.26)
                      .move_to(np.array([x, y + Y_ESCENA, 0.0])))
        return g
