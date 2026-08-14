class Clip3(Scene):
    """2.2.3 - Relaciones M2, p2/p1, T2/T1, rho2/rho1 en funcion de M1.

    Las tres razones crecen sin techo... menos una. La densidad se para en
    seis por mucho Mach que le eches, y ese tope no es un accidente
    numerico: es (gamma+1)/(gamma-1), y explica por que un vehiculo
    hipersonico no puede confiar en comprimir mas. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El salto, en números")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curvas = curvas_choque(grupo="saltos", m_max=M_MAX_CURVAS,
                               ancho=5.0, alto=2.7)
        curvas.move_to(LEFT * 0.55 + DOWN * 0.35)
        self.play(FadeIn(curvas.ejes), run_time=0.6)
        rot.mostrar(pie_curso("Cuánto sube cada cosa al cruzar el choque, "
                              "según el Mach con que llegues."),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)
        self.play(LaggedStart(*[Create(c) for c in curvas.curvas],
                              lag_ratio=0.35), run_time=2.0)
        self.play(FadeIn(curvas.etiquetas), run_time=0.6)
        self.wait(2.6)

        # --- momento: el choque de referencia del modulo -------------------
        # Cifras y puntos salen de la misma funcion; el corte lo dibuja la
        # pieza sobre sus propias coordenadas.
        corte = curvas.vertical_en(M1_REF, color=C_TENUE)
        self.play(Create(corte), run_time=0.6)
        marcas = VGroup()
        x_cifras = curvas.ejes[1].get_left()[0] - 0.62
        for i in range(3):
            punto = Dot(curvas.punto_de(i, M1_REF), radius=0.07,
                        color=curvas.color_de(i))
            cifra = Text(f"{curvas.valor(i, M1_REF):.2f}", font=FUENTE_HUD,
                         font_size=18, color=curvas.color_de(i))
            cifra.move_to([x_cifras, punto.get_center()[1], 0])
            marcas.add(VGroup(punto, cifra))
        self.play(LaggedStart(*[FadeIn(m, scale=1.4) for m in marcas],
                              lag_ratio=0.35), run_time=1.2)

        rot.mostrar(pie_curso(f"A Mach {M1_REF:g}: la presión se multiplica "
                              f"por {SALTO['p2/p1']:.1f} y la temperatura "
                              f"por {SALTO['T2/T1']:.2f}."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        # --- momento: la que no crece --------------------------------------
        rot.mostrar(pie_curso("Pero mira la densidad. Se está aplanando."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        tope = curvas.horizontal_en(TOPE_COMPRESION, color=C_SUB)
        tag_tope = Text(f"{TOPE_COMPRESION:.0f}", font=FUENTE_HUD,
                        font_size=18, color=C_SUB)
        tag_tope.next_to(tope.get_start(), LEFT, buff=0.16)
        self.play(Create(tope), FadeIn(tag_tope), run_time=0.8)
        rot.mostrar(formula_pie(r"\frac{\rho_2}{\rho_1}\Big|_{\max} = "
                                r"\frac{\gamma+1}{\gamma-1} = "
                                rf"{TOPE_COMPRESION:.0f}", color=C_SUB),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Por mucho Mach que le eches, un choque no "
                              "comprime el aire más de seis veces."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
