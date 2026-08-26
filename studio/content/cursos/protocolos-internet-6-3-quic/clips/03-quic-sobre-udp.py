class Clip3(Scene):
    """6.3.3 - La MISMA perdida sobre QUIC: cada flujo lleva su propio
    orden y solo se para el afectado (contado al lado del anterior). Y el
    apreton de transporte y el de TLS ocurren juntos. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("QUIC sobre UDP")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la misma conexion y la misma perdida ----------------
        rot.mostrar(pie_curso("La misma pagina y la misma perdida, pero "
                              "ahora sobre QUIC."),
                    zona="abajo", run_time=0.5)
        srv = nodo("servidor", "servidor", 0.52)
        srv.move_to(np.array([-5.30, 1.75, 0.0]))
        nav = nodo("host", "navegador", 0.52)
        nav.move_to(np.array([5.30, 1.75, 0.0]))
        cable = enlace(srv.centro(), nav.centro(), color=C_RED, grosor=2.2)
        fila = VGroup(*[ficha(ETIQUETA_FLUJO(f), lado=0.52, fs=17)
                        for f in PATRON_MUX]).arrange(RIGHT, buff=0.10)
        fila.move_to(np.array([0.0, 1.75, 0.0]))
        hueco = Square(0.52, stroke_color=C_PERDIDA, stroke_width=2.2,
                       fill_opacity=0.0)
        hueco.move_to(fila[IDX_PERDIDO].get_center())
        fila.remove(fila[IDX_PERDIDO])
        et_pila = tag_hud("una conexion QUIC, encima de UDP", font_size=18,
                          color=C_CAPA)
        et_pila.move_to(np.array([0.0, 2.42, 0.0]))
        self.play(FadeIn(srv), FadeIn(nav), Create(cable),
                  LaggedStart(*[FadeIn(f) for f in fila], lag_ratio=0.05),
                  FadeIn(hueco), run_time=1.3)
        self.play(FadeIn(et_pila), run_time=0.4)
        self.wait(3.8)

        # --- momento: cada flujo con su propio orden ----------------------
        rot.mostrar(pie_curso("QUIC le da a cada flujo su propio orden: el "
                              "hueco solo es hueco para su flujo."),
                    zona="abajo", run_time=0.5)
        pinta = []
        for i, f in enumerate(PATRON_MUX):
            if i == IDX_PERDIDO:
                continue
            caja = fila[i if i < IDX_PERDIDO else i - 1]
            col = C_COLA if f == HOL_FLUJO_PERDIDO else C_OK
            pinta.append(caja.caja.animate.set_stroke(col, width=2.6)
                         .set_fill(col, opacity=0.45))
            pinta.append(caja.texto.animate.set_color(col))
        self.play(*pinta, run_time=0.9)
        et_orden = VGroup(
            tag_hud("suben a la pagina:  %d" % QUIC_ENTREGADAS, font_size=20,
                    color=C_OK),
            tag_hud("esperan en el bufer:  %d" % QUIC_ESPERANDO,
                    font_size=20, color=C_COLA),
        ).arrange(RIGHT, buff=0.90)
        et_orden.move_to(np.array([0.0, 0.62, 0.0]))
        self.play(FadeIn(et_orden), run_time=0.5)
        self.wait(3.8)

        # --- momento: los dos conteos, uno al lado del otro ---------------
        rot.mostrar(pie_curso("Se para el flujo del segmento perdido. Solo "
                              "ese."),
                    zona="abajo", run_time=0.5)
        tarjetas = VGroup()
        for f in range(HOL_FLUJOS):
            parado = HOL["quic"][f]["parado"]
            col = C_PERDIDA if parado else C_OK
            chip = ficha(ETIQUETA_FLUJO(f), lado=0.56, fs=19, color=col)
            et = tag_hud("parado" if parado else "sigue", font_size=17,
                         color=col)
            et.next_to(chip, DOWN, buff=0.16)
            tarjetas.add(VGroup(chip, et))
        tarjetas.arrange(RIGHT, buff=0.95)
        tarjetas.move_to(np.array([0.0, -1.30, 0.0]))
        et_flujos = tag_hud("los cuatro flujos de la pagina", font_size=18,
                            color=C_TENUE)
        et_flujos.move_to(np.array([0.0, -0.35, 0.0]))
        self.play(FadeIn(et_flujos), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(t, shift=0.12 * UP) for t in tarjetas],
                              lag_ratio=0.30), run_time=1.1)
        conteos = VGroup(
            tag_hud("sobre TCP:  %d de %d parados"
                    % (HOL_PARADOS_TCP, HOL_FLUJOS), font_size=21,
                    color=C_PERDIDA),
            tag_hud("sobre QUIC:  %d de %d"
                    % (HOL_PARADOS_QUIC, HOL_FLUJOS), font_size=21,
                    color=C_OK),
        ).arrange(RIGHT, buff=1.10)
        conteos.move_to(np.array([0.0, -2.40, 0.0]))
        self.play(FadeIn(conteos), run_time=0.6)
        self.wait(4.0)

        # --- momento: un solo apreton -------------------------------------
        rot.mostrar(pie_curso("Y hay otro viaje que QUIC se ahorra: no "
                              "negocia el transporte y luego el cifrado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(srv, nav, cable, fila, hueco, et_pila,
                                 et_orden, et_flujos, tarjetas, conteos)),
                  run_time=0.8)
        b_h2 = fila_viajes(VIAJES_H2, "HTTP/2", MS("h2"), y=1.15)
        b_h3 = fila_viajes(VIAJES_H3, "HTTP/3", MS("h3"), y=-0.15)
        self.play(FadeIn(b_h2), run_time=0.7)
        self.play(FadeIn(b_h3), run_time=0.7)
        self.wait(3.6)

        # --- momento: lo que cuesta un viaje ------------------------------
        rot.mostrar(pie_curso("Un viaje menos por cada pagina que abres. "
                              "Cuarenta milisegundos."),
                    zona="abajo", run_time=0.5)
        et_ahorro = VGroup(
            tag_hud("apreton de TCP + TLS 1.3:  %s viajes"
                    % fmt(APRETON_H2, 0), font_size=20, color=C_COLA),
            tag_hud("apreton de QUIC:           %s viaje"
                    % fmt(APRETON_H3, 0), font_size=20, color=C_COLA),
            tag_hud("la pagina entera:  %s ms  en vez de  %s ms"
                    % (fmt(MS("h3"), 0), fmt(MS("h2"), 0)), font_size=22),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        et_ahorro.move_to(np.array([0.0, -1.85, 0.0]))
        self.play(LaggedStart(*[FadeIn(e, shift=0.10 * UP) for e in et_ahorro],
                              lag_ratio=0.35), run_time=1.3)
        self.wait(5.6)
