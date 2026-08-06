class Clip3(Scene):
    """3 - Herramientas: las manos del agente. Un AGENTE cian frente a un
    catalogo cerrado de herramientas violeta; elige una, la llama con
    argumentos concretos (tarjeta JSON) y recibe una observacion de
    vuelta que reemplaza a la llamada."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("Herramientas: las manos del agente")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 03")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(2.2)

        # --- momento: el agente frente a un catalogo cerrado -----------------
        agente = bloque("AGENTE", color=C_AGENTE)
        agente.move_to(np.array([-3.9, 1.2, 0.0]))
        nombres = ["buscar_pase", "mover_antena", "leer_correo",
                   "consultar_tle", "enviar_alerta", "grabar_iq"]
        catalogo = catalogo_herramientas(nombres, columnas=3, color=C_MUNDO)
        catalogo.move_to(np.array([2.4, 1.2, 0.0]))
        self.play(FadeIn(agente, shift=0.18 * LEFT), run_time=0.7)
        self.play(FadeIn(catalogo, shift=0.18 * RIGHT), run_time=0.9)
        rot.mostrar(pie_curso("Un catálogo cerrado: esto y solo esto puede "
                              "hacer."), zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- momento: el agente elige consultar_tle --------------------------
        caja_tle = catalogo.cajas["consultar_tle"]
        conexion = conectar(agente, caja_tle, color=C_ACENTO)
        self.play(Indicate(caja_tle, color=C_ACENTO), GrowArrow(conexion),
                  run_time=1.1)
        rot.mostrar(pie_curso("El agente elige la herramienta..."),
                   zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- momento: la llama con argumentos concretos -----------------------
        tarjeta = tarjeta_json(['{ "sat": "NOAA-19",', '  "fecha": "hoy" }'])
        tarjeta.move_to(np.array([-3.9, -1.3, 0.0]))
        self.play(FadeIn(tarjeta, shift=0.18 * UP), run_time=0.7)
        self.play(flujo([conexion], color=C_ACENTO), run_time=1.0)
        rot.mostrar(pie_curso("...y la llama con argumentos concretos."),
                   zona="abajo", run_time=0.5)
        self.wait(4.2)

        # --- momento: la respuesta vuelve como observacion --------------------
        self.play(FadeOut(conexion), run_time=0.4)
        observacion = burbuja("TLE recibido: época 2026-08-06",
                              tipo="observacion")
        observacion.move_to(tarjeta.get_center())
        self.play(ReplacementTransform(tarjeta, observacion), run_time=1.1)
        rot.mostrar(pie_curso("Acción, resultado, siguiente decisión."),
                   zona="abajo", run_time=0.5)
        self.wait(9.0)
