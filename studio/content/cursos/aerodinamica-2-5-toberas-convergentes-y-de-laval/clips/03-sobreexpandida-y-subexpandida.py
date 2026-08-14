class Clip3(Scene):
    """2.5.3 - Choque interno, tobera sobreexpandida y subexpandida.

    Que la tobera este adaptada o no lo decide la presion de fuera, y el
    chorro lo confiesa: si sale a mas presion que el ambiente se abre, si
    sale a menos se estrangula, y en ambos casos aparecen los diamantes de
    Mach. (~42 s)"""

    def _chorro(self, x, apertura, color, nodos=3):
        """Pluma esquematica: una cinta que se abre o se cierra y los
        diamantes que deja dentro."""
        largo, base = 3.0, 0.34
        pluma = VGroup()
        for signo in (1, -1):
            borde = VMobject(color=color, stroke_width=2.2)
            borde.set_points_smoothly([
                np.array([0, signo * base, 0]),
                np.array([largo * 0.5, signo * base * apertura, 0]),
                np.array([largo, signo * base * (2 - apertura) * 0.9, 0])])
            pluma.add(borde)
        for k in range(nodos):
            cx = largo * (k + 0.5) / nodos
            rombo = Polygon(
                np.array([cx - 0.22, 0, 0]), np.array([cx, base * 0.55, 0]),
                np.array([cx + 0.22, 0, 0]), np.array([cx, -base * 0.55, 0]),
                stroke_width=1.8, color=C_SUPER).set_stroke(opacity=0.85)
            pluma.add(rombo)
        return pluma.move_to(x)

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Sobreexpandida y subexpandida")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        salida = MathTex(rf"\frac{{p_e}}{{p_0}} = "
                         rf"{perfil_tobera(area_garganta=AREA_GARGANTA, regimenes=('diseno',)).salida('diseno'):.4f}",
                         font_size=38, color=C_SUPER)
        salida.move_to(UP * 2.05)
        self.play(FadeIn(salida), run_time=0.6)
        rot.mostrar(pie_curso("Una tobera solo está adaptada a UNA presión "
                              "de fuera. La suya."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: los tres casos ---------------------------------------
        casos = (("adaptada", 1.0, C_SUB, 0),
                 ("sobreexpandida", 0.62, C_TRANS, 3),
                 ("subexpandida", 1.55, C_HIPER, 3))
        pies = ("Si sale a la presión de fuera, el chorro va recto. Nada que "
                "corregir.",
                "Si sale a MENOS presión que fuera, el aire de alrededor lo "
                "aplasta: sobreexpandida.",
                "Y si sale a más, se abre solo en cuanto puede: "
                "subexpandida.")
        alturas = (1.15, -0.15, -1.45)
        plumas = VGroup()
        for (nombre, apertura, color, nodos), pie, y in zip(casos, pies,
                                                            alturas):
            pluma = self._chorro(RIGHT * 0.9 + UP * y, apertura, color, nodos)
            tag = Text(nombre, font_size=20, color=color)
            tag.next_to(pluma, LEFT, buff=0.45)
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            self.play(FadeIn(VGroup(pluma, tag), shift=0.12 * RIGHT),
                      run_time=0.8)
            plumas.add(VGroup(pluma, tag))
            self.wait(4.4)

        rot.mostrar(pie_curso("Esos rombos son ondas rebotando dentro del "
                              "chorro: los diamantes de Mach."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Un cohete despega sobreexpandido y sube "
                              "subexpandido. La atmósfera se va yendo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.4)
