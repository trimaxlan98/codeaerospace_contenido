class Clip1(Scene):
    """6.1.1 - HTTP cabe en unas pocas lineas de texto plano: la peticion,
    la respuesta y los bytes que cuesta cada una. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La peticion")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: navegador y servidor ---------------------------------
        rot.mostrar(pie_curso("El protocolo mas usado del mundo cabe en "
                              "una linea de texto legible."),
                    zona="abajo", run_time=0.5)
        nav = nodo("host", "Navegador", 0.46)
        srv = nodo("servidor", "Servidor", 0.46)
        nav.move_to(LEFT * 4.6 + UP * 1.55)
        srv.move_to(RIGHT * 4.6 + UP * 1.55)
        self.play(FadeIn(nav), FadeIn(srv), run_time=0.7)
        self.wait(4.4)

        # --- momento: la peticion en texto plano ----------------------------
        rot.mostrar(pie_curso("El navegador manda esto. Nada mas: "
                              "metodo, ruta, version, y unas cabeceras."),
                    zona="abajo", run_time=0.5)
        lineas_pet = VGroup(*[
            tag_hud(l, font_size=17, color=C_PAQUETE if i == 0 else C_CAPA)
            for i, l in enumerate(PET_LINEAS)
        ]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        lineas_pet.move_to(UP * 0.15)
        self.play(LaggedStart(*[FadeIn(l, shift=0.10 * UP)
                               for l in lineas_pet], lag_ratio=0.30),
                  run_time=1.6)
        self.wait(4.6)

        # --- momento: la respuesta -------------------------------------------
        rot.mostrar(pie_curso("El servidor contesta igual de plano: "
                              "estado, cabeceras, y el cuerpo detras."),
                    zona="abajo", run_time=0.5)
        self.play(lineas_pet.animate.scale(0.86).to_edge(LEFT, buff=0.9)
                  .shift(UP * 0.15), run_time=0.7)
        lineas_resp = VGroup(*[
            tag_hud(l, font_size=17, color=C_OK if i == 0 else C_CAPA)
            for i, l in enumerate(RESP_LINEAS)
        ]).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        lineas_resp.scale(0.86).to_edge(RIGHT, buff=0.7).shift(UP * 0.15)
        self.play(LaggedStart(*[FadeIn(l, shift=0.10 * UP)
                               for l in lineas_resp], lag_ratio=0.30),
                  run_time=1.6)
        cuerpo_caja = Rectangle(width=2.0, height=0.5, stroke_color=C_PAQUETE,
                                stroke_width=2.2, fill_color=C_PAQUETE,
                                fill_opacity=0.16)
        cuerpo_caja.next_to(lineas_resp, DOWN, buff=0.22)
        et_cuerpo = tag_hud("cuerpo: %d B" % BYTES_CUERPO, font_size=16,
                           color=C_PAQUETE)
        et_cuerpo.move_to(cuerpo_caja.get_center())
        self.play(FadeIn(cuerpo_caja), FadeIn(et_cuerpo), run_time=0.6)
        self.wait(4.2)

        # --- momento: los bytes contados --------------------------------------
        rot.mostrar(pie_curso("Contando byte a byte: pedir cuesta %d B, "
                              "la cabecera de la respuesta %d B, el "
                              "cuerpo %d B."
                              % (BYTES_PETICION, BYTES_CAB_RESP,
                                 BYTES_CUERPO)),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(lineas_pet), FadeOut(lineas_resp),
                  FadeOut(cuerpo_caja), FadeOut(et_cuerpo),
                  FadeOut(nav), FadeOut(srv), run_time=0.6)
        pk = paquete([("Protocolo", BYTES_PROTOCOLO,
                      "%d B" % BYTES_PROTOCOLO),
                     ("Carga util", BYTES_CUERPO, "%d B" % BYTES_CUERPO)],
                    ancho=8.4, alto=0.85, color=C_CAPA,
                    color_carga=C_PAQUETE)
        pk.move_to(UP * 0.35)
        self.play(FadeIn(pk), run_time=0.8)
        et_pct = tag_hud("protocolo: %s %% del total (%d B)"
                         % (fmt(PROTOCOLO_PCT, 1), BYTES_TOTAL),
                         font_size=22, color=C_CIFRA)
        et_pct.next_to(pk, DOWN, buff=0.45)
        self.play(FadeIn(et_pct, shift=0.14 * UP), run_time=0.6)
        self.wait(5.0)
