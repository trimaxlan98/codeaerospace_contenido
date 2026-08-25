class Clip3(Scene):
    """2.2.3 - Un router no busca la direccion exacta: barre su tabla y se
    queda con toda fila cuyo prefijo la contiene. Cuatro filas coinciden
    con el mismo destino. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La tabla de ruteo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: la tabla de ruteo -------------------------------------
        rot.mostrar(pie_curso("Un router no conoce direcciones sueltas: "
                              "conoce prefijos, con su siguiente salto."),
                    zona="abajo", run_time=0.5)
        tab = tabla(["Prefijo", "Siguiente salto"], TABLA_RUTAS,
                   anchos=[3.4, 1.9], alto=0.46, fs=18)
        tab.move_to(UP * 0.35)
        self.play(FadeIn(tab), run_time=1.0)
        self.wait(5.5)

        # --- momento: llega un paquete ---------------------------------------
        rot.mostrar(pie_curso("Llega un paquete con destino %s." % IP_A,
                              font_size=23),
                    zona="abajo", run_time=0.5)
        paq = paquete([("Destino", 1.0, IP_A)], ancho=3.2, alto=0.62)
        paq.to_edge(UP, buff=1.45)
        self.play(FadeIn(paq, shift=0.2 * DOWN), run_time=0.8)
        self.wait(5.0)

        # --- momento: el barrido de las filas que coinciden -------------------
        rot.mostrar(pie_curso("El router barre la tabla de arriba abajo: "
                              "coincide con cuatro filas."),
                    zona="abajo", run_time=0.5)
        orden_barrido = sorted(
            (TABLA_RUTAS.index((p, s)) for p, s, _ in RES_A["coinciden"]))
        for i in orden_barrido:
            nueva = tab.con_filas(TABLA_RUTAS, resaltar=i)
            self.play(Transform(tab, nueva), run_time=0.35)
            self.wait(0.35)
        self.wait(2.0)

        # --- momento: gana la mas especifica -----------------------------
        rot.mostrar(pie_curso("De las cuatro, la tabla se queda con la "
                              "mas especifica: /24 por R4."),
                    zona="abajo", run_time=0.5)
        ganadora = tab.con_filas(TABLA_RUTAS, resaltar=IDX_A)
        self.play(Transform(tab, ganadora), run_time=0.5)
        cifras = VGroup(
            tag_hud("coincide con  %d filas" % RES_A["n_coinciden"],
                    font_size=21),
            tag_hud("gana          %s  por  %s"
                    % (RES_A["elegida"], RES_A["siguiente"]),
                    font_size=21, color=C_CIFRA),
        ).arrange(DOWN, buff=0.24, aligned_edge=LEFT)
        cifras.next_to(tab, DOWN, buff=0.55)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.3), run_time=1.0)
        self.wait(7.0)
