class Clip4(Scene):
    """5.2.4 - La ambiguedad de 180 grados: con la fase inicial por encima
    de 90 grados (2.3 rad) el lazo engancha al reves; la nube de salida se
    ve perfecta, pero todos los bits salen negados (rojo). Con codificacion
    diferencial (el bit va en el CAMBIO de fase) el mismo enganche al
    reves entrega los bits correctos (verde). Cierre. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La ambiguedad de 180"), zona="arriba",
                    run_time=0.6)
        self.wait(0.4)

        # --- las dos corridas (misma fase inicial, mismo ruido) ---------------
        bn = ANCHOS[1]
        n = len(SIM_I)
        fase0 = float(FR_I[0])
        _, f_a, _ = S.costas_bpsk(RX_I, bn)
        k0 = S.tiempo_enganche(f_a, FR_I)
        b = (np.real(SIM_I) > 0).astype(int)          # bits enviados
        r_a = (np.real(OUT_I) > 0).astype(int)         # bits recibidos
        neg = int(np.sum(r_a[k0:] != b[k0:]))
        tot = n - k0
        d = S.diferencial(b)                            # codificados
        tx = (2 * d - 1).astype(complex)
        snr = S.escenario_costas.__defaults__[3]
        rx_b = S.con_desfase(tx, 0.0, fase0) + S.ruido_complejo(
            n, 10 ** (-snr / 10), 4)                    # ruido de semilla 3
        out_b, f_b, _ = S.costas_bpsk(rx_b, bn)
        k0b = S.tiempo_enganche(f_b, FR_I)
        r_b = (np.real(out_b) > 0).astype(int)
        dd = S.dediferencial(r_b)
        err_b = int(np.sum(dd[k0b:] != b[k0b:]))
        tot_b = n - k0b

        def desfase(f):
            return abs(float(np.degrees(np.angle(np.exp(
                1j * (f[-1] - FR_I[-1]))))))

        # --- plano IQ: la senal (ambar) y donde se engancho el NCO (fucsia) ---
        plano = S.PlanoIQ(unidad=1.6, alcance=1.42)
        plano.move_to(LEFT * 4.25 + DOWN * 0.1)

        def figura(rx, f):
            nube = plano.nube(rx[k0::3], color=C_SENAL, radio=0.03,
                              opacidad=0.55)
            o = plano.p(0, 0)
            a_real = Arrow(o, plano.p(1.05 * np.exp(1j * fase0)),
                           buff=0, color=C_SENAL, stroke_width=6,
                           max_tip_length_to_length_ratio=0.12)
            a_nco = Arrow(o, plano.p(1.05 * np.exp(1j * f[-1])), buff=0,
                          color=C_LO, stroke_width=6,
                          max_tip_length_to_length_ratio=0.12)
            ang0 = float(f[-1])
            dang = float(np.angle(np.exp(1j * (fase0 - ang0))))
            arco = Arc(radius=0.42 * plano.u, start_angle=ang0, angle=dang,
                       color=C_CALCULO, stroke_width=3).move_arc_center_to(o)
            med = ang0 + dang / 2
            et = tag_hud(f"{fmt(desfase(f), 1)} grados", font_size=20)
            et.move_to(plano.p(0.95 * np.exp(1j * med)))
            return nube, a_real, a_nco, arco, et

        nube, a_real, a_nco, arco, et_ang = figura(RX_I, f_a)

        def etiqueta(texto, color, ang):
            t = _con_fondo(Text(texto, font=FUENTE_HUD, font_size=20,
                                color=color), buff=0.08)
            t.move_to(plano.p(1.62 * np.exp(1j * ang)))
            return t

        l_real = etiqueta("fase real", C_SENAL, fase0)
        l_nco = etiqueta("NCO", C_LO, float(f_a[-1]))

        # --- las filas de bits -----------------------------------------------
        i0, nb = 1000, 12
        x_fila = 3.2

        def fila(bits, color):
            g = VGroup(*[Text(str(int(v)), font=FUENTE_HUD, font_size=38,
                              color=color) for v in bits[i0:i0 + nb]])
            g.arrange(RIGHT, buff=0.29)
            return g

        def rotulo(texto, g, color=C_TENUE):
            t = Text(texto, font_size=24, color=color)
            t.next_to(g, UP, buff=0.12).align_to(g, LEFT)
            return t

        ys = (2.05, 0.75, -0.55, -1.85)
        f_env = fila(b, C_TITULO).move_to(RIGHT * x_fila + UP * ys[0])
        t_env = rotulo("enviados", f_env)
        self.play(Create(plano), FadeIn(t_env), FadeIn(f_env, lag_ratio=0.1),
                  run_time=1.0)
        self.play(FadeIn(nube, lag_ratio=0.02), run_time=1.4)
        self.play(GrowArrow(a_real), FadeIn(l_real), run_time=0.7)
        rot.mostrar(dato_pie(f"fase inicial {fase0:g} rad"), zona="abajo",
                    run_time=0.5)
        self.wait(1.2)
        self.play(GrowArrow(a_nco), FadeIn(l_nco), run_time=0.8)
        self.play(Create(arco), FadeIn(et_ang), run_time=0.8)
        self.wait(1.6)

        f_rec = fila(r_a, C_RUIDO).move_to(RIGHT * x_fila + UP * ys[1])
        t_rec = rotulo("recibidos", f_rec, C_RUIDO)
        self.play(FadeIn(t_rec), FadeIn(f_rec, lag_ratio=0.1), run_time=1.0)
        self.wait(1.0)
        rot.mostrar(cifra_pie(f"negados: {neg} de {tot}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        # --- codificacion diferencial ---------------------------------------
        rot.limpiar(zona="abajo", run_time=0.3)
        self.play(FadeOut(f_rec), FadeOut(t_rec), FadeOut(arco),
                  FadeOut(et_ang), run_time=0.6)
        nube_b, _, a_nco_b, arco_b, et_b = figura(rx_b, f_b)
        l_nco_b = etiqueta("NCO", C_LO, float(f_b[-1]))
        self.play(FadeOut(nube), FadeIn(nube_b), Transform(a_nco, a_nco_b),
                  Transform(l_nco, l_nco_b), run_time=0.9)
        self.add(a_real, a_nco, l_real, l_nco)     # flechas sobre la nube
        self.play(Create(arco_b), FadeIn(et_b), run_time=0.7)

        f_cod = fila(d, C_TITULO).move_to(RIGHT * x_fila + UP * ys[1])
        t_cod = rotulo("codificados", f_cod)
        f_rb = fila(r_b, C_RUIDO).move_to(RIGHT * x_fila + UP * ys[2])
        t_rb = rotulo("recibidos", f_rb, C_RUIDO)
        f_dd = fila(dd, C_OK).move_to(RIGHT * x_fila + UP * ys[3])
        t_dd = rotulo("decodificados", f_dd, C_OK)
        self.play(FadeIn(t_cod), FadeIn(f_cod, lag_ratio=0.1), run_time=1.0)
        self.wait(0.8)
        self.play(FadeIn(t_rb), FadeIn(f_rb, lag_ratio=0.1), run_time=1.0)
        self.wait(0.8)
        self.play(FadeIn(t_dd), FadeIn(f_dd, lag_ratio=0.1), run_time=1.0)
        self.wait(1.0)
        rot.mostrar(cifra_pie(f"errores: {err_b} de {tot_b}"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)

        cierre_leccion(self, rot, "El lazo encuentra la fase,",
                       "no cual es cual.", plano, nube_b, a_real, a_nco,
                       l_real, l_nco, arco_b, et_b, f_env, t_env, f_cod,
                       t_cod, f_rb, t_rb, f_dd, t_dd)
