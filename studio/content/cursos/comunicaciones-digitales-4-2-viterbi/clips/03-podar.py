class Clip3(Scene):
    """4.2.3 - Podar: las metricas acumuladas bajan por la rejilla columna
    a columna y en cada nodo se apaga el camino caro. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Podar: quedarse con lo barato")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        tr = trellis(pasos=PASOS, ancho=8.6, alto=2.5)
        tr.move_to(DOWN * 0.45)
        ramas = tr.todas_ramas(color=C_REJILLA, grosor=1.2, opacidad=0.55)
        tren = tren_bits(RECIBIDO, lado=0.38)
        tren.move_to(UP * 2.25)
        for _i in IDX_ERROR:
            tren.marcar(_i)
        et_tren = tag_junto(tren, "recibido", direccion=LEFT, buff=0.26)

        def etiquetas_de(t):
            """Las metricas acumuladas de la columna t (solo los estados
            alcanzables: los INF no se rotulan)."""
            return VGroup(*[_con_fondo(tr.metrica(t, s, METRICAS[t][s]),
                                       buff=0.08)
                            for s in range(N_ESTADOS) if vivo(t, s)])

        def apagados_de(t):
            """Las animaciones del tramo t: la rama ganadora de cada nodo
            se enciende, la cara y la imposible se apagan."""
            d = poda(t)
            anims = []
            for s, b, s2, _sal in RAMAS_CONV:
                ln = ramas[idx_rama(t, s, b)]
                if not vivo(t, s):
                    anims.append(ln.animate.set_stroke(opacity=0.05))
                elif d[s2]["gana"] == (s, b):
                    anims.append(ln.animate.set_stroke(
                        C_SENAL, width=2.2, opacity=0.95))
                else:
                    anims.append(ln.animate.set_stroke(opacity=0.10))
            return anims

        # --- momento: la metrica de un nodo -------------------------------
        rot.mostrar(pie_curso("Un camino se paga rama a rama; la métrica de "
                              "un nodo es lo que cuesta llegar a él."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(tren), FadeIn(et_tren), FadeIn(tr), FadeIn(ramas),
                  run_time=1.0)
        met_ini = etiquetas_de(0)
        self.play(FadeIn(met_ini), run_time=0.5)
        self.wait(4.2)

        # --- momento: etapa 1 ---------------------------------------------
        rot.mostrar(pie_curso("Etapa uno: solo el estado 00 está vivo, y el "
                              "precio de sus dos ramas ya es su métrica."),
                    zona="abajo", run_time=0.5)
        self.play(*apagados_de(0), run_time=0.9)
        e1 = etiquetas_de(1)
        self.play(LaggedStart(*[FadeIn(e) for e in e1], lag_ratio=0.25),
                  run_time=0.7)
        self.wait(4.0)

        # --- momento: etapa 2 ---------------------------------------------
        rot.mostrar(pie_curso("Etapa dos: la rejilla se llena y ya viven "
                              "los cuatro estados."),
                    zona="abajo", run_time=0.5)
        self.play(*apagados_de(1), run_time=0.9)
        e2 = etiquetas_de(2)
        self.play(LaggedStart(*[FadeIn(e) for e in e2], lag_ratio=0.25),
                  run_time=0.7)
        self.wait(4.0)

        # --- momento: etapas 3 y 4, ya con competencia --------------------
        rot.mostrar(pie_curso("Desde aquí a cada nodo llegan DOS caminos: "
                              "sobrevive el barato y el caro se apaga."),
                    zona="abajo", run_time=0.5)
        etapas = []
        for t in (2, 3):
            self.play(*apagados_de(t), run_time=0.9)
            et = etiquetas_de(t + 1)
            etapas.append(et)
            self.play(LaggedStart(*[FadeIn(e) for e in et], lag_ratio=0.2),
                      run_time=0.6)
        self.wait(2.7)

        # --- momento: el resto de la rejilla, de golpe --------------------
        rot.mostrar(pie_curso("Y así hasta el final: en cada columna quedan "
                              "cuatro supervivientes, ni uno más."),
                    zona="abajo", run_time=0.5)
        resto = []
        for t in range(4, PASOS):
            resto += apagados_de(t)
        self.play(*resto, run_time=1.6)
        e_resto = VGroup(*[etiquetas_de(t) for t in range(5, PASOS + 1)])
        self.play(LaggedStart(*[FadeIn(e) for e in e_resto],
                              lag_ratio=0.18), run_time=1.2)
        self.wait(2.8)

        # --- momento: la mejor metrica de la ultima columna ---------------
        rot.mostrar(pie_curso("De los cuatro que llegan al final, uno es el "
                              "más barato de todos."),
                    zona="abajo", run_time=0.5)
        # la etiqueta del estado ganador dentro de la ultima columna (las
        # etiquetas solo existen para los estados vivos, de ahi la cuenta)
        final = e_resto[-1][sum(1 for s in range(ESTADO_FINAL)
                                if vivo(PASOS, s))]
        marco = SurroundingRectangle(final, color=C_COD, buff=0.03)
        panel = panel_derecha(
            tag_hud(f"supervivientes = {N_ESTADOS}"),
            tag_hud(f"mejor metrica = {METRICA_FINAL}", color=C_COD))
        self.play(Create(marco), run_time=0.7)
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(4.4)
