class Clip5(Scene):
    """5 - Orbitar es caer de lado. El canon de Newton con balistica
    real: cada disparo mas rapido cae mas lejos, hasta que la caida ya
    no alcanza el suelo. Lo caro no es subir: es correr de lado. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 05")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("Orbitar es caer de lado")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: el experimento mental --------------------------------
        rot.mostrar(pie_curso("Newton, 1687: sube un cañón a la montaña "
                              "más alta y dispara."), zona="abajo",
                    run_time=0.5)
        canon = canon_newton()
        canon.shift(np.array([-1.7, 0.05, 0.0]) - canon._ancla.get_center())
        self.play(Create(canon.tierra), run_time=1.0)
        self.play(Create(canon.monte), run_time=0.5)
        honesto = tag_junto(canon.tierra, "montaña exagerada para verse",
                            DOWN, buff=0.16, font_size=14)
        honesto.move_to(np.array([-4.9, -2.05, 0.0]))  # fuera de la orbita
        self.play(FadeIn(honesto), run_time=0.4)
        self.wait(1.5)

        # --- momento: el abanico de caidas ---------------------------------
        rot.mostrar(pie_curso("Más rápido cae más lejos… pero sigue "
                              "cayendo."), zona="abajo", run_time=0.5)
        abanico = VGroup()
        for v_frac in (0.4, 0.6, 0.8, 0.92):
            tr = canon.trayectoria(v_frac)
            abanico.add(tr)
            self.play(Create(tr), run_time=0.85)
            self.wait(0.3)
        self.wait(1.5)

        # --- momento: la caida que no toca el suelo ------------------------
        rot.mostrar(pie_curso("Hasta que caes tan de lado que el suelo "
                              "se curva contigo: órbita."), zona="abajo",
                    run_time=0.5)
        orbita = canon.trayectoria(1.0, color=C_CARGA, grosor=3.2)
        self.play(Create(orbita), run_time=2.0)
        cifra_orb = tag_hud(f"v = {canon.v_orbital_kms():.2f} km/s",
                            font_size=17)
        cifra_orb.next_to(canon.tierra, RIGHT, buff=0.85)
        cifra_orb.shift(UP * 1.15)
        nota_orb = tag_junto(cifra_orb, "a 200 km, calculada", DOWN,
                             buff=0.10, font_size=14)
        self.play(FadeIn(cifra_orb, shift=0.15 * RIGHT), FadeIn(nota_orb),
                  run_time=0.7)
        self.wait(2.4)

        # --- momento: el presupuesto ---------------------------------------
        rot.mostrar(pie_curso("Subir es lo de menos: lo caro es correr "
                              "de lado, y las pérdidas también cobran."),
                    zona="abajo", run_time=0.5)
        linea = Line(LEFT * 1.1, RIGHT * 1.1, stroke_width=1.8,
                     color=C_EJE)
        presupuesto = VGroup(
            tag_hud(f"órbita   {V_ORB_KMS:.2f} km/s", font_size=15,
                    color=C_TIERRA),
            tag_hud(f"pérdidas +{PERDIDAS_KMS:.1f} km/s (cita)",
                    font_size=15, color=C_MUERTO),
            linea,
            tag_hud(f"LEO      {DV_LEO_KMS:.2f} km/s", font_size=18),
        ).arrange(DOWN, aligned_edge=RIGHT, buff=0.22)
        presupuesto.move_to(np.array([4.35, -0.75, 0.0]))
        for parte in presupuesto:
            self.play(FadeIn(parte, shift=0.15 * DOWN), run_time=0.55)
        self.wait(2.8)

        # --- momento: el cierre --------------------------------------------
        rot.mostrar(pie_curso("Ese número, 9.4 km/s, es la deuda que "
                              "todo cohete le debe al planeta."),
                    zona="abajo", run_time=0.5)
        self.wait(5.8)
