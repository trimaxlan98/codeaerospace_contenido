class Clip2(Scene):
    """6.3.2 - El bloqueo de cabeza de linea: se pierde UN segmento y TCP
    para los cuatro flujos, aunque los datos de los otros tres ya esten
    en la maquina. Flujos parados CONTADOS. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El bloqueo de cabeza de linea")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los cuatro flujos en una sola conexion TCP ----------
        rot.mostrar(pie_curso("Los cuatro flujos entrelazados viajan por UNA "
                              "conexion TCP."),
                    zona="abajo", run_time=0.5)
        srv = nodo("servidor", "servidor", 0.52)
        srv.move_to(np.array([-5.30, 1.75, 0.0]))
        nav = nodo("host", "navegador", 0.52)
        nav.move_to(np.array([5.30, 1.75, 0.0]))
        cable = enlace(srv.centro(), nav.centro(), color=C_RED, grosor=2.2)
        fila = VGroup(*[ficha(ETIQUETA_FLUJO(f), lado=0.52, fs=17)
                        for f in PATRON_MUX]).arrange(RIGHT, buff=0.10)
        fila.move_to(np.array([0.0, 1.75, 0.0]))
        self.play(FadeIn(srv), FadeIn(nav), Create(cable),
                  LaggedStart(*[FadeIn(f) for f in fila], lag_ratio=0.05),
                  run_time=1.3)
        self.wait(3.0)

        # --- momento: se pierde UN segmento -------------------------------
        rot.mostrar(pie_curso("Se pierde un solo segmento: la primera parte "
                              "del flujo %s." % ETIQUETA_FLUJO(HOL_FLUJO_PERDIDO)),
                    zona="abajo", run_time=0.5)
        perdida = fila[IDX_PERDIDO]
        sitio = perdida.get_center()
        cruz = tag_hud("X", font_size=30, color=C_PERDIDA)
        cruz.next_to(perdida, UP, buff=0.20)
        self.play(perdida.animate.set_color(C_PERDIDA), FadeIn(cruz),
                  run_time=0.6)
        self.play(perdida.animate.shift(DOWN * 0.95).set_opacity(0.0),
                  FadeOut(cruz), run_time=0.8)
        hueco = Square(0.52, stroke_color=C_PERDIDA, stroke_width=2.2,
                       fill_opacity=0.0)
        hueco.move_to(sitio)
        self.play(FadeIn(hueco), run_time=0.3)
        self.wait(3.4)

        # --- momento: las otras once SI llegan ----------------------------
        rot.mostrar(pie_curso("Las otras once llegan enteras. Ya estan en tu "
                              "maquina, en el bufer de TCP."),
                    zona="abajo", run_time=0.5)
        brazo = llave(fila, "%d de %d partes ya estan aqui"
                      % (TCP_LLEGADAS, HOL_PARTES), DOWN, font_size=20)
        self.play(FadeIn(brazo), run_time=0.6)
        self.wait(3.4)

        # --- momento: TCP entrega en orden --------------------------------
        rot.mostrar(pie_curso("Pero TCP entrega en orden: solo suben las que "
                              "llegaron antes del hueco."),
                    zona="abajo", run_time=0.5)
        pinta = []
        for i, f in enumerate(fila):
            if i == IDX_PERDIDO:
                continue
            col = C_OK if i < TCP_ENTREGADAS else C_COLA
            pinta.append(f.caja.animate.set_stroke(col, width=2.6)
                         .set_fill(col, opacity=0.45))
            pinta.append(f.texto.animate.set_color(col))
        self.play(FadeOut(brazo), *pinta, run_time=0.8)
        et_orden = VGroup(
            tag_hud("suben a la pagina:  %d" % TCP_ENTREGADAS, font_size=20,
                    color=C_OK),
            tag_hud("esperan en el bufer:  %d" % TCP_ESPERANDO, font_size=20,
                    color=C_COLA),
        ).arrange(RIGHT, buff=0.90)
        et_orden.move_to(np.array([0.0, 0.62, 0.0]))
        self.play(FadeIn(et_orden), run_time=0.5)
        self.wait(4.8)

        # --- momento: los cuatro flujos, parados --------------------------
        rot.mostrar(pie_curso("Los cuatro se paran por un segmento que solo "
                              "era de uno de ellos."),
                    zona="abajo", run_time=0.5)
        tarjetas = VGroup()
        for f in range(HOL_FLUJOS):
            parado = HOL["tcp"][f]["parado"]
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
        et_cuenta = tag_hud("flujos parados sobre TCP:  %d de %d"
                            % (HOL_PARADOS_TCP, HOL_FLUJOS), font_size=22,
                            color=C_PERDIDA)
        et_cuenta.move_to(np.array([0.0, -2.40, 0.0]))
        self.play(FadeIn(et_cuenta), run_time=0.5)
        self.wait(4.8)
