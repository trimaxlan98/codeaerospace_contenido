class Clip5(Scene):
    """5 - La UIT, arbitro del cielo: la cadena de tramites API-COORDINACION-
    NOTIFICACION, el plazo de 7 anos para materializar el registro y el
    orden de llegada como moneda de proteccion."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo --------------------------------------------------
        modulo = hud_modulo("Modulo 05")
        titulo = titulo_curso("La UIT: el árbitro del cielo")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.8)

        # --- momento: la cadena de tramites ----------------------------------
        api = bloque("API", color=C_NGSO, ancho=2.1)
        coordinacion = bloque("COORDINACIÓN", color=C_ONDA, ancho=2.7)
        notificacion = bloque("NOTIFICACIÓN", color=C_OK, ancho=2.5)
        cadena = VGroup(api, coordinacion, notificacion).arrange(RIGHT,
                                                                   buff=0.85)
        cadena.move_to(UP * 0.8)
        self.play(FadeIn(cadena, lag_ratio=0.15), run_time=0.9)
        self.wait(0.8)

        c1 = conectar(api, coordinacion, color=C_EJE)
        c2 = conectar(coordinacion, notificacion, color=C_EJE)
        self.play(Create(c1), Create(c2), run_time=0.7)
        self.play(flujo([c1, c2], color=C_ACENTO))
        rot.mostrar(pie_curso("Nadie enciende un satélite sin pasar por la "
                              "ventanilla: tres trámites ante la UIT."),
                   zona="abajo", run_time=0.45)
        self.wait(5.4)

        # --- momento: el plazo de 7 anos --------------------------------------
        plazo = llave(cadena, "7 años máximo", direccion=DOWN)
        self.play(FadeIn(plazo, shift=0.15 * UP), run_time=0.6)
        rot.mostrar(pie_curso("Siete años para pasar del papel al satélite "
                              "en órbita, o la prioridad se pierde."),
                   zona="abajo", run_time=0.45)
        self.wait(5.3)

        # --- momento: el orden de llegada -------------------------------------
        self.play(FadeOut(plazo), run_time=0.35)

        tiempo = linea_tiempo([("API", "AÑO 0"), ("SERVICIO", "AÑO 7"),
                               ("CADUCIDAD", "")], ancho=6.0)
        tiempo.move_to(DOWN * 1.4)
        self.play(FadeIn(tiempo.linea), FadeIn(tiempo.muescas),
                  LaggedStart(*[FadeIn(r) for r in tiempo.rotulos],
                              lag_ratio=0.2), run_time=0.8)

        recorre = punto_brillante(tiempo.muesca(0), color=C_ONDA)
        self.play(FadeIn(recorre), run_time=0.3)
        self.play(recorre.animate.move_to(tiempo.muesca(1)), run_time=0.9)
        rot.mostrar(pie_curso("El orden de llegada es la moneda: quien "
                              "registra primero, cobra protección "
                              "primero."), zona="abajo", run_time=0.45)
        self.wait(5.4)

        # --- cierre -----------------------------------------------------------
        rot.mostrar(pie_curso("El espectro no se compra: se tramita, se "
                              "usa... o se pierde."), zona="abajo",
                   run_time=0.45)
        self.wait(7.0)
