class Clip7(Scene):
    """7 - Apilar capas: el Transformer. Una fila de tokens sube por dos
    bloques transformer apilados y sale convertida en un vector mas fino;
    dos pasadas alcanzan para intuir por que un LLM real apila decenas.
    (~30 s)"""

    def _releva_contador(self, anterior, texto):
        """HUD 'CAPAS: N' en la esquina UR. Relevo estricto: primero sale
        el contador previo, LUEGO entra el nuevo (nunca coexisten)."""
        nuevo = etiqueta_hud(texto)
        nuevo.to_corner(UR, buff=0.5)
        if anterior is None:
            self.play(FadeIn(nuevo, shift=0.12 * LEFT), run_time=0.4)
        else:
            self.play(FadeOut(anterior, shift=0.12 * RIGHT), run_time=0.3)
            self.play(FadeIn(nuevo, shift=0.12 * LEFT), run_time=0.4)
        return nuevo

    def construct(self):
        rot = Rotulos(self)

        # --- HUD y titulo ---------------------------------------------------
        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)

        titulo = titulo_curso("Apilar capas: el Transformer")
        rot.mostrar(titulo, zona="arriba", run_time=0.7)
        self.wait(1.0)

        # --- momento: la fila de tokens, abajo del todo ----------------------
        fila = fila_tokens("cada palabra atiende a todas")
        fila.scale(0.85)
        fila.move_to(2.2 * DOWN)
        self.play(FadeIn(fila, lag_ratio=0.06), run_time=1.0)
        self.wait(1.3)

        # --- momento: la pila de dos bloques transformer ---------------------
        capa1 = bloque_transformer(color=C_ACENTO)
        capa1.move_to(0.6 * DOWN)
        conexion_base = conectar(fila, capa1, color=C_EJE)
        self.play(FadeIn(capa1, shift=0.2 * UP), Create(conexion_base),
                  run_time=0.8)

        capa2 = bloque_transformer(color=C_ACENTO)
        capa2.move_to(0.7 * UP)
        conexion_media = conectar(capa1, capa2, color=C_EJE)
        self.play(FadeIn(capa2, shift=0.2 * UP), Create(conexion_media),
                  run_time=0.8)

        # --- momento: la ficha de salida, arriba del todo ---------------------
        ficha_salida = ficha_token("salida", color=C_VECTOR)
        ficha_salida.move_to(1.9 * UP)
        conexion_top = conectar(capa2, ficha_salida, color=C_EJE)
        self.play(FadeIn(ficha_salida, shift=0.2 * UP), Create(conexion_top),
                  run_time=0.8)
        self.wait(1.1)

        rot.mostrar(pie_curso("Atención y mezcla, una capa tras otra."),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        segmentos = [conexion_base, conexion_media, conexion_top]
        fichas = fila.fichas
        mitad = len(fichas) // 2 + 1

        # --- momento: primera pasada, la mitad de las fichas se vuelve
        # violeta (el significado empieza a refinarse) ------------------------
        contador = self._releva_contador(None, "CAPAS: 2")
        self.play(flujo(segmentos, color=C_ACENTO), run_time=2.1)
        self.play(*[f.animate.set_color(C_VECTOR) for f in fichas[:mitad]],
                  run_time=1.0)
        rot.mostrar(pie_curso("Cada capa refina lo que cada palabra "
                              "significa."), zona="abajo", run_time=0.5)
        self.wait(2.7)

        # --- momento: segunda pasada, el resto de la fila se pone violeta ----
        contador = self._releva_contador(contador, "CAPAS: 96")
        self.play(flujo(segmentos, color=C_ACENTO), run_time=2.1)
        self.play(*[f.animate.set_color(C_VECTOR) for f in fichas[mitad:]],
                  run_time=1.0)
        rot.mostrar(pie_curso("Un LLM apila decenas de estas capas."),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- momento: cierre, destello completo por toda la pila -------------
        self.play(FadeOut(contador, shift=0.12 * RIGHT), run_time=0.35)
        self.play(flujo(segmentos, color=C_ACENTO),
                  Flash(ficha_salida, color=C_ACENTO), run_time=1.7)
        rot.mostrar(pie_curso("Esto es un Transformer. Nada más... y nada "
                              "menos."), zona="abajo", run_time=0.5)
        self.wait(3.1)
