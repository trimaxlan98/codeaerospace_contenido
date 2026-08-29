class Clip4(Scene):
    """3.2.4 - Cuanta confianza merece ese p95: 4.87 corridas de
    desviacion con N=500 (+/-1 punto percentil) y 9.75 con N=2000
    (+/-0.5). Cuadruplicar solo duplica. Y la semilla. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Cuanto confias en el p95"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(r"\sigma = \sqrt{N\,p\,(1-p)}"),
                    zona="abajo")
        self.wait(1.8)

        # --- la confianza del percentil, en puntos percentil -------------
        # La razon entre las dos es 2: en lineal se lee sola, y ponerla en
        # log aqui esconderia justo lo que hay que ver.
        conf = barras_comparar(
            [INC_500["puntos_percentil"], INC_2000["puntos_percentil"]],
            [f"N={N_CORRIDAS}", "N=2000"], ancho=3.2, alto=1.9,
            colores=[C_SAT, C_OK], unidad="")
        conf.move_to(LEFT * 3.35 + DOWN * 0.45)
        self.play(Create(conf.ejes), run_time=0.6)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in conf.barras], lag_ratio=0.30),
                  FadeIn(conf.rotulos), run_time=1.2)
        t_conf = VGroup()
        for i, inc in enumerate((INC_500, INC_2000)):
            t = tag_hud(f"+/-{fmt(inc['puntos_percentil'], 2)}",
                        font_size=19,
                        color=C_SAT if i == 0 else C_OK)
            t.next_to(conf.barras[i], UP, buff=0.12)
            t_conf.add(t)
        self.play(FadeIn(t_conf), run_time=0.6)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"N={N_CORRIDAS} "
                              f"{fmt(INC_500['corridas_sd'], 2)} corridas",
                              color=C_SAT), zona="abajo")
        self.wait(1.9)

        # --- y contra que se compara: el margen de verdad ----------------
        # p95 y objetivo tienen razon 1.02: se dibujan LINEALES, que es lo
        # que enseña que el diseño pasa raspando.
        margen = barras_comparar(
            [P95, OBJETIVO_DEG], ["p95", "objetivo"], ancho=3.4, alto=1.9,
            colores=[C_SAT, C_CALCULO], unidad="deg")
        margen.move_to(RIGHT * 0.95 + DOWN * 0.45)
        self.play(Create(margen.ejes), run_time=0.6)
        self.play(LaggedStart(*[GrowFromEdge(b, DOWN)
                                for b in margen.barras], lag_ratio=0.30),
                  FadeIn(margen.rotulos), run_time=1.1)
        t_marg = VGroup()
        for i, v in enumerate((P95, OBJETIVO_DEG)):
            t = tag_hud(f"{fmt(v, 3)}", font_size=19,
                        color=C_SAT if i == 0 else C_CALCULO)
            t.next_to(margen.barras[i], UP, buff=0.12)
            t_marg.add(t)
        self.play(FadeIn(t_marg), run_time=0.5)
        self.wait(1.1)

        # El margen del p95 lleva su N DENTRO del rotulo: es la cifra mas
        # dependiente del muestreo de la leccion. Sondeadas 20 semillas a
        # N=500, el p95 va de 0.077 a 0.106 y DOS de las veinte no pasan;
        # con N=4000 se asienta en ~0.088. Decir "pasa por 2 %" sin el N
        # seria vender como propiedad del diseño lo que es de la campaña.
        rot.mostrar(cifra_pie(f"pasa por {fmt(100 * MARGEN_P95, 0)} % "
                              f"N={N_CORRIDAS}"), zona="abajo")
        self.wait(2.1)

        rot.mostrar(cifra_pie(f"N=2000 "
                              f"+/-{fmt(INC_2000['puntos_percentil'], 2)} pt",
                              color=C_OK), zona="abajo")
        self.wait(1.9)
        rot.mostrar(cifra_pie("x4 corridas x2 confianza"), zona="abajo")
        self.wait(1.9)

        panel = panel_cifras((f"p95    {fmt(P95, 3)} deg", C_SAT),
                             f"margen {fmt(100 * MARGEN_P95, 0)} %",
                             (f"N={N_CORRIDAS}  +/-"
                              f"{fmt(INC_500['puntos_percentil'], 2)} pt",
                              C_SAT),
                             (f"N=2000 +/-"
                              f"{fmt(INC_2000['puntos_percentil'], 2)} pt",
                              C_OK))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.1)

        # --- la semilla: misma semilla, histograma identico --------------
        self.play(FadeOut(conf.ejes), FadeOut(conf.barras),
                  FadeOut(conf.rotulos), FadeOut(t_conf),
                  FadeOut(margen.ejes), FadeOut(margen.barras),
                  FadeOut(margen.rotulos), FadeOut(t_marg),
                  FadeOut(panel), run_time=0.7)

        DESPL = DOWN * 0.45
        h_a = histograma(CAMP["rms"], bins=26, ancho=6.4, alto=2.4,
                         x_max=PEOR)
        h_a.shift(DESPL)
        self.play(Create(h_a.ejes), run_time=0.7)
        self.play(FadeIn(h_a.barras), FadeIn(h_a.linea_umbral),
                  FadeIn(h_a.tag_umbral), FadeIn(h_a.linea_p95),
                  FadeIn(h_a.tag_p95), run_time=1.0)
        self.remove(*h_a.get_family())
        self.add(h_a)
        self.wait(0.8)

        # SEMILLA_DEMO es la misma con la que nacio CAMP: la segunda
        # campaña no se parece, es la MISMA, y el contorno cae clavado.
        rms_b = campana_montecarlo(N_CORRIDAS, semilla=SEMILLA_DEMO)["rms"]
        h_b = histograma(rms_b, bins=26, ancho=6.4, alto=2.4, x_max=PEOR)
        h_b.shift(DESPL)
        contorno = h_b.barras
        contorno.set_fill(opacity=0.0)
        contorno.set_stroke(color=C_OK, width=3.2)
        self.play(Create(contorno), run_time=1.6)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"semilla {SEMILLA_DEMO} identica",
                              color=C_OK), zona="abajo")
        self.wait(2.2)

        # --- el cierre ----------------------------------------------------
        cierre_leccion(self, rot,
                       "La mediana no acepta un sistema",
                       "lo acepta la cola.",
                       h_a, contorno, espera=4.4)
