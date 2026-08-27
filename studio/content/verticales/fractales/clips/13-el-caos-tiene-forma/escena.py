class Clip(Scene):
    """13 · El caos tiene forma — el diagrama que se contiene a si mismo.

    La ecuacion mas simple que se puede escribir de un bicho que se
    reproduce, x -> r x (1-x), dibuja al variar r el diagrama de
    bifurcaciones: una rama, dos, cuatro, ocho... y despues caos. Dentro del
    caos hay una ventana de periodo 3, y ampliandola x160 aparece **el
    diagrama entero otra vez**.

    Cierra con el atractor de Lorenz —la trayectoria del aire caliente que
    da vueltas sin repetirse nunca— y con la dimension de su sombra,
    medida con `conteo_cajas` sobre la traza que se dibuja: 1.6861.

    El diagrama y la trayectoria salen de `caos.py`, la libreria del curso
    15; aqui solo se miden.
    """

    R_TODO = (2.8, 4.0)
    R_VENTANA = (3.8495, 3.8570)
    # La malla va mas alta que ancha de lo habitual para que, al fijar el
    # ANCHO de la banda, la altura llegue a 5.4 y no quede un hueco muerto
    # entre el diagrama y el pie de cifra.
    RES_BIF = (1000, 760)
    Y_BIF = 1.55
    ANCHO_BIF = 7.1
    GAMMA = 0.42          # el diagrama en negro sale muy apagado a 0.65
    COLOR_BIF = "#ffd48a"  # ambar claro: el ambar de marca se apaga aqui
    R_SONDA = (3.20, 3.50, 3.556)

    def construct(self):
        import caos

        hud_top = hud_pieza("13 . el caos")
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)

        r0_todo, r1_todo = self.R_TODO
        bif = caos.imagen_bifurcacion(r=self.R_TODO, res=self.RES_BIF,
                                      color=self.COLOR_BIF, gamma=self.GAMMA,
                                      alto_escena=5.0)
        bif.width = self.ANCHO_BIF
        bif.move_to(UP * self.Y_BIF)
        bif.set_z_index(5)
        marco = Rectangle(width=bif.width, height=bif.height,
                          stroke_width=1.4, stroke_color=C_EJE,
                          fill_opacity=0.0)
        marco.move_to(UP * self.Y_BIF)
        marco.set_z_index(20)

        etiqueta = hud("finales", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        sub = hud("de una ecuacion", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)
        numero = None

        self.play(FadeIn(bif), Create(marco), run_time=1.7)
        self.play(FadeIn(etiqueta), FadeIn(sub), run_time=0.5)
        self.wait(1.0)

        # --- cuantos finales tiene la ecuacion para cada r ------------
        # El periodo se CUENTA sobre la propia orbita (valores distintos en
        # la cola), no se da por sabido: es la cifra del primer tramo.
        aguja = None
        for r_val in self.R_SONDA:
            x_r = (-self.ANCHO_BIF / 2
                   + self.ANCHO_BIF * (r_val - r0_todo) / (r1_todo - r0_todo))
            nueva = Line(np.array([x_r, self.Y_BIF - bif.height / 2, 0.0]),
                         np.array([x_r, self.Y_BIF + bif.height / 2, 0.0]),
                         stroke_width=2.4, color=C_MEDIDO)
            nueva.set_z_index(25)
            num_nuevo = cifra(f"{self._periodo(r_val)}", font_size=104)
            num_nuevo.move_to(UP * Y_NUMERO)
            sub_nuevo = hud(f"con r = {r_val:.3f}".rstrip("0").rstrip("."),
                            font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            if aguja is None:
                self.play(Create(nueva), run_time=0.6)
            else:
                self.play(Transform(aguja, nueva), run_time=0.8)
                nueva = aguja
            cambiar(self, [numero, sub], [num_nuevo, sub_nuevo],
                    salida=0.24, entrada=0.32)
            aguja, numero, sub = nueva, num_nuevo, sub_nuevo
            self.wait(1.3)
        self.play(FadeOut(aguja), run_time=0.5)
        self.wait(0.8)

        # =============================================================
        # 1. La ventana de periodo 3, dentro del caos
        # =============================================================
        v0, v1 = self.R_VENTANA
        r0, r1 = r0_todo, r1_todo
        x0 = -self.ANCHO_BIF / 2 + self.ANCHO_BIF * (v0 - r0) / (r1 - r0)
        x1 = -self.ANCHO_BIF / 2 + self.ANCHO_BIF * (v1 - r0) / (r1 - r0)
        lupa = Rectangle(width=max(x1 - x0, 0.06), height=bif.height,
                         stroke_width=2.6, stroke_color=C_MEDIDO,
                         fill_opacity=0.0)
        lupa.move_to(np.array([(x0 + x1) / 2, self.Y_BIF, 0.0]))
        lupa.set_z_index(30)
        self.play(Create(lupa), run_time=0.9)
        self.wait(2.0)

        zoom = caos.imagen_bifurcacion(r=self.R_VENTANA, res=self.RES_BIF,
                                       color=self.COLOR_BIF, gamma=self.GAMMA,
                                       alto_escena=5.0)
        zoom.width = self.ANCHO_BIF
        zoom.move_to(UP * self.Y_BIF)
        zoom.set_z_index(5)
        aumento = (r1 - r0) / (v1 - v0)

        et_nuevo = hud("aumento", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{aumento:.0f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("y esta otra vez", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        self.play(FadeOut(lupa), FadeOut(bif), FadeIn(zoom), run_time=1.5)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.play(Flash(numero, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(4.0)

        # =============================================================
        # 2. Y el atractor: una trayectoria que nunca se repite
        # =============================================================
        pts = caos.trayectoria_lorenz(n=9000)
        xz = np.stack([pts[:, 0], pts[:, 2]], axis=1)
        recuento = fr.conteo_cajas(xz)
        traza = self._lorenz(xz)

        self.play(FadeOut(zoom), FadeOut(marco), run_time=0.7)
        self.play(Create(traza), run_time=4.6, rate_func=linear)

        et_nuevo = hud("dimension", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{recuento['D']:.4f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("de la traza", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(4.4)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, traza, etiqueta, numero,
                                         sub)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    @staticmethod
    def _periodo(r, burn=4000, cola=1024, tol=1e-4, tope=64):
        """Cuantos valores distintos visita la orbita: SU numero de finales.

        Se tira `burn` pasos para caer en el atractor y se cuentan los
        valores distintos (redondeados a `tol`) de la cola. Por encima de
        `tope` ya no es un ciclo: es caos.
        """
        x = 0.5
        for _ in range(int(burn)):
            x = r * x * (1.0 - x)
        vistos = set()
        for _ in range(int(cola)):
            x = r * x * (1.0 - x)
            vistos.add(round(x / tol))
            if len(vistos) > tope:
                return tope
        return len(vistos)

    def _lorenz(self, xz, alto=5.4, y=1.30, cada=3):
        """La sombra del atractor en el plano xz.

        Se toma uno de cada `cada` puntos: 9 000 vertices en un solo
        VMobject hacen que `Create` vaya a rastras y no se gana nada — a
        esta escala la curva se ve igual.
        """
        q = np.asarray(xz)[::cada]
        x0, x1 = q[:, 0].min(), q[:, 0].max()
        y0, y1 = q[:, 1].min(), q[:, 1].max()
        k = alto / (y1 - y0)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0
        v = VMobject(stroke_color=C_MEDIDO, stroke_width=1.5)
        v.set_points_as_corners([np.array([(px - cx) * k,
                                           (py - cy) * k + y, 0.0])
                                 for px, py in q])
        v.set_stroke(opacity=0.85)
        v.set_z_index(10)
        return v
