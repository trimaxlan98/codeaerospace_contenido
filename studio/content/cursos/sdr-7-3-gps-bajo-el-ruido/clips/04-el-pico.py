class Clip4(Scene):
    """7.3.4 - El pico de la rejilla en (2.5 kHz, fase); su fila como perfil
    (dB sobre la media) junto a la mejor fila buscando OTRO satelite (PRN
    3), en la MISMA escala: 13 dB contra 4.5. Cierre. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El pico"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        GRUPO = 22
        n_f, n_j = REJ.shape
        red = REJ.reshape(n_f, n_j // GRUPO, GRUPO).max(axis=2)
        mapa_db = 10 * np.log10(red / REJ.mean())
        TECHO = float(mapa_db.max())

        MX0, MX1, MY_T, MY_B = -5.3, 5.3, 2.5, -1.75
        W, H = MX1 - MX0, MY_T - MY_B
        h_f = H / n_f

        def y_fila(i):
            return MY_B + (i + 0.5) * h_f

        def x_chip(ch):
            return MX0 + (2 * ch / n_j) * W

        # --- el mapa de la leccion anterior, entero -------------------------
        mapa = S.waterfall(mapa_db[::-1], ancho=W, alto=H, piso=0.0,
                           techo=TECHO)
        mapa.set_resampling_algorithm(RESAMPLING_ALGORITHMS["nearest"])
        mapa.move_to([(MX0 + MX1) / 2, (MY_T + MY_B) / 2, 0])
        marco = Rectangle(width=W, height=H, stroke_color=C_EJE,
                          stroke_width=1.4).move_to(mapa)
        t_dop = VGroup()
        for fd in (-5000.0, 0.0, 5000.0):
            i = int(np.argmin(np.abs(DOPS - fd)))
            t = tag_hud(f"{fd / 1e3:+.0f}" if fd else "0", font_size=19,
                        color=C_TENUE)
            t.move_to([MX0 - 0.38, y_fila(i), 0])
            t_dop.add(t)
        u_k = tag_hud("kHz", font_size=19, color=C_TENUE)
        u_k.move_to([MX0 - 0.38, MY_T + 0.3, 0])
        t_ch = VGroup()
        for ch in (0, 250, 500, 750, 1000):
            p = np.array([x_chip(ch), MY_B, 0])
            t_ch.add(Line(p, p + DOWN * 0.1, color=C_EJE, stroke_width=1.6))
            t = tag_hud(f"{ch}", font_size=19, color=C_TENUE)
            t.next_to(p, DOWN, buff=0.16)
            t_ch.add(t)
        u_c = tag_junto(t_ch[-1], "chips", DOWN, buff=0.1, font_size=20)
        ejes_mapa = VGroup(marco, t_dop, u_k, t_ch, u_c)
        self.play(FadeIn(mapa), FadeIn(ejes_mapa), run_time=1.0)
        self.wait(1.4)

        # --- el pico -------------------------------------------------------
        CH_PICO = J_F / 2.0
        p_pico = np.array([x_chip(CH_PICO), y_fila(I_D), 0])
        aro = Circle(radius=0.34, stroke_color=C_CALCULO, stroke_width=3.0)
        aro.move_to(p_pico)
        t_f = tag_hud(f"{DOPS[I_D] / 1e3:.1f} kHz", font_size=22)
        t_p = tag_hud(f"{CH_PICO:.0f} chips", font_size=22)
        t_pk = VGroup(t_f, t_p).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        t_pk.next_to(aro, RIGHT, buff=0.2)
        t_pk = _con_fondo(t_pk, buff=0.1)
        self.play(Create(aro), run_time=0.7)
        self.play(FadeIn(t_pk), run_time=0.5)
        rot.mostrar(cifra_pie(f"{DOPS[I_D] / 1e3:.1f} kHz y "
                              f"{CH_PICO:.0f} chips"),
                    zona="abajo", run_time=0.5)
        self.wait(3.2)

        # --- la fila del pico, como perfil --------------------------------
        cur_fila = Rectangle(width=W + 0.08, height=h_f + 0.04,
                             stroke_color=C_LO, stroke_width=3.0)
        cur_fila.move_to([(MX0 + MX1) / 2, y_fila(I_D), 0])
        self.play(Create(cur_fila), run_time=0.6)
        self.wait(1.0)
        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(FadeOut(mapa), FadeOut(ejes_mapa), FadeOut(aro),
                  FadeOut(t_pk), FadeOut(cur_fila), run_time=0.8)

        P_LO, P_HI = -7.0, float(np.ceil(PICO_DB)) + 1.5
        chips = np.arange(n_j) / 2.0
        f7 = 10 * np.log10(REJ[I_D] / REJ.mean())
        i3 = int(np.unravel_index(np.argmax(_R3), _R3.shape)[0])
        f3 = 10 * np.log10(_R3[i3] / _R3.mean())
        k3 = int(np.argmax(f3))
        # sin reducir: el maximo por columna subiria el suelo sobre la media
        c7, d7 = chips, f7
        c3, d3 = chips, f3
        ANCHO_P, ALTO_P = 5.0, 4.0
        C_IZQ = np.array([-2.95, 0.2, 0])
        C_DER = np.array([3.35, 0.2, 0])
        pa = S.Espectro(c7, d7, piso=P_LO, techo=P_HI, ancho=ANCHO_P,
                        alto=ALTO_P, color=C_SENAL, area=False, grosor=1.4)
        pa.shift(C_IZQ)
        pb = S.Espectro(c3, d3, piso=P_LO, techo=P_HI, ancho=ANCHO_P,
                        alto=ALTO_P, color=C_RUIDO, area=False, grosor=1.4)
        pb.shift(C_DER)

        def mobiliario(p):
            g = VGroup()
            for v in (0, 5, 10):
                t = tag_hud(f"{v}", font_size=18, color=C_TENUE)
                t.next_to(p.en(p.f[0], v), LEFT, buff=0.18)
                g.add(t)
            g.add(DashedLine(p.en(p.f[0], 0), p.en(p.f[-1], 0),
                             color=C_TITULO, stroke_width=1.6,
                             dash_length=0.07))
            g.add(p.marcas([0, 500, 1000], ["0", "500", "1000"],
                           font_size=18))
            u = tag_hud("dB", font_size=18, color=C_TENUE)
            u.next_to(p.en(p.f[0], P_HI), LEFT, buff=0.18)
            g.add(u)
            return g

        m_a, m_b = mobiliario(pa), mobiliario(pb)
        u_media = tag_junto(m_b[3], "media", RIGHT, buff=0.12, font_size=18)
        u_cha = tag_junto(m_b[4], "chips", RIGHT, buff=0.2, font_size=20)
        u_cha.align_to(m_b[4], DOWN)
        prn_a = tag_dato(f"PRN {PRN}", font_size=22)
        prn_a.next_to(pa.en(pa.f[len(pa.f) // 2], P_HI), UP, buff=0.12)
        prn_b = tag_dato("PRN 3", font_size=22)
        prn_b.next_to(pb.en(pb.f[len(pb.f) // 2], P_HI), UP, buff=0.12)

        self.play(Create(pa.ejes), FadeIn(m_a), FadeIn(prn_a), run_time=0.7)
        self.play(Create(pa.curva), run_time=2.0)
        self.add(m_a[3])
        t_7 = tag_hud(f"{fmt(PICO_DB, 1)} dB", font_size=24)
        t_7.next_to(pa.en(CH_PICO, PICO_DB), RIGHT, buff=0.16)
        self.play(FadeIn(t_7), run_time=0.4)
        rot.mostrar(cifra_pie(f"{fmt(PICO_DB, 1)} dB sobre la media"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(Create(pb.ejes), FadeIn(m_b), FadeIn(u_cha),
                  FadeIn(prn_b), FadeIn(u_media), run_time=0.7)
        self.play(Create(pb.curva), run_time=2.0)
        self.add(m_b[3])
        t_3 = tag_hud(f"{fmt(OTRO_DB, 1)} dB", font_size=24)
        t_3.next_to(pb.en(chips[k3], OTRO_DB), UP, buff=0.14)
        self.play(FadeIn(t_3), run_time=0.4)
        rot.mostrar(cifra_pie(f"otro satelite: {fmt(OTRO_DB, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(dato_pie("10 ms sumados"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        cierre_leccion(self, rot, "Veinte decibelios bajo el ruido",
                       "y aun asi se encuentra.", pa.ejes, pa.curva,
                       pb.ejes, pb.curva, m_a, m_b, u_media, u_cha, prn_a,
                       prn_b, t_7, t_3)
