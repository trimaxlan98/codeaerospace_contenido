class Clip3(Scene):
    """3.2.3 - Angulo de deflexion maximo y choque desprendido (bow shock).

    El vertice de cada curva es una frontera fisica: mas alla de theta_max
    no existe ninguna onda pegada que resuelva el problema. El aire no se
    rinde — despega la onda del morro y la pone por delante, curva.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("Cuando el choque se suelta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        mapa = diagrama_theta_beta(machs=MACHS_DIAGRAMA, ancho=4.8, alto=2.7)
        mapa.move_to(LEFT * 3.0 + DOWN * 0.30)
        self.play(FadeIn(mapa.ejes), run_time=0.5)
        self.play(*[Create(mapa.curva(i)) for i in range(len(MACHS_DIAGRAMA))],
                  run_time=1.5)
        self.play(FadeIn(mapa.maximos), run_time=0.7)
        rot.mostrar(pie_curso("Los vértices de las curvas no son un adorno: "
                              "son una frontera."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        i = list(MACHS_DIAGRAMA).index(M_EJEMPLO)
        # El unico hueco limpio del diagrama es la esquina inferior derecha
        # (mucha deflexion y poca beta): ahi no pasa ninguna de las cuatro
        # curvas. Sin guia, porque cualquier linea desde el vertice hasta
        # ahi cruzaria las de Mach 3 y 5; el punto rojo y el pie bastan.
        punto = Dot(mapa.punto_maximo(i), radius=0.09, color=C_SUPER)
        cifra = MathTex(rf"\theta_{{max}} = {THETA_MAX:.1f}^\circ",
                        font_size=26, color=C_SUPER)
        cifra.move_to(mapa.ejes[0].get_end() + UP * 0.52 + LEFT * 1.10)
        self.play(FadeIn(punto, scale=1.6), FadeIn(cifra), run_time=0.7)
        rot.mostrar(pie_curso(f"A Mach {M_EJEMPLO:g} el aire admite girar "
                              f"como mucho {THETA_MAX:.1f} grados."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Pide más y no hay solución. Ninguna onda "
                              "pegada resuelve el problema."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: lo que hace el aire ----------------------------------
        # Cuna demasiado abierta y su onda desprendida: un arco por delante
        # que NO toca el cuerpo.
        semi = np.deg2rad(THETA_MAX + 12.0)
        largo_cuna = 1.5
        cuna = Polygon(
            ORIGIN,
            np.array([largo_cuna, largo_cuna * np.tan(semi), 0]),
            np.array([largo_cuna, -largo_cuna * np.tan(semi), 0]),
            stroke_width=3.0, color=C_TENUE,
            fill_color=C_EJE, fill_opacity=0.45)
        cuna.move_to(RIGHT * 3.4 + DOWN * 0.30)
        arco = Arc(radius=1.35, start_angle=PI - 1.15, angle=2.30,
                   arc_center=cuna.get_left() + RIGHT * 0.85,
                   color=C_SUPER, stroke_width=3.6)
        tag = Text("choque desprendido", font_size=19, color=C_SUPER)
        tag.next_to(VGroup(cuna, arco), DOWN, buff=0.26)

        self.play(FadeIn(cuna), run_time=0.7)
        rot.mostrar(pie_curso(f"Una cuña de "
                              f"{THETA_MAX + 12.0:.0f} grados, por ejemplo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        self.play(Create(arco), FadeIn(tag), run_time=0.8)
        rot.mostrar(pie_curso("El aire despega la onda del morro y la pone "
                              "por delante, curvada."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("En el eje esa onda es normal: detrás, el "
                              "flujo va subsónico y rodea el cuerpo."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
