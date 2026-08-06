class Clip6(Scene):
    """6 - Muchos agentes, un objetivo. Un orquestador reparte el trabajo
    entre tres especialistas; VERIFICA destapa un error en el informe de
    EJECUTA y lo corrige (tache -> palomita) antes de cerrar el ciclo."""

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ------------------------------------------------
        modulo = hud_modulo("Modulo 06")
        titulo = titulo_curso("Muchos agentes, un objetivo")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(1.6)

        # --- El orquestador arriba-centro ----------------------------------
        orquestador = bloque("ORQUESTADOR", color=C_AGENTE, ancho=2.6)
        orquestador.move_to(UP * 1.5)
        self.play(FadeIn(orquestador, shift=0.2 * DOWN), run_time=0.7)
        self.wait(1.0)

        # --- Los tres especialistas abajo, espaciados ------------------------
        planifica = bloque("PLANIFICA", color=C_AGENTE)
        ejecuta = bloque("EJECUTA", color=C_ACENTO)
        verifica = bloque("VERIFICA", color=C_OK)
        especialistas = VGroup(planifica, ejecuta, verifica).arrange(
            RIGHT, buff=1.6)
        especialistas.move_to(DOWN * 0.8)
        self.play(FadeIn(especialistas, lag_ratio=0.15), run_time=1.0)
        self.wait(1.8)

        # --- Conexiones y flujo del reparto -----------------------------------
        c1 = conectar(orquestador, planifica, color=C_EJE)
        c2 = conectar(orquestador, ejecuta, color=C_EJE)
        c3 = conectar(orquestador, verifica, color=C_EJE)
        self.play(Create(c1), Create(c2), Create(c3), run_time=1.0)
        self.play(flujo([c1, c2, c3], color=C_ACENTO))
        rot.mostrar(pie_curso("Dividir el trabajo: cada agente, una "
                              "especialidad."), zona="abajo", run_time=0.45)
        self.wait(3.0)

        # --- EJECUTA entrega un informe ------------------------------------
        informe = burbuja("informe listo", tipo="observacion", ancho_max=1.9,
                          font_size=16)
        # Debajo de EJECUTA, no entre EJECUTA y VERIFICA: ahi la cruza la
        # conexion diagonal ORQUESTADOR->VERIFICA (la atravesaba de lado
        # a lado). Bajo la fila no pasa ninguna linea.
        informe.next_to(ejecuta, DOWN, buff=0.45)
        self.play(FadeIn(informe, shift=0.15 * UP), run_time=0.6)
        self.wait(1.6)

        # --- VERIFICA lo revisa y marca el error -------------------------------
        c4 = conectar(verifica, informe, color=C_EJE)
        self.play(Create(c4), run_time=0.6)

        def _tache(color=C_PELIGRO, tam=0.11):
            l1 = Line(tam * UL, tam * DR, color=color, stroke_width=3)
            l2 = Line(tam * UR, tam * DL, color=color, stroke_width=3)
            return VGroup(l1, l2)

        tache = _tache()
        tache.move_to(informe.get_top() + UP * 0.05)
        self.play(FadeIn(tache, scale=0.6), run_time=0.5)
        rot.mostrar(pie_curso("Y uno cuyo único trabajo es dudar de los "
                              "demás."), zona="abajo", run_time=0.45)
        self.wait(2.8)

        # --- El informe se corrige: tache -> palomita ---------------------------
        def _palomita(color=C_OK, tam=0.13):
            l1 = Line(LEFT * tam * 0.55 + UP * tam * 0.05,
                      DOWN * tam * 0.45, color=color, stroke_width=3)
            l2 = Line(DOWN * tam * 0.45, RIGHT * tam + UP * tam * 0.85,
                      color=color, stroke_width=3)
            return VGroup(l1, l2)

        palomita = _palomita()
        palomita.move_to(tache.get_center())
        self.play(ReplacementTransform(tache, palomita), run_time=0.7)
        rot.mostrar(pie_curso("La verificación adversarial atrapa errores "
                              "antes de que salgan."), zona="abajo",
                   run_time=0.45)
        self.wait(3.0)

        # --- Cierre: el flujo completo otra vez ---------------------------------
        self.play(flujo([c1, c2, c3], color=C_ACENTO))
        rot.mostrar(pie_curso("Así se construye confianza: en equipo."),
                   zona="abajo", run_time=0.45)
        self.wait(3.4)
