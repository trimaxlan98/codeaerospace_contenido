class Clip2(Scene):
    """2 - Un cono de microradianes. Dos satelites a 5000 km: el precio de
    la ganancia de apertura es que el haz sale como un cono finisimo, de
    9.87 microrradianes, que a esa distancia deja una mancha (huella) de
    98.7 m. El receptor mide unos metros: hay que acertar dentro de la
    mancha. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo_curso("Un cono de microrradianes"), zona="arriba",
                    run_time=0.6)

        # --- momento 1: los dos satelites y el cono -----------------------
        rot.mostrar(pie_curso("El precio de esa ganancia: el haz es un "
                              "cono de microrradianes."), zona="abajo")
        sats = dos_satelites(sep_km=5000.0)
        sats.move_to(UP * 1.95)
        self.play(FadeIn(sats.arco), run_time=0.5)
        self.play(FadeIn(sats.a, shift=0.12 * DOWN),
                  FadeIn(sats.b, shift=0.12 * DOWN), run_time=0.6)
        self.play(FadeIn(sats.rotulo), run_time=0.4)

        cono = cono_haz(theta_urad=DIV_ISL_URAD, R_km=R_ISL_KM)
        cono.move_to(DOWN * 0.85)
        self.play(FadeIn(cono.emisor), run_time=0.4)
        self.play(Create(cono.cono), Create(cono.eje), run_time=1.0)
        self.play(FadeIn(cono.huella_elipse), FadeIn(cono.receptor),
                  run_time=0.6)
        self.wait(4.5)

        # --- momento 2: las cifras ------------------------------------------
        rot.mostrar(pie_curso("Nueve coma nueve microrradianes: a cinco "
                              "mil kilómetros, una mancha de cien "
                              "metros."), zona="abajo")
        self.play(FadeIn(cono.rotulo, shift=0.10 * UP), run_time=0.6)
        self.wait(5.5)

        # --- momento 3: acertar en la mancha ---------------------------------
        rot.mostrar(pie_curso("El satélite receptor mide unos metros: hay "
                              "que acertar en la mancha."), zona="abajo")
        zoom = VGroup(cono.huella_elipse, cono.receptor)
        etq = tag_junto(cono.receptor, "unos metros", RIGHT, buff=0.20,
                        font_size=15, color=C_OBJETO)
        self.play(FadeIn(etq), run_time=0.4)
        self.play(Circumscribe(zoom, color=C_FRANJA, buff=0.18,
                               time_width=0.55), run_time=1.3)
        self.wait(4.5)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("Un cono finísimo, y al final del cono, "
                              "otro satélite."), zona="abajo")
        self.wait(6.5)
