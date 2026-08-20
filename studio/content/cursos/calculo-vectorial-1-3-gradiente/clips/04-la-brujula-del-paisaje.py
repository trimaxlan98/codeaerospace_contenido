class Clip4(Scene):
    """1.3.4 - Ascenso por gradiente: seguir la flecha lleva a la cima (a
    la mas cercana, no a la mas alta). Cierre de la leccion. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La brújula del paisaje")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        def por_arco(linea):
            """Recorrido de la linea de flujo a velocidad CONSTANTE en
            pantalla: reparametriza `.puntos` por longitud de arco."""
            pts = linea.puntos
            s = np.concatenate([[0.0], np.cumsum(
                np.linalg.norm(np.diff(pts, axis=0), axis=1))])

            def pos(a):
                u = float(np.clip(a, 0.0, 1.0)) * s[-1]
                return np.array([np.interp(u, s, pts[:, 0]),
                                 np.interp(u, s, pts[:, 1])])

            return pos

        # --- momento: el mapa y el altimetro -------------------------------
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100,
                            opacidad=0.7)
        self.play(FadeIn(pl), FadeIn(mapa), run_time=1.0)
        rot.mostrar(pie_curso("Si el gradiente apunta a la subida, seguirlo "
                              "tendría que llevarnos a la cima."),
                    zona="abajo", run_time=0.5)

        dot = Dot(pl.p(P0_ASCENSO), radius=0.095, color=C_VEC)
        etiqueta = tag_hud("altimetro f =", font_size=20)
        alti = DecimalNumber(PAISAJE(P0_ASCENSO), num_decimal_places=2,
                             color=C_CALCULO, font_size=34)
        grupo_alti = VGroup(etiqueta, alti).arrange(RIGHT, buff=0.18)
        grupo_alti.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        alti.add_updater(lambda a: a.set_value(
            PAISAJE(pl.coords_de(dot.get_center()))))
        alti.add_updater(lambda a: a.next_to(etiqueta, RIGHT, buff=0.18))
        self.play(FadeIn(dot, scale=0.5), FadeIn(grupo_alti), run_time=0.7)
        self.wait(3.6)

        # --- momento: el ascenso por gradiente ------------------------------
        rot.mostrar(pie_curso("Ascenso por gradiente: leer la flecha, dar "
                              "un paso en su dirección y volver a leer."),
                    zona="abajo", run_time=0.5)
        subida = linea_flujo(pl, campo_gradiente(PAISAJE), P0_ASCENSO,
                             T=T_ASCENSO, color=C_FLUJO, grosor=3.0)
        pos = por_arco(subida)
        # Lecturas de la brujula: solo la DIRECCION del gradiente, a largo
        # fijo. A escala real la primera seria invisible (el llano del
        # sureste tiene |grad f| ~ 0.02) y no se veria a donde apunta.
        def _brujula(a):
            q = pos(a)
            u = grad_num(PAISAJE, q)
            u = u / np.linalg.norm(u)
            return flecha_libre(pl, q, q + u * 0.8, color=C_GRAD,
                                grosor=3.6, punta_len=0.20)

        brujulas = VGroup(*[_brujula(a)
                            for a in (0.14, 0.34, 0.52, 0.68)])
        self.play(LaggedStart(*[GrowArrow(f) for f in brujulas],
                              lag_ratio=0.25), run_time=1.4)
        self.play(Create(subida), run_time=1.6)
        marcha = ValueTracker(0.0)
        dot.add_updater(lambda d: d.move_to(pl.p(pos(marcha.get_value()))))
        self.play(marcha.animate.set_value(1.0), run_time=5.0,
                  rate_func=linear)
        self.wait(1.6)

        # --- momento: el altimetro nunca baja -------------------------------
        z_alta = PAISAJE(subida.puntos[-1])
        rot.mostrar(pie_curso("El altímetro no ha bajado ni una vez: cada "
                              "paso cruza un nivel hacia arriba."),
                    zona="abajo", run_time=0.5)
        cima = tag_hud(f"cima = {fmt(z_alta, 2)}", font_size=20,
                       color=C_GRAD)
        cima.next_to(pl.p(subida.puntos[-1]), UR, buff=0.18)
        self.play(FadeIn(cima), Indicate(dot, color=C_GRAD,
                                         scale_factor=1.5), run_time=1.0)
        self.wait(3.6)

        # --- momento: la cima mas CERCANA, no la mas alta -------------------
        rot.mostrar(pie_curso("Pero el gradiente es miope: sube a la cima "
                              "más cercana, no a la más alta."),
                    zona="abajo", run_time=0.5)
        vecina = linea_flujo(pl, campo_gradiente(PAISAJE), P0_CERCA,
                             T=T_CERCA, color=C_FLUJO, grosor=3.0)
        pos2 = por_arco(vecina)
        dot2 = Dot(pl.p(P0_CERCA), radius=0.095, color=C_VEC)
        alti.clear_updaters()
        alti.add_updater(lambda a: a.set_value(
            PAISAJE(pl.coords_de(dot2.get_center()))))
        alti.add_updater(lambda a: a.next_to(etiqueta, RIGHT, buff=0.18))
        self.play(FadeIn(dot2, scale=0.5), Create(vecina), run_time=1.2)
        marcha2 = ValueTracker(0.0)
        dot2.add_updater(lambda d: d.move_to(pl.p(pos2(marcha2.get_value()))))
        self.play(marcha2.animate.set_value(1.0), run_time=3.6,
                  rate_func=linear)
        z_baja = PAISAJE(vecina.puntos[-1])
        cima2 = tag_hud(f"cima = {fmt(z_baja, 2)}", font_size=20,
                        color=C_GRAD)
        cima2.next_to(pl.p(vecina.puntos[-1]), UL, buff=0.18)
        self.play(FadeIn(cima2), run_time=0.5)
        self.wait(3.2)

        # --- cierre ---------------------------------------------------------
        dot.clear_updaters()
        dot2.clear_updaters()
        alti.clear_updaters()
        cierre_leccion(self, rot,
                       "El gradiente apunta a la subida.",
                       "Seguirlo es escalar.",
                       "Siguiente lección: el campo, una flecha en cada punto.",
                       pl, mapa, subida, vecina, brujulas, dot, dot2,
                       grupo_alti, cima, cima2)
