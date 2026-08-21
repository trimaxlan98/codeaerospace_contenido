class Clip3(Scene):
    """5.2.3 - Conmutar el modcod: acm_conmutar elige cada minuto el
    modcod mas denso que todavia cierra (histeresis incluida); la
    escalera sigue la lluvia y el unico corte (20 min) se marca en rojo.
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Conmutar el modcod")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el enlace elige, minuto a minuto -----------------------
        rot.mostrar(pie_curso("Un enlace ACM no se queda quieto: cada "
                              "minuto elige el modcod mas denso que "
                              "TODAVIA cierra."), zona="abajo",
                    run_time=0.5)
        tasa = onda(T_LLUVIA, TASA_ELEGIDA, rango_y=(0.0, TASA_TECHO),
                   ancho=8.6, alto=3.2, color=C_TECHO)
        tasa.move_to(DOWN * 0.2)
        self.play(FadeIn(tasa.ejes), run_time=0.5)

        # tramos contiguos del MISMO modcod (agrupar el array elegido)
        tramos = []
        inicio = 0
        for i in range(1, MIN_TOTAL + 1):
            if i == MIN_TOTAL or ELECCION[i] != ELECCION[inicio]:
                tramos.append((inicio, i - 1, int(ELECCION[inicio])))
                inicio = i

        segmentos = VGroup()
        for a, b, idx in tramos:
            color = MODCOD_COLORES[idx] if idx >= 0 else C_RUIDO
            seg = tasa.curva_de(T_LLUVIA[a:b + 1], TASA_ELEGIDA[a:b + 1],
                                color=color, grosor=3.4)
            segmentos.add(seg)
        self.play(LaggedStart(*[Create(s) for s in segmentos],
                              lag_ratio=0.04), run_time=3.0)
        self.wait(3.6)

        # --- momento: el color dice el modcod ---------------------------------
        rot.mostrar(pie_curso("Cada color es un modcod: mas denso, mas "
                              "bits por simbolo -- pero exige mas SNR."),
                    zona="abajo", run_time=0.5)
        filas = VGroup(*[
            VGroup(Dot(radius=0.06, color=col),
                  tag_hud(f"{nombre} ({fmt(umbral, 1)} dB)",
                          font_size=15, color=col)
                  ).arrange(RIGHT, buff=0.12)
            for nombre, umbral, col in zip(MODCOD_NOMBRES, MODCOD_UMBRALES,
                                           MODCOD_COLORES)])
        panel = panel_derecha(*filas)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(5.4)

        # --- momento: el corte, el unico tramo rojo ----------------------------
        rot.mostrar(pie_curso("Y cuando ni el modcod mas robusto cierra, "
                              "el enlace se corta: veinte minutos "
                              "seguidos, marcados en rojo."),
                    zona="abajo", run_time=0.5)
        t_medio = 0.5 * (T_LLUVIA[CORTE_INICIO] + T_LLUVIA[CORTE_FIN])
        p_corte = tasa.en(t_medio, 0.0)
        et_corte = tag_hud(f"corte = {fmt(float(CORTE_FIN - CORTE_INICIO + 1), 0)} min",
                           font_size=16, color=C_RUIDO)
        et_corte.next_to(p_corte, DOWN, buff=0.24)
        fila_corte = VGroup(Dot(radius=0.06, color=C_RUIDO),
                            tag_hud("sin enlace", font_size=15,
                                   color=C_RUIDO)).arrange(RIGHT, buff=0.12)
        panel_corte = panel_derecha(fila_corte)
        panel_corte.next_to(panel, DOWN, buff=0.22)
        i_corte = next(i for i, (_, _, idx) in enumerate(tramos) if idx < 0)
        self.play(FadeIn(et_corte), FadeIn(panel_corte), run_time=0.5)
        self.play(Indicate(segmentos[i_corte], color=C_RUIDO,
                           scale_factor=1.15), run_time=0.9)
        self.wait(4.8)

        # --- momento: el enlace elige solo -------------------------------------
        rot.mostrar(pie_curso("El enlace escala y baja solo: siempre el "
                              "mejor plan que el clima de verdad "
                              "permite."), zona="abajo", run_time=0.5)
        self.wait(7.0)
