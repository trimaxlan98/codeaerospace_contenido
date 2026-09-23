class Clip3(Scene):
    """1.4.3 - Tres agentes con tres acciones cada uno: 27 acciones
    conjuntas. La mejor FIJA de las 27 es que los tres usen la ruta
    alterna. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Tres que deciden"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        acc = ["bajo", "alto", "ruta"]
        cols = [C_ENLACE, C_PRIV, C_OK]
        # las 27 como tres capas de 3x3 (capa = accion del gateway)
        celdas = {}
        grupo = VGroup()
        for g in range(3):
            for s2 in range(3):
                for s1 in range(3):
                    x = -4.6 + g * 3.3 + s1 * 0.78
                    y = 1.2 - s2 * 0.78
                    c = Square(side_length=0.66, stroke_color=C_TENUE, stroke_width=2)
                    c.move_to([x, y, 0])
                    celdas[(s1, s2, g)] = c
                    grupo.add(c)
        capas = VGroup(*[tag_hud(f"gateway: {acc[g]}", font_size=16, color=cols[g])
                         .move_to([-4.6 + g * 3.3 + 0.78, 2.05, 0]) for g in range(3)])
        e1 = tag_hud("satelite 1", font_size=16, color=C_TENUE).move_to([-3.8, -1.0, 0])
        e2 = tag_hud("satelite 2", font_size=16, color=C_TENUE).rotate(PI / 2).move_to([-5.45, 0.42, 0])
        self.play(LaggedStart(*[Create(c) for c in grupo], lag_ratio=0.02), FadeIn(capas),
                  FadeIn(e1), FadeIn(e2), run_time=2.6)
        self.wait(2.6)
        rot.mostrar(cifra_pie(f"{N_ACC}^{N_AG} = {N_CONJ} conjuntas"), zona="abajo", run_time=0.5)
        self.wait(3.4)

        # la recompensa de las cinco mejores fijas (G1, semilla 42) enciende sus celdas
        vals = sorted(((float(v), k) for k, v in TOP5.items()), reverse=True)
        vmax = vals[0][0]
        for v, k in vals[::-1]:
            s1, s2, g = (int(ch) for ch in k)
            c = celdas[(s1, s2, g)]
            self.play(c.animate.set_fill(C_ADAPTA, opacity=0.25 + 0.6 * (v / vmax) ** 4),
                      run_time=0.45)
        self.wait(1.0)
        mejor = vals[0][1]
        s1, s2, g = (int(ch) for ch in mejor)
        marco = SurroundingRectangle(celdas[(s1, s2, g)], color=C_ESTATICA, buff=0.06, stroke_width=5)
        self.play(Create(marco), run_time=0.7)
        rot.mostrar(dato_pie(f"mejor fija: {','.join(mejor)} (todos ruta)"), zona="abajo",
                    run_time=0.5)
        self.wait(5.6)
        rot.mostrar(dato_pie(f"recompensa {vmax:,.0f}".replace(",", " ")), zona="abajo", run_time=0.5)
        self.wait(5.4)
        self.wait(2.2)
