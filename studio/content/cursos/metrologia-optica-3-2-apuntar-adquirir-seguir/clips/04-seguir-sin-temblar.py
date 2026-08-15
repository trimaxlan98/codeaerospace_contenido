class Clip4(Scene):
    """4 - Seguir sin temblar. El detector de cuatro cuadrantes convierte la
    posicion de la mancha en dos voltajes (ex, ey): en cuanto se corre, las
    barras lo dicen y el espejo rapido la devuelve al centro. Y como el otro
    se aleja a 7.6 km/s, la luz llega corrida 4.9 GHz: el Doppler optico
    tambien se sigue. Cierra la leccion a pantalla limpia. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Seguir sin temblar"), zona="arriba",
                    run_time=0.6)

        # Detector a la IZQUIERDA (sus dos barras horizontales llegan hasta
        # x = 0.5); la columna del Doppler vive de x = 2.2 a la derecha.
        det = detector_cuadrantes()
        det.scale(1.20)
        det.move_to(LEFT * 1.15 + UP * 0.05)

        def cifra(texto, y, color=None, font_size=16):
            t = tag_hud(texto, font_size=font_size, color=color)
            t.move_to(np.array([2.2, y, 0.0]), aligned_edge=LEFT)
            return t

        # --- momento: el detector ---------------------------------------------
        rot.mostrar(pie_curso("Un detector de cuatro cuadrantes vigila la "
                              "mancha del otro haz."), zona="abajo")
        self.play(FadeIn(det, shift=0.14 * UP), run_time=0.9)
        et_mancha = tag_junto(det.cuadro, "la mancha del otro haz", UP,
                              buff=0.20, font_size=18, color=C_FRANJA)
        self.play(FadeIn(et_mancha), run_time=0.4)
        self.wait(4.8)

        # --- momento: el lazo de control ---------------------------------------
        rot.mostrar(pie_curso("Si la mancha se corre, la diferencia entre "
                              "cuadrantes lo dice y un espejo la devuelve."),
                    zona="abajo")
        # `a_mancha` MUTA (rehace barras y lectura): dos ValueTracker y el
        # updater se limpia en cuanto acaba el lazo.
        mx, my = ValueTracker(0.0), ValueTracker(0.0)

        def _lazo(m):
            # El renderer congela la lista de mobjects "en movimiento" al
            # empezar el play: las barras y la lectura que `a_mancha`
            # SUSTITUYE se seguirian dibujando encima de las nuevas (las
            # cifras salian dobles). Se apagan al relevarlas.
            viejos = (m.barra_x, m.barra_y, m.lectura)
            m.a_mancha(mx.get_value(), my.get_value())
            for v in viejos:
                v.set_opacity(0.0)

        det.add_updater(_lazo)
        self.play(mx.animate.set_value(0.30), my.animate.set_value(-0.20),
                  run_time=1.2)
        self.wait(1.3)
        self.play(mx.animate.set_value(-0.24), my.animate.set_value(0.28),
                  run_time=1.0)
        self.wait(1.1)
        self.play(mx.animate.set_value(0.0), my.animate.set_value(0.0),
                  run_time=1.0)
        det.clear_updaters()
        det.a_mancha(0.0, 0.0)
        self.wait(2.2)

        # --- momento: el Doppler optico -----------------------------------------
        rot.mostrar(pie_curso(f"Y como el otro se mueve, la luz llega corrida "
                              f"{DOPPLER_GHZ:.1f} gigahercios: el Doppler "
                              f"óptico también se sigue."), zona="abajo")
        t_v = cifra(f"v = {V_LEO_KMS:.1f} km/s", 0.62, color=C_TENUE,
                    font_size=15)
        t_dop = cifra(f"Doppler: {DOPPLER_GHZ:.1f} GHz", -0.06)
        self.play(FadeIn(t_v), run_time=0.35)
        self.play(FadeIn(t_dop), run_time=0.45)
        self.wait(4.6)

        # --- cierre de la leccion: pantalla limpia --------------------------------
        self.play(FadeOut(det), FadeOut(et_mancha), FadeOut(t_v),
                  FadeOut(t_dop), run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        rot.limpiar("abajo", run_time=0.4)
        linea1 = Text("Adquirir es encontrarse.", font_size=40,
                      color=C_OBJETO)
        linea2 = Text("Seguir es no soltarse.", font_size=40, color=C_OBJETO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.8)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.8)
        self.wait(5.0)
