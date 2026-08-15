class Clip3(Scene):
    """3 - Desenvolver la fase. El detector solo da la fase modulo 2 pi:
    dientes de sierra. Desenvolver (np.unwrap) es sumar una vuelta en cada
    uno de los 6 saltos CONTADOS sobre los datos, y lo que queda es la rampa
    continua de la forma: fase_real = fase + 2 pi k. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 02")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Desenvolver la fase"), zona="arriba",
                    run_time=0.6)

        # --- geometria: los dos paneles, envuelta (izq) y desenvuelta -------
        # mapa_fase mide 8.59 x 2.08: escalado 1.25 llena la banda alta sin
        # tocar los margenes (los rotulos laterales llegan a x ~ 5.3). Se
        # sube a y = +0.72 para dejar la banda baja al MathTex; los paneles
        # son VGroup(eje_x, eje_y, curva, titulo, rotulo-de-rango).
        mf = mapa_fase(sag_ondas=3.0)
        mf.scale(1.25).move_to(UP * 0.72)
        p_env, p_des = mf.envuelta, mf.desenvuelta
        curva_env, curva_des = p_env[2], p_des[2]
        ejes_env = VGroup(p_env[0], p_env[1])
        ejes_des = VGroup(p_des[0], p_des[1])

        def punto_panel(panel, datos, i, y_min, y_max):
            """Muestra i de un panel -> punto de ESCENA, leyendo los ejes ya
            colocados (el mapeo del panel es lineal en el indice)."""
            x0 = panel[0].get_left()[0]
            x1 = panel[0].get_right()[0]
            y0 = panel[1].get_bottom()[1]
            y1 = panel[1].get_top()[1]
            t = float(i) / (len(datos) - 1.0)
            v = (datos[i] - y_min) / max(y_max - y_min, 1e-12)
            return np.array([x0 + t * (x1 - x0), y0 + v * (y1 - y0), 0.0])

        env = mf.datos_envuelta
        i_saltos = np.nonzero(np.abs(np.diff(env)) > PI)[0]
        # Un marcador por salto, en el extremo +pi del diente: una linea
        # vertical se confundiria con el propio salto (la poligonal ya lo
        # dibuja casi vertical), asi que el marcador es un punto ambar.
        marcas = VGroup()
        for i in i_saltos:
            j = i if env[i] > env[i + 1] else i + 1
            marcas.add(Dot(punto_panel(p_env, env, j, -PI, PI), radius=0.075,
                           color=C_ONDA))
        t_saltos = tag_hud(f"{mf.saltos()} saltos de 2 pi", font_size=15,
                           color=C_ONDA)
        t_saltos.next_to(p_env[0], DOWN, buff=0.26)

        form = MathTex(r"\phi_{\mathrm{real}} = \phi + 2\pi k", font_size=42,
                       color=C_MEDIDA)
        form.move_to(np.array([0.0, -1.85, 0.0]))

        # --- momento: la fase envuelta ---------------------------------------
        rot.mostrar(pie_curso("La fase envuelta salta cada vuelta: dientes de "
                              "sierra."), zona="abajo")
        self.play(Create(ejes_env), FadeIn(p_env[3]), FadeIn(p_env[4]),
                  run_time=0.8)
        self.play(Create(curva_env), run_time=2.2)
        self.wait(4.2)

        # --- momento: sumar una vuelta en cada salto -------------------------
        rot.mostrar(pie_curso("Desenvolver es sumar una vuelta cada vez que "
                              "salta."), zona="abajo")
        self.play(LaggedStart(*[FadeIn(m) for m in marcas], lag_ratio=0.30),
                  run_time=1.4)
        self.play(FadeIn(t_saltos), run_time=0.4)
        self.play(Create(ejes_des), FadeIn(p_des[3]), FadeIn(p_des[4]),
                  run_time=0.8)
        self.play(Create(curva_des), run_time=2.6)
        self.wait(3.4)

        # --- momento: la rampa continua es la forma --------------------------
        rot.mostrar(pie_curso("Queda una rampa continua: la altura real, "
                              "vuelta a vuelta."), zona="abajo")
        self.play(Write(form), run_time=1.2)
        self.play(Indicate(curva_des, scale_factor=1.03, color=C_MEDIDA),
                  run_time=1.0)
        self.wait(4.2)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("La fase se pliega. Desenvolverla es leer la "
                              "forma."), zona="abajo")
        self.wait(5.5)
