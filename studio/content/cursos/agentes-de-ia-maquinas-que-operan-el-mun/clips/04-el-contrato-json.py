class Clip4(Scene):
    """4 - El contrato: JSON Schema. Dos tarjetas JSON lado a lado, una
    valida y una invalida por tipos, muestran que el contrato se aplica
    ANTES de que el agente actue; el error vuelve como una burbuja roja
    transitoria que se convierte en la tarjeta corregida, en el mismo
    sitio que ocupaba la invalida."""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: titulo y HUD del modulo ------------------------------
        titulo = titulo_curso("El contrato: JSON Schema")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        modulo = hud_modulo("Modulo 04")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.wait(2.0)

        # --- momento: la tarjeta valida --------------------------------------
        tarjeta_izq = tarjeta_json(['{ "sat": "NOAA-19",',
                                    '  "elevacion_min": 10 }'], valida=True)
        tarjeta_izq.move_to(np.array([-2.7, 0.3, 0.0]))
        self.play(FadeIn(tarjeta_izq, shift=0.18 * UP), run_time=0.8)
        rot.mostrar(pie_curso("El contrato dice qué campos, de qué tipo, y "
                              "cuándo usarla."), zona="abajo", run_time=0.5)
        self.wait(3.2)

        # --- momento: la tarjeta invalida, en secuencia -----------------------
        tarjeta_der = tarjeta_json(['{ "sat": 42,',
                                    '  "elevacion_min": "alta" }'],
                                   valida=False)
        tarjeta_der.move_to(np.array([2.7, 0.3, 0.0]))
        self.play(FadeIn(tarjeta_der, shift=0.18 * UP), run_time=0.8)
        rot.mostrar(pie_curso("Tipos equivocados: rechazo inmediato, antes "
                              "de tocar nada."), zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- momento: el error sube como una burbuja roja ---------------------
        origen_error = tarjeta_der.get_top()
        self.play(FadeOut(tarjeta_der), run_time=0.5)
        burbuja_error = burbuja("error: sat debe ser texto", tipo="peligro")
        burbuja_error.move_to(np.array([2.7, 1.7, 0.0]))
        flecha_error = Arrow(origen_error, burbuja_error.get_bottom(),
                             color=C_ACENTO, buff=0.12)
        self.play(GrowArrow(flecha_error),
                  FadeIn(burbuja_error, shift=0.18 * UP), run_time=1.0)
        rot.mostrar(pie_curso("El error es información: el agente corrige "
                              "y reintenta."), zona="abajo", run_time=0.5)
        self.wait(3.8)

        # --- momento: el error se convierte en tarjeta corregida ---------------
        self.play(FadeOut(flecha_error), run_time=0.4)
        tarjeta_corregida = tarjeta_json(['{ "sat": "NOAA-19",',
                                          '  "elevacion_min": 10 }'],
                                         valida=True)
        tarjeta_corregida.move_to(np.array([2.7, 0.3, 0.0]))
        self.play(ReplacementTransform(burbuja_error, tarjeta_corregida),
                  run_time=1.1)
        self.play(Indicate(tarjeta_izq, color=C_OK),
                  Indicate(tarjeta_corregida, color=C_OK), run_time=0.9)
        rot.mostrar(pie_curso("Validar en el servidor, siempre."),
                   zona="abajo", run_time=0.5)
        self.wait(9.0)
