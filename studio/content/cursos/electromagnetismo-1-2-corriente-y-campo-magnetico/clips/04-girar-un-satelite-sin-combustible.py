class Clip4(Scene):
    """1.2.4 - El magnetorquer: una bobina que se apoya en el campo de la
    Tierra para girar el satelite. Par de 6e-6 N m, 90 grados en ~32 s:
    lento, gratis e inagotable. Cierra la leccion. (~39 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Girar un satélite sin combustible")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: el cubesat y su bobina -------------------------------
        cs = cubesat_torquer()
        cs.move_to(DOWN * 0.1)
        rot.mostrar(pie_curso("Un satélite pequeño no lleva tanque para "
                              "girarse. Lleva una bobina a bordo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cs.cuerpo, scale=1.1), Create(cs.bobina),
                  run_time=1.1)
        self.wait(4.4)

        # --- momento: el satelite-iman -------------------------------------
        rot.mostrar(pie_curso("Corriente en la bobina: el satélite entero "
                              "se vuelve un imán, con su flecha."),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(cs.flecha_m), run_time=0.7)
        self.wait(4.4)

        # --- momento: el campo de fondo ------------------------------------
        rot.mostrar(pie_curso("Y alrededor, en verde, el campo de la "
                              "Tierra: siempre presente, gratis."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(cs.flecha_b, lag_ratio=0.1), run_time=0.8)
        self.wait(4.4)

        # --- momento: el par -----------------------------------------------
        rot.mostrar(formula_pie(r"\vec{\tau} = \vec{m}\times\vec{B}"),
                    zona="abajo", run_time=0.5)
        par_tag = tag_hud(f"par: {cs.par() * 1e6:.0f}e-6 N m",
                          font_size=16)
        par_tag.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(Create(cs.arco_par), FadeIn(par_tag, shift=0.1 * DOWN),
                  run_time=0.9)
        self.wait(4.4)

        # --- momento: el giro ----------------------------------------------
        rot.mostrar(pie_curso("El par es minúsculo... pero un cuarto de "
                              "vuelta solo tarda medio minuto."),
                    zona="abajo", run_time=0.5)
        giro_tag = tag_hud(f"90 grados en {cs.segundos_para(90):.0f} s",
                           font_size=16)
        giro_tag.next_to(par_tag, DOWN, buff=0.18).align_to(par_tag, RIGHT)
        self.play(Rotate(cs.girable(), angle=-PI / 2,
                         about_point=cs.cuerpo.get_center()), run_time=3.0)
        self.play(FadeIn(giro_tag, shift=0.1 * DOWN), run_time=0.5)
        self.wait(1.5)

        rot.mostrar(pie_curso("Lento, gratis e inagotable: así se "
                              "orientan los CubeSats de verdad."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(cs), FadeOut(par_tag), FadeOut(giro_tag),
                  run_time=0.8)
        rot.limpiar("arriba", run_time=0.4)
        linea1 = Text("La Tierra empuja gratis.", font_size=40,
                      color=C_TITULO)
        linea2 = Text("Solo hay que saber pedirle.", font_size=40,
                      color=C_CALCULO)
        linea1.move_to(UP * 0.42)
        linea2.move_to(DOWN * 0.42)
        rot.mostrar(pie_curso("Campos quietos, dominados. Ahora toca "
                              "soltar una carga a correr entre ellos."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(linea1, shift=0.2 * UP), run_time=0.7)
        self.play(FadeIn(linea2, shift=0.2 * UP), run_time=0.7)
        self.wait(4.6)
