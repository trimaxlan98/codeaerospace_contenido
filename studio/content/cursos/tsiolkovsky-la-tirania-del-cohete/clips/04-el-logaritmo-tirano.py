class Clip4(Scene):
    """4 - El logaritmo tirano. La curva m0/mf = e^(dv/ve): suave al
    arranque, vertical al final. Marcadores de orbita y LEO, y las tres
    quimicas (RP-1, promedio, hidrolox) leidas sobre la MISMA vertical de
    LEO: mismo viaje, tres precios. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El logaritmo tirano")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la curva de la tirania --------------------------------
        rot.mostrar(pie_curso("La curva de la tiranía: cuánto cohete "
                              "cuesta cada kilómetro por segundo."),
                    zona="abajo", run_time=0.5)
        # sin .scale(): `con_ve` reconstruye a tamano de constructor
        curva = curva_tirania()
        curva.shift(UP * 0.3 + LEFT * 0.45)

        eje_x = curva.ejes[0]
        eje_y = curva.ejes[1]
        etiq_x = MathTex(r"\Delta v", font_size=26, color=C_TENUE)
        etiq_x.next_to(eje_x, RIGHT, buff=0.18)
        etiq_y = MathTex(r"m_0/m_f", font_size=26, color=C_TENUE)
        etiq_y.next_to(eje_y, UP, buff=0.18)
        self.play(Create(eje_x), Create(eje_y), run_time=0.8)
        self.play(Create(curva.curva), FadeIn(etiq_x), FadeIn(etiq_y),
                  run_time=1.8)
        self.wait(2.2)

        # --- momento: orbita y LEO sobre la curva ---------------------------
        rot.mostrar(pie_curso(f"A {DV_LEO_KMS:.2f} km/s el cohete pesa "
                              f"×{RAZON_QUIMICO:.1f}: cada km/s no suma, "
                              "multiplica."), zona="abajo", run_time=0.5)
        y_eje = eje_x.get_center()[1]

        p_orb = curva.en(V_ORB_KMS * 1000.0)
        d_orb = Dot(p_orb, radius=0.07, color=C_TIERRA)
        guia_orb = DashedLine(np.array([p_orb[0], y_eje, 0.0]), p_orb,
                              dash_length=0.09, stroke_width=1.8,
                              color=C_TIERRA)
        guia_orb.set_stroke(opacity=0.55)
        t_orb = tag_hud(f"órbita: {V_ORB_KMS:.2f} km/s", font_size=16,
                        color=C_TIERRA)
        t_orb.next_to(np.array([p_orb[0], y_eje, 0.0]), DOWN, buff=0.28)
        self.play(Create(guia_orb), FadeIn(d_orb, scale=0.4),
                  FadeIn(t_orb, shift=0.12 * DOWN), run_time=0.7)
        self.wait(1.6)

        p_leo = curva.en(DV_LEO)
        d_leo = Dot(p_leo, radius=0.075, color=C_CARGA)
        t_leo = tag_hud(f"LEO: ×{RAZON_QUIMICO:.1f}", font_size=18,
                        color=C_CARGA)
        t_leo.next_to(d_leo, RIGHT, buff=0.20)
        self.play(FadeIn(d_leo, scale=0.4),
                  FadeIn(t_leo, shift=0.12 * RIGHT), run_time=0.7)
        self.wait(2.6)

        # --- momento: la misma vertical, tres quimicas ----------------------
        rot.mostrar(pie_curso("¿Y si cambias de química? La misma cuenta, "
                              "otra pendiente."), zona="abajo",
                    run_time=0.5)
        guia_leo = DashedLine(np.array([p_leo[0], y_eje, 0.0]),
                              np.array([p_leo[0], y_eje + 3.04, 0.0]),
                              dash_length=0.09, stroke_width=1.6,
                              color=C_EJE)
        self.play(Create(guia_leo), run_time=0.5)

        # `con_ve` conserva el rango y: la comparacion es honesta
        rp1 = curva.con_ve(VE_RP1)
        rp1.curva.set_stroke(color=C_MUERTO, width=2.6)
        p_rp1 = rp1.en(DV_LEO)
        d_rp1 = Dot(p_rp1, radius=0.07, color=C_MUERTO)
        t_rp1 = tag_hud(f"RP-1: ×{RAZON_RP1:.1f}", font_size=17,
                        color=C_MUERTO)
        # arriba del techo de la caja: ahi no pasa ninguna curva
        t_rp1.next_to(d_rp1, RIGHT, buff=0.20).shift(UP * 0.34)
        self.play(Create(rp1.curva), run_time=1.2)
        self.play(FadeIn(d_rp1, scale=0.4), FadeIn(t_rp1), run_time=0.6)
        self.wait(1.4)

        hid = curva.con_ve(VE_HIDROLOX)
        hid.curva.set_stroke(color=C_ESTRUCTURA, width=2.6)
        p_hid = hid.en(DV_LEO)
        d_hid = Dot(p_hid, radius=0.07, color=C_ESTRUCTURA)
        t_hid = tag_hud(f"hidrolox: ×{RAZON_HIDROLOX:.1f}", font_size=17,
                        color=C_ESTRUCTURA)
        t_hid.next_to(d_hid, RIGHT, buff=0.20).shift(DOWN * 0.45)
        self.play(Create(hid.curva), run_time=1.2)
        self.play(FadeIn(d_hid, scale=0.4), FadeIn(t_hid), run_time=0.6)
        self.wait(1.6)

        # --- momento: el mismo viaje, tres precios --------------------------
        rot.mostrar(pie_curso(f"El mismo viaje cuesta ×{RAZON_RP1:.1f} con "
                              f"queroseno y ×{RAZON_HIDROLOX:.1f} con "
                              "hidrógeno."), zona="abajo", run_time=0.5)
        self.play(Indicate(t_rp1, color=C_MUERTO, scale_factor=1.14),
                  Indicate(t_hid, color=C_ESTRUCTURA, scale_factor=1.14),
                  run_time=0.9)
        self.wait(4.0)

        # --- momento: la tesis ----------------------------------------------
        rot.mostrar(pie_curso("La tiranía tiene nombre y es viejo: "
                              "exponencial."), zona="abajo", run_time=0.5)
        self.wait(5.0)
