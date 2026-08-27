class Clip(Scene):
    """07 · Girar y estirar — la unica operacion del resto del curso.

    Elevar un numero complejo al cuadrado hace dos cosas a la vez: DOBLA su
    angulo y ELEVA AL CUADRADO su distancia al origen. Con eso, el circulo
    de radio 1 se vuelve una frontera: por dentro todo se hunde hacia el
    cero, por fuera todo se dispara, y justo encima todo se queda dando
    vueltas para siempre.

    Las cifras son los modulos MEDIDOS tras seis pasos (z -> z^64) sobre las
    orbitas que se ven en pantalla, calculadas con `traza_orbita`. Al final
    entra la regla que gobierna los cuatro clips siguientes: z -> z^2 + c.
    """

    R_DENTRO = 0.92
    R_FUERA = 1.08
    ANGULO_DEG = 37.0
    PASOS = 6
    # El encuadre se calcula, no se elige a ojo: la orbita que se fuga
    # tiene que salir del cuadro SIN cruzar el pie de cifra. Con el plano
    # centrado en Y_PLANO y radio maximo RADIO_VISIBLE + 0.25, el punto mas
    # bajo que puede tocar la traza es Y_PLANO - 2.10*UNIDAD = -1.18, muy
    # por encima del renglon de la etiqueta (-2.55).
    UNIDAD = 1.30          # unidades de escena por unidad del plano
    Y_PLANO = 1.55

    def construct(self):
        centro = np.array([0.0, self.Y_PLANO, 0.0])

        def punto(z):
            return centro + np.array([z.real * self.UNIDAD,
                                      z.imag * self.UNIDAD, 0.0])

        hud_top = hud_pieza("07 . z al cuadrado")
        ejes = VGroup(
            Line(centro + LEFT * 2.85, centro + RIGHT * 2.85,
                 stroke_width=1.4, color=C_EJE),
            Line(centro + DOWN * 2.65, centro + UP * 2.65,
                 stroke_width=1.4, color=C_EJE))
        circulo = Circle(radius=self.UNIDAD, stroke_width=2.6,
                         color=C_MEDIDO, stroke_opacity=0.85)
        circulo.move_to(centro)

        self.play(FadeIn(hud_top, shift=DOWN * 0.15), run_time=0.7)
        self.play(Create(ejes), run_time=0.7)
        self.play(Create(circulo), run_time=1.1)

        # =============================================================
        # 1. Un paso: el angulo se dobla, el radio se eleva al cuadrado
        # =============================================================
        z = complex(1.28 * math.cos(0.62), 1.28 * math.sin(0.62))
        etiqueta = hud("modulo", font_size=20, color=CODE_MUTED)
        etiqueta.move_to(UP * Y_ETIQUETA)
        numero = cifra(f"{abs(z):.3f}", font_size=104)
        numero.move_to(UP * Y_NUMERO)
        sub = hud("de partida", font_size=18, color=C_REGLA)
        sub.move_to(UP * Y_SUB)

        radio = Line(centro, punto(z), stroke_width=2.4, color=C_REGLA)
        dot = Dot(punto(z), radius=0.085, color=C_REGLA)
        arco = self._arco(centro, z)
        self.play(Create(radio), FadeIn(dot), Create(arco),
                  FadeIn(etiqueta), FadeIn(numero), FadeIn(sub), run_time=1.0)
        self.wait(0.7)

        for paso in (1, 2):
            z_sig = z * z
            self.play(Transform(radio, Line(centro, punto(z_sig),
                                            stroke_width=2.4, color=C_REGLA)),
                      Transform(arco, self._arco(centro, z_sig)),
                      dot.animate.move_to(punto(z_sig)), run_time=1.2,
                      rate_func=rate_functions.ease_in_out_sine)
            num_sig = cifra(f"{abs(z_sig):.3f}", font_size=104)
            num_sig.move_to(UP * Y_NUMERO)
            sub_sig = hud(f"tras {paso} paso" + ("" if paso == 1 else "s"),
                          font_size=18, color=C_REGLA)
            sub_sig.move_to(UP * Y_SUB)
            # cambio instantaneo: el numero acompaña al movimiento, no lo
            # comenta despues (y a este ritmo un cruce emborrona).
            self.remove(numero, sub)
            self.add(num_sig, sub_sig)
            numero, sub = num_sig, sub_sig
            self.wait(0.6)
            z = z_sig

        self.play(FadeOut(radio), FadeOut(arco), FadeOut(dot), run_time=0.5)

        # =============================================================
        # 2. Tres semillas y el circulo que decide
        # =============================================================
        ang = math.radians(self.ANGULO_DEG)
        semillas = ((self.R_FUERA, C_ESCAPA, "por fuera"),
                    (self.R_DENTRO, C_ATRAPADO, "por dentro"),
                    (1.0, C_MEDIDO, "en el circulo"))

        sub_nuevo = hud("tres semillas", font_size=18, color=C_REGLA)
        sub_nuevo.move_to(UP * Y_SUB)
        self.play(FadeOut(numero, scale=0.92), FadeOut(sub), run_time=0.3)
        self.play(FadeIn(sub_nuevo, scale=1.04), run_time=0.36)
        sub, numero = sub_nuevo, None

        # Una semilla cada vez: las tres a la vez se cruzan y no se lee
        # ninguna. El orden es el del golpe: primero la que se dispara.
        trazas = []
        for r, color, texto in semillas:
            z0 = complex(r * math.cos(ang), r * math.sin(ang))
            orb = fr.traza_orbita(0j, z0=z0, n=self.PASOS)
            modulo = math.hypot(*orb[-1])
            traza = VMobject(stroke_color=color, stroke_width=2.8)
            traza.set_points_as_corners(
                [punto(complex(x, y)) for x, y in self._recortada(orb)])
            traza.set_z_index(20)
            trazas.append(traza)
            semilla = Dot(punto(z0), radius=0.085, color=color)
            semilla.set_z_index(30)

            self.play(FadeIn(semilla, scale=2.2), run_time=0.45)
            self.play(Create(traza), run_time=1.7, rate_func=linear)
            self.play(FadeOut(semilla), run_time=0.3)

            texto_num = (f"{modulo:.3f}" if modulo < 100
                         else f"{modulo:.1f}")
            num_nuevo = cifra(texto_num, font_size=104, color=color)
            num_nuevo.move_to(UP * Y_NUMERO)
            sub_nuevo = hud(texto, font_size=18, color=color)
            sub_nuevo.move_to(UP * Y_SUB)
            et_nuevo = hud("modulo tras 6", font_size=20, color=CODE_MUTED)
            et_nuevo.move_to(UP * Y_ETIQUETA)
            cambiar(self, [numero, sub, etiqueta],
                    [num_nuevo, sub_nuevo, et_nuevo],
                    salida=0.26, entrada=0.34)
            numero, sub, etiqueta = num_nuevo, sub_nuevo, et_nuevo
            self.wait(1.6)

        # =============================================================
        # 3. La regla que gobierna el resto del curso
        # =============================================================
        formula = MathTex(r"z \;\to\; z^{2} + c", font_size=78,
                          color=C_TINTA)
        formula.move_to(UP * (self.Y_PLANO + 0.1))
        formula.set_z_index(60)
        self.play(FadeOut(VGroup(*trazas)), FadeOut(circulo), FadeOut(ejes),
                  FadeOut(etiqueta), FadeOut(numero), FadeOut(sub),
                  run_time=0.8)
        self.play(Write(formula), run_time=1.8)
        self.wait(3.0)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(FadeOut(formula), FadeOut(hud_top), run_time=1.1)
        self.wait(0.5)

    # -----------------------------------------------------------------
    RADIO_VISIBLE = 1.85

    def _recortada(self, orb):
        """La orbita, cortada donde se sale del encuadre.

        Sin esto, la semilla de fuera llega a modulo 137 y su poligonal
        cruza la pantalla entera de esquina a esquina: se lee como ruido,
        no como una fuga. Se conserva el ultimo punto de dentro y se añade
        UNO fuera del borde, en la misma direccion: la linea sale del
        cuadro y no vuelve, que es exactamente lo que hace la orbita.
        """
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

    def _arco(self, centro, z, radio=0.50):
        """El angulo de z, dibujado desde el eje real. Es la mitad visible
        de la operacion: al elevar al cuadrado, este arco se DUPLICA."""
        ang = math.atan2(z.imag, z.real) % (2 * PI)
        return Arc(radius=radio, start_angle=0.0, angle=ang,
                   stroke_width=2.4, color=C_REGLA, arc_center=centro)
