class Clip3(Scene):
    """1.3.3 - Las dos direcciones de subida cero son la tangente al nivel:
    el gradiente sale perpendicular a la curva, en todo el mapa. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Perpendicular al nivel")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        def escuadra(centro, a, b, lado=0.19):
            """Marca de angulo recto entre dos direcciones de pantalla."""
            a = a / np.linalg.norm(a)
            b = b / np.linalg.norm(b)
            m = VMobject(stroke_color=C_GRAD, stroke_width=2.4)
            m.set_points_as_corners([centro + lado * a,
                                     centro + lado * (a + b),
                                     centro + lado * b])
            return m

        def pantalla(v):
            return np.array([v[0], v[1], 0.0]) / np.linalg.norm(v)

        # --- momento: el punto sobre su curva de nivel ---------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100,
                            opacidad=0.8)
        self.play(FadeIn(pl), FadeIn(mapa), run_time=1.0)
        rot.mostrar(pie_curso("Aquellas dos direcciones de subida cero no "
                              "eran ninguna casualidad."), zona="abajo",
                    run_time=0.5)
        p0 = PUNTOS_NIVEL[I_DEMO]
        g0 = GRADS_NIVEL[I_DEMO]
        t0 = TANS_NIVEL[I_DEMO]
        i_curva = NIVELES.index(NIVELES_PUNTO[I_DEMO])
        d0 = Dot(pl.p(p0), radius=0.085, color=C_VEC)
        self.play(FadeIn(d0, scale=0.5),
                  Indicate(mapa.curva(i_curva), color=C_CIFRA,
                           scale_factor=1.02), run_time=1.2)
        self.wait(3.6)

        # --- momento: la tangente al nivel no sube -------------------------
        rot.mostrar(pie_curso("Andar sobre la curva de nivel es andar sin "
                              "ganar ni perder altura."), zona="abajo",
                    run_time=0.5)
        tang = VGroup(
            flecha_libre(pl, p0, p0 + t0 * R_TANGENTE, color=C_CIFRA,
                         grosor=3.6, punta_len=0.18),
            flecha_libre(pl, p0, p0 - t0 * R_TANGENTE, color=C_CIFRA,
                         grosor=3.6, punta_len=0.18))
        # fondo bajo la cifra: la curva de nivel pasa justo por debajo
        tag_t = _con_fondo(tag_hud(f"subida = {fmt(DOTS_NIVEL[I_DEMO], 2)}",
                                   font_size=20), buff=0.10, opacidad=0.8)
        tag_t.next_to(pl.p(p0 + t0 * R_TANGENTE), DOWN, buff=0.24)
        self.play(GrowArrow(tang[0]), GrowArrow(tang[1]), run_time=0.9)
        self.play(FadeIn(tag_t), run_time=0.4)
        self.wait(3.8)

        # --- momento: el gradiente sale de frente --------------------------
        rot.mostrar(pie_curso("El gradiente, en cambio, sale de frente: "
                              "perpendicular a la curva."), zona="abajo",
                    run_time=0.5)
        gr0 = flecha_libre(pl, p0, p0 + g0 * ESC_NIVEL, color=C_GRAD,
                           grosor=5.0, punta_len=0.24)
        esc0 = escuadra(pl.p(p0), pantalla(g0), pantalla(t0))
        self.play(GrowArrow(gr0), run_time=0.9)
        self.play(Create(esc0), run_time=0.5)
        panel = panel_derecha(MathTex(r"\nabla f \cdot \hat t = "
                                      + fmt(DOTS_NIVEL[I_DEMO], 2),
                                      font_size=32, color=C_RES))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        # --- momento: pasa en todo el mapa ---------------------------------
        rot.mostrar(pie_curso("Y no es cosa de este punto: pasa en cada "
                              "punto de cada curva del mapa."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tang), FadeOut(tag_t), run_time=0.5)
        resto = VGroup()
        for i in range(len(PUNTOS_NIVEL)):
            if i == I_DEMO:
                continue
            p = PUNTOS_NIVEL[i]
            g = GRADS_NIVEL[i]
            t = TANS_NIVEL[i]
            resto.add(VGroup(Dot(pl.p(p), radius=0.07, color=C_VEC),
                             flecha_libre(pl, p, p + g * ESC_NIVEL,
                                          color=C_GRAD, grosor=4.4,
                                          punta_len=0.22),
                             escuadra(pl.p(p), pantalla(g), pantalla(t))))
        self.play(LaggedStart(*[FadeIn(m, scale=0.7) for m in resto],
                              lag_ratio=0.28), run_time=2.4)
        self.wait(3.2)

        # --- momento: la comprobacion de los cinco -------------------------
        rot.mostrar(pie_curso("Medidos los cinco, el mayor desvío del "
                              "ángulo recto es cero. Ni uno se tuerce."),
                    zona="abajo", run_time=0.5)
        peor = tag_hud(f"peor desvio = {fmt(PERP_PEOR, 2)}",
                       font_size=19, color=C_RES)
        peor.next_to(panel, DOWN, buff=0.20).align_to(panel, RIGHT)
        peor.shift(LEFT * 0.18)
        self.play(FadeIn(peor), run_time=0.5)
        self.wait(4.4)
