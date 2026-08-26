class Clip4(Scene):
    """6.1.4 - Una pagina de 40 objetos, tres formas de pedirla: serie,
    keepalive y paralelo, con el tiempo total MEDIDO. Cierre de la
    leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Una fila para 40 objetos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: una pagina no es un archivo -------------------------------
        rot.mostrar(pie_curso("Una pagina no es un archivo: son decenas "
                              "de imagenes, hojas de estilo y scripts."),
                    zona="abajo", run_time=0.5)
        grid = VGroup(*[
            Square(0.34, stroke_color=C_PAQUETE, stroke_width=1.6,
                  fill_color=C_PAQUETE, fill_opacity=0.18)
            for _ in range(N_OBJETOS)])
        grid.arrange_in_grid(rows=4, cols=10, buff=0.10)
        grid.move_to(UP * 0.75)
        et_grid = tag_hud("%d objetos en una sola pagina" % N_OBJETOS,
                         font_size=19)
        et_grid.next_to(grid, DOWN, buff=0.35)
        self.play(LaggedStart(*[FadeIn(c, scale=1.3) for c in grid],
                              lag_ratio=0.03), run_time=1.2)
        self.play(FadeIn(et_grid), run_time=0.4)
        self.wait(2.8)

        # --- momento: serie (HTTP/1.0) -------------------------------------------
        rot.mostrar(pie_curso("HTTP/1.0 abria una conexion nueva -- con "
                              "su apreton completo -- para CADA objeto."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(grid), FadeOut(et_grid), run_time=0.5)
        et_apreton = tag_hud("apreton por conexion: 1 RTT TCP + %s RTT "
                            "TLS = %s RTT" % (fmt(APRETON["rtt"], 0),
                                              fmt(HT_SERIE["apreton_rtts"],
                                                  0)),
                            font_size=18, color=C_CIFRA)
        et_apreton.to_edge(UP, buff=1.15)
        g = grafica(F_SERIE, (1, N_OBJETOS), (0, 4800.0), ancho=8.6,
                   alto=3.6, color=C_PERDIDA, muestras=161,
                   etiqueta_x="objetos pedidos", etiqueta_y="ms acumulados")
        g.move_to(DOWN * 0.55)
        self.play(FadeIn(et_apreton), run_time=0.5)
        self.play(FadeIn(g.ejes), run_time=0.5)
        self.play(Create(g.curva), run_time=1.8)
        et_serie = tag_hud("serie: %d ms" % int(HT_SERIE["ms"]),
                          font_size=19, color=C_PERDIDA)
        et_serie.move_to(g.punto_de(N_OBJETOS) + UP * 0.30 + LEFT * 0.55)
        self.play(FadeIn(et_serie), run_time=0.4)
        self.wait(3.2)

        # --- momento: keepalive (HTTP/1.1, una conexion) --------------------------
        rot.mostrar(pie_curso("HTTP/1.1 reutiliza una sola conexion, "
                              "pero los 40 objetos siguen en fila india."),
                    zona="abajo", run_time=0.5)
        curva_keep = VMobject(color=C_COLA, stroke_width=3.0)
        curva_keep.set_points_as_corners(
            [g._en(x, min(F_KEEPALIVE(x), 4800.0))
             for x in np.linspace(1, N_OBJETOS, 161)])
        self.play(Create(curva_keep), run_time=1.6)
        et_keep = tag_hud("keepalive: %d ms" % int(HT_KEEPALIVE["ms"]),
                         font_size=19, color=C_COLA)
        et_keep.move_to(g._en(N_OBJETOS, HT_KEEPALIVE["ms"]) + UP * 0.30 +
                        LEFT * 0.75)
        self.play(FadeIn(et_keep), run_time=0.4)
        self.wait(3.2)

        # --- momento: paralelo (6 conexiones a la vez) -----------------------------
        rot.mostrar(pie_curso("Abrir varias conexiones a la vez si "
                              "ayuda: seis tuberias en paralelo."),
                    zona="abajo", run_time=0.5)
        curva_par = VMobject(color=C_OK, stroke_width=3.0)
        curva_par.set_points_as_corners(
            [g._en(x, min(F_PARALELO(x), 4800.0))
             for x in np.linspace(1, N_OBJETOS, 161)])
        self.play(Create(curva_par), run_time=1.4)
        et_par = tag_hud("paralelo: %d ms" % int(HT_PARALELO["ms"]),
                        font_size=17, color=C_OK)
        et_par.move_to(np.array(
            [0.0, g._en(N_OBJETOS, HT_PARALELO["ms"])[1], 0.0]))
        et_par.to_edge(RIGHT, buff=0.3)
        self.play(FadeIn(et_par), run_time=0.4)
        self.wait(3.0)

        # --- momento: el problema real -------------------------------------------
        rot.mostrar(pie_curso("El cuello de botella no es el ancho de "
                              "banda: son los viajes de ida y vuelta."),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- cierre de la leccion --------------------------------------------------
        cierre_leccion(
            self, rot,
            "Pedir es facil.",
            "Pedir cuarenta cosas por un solo tubo, no.",
            "Siguiente: TLS, el candado de la web.",
            g, curva_keep, curva_par, et_apreton, et_serie, et_keep, et_par,
            espera=4.4)
