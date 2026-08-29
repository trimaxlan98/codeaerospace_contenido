class Clip1(Scene):
    """1.3.1 - La mascara no es adorno: subirla de 5 a 10 grados recorta
    el contacto y borra del catalogo los pases bajos. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La mascara no es adorno"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # El el_max de cada traza es una ELECCION DE DIBUJO (como el
        # acimut de culminacion en el molde), no una cifra rotulada: la
        # duracion de cada pase la mide la libreria.
        EL_CENITAL = 89.0
        EL_BAJA = 8.0
        DUR_BAJA = duracion_pase(H_LEO, EL_BAJA, MASCARA) / 60.0

        def tramo(traza, el_min, n=601):
            """(t_entrada, t_salida) del trozo de traza por encima de
            `el_min`, leyendo la elevacion de la traza YA colocada."""
            ts = np.linspace(0.0, 1.0, n)
            dentro = [t for t in ts if traza.el_en(t) >= el_min]
            if not dentro:
                return None
            return float(dentro[0]), float(dentro[-1])

        def util_de(traza, el_min, color=C_OK, grosor=6.0):
            par = tramo(traza, el_min)
            if par is None:
                return None
            return Line(traza.punto_en(par[0]), traza.punto_en(par[1]),
                        color=color, stroke_width=grosor)

        # --- el cielo de la estacion, con su mascara ---------------------
        vista = vista_polar(radio=2.22, font_size=16)
        vista.move_to(LEFT * 3.35 + UP * 0.20)
        self.play(Create(vista), run_time=1.5)

        mask = mascara_elevacion(vista, el_min=MASCARA, color=C_EJE)
        self.play(FadeIn(mask), run_time=0.8)
        t_mask = tag_hud(f"mascara {fmt(MASCARA, 0)} deg", font_size=20,
                         color=C_TENUE)
        t_mask.next_to(vista, DOWN, buff=0.24)
        self.play(FadeIn(t_mask), run_time=0.4)
        self.wait(1.1)

        # --- el pase cenital y el trozo que de verdad sirve --------------
        traza = traza_pase(vista, el_max=EL_CENITAL, az_culminacion=140.0,
                           muestras=160, color=C_CIELO)
        self.play(Create(traza), run_time=1.6)
        util = util_de(traza, MASCARA)
        self.play(Create(util), run_time=0.9)

        d_aos = Dot(util.get_start(), radius=0.07, color=C_OK)
        d_los = Dot(util.get_end(), radius=0.07, color=C_OK)
        t_aos = tag_junto(d_aos, "AOS", direccion=DL, buff=0.12, color=C_OK)
        t_los = tag_junto(d_los, "LOS", direccion=UR, buff=0.12, color=C_OK)
        self.play(FadeIn(d_aos), FadeIn(t_aos), FadeIn(d_los), FadeIn(t_los),
                  run_time=0.7)
        self.wait(0.9)

        # --- la ventana de contacto, dibujada a escala ------------------
        L_BARRA = 3.55
        CENTRO_BARRA = RIGHT * 3.55 + DOWN * 0.30
        barra = Rectangle(width=L_BARRA, height=0.40, stroke_width=0,
                          fill_color=C_OK, fill_opacity=0.85)
        barra.move_to(CENTRO_BARRA)
        t_barra = tag_junto(barra, "ventana de contacto", direccion=UP,
                            buff=0.22)
        cont = tag_hud(f"{fmt(DUR_MASCARA_5, 1)} min", font_size=32)
        cont.next_to(barra, DOWN, buff=0.30)
        self.play(GrowFromEdge(barra, LEFT), FadeIn(t_barra), run_time=1.0)
        self.play(FadeIn(cont), run_time=0.5)
        rot.mostrar(cifra_pie(f"pase {fmt(DUR_MASCARA_5, 1)} min"),
                    zona="abajo")
        self.wait(1.9)

        # --- y un pase bajo, de los que apenas asoman --------------------
        baja = traza_pase(vista, el_max=EL_BAJA, az_culminacion=300.0,
                          muestras=140, color=C_CIELO)
        baja.set_stroke(opacity=0.55)
        util_baja = util_de(baja, MASCARA, grosor=5.0)
        t_baja = tag_hud(f"pase {fmt(DUR_BAJA, 1)} min", font_size=19,
                         color=C_TENUE)
        t_baja.move_to(LEFT * 4.95 + UP * 2.56)
        self.play(Create(baja), run_time=1.1)
        self.play(Create(util_baja), FadeIn(t_baja), run_time=0.7)
        self.wait(1.3)

        # --- se sube la mascara a 10 grados ------------------------------
        mask10 = mascara_elevacion(vista, el_min=MASCARA_ALTA, color=C_EJE)
        # El rotulo se releva con `become` DESPUES del morfeo de la
        # mascara: los kwargs de play() pisan los de cada animacion
        # (manim 0.20.1), asi que el run_time=0.02 no se respetaba y el
        # texto pasaba 1.2 s a medio morfar.
        self.play(Transform(mask, mask10), run_time=1.2)
        t_mask.become(tag_hud(f"mascara {fmt(MASCARA_ALTA, 0)} deg",
                              font_size=20,
                              color=C_TENUE).move_to(t_mask))
        self.wait(0.6)

        # el pase cenital se acorta por los dos extremos
        util10 = util_de(traza, MASCARA_ALTA)
        cortes = VGroup(
            Line(util.get_start(), util10.get_start(), color=C_PELIGRO,
                 stroke_width=6.0),
            Line(util10.get_end(), util.get_end(), color=C_PELIGRO,
                 stroke_width=6.0),
        )
        self.play(Transform(util, util10),
                  d_aos.animate.move_to(util10.get_start()),
                  d_los.animate.move_to(util10.get_end()),
                  FadeOut(t_aos), FadeOut(t_los), run_time=1.0)
        self.play(Create(cortes), run_time=0.6)
        self.wait(0.7)

        # y el pase bajo se cae entero del catalogo
        self.play(util_baja.animate.set_color(C_PELIGRO), run_time=0.5)
        self.play(FadeOut(util_baja), FadeOut(t_baja),
                  baja.animate.set_stroke(opacity=0.16), run_time=0.9)
        rot.mostrar(cifra_pie(f"pase {fmt(DUR_BAJA, 1)} min perdido"),
                    zona="abajo")
        self.wait(2.0)

        # --- la ventana, recortada ---------------------------------------
        L10 = L_BARRA * DUR_MASCARA_10 / DUR_MASCARA_5
        barra10 = Rectangle(width=L10, height=0.40, stroke_width=0,
                            fill_color=C_OK, fill_opacity=0.85)
        barra10.move_to(CENTRO_BARRA)
        perdidos = VGroup()
        for signo in (-1.0, 1.0):
            trozo = Rectangle(width=(L_BARRA - L10) / 2.0, height=0.40,
                              stroke_width=0, fill_color=C_PELIGRO,
                              fill_opacity=0.85)
            trozo.move_to(CENTRO_BARRA
                          + RIGHT * signo * (L_BARRA + L10) / 4.0)
            perdidos.add(trozo)
        self.play(Transform(barra, barra10), run_time=1.1)
        cont.become(tag_hud(f"{fmt(DUR_MASCARA_10, 1)} min",
                            font_size=32).move_to(cont))
        self.play(FadeIn(perdidos), run_time=0.6)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"recorte {fmt(RECORTE * 100.0, 1)} pct"),
                    zona="abajo")
        self.wait(2.2)

        panel = panel_cifras(f"mask {fmt(MASCARA, 0)}  "
                             f"{fmt(DUR_MASCARA_5, 1)} min",
                             (f"mask {fmt(MASCARA_ALTA, 0)}  "
                              f"{fmt(DUR_MASCARA_10, 1)} min", C_PELIGRO),
                             f"recorte {fmt(RECORTE * 100.0, 1)} pct")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
