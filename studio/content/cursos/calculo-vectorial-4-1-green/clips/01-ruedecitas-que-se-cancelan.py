class Clip1(Scene):
    """4.1.1 - La region embaldosada: cada baldosa tiene su circulacion, y
    el lado que comparten dos vecinas se recorre dos veces en sentidos
    opuestos, asi que se cancela. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Ruedecitas que se cancelan")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el campo llena el plano -----------------------------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Un campo llena el plano. Queremos saber "
                              "cuánto GIRA dentro de una región."),
                    zona="abajo", run_time=0.5)
        campo = campo_flechas(pl, F_GREEN, paso=1.0, escala=0.55,
                              x0=-2.5, x1=2.5, y0=-1.5, y1=1.5)
        self.play(LaggedStart(*[FadeIn(f, scale=0.5) for f in campo.flechas],
                              lag_ratio=0.05), run_time=1.6)
        self.wait(3.4)

        # --- momento: la region y su ruedecita ----------------------------
        rot.mostrar(pie_curso("Esta región naranja. Una ruedecita puesta "
                              "dentro gira sola: ese giro es el rotacional."),
                    zona="abajo", run_time=0.5)
        reg = region_rect(pl, X0, X1, Y0, Y1, flechas=0)
        self.play(campo.animate.fade(0.62), FadeIn(reg.relleno),
                  Create(reg.borde), run_time=1.0)
        rd = rueda(pl, (0.0, 0.0), radio=0.30)
        etiqueta = _con_fondo(tag_hud(f"rot F = {fmt(ROT_G)}",
                                      font_size=19), buff=0.11)
        etiqueta.next_to(rd, UP, buff=0.18)
        self.play(FadeIn(rd, scale=0.6), FadeIn(etiqueta), run_time=0.6)
        self.play(Rotate(rd.aspas, angle=ROT_G / 2 * 3.0,
                         about_point=rd.centro()),
                  run_time=3.0, rate_func=linear)
        self.wait(1.6)

        # --- momento: el mosaico de baldosas ------------------------------
        rot.mostrar(pie_curso("Partamos la región en baldosas. Cada una "
                              "lleva su propia circulación antihoraria."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(rd), FadeOut(etiqueta), FadeOut(reg.relleno),
                  FadeOut(reg.borde), run_time=0.6)
        mos = mosaico_circulaciones(pl, X0, X1, Y0, Y1, nx=NX, ny=NY,
                                    margen=MARGEN_BALDOSA)
        self.play(LaggedStart(*[FadeIn(b, scale=0.7) for b in mos],
                              lag_ratio=0.14), run_time=2.2)
        self.wait(3.0)

        # --- momento: dos vecinas y su lado compartido --------------------
        rot.mostrar(pie_curso("Miremos dos vecinas. El lado que comparten "
                              "lo recorren LAS DOS."), zona="abajo",
                    run_time=0.5)
        i_izq, i_der = 1 * NX + 0, 1 * NX + 1
        otras = [b for k, b in enumerate(mos) if k not in (i_izq, i_der)]
        self.play(*[b.animate.fade(0.86) for b in otras], run_time=0.8)
        rd1 = rueda(pl, CENTRO_B_IZQ, radio=0.18)
        rd2 = rueda(pl, CENTRO_B_DER, radio=0.18)
        self.play(FadeIn(rd1, scale=0.6), FadeIn(rd2, scale=0.6),
                  run_time=0.5)
        self.play(Rotate(rd1.aspas, angle=ROT_G / 2 * 2.2,
                         about_point=rd1.centro()),
                  Rotate(rd2.aspas, angle=ROT_G / 2 * 2.2,
                         about_point=rd2.centro()),
                  run_time=2.2, rate_func=linear)
        self.wait(1.4)
        # Las separo: el pasillo entre baldosas mide 0.27 u de pantalla y
        # las dos flechitas del lado compartido no caben legibles ahi.
        self.play(VGroup(mos[i_izq], rd1).animate.shift(LEFT * 0.55),
                  VGroup(mos[i_der], rd2).animate.shift(RIGHT * 0.55),
                  run_time=0.7)

        # --- momento: las dos flechitas y sus cifras ----------------------
        rot.mostrar(pie_curso("La de la izquierda lo sube; la de la derecha "
                              "lo baja. Mismo tramo, sentidos opuestos."),
                    zona="abajo", run_time=0.5)
        d = 0.11
        sube = flecha_libre(pl, (X_COMPARTIDO - d, Y_COMP_A),
                            (X_COMPARTIDO - d, Y_COMP_B),
                            color=C_REGION, grosor=6.0, punta_len=0.18)
        baja = flecha_libre(pl, (X_COMPARTIDO + d, Y_COMP_B),
                            (X_COMPARTIDO + d, Y_COMP_A),
                            color=C_REGION, grosor=6.0, punta_len=0.18)
        par = VGroup(sube, baja)
        self.play(GrowArrow(sube), GrowArrow(baja), run_time=0.9)
        libro = panel_derecha(
            tag_hud(f"sube  {fmt(W_IZQ, 2)}", font_size=20, color=C_REGION),
            tag_hud(f"baja  {fmt(W_DER, 2)}", font_size=20, color=C_REGION),
            tag_hud(f"suma  {fmt(W_PAR, 2)}", font_size=22, color=C_RES),
            buff=0.22)
        self.play(FadeIn(libro, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.2)

        # --- momento: el par se borra -------------------------------------
        rot.mostrar(pie_curso("Suman cero: se borran. Y eso le pasa a TODO "
                              "tramo interior."), zona="abajo", run_time=0.5)
        self.play(Indicate(par, color=C_RES, scale_factor=1.04),
                  run_time=0.9)
        self.play(FadeOut(par, scale=0.4), run_time=0.7)
        self.wait(3.4)
