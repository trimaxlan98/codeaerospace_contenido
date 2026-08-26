class Clip4(Scene):
    """3.2.4 - Contraste honesto: el vector distancia converge rapido por
    rumores (Bellman-Ford, 3 rondas); el estado del enlace reparte el
    mapa completo mas caro (4 rondas, 16 mensajes) y a cambio nadie
    calcula sobre un rumor. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Converger rapido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: lo que ya costo el mapa compartido --------------------
        rot.mostrar(pie_curso("El estado del enlace ya lo vimos: cuatro "
                              "rondas, dieciseis mensajes, el mismo mapa "
                              "para los seis."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_RED, RED, costos=False)
        topo.move_to(UP * 1.9)
        topo.scale(0.42)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=0.9)
        self.play(*[topo.nodo(n).forma.animate.set_stroke(C_OK, width=3.0)
                    for n in ORDEN_DIJ], run_time=0.4)
        cifras_inu = VGroup(
            tag_hud("estado del enlace  ·  inundacion", font_size=20,
                   color=C_TENUE),
            tag_hud("4 rondas   ·   16 mensajes contados", font_size=24),
        ).arrange(DOWN, buff=0.18)
        cifras_inu.move_to(DOWN * 0.35)
        self.play(LaggedStart(*[FadeIn(c, shift=0.1 * UP)
                                for c in cifras_inu], lag_ratio=0.4),
                  run_time=0.9)
        self.wait(3.4)

        # --- momento: el rumor converge en tres rondas -----------------------
        rot.mostrar(pie_curso("Por rumores, desde F, el vector distancia "
                              "converge en solo tres rondas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifras_inu), run_time=0.4)

        def fila_bf(estado):
            return [[n, fmt(estado[n][0], 0)] for n in BF_F["nodos"]]

        tbl = tabla(["Router", "Dist a F"], fila_bf(BF_F["historia"][0]),
                   anchos=[1.7, 2.1], alto=0.42, fs=17, color=C_CALCULO)
        tbl.move_to(DOWN * 0.85)
        et_ronda = tag_hud("ronda 0", font_size=20, color=C_TENUE)
        et_ronda.next_to(tbl, UP, buff=0.22)
        self.play(FadeIn(tbl), FadeIn(et_ronda), run_time=0.6)
        self.wait(0.6)
        for r in range(1, BF_F["rondas"] + 1):
            nueva_tbl = tbl.con_filas(fila_bf(BF_F["historia"][r]))
            nuevo_ronda = tag_hud("ronda %d" % r, font_size=20,
                                 color=C_TENUE)
            nuevo_ronda.move_to(et_ronda)
            self.play(Transform(tbl, nueva_tbl),
                      Transform(et_ronda, nuevo_ronda), run_time=0.6)
            self.wait(0.8)
        self.wait(1.2)

        # --- momento: la comparacion honesta -----------------------------
        rot.mostrar(pie_curso("El estado del enlace cuesta mas mensajes. "
                              "A cambio, nadie calcula sobre un rumor."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tbl), FadeOut(et_ronda), FadeOut(topo),
                  run_time=0.5)
        comparacion = VGroup(
            tag_hud("rumores (vector distancia):  3 rondas", font_size=23),
            tag_hud("mapa compartido (estado del enlace):  4 rondas   ·   "
                    "16 mensajes", font_size=23),
        ).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        comparacion.move_to(UP * 0.9)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP)
                                for c in comparacion], lag_ratio=0.4),
                  run_time=1.0)
        self.wait(3.6)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(
            self, rot,
            "Un mapa compartido cuesta mas de mantener.",
            "Y se equivoca mucho menos.",
            "Siguiente: BGP, la politica entre paises.",
            comparacion, espera=4.8)
