class Clip5(Scene):
    """5 - El reloj que vuela. La orbita GPS a escala: v = sqrt(GM/r) da
    3.874 km/s y una vuelta cada 11.97 h. La relatividad especial cobra su
    parte: el reloj del satelite atrasa 7.21 us cada dia. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El reloj que vuela")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        orb = orbita_gps().scale(0.88)
        orb.shift(LEFT * 2.6 + UP * 0.2)
        tag_escala = tag_junto(orb.tierra, "a escala", DOWN, buff=0.18,
                               font_size=15)
        radio_km = f"{RADIO_GPS / 1000:,.0f}".replace(",", " ")

        # --- momento: la orbita, a escala ----------------------------------
        rot.mostrar(pie_curso(
            f"Cada satélite del GPS gira a {radio_km} km del centro de la "
            "Tierra."), zona="abajo", run_time=0.5)
        self.play(FadeIn(orb.tierra, scale=0.7), FadeIn(tag_escala),
                  run_time=0.9)
        self.play(Create(orb.orbita), run_time=1.7)
        self.play(FadeIn(orb.satelite, scale=0.5), run_time=0.7)
        self.wait(1.9)
        # El grupo entero pasa a la escena para animarlo con .en(alpha)
        # sin que sus piezas se dibujen dos veces.
        self.remove(orb.tierra, orb.orbita, orb.satelite)
        self.add(orb)

        # --- momento: la velocidad sale de la gravedad ---------------------
        rot.mostrar(formula_pie(r"v = \sqrt{GM/r}"), zona="abajo",
                    run_time=0.5)
        v_tag = tag_hud(f"v = {V_GPS / 1000:.3f} km/s", font_size=20)
        t_tag = tag_hud(f"T = {PERIODO_GPS_H:.2f} h", font_size=20)
        panel = VGroup(v_tag, t_tag)
        panel.arrange(DOWN, aligned_edge=LEFT, buff=0.30)
        panel.move_to(RIGHT * 3.6 + UP * 1.75)
        self.play(FadeIn(v_tag, shift=0.12 * RIGHT), run_time=0.6)
        self.wait(0.6)
        self.play(FadeIn(t_tag, shift=0.12 * RIGHT), run_time=0.6)
        self.wait(3.3)

        # --- momento: media vuelta, sin motor ------------------------------
        rot.mostrar(pie_curso(
            "Nadie lo empuja: cae alrededor de la Tierra, y no para."),
            zona="abajo", run_time=0.5)
        self.play(UpdateFromAlphaFunc(orb, lambda m, a: m.en(0.125 + 0.5 * a)),
                  run_time=5.5, rate_func=linear)
        self.wait(0.6)

        # --- momento: la relatividad especial cobra ------------------------
        rot.mostrar(pie_curso(
            "A esa velocidad la relatividad especial cobra su parte."),
            zona="abajo", run_time=0.5)
        reloj = carita_reloj()
        reloj.move_to(RIGHT * 2.9 + DOWN * 0.55)
        sr_tag = tag_hud(f"{DERIVA_SR:+.2f} µs/día", font_size=20,
                         color=C_ERROR)
        sr_tag.next_to(reloj, RIGHT, buff=0.35)
        self.play(FadeIn(reloj, scale=0.6), run_time=0.7)
        self.play(UpdateFromAlphaFunc(reloj, lambda m, a: m.en(2 * a)),
                  run_time=3.4, rate_func=linear)
        self.play(FadeIn(sr_tag, shift=0.15 * RIGHT), run_time=0.6)
        self.wait(1.3)

        # --- momento: el precio en metros ----------------------------------
        rot.mostrar(pie_curso(
            f"Atrasa {abs(DERIVA_SR):.2f} µs cada día: "
            f"{abs(DERIVA_SR) * M_POR_US / 1000:.1f} km de posición."),
            zona="abajo", run_time=0.5)
        self.wait(5.2)
