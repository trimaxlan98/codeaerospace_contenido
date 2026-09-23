class Clip4(Scene):
    """3.2.4 - El limite honesto del resultado: la condicion es necesaria,
    no suficiente. En un juego de m casillas donde nadie ve cual paga, el
    margen del entorno es m - 1 y el alcanzable, cero. Por eso la tesis
    EXHIBE una politica que gana, en vez de fiarse del margen. Cierre.
    (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Una holgura sin techo"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        filas = [("oraculo", C_PRIV), ("estatica", C_ESTATICA), ("descentralizada", C_ADAPTA)]
        ys = [1.4, 0.0, -1.4]
        x0, lado, dx = -2.6, 0.6, 0.72
        rng = np.random.default_rng(42)

        def tablero(m):
            return VGroup(*[VGroup(*[Square(side_length=lado, stroke_color=C_TENUE, stroke_width=2.5)
                                     .move_to([x0 + i * dx, y, 0]) for i in range(m)]) for y in ys])
        etq = VGroup(*[tag_hud(n, font_size=17, color=col).next_to([x0 - 0.45, y, 0], LEFT, buff=0.0)
                       for (n, col), y in zip(filas, ys)])
        tab = tablero(3)
        fichas = VGroup(*[Dot([x0, y, 0], radius=0.16, color=col) for (_, col), y in zip(filas, ys)])
        self.play(FadeIn(etq), FadeIn(tab), FadeIn(fichas), run_time=0.9)
        self.wait(1.0)

        def jugar(m, tab, pasos, dt):
            for _ in range(pasos):
                s = int(rng.integers(0, m))
                luz = VGroup(*[Square(side_length=lado, stroke_width=0, fill_color=C_TIERRA,
                                      fill_opacity=1.0).move_to(f[s]) for f in tab])
                luz.set_z_index(-1)
                self.add(luz)
                self.play(*[fi.animate.move_to(tab[j][d]) for j, (fi, d) in enumerate(zip(fichas, (s, 0, 0)))],
                          run_time=dt)
                self.remove(luz)
        jugar(3, tab, 8, 0.32)
        cifras = VGroup(MathTex(rf"\mathrm{{MA}} = {J3['MA']:.0f}", color=C_PRIV, font_size=40),
                        MathTex(rf"\mathrm{{MA_{{dec}}}} = {J3['MA_dec']:.0f}", color=C_ADAPTA, font_size=40))
        cifras.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to([4.6, 1.2, 0])
        self.play(FadeIn(cifras), run_time=0.6)
        rot.mostrar(dato_pie("nadie ve cual paga"), zona="abajo", run_time=0.5)
        self.wait(2.8)

        tab2 = tablero(8)
        self.play(FadeOut(tab), FadeIn(tab2), *[f.animate.move_to([x0, y, 0]) for f, y in zip(fichas, ys)],
                  run_time=0.9)
        jugar(8, tab2, 10, 0.26)
        cifras2 = VGroup(MathTex(rf"\mathrm{{MA}} = {J8['MA']:.0f}", color=C_PRIV, font_size=40),
                         MathTex(rf"\mathrm{{MA_{{dec}}}} = {J8['MA_dec']:.0f}", color=C_ADAPTA, font_size=40))
        cifras2.arrange(DOWN, buff=0.25, aligned_edge=LEFT).move_to(cifras, aligned_edge=LEFT)
        self.play(Transform(cifras, cifras2), run_time=0.6)
        rot.mostrar(dato_pie("necesaria, no suficiente"), zona="abajo", run_time=0.5)
        self.wait(3.6)
        rot.mostrar(cifra_pie(f"G2b exhibe: MA_dec >= {fmt(MA_DEC, 3)}"), zona="abajo", run_time=0.5)
        self.wait(4.0)

        cierre_leccion(self, rot, "El margen no promete ganancia.",
                       "Sin margen, no hay ganancia posible.",
                       tab2, fichas, etq, cifras)
