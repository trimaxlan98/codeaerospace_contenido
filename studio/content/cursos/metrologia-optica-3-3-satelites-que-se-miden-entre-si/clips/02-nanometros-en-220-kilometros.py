class Clip2(Scene):
    """2 - Nanometros en 220 kilometros. El LRI de GRACE-FO manda un haz al
    otro satelite y lee la fase que vuelve: cada franja vale lambda/2 =
    775 nm y contandolas se sigue la separacion al nanometro. 1 nm en 220
    km son 4.5e-15, cuatro partes en mil billones. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Nanómetros en 220 kilómetros"),
                    zona="arriba", run_time=0.6)

        # 6.60 x 3.66 tal cual, centrado en y = -0.35: banda -2.18 .. +1.48.
        lri = interferometro_espacial(fase=0.0)
        lri.move_to(DOWN * 0.35)

        # El esquema se arma por partes: primero los satelites y el haz,
        # despues el detector y la senal. `.ejes` es VGroup(ejes, cable,
        # tallo): el tallo del laser se queda desde el principio.
        ejes_curva, cable = lri.ejes[0], lri.ejes[1]
        lri.remove(lri.rotulo)          # sus dos cifras salen por tags propios
        lri.ejes.remove(ejes_curva, cable)
        lri.remove(lri.detector, lri.franjas, lri.senal, lri.marcador,
                   lri.ida, lri.vuelta)

        def girar(desde, hasta, t):
            """Avanza la fase de la senal (radianes)."""
            self.play(UpdateFromAlphaFunc(
                lri, lambda m, a: m.a_fase(desde + (hasta - desde) * a)),
                run_time=t, rate_func=linear)

        # --- momento: el haz va y vuelve -------------------------------
        rot.mostrar(pie_curso("El instrumento láser LRI manda un haz al otro "
                              "satélite y compara la fase que vuelve."),
                    zona="abajo")
        self.play(FadeIn(lri, shift=0.12 * UP), run_time=0.9)
        lri.add(lri.ida)
        self.play(Create(lri.ida), run_time=1.0)
        lri.add(lri.vuelta)
        self.play(Create(lri.vuelta), run_time=0.9)
        self.wait(2.6)

        # --- momento: cada franja vale lambda/2 ------------------------
        rot.mostrar(pie_curso("Cada franja vuelve a ser media longitud de "
                              "onda: los cambios se ven en nanómetros."),
                    zona="abajo")
        lri.ejes.add(cable)
        lri.add(lri.detector, lri.franjas)
        self.play(FadeIn(cable), FadeIn(lri.detector), FadeIn(lri.franjas),
                  run_time=0.8)
        lri.ejes.add(ejes_curva)
        lri.add(lri.senal, lri.marcador)
        self.play(Create(ejes_curva), run_time=0.7)
        self.play(Create(lri.senal), FadeIn(lri.marcador), run_time=1.1)
        # Columna izquierda: los tags se alinean por su borde DERECHO en
        # x = -3.15, medio metro a la izquierda de lo mas saliente del
        # esquema a esa altura (el telescopio laser, en x = -2.64).
        t_franja = tag_hud(
            f"1 franja = lambda/2 = {paso_franja(LAMBDA_ISL) * 1e9:.0f} nm",
            font_size=14, color=C_FRANJA)
        t_franja.move_to(np.array([-3.15, 0.42, 0.0]), aligned_edge=RIGHT)
        self.play(FadeIn(t_franja), run_time=0.5)
        girar(0.0, 3.0 * TAU, 4.2)
        self.wait(1.2)

        # --- momento: la cifra -----------------------------------------
        rot.mostrar(pie_curso("Un nanómetro en 220 kilómetros: cuatro partes "
                              "en mil billones."), zona="abajo")
        self.play(FadeOut(t_franja), run_time=0.35)
        cifras = VGroup(
            tag_hud(f"1 nm / {SEP_GRACE_KM:.0f} km = {SENS_GRACE:.1e}",
                    font_size=15, color=C_MEDIDA),
            tag_hud("orden de magnitud", font_size=13, color=C_TENUE),
            tag_hud(f"luz: {T_GRACE_MS:.2f} ms", font_size=13, color=C_TENUE),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        cifras.move_to(np.array([-3.15, 0.30, 0.0]), aligned_edge=RIGHT)
        self.play(FadeIn(cifras), run_time=0.6)
        girar(3.0 * TAU, 4.6 * TAU, 2.6)
        self.wait(2.4)

        # --- cierre ----------------------------------------------------
        rot.mostrar(pie_curso("La regla más fina del taller, tendida entre "
                              "dos satélites."), zona="abajo")
        girar(4.6 * TAU, 5.4 * TAU, 2.8)
        self.wait(5.0)
