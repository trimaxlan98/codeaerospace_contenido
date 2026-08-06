class Clip5(Scene):
    """5 - Pensar en voz alta: ReAct. La traza de seis pasos (pensar,
    actuar, observar, dos veces) se construye burbuja a burbuja a la
    izquierda mientras el lazo percibir-razonar-actuar, pequeno a la
    derecha, gira un tramo con cada par accion/observacion."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 05")
        titulo = titulo_curso("Pensar en voz alta: ReAct")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.8)

        # --- El lazo pequeno a la derecha ---------------------------------
        lazo = lazo_agente(radio=1.15)
        lazo.move_to(RIGHT * 3.3)
        self.play(Create(lazo), run_time=1.2)
        self.wait(1.7)

        # --- La traza completa, lista para revelarse paso a paso ------------
        pasos = [
            ("pensamiento", "¿Cuándo pasa NOAA-19 sobre la estación?"),
            ("accion", "consultar_tle(NOAA-19)"),
            ("observacion", "TLE fresco, época de hoy"),
            ("pensamiento", "Ahora puedo propagar el pase"),
            ("accion", "buscar_pase(hoy, elev>10°)"),
            ("observacion", "Pase a las 14:32, elev 44°"),
        ]
        traza = traza_react(pasos)
        traza.move_to(LEFT * 3.2)
        alto_disponible = config.frame_height - 2.9
        if traza.height > alto_disponible:
            traza.scale_to_fit_height(alto_disponible)
            traza.move_to(LEFT * 3.2)

        # --- Paso 1: piensa -----------------------------------------------
        rot.mostrar(pie_curso("Piensa..."), zona="abajo", run_time=0.45)
        self.play(FadeIn(traza.burbujas[0], shift=0.15 * UP), run_time=0.55)
        self.wait(2.7)

        # --- Paso 2: actua con una herramienta -------------------------------
        rot.mostrar(pie_curso("...actúa con una herramienta..."),
                   zona="abajo", run_time=0.45)
        self.play(FadeIn(traza.burbujas[1], shift=0.15 * UP), run_time=0.55)
        self.wait(2.5)

        # --- Paso 3: observa el resultado, primer tramo del lazo -------------
        rot.mostrar(pie_curso("...observa el resultado. Y repite."),
                   zona="abajo", run_time=0.45)
        self.play(FadeIn(traza.burbujas[2], shift=0.15 * UP), run_time=0.55)
        self.play(girar_lazo(lazo, vueltas=0.34))
        self.wait(2.9)

        # --- Segundo ciclo: piensa, actua, observa ---------------------------
        self.play(FadeIn(traza.burbujas[3], shift=0.15 * UP), run_time=0.55)
        self.wait(2.0)
        self.play(FadeIn(traza.burbujas[4], shift=0.15 * UP), run_time=0.55)
        self.wait(1.9)
        self.play(FadeIn(traza.burbujas[5], shift=0.15 * UP), run_time=0.55)
        self.play(girar_lazo(lazo, vueltas=0.34))
        self.wait(2.7)

        # --- Cierre: la meta alcanzada ---------------------------------------
        self.play(Indicate(traza.burbujas[5], color=C_OK, scale_factor=1.06),
                  run_time=1.2)
        rot.mostrar(pie_curso("Meta alcanzada en tres vueltas del lazo."),
                   zona="abajo", run_time=0.45)
        self.wait(3.8)
