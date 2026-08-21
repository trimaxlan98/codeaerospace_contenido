class Clip4(Scene):
    """3.1.4 - El mapa de la divergencia punto a punto (verde fuente, rojo
    sumidero) para un campo cuyo div CAMBIA de signo; particulas sembradas
    alrededor de la fuente se acumulan donde la divergencia es negativa.
    Cierre de la leccion. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El mapa de la divergencia")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mapa, cuadro a cuadro por el signo de div ----------
        pl = plano_leccion()
        self.play(FadeIn(pl), run_time=0.7)
        rot.mostrar(pie_curso("Coloreemos el plano por el signo de la "
                              "divergencia: verde donde nace, rojo donde "
                              "se pierde."), zona="abajo", run_time=0.5)

        malla = MALLA_MAPA
        xs = np.arange(malla["x0"], malla["x1"] + 1e-9, malla["paso"])
        ys = np.arange(malla["y0"], malla["y1"] + 1e-9, malla["paso"])
        puntos_malla = [(x, y) for y in ys for x in xs]
        divs_malla = [div_num(CAMPO_MAPA, np.array(p)) for p in puntos_malla]
        max_div = max(1e-6, max(abs(d) for d in divs_malla))
        lado_px = malla["paso"] * pl.unidad * 0.92
        cuadros = VGroup()
        for (x, y), d in zip(puntos_malla, divs_malla):
            color = C_RES if d >= 0 else C_VEC
            op = 0.12 + 0.75 * min(1.0, abs(d) / max_div)
            cu = Square(side_length=lado_px, stroke_width=0,
                       fill_color=color, fill_opacity=op)
            cu.move_to(pl.p(x, y))
            cuadros.add(cu)
        cuadros.set_z_index(-1)
        self.play(FadeIn(cuadros), run_time=1.4)
        self.wait(3.2)

        # --- momento: dos cifras, fuente y sumidero -------------------------
        rot.mostrar(pie_curso("En el origen, cos(0)+cos(0): una fuente "
                              "clara. Más lejos, la cuenta cambia de "
                              "signo."), zona="abajo", run_time=0.5)
        d_fuente = div_num(CAMPO_MAPA, P_FUENTE_MAPA)
        dot_f = Dot(pl.p(P_FUENTE_MAPA), radius=0.08, color=C_RES)
        etq_f = tag_hud(f"div = +{fmt(d_fuente)}", font_size=16, color=C_RES)
        etq_f.next_to(dot_f, UP, buff=0.12)
        t_f = _con_fondo(etq_f, buff=0.08, opacidad=0.85)
        d_sumidero = div_num(CAMPO_MAPA, P_SUMIDERO_MAPA)
        dot_s = Dot(pl.p(P_SUMIDERO_MAPA), radius=0.08, color=C_VEC)
        etq_s = tag_hud(f"div = {fmt(d_sumidero)}", font_size=16, color=C_VEC)
        etq_s.next_to(dot_s, UP, buff=0.12)
        t_s = _con_fondo(etq_s, buff=0.08, opacidad=0.85)
        self.play(FadeIn(dot_f, scale=0.5), FadeIn(t_f), run_time=0.6)
        self.play(FadeIn(dot_s, scale=0.5), FadeIn(t_s), run_time=0.6)
        self.wait(3.4)

        # --- momento: siembra de particulas alrededor de la fuente ----------
        rot.mostrar(pie_curso("Sembremos partículas alrededor de la "
                              "fuente y sigamos la corriente."),
                    zona="abajo", run_time=0.5)
        # Desfase de medio paso: ningun angulo cae en un eje (x=0 o y=0
        # son puntos silla de CAMPO_MAPA, no sumideros) -- las 8 semillas
        # caen todas en sumideros diagonales genuinos (div < 0 real).
        angulos = (np.linspace(0, 2 * np.pi, N_SIEMBRA, endpoint=False)
                  + np.pi / N_SIEMBRA)
        semillas = [P_FUENTE_MAPA + RADIO_SIEMBRA
                   * np.array([np.cos(a), np.sin(a)]) for a in angulos]
        lineas = VGroup(*[linea_flujo(pl, CAMPO_MAPA, s0, T=6.0,
                                      opacidad=0.4) for s0 in semillas])
        particulas = VGroup(*[Dot(pl.p(s0), radius=0.06, color=C_VEC)
                              for s0 in semillas])
        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.12),
                  run_time=1.8)
        self.play(FadeIn(particulas), run_time=0.5)
        self.wait(3.0)

        # --- momento: se acumulan donde la divergencia es negativa ----------
        rot.mostrar(pie_curso("Donde la caja se vacía, la corriente se "
                              "estanca: las partículas se acumulan ahí."),
                    zona="abajo", run_time=0.5)
        self.play(AnimationGroup(*[MoveAlongPath(p, l) for p, l in
                                   zip(particulas, lineas)], lag_ratio=0.0),
                  run_time=3.8, rate_func=linear)
        self.wait(2.8)

        # --- cierre -----------------------------------------------------------
        cierre_leccion(self, rot,
                       "La divergencia es el balance de la cajita.",
                       "Fuentes y sumideros, punto a punto.",
                       "Siguiente lección: la ruedecita y el rotacional.",
                       pl, cuadros, dot_f, t_f, dot_s, t_s, lineas,
                       particulas)
