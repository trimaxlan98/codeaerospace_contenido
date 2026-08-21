class Clip2(Scene):
    """1.3.2 - La derivada direccional mide la subida en cada direccion;
    el maximo se alcanza justo en la del gradiente. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La máxima subida")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el abanico de direcciones ----------------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100,
                            opacidad=0.35)
        dot = Dot(pl.p(P_G), radius=0.085, color=C_VEC)
        self.play(FadeIn(pl), FadeIn(mapa), FadeIn(dot), run_time=0.9)
        rot.mostrar(pie_curso("Desde el punto puedo salir en cualquier "
                              "dirección. ¿Cuánto sube el terreno en cada "
                              "una?"), zona="abajo", run_time=0.5)
        rayos = VGroup(*[flecha_libre(pl, P_G, P_G + u * R_ABANICO,
                                      color=C_CIFRA, grosor=3.0,
                                      punta_len=0.16)
                         for u in DIRS_ABANICO])
        self.play(LaggedStart(*[GrowArrow(f) for f in rayos],
                              lag_ratio=0.16), run_time=2.2)
        self.wait(3.2)

        # --- momento: medir la subida de cada una --------------------------
        rot.mostrar(pie_curso("Lo medimos: cuánto sube el terreno por cada "
                              "paso dado en esa dirección."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup()
        for u, d in zip(DIRS_ABANICO, DERIV_ABANICO):
            t = tag_hud(fmt(d, 2), font_size=19)
            t.move_to(pl.p(P_G + u * R_TAG))
            cifras.add(t)
        self.play(LaggedStart(*[FadeIn(c, scale=0.6) for c in cifras],
                              lag_ratio=0.16), run_time=2.4)
        self.wait(3.4)

        # --- momento: negativas y las dos que dan cero ---------------------
        rot.mostrar(pie_curso("Las de enfrente salen negativas: por ahí se "
                              "baja. Y dos no hacen ni lo uno ni lo otro."),
                    zona="abajo", run_time=0.5)
        self.play(*[Indicate(cifras[k], color=C_VEC, scale_factor=1.4)
                    for k in K_BAJA], run_time=1.1)
        self.play(*[Indicate(cifras[k], color=C_RES, scale_factor=1.4)
                    for k in K_CERO], run_time=1.1)
        self.wait(3.2)

        # --- momento: la ganadora ------------------------------------------
        rot.mostrar(pie_curso("Y una gana a todas las demás."), zona="abajo",
                    run_time=0.5)
        otros = [k for k in range(N_ABANICO) if k != K_GANA]
        self.play(*[rayos[k].animate.set_opacity(0.22) for k in otros],
                  *[cifras[k].animate.set_opacity(0.3) for k in otros],
                  rayos[K_GANA].animate.set_color(C_GRAD),
                  cifras[K_GANA].animate.set_color(C_GRAD),
                  run_time=1.0)
        self.wait(3.6)

        # --- momento: la ganadora ES el gradiente --------------------------
        rot.mostrar(pie_curso("Es exactamente la del gradiente. Y su subida "
                              "es lo que mide esa flecha."),
                    zona="abajo", run_time=0.5)
        gr = flecha_libre(pl, P_G, P_G + G * ESC_GRAD, color=C_GRAD,
                          grosor=5.5, punta_len=0.26)
        self.play(GrowArrow(gr), run_time=0.9)
        panel = panel_derecha(MathTex(r"|\nabla f| = " + fmt(G_MOD, 2),
                                      font_size=34, color=C_GRAD))
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        # --- momento: la formula -------------------------------------------
        rot.mostrar(formula_pie(r"D_{\hat u}\,f = \nabla f \cdot \hat u"
                                r" = |\nabla f|\,\cos\theta"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
