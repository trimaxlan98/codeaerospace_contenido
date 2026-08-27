class Clip(Scene):
    """01 · La costa — el gancho del curso: una linea que no se deja medir.

    Una costa modelo baja por la pantalla. Un compas ambar la camina a
    zancadas de largo fijo y la cifra sube con cada zancada. Despues la
    regla se parte por la mitad cuatro veces: cada regla mas corta descubre
    entrantes que la anterior se saltaba, y la longitud NO converge — sube
    de 21.81 a 41.36. Al final las cinco medidas quedan como una escalera
    que sigue subiendo.

    Todas las cifras las mide `fractales.medir_con_regla` sobre ESTA costa
    (semilla 17) en este render: no hay tabla escrita a mano. Duracion
    medida: 34.70 s, y el guion de voz del clip.json esta cuadrado con los
    instantes de ESTA linea de tiempo.
    """

    # --- la costa (semilla fija: el clip es reproducible) -----------
    SEMILLA = 17
    NIVEL = 12                # 4097 puntos: hay estructura muy por debajo
    HURST = 0.75              # traza de dimension teorica 2 - H = 1.25
    LARGO = 10.0
    AMPLITUD = 3.6

    REGLAS = (1.0, 0.5, 0.25, 0.125, 0.0625)
    NOMBRE_REGLA = ("regla 1", "regla 1/2", "regla 1/4", "regla 1/8",
                    "regla 1/16")
    DUR_PASEO = (2.6, 2.3, 2.0, 1.8)      # las cuatro reglas cortas

    # --- hueco del dibujo (medido contra los renglones, no a ojo) ---
    ALTO = 6.4
    Y_CENTRO = 1.25

    def construct(self):
        # =============================================================
        # 0. La costa, sus medidas y el mapeo a la escena
        # =============================================================
        costa = fr.costa(nivel=self.NIVEL, H=self.HURST, semilla=self.SEMILLA,
                         largo=self.LARGO, amplitud=self.AMPLITUD)
        medidas = [fr.medir_con_regla(costa, r) for r in self.REGLAS]

        # La costa nace tumbada (la primera columna recorre el largo); en
        # vertical baja por la pantalla, asi que el serpenteo pasa a ser la
        # horizontal y el largo, la vertical invertida.
        def _girar(p):
            q = np.atleast_2d(np.asarray(p, dtype=float))
            return np.stack([q[:, 1], -q[:, 0]], axis=1)

        girada = _girar(costa)
        centro = np.array([(girada[:, 0].min() + girada[:, 0].max()) / 2.0,
                           (girada[:, 1].min() + girada[:, 1].max()) / 2.0])
        escala = self.ALTO / self.LARGO

        def a_pantalla(p):
            q = (_girar(p) - centro) * escala
            q = q + np.array([0.0, self.Y_CENTRO])
            return np.column_stack([q, np.zeros(len(q))])

        linea = VMobject(stroke_color=C_VIDA, stroke_width=2.4)
        linea.set_points_as_corners(list(a_pantalla(costa)))
        linea.set_z_index(10)

        hud_top = hud_pieza("01 . la costa")
        vivos = [hud_top]

        # =============================================================
        # 1. Entra la pieza y la costa se dibuja de arriba abajo
        # =============================================================
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)
        self.wait(0.4)
        self.play(Create(linea), run_time=4.0,
                  rate_func=rate_functions.ease_in_out_sine)
        vivos.append(linea)
        self.wait(0.4)

        # =============================================================
        # 2. El compas camina con la regla mas larga
        # =============================================================
        pie = medida(f"{medidas[0]['longitud']:5.2f}", etiqueta="longitud",
                     sub=self.NOMBRE_REGLA[0])
        etiqueta, sub, numero = pie.etiqueta, pie.sub, pie.numero
        vivos += [etiqueta, sub]

        cuerdas, punto = self._compas(medidas[0], a_pantalla)
        n = len(cuerdas)
        # El contador se pre-renderiza entero: `become` sobre un mobject ya
        # construido no cuesta un render de pango por frame (always_redraw
        # con Text si, y son 300 frames).
        pasos = medidas[0]["pasos"]
        valores = [k * self.REGLAS[0] for k in range(n)]
        valores[-1] = medidas[0]["longitud"]   # la ultima zancada + el resto
        parciales = []
        for v in valores:
            t = cifra(f"{v:5.2f}")
            t.move_to(UP * Y_NUMERO)
            parciales.append(t)
        contador = VGroup(parciales[0].copy())

        self.play(FadeIn(etiqueta), FadeIn(sub), FadeIn(contador),
                  run_time=0.7)
        vivos.append(contador)

        self.play(
            Create(cuerdas, lag_ratio=1.0),
            UpdateFromAlphaFunc(
                contador,
                lambda m, a: m.become(VGroup(parciales[min(int(a * n),
                                                           n - 1)]))),
            UpdateFromAlphaFunc(
                punto,
                lambda m, a: m.move_to(cuerdas[min(int(a * n),
                                                   n - 1)].get_end())),
            run_time=5.0, rate_func=linear)
        contador.clear_updaters()
        punto.clear_updaters()
        vivos += [cuerdas, punto]

        self.play(Flash(contador, color=C_MEDIDO, line_length=0.22,
                        num_lines=14, flash_radius=0.95), run_time=0.8)
        self.wait(0.7)

        # =============================================================
        # 3. La regla se parte por la mitad, cuatro veces
        # =============================================================
        for i in range(1, len(self.REGLAS)):
            med = medidas[i]
            sub_nuevo = hud(self.NOMBRE_REGLA[i], font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            camino = VMobject(stroke_color=C_REGLA, stroke_width=2.2)
            camino.set_points_as_corners(list(a_pantalla(med["vertices"])))
            camino.set_z_index(20)
            num_nuevo = cifra(f"{med['longitud']:5.2f}")
            num_nuevo.move_to(UP * Y_NUMERO)

            self.play(FadeOut(cuerdas), FadeOut(punto),
                      FadeOut(sub, shift=DOWN * 0.1),
                      FadeIn(sub_nuevo, shift=DOWN * 0.1), run_time=0.4)
            for m in (cuerdas, punto, sub):
                if m in vivos:
                    vivos.remove(m)
            sub = sub_nuevo
            vivos.append(sub)

            self.play(Create(camino), run_time=self.DUR_PASEO[i - 1],
                      rate_func=linear)
            self.play(FadeOut(contador, scale=0.92),
                      FadeIn(num_nuevo, scale=1.08), run_time=0.4)
            vivos.remove(contador)
            contador = num_nuevo
            vivos += [camino, contador]
            self.wait(0.3)
            cuerdas, punto = camino, VGroup()

        self.wait(0.7)

        # =============================================================
        # 4. Las cinco medidas, como escalera que sigue subiendo
        # =============================================================
        self.play(FadeOut(cuerdas), FadeOut(linea), run_time=0.6)
        for m in (cuerdas, linea):
            if m in vivos:
                vivos.remove(m)

        escalera = self._escalera(medidas)
        self.play(Create(escalera.suelo), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in escalera.barras],
                              lag_ratio=0.22), run_time=2.2)
        self.play(FadeIn(escalera.marcas, lag_ratio=0.2), run_time=0.9)
        vivos.append(escalera)
        self.wait(2.4)

        # =============================================================
        # 5. Fundido a fondo limpio (el empalme con la pieza siguiente)
        # =============================================================
        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in vivos], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _compas(self, med, a_pantalla):
        """Las zancadas como Lines sueltas (para encenderlas una a una) y
        el pie del compas, que va saltando de apoyo en apoyo."""
        v = a_pantalla(med["vertices"])
        cuerdas = VGroup(*[
            Line(v[i], v[i + 1], stroke_width=3.0, color=C_REGLA)
            for i in range(len(v) - 1)])
        cuerdas.set_z_index(20)
        punto = Dot(v[0], radius=0.075, color=C_REGLA)
        punto.set_z_index(30)
        return cuerdas, punto

    def _escalera(self, medidas):
        """Una barra por regla, de altura proporcional a la longitud medida.

        Ocupa el hueco que deja la costa al apagarse. Las barras van en cian
        (es una cifra medida) y encima de cada una, su valor.
        """
        alto_max = 4.9
        base = -0.90
        ancho = 0.86
        hueco = 0.34
        total = len(medidas) * ancho + (len(medidas) - 1) * hueco
        x0 = -total / 2 + ancho / 2
        techo = max(m["longitud"] for m in medidas)

        barras = VGroup()
        marcas = VGroup()
        for i, m in enumerate(medidas):
            h = alto_max * m["longitud"] / techo
            x = x0 + i * (ancho + hueco)
            b = Rectangle(width=ancho, height=h, stroke_width=1.6,
                          stroke_color=C_MEDIDO, fill_color=C_MEDIDO,
                          fill_opacity=0.20)
            b.move_to(np.array([x, base + h / 2, 0.0]))
            barras.add(b)
            v = cifra(f"{m['longitud']:.1f}", font_size=19, color=C_MEDIDO)
            v.next_to(b, UP, buff=0.14)
            marcas.add(v)
        suelo = Line(np.array([x0 - ancho / 2 - 0.22, base, 0.0]),
                     np.array([x0 + total - ancho / 2 + 0.22, base, 0.0]),
                     stroke_width=1.6, color=C_EJE)
        g = VGroup(suelo, barras, marcas)
        g.suelo = suelo
        g.barras = barras
        g.marcas = marcas
        return g
