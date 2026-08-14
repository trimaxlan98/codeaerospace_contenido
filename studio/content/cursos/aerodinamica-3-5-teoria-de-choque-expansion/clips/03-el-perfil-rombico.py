class Clip3(Scene):
    """3.5.3 - Perfil rombico (doble cuna): distribucion de presiones.

    Cuatro caras, cuatro deflexiones, cuatro presiones. Y una consecuencia
    que la placa plana no podia enseñar: el rombo arrastra AUNQUE no
    sustente, porque su propio espesor ya empuja hacia atras. (~42 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El perfil rómbico")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        rombo = perfil_supersonico("rombo", M_PERFIL, ALFA,
                                   semiangulo=SEMIANGULO, cuerda=3.0,
                                   largo_onda=1.5)
        rombo.move_to(LEFT * 1.7 + UP * 0.60)
        self.play(Create(rombo.perfil), run_time=0.9)
        rot.mostrar(pie_curso(f"Ahora un rombo: dos cuñas pegadas por la "
                              f"base, de {SEMIANGULO:g} grados cada una."),
                    zona="abajo", run_time=0.5)
        self.wait(5.0)

        self.play(LaggedStart(*[Create(o) for o in rombo.ondas],
                              lag_ratio=0.22), run_time=2.0)
        rot.mostrar(pie_curso("Seis ondas: choques en el morro y en la cola, "
                              "abanicos en las dos esquinas de en medio."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- momento: las cuatro presiones ---------------------------------
        orden = ("sup_del", "sup_tras", "inf_del", "inf_tras")
        nombres = ("extradós delantero", "extradós trasero",
                   "intradós delantero", "intradós trasero")
        barras = VGroup(*[rombo.barra_presion(c, escala=0.95) for c in orden])
        cifras = VGroup(*[
            Text(f"{n:<20} {rombo.presion(c):.3f}", font=FUENTE_HUD,
                 font_size=16,
                 color=C_SUPER if rombo.presion(c) > 1 else C_CALCULO)
            for c, n in zip(orden, nombres)]).arrange(
                DOWN, aligned_edge=LEFT, buff=0.14)
        cifras.move_to(RIGHT * 3.7 + UP * 0.60)

        self.play(FadeIn(barras), run_time=0.8)
        self.play(FadeIn(cifras, shift=0.10 * UP), run_time=0.8)
        rot.mostrar(pie_curso("Cuatro caras, cuatro presiones. Rojo empuja, "
                              "cian succiona."), zona="abajo", run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("Y las dos traseras están a menos presión que "
                              "las delanteras. Siempre."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- momento: el arrastre de espesor -------------------------------
        rot.mostrar(pie_curso(f"Por eso, incluso a cero grados de ataque, un "
                              f"rombo arrastra: cd = "
                              f"{ROMBO_SIN_ALFA['cd']:.4f}."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Su espesor le empuja hacia atrás aunque no "
                              "esté sustentando nada."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)
