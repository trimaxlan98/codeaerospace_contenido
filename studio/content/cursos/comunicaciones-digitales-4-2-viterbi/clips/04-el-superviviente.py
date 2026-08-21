class Clip4(Scene):
    """4.2.4 - El superviviente: el camino ganador se ilumina de vuelta,
    los bits vuelven a ser los transmitidos y los 2 errores caen a 0.
    Cierre de leccion. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El superviviente")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # la rejilla llega ya podada del clip 3: solo viven las ramas que
        # ganaron su nodo (mismo criterio, misma tabla)
        tr = trellis(pasos=PASOS, ancho=8.6, alto=2.4)
        tr.move_to(DOWN * 0.55)
        ramas = tr.todas_ramas(color=C_REJILLA, grosor=1.2, opacidad=0.55)
        for t in range(PASOS):
            d = poda(t)
            for s, b, s2, _sal in RAMAS_CONV:
                ln = ramas[idx_rama(t, s, b)]
                if not vivo(t, s):
                    ln.set_stroke(opacity=0.05)
                elif d[s2]["gana"] == (s, b):
                    ln.set_stroke(C_SENAL, width=2.2, opacity=0.95)
                else:
                    ln.set_stroke(opacity=0.10)
        mets = VGroup(*[_con_fondo(tr.metrica(PASOS, s, METRICAS[PASOS][s]),
                                   buff=0.08)
                        for s in range(N_ESTADOS) if vivo(PASOS, s)])
        marco = SurroundingRectangle(
            mets[sum(1 for s in range(ESTADO_FINAL) if vivo(PASOS, s))],
            color=C_COD, buff=0.03)

        # --- momento: el camino ganador se ilumina de vuelta --------------
        rot.mostrar(pie_curso("El más barato de los cuatro finales guarda su "
                              "historia: se sigue hacia atrás."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(tr), FadeIn(ramas), FadeIn(mets), FadeIn(marco),
                  run_time=1.0)
        cam = tr.camino(CAMINO, color=C_COD, grosor=3.6)
        cam.reverse_points()          # se dibuja desde el FINAL hacia atras
        self.play(Create(cam), run_time=2.6)
        self.wait(2.3)

        # --- momento: los bits del camino son los del mensaje -------------
        rot.mostrar(pie_curso("El camino dice qué bits entraron. Y son "
                              "exactamente los que salieron."),
                    zona="abajo", run_time=0.5)
        tren_tx = tren_bits(MENSAJE, lado=0.42)
        tren_tx.move_to(UP * 2.45)
        et_tx = tag_junto(tren_tx, "transmitido", direccion=LEFT, buff=0.26)
        tren_dec = tren_bits(BITS_DEC, lado=0.42, color=C_COD)
        tren_dec.move_to(UP * 1.85)
        et_dec = tag_junto(tren_dec, "decodificado", direccion=LEFT,
                           buff=0.26)
        self.play(FadeIn(tren_tx), FadeIn(et_tx), run_time=0.6)
        self.play(TransformFromCopy(cam, tren_dec), FadeIn(et_dec),
                  run_time=1.4)
        panel = panel_derecha(
            tag_hud(f"diferencias = {N_DIF_BITS}", color=C_COD))
        self.play(FadeIn(panel), run_time=0.5)
        self.wait(2.7)

        # --- momento: los dos bits volteados, corregidos ------------------
        rot.mostrar(pie_curso("Y los dos bits que volteó el canal quedan "
                              "corregidos por el camino."),
                    zona="abajo", run_time=0.5)
        tren16 = tren_bits(RECIBIDO, lado=0.42)
        tren16.move_to(DOWN * 0.35)
        for _i in IDX_ERROR:
            tren16.marcar(_i)
        cuenta = tag_hud(f"errores = {N_ERR_CANAL}", font_size=20,
                         color=C_RUIDO)
        cuenta.next_to(tren16, DOWN, buff=0.34)
        self.play(FadeOut(tr), FadeOut(ramas), FadeOut(mets),
                  FadeOut(marco), FadeOut(cam), FadeIn(tren16),
                  FadeIn(cuenta), run_time=1.0)
        tren16b = tren16.con_bits(CORREGIDO)
        for _i in IDX_ERROR:
            tren16b.marcar(_i, color=C_COD)
        cuenta2 = tag_hud(f"errores = {N_ERR_VITERBI}", font_size=20,
                          color=C_COD)
        cuenta2.move_to(cuenta)
        self.play(Transform(tren16, tren16b), Transform(cuenta, cuenta2),
                  run_time=1.4)
        self.wait(3.2)

        # --- momento: Voyager llevo esta maquina --------------------------
        rot.mostrar(pie_curso("Voyager llevó este decodificador a los "
                              "planetas exteriores, con más memoria."),
                    zona="abajo", run_time=0.5)
        enl = enlace_tierra(dist=3.6, radio_tierra=0.44, curva=0.32)
        enl.rotate(PI)
        enl.move_to(DOWN * 0.5)
        paq = enl.paquete(radio=0.07)
        cam_ida = enl.camino.copy().reverse_points()
        paq.move_to(cam_ida.point_from_proportion(0.0))
        panel_v = panel_derecha(
            tag_hud(f"Voyager: K = {VOYAGER_K}"),
            tag_hud(f"{VOYAGER_ESTADOS} estados, no {N_ESTADOS}"))
        self.play(FadeOut(tren16), FadeOut(cuenta), FadeOut(tren_tx),
                  FadeOut(et_tx), FadeOut(tren_dec), FadeOut(et_dec),
                  FadeOut(panel), run_time=0.7)
        self.play(FadeIn(enl), FadeIn(panel_v), run_time=0.7)
        self.play(PulsoDeSenal(paq, cam_ida, rate_func=linear),
                  destello(enl.camino, color=C_COD), run_time=1.6)
        self.wait(2.6)

        # --- cierre de leccion --------------------------------------------
        cierre_leccion(
            self, rot,
            "Entre todos los mensajes posibles,",
            "gana el que menos ruido necesita.",
            "Siguiente leccion: LDPC, el murmullo que corrige.",
            enl, paq, panel_v)
