class Clip3(Scene):
    """3.2.3 - Quinientas corridas. La campana crece, el p95 se asienta
    en 0.098 deg justo por debajo del umbral, y la cola llega a 0.270:
    el peor caso NO pasa. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("El histograma"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        DESPL = LEFT * 1.30 + DOWN * 0.35
        ETAPAS = (25, 100, 250, N_CORRIDAS)

        # El eje se fija con el PEOR caso de la campaña entera: si cada
        # etapa eligiera su propia escala, el histograma "crecería" por
        # cambio de regla y no por corridas nuevas.
        h = histograma(CAMP["rms"][:ETAPAS[0]], bins=26, ancho=6.6,
                       alto=2.6, x_max=PEOR)
        h.shift(DESPL)

        self.play(Create(h.ejes), run_time=0.8)
        self.wait(0.3)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN) for b in h.barras],
                              lag_ratio=0.05), run_time=1.6)

        # El contador baja de carril: el panel de cifras que entra al
        # final ocupa la esquina UR hasta y ~ 1.4 y le caia encima.
        POS_CONT = RIGHT * 4.45 + UP * 0.30
        cont = tag_hud(f"corridas {ETAPAS[0]:03d}", font_size=26)
        cont.move_to(POS_CONT)
        self.play(FadeIn(cont), run_time=0.5)
        self.wait(0.8)

        self.play(FadeIn(h.linea_umbral), FadeIn(h.tag_umbral),
                  run_time=0.6)
        self.wait(1.2)
        self.play(FadeIn(h.linea_p95), FadeIn(h.tag_p95), run_time=0.6)
        self.wait(1.0)

        # La pieza entro por sus hijos: se consolida antes de relevarla.
        self.remove(*h.get_family())
        self.add(h)

        # --- corre la campaña --------------------------------------------
        for k in ETAPAS[1:]:
            gem = h.gemela(CAMP["rms"][:k])
            gem.shift(DESPL)
            self.play(FadeOut(cont), run_time=0.25)
            self.play(Transform(h, gem), run_time=1.1)
            cont = tag_hud(f"corridas {k:03d}", font_size=26)
            cont.move_to(POS_CONT)
            self.play(FadeIn(cont), run_time=0.35)
            self.wait(0.7)

        # --- lo que dice la campaña --------------------------------------
        rot.mostrar(cifra_pie(f"p50 {fmt(P50, 3)} deg"), zona="abajo")
        self.wait(2.0)

        # Un percentil SIN su numero de corridas no significa nada: el N
        # va dentro del rotulo, no en la narracion.
        rot.mostrar(cifra_pie(f"p95 {fmt(P95, 3)} deg N={N_CORRIDAS}",
                              color=C_SAT), zona="abajo")
        self.wait(2.4)

        # --- y la cola, que es lo que NO pasa -----------------------------
        punta = h.ejes[0].get_end() + UP * 0.10
        flecha = Arrow(punta + UP * 1.05 + RIGHT * 0.55, punta, buff=0.0,
                       color=C_PELIGRO, stroke_width=4,
                       max_tip_length_to_length_ratio=0.20)
        t_peor = tag_hud(f"{fmt(PEOR, 3)} deg", font_size=20,
                         color=C_PELIGRO)
        t_peor.next_to(flecha, UP, buff=0.14)
        self.play(GrowArrow(flecha), FadeIn(t_peor), run_time=0.8)
        rot.mostrar(cifra_pie(f"peor {fmt(PEOR, 3)} deg fuera",
                              color=C_PELIGRO), zona="abajo")
        self.wait(2.4)

        panel = panel_cifras(f"p50  {fmt(P50, 3)} deg",
                             (f"p95  {fmt(P95, 3)} deg", C_SAT),
                             (f"peor {fmt(PEOR, 3)} deg", C_PELIGRO),
                             (f"N = {N_CORRIDAS} corridas", C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"p95 {fmt(P95, 3)} deg N={N_CORRIDAS}",
                              color=C_SAT), zona="abajo")
        self.wait(3.2)
