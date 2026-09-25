class Clip3(Scene):
    """8.1.3 - El filtro de reconstruccion (fucsia) deja pasar el tono y
    atenua las imagenes; una mascara espectral esquematica (gris, escalon
    ilustrativo) marca el nivel que el transmisor tiene que respetar lejos
    de la portadora. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La mascara"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        f_min_img = min(im[1] for im in IMAGENES)
        f_max_img = max(im[1] for im in IMAGENES)
        piso, techo = f_min_img - 20.0, 3.0
        ANCHO, ALTO = 12.0, 4.0

        f_env = np.linspace(0.0, 3.5, 700)
        esp = S.Espectro(f_env, np.full_like(f_env, piso), piso=piso,
                         techo=techo, ancho=ANCHO, alto=ALTO, color=C_EJE,
                         area=False)
        esp.curva.set_stroke(opacity=0)
        esp.move_to(DOWN * 0.65)
        ticks = esp.marcas([0.0, 1.0, 2.0, 3.0], ["0", "1", "2", "3"])
        u = tag_junto(ticks[-1], "fs", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.8)
        self.wait(0.4)

        # --- el tono y las imagenes, ya conocidos ----------------------------
        tallo0 = Line(esp.en(F0_REL, piso), esp.en(F0_REL, 0.0), color=C_SENAL,
                     stroke_width=3.4)
        punta0 = Dot(esp.en(F0_REL, 0.0), radius=0.075, color=C_SENAL)
        tallos, puntas = VGroup(), VGroup()
        for frel, dbc, _teo in IMAGENES:
            tallos.add(Line(esp.en(frel, piso), esp.en(frel, dbc),
                            color=C_RUIDO, stroke_width=3.0))
            puntas.add(Dot(esp.en(frel, dbc), radius=0.06, color=C_RUIDO))
        self.play(Create(tallo0), FadeIn(punta0),
                  LaggedStart(*[Create(t) for t in tallos], lag_ratio=0.1),
                  FadeIn(puntas), run_time=1.6)
        self.wait(2.0)

        # --- el filtro de reconstruccion, paso bajo, fucsia -------------------
        f_pass, f_stop = 0.28, 0.6
        h_lin = np.where(
            f_env <= f_pass, 1.0,
            np.where(f_env >= f_stop, 1e-6,
                    0.5 * (1 + np.cos(np.pi * (f_env - f_pass)
                                      / (f_stop - f_pass)))))
        db_filtro = 20 * np.log10(np.maximum(h_lin, 1e-6))
        filtro = esp.con_db(db_filtro, color=C_LO)
        t_filtro = tag_junto(filtro.curva, "filtro", UP, buff=0.18,
                             font_size=20, color=C_LO)
        t_filtro.move_to(esp.en(0.45, -1.0))
        self.play(Create(filtro.curva), run_time=1.8)
        self.play(FadeIn(t_filtro), run_time=0.4)
        self.wait(2.4)

        # --- las imagenes, DESPUES del filtro: mismo roll-off, gemelas -------
        # (el tono no se mueve: cae en la banda de paso, atenuacion ~0 dB)
        nuevos_tallos, nuevos_puntas = VGroup(), VGroup()
        for frel, dbc, _teo in IMAGENES:
            atenuacion = float(np.interp(frel, f_env, db_filtro))
            dbc_filtrado = dbc + atenuacion
            nuevos_tallos.add(Line(esp.en(frel, piso),
                                   esp.en(frel, dbc_filtrado), color=C_RUIDO,
                                   stroke_width=3.0))
            nuevos_puntas.add(Dot(esp.en(frel, dbc_filtrado), radius=0.06,
                                  color=C_RUIDO))
        self.play(*[Transform(tallos[i], nuevos_tallos[i])
                    for i in range(len(IMAGENES))],
                  *[Transform(puntas[i], nuevos_puntas[i])
                    for i in range(len(IMAGENES))], run_time=1.6)
        self.wait(1.6)

        # --- la mascara: escalon ilustrativo, gris --------------------------
        # (mask_far entre la imagen mas alta ANTES del filtro y el piso: la
        # violan antes de filtrar y quedan debajo despues, sin numeros reales)
        f_esc = 0.75
        mask_near = techo - 0.6
        mask_far = (f_max_img + piso) / 2.0
        p1 = esp.en(0.0, mask_near)
        p2 = esp.en(f_esc, mask_near)
        p3 = esp.en(f_esc, mask_far)
        p4 = esp.en(3.5, mask_far)
        mask_line = VMobject(stroke_color=C_DATO, stroke_width=2.4)
        mask_line.set_points_as_corners([p1, p2, p3, p4])
        mask_trazos = DashedVMobject(mask_line, num_dashes=40,
                                     dashed_ratio=0.55)
        t_mask = tag_dato("mascara", font_size=19)
        t_mask.next_to(p2, UP, buff=0.16)
        self.play(Create(mask_trazos), run_time=1.2)
        self.play(FadeIn(t_mask), run_time=0.4)
        self.wait(3.0)

        rot.mostrar(dato_pie("escala ilustrativa"), zona="abajo",
                    run_time=0.5)
        self.wait(8.0)

        self.play(Indicate(filtro.curva, color=C_LO, scale_factor=1.02),
                  Indicate(mask_trazos, color=C_DATO, scale_factor=1.02),
                  run_time=1.3)
        self.wait(8.0)
