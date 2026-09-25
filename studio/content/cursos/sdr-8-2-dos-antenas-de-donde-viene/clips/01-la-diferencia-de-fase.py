class Clip1(Scene):
    """8.2.1 - Frentes de onda planos llegando en angulo (25 grados, param)
    a dos antenas separadas d = lambda/2: la onda llega antes a una
    (distancia extra resaltada); luego las dos senales, una por antena,
    con la diferencia de fase MEDIDA = DPHI_05 = 76.1 grados. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La diferencia de fase"), zona="arriba",
                   run_time=0.6)
        self.wait(0.3)

        # --- las dos antenas, separadas d = lambda/2, y los frentes ---------
        # todo junto desde el primer play: nada de pantalla a medio llenar.
        D_VIS = 2.9
        Y0 = 0.55
        a_izq = np.array([-D_VIS / 2, Y0, 0.0])
        a_der = np.array([D_VIS / 2, Y0, 0.0])

        def antena(pos):
            palo = Line(pos, pos + UP * 0.42, color=C_TENUE,
                       stroke_width=2.6)
            base = Dot(pos, radius=0.075, color=C_TENUE)
            return VGroup(palo, base)

        an1, an2 = antena(a_izq), antena(a_der)
        base_linea = Line(a_izq, a_der, color=C_EJE, stroke_width=1.8)
        et_d = tag_junto(base_linea, "d", DOWN, buff=0.14, font_size=20)

        th = math.radians(THETA)
        p = np.array([math.sin(th), -math.cos(th), 0.0])   # propagacion
        w = np.array([math.cos(th), math.sin(th), 0.0])    # a lo largo
        centro = (a_izq + a_der) / 2.0
        frentes = VGroup(*[
            Line(centro + p * t - w * 3.4, centro + p * t + w * 3.4,
                color=C_SENAL, stroke_width=2.2)
            for t in (3.4, 2.2, 1.0)])
        flecha = Arrow(centro + p * 4.1, centro + p * 1.85, color=C_SENAL,
                      stroke_width=3.0, tip_length=0.2, buff=0.0)
        ang_txt = MathTex(f"{int(THETA)}^\\circ", font_size=30,
                          color=C_DATO)
        ang_txt.next_to(flecha.get_start(), LEFT, buff=0.18)

        geo = VGroup(base_linea, an1, an2, et_d, frentes, flecha, ang_txt)
        self.play(Create(base_linea), FadeIn(an1), FadeIn(an2), FadeIn(et_d),
                  LaggedStart(*[Create(f) for f in frentes], lag_ratio=0.2),
                  run_time=1.6)
        self.play(GrowArrow(flecha), FadeIn(ang_txt), run_time=0.7)
        self.wait(1.4)
        rot.mostrar(dato_pie(f"{fmt(THETA, 0)} grados"), zona="abajo",
                   run_time=0.5)
        self.wait(2.2)

        # --- la distancia extra: la onda llega antes a una ------------------
        extra = D_VIS * math.sin(th)
        pie = a_der - p * extra
        seg = DashedLine(a_der, pie, color=C_TITULO, stroke_width=2.6,
                         dash_length=0.09)
        et_extra = tag_junto(seg, "distancia extra", RIGHT, buff=0.16,
                             font_size=20)
        geo.add(seg, et_extra)
        self.play(Create(seg), FadeIn(et_extra), run_time=1.0)
        self.wait(3.0)
        self.play(FadeOut(geo), run_time=0.7)

        # --- las dos senales, una por antena, desfasadas ---------------------
        t = np.linspace(0.0, 2.0, 400)
        y1 = np.cos(2 * np.pi * t)
        y2 = np.cos(2 * np.pi * t - DPHI_05)
        t_pico2 = DPHI_05 / (2 * np.pi)

        esp1 = S.Espectro(t, y1, piso=-1.3, techo=1.3, ancho=10.4, alto=1.9,
                          color=C_SENAL, area=False)
        esp1.shift(UP * 1.35)          # nace en el origen: shift = destino
        esp2 = S.Espectro(t, y2, piso=-1.3, techo=1.3, ancho=10.4, alto=1.9,
                          color=C_SENAL, area=False)
        esp2.shift(DOWN * 1.25)
        # los rotulos van ENCIMA de cada traza, a la izquierda pero DENTRO
        # del margen (no colgando del panel hacia el borde del cuadro).
        et1 = tag_junto(esp1.curva, "antena 1", UP, buff=0.12, font_size=20)
        et1.align_to(esp1, RIGHT)
        et2 = tag_junto(esp2.curva, "antena 2", UP, buff=0.12, font_size=20)
        et2.align_to(esp2, RIGHT)
        self.play(Create(esp1.ejes), Create(esp1.curva), FadeIn(et1),
                  run_time=1.1)
        self.wait(1.0)
        self.play(Create(esp2.ejes), Create(esp2.curva), FadeIn(et2),
                  run_time=1.1)
        self.wait(2.0)

        # --- el desfase entre los dos picos, marcado ------------------------
        m1 = esp1.marca_f(0.0, color=C_CALCULO)
        m2 = esp2.marca_f(t_pico2, color=C_CALCULO)
        self.play(Create(m1), Create(m2), run_time=0.9)
        y_medio = (esp1.get_bottom()[1] + esp2.get_top()[1]) / 2.0
        pa = np.array([esp1.x_de(0.0), y_medio, 0.0])
        pb = np.array([esp2.x_de(t_pico2), y_medio, 0.0])
        brecha = DoubleArrow(pa, pb, color=C_CALCULO, stroke_width=2.6,
                             tip_length=0.14, buff=0.0)
        self.play(GrowFromCenter(brecha), run_time=0.6)
        self.wait(2.4)
        rot.mostrar(cifra_pie(f"{fmt(math.degrees(DPHI_05), 1)} grados"),
                   zona="abajo", run_time=0.5)
        self.wait(6.5)
