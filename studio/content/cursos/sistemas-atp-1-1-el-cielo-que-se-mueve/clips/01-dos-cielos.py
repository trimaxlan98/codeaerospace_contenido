class Clip1(Scene):
    """1.1.1 - Dos cielos: el GEO clavado y el LEO que cruza. La
    diferencia es puramente cinematica. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Dos cielos, dos antenas"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        vista = vista_polar(radio=2.35, font_size=16)
        vista.move_to(LEFT * 3.05 + UP * 0.32)
        self.play(Create(vista), run_time=1.6)
        self.wait(0.5)

        # --- el GEO: un punto que no se mueve ----------------------------
        p_geo = vista.punto(118.0, 42.0)
        geo = Dot(p_geo, radius=0.085, color=C_SAT)
        t_geo = tag_junto(geo, "GEO", direccion=UR, buff=0.10,
                          color=C_SAT)
        self.play(FadeIn(geo, scale=1.6), FadeIn(t_geo), run_time=0.7)

        # El reloj va en SU carril (a la derecha), no debajo de la carta:
        # ahi caia sobre el rotulo "S" y sobre el carril de la cifra, y el
        # fondo del pie se lo comia a medias.
        reloj = tag_hud("t = 00 s", font_size=24, color=C_TENUE)
        reloj.move_to(RIGHT * 3.30 + UP * 1.05)
        self.add(reloj)
        # el reloj corre y el punto sigue exactamente donde estaba
        for k in (4, 8, 12):
            self.play(Transform(reloj,
                                tag_hud(f"t = {k:02d} s", font_size=22,
                                        color=C_TENUE).move_to(reloj),
                                run_time=0.02),
                      run_time=0.90)
        estela = Circle(radius=0.30, color=C_SAT, stroke_width=2.0)
        estela.move_to(p_geo)
        self.play(Create(estela), run_time=0.5)
        self.play(FadeOut(estela), run_time=0.4)
        self.wait(0.6)
        self.play(FadeOut(reloj), run_time=0.4)

        rot.mostrar(cifra_pie(f"periodo GEO {fmt(T_GEO_H, 2)} h"),
                    zona="abajo")
        self.wait(2.0)
        rot.mostrar(dato_pie("caja de control 0.05 deg"), zona="abajo")
        self.wait(2.2)

        # --- el LEO: cruza el cielo entero -------------------------------
        traza = traza_pase(vista, el_max=72.0, az_culminacion=140.0,
                           muestras=140, color=C_CIELO)
        # el GEO se atenua: deja de ser el sujeto y no compite con el LEO
        self.play(geo.animate.set_opacity(0.35),
                  t_geo.animate.set_opacity(0.35), run_time=0.6)
        self.play(Create(traza), run_time=2.0)

        leo = Dot(traza.punto_en(0.0), radius=0.085, color=C_SAT)
        t_leo = tag_junto(leo, "LEO", direccion=DL, buff=0.10, color=C_SAT)
        t_leo.add_updater(lambda m: m.next_to(leo, DL, buff=0.10))
        self.play(FadeIn(leo, scale=1.6), FadeIn(t_leo), run_time=0.6)
        self.play(MoveAlongPath(leo, traza), run_time=4.2,
                  rate_func=linear)
        t_leo.clear_updaters()
        self.wait(0.8)

        rot.mostrar(cifra_pie(f"LEO {fmt(H_LEO, 0)} km"), zona="abajo")
        self.wait(1.8)

        panel = panel_cifras((f"GEO {fmt(H_GEO, 0)} km", C_DATO),
                             f"LEO {fmt(H_LEO, 0)} km",
                             f"v = {fmt(V_LEO, 2)} km/s")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.4)
