class Clip1(Scene):
    """6.3.1 - El filtro peine: y[n] = x[n] + 0.85 x[n-8], sus dos golpes
    en h[n] y los tres dientes que produce en la respuesta. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("El peine"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        rot.mostrar(formula_pie(r"y[n] = x[n] + 0.85\,x[n-8]"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- h[n]: dos golpes ----------------------------------------------
        sec = Secuencia(H_PEINE, 0, ancho=9.2, alto=1.7, color=C_MUESTRA,
                        radio=0.05)
        sec.move_to(UP * 1.65)
        et_sec = tag_hud("h[n]", font_size=19, color=C_MUESTRA)
        et_sec.next_to(sec, LEFT, buff=0.28)
        self.play(FadeIn(sec.ejes), FadeIn(et_sec), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i))
                                for i in range(len(H_PEINE))], lag_ratio=0.04),
                  LaggedStart(*[FadeIn(sec.punto(i))
                                for i in range(len(H_PEINE))], lag_ratio=0.04),
                  run_time=1.2)
        self.wait(1.8)

        base_izq = sec.en(0, 0)
        base_der = sec.en(M_PEINE, 0)
        span = Line(base_izq, base_der)
        brace = llave(span, f"M = {M_PEINE}", direccion=DOWN, font_size=20,
                     color=C_CALCULO)
        self.play(FadeIn(brace), run_time=0.6)
        rot.mostrar(cifra_pie(f"M = {M_PEINE}"), zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- la respuesta: tres dientes -------------------------------------
        rf = respuesta_dibujo(W_PEINE, MAG_PEINE, ancho=9.2, alto=2.1,
                              piso_db=MIN_PEINE - 3.0, techo_db=MAX_PEINE + 3.0,
                              color=C_SALIDA)
        rf.move_to(DOWN * 1.15)
        et_rf = tag_hud("|H| dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, LEFT, buff=0.28)
        self.play(FadeOut(brace), FadeIn(rf.ejes), FadeIn(et_rf), run_time=0.6)
        self.play(Create(rf.curva), run_time=1.9)
        self.wait(1.6)

        marcas = VGroup(*[rf.marca_w(d * np.pi) for d in DIENTES])
        puntos = VGroup(*[rf.punto(d * np.pi) for d in DIENTES])
        self.play(LaggedStart(*[FadeIn(m) for m in marcas], lag_ratio=0.3),
                  LaggedStart(*[FadeIn(p) for p in puntos], lag_ratio=0.3),
                  run_time=1.4)
        rot.mostrar(cifra_pie("dientes 0.25 0.50 0.75 pi"), zona="abajo",
                    run_time=0.5)
        self.wait(3.6)

        panel = panel_cifras((f"max {fmt(MAX_PEINE, 2)} dB", C_CALCULO),
                             (f"min {fmt(MIN_PEINE, 2)} dB", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(7.0)
