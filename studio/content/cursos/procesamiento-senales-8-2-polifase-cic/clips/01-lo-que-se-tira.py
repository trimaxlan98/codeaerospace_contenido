class Clip1(Scene):
    """8.2.1 - Filtrar con 61 taps y quedarse con una salida de cada
    cuatro: tres cuartas partes del trabajo van a la basura. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("Lo que se tira"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la forma directa (nueve tomas centrales, para que se vea) ----
        centro = N_TAPS_P // 2
        corto = H_P[centro - 4:centro + 5]
        lr = linea_retardos(corto, ancho=6.6, alto=1.6)
        lr.move_to(LEFT * 0.9 + UP * 1.95)
        partes = VGroup(lr.linea, lr.cajas, lr.tomas, lr.suma, lr.coefs)
        et_lr = tag_hud("h[n]", font_size=19, color=C_MUESTRA)
        et_lr.next_to(lr, LEFT, buff=0.28)

        self.play(Create(lr.linea), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(c) for c in lr.cajas],
                              lag_ratio=0.09), run_time=1.1)
        self.play(LaggedStart(*[Create(t) for t in lr.tomas],
                              lag_ratio=0.07),
                  LaggedStart(*[Create(c) for c in lr.coefs],
                              lag_ratio=0.07), run_time=1.3)
        self.play(Create(lr.suma), FadeIn(et_lr), run_time=0.7)
        rot.mostrar(cifra_pie(f"{N_TAPS_P} taps"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        # --- lo que sale del filtro, muestra a muestra --------------------
        y_todo = filtrar(H_P, (1.0,), X_C)
        vent = y_todo[64:88]
        sec = Secuencia(vent, 0, (-1.25, 1.25), ancho=10.8, alto=1.9,
                        color=C_MUESTRA, radio=0.05)
        sec.move_to(DOWN * 0.75)
        self.play(FadeIn(sec.ejes), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(len(vent))],
                              lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(len(vent))],
                              lag_ratio=0.02), run_time=1.8)
        self.wait(1.4)

        # --- de cada M_DIEZ salidas, solo una sobrevive -------------------
        grupo = VGroup(*[sec.tallo(i) for i in range(M_DIEZ)],
                       *[sec.punto(i) for i in range(M_DIEZ)])
        lla = llave(grupo, f"1 de {M_DIEZ}", direccion=DOWN, font_size=20)
        self.play(Create(lla), run_time=0.8)
        self.wait(2.2)

        guardadas = list(range(0, len(vent), M_DIEZ))
        tiradas = [i for i in range(len(vent)) if i % M_DIEZ]

        self.play(LaggedStart(
            *[sec.tallo(i).animate.set_color(C_SALIDA) for i in guardadas],
            *[sec.punto(i).animate.set_color(C_SALIDA) for i in guardadas],
            lag_ratio=0.05), run_time=1.5)
        rot.mostrar(cifra_pie(f"1 de cada {M_DIEZ} sobrevive"), zona="abajo",
                    run_time=0.5)
        self.wait(2.4)

        self.play(LaggedStart(
            *[sec.tallo(i).animate.set_color(C_RUIDO) for i in tiradas],
            *[sec.punto(i).animate.set_color(C_RUIDO) for i in tiradas],
            lag_ratio=0.02), run_time=1.4)
        rot.mostrar(cifra_pie(f"tira {TIRADAS} de cada {M_DIEZ}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        self.play(*[sec.tallo(i).animate.set_opacity(0.26).shift(DOWN * 0.3)
                    for i in tiradas],
                  *[sec.punto(i).animate.set_opacity(0.26).shift(DOWN * 0.3)
                    for i in tiradas], run_time=1.2)
        self.wait(2.2)

        # --- el precio, contado en multiplicaciones -----------------------
        panel = panel_cifras(f"taps = {N_TAPS_P}",
                             f"M = {M_DIEZ}",
                             (f"macs = {MACS_DIRECTO}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        rot.mostrar(cifra_pie(f"{MACS_DIRECTO} macs por muestra"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        rot.mostrar(formula_pie(r"y[m] = (x \ast h)[M\,m]"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)
