class Clip2(Scene):
    """8.3.2 - El presupuesto del enlace de Meteor como escalera de dB en
    UNA escala vertical (dBm): 37 dBm del transmisor, la caida de espacio
    libre (140.5 dB a 1822.6 km), antenas y perdidas (+3 -3), recibida
    -103.5 dBm contra un piso de -124.4 dBm: Es/N0 20.9 dB. Luego la
    misma escala se acerca (una sola escala a la vez, eje rehecho) a los
    ultimos 30 dB: la raya de los 4 dB que pide la cadena del 7.2 y el
    margen de 16.9 dB. Insumos en gris, resultados en cian. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El presupuesto"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        p_tx = P["p_tx_dbm"]
        fspl = PRES["fspl_db"]
        prx = PRES["prx_dbm"]
        piso = PRES["ruido_dbm"]
        esn0 = PRES["snr_db"]
        req = piso + P["esn0_req_db"]
        margen = PRES["margen_db"]
        tras_fspl = p_tx + P["g_tx_dbi"] - fspl
        vatios = 10 ** ((p_tx - 30) / 10)

        X_EJE = -5.55

        def escala(lo, hi, y0=-2.3, y1=2.2):
            return lambda d: y0 + (d - lo) / (hi - lo) * (y1 - y0)

        def eje(y, lo, hi, paso_tick, paso_rot):
            g = VGroup()
            g.add(Line([X_EJE, y(lo), 0], [X_EJE, y(hi), 0], color=C_EJE,
                       stroke_width=2))
            v = math.ceil(lo / paso_tick) * paso_tick
            while v <= hi + 1e-9:
                yy = y(v)
                g.add(Line([X_EJE - 0.1, yy, 0], [X_EJE, yy, 0],
                           color=C_EJE, stroke_width=2))
                if abs(v / paso_rot - round(v / paso_rot)) < 1e-9:
                    t = Text(f"{v:+.0f}" if v else "0", font=FUENTE_HUD,
                             font_size=18, color=C_TENUE)
                    t.next_to([X_EJE - 0.1, yy, 0], LEFT, buff=0.1)
                    g.add(t)
                v += paso_tick
            u = Text("dBm", font=FUENTE_HUD, font_size=18, color=C_TENUE)
            u.next_to([X_EJE, y(hi), 0], UP, buff=0.34).align_to(
                [X_EJE, 0, 0], RIGHT)
            g.add(u)
            return g

        # ================= ESCALA COMPLETA: +40 a -130 dBm ================
        ya = escala(-130.0, 40.0)
        eje_a = eje(ya, -130.0, 40.0, 10.0, 40.0)
        self.play(FadeIn(eje_a), run_time=0.8)

        # --- el transmisor --------------------------------------------------
        x_tx0, x_tx1 = -4.9, -3.6
        s_tx = Line([x_tx0, ya(p_tx), 0], [x_tx1, ya(p_tx), 0],
                    color=C_SENAL, stroke_width=5)
        t_tx = tag_dato(f"TX {fmt(p_tx, 0)} dBm = {fmt(vatios, 0)} W",
                        font_size=21)
        t_tx.next_to(s_tx, UP, buff=0.16).align_to(s_tx, LEFT)
        self.play(Create(s_tx), FadeIn(t_tx), run_time=0.9)
        self.wait(1.6)

        # --- la caida de espacio libre -------------------------------------
        caida = Line([x_tx1, ya(p_tx), 0], [x_tx1, ya(tras_fspl), 0],
                     color=C_SENAL, stroke_width=4)
        t_fs1 = Text("espacio libre", font_size=24, color=C_TENUE)
        t_fs2 = tag_hud(f"-{fmt(fspl, 1)} dB", font_size=28)
        t_fs3 = tag_hud(f"a {fmt(PRES['alcance_km'], 1)} km", font_size=22)
        t_fs = VGroup(t_fs1, t_fs2, t_fs3).arrange(DOWN, buff=0.14,
                                                   aligned_edge=LEFT)
        t_fs.next_to(caida, RIGHT, buff=0.3).set_y(ya(-30))
        self.play(Create(caida), run_time=1.6)
        self.play(FadeIn(t_fs, shift=LEFT * 0.1), run_time=0.6)
        d_fs = tag_dato(f"{mhz(P['f_hz'])} MHz, "
                        f"{fmt(P['elev_deg'], 0)} grados", font_size=20)
        d_fs.next_to(t_fs, DOWN, buff=0.18, aligned_edge=LEFT)
        self.play(FadeIn(d_fs), run_time=0.5)
        self.wait(2.2)

        # --- antenas y perdidas: +3 -3 --------------------------------------
        x_ant = -1.2
        s_ant = Line([x_tx1, ya(tras_fspl), 0], [x_ant, ya(prx), 0],
                     color=C_SENAL, stroke_width=4)
        t_ant = tag_dato(f"+{fmt(P['g_rx_dbi'], 0)} dBi  "
                         f"-{fmt(P['perdidas_db'], 0)} dB", font_size=21)
        t_ant.next_to(s_ant, DOWN, buff=0.18)
        self.play(Create(s_ant), FadeIn(t_ant), run_time=0.9)
        self.wait(1.4)

        # --- la recibida -----------------------------------------------------
        x_rx1 = 1.3
        s_rx = Line([x_ant, ya(prx), 0], [x_rx1, ya(prx), 0], color=C_SENAL,
                    stroke_width=7)
        t_rx = tag_hud(f"{fmt(prx, 1)} dBm", font_size=26)
        t_rx.next_to(s_rx, UP, buff=0.16)
        self.play(Create(s_rx), FadeIn(t_rx), run_time=0.8)
        self.wait(1.6)

        # --- el piso de ruido a la derecha --------------------------------------
        x_n0, x_n1 = 1.9, 4.3
        s_n = Line([x_n0, ya(piso), 0], [x_n1, ya(piso), 0], color=C_RUIDO,
                   stroke_width=5)
        ext = DashedLine([x_rx1, ya(prx), 0], [x_n1, ya(prx), 0],
                         color=C_SENAL, stroke_width=2, dash_length=0.1)
        t_n = tag_hud(f"{fmt(piso, 1)} dBm", font_size=24)
        t_n.next_to(s_n, DOWN, buff=0.14)
        self.play(Create(s_n), Create(ext), FadeIn(t_n), run_time=0.9)
        self.wait(1.2)
        f_es = DoubleArrow([x_n1 + 0.3, ya(piso), 0], [x_n1 + 0.3, ya(prx), 0],
                           buff=0, color=C_CALCULO, stroke_width=3,
                           tip_length=0.14,
                           max_tip_length_to_length_ratio=0.3)
        t_es = tag_hud(f"{fmt(esn0, 1)} dB", font_size=24)
        t_es.next_to(f_es, RIGHT, buff=0.16)
        self.play(GrowFromCenter(f_es), FadeIn(t_es), run_time=0.7)
        rot.mostrar(cifra_pie(f"Es/N0 = {fmt(esn0, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        # ============ LA MISMA MAGNITUD, MAS CERCA: -128 a -98 dBm ===========
        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(FadeOut(VGroup(eje_a, s_tx, t_tx, caida, t_fs, d_fs, s_ant,
                                 t_ant, t_rx, t_n, t_es, ext)), run_time=0.8)
        yb = escala(-128.0, -98.0, y0=-2.0, y1=2.2)
        eje_b = eje(yb, -128.0, -98.0, 1.0, 5.0)
        x0, x1 = -5.0, 4.4
        s_rx_b = Line([x0, yb(prx), 0], [x1, yb(prx), 0],
                      color=C_SENAL, stroke_width=7)
        s_n_b = Line([x0, yb(piso), 0], [x1, yb(piso), 0],
                     color=C_RUIDO, stroke_width=5)
        x_es = 0.6
        f_es_b = DoubleArrow([x_es, yb(piso), 0], [x_es, yb(prx), 0],
                             buff=0, color=C_CALCULO, stroke_width=3,
                             tip_length=0.2,
                             max_tip_length_to_length_ratio=0.3)
        self.play(FadeIn(eje_b),
                  Transform(s_rx, s_rx_b), Transform(s_n, s_n_b),
                  Transform(f_es, f_es_b), run_time=1.6)
        t_rx_b = VGroup(Text("recibida", font_size=24, color=C_TENUE),
                        tag_hud(f"{fmt(prx, 1)} dBm", font_size=26)
                        ).arrange(RIGHT, buff=0.3)
        t_rx_b.next_to(s_rx_b, UP, buff=0.16).align_to(s_rx_b, LEFT)
        t_n_b = VGroup(Text("ruido", font_size=24, color=C_TENUE),
                       tag_hud(f"{fmt(piso, 1)} dBm", font_size=26)
                       ).arrange(RIGHT, buff=0.3)
        t_n_b.next_to(s_n_b, DOWN, buff=0.16).align_to(s_n_b, LEFT)
        d_n = tag_dato(f"NF {fmt(NF_ANT, 2)} dB, "
                       f"{fmt(P['b_hz'] / 1e3, 0)} kHz", font_size=20)
        d_n.next_to(s_n_b, DOWN, buff=0.2).align_to(s_n_b, RIGHT)
        t_es_b = VGroup(MathTex(r"E_s/N_0", font_size=36, color=C_CALCULO),
                        tag_hud(f"{fmt(esn0, 1)} dB", font_size=28)
                        ).arrange(DOWN, buff=0.14)
        t_es_b.next_to(f_es_b, RIGHT, buff=0.25)
        self.play(FadeIn(t_rx_b), FadeIn(t_n_b), FadeIn(d_n),
                  FadeIn(t_es_b), run_time=0.8)
        self.wait(2.6)

        # --- lo que pide la cadena del 7.2 y el margen ------------------------
        s_req = DashedLine([x0, yb(req), 0], [x1, yb(req), 0],
                           color=C_DATO, stroke_width=3, dash_length=0.14)
        t_req = tag_dato(f"pide {fmt(P['esn0_req_db'], 0)} dB", font_size=21)
        t_req.next_to(s_req, UP, buff=0.12).align_to(s_req, LEFT)
        self.play(Create(s_req), FadeIn(t_req), run_time=0.9)
        self.wait(1.8)
        x_m = 3.5
        f_m = DoubleArrow([x_m, yb(req), 0], [x_m, yb(prx), 0], buff=0,
                          color=C_CALCULO, stroke_width=4, tip_length=0.2,
                          max_tip_length_to_length_ratio=0.3)
        t_m = VGroup(Text("margen", font_size=24, color=C_TENUE),
                     tag_hud(f"{fmt(margen, 1)} dB", font_size=28)
                     ).arrange(DOWN, buff=0.14)
        t_m.next_to(f_m, RIGHT, buff=0.22)
        self.play(GrowFromCenter(f_m), FadeIn(t_m), run_time=0.8)
        rot.mostrar(cifra_pie(f"margen {fmt(margen, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(7.0)
