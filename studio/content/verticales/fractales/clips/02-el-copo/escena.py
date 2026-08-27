class Clip(Scene):
    """02 · El copo — perimetro infinito, area finita.

    Un triangulo. Una sola instruccion: parte cada lado en tres y levanta un
    pico en el tercio central. Aplicada cinco veces, los picos crecen a la
    vista (la curva se reconstruye con `altura` de 0 a 1, asi que el numero
    de puntos NO cambia durante el barrido y no hay que casar estructuras
    distintas).

    El perimetro se multiplica por 4/3 en cada pasada — 15.59, 20.79, 27.71,
    36.95, 49.27, 65.69 — mientras el area se estanca contra un techo: 1.590
    veces el triangulo, camino de 8/5. Las cifras salen de `koch_perimetro`
    y `koch_area`, y `area_poligono` sobre los puntos DIBUJADOS da lo mismo
    hasta la sexta cifra (lo comprueba la sonda de la libreria).
    """

    RADIO = 3.0
    NIVELES = 5
    DUR_NIVEL = (2.6, 2.4, 2.2, 2.0, 2.0)

    ALTO = 5.6                # el copo del nivel 5 mide 6.0 de alto
    GAUGE_X = -3.15
    GAUGE_BASE = -1.50
    GAUGE_ALTO = 4.60
    GAUGE_TOPE = 2.0          # el aforo del medidor, en multiplos de A0

    def construct(self):
        lado = fr.koch_lado_inicial(self.RADIO)
        perimetros = [fr.koch_perimetro(n, lado)
                      for n in range(self.NIVELES + 1)]
        areas = [fr.koch_area(n, lado) for n in range(self.NIVELES + 1)]
        razon_area = [a / areas[0] for a in areas]

        # Escala FIJA (no `.height` por nivel: el copo tiene que quedarse
        # clavado mientras le crecen los picos, no re-encuadrarse solo).
        escala = self.ALTO / (2.0 * self.RADIO)

        def curva(nivel, altura=1.0):
            pts = fr.copo_koch(nivel, self.RADIO, altura=altura)
            return [np.array([x * escala, y * escala + Y_ESCENA, 0.0])
                    for x, y in pts]

        hud_top = hud_pieza("02 . el copo")
        copo = VMobject(stroke_color=C_MEDIDO, stroke_width=2.6)
        copo.set_points_as_corners(curva(0))
        copo.set_z_index(10)

        aforo, techo, relleno_aforo = self._aforo()
        pie = medida(f"{perimetros[0]:5.2f}", etiqueta="perimetro",
                     sub="nivel 0")
        etiqueta, sub, numero = pie.etiqueta, pie.sub, pie.numero
        vivos = [hud_top, copo, aforo, techo, relleno_aforo, etiqueta, sub,
                 numero]

        # =============================================================
        # 1. El triangulo de partida y los dos instrumentos
        # =============================================================
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)
        self.play(Create(copo), run_time=2.2)
        relleno_aforo.stretch_to_fit_height(self._altura_aforo(razon_area[0]))
        relleno_aforo.move_to(np.array([
            self.GAUGE_X,
            self.GAUGE_BASE + relleno_aforo.height / 2, 0.0]))
        self.play(FadeIn(etiqueta), FadeIn(numero), FadeIn(sub),
                  Create(aforo), Create(techo), FadeIn(relleno_aforo),
                  run_time=1.0)
        self.wait(0.6)

        # =============================================================
        # 2. Cinco pasadas de la misma instruccion
        # =============================================================
        for n in range(1, self.NIVELES + 1):
            copo.set_points_as_corners(curva(n, altura=0.0))
            self.play(
                UpdateFromAlphaFunc(
                    copo,
                    lambda m, a, _n=n: m.set_points_as_corners(
                        curva(_n, altura=a))),
                self._crecer_aforo(relleno_aforo, razon_area[n]),
                run_time=self.DUR_NIVEL[n - 1],
                rate_func=rate_functions.ease_in_out_sine)
            copo.clear_updaters()

            num_nuevo = cifra(f"{perimetros[n]:5.2f}")
            num_nuevo.move_to(UP * Y_NUMERO)
            sub_nuevo = hud(f"nivel {n}", font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            cambiar(self, [numero, sub], [num_nuevo, sub_nuevo])
            for m in (numero, sub):
                vivos.remove(m)
            numero, sub = num_nuevo, sub_nuevo
            vivos += [numero, sub]
            self.wait(0.3)

        self.wait(0.9)

        # =============================================================
        # 3. Lo que crecio el perimetro
        # =============================================================
        sub_nuevo = hud(f"x {perimetros[-1] / perimetros[0]:.2f} en 5 pasadas",
                        font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, sub, sub_nuevo)
        vivos.remove(sub)
        sub = sub_nuevo
        vivos.append(sub)
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(2.1)

        # =============================================================
        # 4. Y lo poco que crecio el area (el aforo, clavado en el techo)
        # =============================================================
        relleno_copo = Polygon(*curva(self.NIVELES), stroke_width=0,
                               fill_color=C_ATRAPADO, fill_opacity=0.0)
        relleno_copo.set_z_index(5)
        self.add(relleno_copo)
        vivos.append(relleno_copo)
        self.play(relleno_copo.animate.set_fill(opacity=0.30),
                  Indicate(relleno_aforo, color=C_TINTA,
                           scale_factor=1.0), run_time=1.4)

        et_nuevo = hud("area", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{razon_area[-1]:5.3f}")
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("x el triangulo", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        for m in (etiqueta, numero, sub):
            vivos.remove(m)
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        vivos += [etiqueta, numero, sub]
        self.wait(4.6)

        # =============================================================
        # 5. Fundido a fondo limpio
        # =============================================================
        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in vivos], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _altura_aforo(self, razon):
        return max(0.001, self.GAUGE_ALTO * razon / self.GAUGE_TOPE)

    def _aforo(self):
        """El medidor de area: caja vacia, techo de 8/5 punteado y relleno.

        El techo NO se rotula: se dibuja. Que el relleno se pare justo ahi
        mientras la cifra del perimetro corre es toda la leccion del clip.
        """
        caja = Rectangle(width=0.40, height=self.GAUGE_ALTO,
                         stroke_width=1.6, stroke_color=C_EJE,
                         fill_opacity=0.0)
        caja.move_to(np.array([self.GAUGE_X,
                               self.GAUGE_BASE + self.GAUGE_ALTO / 2, 0.0]))
        y_techo = self.GAUGE_BASE + self._altura_aforo(1.6)
        # El techo va en tinta, NO en violeta: si comparte color con el
        # relleno se confunde con el borde del liquido justo cuando el
        # relleno llega a rozarlo, que es el instante que hay que ver.
        techo = DashedLine(
            np.array([self.GAUGE_X - 0.48, y_techo, 0.0]),
            np.array([self.GAUGE_X + 0.48, y_techo, 0.0]),
            stroke_width=3.0, color=C_TINTA, dash_length=0.11)
        relleno = Rectangle(width=0.40, height=self.GAUGE_ALTO,
                            stroke_width=0, fill_color=C_ATRAPADO,
                            fill_opacity=0.45)
        return caja, techo, relleno

    def _crecer_aforo(self, relleno, razon):
        """El relleno del aforo, estirado desde su BASE (un `scale` lo
        despegaria del suelo del medidor)."""
        h = self._altura_aforo(razon)
        destino = relleno.copy()
        destino.stretch_to_fit_height(h)
        destino.move_to(np.array([self.GAUGE_X,
                                  self.GAUGE_BASE + h / 2, 0.0]))
        return Transform(relleno, destino)
