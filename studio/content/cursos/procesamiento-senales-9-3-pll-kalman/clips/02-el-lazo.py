class Clip2(Scene):
    """9.3.2 - El detector de fase mide el angulo, el filtro lo integra
    y corrige el NCO: un lazo. ERR_PLL cae y se queda en ERR_RMS_PLL tras
    N_ENGANCHE muestras (medido DESPUES de enganchar). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 09"))
        rot.mostrar(titulo_curso("El lazo"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el diagrama del lazo, arriba -----------------------------
        det = bloque("Detector", ancho=2.1, alto=0.68, color=C_DATO,
                     color_texto=C_DATO, tamano=19)
        filt = bloque("Filtro", ancho=2.1, alto=0.68, color=C_DATO,
                      color_texto=C_DATO, tamano=19)
        nco = bloque("NCO", ancho=2.1, alto=0.68, color=C_DATO,
                     color_texto=C_DATO, tamano=19)
        fila = VGroup(det, filt, nco).arrange(RIGHT, buff=1.0)
        fila.to_edge(UP, buff=1.35)
        c1 = conectar(det, filt, color=C_DATO, grosor=2.2)
        c2 = conectar(filt, nco, color=C_DATO, grosor=2.2)
        realim = ArcBetweenPoints(nco.get_bottom(), det.get_bottom(),
                                  angle=-TAU / 5, color=C_TENUE,
                                  stroke_width=2.2)
        realim.add_tip(tip_length=0.14)
        et_realim = tag_hud("realimentacion", font_size=16, color=C_TENUE)
        et_realim.next_to(realim, DOWN, buff=0.10)
        self.play(LaggedStart(*[FadeIn(b) for b in (det, filt, nco)],
                              lag_ratio=0.2), run_time=1.0)
        self.play(Create(c1), Create(c2), Create(realim), run_time=0.9)
        self.play(FadeIn(et_realim), run_time=0.4)
        self.wait(0.5)
        self.play(flujo([c1, c2, realim], color=C_CALCULO, ancho=6,
                        por_conexion=0.5), run_time=1.6)
        self.wait(0.6)

        # --- el error de fase, cayendo hasta engancharse ----------------
        idx = np.arange(N_PLL)
        margen_err = float(np.max(np.abs(ERR_PLL))) * 1.15
        rf = respuesta_dibujo(idx, ERR_PLL, ancho=10.2, alto=2.6,
                              piso_db=-margen_err, techo_db=margen_err,
                              color=C_CALCULO)
        rf.move_to(DOWN * 1.85)
        self.play(FadeIn(rf.ejes), Create(rf.curva), run_time=2.0)
        et_err = tag_hud("err fase", font_size=18, color=C_CALCULO)
        et_err.next_to(rf, LEFT, buff=0.22)
        self.play(FadeIn(et_err), run_time=0.4)
        self.wait(1.0)

        marca = rf.marca_w(N_ENGANCHE, color=C_TENUE)
        rot.mostrar(cifra_pie(f"enganche en {N_ENGANCHE}"), zona="abajo",
                    run_time=0.5)
        self.play(Create(marca), run_time=0.6)
        self.wait(1.4)

        linea_rms = DashedLine(rf.en(N_ENGANCHE, ERR_RMS_PLL),
                               rf.en(N_PLL - 1, ERR_RMS_PLL),
                               color=C_RUIDO, stroke_width=2.2,
                               dash_length=0.08)
        self.play(Create(linea_rms), run_time=0.9)
        rot.mostrar(cifra_pie(f"tras enganche {fmt(ERR_RMS_PLL, 3)} rad"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        panel = panel_cifras((f"kp {fmt(KP, 3)}", C_MUESTRA),
                             (f"ki {fmt(KI, 3)}", C_MUESTRA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)

        rot.mostrar(formula_pie(r"\varphi_{k+1} = \varphi_k + 2\pi f_k "
                                r"+ k_p\,e_k"), zona="abajo", run_time=0.5)
        self.wait(8.5)
