class Clip2(Scene):
    """8.1.2 - TCP sufre. El tubo tiene 2 914 kB en vuelo y la ventana solo
    64: el techo MEDIDO es el 2.2 % de lo contratado. Y con 477 ms la
    diferencia Reno/CUBIC de la 4.3 deja de ser teorica. El PEP lo arregla
    y dice su precio. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("TCP sufre")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el tubo y la ventana --------------------------------
        rot.mostrar(pie_curso("Con esos 477 milisegundos, un enlace de 50 "
                              "megabits guarda casi tres megabytes EN VUELO."),
                    zona="abajo", run_time=0.5)
        ancho_tubo, y_tubo = 9.60, 1.35
        tubo = Rectangle(width=ancho_tubo, height=0.62, stroke_color=C_RED,
                         stroke_width=2.6, fill_color=C_RED,
                         fill_opacity=0.06)
        tubo.move_to(np.array([0.0, y_tubo, 0.0]))
        et_tubo = tag_hud("en vuelo a %s Mb/s con %s ms:  %s kB"
                          % (fmt(CAP_MBPS, 0), fmt(GEO_USR, 1),
                             miles(TUBO_KB)), font_size=20)
        et_tubo.move_to(np.array([0.0, 2.20, 0.0]))
        self.play(Create(tubo), run_time=0.8)
        self.play(FadeIn(et_tubo), run_time=0.4)

        def barra_ventana(kb):
            w = ancho_tubo * float(kb) / TUBO_KB
            r = Rectangle(width=w, height=0.62, stroke_color=C_PAQUETE,
                          stroke_width=2.4, fill_color=C_PAQUETE,
                          fill_opacity=0.55)
            r.move_to(np.array([-ancho_tubo / 2.0 + w / 2.0, y_tubo, 0.0]))
            return r

        vent = barra_ventana(VENT_CHICA)
        et_vent = tag_hud("la ventana de TCP: %d kB" % VENT_CHICA,
                          font_size=19, color=C_PAQUETE)
        et_vent.move_to(np.array([-2.55, 0.58, 0.0]))
        guia = Line(np.array([-ancho_tubo / 2.0 + 0.10, y_tubo - 0.34, 0.0]),
                    np.array([-3.90, 0.70, 0.0]), color=C_PAQUETE,
                    stroke_width=1.6)
        self.play(FadeIn(vent), run_time=0.5)
        self.play(Create(guia), FadeIn(et_vent), run_time=0.4)
        self.wait(2.5)

        # --- momento: el techo MEDIDO -------------------------------------
        rot.mostrar(pie_curso("Por mucho que contrates, la ventana dividida "
                              "entre el viaje pone el techo."),
                    zona="abajo", run_time=0.5)
        t_techo = tabla(
            ["ventana", "techo medido", "de los %s Mb/s" % fmt(CAP_MBPS, 0),
             "limitado por"],
            [["%d kB" % VENT_CHICA, "%s Mb/s" % fmt(T64["mbps"], 2),
              "%s %%" % fmt(T64["pct_capacidad"], 1), T64["limitado_por"]],
             ["%d kB" % VENT_GRANDE, "%s Mb/s" % fmt(T256["mbps"], 2),
              "%s %%" % fmt(T256["pct_capacidad"], 1), T256["limitado_por"]]],
            anchos=[1.9, 2.4, 2.5, 2.4], alto=0.46, fs=18)
        t_techo.move_to(np.array([0.0, -1.15, 0.0]))
        for j in (1, 2):
            for i in (0, 1):
                t_techo.celda(i, j).set_color(C_CALCULO)
        self.play(FadeIn(t_techo), run_time=0.8)
        self.wait(2.0)
        et_vent2 = tag_hud("la ventana de TCP: %d kB" % VENT_GRANDE,
                           font_size=19, color=C_PAQUETE)
        et_vent2.move_to(et_vent.get_center())
        self.play(Transform(vent, barra_ventana(VENT_GRANDE)),
                  FadeOut(et_vent), run_time=0.6)
        self.play(FadeIn(et_vent2), run_time=0.35)
        self.wait(1.2)
        et_slow = tag_hud("y solo arrancar cuesta %d RTT de arranque lento = "
                          "%s s   (en LEO, %s s)"
                          % (SLOW_RTTS, fmt(SLOW_S, 1), fmt(SLOW_S_LEO, 2)),
                          font_size=18, color=C_COLA)
        et_slow.move_to(np.array([0.0, -2.18, 0.0]))
        self.play(FadeIn(et_slow, shift=0.10 * UP), run_time=0.5)
        self.wait(2.0)

        # --- momento: el enganche con la 4.3 ------------------------------
        rot.mostrar(pie_curso("Y en la 4.3 vimos que Reno se recupera al "
                              "ritmo del RTT. Aqui el RTT es medio segundo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(tubo, et_tubo, vent, guia, et_vent,
                                 t_techo, et_vent2, et_slow)), run_time=0.5)
        cap = tag_hud("volver a llenar una ventana de %s segmentos tras una "
                      "perdida" % miles(TUBO_SEG), font_size=19, color=C_EJE)
        cap.move_to(np.array([0.0, 1.62, 0.0]))
        t_rec = tabla(
            ["RTT", "Reno", "CUBIC", "recupera antes"],
            [[fmt(r["rtt_ms"], 1) + " ms", fmt(r["reno_s"], 1) + " s",
              fmt(r["cubic_s"], 1) + " s", GANADOR(r)] for r in RECUP],
            anchos=[2.0, 2.1, 2.0, 3.0], alto=0.50, fs=19)
        t_rec.move_to(np.array([0.0, 0.42, 0.0]))
        for i in (0, 1):
            for j in (0, 1, 2):
                t_rec.celda(i, j).set_color(C_CALCULO)
        t_rec.celda(1, 1).set_color(C_PERDIDA)
        self.play(FadeIn(cap), run_time=0.4)
        self.play(FadeIn(t_rec), run_time=0.8)
        self.wait(3.5)
        et_min = tag_hud("Reno sube +1 segmento por RTT: %s RTT son %s "
                         "MINUTOS de tubo a medio llenar"
                         % (fmt(RECUP_RENO_RTTS, 1), fmt(RECUP_GEO_MIN, 1)),
                         font_size=19, color=C_PERDIDA)
        et_min.move_to(np.array([0.0, -1.10, 0.0]))
        self.play(FadeIn(et_min, shift=0.10 * UP), run_time=0.5)
        # 2.9 y no 1.7: el frame 6 del muestreo caia justo en el relevo
        # de pie del momento 4 (pie nuevo sobre la tabla que se iba).
        # Alargar la espera ANTERIOR mueve el relevo mas que el punto
        # de muestreo, y el frame cae limpio dentro de este momento.
        self.wait(3.7)

        # --- momento: el PEP, y su precio ---------------------------------
        rot.mostrar(pie_curso("El operador hace trampa: parte la conexion en "
                              "dos y contesta el mismo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(cap, t_rec, et_min)), run_time=0.5)
        pos = {"tu": (-4.90, 0.55), "PEP": (-2.10, 0.55),
               "GEO": (0.60, 2.15), "servidor": (3.40, 0.55)}
        aristas = {("tu", "PEP"): None, ("PEP", "GEO"): None,
                   ("GEO", "servidor"): None}
        tipos = {"tu": "host", "PEP": "router", "GEO": "satelite",
                 "servidor": "servidor"}
        topo = topologia(pos, aristas, tipos, costos=False, tam=0.46, fs=15)
        topo.etiquetas_a({"GEO": UP, "tu": LEFT})
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=0.8)
        topo.enlace("tu", "PEP").linea.set_stroke(C_OK, width=4.4)
        et_a = tag_hud("TCP 1: RTT terrestre", font_size=17, color=C_OK)
        # Sobre el cable, no pegada a el: a 0.28 la etiqueta se montaba
        # encima del host y del circulo del PEP (los nodos son mas altos
        # que la linea).
        et_a.move_to(np.array([-3.50, 1.32, 0.0]))
        et_b = tag_hud("TCP 2: la ventana la maneja el PEP", font_size=17,
                       color=C_PAQUETE)
        et_b.move_to(np.array([1.30, -0.35, 0.0]))
        for a, b in (("PEP", "GEO"), ("GEO", "servidor")):
            topo.enlace(a, b).linea.set_stroke(C_PAQUETE, width=4.4)
        self.play(FadeIn(et_a), FadeIn(et_b), run_time=0.6)
        self.wait(1.8)
        cifras = VGroup(
            tag_hud("con PEP, ventana %d kB    %s Mb/s    %sx"
                    % (VENT_CHICA, fmt(T64["con_pep_mbps"], 1),
                       fmt(T64["ganancia_pep"], 1)), font_size=19),
            tag_hud("con PEP, ventana %d kB   %s Mb/s    %sx   el enlace "
                    "entero" % (VENT_GRANDE, fmt(T256["con_pep_mbps"], 1),
                                fmt(T256["ganancia_pep"], 1)), font_size=19),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(np.array([0.0, -1.32, 0.0]))
        self.play(LaggedStart(*[FadeIn(c, shift=0.10 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.0)
        self.wait(1.8)
        rot.mostrar(pie_curso("Pero mira lo que se rompe: ya no hay una "
                              "conexion tuya de punta a punta."),
                    zona="abajo", run_time=0.5)
        precio = tag_hud(PRECIO_PEP, font_size=19, color=C_PERDIDA)
        precio.move_to(np.array([0.0, -2.20, 0.0]))
        self.play(FadeIn(precio), run_time=0.5)
        self.wait(2.4)
