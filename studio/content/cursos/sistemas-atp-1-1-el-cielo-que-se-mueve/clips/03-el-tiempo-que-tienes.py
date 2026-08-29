class Clip3(Scene):
    """1.1.3 - El pase entero dura menos de diez minutos, y eso es todo
    el tiempo que hay. AOS, culminacion, LOS. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Todo el tiempo que tienes"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        vista = vista_polar(radio=2.45, font_size=16)
        vista.move_to(LEFT * 2.85 + DOWN * 0.28)
        self.play(Create(vista), run_time=1.5)

        # --- la mascara: por debajo no hay pase util ---------------------
        mask = mascara_elevacion(vista, el_min=MASCARA, color=C_EJE)
        self.play(FadeIn(mask), run_time=0.9)
        t_mask = tag_hud(f"mascara {fmt(MASCARA, 0)} deg", font_size=19,
                         color=C_TENUE)
        t_mask.next_to(vista, DOWN, buff=0.28)
        self.play(FadeIn(t_mask), run_time=0.5)
        self.wait(1.4)

        # --- la traza del pase -------------------------------------------
        traza = traza_pase(vista, el_max=72.0, az_culminacion=140.0,
                           muestras=140, color=C_CIELO)
        self.play(Create(traza), run_time=1.8)
        self.wait(0.5)

        p_aos, p_los = traza.punto_en(0.0), traza.punto_en(1.0)
        d_aos = Dot(p_aos, radius=0.07, color=C_OK)
        d_los = Dot(p_los, radius=0.07, color=C_PELIGRO)
        t_aos = tag_junto(d_aos, "AOS", direccion=LEFT, buff=0.12,
                          color=C_OK)
        t_los = tag_junto(d_los, "LOS", direccion=RIGHT, buff=0.12,
                          color=C_PELIGRO)
        self.play(FadeIn(d_aos), FadeIn(t_aos), FadeIn(d_los),
                  FadeIn(t_los), run_time=0.8)
        self.wait(1.0)

        # --- el pase corre y el reloj cuenta -----------------------------
        sat = Dot(p_aos, radius=0.085, color=C_SAT)
        reloj = tag_hud("00:00", font_size=30)
        reloj.move_to(RIGHT * 3.35 + UP * 0.85)
        t_reloj = tag_junto(reloj, "en el aire", direccion=DOWN, buff=0.20)
        self.play(FadeIn(sat, scale=1.5), FadeIn(reloj), FadeIn(t_reloj),
                  run_time=0.7)

        # MoveAlongPath reparametriza el recorrido ENTERO en cada
        # llamada, asi que no sirve para avanzar por tramos: el satelite
        # se coloca con `punto_en`. Y el reloj se releva con `become`
        # FUERA del play: los kwargs de play() pisan los de cada
        # animacion (manim 0.20.1), asi que un Transform con
        # run_time=0.02 dentro de un play de 0.46 dura 0.46 y ensena los
        # digitos a medio morfar.
        pasos = 10
        total_s = DUR_PASE_MIN * 60.0
        for k in range(1, pasos + 1):
            seg = total_s * k / pasos
            sat.move_to(traza.punto_en(k / pasos))
            reloj.become(tag_hud(f"{int(seg // 60):02d}:"
                                 f"{int(seg % 60):02d}",
                                 font_size=30).move_to(reloj))
            self.wait(0.46)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"pase {fmt(DUR_PASE_MIN, 1)} min"),
                    zona="abajo")
        self.wait(2.2)

        panel = panel_cifras(f"arco {fmt(ARCO_PASE, 1)} deg",
                             f"T = {fmt(T_LEO_MIN, 1)} min",
                             f"pase {fmt(DUR_PASE_MIN, 1)} min")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.9)

        # --- tres oportunidades al dia, y se acabo -----------------------
        otras = VGroup(
            traza_pase(vista, el_max=24.0, az_culminacion=52.0,
                       muestras=120, color=C_CIELO),
            traza_pase(vista, el_max=11.0, az_culminacion=232.0,
                       muestras=120, color=C_CIELO),
        )
        for t in otras:
            t.set_stroke(opacity=0.45)
        self.play(LaggedStart(*[Create(t) for t in otras], lag_ratio=0.35),
                  run_time=1.8)
        rot.mostrar(cifra_pie("tres pases al dia"), zona="abajo")
        self.wait(4.6)
