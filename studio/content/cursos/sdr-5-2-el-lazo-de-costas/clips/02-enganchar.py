from comunicaciones import Onda  # noqa: E402


def _traza(o, t, y, color, grosor=2.6, salto=90.0):
    """Polilinea en la caja de `o`, cortada donde el error de fase da la
    vuelta (modulo 180 grados): sin la raya vertical del salto."""
    g = VGroup()
    cortes = np.where(np.abs(np.diff(y)) > salto)[0] + 1
    for a, b in zip(np.r_[0, cortes], np.r_[cortes, len(y)]):
        if b - a < 2:
            continue
        c = VMobject(color=color, stroke_width=grosor)
        c.set_points_as_corners([o.en(u, v) for u, v in zip(t[a:b], y[a:b])])
        g.add(c)
    return g


class Clip2(Scene):
    """5.2.2 - Enganchar (Bn*T = 0.02): la fase del NCO (fucsia) persigue a
    la fase real (ambar) hasta pegarse; debajo, el error de fase cae a
    cero. A la derecha, la entrada es un anillo (la fase gira) y la salida
    del lazo, ya enganchado, dos puntos. Cian: enganche mediano de 8
    semillas. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Enganchar"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        L = LAZOS[0.02]
        n_ver = 400
        k = np.arange(n_ver)
        f_real = np.degrees(FASE_REAL[:n_ver])
        f_nco = np.degrees(L["fase"][:n_ver])
        e = np.degrees(np.angle(np.exp(1j * 2 * (L["fase"][:n_ver]
                                                   - FASE_REAL[:n_ver]))) / 2)
        techo = 30.0 * np.ceil(max(f_real.max(), f_nco.max()) / 30.0 + 0.2)

        # --- las fases: real (ambar) y NCO (fucsia) ---------------------------
        o_f = Onda(k, f_real, rango_y=(0.0, techo), ancho=6.8, alto=2.45,
                   color=C_SENAL)
        o_e = Onda(k, e, rango_y=(-90.0, 90.0), ancho=6.8, alto=1.95,
                   color=C_LO)
        VGroup(o_f, o_e).arrange(DOWN, buff=0.62).move_to(LEFT * 2.85
                                                          + DOWN * 0.02)
        c_real = _traza(o_f, k, f_real, C_SENAL)
        c_nco = _traza(o_f, k, f_nco, C_LO)
        c_err = _traza(o_e, k, e, C_LO)
        cero = o_e.horizontal_en(0.0, color=C_TENUE)
        l_real = Text("real", font=FUENTE_HUD, font_size=20, color=C_SENAL)
        l_nco = Text("NCO", font=FUENTE_HUD, font_size=20, color=C_LO)
        leyenda = VGroup(l_real, l_nco).arrange(DOWN, buff=0.14,
                                                aligned_edge=LEFT)
        leyenda.move_to(o_f.en(0.0, techo), aligned_edge=UL).shift(
            RIGHT * 0.3 + DOWN * 0.05)
        t_f = tag_junto(o_f, "fase, grados", LEFT, font_size=22)
        t_f.rotate(PI / 2).next_to(o_f.ejes[1], LEFT, buff=0.18)
        t_e = tag_junto(o_e, "error, grados", LEFT, font_size=22,
                        color=C_LO)
        t_e.rotate(PI / 2).next_to(o_e.ejes[1], LEFT, buff=0.18)
        t_k = tag_junto(o_e, "simbolos", DOWN, buff=0.12, font_size=20)
        t_k.next_to(o_e.en(float(k[-1]), 0.0), RIGHT, buff=0.15)
        t90 = VGroup(
            Text("90", font=FUENTE_HUD, font_size=18, color=C_TENUE)
            .next_to(o_e.en(0.0, 90.0), LEFT, buff=0.1),
            Text("-90", font=FUENTE_HUD, font_size=18, color=C_TENUE)
            .next_to(o_e.en(0.0, -90.0), LEFT, buff=0.1))
        bn = tag_dato(f"Bn T = {0.02:g}", font_size=20)
        bn.move_to(o_e.en(0.72 * k[-1], -55.0))

        # --- el plano IQ: entrada (anillo) y salida (dos puntos) --------------
        plano = S.PlanoIQ(unidad=1.45, alcance=1.42)
        plano.move_to(RIGHT * 4.3 + DOWN * 0.02)
        anillo = plano.nube(RX[::3], color=C_SENAL, radio=0.03)
        salida = plano.nube(L["out"][L["enganche"]::3], color=C_SENAL,
                            radio=0.03)
        t_in = tag_junto(plano, "entrada", DOWN, buff=0.14, font_size=22)
        t_out = tag_junto(plano, "salida", DOWN, buff=0.14, font_size=22,
                          color=C_SENAL)

        self.play(Create(o_f.ejes), Create(o_e.ejes), Create(cero),
                  FadeIn(t_f), FadeIn(t_e), FadeIn(t_k), FadeIn(t90),
                  Create(plano), run_time=1.0)
        self.play(FadeIn(anillo, lag_ratio=0.02), FadeIn(t_in),
                  Create(c_real), FadeIn(l_real), run_time=1.8)
        self.wait(1.0)
        df_rs = float(np.diff(FASE_REAL[:2])[0] / (2 * np.pi))
        rot.mostrar(dato_pie(f"{df_rs:.3f} ciclos por simbolo"), zona="abajo",
                    run_time=0.5)
        self.wait(1.4)
        self.wait(1.6)

        # --- el lazo persigue ---------------------------------------------
        self.play(FadeIn(l_nco), FadeIn(bn), run_time=0.4)
        self.play(Create(c_nco), Create(c_err), run_time=5.0,
                  rate_func=linear)
        self.wait(1.4)
        rot.limpiar(zona="abajo", run_time=0.3)

        marca = o_e.vertical_en(float(ENG_MED[0.02]), color=C_CALCULO)
        marca_f = o_f.vertical_en(float(ENG_MED[0.02]), color=C_CALCULO)
        self.play(Create(marca), Create(marca_f), run_time=0.6)
        self.play(FadeOut(anillo), FadeOut(t_in), run_time=0.7)
        self.play(FadeIn(salida, lag_ratio=0.02), FadeIn(t_out),
                  run_time=1.8)
        self.wait(1.0)
        rot.mostrar(cifra_pie(f"enganche: {ENG_MED[0.02]} simbolos"),
                    zona="abajo", run_time=0.5)
        self.wait(12.0)
