class Clip2(Scene):
    """2 - La velocidad de la luz no negocia. Las cuatro ciudades separadas
    por su distancia REAL y tres arcos de mensaje desde CDMX: 34, 91 y 113 ms
    de ida y vuelta. Es el PISO fisico (2d/v en fibra), sin colas ni rutas:
    por eso la nube te pone una replica al lado. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La velocidad de la luz no negocia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # La linea va A ESCALA de distancia real: CDMX en x = -5.2, Nueva
        # York en -2.11, Madrid en 3.14 y Tokio en 5.2. Los cuatro nombres
        # caben debajo sin tocarse. Los tres arcos se cruzan sobre Nueva
        # York, asi que las cifras van escalonadas en altura (0.23 / 0.72 /
        # 1.12) y en el mismo orden que los arcos: la de mas arriba es la
        # del arco mas alto.
        ciudades = ("CDMX", "Nueva York", "Madrid", "Tokio")
        ll = linea_latencia().shift(DOWN * 0.6)
        nombres = VGroup(*[tag_junto(ll.ciudad(c), c, DOWN, buff=0.18,
                                     font_size=15) for c in ciudades])

        # --- momento: la fisica primero ------------------------------------
        vel = f"{V_FIBRA_KMS:,.0f}".replace(",", " ")
        rot.mostrar(pie_curso(f"En fibra, la luz viaja a {vel} km/s."),
                    zona="abajo", run_time=0.45)
        self.play(Create(ll.base), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(ll.ciudad(c), scale=0.6)
                                for c in ciudades], lag_ratio=0.25),
                  run_time=0.8)
        self.play(FadeIn(nombres, shift=0.10 * DOWN), run_time=0.6)
        self.wait(3.0)

        # --- momento: los tres arcos, uno a uno ----------------------------
        rot.mostrar(pie_curso("Ida y vuelta desde CDMX: lo que cuesta cada "
                              "salto."), zona="abajo")

        def arco_con_cifra(destino, dy, font_size=17):
            """El arco sobre geometria ACTUAL y su cifra sobre el pico."""
            a = ll.arco(destino)
            t = tag_hud(f"{ll.rtt(destino):.0f} ms", font_size=font_size)
            t.move_to(a.point_from_proportion(0.5) + UP * dy)
            return a, t

        a_ny, c_ny = arco_con_cifra("Nueva York", 0.62)
        a_ma, c_ma = arco_con_cifra("Madrid", 0.74)
        a_tk, c_tk = arco_con_cifra("Tokio", 1.00, font_size=19)
        self.play(Create(a_ny), run_time=0.9)
        self.play(FadeIn(c_ny, shift=0.12 * UP), run_time=0.4)
        self.wait(0.5)
        self.play(Create(a_ma), run_time=1.0)
        self.play(FadeIn(c_ma, shift=0.12 * UP), run_time=0.4)
        self.wait(0.4)
        self.play(Create(a_tk), run_time=1.1)
        self.play(FadeIn(c_tk, shift=0.12 * UP), run_time=0.45)
        self.wait(0.7)

        # --- momento: es el PISO, no la latencia real ----------------------
        rot.mostrar(formula_pie(r"t_{\min} = 2d / v"), zona="abajo")
        dist = f"{DIST_TOKIO:,.0f}".replace(",", " ")
        t_dist = tag_hud(f"CDMX–Tokio: {dist} km", font_size=16)
        t_dist.move_to(np.array([4.55, 0.35, 0.0]))
        nota = tag_junto(t_dist, "piso físico: sin colas ni rutas", DOWN,
                         buff=0.16, font_size=14)
        self.play(FadeIn(t_dist, shift=0.12 * UP), run_time=0.5)
        self.play(Indicate(c_tk, color=C_MENSAJE, scale_factor=1.18),
                  run_time=0.8)
        self.play(FadeIn(nota), run_time=0.45)
        self.wait(3.45)

        # --- momento: la consecuencia, una replica al lado -----------------
        rot.mostrar(pie_curso("Por eso la nube guarda una copia cerca de "
                              "ti."), zona="abajo")
        cdmx = ll.ciudad("CDMX")
        replica = Dot(cdmx.get_center() + DOWN * 1.15 + RIGHT * 0.35,
                      radius=0.085, color=C_OK)
        salto = ArcBetweenPoints(cdmx.get_center(), replica.get_center(),
                                 angle=0.9, stroke_width=2.6,
                                 color=C_MENSAJE)
        t_rep = tag_junto(replica, "réplica local", RIGHT, buff=0.18,
                          font_size=15, color=C_OK)
        self.play(FadeIn(replica, scale=0.6), Create(salto), run_time=0.7)
        self.play(FadeIn(t_rep, shift=0.10 * RIGHT), run_time=0.45)
        self.play(Flash(replica, color=C_OK, line_length=0.16, num_lines=10,
                        flash_radius=0.24), run_time=0.6)
        self.wait(3.3)

        # --- cierre: no es un lujo, es fisica ------------------------------
        rot.mostrar(pie_curso("Las réplicas cerca de ti no son un lujo: "
                              "son física."), zona="abajo")
        self.wait(5.0)
