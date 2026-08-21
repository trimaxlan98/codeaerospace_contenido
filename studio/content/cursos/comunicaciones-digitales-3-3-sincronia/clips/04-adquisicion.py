class Clip4(Scene):
    """3.3.4 - Adquisicion: con el instante cero hallado se abren los
    relojes de simbolo y las decisiones caen en el centro del ojo.
    Cierre de leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Adquisición: el reloj se engancha")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el instante cero del receptor -----------------------
        rot.mostrar(pie_curso("El máximo no era un número suelto: es el "
                              "instante cero del receptor."),
                    zona="abajo", run_time=0.5)
        on = onda(T_RX, RX, rango_y=(-3.3, 3.3), ancho=10.6, alto=2.0)
        on.move_to(UP * 1.5)
        on.curva.set_stroke(opacity=0.55)
        paso = float(on.en(1.0, 0.0)[0] - on.en(0.0, 0.0)[0])
        marco = Rectangle(width=N_CHIPS * paso, height=on.alto,
                          color=C_BIT, stroke_width=1.8)
        marco.set_fill(C_BIT, opacity=0.12)
        marco.move_to(on.en(OFFSET_HALLADO + (N_CHIPS - 1) / 2.0, 0.0))
        et_pre = tag_junto(marco, "preámbulo", direccion=UP, buff=0.08)
        v_ini = on.vertical_en(float(OFFSET_HALLADO), color=C_CIFRA)
        v_dat = on.vertical_en(float(INICIO_DATOS), color=C_COD)
        self.play(FadeIn(on), run_time=0.7)
        self.play(FadeIn(marco), FadeIn(et_pre), Create(v_ini),
                  run_time=0.9)
        et_ini = tag_hud(f"inicio = {OFFSET_HALLADO}", font_size=20)
        et_ini.next_to(on.en(float(OFFSET_HALLADO), -3.3), DOWN, buff=0.12)
        self.play(FadeIn(et_ini), run_time=0.5)
        self.wait(3.2)

        # --- momento: tras 31 chips empiezan los datos --------------------
        rot.mostrar(pie_curso("Tras los 31 chips del preámbulo empiezan "
                              "los datos: muestra 71."),
                    zona="abajo", run_time=0.5)
        et_dat = tag_hud(f"datos desde {INICIO_DATOS}", font_size=20,
                         color=C_COD)
        et_dat.next_to(on.en(float(INICIO_DATOS), -3.3), DOWN, buff=0.12)
        self.play(Create(v_dat), FadeIn(et_dat), run_time=0.8)
        self.wait(4.0)

        # --- momento: los relojes de simbolo se abren ---------------------
        rot.mostrar(pie_curso("Contando desde ahí, el receptor abre su "
                              "reloj: un instante de decisión por símbolo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(on, marco, et_pre, v_ini, v_dat, et_ini,
                                 et_dat)), run_time=0.6)
        on_d = onda(T_DATOS, Y_DATOS, rango_y=(-1.9, 1.9), ancho=9.6,
                    alto=1.9)
        on_d.move_to(UP * 1.7)
        relojes = VGroup(*[on_d.vertical_en(float(k), color=C_CIFRA)
                           for k in range(N_SIMB)])
        relojes.set_stroke(opacity=0.5, width=1.2)
        puntos = VGroup(*[Dot(on_d.en(float(k), float(Y_DECISION[k])),
                              radius=0.055, color=C_BIT)
                          for k in range(N_SIMB)])
        self.play(FadeIn(on_d), run_time=0.7)
        self.play(LaggedStart(*[Create(r) for r in relojes],
                              lag_ratio=0.05), run_time=1.6)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in puntos],
                              lag_ratio=0.05), run_time=1.2)
        self.wait(2.0)

        # --- momento: el centro del ojo (1.2) -----------------------------
        rot.mostrar(pie_curso("Superponiendo los símbolos: cada decisión "
                              "cae en el centro del ojo de la lección 1.2."),
                    zona="abajo", run_time=0.5)
        ojo = diagrama_ojo(Y_DATOS, sps=SPS, n_trazas=16, ancho=4.4,
                           alto=2.2)
        ojo.move_to(LEFT * 2.9 + DOWN * 1.15)
        d_up = Dot(ojo._en(0.5, 1.0), radius=0.06, color=C_BIT)
        d_dn = Dot(ojo._en(0.5, -1.0), radius=0.06, color=C_BIT)
        et_ojo = tag_junto(ojo, "el instante de decisión", direccion=DOWN,
                           buff=0.14)
        cifras = VGroup(
            tag_hud(f"T = 1 simbolo = {SPS} muestras", font_size=20),
            tag_hud(f"simbolos leidos = {N_SIMB}", font_size=20),
            tag_hud(f"apertura medida = {fmt(APERTURA, 2)}", font_size=21),
        ).arrange(DOWN, buff=0.2, aligned_edge=LEFT)
        cifras.move_to(RIGHT * 1.1 + DOWN * 1.15, aligned_edge=LEFT)
        self.play(FadeIn(ojo), FadeIn(et_ojo), run_time=0.9)
        self.play(FadeIn(d_up), FadeIn(d_dn), FadeIn(cifras), run_time=0.7)
        self.wait(3.6)

        # --- momento: la frecuencia (3.2) y el instante (3.3) -------------
        rot.mostrar(pie_curso("La lección 3.2 corrigió la frecuencia; "
                              "ésta fija el instante. El enlace ya escucha."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "Oír no es lo difícil.",
            "Lo difícil es saber cuándo empezó la frase.",
            "Siguiente módulo: códigos que recuerdan lo que dijeron.",
            on_d, relojes, puntos, ojo, d_up, d_dn, et_ojo, cifras)
