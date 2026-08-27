class Clip(Scene):
    """08 · Julia — prisioneros y fugitivos.

    Se fija un c y se pregunta lo mismo para CADA punto de partida: ¿su
    orbita se queda o se va? Los que se quedan (en violeta, el color de "lo
    atrapado" en todo el curso) son el conjunto de Julia lleno. Con
    c = -0.123 + 0.745i queda el conejo de Douady: 17 302 puntos presos de
    los 90 000 de la malla. Con c = 0.285 + 0.01i, apenas un paso mas alla,
    **no queda ni uno**.

    Las dos cuentas las hace `prisioneros` sobre la malla que se dibuja
    (300x300, 300 pasos antes de dar un punto por preso), y el paso de un c
    al otro es un morph de verdad: 34 fotogramas de Julia calculados uno a
    uno, no un fundido entre dos imagenes.
    """

    C_CONEXO = complex(-0.123, 0.745)
    C_POLVO = complex(0.285, 0.01)
    RES = (560, 760)
    ANCHO = 2.6
    ALTO = 6.5

    def construct(self):
        hud_top = hud_pieza("08 . julia")
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        pris_conexo = fr.prisioneros(self.C_CONEXO, res=(300, 300),
                                     ancho=self.ANCHO, max_iter=300)
        pris_polvo = fr.prisioneros(self.C_POLVO, res=(300, 300),
                                    ancho=self.ANCHO, max_iter=300)
        de_cuantos = f"de {pris_conexo['total']:,}".replace(",", " ")

        # =============================================================
        # 1. Un c fijo, y dos puntos de partida
        # =============================================================
        unidad = 1.30
        centro = np.array([0.0, 1.55, 0.0])

        def punto(z):
            return centro + np.array([z.real * unidad, z.imag * unidad, 0.0])

        ejes = VGroup(
            Line(centro + LEFT * 2.85, centro + RIGHT * 2.85,
                 stroke_width=1.4, color=C_EJE),
            Line(centro + DOWN * 2.65, centro + UP * 2.65,
                 stroke_width=1.4, color=C_EJE))
        marca_c = VGroup(Dot(punto(self.C_CONEXO), radius=0.075,
                             color=C_REGLA),
                         hud("c", font_size=17, color=C_REGLA)
                         .next_to(punto(self.C_CONEXO), UR, buff=0.10))
        marca_c.set_z_index(40)

        etiqueta = hud("el mismo c", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        sub = hud("dos partidas", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)
        numero = None

        self.play(Create(ejes), run_time=0.6)
        self.play(FadeIn(marca_c, scale=1.8), FadeIn(etiqueta), FadeIn(sub),
                  run_time=0.8)

        semillas = ((complex(-0.20, 0.42), C_ATRAPADO, 26),
                    (complex(0.55, -0.30), C_ESCAPA, 8))
        trazas = []
        for z0, color, pasos in semillas:
            orb = fr.traza_orbita(self.C_CONEXO, z0=z0, n=pasos)
            pts = self._recortada(orb)
            v = VMobject(stroke_color=color, stroke_width=2.4)
            v.set_points_as_corners([punto(complex(x, y)) for x, y in pts])
            v.set_z_index(20)
            d = Dot(punto(z0), radius=0.075, color=color)
            d.set_z_index(30)
            trazas.append(v)
            self.play(FadeIn(d, scale=2.0), run_time=0.35)
            self.play(Create(v), run_time=1.9, rate_func=linear)
            self.play(FadeOut(d), run_time=0.25)
            self.wait(0.7)

        # =============================================================
        # 2. Todos los puntos a la vez: el conjunto de Julia
        # =============================================================
        julia = fr.imagen_julia(self.C_CONEXO, res=self.RES,
                                ancho=self.ANCHO, max_iter=260,
                                paleta="fuego", ciclo=22.0,
                                interior=C_ATRAPADO, alto_escena=self.ALTO)
        julia.move_to(UP * Y_ESCENA)
        julia.set_z_index(5)
        # La imagen es una VENTANA al plano, no una mancha: un marco fino la
        # declara como tal y evita que el borde duro del rectangulo parezca
        # un defecto del render.
        ventana = Rectangle(width=julia.width, height=julia.height,
                            stroke_width=1.6, stroke_color=C_EJE,
                            fill_opacity=0.0)
        ventana.move_to(UP * Y_ESCENA)
        ventana.set_z_index(8)
        self.play(FadeOut(VGroup(*trazas)), FadeOut(ejes), FadeOut(marca_c),
                  run_time=0.6)
        self.play(FadeIn(julia), Create(ventana), run_time=1.8)

        et_nuevo = hud("atrapados", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{pris_conexo['atrapados']}", font_size=104,
                          color=C_ATRAPADO)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud(de_cuantos, font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, sub], [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(3.9)

        # =============================================================
        # 3. Se mueve c un paso y el conjunto estalla
        # =============================================================
        # Durante el morph no hay cifra que valga (la vieja ya no vale y la
        # nueva todavia no): se van tambien la etiqueta y el numero, y solo
        # queda dicho lo que esta pasando.
        sub_mov = hud("y ahora movemos c", font_size=18, color=C_REGLA)
        sub_mov.move_to(UP * Y_SUB)
        cambiar(self, [numero, sub, etiqueta], sub_mov,
                salida=0.28, entrada=0.32)
        sub, numero, etiqueta = sub_mov, None, None

        c0, c1 = self.C_CONEXO, self.C_POLVO
        fr.morph_julia(self, lambda a: c0 + a * (c1 - c0), duracion=5.4,
                       frames=40, res=(380, 520), ancho=self.ANCHO,
                       max_iter=220, paleta="fuego", ciclo=22.0,
                       interior=C_ATRAPADO, alto_escena=self.ALTO,
                       imagen=julia)
        self.wait(1.0)

        # el destino, ya a resolucion buena
        polvo = fr.imagen_julia(self.C_POLVO, res=self.RES, ancho=self.ANCHO,
                                max_iter=260, paleta="fuego", ciclo=22.0,
                                interior=C_ATRAPADO, alto_escena=self.ALTO)
        polvo.move_to(UP * Y_ESCENA)
        polvo.set_z_index(5)
        self.add(polvo)
        self.remove(julia)

        et_nuevo = hud("atrapados", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{pris_polvo['atrapados']}", font_size=104,
                          color=C_ESCAPA)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud(de_cuantos, font_size=18, color=C_ESCAPA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, sub, [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.play(Flash(numero, color=C_ESCAPA, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(4.4)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, polvo, ventana, etiqueta,
                                         numero, sub)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    RADIO_VISIBLE = 1.85

    def _recortada(self, orb):
        """La orbita cortada donde se sale del encuadre (ver clip 07)."""
        pts = [orb[0]]
        for p in orb[1:]:
            r = math.hypot(*p)
            if r <= self.RADIO_VISIBLE:
                pts.append(p)
                continue
            u = np.asarray(p, dtype=float) / r
            pts.append(u * (self.RADIO_VISIBLE + 0.25))
            break
        return pts
