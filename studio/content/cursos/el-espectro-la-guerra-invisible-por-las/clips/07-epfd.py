class Clip7(Scene):
    """7 - epfd: medir el dano donde duele. El patron de antena a la
    izquierda recibe una interferencia por el eje del lobulo principal
    (pulsa rojo) y luego por un lobulo lateral a 40 grados (apenas
    reacciona, verde); a la derecha una mini tierra_y_anillos muestra
    como el satelite NGSO mas cercano al haz cede el paso: se apaga,
    se reenciende y vuelve a apagarse al cerrar el clip. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: arranque del modulo -------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("epfd: medir el daño donde duele")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el patron, un lobulo principal y varios laterales -----
        patron = patron_antena(ancho=3.4, color=C_GSO, font_size=14)
        patron.move_to(np.array([-2.9, -0.1, 0.0]))

        self.play(Create(patron.contorno), FadeIn(patron.eje, patron.rotulo),
                  run_time=1.2)
        rot.mostrar(pie_curso("Una antena no escucha igual en todas "
                              "direcciones: un lóbulo principal y muchos "
                              "laterales."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: interferencia por el eje principal: devastadora -------
        punto_eje = patron.punto_de(0.0)
        flecha_1 = Arrow(punto_eje + 2.6 * RIGHT, punto_eje, buff=0.0,
                         color=C_ONDA, stroke_width=5.0,
                         max_tip_length_to_length_ratio=0.15)

        rot.mostrar(pie_curso("La misma potencia por el eje: devastadora."),
                   zona="abajo", run_time=0.5)
        self.play(GrowArrow(flecha_1), run_time=0.8)
        self.play(Indicate(patron.contorno, color=C_PERDIDA,
                           scale_factor=1.08), run_time=1.0)
        self.wait(3.0)
        self.play(FadeOut(flecha_1), run_time=0.4)

        # --- momento: relevo -> lobulo lateral a 40 grados: casi irrelevante -
        punto_lat = patron.punto_de(40.0)
        direccion_lat = patron.direccion(40.0)
        flecha_2 = Arrow(punto_lat + direccion_lat * 2.3, punto_lat,
                         buff=0.0, color=C_ONDA, stroke_width=5.0,
                         max_tip_length_to_length_ratio=0.15)

        rot.mostrar(pie_curso("...por un lóbulo lateral: casi irrelevante."),
                   zona="abajo", run_time=0.5)
        self.play(GrowArrow(flecha_2), run_time=0.8)
        self.play(Indicate(patron.contorno, color=C_OK, scale_factor=1.03),
                  run_time=0.8)
        self.wait(3.4)
        self.play(FadeOut(flecha_2), run_time=0.4)

        # --- momento: la epfd pesa potencia y geometria ----------------------
        rot.mostrar(pie_curso("La epfd pesa cada emisor por dónde entra. "
                              "Es el número que vigila la UIT."),
                   zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- momento: la mini tierra, el haz y el satelite que cede el paso --
        tierra = tierra_y_anillos(radio_gso=2.0, radio_ngso=1.15, sats_gso=8,
                                  sats_ngso=6, font_size=14)
        tierra.scale(0.85)
        tierra.move_to(np.array([2.9, -0.1, 0.0]))

        haz_enlace = haz(tierra.estacion(-30.0),
                         tierra.sat_gso_mas_cercano(tierra.pos_gso(-30.0)),
                         color=C_GSO)

        self.play(FadeIn(tierra, shift=0.1 * RIGHT), run_time=1.0)
        self.play(Create(haz_enlace), run_time=0.8)

        # El satelite NGSO que cede el paso es el mas cercano al SEGMENTO
        # del haz (no un indice fijo): se mide contra la recta
        # origen->destino con la geometria YA escalada y movida.
        origen_h, destino_h = haz_enlace.origen, haz_enlace.destino
        vector_h = destino_h - origen_h

        def _dist_al_haz(sat):
            p = sat.get_center()
            t = np.clip(np.dot(p - origen_h, vector_h) /
                        np.dot(vector_h, vector_h), 0.0, 1.0)
            return np.linalg.norm(p - (origen_h + t * vector_h))

        sat_cede = min(tierra.sats_ngso, key=_dist_al_haz)

        rot.mostrar(pie_curso("Por eso las constelaciones apagan el haz al "
                              "cruzar el arco: la guerra se gana cediendo "
                              "el paso."), zona="abajo", run_time=0.5)
        self.play(sat_cede.animate.set_opacity(0.2), run_time=0.6)
        self.wait(1.5)
        self.play(sat_cede.animate.set_opacity(1.0), run_time=0.6)
        self.wait(1.0)
        self.play(sat_cede.animate.set_opacity(0.2), run_time=0.5)
        self.wait(2.5)
