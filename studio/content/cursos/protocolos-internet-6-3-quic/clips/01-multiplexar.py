class Clip1(Scene):
    """6.3.1 - HTTP/2: los 40 objetos como flujos entrelazados en UNA
    conexion, en binario y sin repetir cabeceras. Tiempo MEDIDO frente a
    las dos formas que dejo la 6.1. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Multiplexar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: lo que dejo la 6.1 ----------------------------------
        rot.mostrar(pie_curso("La leccion 6.1 dejo una pagina de 40 objetos "
                              "y tres maneras de pedirla."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(*[
            tag_hud("%-36s %5s ms" % (NOMBRE_MODO[m], fmt(MS(m), 0)),
                    font_size=19)
            for m in ("serie", "keepalive", "paralelo")
        ]).arrange(DOWN, buff=0.26, aligned_edge=LEFT)
        cifras.move_to(DOWN * 0.55)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.4)
        self.wait(4.4)

        # --- momento: las tres son la misma fila india --------------------
        rot.mostrar(pie_curso("Las tres son la misma fila india: cada objeto "
                              "espera a que termine el anterior."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifras), run_time=0.4)

        srv = nodo("servidor", "servidor", 0.52)
        srv.move_to(np.array([-5.30, 0.50, 0.0]))
        nav = nodo("host", "navegador", 0.52)
        nav.move_to(np.array([5.30, 0.50, 0.0]))
        cable = enlace(srv.centro(), nav.centro(), color=C_RED, grosor=2.2)

        fila = VGroup(*[ficha(ETIQUETA_FLUJO(f), lado=0.52, fs=17)
                        for f in PATRON_FILA]).arrange(RIGHT, buff=0.10)
        fila.move_to(np.array([0.0, 0.50, 0.0]))
        self.play(FadeIn(srv), FadeIn(nav), Create(cable), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(f) for f in fila], lag_ratio=0.06),
                  run_time=1.0)
        et_fila = tag_hud("los objetos 1, 2, 3 y 4, uno detras de otro",
                          font_size=18, color=C_TENUE)
        et_fila.move_to(np.array([0.0, -0.60, 0.0]))
        self.play(FadeIn(et_fila), run_time=0.4)
        self.wait(3.4)

        # --- momento: HTTP/2 entrelaza ------------------------------------
        rot.mostrar(pie_curso("HTTP/2 abre UNA conexion y entrelaza los "
                              "cuarenta: cada objeto es un flujo."),
                    zona="abajo", run_time=0.5)
        mux = VGroup(*[ficha(ETIQUETA_FLUJO(f), lado=0.52, fs=17)
                       for f in PATRON_MUX]).arrange(RIGHT, buff=0.10)
        mux.move_to(np.array([0.0, 0.50, 0.0]))
        self.play(FadeOut(et_fila), run_time=0.3)
        self.play(Transform(fila, mux), run_time=1.3)
        et_mux = tag_hud("una sola conexion, %d flujos entrelazados"
                         % HOL_FLUJOS, font_size=18, color=C_PAQUETE)
        et_mux.move_to(np.array([0.0, -0.60, 0.0]))
        self.play(FadeIn(et_mux), run_time=0.4)
        self.wait(3.6)

        # --- momento: en binario y sin repetir cabeceras ------------------
        rot.mostrar(pie_curso("Y en binario: las cabeceras que HTTP/1.1 "
                              "repetia objeto tras objeto ya no viajan."),
                    zona="abajo", run_time=0.5)
        hpack = VGroup(
            tag_hud("cada peticion HTTP/1.1    %d B de cabeceras"
                    % PET["bytes_peticion"], font_size=19),
            tag_hud("por %d objetos            %s B repetidos"
                    % (N_OBJETOS, fmt(CABECERAS_REPETIDAS, 0)),
                    font_size=19),
            tag_hud("HPACK: la tabla comun no se vuelve a mandar",
                    font_size=18, color=C_CAPA),
        ).arrange(DOWN, buff=0.20, aligned_edge=LEFT)
        hpack.move_to(np.array([0.0, -1.60, 0.0]))
        self.play(LaggedStart(*[FadeIn(h, shift=0.10 * UP) for h in hpack],
                              lag_ratio=0.35), run_time=1.3)
        self.wait(3.8)

        # --- momento: el tiempo medido ------------------------------------
        rot.mostrar(pie_curso("Un apreton y un solo viaje para los cuarenta. "
                              "Ciento veinte milisegundos."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(hpack), run_time=0.4)
        marca = VGroup(
            tag_hud("%-36s %5s ms" % (NOMBRE_MODO["h2"], fmt(MS("h2"), 0)),
                    font_size=22),
            tag_hud("%s veces mas rapido que seis conexiones   /   "
                    "%s veces mas que la fila india"
                    % (fmt(GANANCIA_H2, 0), fmt(GANANCIA_H2_FILA, 0)),
                    font_size=19, color=C_PAQUETE),
        ).arrange(DOWN, buff=0.28)
        marca.move_to(np.array([0.0, -1.65, 0.0]))
        self.play(FadeIn(marca[0], shift=0.12 * UP), run_time=0.6)
        self.play(FadeIn(marca[1]), run_time=0.5)
        self.wait(4.6)
