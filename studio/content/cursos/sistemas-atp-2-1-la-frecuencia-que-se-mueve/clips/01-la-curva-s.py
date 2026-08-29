class Clip1(Scene):
    """2.1.1 - La curva S del Doppler se construye mientras el satelite
    cruza la carta polar: los dos graficos comparten el mismo tiempo.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("La curva S del Doppler"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- izquierda: la carta polar y la traza del pase ----------------
        vista = vista_polar(radio=2.15, font_size=15)
        vista.move_to(LEFT * 3.35 + DOWN * 0.15)
        self.play(Create(vista), run_time=1.6)
        self.wait(0.4)

        traza = traza_pase(vista, el_max=72.0, az_culminacion=140.0,
                           muestras=140, color=C_CIELO)
        self.play(Create(traza), run_time=2.0)
        self.wait(0.5)

        p_aos = traza.punto_en(0.0)
        p_cul = traza.punto_en(0.5)
        p_los = traza.punto_en(1.0)
        t_aos = tag_hud("AOS", font_size=16, color=C_TENUE)
        t_aos.next_to(p_aos, LEFT, buff=0.10)
        t_los = tag_hud("LOS", font_size=16, color=C_TENUE)
        t_los.next_to(p_los, RIGHT, buff=0.10)
        self.play(FadeIn(t_aos), FadeIn(t_los), run_time=0.7)
        self.wait(0.8)

        # --- derecha: los ejes de la curva S, sin la curva todavia ---------
        s = curva_s_doppler(ancho=4.9, alto=2.55, color=C_SAT)
        s.move_to(RIGHT * 3.1 + DOWN * 0.15)
        self.play(Create(s.ejes), FadeIn(s.linea_f0), FadeIn(s.etiquetas),
                  run_time=1.3)
        self.wait(0.6)

        # --- el satelite entra en AOS: se acerca, la frecuencia sube -------
        leo = Dot(p_aos, radius=0.08, color=C_SAT)
        t_leo = tag_junto(leo, "LEO", direccion=DOWN, buff=0.10,
                          color=C_SAT)
        t_leo.add_updater(lambda m: m.next_to(leo, DOWN, buff=0.10))
        self.play(FadeIn(leo, scale=1.6), FadeIn(t_leo), run_time=0.7)
        t_acerca = tag_hud("se acerca", font_size=17, color=C_SAT)
        t_acerca.next_to(s.eje_f, LEFT, buff=0.20).align_to(s.eje_f, UP)
        self.play(FadeIn(t_acerca), run_time=0.6)
        self.wait(1.0)

        # --- la curva REAL medida, sobre CURVA_D/PERFIL_D ------------------
        # Los dos graficos comparten el MISMO parametro de tiempo: el
        # satelite recorre la traza mientras la curva se dibuja, con el
        # mismo run_time y el mismo rate_func lineal.
        origen = np.asarray(s.eje_t.get_start(), dtype=np.float64)
        ancho_s = float(s.eje_t.width)
        alto_s = float(s.eje_f.height)
        xs = PERFIL_D["t"] / PERFIL_D["duracion"]
        ymax = float(np.max(np.abs(CURVA_D)))
        puntos = [
            origen + np.array([x_rel * ancho_s,
                               (0.5 + 0.42 * (y / ymax)) * alto_s, 0.0])
            for x_rel, y in zip(xs, CURVA_D)
        ]
        curva_real = VMobject(stroke_color=C_SAT, stroke_width=3.4)
        curva_real.set_points_as_corners(puntos)

        self.play(FadeOut(t_acerca), run_time=0.4)
        self.play(Create(curva_real, rate_func=linear),
                  MoveAlongPath(leo, traza, rate_func=linear), run_time=5.6)
        t_leo.clear_updaters()
        self.wait(0.4)
        # el satelite llega a LOS: su etiqueta ya no hace falta, el punto
        # queda marcado por "LOS"
        self.play(FadeOut(t_leo), FadeOut(leo), run_time=0.5)

        t_aleja = tag_hud("se aleja", font_size=17, color=C_SAT)
        t_aleja.next_to(t_los, DOWN, buff=0.16)
        self.play(FadeIn(t_aleja), run_time=0.6)
        self.wait(1.0)

        # --- las dos vistas marcan el MISMO instante: la culminacion -------
        p_cruce = curva_real.point_from_proportion(0.5)
        cruce = Dot(p_cruce, radius=0.07, color=C_CALCULO)
        guia = DashedLine(p_cul, p_cruce, stroke_width=1.6, color=C_TENUE)
        self.play(Create(guia), FadeIn(cruce, scale=1.4), run_time=1.0)
        t_cul = tag_hud("culminacion", font_size=16, color=C_CALCULO)
        t_cul.next_to(cruce, UP, buff=0.12)
        self.play(FadeIn(t_cul), run_time=0.6)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"excursion UHF {fmt(EXC_UHF / 1000.0, 1)} "
                              f"kHz"), zona="abajo")
        self.wait(3.0)

        panel = panel_cifras((f"f0 = {fmt(F_UHF / 1.0e6, 0)} MHz", C_DATO),
                             f"excursion = {fmt(EXC_UHF / 1000.0, 1)} kHz",
                             "AOS a LOS")
        self.play(FadeIn(panel), run_time=0.8)
        self.wait(3.6)
