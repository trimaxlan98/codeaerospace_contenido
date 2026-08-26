class Clip4(Scene):
    """2.1.4 - Fragmentar: 4000 B por un enlace de MTU 1500 salen como tres
    datagramas con offset y MF reales. Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Fragmentar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: lo que no cabe --------------------------------------
        rot.mostrar(pie_curso("Cuatro mil bytes de datos llegan a un enlace "
                              "que no deja pasar mas de %d." % MTU),
                    zona="abajo", run_time=0.5)
        barra = Rectangle(width=CARGA_BYTES * FRAG_ESCALA, height=0.74,
                          stroke_color=C_PAQUETE, stroke_width=2.6,
                          fill_color=C_PAQUETE, fill_opacity=0.16)
        barra.move_to(UP * 1.85)
        et_barra = tag_hud("%d B de datos" % CARGA_BYTES, font_size=22,
                           color=C_PAQUETE)
        et_barra.move_to(barra.get_center())
        self.play(FadeIn(barra), FadeIn(et_barra), run_time=0.8)
        puerta = Rectangle(width=MTU * FRAG_ESCALA, height=0.74,
                           stroke_color=C_COLA, stroke_width=2.8)
        puerta.move_to(UP * 0.45)
        et_puerta = tag_hud("MTU del enlace:  %d B" % MTU, font_size=22,
                            color=C_COLA)
        et_puerta.next_to(puerta, DOWN, buff=0.22)
        self.play(Create(puerta), FadeIn(et_puerta), run_time=0.7)
        et_nocabe = tag_hud("no cabe", font_size=24, color=C_PERDIDA)
        et_nocabe.move_to(np.array([5.20, 1.15, 0.0]))
        self.play(FadeIn(et_nocabe, scale=1.25), run_time=0.4)
        self.wait(3.4)

        # --- momento: tres datagramas nuevos ------------------------------
        self.play(FadeOut(barra), FadeOut(et_barra), FadeOut(puerta),
                  FadeOut(et_puerta), FadeOut(et_nocabe), run_time=0.4)
        rot.mostrar(pie_curso("IP lo parte en tres, y cada trozo se vuelve "
                              "un datagrama con su propia cabecera."),
                    zona="abajo", run_time=0.5)
        # Los pesos suman el ancho: asi la carga queda a escala entre
        # fragmentos (1480 B mas larga que 1040 B) y la cabecera mide lo
        # mismo en los tres, como en la realidad.
        caps = VGroup(*[
            paquete([("Cabecera IP", 0.95, "%d B" % FRAG_CAB),
                     ("Carga", 4.6 * f["datos"] / FRAG_UTIL,
                      "%d B" % f["datos"])],
                    ancho=0.95 + 4.6 * f["datos"] / FRAG_UTIL, alto=0.58,
                    fs=14)
            for f in FRAGS])
        caps.arrange(DOWN, buff=0.58, aligned_edge=LEFT)
        caps.move_to(np.array([-3.35, 0.45, 0.0]))
        et_escala = tag_hud("esquema: la carga va a escala; los %d B de "
                            "cabecera, no" % FRAG_CAB,
                            font_size=15, color=C_EJE)
        et_escala.move_to(np.array([-1.55, 2.62, 0.0]))
        self.play(LaggedStart(*[FadeIn(c, shift=0.18 * RIGHT) for c in caps],
                              lag_ratio=0.35), run_time=1.6)
        self.play(FadeIn(et_escala), run_time=0.4)
        self.wait(3.0)

        # --- momento: donde encaja cada trozo -----------------------------
        rot.mostrar(pie_curso("El desplazamiento dice donde encaja cada "
                              "trozo; MF, si viene otro detras."),
                    zona="abajo", run_time=0.5)
        tab = tabla(["frag", "despl.", "datos", "MF"], FILAS_FRAG,
                    anchos=[0.95, 1.35, 1.35, 0.75], alto=0.46, fs=17)
        tab.move_to(np.array([3.85, caps[1].get_center()[1], 0.0]))
        self.play(FadeIn(tab), run_time=1.0)
        et_extra = tag_hud("el desplazamiento va en unidades de 8 B:  "
                           "%d / 8 = %d" % (FRAGS[1]["offset_bytes"],
                                            FRAGS[1]["offset_campo"]),
                           font_size=19, color=C_EJE)
        et_extra.move_to(DOWN * 1.80)
        et_coste = tag_hud("y ahora viajan %d B de cabecera de mas"
                           % FRAG_EXTRA, font_size=21, color=C_COLA)
        et_coste.move_to(DOWN * 2.30)
        self.play(FadeIn(et_extra), run_time=0.45)
        self.play(FadeIn(et_coste), run_time=0.45)
        self.wait(3.6)

        # --- momento: si falta uno, faltan todos --------------------------
        self.play(FadeOut(et_extra), FadeOut(et_coste), run_time=0.35)
        rot.mostrar(pie_curso("Si se pierde uno solo, se pierde el datagrama "
                              "entero: nadie retransmite fragmentos."),
                    zona="abajo", run_time=0.5)
        i = FRAG_PERDIDO - 1
        self.play(caps[i].animate.set_color(C_PERDIDA),
                  tab.fila(i).animate.set_color(C_PERDIDA), run_time=0.5)
        self.play(caps[i].animate.shift(DOWN * 0.9).set_opacity(0.0),
                  run_time=0.7)
        et_todo = tag_hud("faltan %d B: los otros %d fragmentos se tiran "
                          "tambien" % (FRAGS[i]["datos"], FRAG_N - 1),
                          font_size=21, color=C_PERDIDA)
        et_todo.move_to(DOWN * 2.15)
        self.play(FadeIn(et_todo), run_time=0.45)
        self.play(*[caps[k].animate.set_color(C_PERDIDA)
                    for k in range(FRAG_N) if k != i], run_time=0.6)
        self.wait(3.0)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "IP es un acuerdo minimo.",
            "Por eso cupo todo el mundo dentro.",
            "Siguiente: el prefijo manda.",
            caps, tab, et_todo, et_escala, espera=4.6)
