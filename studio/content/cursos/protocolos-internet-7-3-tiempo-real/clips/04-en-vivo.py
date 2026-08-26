class Clip4(Scene):
    """7.3.4 - Donde se van los segundos de un directo: el desglose
    medido, y como WebRTC lo recorta a decenas de ms. Cierre de la
    leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("En vivo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: varios tramos se suman ------------------------------
        rot.mostrar(pie_curso("Un directo no es instantaneo: varios "
                              "tramos se suman antes de que lo veas."),
                    zona="abajo", run_time=0.5)
        filas = [[nombre, "%d ms" % ms] for nombre, ms in DIRECTO["partes"]]
        idx_peor = [n for n, _ in DIRECTO["partes"]].index(
            DIRECTO_PEOR_NOMBRE)
        t = tabla(["tramo", "duracion"], filas, anchos=[3.2, 1.8],
                 alto=0.46, fs=17, resaltar=idx_peor)
        t.move_to(UP * 0.65)
        self.play(FadeIn(t), run_time=0.8)
        self.wait(3.0)

        # --- momento: el total medido --------------------------------------
        rot.mostrar(pie_curso("Sumados, esos tramos son el retardo que "
                              "ves entre lo que pasa y lo que miras."),
                    zona="abajo", run_time=0.5)
        et_total = tag_hud("total: %s s" % fmt(DIRECTO["total_s"], 1),
                           font_size=26, color=C_CIFRA)
        et_total.next_to(t, DOWN, buff=0.35)
        self.play(FadeIn(et_total, shift=0.12 * UP), run_time=0.6)
        self.wait(3.2)

        # --- momento: el tramo que mas pesa ---------------------------------
        rot.mostrar(pie_curso("El que mas pesa, con diferencia, es el "
                              "bufer del reproductor."),
                    zona="abajo", run_time=0.5)
        et_peor = tag_hud("bufer del reproductor: %d ms de %d ms totales"
                          % (int(DIRECTO_PEOR_MS), int(DIRECTO["total_ms"])),
                          font_size=19, color=C_COLA)
        et_peor.next_to(et_total, DOWN, buff=0.30)
        self.play(FadeIn(et_peor, shift=0.12 * UP), run_time=0.5)
        self.wait(3.0)

        # --- momento: WebRTC recorta el bufer --------------------------------
        rot.mostrar(pie_curso("Si no puedes esperar -una conversacion "
                              "real- WebRTC recorta ese bufer y todo lo "
                              "demas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(t), FadeOut(et_total), FadeOut(et_peor),
                  run_time=0.5)
        escala = 0.85
        barra_d = Rectangle(width=DIRECTO["total_s"] * escala, height=0.42,
                            stroke_color=C_COLA, stroke_width=2.0,
                            fill_color=C_COLA, fill_opacity=0.45)
        et_d = tag_hud("directo: %s s" % fmt(DIRECTO["total_s"], 1),
                       font_size=18, color=C_COLA)
        fila_d = VGroup(barra_d, et_d).arrange(RIGHT, buff=0.24)
        barra_w = Rectangle(width=(DIRECTO["webrtc_ms"] / 1000.0) * escala,
                            height=0.42, stroke_color=C_OK, stroke_width=2.0,
                            fill_color=C_OK, fill_opacity=0.45)
        et_w = tag_hud("WebRTC: %d ms" % int(DIRECTO["webrtc_ms"]),
                       font_size=18, color=C_OK)
        fila_w = VGroup(barra_w, et_w).arrange(RIGHT, buff=0.24)
        barras = VGroup(fila_d, fila_w).arrange(DOWN, buff=0.55,
                                                aligned_edge=LEFT)
        barras.move_to(UP * 0.35)
        self.play(FadeIn(fila_d), run_time=0.6)
        self.play(FadeIn(fila_w), run_time=0.6)
        self.wait(3.6)

        # --- cierre de la leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "Para la voz, un paquete tarde",
            "es un paquete perdido.",
            "Siguiente: Internet en orbita.",
            barras, espera=6.0)
