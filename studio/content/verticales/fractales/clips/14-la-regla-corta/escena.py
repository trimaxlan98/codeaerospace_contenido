class Clip(Scene):
    """14 · La regla corta — para que sirve todo esto.

    Dos oficios de la misma idea.

    Una antena es un hilo, y lo que fija su resonancia es el LARGO del hilo,
    no lo que ocupa en la placa. Doblandolo con la regla de Koch, el mismo
    hilo cabe en un ancho 3.16 veces menor: 12.64 de hilo en un vano de
    4.00. Es la razon por la que existen las antenas fractales, y por la que
    caben varias bandas en un nanosatelite. La cifra la mide
    `antena_koch` sobre la curva que se dibuja; que la resonancia dependa
    del hilo es fisica de manual, y va en gris.

    Y un paisaje: el MISMO programa de la costa del clip 01 —parte por la
    mitad y desplaza— dibuja una cordillera. Su dimension, medida con
    `conteo_cajas` sobre el perfil dibujado, sale 1.20: la misma clase de
    objeto que la costa con la que empezo el curso.
    """

    NIVELES = 4
    VANO = 4.0
    ESCALA = 1.40           # unidades de escena por unidad de la antena
    Y_ANTENA = 2.55
    DUR_NIVEL = (1.5, 1.4, 1.3, 1.3)

    SEMILLA_T = 23
    NIVEL_T = 9
    LARGO_T = 7.0
    AMPL_T = 2.4
    Y_TERRENO = 1.10

    def construct(self):
        hud_top = hud_pieza("14 . la regla corta")
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        antenas = [fr.antena_koch(n, ancho=self.VANO)
                   for n in range(self.NIVELES + 1)]

        def a_pantalla(pts):
            p = np.asarray(pts, dtype=float)
            return [np.array([(x - self.VANO / 2) * self.ESCALA,
                              y * self.ESCALA + self.Y_ANTENA, 0.0])
                    for x, y in p]

        hilo = VMobject(stroke_color=C_REGLA, stroke_width=3.0)
        hilo.set_points_as_corners(a_pantalla(antenas[0]["puntos"]))
        hilo.set_z_index(20)
        vano = self._vano()

        etiqueta = hud("hilo", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        numero = cifra(f"{antenas[0]['longitud_hilo']:5.2f}", font_size=104,
                       color=C_REGLA)
        numero.move_to(UP * Y_NUMERO)
        sub = hud("en un vano de 4", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)

        self.play(Create(hilo), Create(vano), FadeIn(etiqueta),
                  FadeIn(numero), FadeIn(sub), run_time=1.4)
        self.wait(0.7)

        # =============================================================
        # 1. El hilo se dobla: mas largo, mismo vano
        # =============================================================
        for n in range(1, self.NIVELES + 1):
            hilo.set_points_as_corners(
                a_pantalla(fr.curva_koch(n, largo=self.VANO, altura=0.0)))
            self.play(
                UpdateFromAlphaFunc(
                    hilo,
                    lambda m, a, _n=n: m.set_points_as_corners(
                        a_pantalla(fr.curva_koch(_n, largo=self.VANO,
                                                 altura=a)))),
                run_time=self.DUR_NIVEL[n - 1],
                rate_func=rate_functions.ease_in_out_sine)
            hilo.clear_updaters()
            num_nuevo = cifra(f"{antenas[n]['longitud_hilo']:5.2f}",
                              font_size=104, color=C_REGLA)
            num_nuevo.move_to(UP * Y_NUMERO)
            self.remove(numero)
            self.add(num_nuevo)
            numero = num_nuevo
            self.wait(0.35)

        self.wait(1.0)

        # =============================================================
        # 2. El mismo hilo, estirado: no cabe
        # =============================================================
        largo = antenas[-1]["longitud_hilo"]
        recta = Line(np.array([-largo * self.ESCALA / 2, 0.55, 0.0]),
                     np.array([largo * self.ESCALA / 2, 0.55, 0.0]),
                     stroke_width=3.0, color=C_ESCAPA)
        recta.set_z_index(20)
        self.play(Create(recta), run_time=1.3)

        et_nuevo = hud("veces mas corta", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{antenas[-1]['plegado']:.2f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("con el mismo hilo", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(2.2)

        nota = nota_externa("manda el hilo", font_size=17)
        nota.move_to(UP * Y_SUB)
        cambiar(self, sub, nota, salida=0.26, entrada=0.32)
        sub = nota
        self.wait(2.4)

        # =============================================================
        # 3. Y el mismo programa de la costa, hecho cordillera
        # =============================================================
        self.play(FadeOut(hilo), FadeOut(recta), FadeOut(vano), run_time=0.7)

        perfiles = [self._perfil(k) for k in range(2, self.NIVEL_T + 1)]
        et_nuevo = hud("un paisaje", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        sub_nuevo = hud("parte y desplaza", font_size=18, color=C_VIDA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub], [et_nuevo, sub_nuevo])
        etiqueta, sub, numero = et_nuevo, sub_nuevo, None

        actual = perfiles[0]
        self.play(Create(actual), run_time=1.1)
        for siguiente in perfiles[1:]:
            self.remove(actual)
            self.add(siguiente)
            actual = siguiente
            self.wait(0.42)
        self.wait(1.2)

        pts = fr.costa(nivel=self.NIVEL_T, H=0.75, semilla=self.SEMILLA_T,
                       largo=self.LARGO_T, amplitud=self.AMPL_T)
        recuento = fr.conteo_cajas(pts)
        et_nuevo = hud("dimension", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{recuento['D']:.4f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("el mismo programa", font_size=18, color=C_VIDA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, sub], [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(3.4)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, actual, etiqueta, numero,
                                         sub)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _vano(self):
        """Las dos marcas del ancho que la antena NO puede pasar."""
        media = self.VANO * self.ESCALA / 2
        g = VGroup()
        for x in (-media, media):
            g.add(Line(np.array([x, self.Y_ANTENA - 0.55, 0.0]),
                       np.array([x, self.Y_ANTENA + 1.15, 0.0]),
                       stroke_width=1.6, color=C_EJE))
        g.add(DashedLine(np.array([-media, self.Y_ANTENA - 0.42, 0.0]),
                         np.array([media, self.Y_ANTENA - 0.42, 0.0]),
                         stroke_width=1.6, color=C_EJE, dash_length=0.12))
        return g

    def _perfil(self, nivel):
        """La cordillera del nivel `nivel`: el mismo motor que la costa."""
        pts = fr.costa(nivel=nivel, H=0.75, semilla=self.SEMILLA_T,
                       largo=self.LARGO_T, amplitud=self.AMPL_T)
        base = fr.costa(nivel=self.NIVEL_T, H=0.75, semilla=self.SEMILLA_T,
                        largo=self.LARGO_T, amplitud=self.AMPL_T)
        y0, y1 = base[:, 1].min(), base[:, 1].max()
        k = 2.9 / (y1 - y0)
        suelo = self.Y_TERRENO - 1.55
        vertices = [np.array([x - self.LARGO_T / 2,
                              (y - y0) * k + suelo, 0.0])
                    for x, y in pts]
        vertices.append(np.array([self.LARGO_T / 2, suelo - 0.02, 0.0]))
        vertices.append(np.array([-self.LARGO_T / 2, suelo - 0.02, 0.0]))
        p = Polygon(*vertices, stroke_width=2.2, stroke_color=C_VIDA,
                    fill_color=C_VIDA, fill_opacity=0.16)
        p.set_z_index(10)
        return p
