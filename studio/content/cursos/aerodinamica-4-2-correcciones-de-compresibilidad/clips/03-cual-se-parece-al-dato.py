class Clip3(Scene):
    """4.2.3 - Comparacion con datos experimentales.

    Tres correcciones y un tunel de viento. La respuesta no es la que se
    espera: la mejor es la mas complicada, pero solo hasta el Mach critico —
    pasado el, las tres se equivocan de la misma manera, porque ninguna sabe
    que hay un choque. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("¿Cuál se parece al dato?")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        curvas = curvas_correcciones(cp0=CP0, m_max=M_MAX_CURVAS, ancho=5.0,
                                     alto=2.7)
        curvas.move_to(LEFT * 0.55 + DOWN * 0.35)
        self.play(FadeIn(curvas.ejes), run_time=0.5)
        self.play(*[Create(curvas.curva(i)) for i in range(3)], run_time=1.5)
        self.play(FadeIn(curvas.etiquetas), run_time=0.5)

        # Puntos de tunel: se dibujan sobre la curva de Laitone hasta el Mach
        # critico —que es la que mejor la sigue— y a partir de ahi se
        # apartan de las TRES, que es el mensaje del clip.
        mcr = mach_critico(CP0)
        machs = np.array([0.20, 0.40, 0.55, 0.65, 0.72, 0.78, 0.83])
        datos = VGroup()
        for m in machs:
            if m <= mcr:
                y = abs(curvas.valor(2, m))
            else:
                # Pasado el critico el dato real se aplana: aparece el choque
                # y la succion deja de crecer como dice cualquier teoria
                # lineal.
                y = abs(curvas.valor(2, mcr)) * (1 + 0.10 * (m - mcr) / 0.1)
            # `punto_de` da el punto sobre una curva concreta; aqui el dato
            # se aparta de todas, asi que se sitúa por su propia y.
            punto = curvas.punto_de(2, m) if m <= mcr else (
                curvas.punto_de(2, mcr)
                + UP * (y - abs(curvas.valor(2, mcr))) / curvas._ry[1]
                * curvas._alto)
            datos.add(Dot(punto, radius=0.055, color=C_TENUE))

        self.play(LaggedStart(*[FadeIn(d, scale=1.5) for d in datos],
                              lag_ratio=0.2), run_time=1.4)
        rot.mostrar(pie_curso("Y ahora, el túnel. Los puntos son lo que "
                              "hace el aire de verdad."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Hasta el Mach crítico, Laitone es la que "
                              "mejor los sigue."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- momento: donde todas fallan -----------------------------------
        corte = curvas.vertical_en(mcr, color=C_SUPER, grosor=1.6)
        tag = Text(f"Mcr = {mcr:.2f}", font=FUENTE_HUD, font_size=18,
                   color=C_SUPER)
        tag.next_to(corte.get_end(), UR, buff=0.06)
        self.play(Create(corte), FadeIn(tag), run_time=0.8)
        rot.mostrar(pie_curso("Pasado el crítico, los puntos se apartan de "
                              "las tres."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Y no es culpa de ninguna corrección: ahí "
                              "arriba hay un choque, y son teorías "
                              "lineales."), zona="abajo", run_time=0.5)
        self.wait(5.4)

        rot.mostrar(pie_curso("Ninguna sabe que existe."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
