class Clip4(Scene):
    """4.1.4 - El mismo mensaje codificado con un bit volteado: el par
    recibido no coincide con NINGUNA de las dos salidas posibles del
    estado (RAMAS_CONV): incoherencia detectable. Cierre de leccion.
    (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La memoria protege")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mismo mensaje, codificado igual -----------------------
        rot.mostrar(pie_curso("El mismo mensaje, codificado exactamente "
                              "igual que antes."),
                    zona="abajo", run_time=0.5)
        entrada = tren_bits(BITS_MENSAJE, lado=0.42)
        entrada.move_to(UP * 1.7)
        et_entrada = tag_junto(entrada, "el mensaje", direccion=UP,
                               buff=0.14)
        enviado = tren_bits(SALIDA_CONV, lado=0.38, color=C_COD)
        enviado.move_to(UP * 0.55)
        et_enviado = tag_junto(enviado, "enviado", direccion=DOWN, buff=0.14)
        self.play(FadeIn(entrada), FadeIn(et_entrada), run_time=0.7)
        self.play(FadeIn(enviado), FadeIn(et_enviado), run_time=0.9)
        self.wait(3.6)

        # --- momento: un solo bit se voltea --------------------------------------
        rot.mostrar(pie_curso("Un solo bit se voltea en la salida: uno "
                              "solo, en rojo."),
                    zona="abajo", run_time=0.5)
        recibido = enviado.con_bits(RX_CONV)
        recibido.move_to(DOWN * 0.9)
        recibido.marcar(IDX_ERROR, color=C_RUIDO)
        et_recibido = tag_junto(recibido, "recibido", direccion=DOWN,
                                buff=0.14)
        self.play(TransformFromCopy(enviado, recibido), FadeIn(et_recibido),
                  run_time=1.2)
        self.wait(4.2)

        # --- momento: la incoherencia --------------------------------------------
        rot.mostrar(pie_curso(f"En el estado {ESTADO_ERROR_BIN}, solo hay "
                              "dos salidas posibles - y ninguna es esta."),
                    zona="abajo", run_time=0.5)
        lineas_opcion = [
            tag_hud(f"bit={fmt(b, 0)} -> {fmt(sal[0], 0)}{fmt(sal[1], 0)}",
                   font_size=18, color=C_COD)
            for b, sal in OPCIONES_ERROR]
        linea_recibido = tag_hud(
            f"recibido = {fmt(RECIBIDO_PAR[0], 0)}{fmt(RECIBIDO_PAR[1], 0)}",
            font_size=18, color=C_RUIDO)
        panel = panel_derecha(*lineas_opcion, linea_recibido)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(1.0)
        incoherencia = Text("INCOHERENCIA", font_size=26, color=C_RUIDO)
        incoherencia.next_to(et_recibido, DOWN, buff=0.28)
        self.play(FadeIn(incoherencia, scale=0.85),
                  Indicate(recibido.digito(IDX_ERROR), color=C_RUIDO),
                  run_time=1.0)
        self.wait(4.0)

        # --- cierre de leccion -----------------------------------------------
        rot.mostrar(pie_curso("Detectar el error ya es posible. "
                              "Corregirlo, en la proxima leccion."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)

        cierre_leccion(
            self, rot,
            "Un código sin memoria olvida.",
            "Este recuerda por ti.",
            "Siguiente leccion: Viterbi, el camino mas probable.",
            entrada, et_entrada, enviado, et_enviado, recibido, et_recibido,
            panel, incoherencia)
