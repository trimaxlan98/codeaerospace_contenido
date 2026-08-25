class Clip4(Scene):
    """1.1.4 - Lo que se paga por no reservar: la cola del router, la
    espera medida y los descartes contados. Cierre de la leccion. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El precio: la espera")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el bufer del router ---------------------------------
        rot.mostrar(pie_curso("Cuando llegan mas paquetes de los que caben, "
                              "el router los guarda en una cola."),
                    zona="abajo", run_time=0.5)
        q = cola(capacidad=COLA_CAP, ocupacion=0, lado=0.52,
                 etiqueta="bufer del router")
        q.move_to(UP * 0.55)
        enc = nodo("router", "R1", 0.50)
        enc.next_to(q, LEFT, buff=0.85)
        salida = nodo("router", "R2", 0.50)
        salida.next_to(q, RIGHT, buff=0.85)
        self.play(FadeIn(enc), FadeIn(q), FadeIn(salida), run_time=0.9)
        for n in OCUPACIONES[1:7]:
            nueva = q.con_ocupacion(n)
            self.play(Transform(q, nueva), run_time=0.28)
        self.wait(3.4)

        # --- momento: se llena y se descarta ------------------------------
        rot.mostrar(pie_curso("Si la cola se llena, el router no tiene mas "
                              "remedio: tira el paquete."),
                    zona="abajo", run_time=0.5)
        for n in OCUPACIONES[7:10]:
            nueva = q.con_ocupacion(n)
            self.play(Transform(q, nueva), run_time=0.30)
        caido = Square(0.44, stroke_color=C_PERDIDA, stroke_width=2.4,
                       fill_color=C_PERDIDA, fill_opacity=0.30)
        caido.next_to(q, LEFT, buff=0.10)
        self.play(FadeIn(caido), run_time=0.3)
        self.play(caido.animate.shift(DOWN * 1.25).set_opacity(0.0),
                  run_time=0.8)
        et_desc = tag_hud("descartados: %d de %d  =  %s %%"
                          % (COLA["descartes"], COLA["llegadas"],
                             fmt(COLA["pct_descarte"], 2)),
                          font_size=21, color=C_PERDIDA)
        et_desc.move_to(DOWN * 1.30)
        self.play(FadeIn(et_desc), run_time=0.5)
        self.wait(4.2)

        # --- momento: lo que se paga en tiempo ----------------------------
        rot.mostrar(pie_curso("Y el que no se pierde, espera. Esa espera es "
                              "el precio de no haber reservado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_desc), run_time=0.3)
        cifras = VGroup(
            tag_hud("ocupacion media de la cola   %s paquetes"
                    % fmt(COLA["ocupacion_media"], 2), font_size=20),
            tag_hud("espera media                 %s tiempos de servicio"
                    % fmt(COLA["espera_media"], 2), font_size=20),
            tag_hud("la peor espera medida        %s tiempos de servicio"
                    % fmt(COLA["espera_max"], 1), font_size=20,
                    color=C_COLA),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(DOWN * 1.45)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.5)
        self.wait(4.6)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "Internet no te reserva nada.",
            "Te deja competir, y casi siempre alcanza.",
            "Siguiente: el sobre dentro del sobre.",
            cifras, q, enc, salida, espera=4.8)
