class Clip1(Scene):
    """3.2.1 - El pase LEO real (h=550 km, elev. max. 60 grados, Tierra
    sin rotar): doce minutos de horizonte a horizonte y la distancia que
    baja hasta el cenit y vuelve a subir. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El pase")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.5)

        # --- momento: la boveda y el trayecto -------------------------
        rot.mostrar(pie_curso("Un satelite LEO no espera quieto en el "
                              "cielo: asoma por un borde y cruza la "
                              "boveda entera."),
                    zona="abajo", run_time=0.5)
        cielo = pase_cielo(PASE, radio=2.35, theta_max=68.0)
        cielo.move_to(DOWN * 0.55)
        # submobjects (tras el ancla, indice 0): horizonte, cupula, arcos,
        # trayecto -- se revela primero la boveda y luego el trayecto.
        boveda = VGroup(*cielo.submobjects[1:4])
        self.play(FadeIn(boveda), run_time=0.8)
        self.play(Create(cielo.trayecto), run_time=2.2)
        self.wait(2.2)

        # --- momento: el satelite recorre el trayecto -------------------
        rot.mostrar(pie_curso("Sigue su marcha: la elevacion sube hasta "
                              "el cenit y vuelve a bajar."),
                    zona="abajo", run_time=0.5)
        tv = ValueTracker(0.0)
        sat = always_redraw(lambda: Dot(cielo.sat_en(tv.get_value()),
                                        radius=0.09, color=C_CIFRA))
        cifra = always_redraw(
            lambda: tag_hud(
                f"elev {fmt(ELEV_DEG[idx_de_frac(tv.get_value())], 0)} deg"
                f"   d {fmt(D_KM[idx_de_frac(tv.get_value())], 0)} km",
                font_size=18).next_to(cielo.sat_en(tv.get_value()), UP,
                                      buff=0.16))
        self.play(FadeIn(sat, scale=1.5), FadeIn(cifra), run_time=0.4)
        self.play(tv.animate.set_value(1.0), run_time=5.6, rate_func=linear)
        self.wait(1.4)

        # --- momento: la distancia baja y sube (curva medida) -----------
        rot.mostrar(pie_curso("Y mientras cruza, la distancia a la "
                              "estacion baja... y vuelve a subir."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(sat), FadeOut(cifra), FadeOut(cielo),
                  run_time=0.6)
        on = onda(T_MIN, D_KM, rango_y=(550.0, 2820.0), ancho=8.4,
                  alto=3.0, color=C_SENAL)
        on.move_to(DOWN * 0.35)
        self.play(FadeIn(on.ejes), run_time=0.4)
        self.play(Create(on.curva), run_time=2.2)
        i_cenit = idx_de_frac(0.5)
        p_min = Dot(on.en(T_MIN[i_cenit], D_KM[i_cenit]), radius=0.08,
                   color=C_CIFRA)
        et_min = tag_hud(f"minimo: {fmt(D_MIN_KM, 0)} km", font_size=19)
        et_min.next_to(p_min, DOWN, buff=0.2)
        self.play(FadeIn(p_min, scale=1.6), FadeIn(et_min), run_time=0.6)
        self.wait(3.4)

        # --- momento: los numeros del pase, y la simplificacion ----------
        panel = panel_derecha(
            tag_hud(f"pase: {fmt(T_TOTAL_MIN, 1)} min"),
            tag_hud(f"elev max: {fmt(ELEV_MAX_DEG, 0)} deg"),
            tag_hud(f"d min: {fmt(D_MIN_KM, 0)} km"))
        rot.mostrar(pie_curso("Tierra sin rotar y pase de maxima "
                              "elevacion 60 grados: geometria "
                              "simplificada."), zona="abajo", run_time=0.5)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(5.6)
