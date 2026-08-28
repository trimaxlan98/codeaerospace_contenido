class Clip(Scene):
    """03 · La dimension — el numero que no es entero.

    La misma pregunta tres veces: si encojo la figura a un factor f, ¿cuantas
    copias necesito para rehacerla? La respuesta define la dimension,
    D = log(copias) / log(1/f), y con eso la recta da 1 y el cuadrado da 2.
    Koch da 4 copias a un tercio: **1.2619**. No es un error de medida — es
    lo que vale.

    Despues, la costa del clip 01 vuelve bajo una rejilla que se afina:
    12, 32, 72 y 161 cajas para lados 2, 1, 1/2 y 1/4. La pendiente del
    ajuste da 1.2408. Todas las cifras salen de `dimension_autosemejanza` y
    `conteo_cajas`; las cajas que se ven en pantalla SON las que se cuentan.
    """

    Y_FIG = 1.70
    COSTA = dict(nivel=12, H=0.75, semilla=17, largo=10.0, amplitud=3.6)
    LADOS = (2.0, 1.0, 0.5, 0.25)
    NOMBRE_LADO = ("lado 2", "lado 1", "lado 1/2", "lado 1/4")
    ALTO_COSTA = 6.0

    def construct(self):
        hud_top = hud_pieza("03 . la dimension")
        etiqueta = hud("dimension", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        numero = None
        sub = None

        # =============================================================
        # 1. Recta, cuadrado y Koch: la misma cuenta, tres respuestas
        # =============================================================
        casos = (self._recta(), self._cuadrado(), self._koch())
        for k, (figura, piezas, copias, factor, texto_sub) in enumerate(casos):
            valor = fr.dimension_autosemejanza(copias, factor)
            num_nuevo = cifra(f"{valor:.4f}", font_size=96)
            num_nuevo.move_to(UP * Y_NUMERO)
            sub_nuevo = hud(texto_sub, font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)

            self.play(Create(figura), run_time=1.1)
            if numero is None:
                self.play(FadeIn(etiqueta), FadeIn(num_nuevo),
                          FadeIn(sub_nuevo), run_time=0.6)
            else:
                cambiar(self, [numero, sub], [num_nuevo, sub_nuevo])
            numero, sub = num_nuevo, sub_nuevo

            # las copias se separan para que se puedan CONTAR
            self.add(piezas)
            self.play(FadeOut(figura),
                      *[p.animate.shift(d) for p, d in piezas.desvios],
                      run_time=1.2)
            self.wait(1.5 if k < 2 else 2.6)
            if k < len(casos) - 1:
                self.play(FadeOut(piezas), run_time=0.5)
            else:
                self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                                num_lines=14, flash_radius=1.0),
                          run_time=0.9)
                self.wait(0.8)
                self.play(FadeOut(piezas), run_time=0.6)

        # =============================================================
        # 2. Y una costa, que no tiene copias exactas: se cuentan cajas
        # =============================================================
        costa = fr.costa(**self.COSTA)
        recuento = fr.conteo_cajas(costa, lados=list(self.LADOS))
        linea = fr.poligonal(costa, color=C_VIDA, grosor=2.2)
        linea.apply_function(self._al_lienzo(costa))
        linea.set_z_index(10)

        et_cajas = hud("cajas", font_size=20, color=CODE_MUTED)
        et_cajas.move_to(UP * Y_ETIQUETA)
        self.play(Create(linea), run_time=1.4)
        cambiar(self, [etiqueta, numero, sub], et_cajas)
        etiqueta = et_cajas
        numero = sub = None

        rejilla = None
        for i, lado in enumerate(self.LADOS):
            nueva = fr.rejilla_cajas(costa, lado, color=C_REGLA, grosor=1.3,
                                     opacidad=0.75)
            nueva.apply_function(self._al_lienzo(costa))
            nueva.set_z_index(5)
            num_nuevo = cifra(f"{recuento['conteos'][i]}", font_size=96)
            num_nuevo.move_to(UP * Y_NUMERO)
            sub_nuevo = hud(self.NOMBRE_LADO[i], font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            anims = [FadeIn(nueva, lag_ratio=0.02)]
            if rejilla is not None:
                anims.append(FadeOut(rejilla))
            if numero is None:
                anims += [FadeIn(num_nuevo), FadeIn(sub_nuevo)]
            else:
                anims += [FadeOut(numero, scale=0.92),
                          FadeIn(num_nuevo, scale=1.08),
                          FadeOut(sub, shift=DOWN * 0.1),
                          FadeIn(sub_nuevo, shift=DOWN * 0.1)]
            self.play(*anims, run_time=1.1)
            rejilla, numero, sub = nueva, num_nuevo, sub_nuevo
            self.wait(0.8)

        # =============================================================
        # 3. La pendiente del ajuste ES la dimension
        # =============================================================
        et_nuevo = hud("dimension", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{recuento['D']:.4f}", font_size=96)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("por conteo de cajas", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        self.play(Flash(num_nuevo, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(2.8)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, linea, rejilla, et_nuevo,
                                         num_nuevo, sub_nuevo)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _al_lienzo(self, costa):
        """Mapa costa -> pantalla: girada 90 grados (baja por la columna,
        como en el clip 01) y a escala fija.

        Es un giro RIGIDO mas una homotecia, asi que una caja cuadrada del
        conteo sigue siendo un cuadrado en pantalla: lo que se ve contado es
        exactamente lo que la libreria conto.
        """
        x0, x1 = costa[:, 0].min(), costa[:, 0].max()
        y0, y1 = costa[:, 1].min(), costa[:, 1].max()
        k = self.ALTO_COSTA / (x1 - x0)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

        def mapa(p):
            return np.array([(p[1] - cy) * k,
                             -(p[0] - cx) * k + self.Y_FIG - 0.45, 0.0])
        return mapa

    def _con_desvios(self, piezas, centro, empuje):
        """VGroup de copias + hacia donde se separa cada una."""
        g = VGroup(*piezas)
        desvios = []
        for p in piezas:
            d = p.get_center() - centro
            n = np.linalg.norm(d)
            u = d / n if n > 1e-6 else np.array([0.0, 1.0, 0.0])
            desvios.append((p, u * empuje))
        g.desvios = desvios
        return g

    def _recta(self):
        largo = 5.4
        c = np.array([0.0, self.Y_FIG, 0.0])
        figura = Line(c + LEFT * largo / 2, c + RIGHT * largo / 2,
                      stroke_width=5.0, color=C_MEDIDO)
        mitades = [
            Line(c + LEFT * largo / 2, c, stroke_width=5.0, color=C_REGLA),
            Line(c, c + RIGHT * largo / 2, stroke_width=5.0, color=C_REGLA)]
        return (figura, self._con_desvios(mitades, c, 0.26), 2, 0.5,
                "2 copias a 1/2")

    def _cuadrado(self):
        lado = 3.8
        c = np.array([0.0, self.Y_FIG, 0.0])
        figura = Square(side_length=lado, stroke_width=4.0, color=C_MEDIDO,
                        fill_opacity=0.0).move_to(c)
        cuartos = []
        for sx in (-1, 1):
            for sy in (-1, 1):
                q = Square(side_length=lado / 2, stroke_width=3.2,
                           color=C_REGLA, fill_color=C_REGLA,
                           fill_opacity=0.10)
                q.move_to(c + np.array([sx * lado / 4, sy * lado / 4, 0.0]))
                cuartos.append(q)
        return (figura, self._con_desvios(cuartos, c, 0.22), 4, 0.5,
                "4 copias a 1/2")

    def _koch(self):
        pts = fr.curva_koch(4, largo=6.0)
        ancho = 6.0
        escala = 6.2 / ancho
        cx = (pts[:, 0].min() + pts[:, 0].max()) / 2.0
        cy = (pts[:, 1].min() + pts[:, 1].max()) / 2.0

        def mapa(p):
            return np.array([(p[0] - cx) * escala,
                             (p[1] - cy) * escala + self.Y_FIG, 0.0])

        def curva(sub, color, grosor):
            v = VMobject(stroke_color=color, stroke_width=grosor)
            v.set_points_as_corners([mapa(q) for q in sub])
            return v

        figura = curva(pts, C_MEDIDO, 3.4)
        c = figura.get_center()
        n = (len(pts) - 1) // 4
        cuartos = [curva(pts[i * n:(i + 1) * n + 1], C_REGLA, 3.0)
                   for i in range(4)]
        return (figura, self._con_desvios(cuartos, c, 0.24), 4, 1.0 / 3.0,
                "4 copias a 1/3")
