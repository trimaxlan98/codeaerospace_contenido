class Clip(Scene):
    """04 · El juego del caos — del azar puro sale una figura exacta.

    Tres esquinas y un dado. Se tira, se salta a la mitad de camino hacia la
    esquina que salio, y se marca. Nada mas. Los catorce primeros saltos se
    ven uno a uno; despues el mismo camino sigue solo hasta 200 000 puntos y
    lo que aparece es el triangulo de Sierpinski.

    Los puntos de la nube son LOS MISMOS que los de los saltos visibles:
    `ifs_camino` es secuencial y determinista, asi que la nube es la
    continuacion literal de lo que se acaba de ver. La dimension del final
    (1.5920) la mide `conteo_cajas` sobre esa nube, y la exacta por
    autosemejanza es log3/log2 = 1.5850.
    """

    SEMILLA = 4
    VISIBLES = 14
    TOTAL = 200_000
    RELEVOS = (60, 400, 3_000, 25_000, 200_000)
    ALTO = 5.1

    def construct(self):
        caja = fr.caja_ifs("sierpinski", semilla=self.SEMILLA, orden="camino")
        x0, x1, y0, y1 = caja
        escala = self.ALTO / (y1 - y0)
        cx, cy = (x0 + x1) / 2.0, (y0 + y1) / 2.0

        def punto(p):
            return np.array([(p[0] - cx) * escala,
                             (p[1] - cy) * escala + Y_ESCENA, 0.0])

        # Los puntos fijos de los tres mapas: las esquinas del juego.
        esquinas = [np.array([0.0, 0.0]), np.array([2.0, 0.0]),
                    np.array([1.0, math.sqrt(3.0)])]
        centro = sum(esquinas) / 3.0
        camino, eleccion = fr.ifs_camino("sierpinski", self.TOTAL,
                                         semilla=self.SEMILLA,
                                         z0=tuple(centro), quema=0)

        hud_top = hud_pieza("04 . el juego")
        vertices = VGroup(*[Dot(punto(e), radius=0.085, color=C_REGLA)
                            for e in esquinas])
        vertices.set_z_index(40)
        marco = Polygon(*[punto(e) for e in esquinas], stroke_width=1.6,
                        stroke_color=C_EJE, fill_opacity=0.0)

        etiqueta = hud("puntos", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        sub = hud("un dado de 3 caras", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)
        numero = cifra("0", font_size=96)
        numero.move_to(UP * Y_NUMERO)

        # =============================================================
        # 1. Tres esquinas, un punto
        # =============================================================
        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)
        self.play(Create(marco), FadeIn(vertices, lag_ratio=0.25),
                  run_time=1.1)
        viajero = Dot(punto(centro), radius=0.09, color=C_TINTA)
        viajero.set_z_index(50)
        self.play(FadeIn(viajero, scale=2.0), FadeIn(etiqueta),
                  FadeIn(numero), FadeIn(sub), run_time=0.7)
        self.wait(0.4)

        # =============================================================
        # 2. Catorce saltos, uno a uno
        # =============================================================
        marcas = VGroup()
        marcas.set_z_index(20)
        self.add(marcas)
        anterior = centro
        for k in range(self.VISIBLES):
            destino = camino[k]
            esquina = esquinas[eleccion[k]]
            traza = DashedLine(punto(anterior), punto(esquina),
                               stroke_width=1.6, color=C_REGLA,
                               dash_length=0.10, stroke_opacity=0.55)
            marca = Dot(punto(destino), radius=0.055, color=C_MEDIDO)
            num_nuevo = cifra(f"{k + 1}", font_size=96)
            num_nuevo.move_to(UP * Y_NUMERO)
            dur = 0.62 if k < 6 else 0.40
            self.play(
                Flash(vertices[eleccion[k]], color=C_REGLA, line_length=0.16,
                      num_lines=10, flash_radius=0.28, run_time=dur * 0.6),
                Create(traza, run_time=dur * 0.6))
            # El contador salta de golpe (no cruzado): son numeros de una
            # cifra en el mismo sitio y a esa velocidad un cruce emborrona.
            self.remove(numero)
            self.add(num_nuevo)
            self.play(viajero.animate.move_to(punto(destino)),
                      FadeOut(traza), FadeIn(marca), run_time=dur)
            marcas.add(marca)
            numero = num_nuevo
            anterior = destino
        self.wait(0.6)

        # =============================================================
        # 3. El mismo camino, cien mil saltos mas
        # =============================================================
        nube = None
        for total in self.RELEVOS:
            img = fr.imagen_nube(camino[:total], caja, res=(760, 700),
                                 color=C_MEDIDO, alto_escena=self.ALTO)
            img.move_to(UP * Y_ESCENA)
            img.set_z_index(15)
            num_nuevo = cifra(f"{total}", font_size=96)
            num_nuevo.move_to(UP * Y_NUMERO)
            anims = [FadeOut(numero, scale=0.92)]
            if nube is None:
                # Cada marca entro en escena por su cuenta (un FadeIn por
                # salto), asi que ademas de estar en el VGroup es un mobject
                # suelto: un FadeOut del grupo las quita del grupo y las deja
                # dibujadas encima de la nube. Hay que apagarlas UNA A UNA.
                anims += [FadeIn(img), FadeOut(viajero)]
                anims += [FadeOut(m) for m in marcas]
            else:
                anims += [FadeIn(img), FadeOut(nube)]
            self.play(*anims, run_time=0.9)
            if nube is None:
                self.remove(marcas, viajero, *marcas)
            self.play(FadeIn(num_nuevo, scale=1.06), run_time=0.35)
            nube, numero = img, num_nuevo
            self.wait(0.6)

        self.play(FadeOut(vertices), FadeOut(marco), run_time=0.6)
        self.wait(1.2)

        # =============================================================
        # 4. Y la figura tiene dimension: 1.5920 medida
        # =============================================================
        recuento = fr.conteo_cajas(camino, densificar_a=1e9)
        et_nuevo = hud("dimension", font_size=20, color=CODE_MUTED)
        et_nuevo.move_to(UP * Y_ETIQUETA)
        num_nuevo = cifra(f"{recuento['D']:.4f}", font_size=96)
        num_nuevo.move_to(UP * Y_NUMERO)
        sub_nuevo = hud("exacta log3/log2", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        cambiar(self, [etiqueta, numero, sub],
                [et_nuevo, num_nuevo, sub_nuevo])
        self.play(Flash(num_nuevo, color=C_MEDIDO, line_length=0.24,
                        num_lines=14, flash_radius=1.0), run_time=0.9)
        self.wait(2.6)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in (hud_top, nube, et_nuevo, num_nuevo,
                                         sub_nuevo)], run_time=1.1)
        self.wait(0.5)
