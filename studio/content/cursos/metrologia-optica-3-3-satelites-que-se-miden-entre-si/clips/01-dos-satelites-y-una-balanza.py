class Clip1(Scene):
    """1 - Dos satelites y una balanza. GRACE-FO vuela en fila a 220 km;
    cuando una masa pasa por debajo tira mas del satelite que tiene mas
    cerca y la separacion respira (la firma antisimetrica de `delta_nm`,
    exagerada en pantalla). Medir esa distancia es pesar lo que hay
    debajo: delta d <-> delta g. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Dos satélites y una balanza"),
                    zona="arriba", run_time=0.6)

        # La pieza mide 6.40 x ~4.1: al 0.95 ocupa 6.08 x ~3.9 y cabe en la
        # banda central (-2.28 .. +1.68) dejando aire al titulo y al pie.
        # Nace en frac = 0 (la masa entra por la izquierda) y su rotulo
        # propio ya lleva "220 km" y el "delta" vivo en nanometros.
        par = grace_par(SEP_GRACE_KM, amplitud_nm=1.0, frac=0.0)
        par.scale(0.95).move_to(DOWN * 0.28)

        def barrer(desde, hasta, t):
            """La masa recorre el trozo [desde, hasta] de la pasada."""
            self.play(UpdateFromAlphaFunc(
                par, lambda m, a: m.a_t(desde + (hasta - desde) * a)),
                run_time=t, rate_func=linear)

        # --- momento: el par en orbita ---------------------------------
        rot.mostrar(pie_curso("GRACE-FO: dos satélites en fila, a 220 "
                              "kilómetros, dando vueltas a la Tierra."),
                    zona="abajo")
        self.play(FadeIn(par, shift=0.12 * UP), run_time=0.9)
        ficha = VGroup(
            tag_hud("GRACE-FO", font_size=18, color=C_OBJETO),
            tag_hud("dos satelites en fila", font_size=13, color=C_TENUE),
        ).arrange(DOWN, buff=0.12)
        ficha.move_to(np.array([-4.45, 1.15, 0.0]))
        self.play(FadeIn(ficha), run_time=0.5)
        self.wait(4.8)

        # --- momento: la masa los separa -------------------------------
        rot.mostrar(pie_curso("Cuando el primero pasa sobre una masa, la "
                              "gravedad lo tira un poco más: la distancia "
                              "cambia."), zona="abajo")
        aviso = tag_hud("movimiento exagerado", font_size=13, color=C_TENUE)
        aviso.move_to(np.array([-1.75, -2.52, 0.0]))
        self.play(FadeIn(aviso), run_time=0.45)
        barrer(0.0, 0.62, 5.4)
        self.wait(2.2)

        # --- momento: medir la distancia es pesar ----------------------
        rot.mostrar(pie_curso("Medir esa distancia con precisión es pesar "
                              "lo que hay debajo."), zona="abajo")
        # Columna derecha libre: la pieza acaba en x = +2.56 y la marca de
        # agua vive mas abajo, asi que la relacion cabe en (3.55, 0.95).
        relacion = MathTex(r"\Delta d \;\leftrightarrow\; \Delta g",
                           font_size=38, color=C_MEDIDA)
        relacion.move_to(np.array([3.55, 0.95, 0.0]))
        pie_rel = tag_hud("distancia -> masa", font_size=13, color=C_TENUE)
        pie_rel.next_to(relacion, DOWN, buff=0.22)
        self.play(Write(relacion), run_time=1.1)
        self.play(FadeIn(pie_rel), run_time=0.45)
        self.wait(4.4)

        # --- cierre ----------------------------------------------------
        rot.mostrar(pie_curso("Dos satélites son una balanza si sabes medir "
                              "lo que los separa."), zona="abajo")
        barrer(0.62, 1.0, 3.4)
        self.wait(5.0)
