class Clip4(Scene):
    """5.1.4 - Los haces de una constelacion LEO reutilizan frecuencias:
    haces NO vecinos repiten color/banda (asignacion 0,1,2 x3). Cierre de
    leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Los haces del cielo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: muchos haces, no uno solo -----------------------------
        rot.mostrar(pie_curso("Una constelación LEO no manda un solo "
                              "haz: manda muchos, como focos sobre "
                              "franjas de la Tierra."),
                    zona="abajo", run_time=0.5)
        mh = mapa_haces(n=N_HACES)
        mh.move_to(DOWN * 0.6)
        self.play(FadeIn(mh), run_time=1.0)
        self.wait(3.2)

        # --- momento: si cada haz pidiera su banda ---------------------------
        rot.mostrar(pie_curso(f"Si cada uno de los {N_HACES} haces "
                              "pidiera su propia banda, habría que "
                              "cortar el espectro en pedazos diminutos."),
                    zona="abajo", run_time=0.5)
        self.wait(4.0)

        # --- momento: reutilizar en los no vecinos ---------------------------
        rot.mostrar(pie_curso("Pero los haces que NO son vecinos pueden "
                              "REPETIR la misma banda: entre ellos hay "
                              "haces de por medio que los aíslan."),
                    zona="abajo", run_time=0.5)
        mh_asig = mh.con_asignacion(ASIGNACION_HACES)
        self.play(Transform(mh, mh_asig), run_time=1.4)
        self.play(*[Indicate(mh.haz(k), color=C_BIT, scale_factor=1.5)
                    for k in (0, 3, 6)], run_time=1.0)
        self.wait(3.6)

        # --- momento: el espectro se multiplica por geografia -----------------
        rot.mostrar(pie_curso("El espectro se multiplica por "
                              "geografía: pocas bandas alcanzan para "
                              "todos los haces."),
                    zona="abajo", run_time=0.5)
        cuenta = tag_hud(f"{N_BANDAS_HACES} bandas -> {N_HACES} haces",
                         font_size=22)
        cuenta.next_to(mh, UP, buff=0.35)
        self.play(FadeIn(cuenta, shift=0.15 * DOWN), run_time=0.6)
        self.wait(4.4)

        # --- cierre de leccion -------------------------------------------------
        cierre_leccion(
            self, rot,
            "El cielo no se agranda.",
            "Se reparte mejor.",
            "Siguiente: el enlace que se adapta al clima.",
            mh, cuenta)
