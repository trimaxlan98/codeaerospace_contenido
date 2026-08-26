class Clip1(Scene):
    """7.2.1 - La ley de Little verificada SOBRE la simulacion de una cola
    M/M/1 con bufer finito: L, lambda y W medidos (no citados), y la
    ocupacion que explota cuando la carga se acerca a 1. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La ley de Little")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la cola llenandose -----------------------------------
        rot.mostrar(pie_curso("Una cola de bufer finito: los paquetes "
                              "llegan, esperan su turno y salen."),
                    zona="abajo", run_time=0.5)
        q = cola(capacidad=CAP_COLA1, ocupacion=0, lado=0.50,
                 etiqueta="bufer, capacidad %d" % CAP_COLA1)
        q.move_to(UP * 0.3)
        enc = nodo("router", "entra", 0.44)
        enc.next_to(q, LEFT, buff=0.85)
        sal = nodo("servidor", "sirve", 0.44)
        sal.next_to(q, RIGHT, buff=0.85)
        self.play(FadeIn(enc), FadeIn(q), FadeIn(sal), run_time=0.8)
        for n in (2, 4, 6, 8, 5, 7, 8):
            self.play(Transform(q, q.con_ocupacion(n)), run_time=0.26)
        self.wait(1.4)

        # --- momento: la traza real en el tiempo (Sierra) -------------------
        rot.mostrar(pie_curso("Esa misma simulacion a lo largo del tiempo: "
                              "sube y baja alrededor de su media."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(enc), FadeOut(q), FadeOut(sal), run_time=0.4)
        s = sierra(TRAZA_OCUPACION, ancho=7.2, alto=2.6, color=C_COLA,
                  etiqueta="ocupacion de la cola en el tiempo")
        s.move_to(UP * 0.35)
        self.play(FadeIn(s.ejes), FadeIn(s.etiqueta), run_time=0.4)
        self.play(Create(s.curva), run_time=1.8)
        self.play(Create(s.media), run_time=0.5)
        et_media = tag_hud("L medida = %s paquetes en promedio"
                           % fmt(L_MEDIDA, 3), font_size=19, color=C_CIFRA)
        et_media.next_to(s, DOWN, buff=0.32)
        self.play(FadeIn(et_media), run_time=0.4)
        self.wait(2.6)

        # --- momento: las tres cifras y la verificacion ---------------------
        rot.mostrar(pie_curso("La ley de Little dice L = lambda por W. "
                              "Verificala con las tres cifras medidas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(s), FadeOut(et_media), run_time=0.4)
        cifras = VGroup(
            tag_hud("L  (en el sistema)          %s" % fmt(L_MEDIDA, 3),
                    font_size=20),
            tag_hud("lambda efectiva (aceptada)  %s" %
                    fmt(LAMBDA_EFECTIVA, 3), font_size=20),
            tag_hud("W  (tiempo total dentro)    %s" % fmt(W_MEDIA, 3),
                    font_size=20),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(UP * 1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.3), run_time=1.3)
        self.wait(0.6)

        formula = formula_pie(r"L \approx \lambda \cdot W")
        rot.mostrar(formula, zona="abajo", run_time=0.5)
        pred = tag_hud("lambda x W = %s   (medido: %s, %s%% de diferencia)"
                       % (fmt(L_PREDICHA, 3), fmt(L_MEDIDA, 3),
                          fmt(GAP_LITTLE_PCT, 1)), font_size=19,
                       color=C_CIFRA)
        pred.next_to(cifras, DOWN, buff=0.4)
        self.play(FadeIn(pred), run_time=0.5)
        self.wait(1.4)

        rot.mostrar(pie_curso("No sale exacta: %d de %d paquetes se "
                              "descartaron por bufer lleno, y esos no "
                              "cuentan como lambda." %
                              (COLA1["descartes"], COLA1["llegadas"])),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- momento: la explosion cerca de carga 1 -------------------------
        rot.mostrar(pie_curso("Y si subes la carga hacia 1, la ocupacion "
                              "no crece poco a poco: EXPLOTA."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifras), FadeOut(pred), run_time=0.4)
        g = grafica(OCUPACION_EN, (0.05, 0.99), (0.0, 4.3), ancho=7.2,
                   alto=2.8, color=C_COLA, etiqueta_x="carga (lambda/mu)",
                   etiqueta_y="ocupacion media")
        g.move_to(DOWN * 0.25)
        self.play(FadeIn(g.ejes), run_time=0.4)
        self.play(Create(g.curva), run_time=1.8)
        self.wait(3.0)
