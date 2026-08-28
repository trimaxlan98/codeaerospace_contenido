class Clip(Scene):
    """05 · El helecho — veinticuatro numeros y sale una planta.

    El mismo juego del clip 04 con otro dado: cuatro reglas afines en vez de
    tres, y la nube que sale es el helecho de Barnsley. Primero se acumula
    (400 -> 200 000 puntos, prefijo estable, asi que el relevo de imagenes
    no salta), despues se encienden los CUATRO MARCOS: cada regla mete un
    helecho entero dentro del helecho, y ahi se ve por que la hoja se
    parece a sus hojas.

    Las cifras: 24 coeficientes (se cuentan sobre `fr.MAPAS["helecho"]`, no
    se afirman) y el reparto REAL de los saltos medido con `ifs_reparto` —
    85.01 %, 7.05 %, 6.97 % y 0.97 % — frente a lo que promete el dado.
    """

    SEMILLA = 3
    RELEVOS = (150, 1_200, 10_000, 60_000, 200_000)
    ALTO = 6.6
    BARRA_X = -2.95

    def construct(self):
        caja = fr.caja_ifs("helecho", semilla=self.SEMILLA)
        reparto = fr.ifs_reparto("helecho", 200_000, semilla=self.SEMILLA)
        coeficientes = sum(len(m) + len(t) for m, t, _ in fr.MAPAS["helecho"])
        colores = (C_REGLA, C_MEDIDO, C_ATRAPADO, C_ESCAPA)

        hud_top = hud_pieza("05 . el helecho")
        etiqueta = hud("puntos", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        sub = hud("un dado de 4 caras", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)
        numero = None

        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        # =============================================================
        # 1. El helecho se acumula
        # =============================================================
        nube = None
        for total in self.RELEVOS:
            img = fr.imagen_ifs("helecho", total, res=(620, 900),
                                color=C_VIDA, alto_escena=self.ALTO,
                                semilla=self.SEMILLA, caja=caja)
            img.move_to(UP * Y_ESCENA)
            img.set_z_index(10)
            num_nuevo = cifra(f"{total}", font_size=96)
            num_nuevo.move_to(UP * Y_NUMERO)
            anims = [FadeIn(img)]
            if nube is None:
                anims += [FadeIn(etiqueta), FadeIn(sub), FadeIn(num_nuevo)]
                self.play(*anims, run_time=1.2)
            else:
                anims += [FadeOut(nube), FadeOut(numero, scale=0.92)]
                self.play(*anims, run_time=1.0)
                self.play(FadeIn(num_nuevo, scale=1.06), run_time=0.35)
            nube, numero = img, num_nuevo
            self.wait(0.9)

        self.wait(1.0)

        # =============================================================
        # 2. Los cuatro marcos: cada regla mete un helecho entero
        # =============================================================
        marcos = fr.marcos_ifs("helecho", alto_escena=self.ALTO, caja=caja,
                               colores=colores, semilla=self.SEMILLA,
                               grosor=2.4, opacidad=0.95)
        marcos.shift(UP * Y_ESCENA)
        marcos.set_z_index(30)
        self.play(LaggedStart(*[Create(m) for m in marcos], lag_ratio=0.45),
                  run_time=2.6)
        self.wait(2.0)

        et_nuevo = hud("numeros", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{coeficientes}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("4 reglas afines", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(2.6)

        # =============================================================
        # 3. Y el reparto REAL de los saltos
        # =============================================================
        barras = self._barras(reparto["fracciones"], colores)
        self.play(FadeOut(marcos), run_time=0.5)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in barras.barras],
                              lag_ratio=0.25), run_time=1.8)
        self.play(FadeIn(barras.marcas, lag_ratio=0.25), run_time=0.8)

        pct = reparto["fracciones"][1] * 100.0
        et_nuevo = hud("por ciento", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{pct:.2f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("en una sola regla", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(3.6)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, nube, barras, etiqueta,
                                         numero, sub)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _barras(self, fracciones, colores):
        """El reparto medido, en una columna estrecha al lado del helecho.

        La barra grande es el mapa que dibuja el tallo y la copia principal:
        85 de cada 100 saltos van ahi. Las otras tres reglas se llevan las
        migajas y aun asi son las que hacen las frondas.
        """
        alto_max = 3.9
        base = -1.55
        ancho = 0.42
        hueco = 0.16
        barras = VGroup()
        marcas = VGroup()
        x0 = self.BARRA_X - (4 * ancho + 3 * hueco) / 2 + ancho / 2
        for i, f in enumerate(fracciones):
            h = max(0.05, alto_max * f)
            x = x0 + i * (ancho + hueco)
            b = Rectangle(width=ancho, height=h, stroke_width=1.4,
                          stroke_color=colores[i], fill_color=colores[i],
                          fill_opacity=0.28)
            b.move_to(np.array([x, base + h / 2, 0.0]))
            barras.add(b)
            v = cifra(f"{f * 100:.0f}", font_size=16, color=colores[i])
            v.next_to(b, UP, buff=0.12)
            marcas.add(v)
        g = VGroup(barras, marcas)
        g.barras = barras
        g.marcas = marcas
        return g
