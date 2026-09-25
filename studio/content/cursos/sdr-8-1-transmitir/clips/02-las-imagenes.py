class Clip2(Scene):
    """8.1.2 - El espectro de salida del DAC, 0 a 3.5 fs: el tono en 0.1 fs
    (ambar) y sus imagenes en k*fs +- 0.1 (rojo), con la envolvente sinc
    teorica (gris) encima, pasando por las puntas: lo medido coincide con
    la teoria. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Las imagenes"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        f_min_img = min(im[1] for im in IMAGENES)
        piso, techo = f_min_img - 5.0, 3.0
        ANCHO, ALTO = 12.0, 4.0

        f_env = np.linspace(0.0, 3.5, 700)
        sinc_ratio = np.abs(np.sinc(f_env)) / np.abs(np.sinc(F0_REL))
        db_env = 20 * np.log10(np.maximum(sinc_ratio, 1e-6))

        esp = S.Espectro(f_env, np.full_like(f_env, piso), piso=piso,
                         techo=techo, ancho=ANCHO, alto=ALTO, color=C_EJE,
                         area=False)
        esp.curva.set_stroke(opacity=0)
        esp.move_to(DOWN * 0.15)
        ticks = esp.marcas([0.0, 1.0, 2.0, 3.0], ["0", "1", "2", "3"])
        u = tag_junto(ticks[-1], "fs", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.wait(0.4)

        # --- el tono, ambar ---------------------------------------------------
        tallo0 = Line(esp.en(F0_REL, piso), esp.en(F0_REL, 0.0), color=C_SENAL,
                     stroke_width=3.4)
        punta0 = Dot(esp.en(F0_REL, 0.0), radius=0.075, color=C_SENAL)
        t_tono = tag_junto(punta0, "tono", UP, buff=0.16, font_size=20,
                           color=C_SENAL)
        self.play(Create(tallo0), FadeIn(punta0), run_time=0.6)
        self.play(FadeIn(t_tono), run_time=0.4)
        self.wait(1.2)

        # --- las imagenes, rojo -------------------------------------------
        tallos, puntas = VGroup(), VGroup()
        for frel, dbc, _teo in IMAGENES:
            tallos.add(Line(esp.en(frel, piso), esp.en(frel, dbc),
                            color=C_RUIDO, stroke_width=3.0))
            puntas.add(Dot(esp.en(frel, dbc), radius=0.06, color=C_RUIDO))
        t_img = tag_junto(puntas[2], "imagenes", UP, buff=0.3, font_size=20,
                          color=C_RUIDO)
        t_img.move_to(esp.en(2.0, -19.0))
        self.play(LaggedStart(*[Create(t) for t in tallos], lag_ratio=0.15),
                  run_time=1.4)
        self.play(FadeIn(puntas), FadeIn(t_img), run_time=0.5)
        self.wait(2.0)

        # --- la envolvente sinc teorica, gris, a trozos (toca piso en k*fs) --
        envolvente = esp.con_db(db_env, color=C_DATO)
        env_trazos = DashedVMobject(envolvente.curva, num_dashes=90,
                                    dashed_ratio=0.55)
        t_env = tag_junto(env_trazos, "envolvente sinc", UP, buff=0.4,
                          font_size=20, color=C_DATO)
        t_env.move_to(esp.en(2.15, techo - 0.35))
        self.play(Create(env_trazos), run_time=1.8)
        self.play(FadeIn(t_env), run_time=0.4)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"imagen: {fmt(IMG_09, 1)} dBc"), zona="abajo",
                    run_time=0.5)
        self.wait(4.5)

        # --- lo medido coincide con la teoria ---------------------------------
        teo_09 = IMAGENES[0][2]
        panel = panel_cifras((f"medido {fmt(IMG_09, 1)} dBc", C_CALCULO),
                             (f"teoria {fmt(teo_09, 1)} dBc", C_DATO))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.5)
        self.play(Indicate(puntas[0], color=C_RUIDO, scale_factor=1.6),
                  Indicate(env_trazos, color=C_DATO, scale_factor=1.02),
                  run_time=1.3)
        self.wait(6.6)
