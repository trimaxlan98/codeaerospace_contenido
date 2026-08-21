class Clip2(Scene):
    """3.1.2 - La escalera de los enlaces: FSPL medido con fspl_db para
    LEO, GEO, Marte y Voyager -- y por que aun asi se oye (curso 13).
    (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La escalera de los enlaces")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        base_y = -1.7
        escala = 3.9 / (FSPL_TOPE - FSPL_BASE)
        xs = [-4.8, -1.6, 1.6, 4.8]
        ancho_barra = 1.15
        eje = Line([-6.2, base_y, 0], [6.2, base_y, 0], color=C_EJE,
                  stroke_width=2.0)

        def hacer_barra(nombre, v, x):
            h = (v - FSPL_BASE) * escala
            b = Rectangle(width=ancho_barra, height=h, stroke_color=C_SENAL,
                         fill_color=C_SENAL, fill_opacity=0.55,
                         stroke_width=2.0)
            b.move_to([x, base_y + h / 2, 0])
            et = tag_hud(nombre, font_size=17, color=C_TENUE)
            et.next_to(b, DOWN, buff=0.15)
            cif = tag_hud(f"{fmt(v, 1)} dB", font_size=18, color=C_CIFRA)
            cif.next_to(b, UP, buff=0.1)
            return b, et, cif

        # --- momento: cuatro presupuestos, la misma formula -----------------
        rot.mostrar(pie_curso("Cuatro presupuestos de enlace, todos con la "
                              "misma formula; el eje no arranca en 0 dB "
                              "para que quepan los cuatro."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(eje), run_time=0.6)
        self.wait(2.6)

        pies = [
            "El enlace mas cercano: una LEO a 550 km, 12 GHz.",
            "Geoestacionaria: 35 786 km, la que nunca se mueve del cielo.",
            "Marte, cuando esta lejos: 225 millones de km.",
            "Y el limite que aun habla: Voyager, a 24 600 millones de km.",
        ]
        barras = []
        for i, (nombre, d, f, v) in enumerate(ESCALERA):
            rot.mostrar(pie_curso(pies[i]), zona="abajo", run_time=0.5)
            b, et, cif = hacer_barra(nombre, v, xs[i])
            barras.append(b)
            anims = [GrowFromEdge(b, DOWN), FadeIn(et), FadeIn(cif)]
            if i > 0:
                paso = Line(barras[i - 1].get_top(), b.get_top(),
                           color=C_EJE, stroke_width=1.6)
                anims.append(Create(paso))
            self.play(*anims, run_time=1.3)
            self.wait(2.8 if i < 3 else 1.2)

        # --- momento: y aun asi se oye (curso 13, citado UNA vez) -----------
        rot.mostrar(pie_curso("Y aun asi se oye: el presupuesto del enlace "
                              "-- antenas, ganancia, codigos, visto en "
                              "'Cerrar el enlace' (curso 13) -- compensa "
                              "cada escalon."),
                    zona="abajo", run_time=0.5)
        self.wait(6.0)
