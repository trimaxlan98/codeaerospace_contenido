class Clip3(Scene):
    """4.3.3 - Dos filtros con el MISMO |H| y distinta fase: reflejar el
    cero de fuera adelanta la energia y aplana el retardo. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("El mismo modulo, otra fase"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- el plano: un cero dentro y otro FUERA -------------------------
        pz = plano_z(CEROS_NOMIN, [], unidad=1.05, alcance=2.35)
        pz.move_to(LEFT * 3.55 + DOWN * 0.35)
        et_re = tag_hud("Re", font_size=17, color=C_TENUE)
        et_re.move_to(pz.en(-2.15) + DOWN * 0.28)
        self.play(FadeIn(pz.ejes), FadeIn(et_re), run_time=0.5)
        self.play(Create(pz.circulo), run_time=1.3)
        self.play(FadeIn(pz.ceros[0], scale=0.5),
                  FadeIn(pz.ceros[1], scale=0.5), run_time=0.7)
        p_bajo = pz.en(CEROS_NOMIN[0]) + DOWN * 1.62
        et_dentro = _con_fondo(tag_hud("cero dentro", font_size=18,
                                       color=C_SALIDA).move_to(p_bajo))
        et_fuera = tag_hud("cero fuera", font_size=18, color=C_RUIDO)
        et_fuera.next_to(pz.en(CEROS_NOMIN[1]), UP, buff=0.22)
        self.play(FadeIn(et_dentro), FadeIn(et_fuera), run_time=0.6)
        self.wait(2.2)

        # --- su modulo -----------------------------------------------------
        mag = respuesta_dibujo(W_N, MAG_NOMIN, ancho=4.9, alto=2.1,
                               piso_db=-9.0, techo_db=15.0, color=C_RUIDO)
        mag.move_to(RIGHT * 3.45 + DOWN * 0.55)
        et_mag = tag_hud("|H| dB", font_size=18, color=C_TENUE)
        et_mag.next_to(mag, UP, buff=0.20)
        self.play(FadeIn(mag.ejes), FadeIn(et_mag), run_time=0.5)
        self.play(Create(mag.curva), run_time=1.8)
        self.wait(2.0)

        # --- reflejar el cero de fuera: el modulo NO se entera --------------
        fantasma = DashedVMobject(mag.curva.copy(), num_dashes=46)
        fantasma.set_stroke(C_RUIDO, width=3.4, opacity=1.0)
        gemela_pz = pz.con_pz(np.roots(B_MIN), [])
        gemela_mag = mag.con_mag(MAG_MIN, color=C_SALIDA)
        et_doble = _con_fondo(tag_hud("cero doble en 0.5", font_size=18,
                                      color=C_SALIDA).move_to(p_bajo))
        self.play(FadeOut(et_fuera), FadeOut(et_dentro), run_time=0.4)
        self.add(fantasma)
        self.play(Transform(pz, gemela_pz),
                  Transform(mag.curva, gemela_mag.curva), run_time=1.8)
        self.play(FadeIn(et_doble), run_time=0.4)
        rot.mostrar(cifra_pie(f"diferencia = {DIF_MAG:.1e} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        # --- pero la energia se reparte distinto ---------------------------
        self.play(FadeOut(pz), FadeOut(et_re), FadeOut(et_doble),
                  FadeOut(mag), FadeOut(fantasma), FadeOut(et_mag),
                  run_time=0.7)

        rango = (-2.8, 2.4)
        s_no = Secuencia(H_NOMIN, 0, rango, ancho=5.4, alto=1.6,
                         color=C_RUIDO)
        s_no.move_to(UP * 1.35)
        s_mi = Secuencia(H_MIN, 0, rango, ancho=5.4, alto=1.6,
                         color=C_SALIDA)
        s_mi.move_to(DOWN * 0.85)
        et_no = tag_hud("no minima", font_size=18, color=C_RUIDO)
        et_no.next_to(s_no, LEFT, buff=0.26)
        et_mi = tag_hud("fase minima", font_size=18, color=C_SALIDA)
        et_mi.next_to(s_mi, LEFT, buff=0.26)
        self.play(FadeIn(s_no), FadeIn(et_no), run_time=0.8)
        self.play(FadeIn(s_mi), FadeIn(et_mi), run_time=0.8)
        self.wait(2.0)

        marca_no = s_no.marcar(0, color=C_CALCULO)
        marca_mi = s_mi.marcar(0, color=C_CALCULO)
        self.play(Create(marca_no), Create(marca_mi), run_time=0.7)
        panel = panel_cifras((f"primera {fmt(ENERGIA_NOMIN, 1)} %", C_RUIDO),
                             (f"primera {fmt(ENERGIA_MIN, 1)} %", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(4.0)

        rot.mostrar(cifra_pie(f"retardo medio {fmt(GD_NOMIN, 3)} y "
                              f"{fmt(GD_MIN2, 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(5.4)
