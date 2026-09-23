class Clip4(Scene):
    """2.2.4 - La ablacion de la tesis: cambiar el mezclador monotono no
    lineal de QMIX por la suma de VDN. Con el mismo protocolo, las dos
    superan a la estatica y quedan pegadas: la no linealidad no se gana su
    sitio en este entorno. Cierre. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("La complejidad no paga"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        y0, alto = -2.2, 4.2
        vmax = max(v["oraculo"] for v in VQ)
        centros = [-3.6, 0.0, 3.6]
        suelo = Line([-6.0, y0, 0], [6.0, y0, 0], stroke_color=C_TENUE, stroke_width=2)
        sem = VGroup(*[tag_hud(f"semilla {v['semilla']}", font_size=17, color=C_TENUE)
                       .move_to([c, y0 - 0.35, 0]) for c, v in zip(centros, VQ)])
        self.play(FadeIn(suelo), FadeIn(sem), run_time=0.6)

        def barra(x, val, color, contorno=False):
            h = alto * val / vmax
            r = Rectangle(width=0.8, height=h, stroke_color=color, stroke_width=3 if contorno else 0,
                          fill_color=color, fill_opacity=0.0 if contorno else 1.0)
            if contorno:
                r = DashedVMobject(r, num_dashes=36)
            return r.move_to([x, y0 + h / 2, 0])

        series = [("estatica", C_ESTATICA, -0.9), ("VDN", C_OK, 0.0), ("QMIX", C_ADAPTA, 0.9)]
        ley = VGroup(*[tag_hud(n, font_size=17, color=c) for n, c, _ in series],
                     tag_hud("oraculo", font_size=17, color=C_PRIV)).arrange(RIGHT, buff=0.6)
        ley.move_to([0, 2.45, 0])
        for (nombre, col, dx), e in zip(series, ley):
            clave = {"estatica": "estatica", "VDN": "vdn", "QMIX": "qmix"}[nombre]
            bs = [barra(c + dx, v[clave], col) for c, v in zip(centros, VQ)]
            self.play(*[GrowFromEdge(b, DOWN) for b in bs], FadeIn(e), run_time=0.9)
            self.wait(2.2)
        self.wait(1.2)
        orc = [DashedLine([c - 1.4, y0 + alto * v["oraculo"] / vmax, 0],
                          [c + 1.4, y0 + alto * v["oraculo"] / vmax, 0], dash_length=0.12,
                          stroke_color=C_PRIV, stroke_width=3) for c, v in zip(centros, VQ)]
        self.play(*[FadeIn(o) for o in orc], FadeIn(ley[3]), run_time=0.8)
        rot.mostrar(dato_pie("mejor evaluacion, fase 0 G2b"), zona="abajo", run_time=0.5)
        self.wait(4.4)
        dif = [100 * (v["vdn"] - v["qmix"]) / v["qmix"] for v in VQ]
        rot.mostrar(cifra_pie(f"VDN - QMIX: {min(dif):+.1f} a {max(dif):+.1f} %"), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)

        cierre_leccion(self, rot, "Se entrena en equipo",
                       "y se decide por separado.",
                       suelo, sem, ley, *orc, *[m for m in self.mobjects
                                                if isinstance(m, Rectangle)])
