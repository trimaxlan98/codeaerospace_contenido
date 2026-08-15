class Clip3(Scene):
    """3 - Los nombres de Zernike. Las cuatro formas basicas de un frente
    torcido, cada una con su mapa sobre la pupila (cian negativo, ambar
    positivo): desenfoque y astigmatismo son las del oftalmologo, coma y
    esferica las que persiguen los fabricantes de telescopios. Cualquier
    frente es una suma de estas piezas. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Los nombres de Zernike"), zona="arriba",
                    run_time=0.6)

        # Cuatro tarjetas en fila: 8.5 de ancho, 2.6 de alto. Suben a
        # y = +0.42 para dejar la franja de -1.0 hacia abajo a los tags y a
        # la formula, y el pie a -3.05.
        tz = tarjetas_zernike(lado=1.85, sep=0.30)
        tz.move_to(UP * 0.42)
        m_des = tz.tarjeta("desenfoque")[1]
        m_ast = tz.tarjeta("astigmatismo")[1]
        m_com = tz.tarjeta("coma")[1]
        m_esf = tz.tarjeta("esferica")[1]

        # --- momento: las cuatro formas basicas ---------------------------
        rot.mostrar(pie_curso("Zernike dio nombre a las formas básicas de un "
                              "frente torcido."), zona="abajo")
        # Llevan ImageMobject (Group): FadeIn, nunca Transform.
        self.play(LaggedStart(*[FadeIn(t, shift=0.14 * UP)
                                for t in tz.tarjetas], lag_ratio=0.30),
                  run_time=2.2)
        self.add(tz)
        self.wait(4.9)

        # --- momento: las dos del oftalmologo ------------------------------
        rot.mostrar(pie_curso("Desenfoque y astigmatismo: los que corrige un "
                              "oftalmólogo."), zona="abajo")
        self.play(Indicate(VGroup(m_des, m_ast), color=C_MEDIDA,
                           scale_factor=1.05), run_time=1.3)
        t_ojo = tag_hud("el oftalmologo", font_size=18, color=C_MEDIDA)
        t_ojo.move_to(np.array([-2.15, -1.28, 0.0]))
        self.play(FadeIn(t_ojo, shift=0.10 * UP), run_time=0.5)
        self.wait(4.7)

        # --- momento: las dos del telescopio -------------------------------
        rot.mostrar(pie_curso("Coma y esférica: los que persiguen los "
                              "fabricantes de telescopios."), zona="abajo")
        self.play(Indicate(VGroup(m_com, m_esf), color=C_MEDIDA,
                           scale_factor=1.05), run_time=1.3)
        t_tel = tag_hud("el telescopio", font_size=18, color=C_MEDIDA)
        t_tel.move_to(np.array([2.15, -1.28, 0.0]))
        self.play(FadeIn(t_tel, shift=0.10 * UP), run_time=0.5)
        self.wait(4.7)

        # --- cierre --------------------------------------------------------
        rot.mostrar(pie_curso("Cualquier frente es una suma de estas "
                              "piezas."), zona="abajo")
        suma = MathTex(r"W(\rho, \varphi) = \sum_i c_i\, Z_i(\rho, \varphi)",
                       font_size=38, color=C_ONDA)
        suma.move_to(np.array([0.0, -2.05, 0.0]))
        self.play(Write(suma), run_time=1.4)
        self.wait(5.0)
