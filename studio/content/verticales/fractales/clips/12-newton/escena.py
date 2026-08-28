class Clip(Scene):
    """12 · Newton — tres raices y una frontera imposible.

    El metodo de Newton para z^3 = 1: desde cualquier punto de partida se
    va cayendo hacia una de las tres raices. La pregunta del clip es cual, y
    la respuesta pinta el plano de tres colores.

    Dos puntos separados por dos centesimas (0.3847+1.0291i y el mismo
    corrido 0.02 a la derecha) caen en raices DISTINTAS. Y al
    ampliar la frontera se ve por que: no hay una linea que separe dos
    cuencas, porque en cualquier punto del borde se tocan LAS TRES (la
    propiedad de Wada). Ampliando x67 el dibujo es el mismo.

    Cifras medidas por `newton_reparto` sobre la malla dibujada: 6.73 pasos
    de media hasta una raiz, y el reparto 34.47 / 32.77 / 32.77.
    """

    ANCHO0 = 3.0
    ZOOMS = (0.35, 0.045)
    RES = (560, 700)
    ALTO = 6.0
    Y_IMG = 1.40
    # Elegidos midiendo, no a ojo: el par mas "manso" (radio maximo 1.24,
    # dentro del encuadre) entre los que, separados 0.02, caen en raices
    # distintas. Con otros pares la trayectoria de Newton pega un salto
    # enorme y cruza la pantalla entera: se lee como ruido.
    Z0_A = complex(0.3847, 1.0291)
    SEPARACION = 0.02

    def construct(self):
        k = self.ALTO / (self.ANCHO0 * self.RES[1] / self.RES[0])
        centro = np.array([0.0, self.Y_IMG, 0.0])

        def punto(z):
            x, y = (z.real, z.imag) if isinstance(z, complex) else (z[0], z[1])
            return centro + np.array([x * k, y * k, 0.0])

        hud_top = hud_pieza("12 . newton")
        raices = VGroup(*[
            Dot(punto(r), radius=0.09, color=c)
            for r, c in zip(fr.RAICES_CUBICAS, fr.COLORES_NEWTON)])
        raices.set_z_index(40)
        aro = Circle(radius=k, stroke_width=1.4, color=C_EJE)
        aro.move_to(centro)

        etiqueta = hud("tres raices", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        sub = hud("de z cubo = 1", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)
        numero = None

        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)
        self.play(Create(aro), FadeIn(raices, lag_ratio=0.3),
                  FadeIn(etiqueta), FadeIn(sub), run_time=1.3)
        self.wait(0.7)

        # =============================================================
        # 1. Dos partidas casi iguales, dos destinos distintos
        # =============================================================
        caminos = []
        for z0 in (self.Z0_A, self.Z0_A + self.SEPARACION):
            orb = fr.newton_orbita(z0, n=14)
            destino = complex(orb[-1][0], orb[-1][1])
            cual = min(range(3),
                       key=lambda i: abs(destino - complex(
                           fr.RAICES_CUBICAS[i])))
            col_destino = fr.COLORES_NEWTON[cual]
            v = VMobject(stroke_color=col_destino, stroke_width=2.6)
            v.set_points_as_corners([punto(p) for p in orb])
            v.set_z_index(25)
            d = Dot(punto(z0), radius=0.075, color=C_TINTA)
            d.set_z_index(35)
            caminos.append((v, d, col_destino, len(orb) - 1))

        for i, (v, d, col, pasos) in enumerate(caminos):
            self.play(FadeIn(d, scale=2.2), run_time=0.4)
            self.play(Create(v), run_time=1.6, rate_func=linear)
            num_nuevo = cifra(f"{pasos}", font_size=104, color=col)
            num_nuevo.move_to(UP * Y_NUMERO)
            et_nuevo = hud("pasos", font_size=20, color=CODE_MUTED)
            et_nuevo.move_to(UP * Y_ETIQUETA)
            sub_nuevo = hud("hasta una raiz", font_size=18, color=col)
            sub_nuevo.move_to(UP * Y_SUB)
            if i == 1:
                # El segundo golpe no es "cuantos pasos" sino LO POCO que se
                # movio la partida: dos centesimas y otra raiz.
                et_nuevo = hud("de separacion", font_size=20,
                               color=CODE_MUTED)
                et_nuevo.move_to(UP * Y_ETIQUETA)
                num_nuevo = cifra(f"{self.SEPARACION:.3f}", font_size=104,
                                  color=col)
                num_nuevo.move_to(UP * Y_NUMERO)
                sub_nuevo = hud("y otra raiz", font_size=18, color=col)
                sub_nuevo.move_to(UP * Y_SUB)
            cambiar(self, [etiqueta, numero, sub],
                    [et_nuevo, num_nuevo, sub_nuevo])
            etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
            self.wait(1.6 if i == 0 else 2.2)

        # =============================================================
        # 2. Todos los puntos de partida a la vez
        # =============================================================
        img = self._newton(self.ANCHO0)
        marco = Rectangle(width=img.width, height=img.height,
                          stroke_width=1.4, stroke_color=C_EJE,
                          fill_opacity=0.0)
        marco.move_to(UP * self.Y_IMG)
        marco.set_z_index(45)
        reparto = fr.newton_reparto(res=(420, 420), ancho=self.ANCHO0)

        self.play(FadeOut(VGroup(*[c[0] for c in caminos])),
                  FadeOut(VGroup(*[c[1] for c in caminos])),
                  FadeOut(aro), FadeOut(raices), run_time=0.6)
        self.play(FadeIn(img), Create(marco), run_time=1.6)

        et_nuevo = hud("pasos medios", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{reparto['pasos_medios']:.2f}", font_size=104)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("hasta una raiz", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
        self.wait(2.6)

        # =============================================================
        # 3. La frontera, ampliada dos veces: siempre las tres
        # =============================================================
        actual = img
        for ancho in self.ZOOMS:
            nueva = self._newton(ancho)
            aumento = self.ANCHO0 / ancho
            et_nuevo = hud("aumento", font_size=20, color=CODE_MUTED)
            et_nuevo.move_to(UP * Y_ETIQUETA)
            num_nuevo = cifra(f"{aumento:.0f}", font_size=104)
            num_nuevo.move_to(UP * Y_NUMERO)
            sub_nuevo = hud("y siguen las tres", font_size=18, color=C_REGLA)
            sub_nuevo.move_to(UP * Y_SUB)
            self.play(FadeOut(actual), FadeIn(nueva), run_time=1.2)
            actual = nueva
            cambiar(self, [etiqueta, numero, sub],
                    [et_nuevo, num_nuevo, sub_nuevo])
            etiqueta, numero, sub = et_nuevo, num_nuevo, sub_nuevo
            self.wait(2.4)

        sub_nuevo = hud("ninguna separa dos", font_size=17, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, sub, sub_nuevo, salida=0.26, entrada=0.32)
        sub = sub_nuevo
        self.wait(3.0)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, actual, marco, etiqueta,
                                         numero, sub)], run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    def _newton(self, ancho):
        img = fr.imagen_newton(res=self.RES, centro=0j, ancho=ancho,
                               max_iter=60, alto_escena=self.ALTO)
        img.move_to(UP * self.Y_IMG)
        img.set_z_index(5)
        return img
