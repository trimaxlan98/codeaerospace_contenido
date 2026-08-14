class Clip8(Scene):
    """8 - La nube es un pacto. La cuenta final: una maquina al 99.9 %,
    tres replicas al 99.9999999 %; el 63 % de algo caido con mil maquinas
    es el mismo dato del clip 1, ahora con salida. Recapitulacion en
    miniaturas y cierre del curso. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("La nube es un pacto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: la cuenta final -------------------------------------
        rot.mostrar(pie_curso("La fiabilidad no se compra: se construye."),
                    zona="abajo", run_time=0.5)

        una = tag_hud(f"una máquina: {P_MAQUINA:.1%}", font_size=30,
                      color=C_NODO)
        tres = tag_hud(f"tres réplicas: {NUEVE_NUEVES:.7%}", font_size=40,
                       color=C_OK)
        cuenta = VGroup(una, tres).arrange(DOWN, buff=0.46)
        if cuenta.width > 10.6:
            cuenta.scale_to_fit_width(10.6)
        cuenta.move_to(DOWN * 0.15)

        self.play(FadeIn(una, shift=0.14 * UP), run_time=0.7)
        self.wait(0.8)
        self.play(FadeIn(tres, shift=0.14 * UP), run_time=0.9)
        self.play(Indicate(tres, color=C_OK, scale_factor=1.10),
                  run_time=0.9)
        self.wait(3.0)

        # --- momento: el mismo dato del clip 1, con salida ----------------
        rot.mostrar(pie_curso("Nadie promete máquinas perfectas: se promete "
                              "el pacto entre ellas."),
                    zona="abajo", run_time=0.5)

        caida = tag_hud(f"1000 máquinas: {P_CAIDA_1000:.0%} con algo caído",
                        font_size=24, color=C_FALLO)
        caida.next_to(cuenta, UP, buff=0.72)
        self.play(FadeIn(caida, shift=0.12 * DOWN), run_time=0.8)
        self.wait(4.2)

        # --- momento: la recapitulacion -----------------------------------
        rot.mostrar(pie_curso("Fallas, tiempo, mayorías, reparto: cada pieza "
                              "es matemática."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cuenta), FadeOut(caida), run_time=0.7)

        nube = rejilla_nodos(filas=3, columnas=5)
        nube.apaga(indices_caidos(15, 2, SEMILLA_CAIDOS))
        nube.scale_to_fit_height(1.1)
        # Los aros salen de ESTA pieza y se agrupan antes de escalar: si se
        # pidieran a otro nodos_quorum() no viajarian con el grupo.
        nq = nodos_quorum()
        quorum = VGroup(nq, nq.aro(IDX_W, C_OK, 0.30),
                        nq.aro(IDX_R, C_MENSAJE, 0.42))
        quorum.scale_to_fit_width(3.0)
        minis = VGroup(
            nube,
            diagrama_lamport().scale_to_fit_height(1.4),
            quorum,
            anillo_hash(nodo_extra=NODO_NUEVO).scale_to_fit_height(1.5),
        ).arrange(RIGHT, buff=0.75)
        if minis.width > 11.0:
            minis.scale_to_fit_width(11.0)
        minis.move_to(UP * 0.35)

        self.play(LaggedStart(*[FadeIn(m, shift=0.18 * UP) for m in minis],
                              lag_ratio=0.22), run_time=1.9)
        self.wait(4.6)

        # --- momento: cierre del curso ------------------------------------
        rot.limpiar("arriba", run_time=0.3)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(minis), run_time=0.5)

        cierre = VGroup(
            titulo_marca("Ninguna máquina es fiable.", font_size=38),
            Text("El pacto entre ellas, sí.", font_size=26, color=C_NODO),
        ).arrange(DOWN, buff=0.4)
        cierre.move_to(UP * 0.2)
        self.play(Write(cierre[0]), run_time=1.2)
        self.play(FadeIn(cierre[1], shift=0.18 * UP), run_time=0.8)
        self.wait(6.0)
