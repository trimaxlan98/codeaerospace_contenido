class Clip4(Scene):
    """5.3.4 - PMTUD real: el tercer enlace tiene un MTU menor (1400); el
    paquete con DF rebota con "fragmentacion necesaria" y el emisor
    ajusta su tamano. Si alguien filtra ese ICMP, el agujero negro: la
    conexion se cuelga sin motivo aparente. Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El MTU escondido")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: cada enlace tiene su propio limite --------------------
        rot.mostrar(pie_curso("Cada enlace del camino tiene su propio "
                              "limite de tamano: el MTU."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_MTU, ARISTAS_MTU, TIPOS_MTU, costos=True,
                        tam=0.46, fs=15)
        topo.move_to(UP * 1.35)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        self.wait(2.4)

        # --- momento: sale un paquete de 1500, con DF ------------------------
        rot.mostrar(pie_curso("Sale un paquete de 1500 bytes con la "
                              "bandera DF: no fragmentar, bajo ninguna "
                              "circunstancia."),
                    zona="abajo", run_time=0.5)
        pk = ficha("1500 DF", lado=0.62, fs=13, color=C_PAQUETE)
        pk.move_to(topo.punto("origen"))
        self.add(pk)
        self.play(MoveAlongPath(pk, topo.camino(["origen", "R1", "R2"])),
                  run_time=1.1)
        # El limite esta en el ENLACE R2-R3 (MTU 1400), no en el nodo R2:
        # avanza un tramo corto sobre ese cable, por DEBAJO, para no
        # montarse en R2 ni tapar el rotulo "1400" que cuelga arriba.
        tope = VMobject()
        tope.set_points_as_corners([topo.punto("R2") + DOWN * 0.36,
                                    topo.enlace("R2", "R3").punto_en(0.32)
                                    + DOWN * 0.36])
        self.play(MoveAlongPath(pk, tope), run_time=0.5)
        self.wait(1.0)

        # --- momento: no cabe, rebota con ICMP ------------------------------
        rot.mostrar(pie_curso("En el siguiente enlace no cabe: rebota con "
                              "un ICMP de fragmentacion necesaria, MTU "
                              "1400."),
                    zona="abajo", run_time=0.5)
        self.play(pk.animate.set_color(C_PERDIDA), run_time=0.35)
        self.play(FadeOut(pk), run_time=0.45)
        aviso = Arrow(topo.enlace("R2", "R3").punto_en(0.32) + DOWN * 0.55,
                     topo.punto("origen") + DOWN * 0.55, color=C_CAPA,
                     stroke_width=3.0, buff=0.10,
                     max_tip_length_to_length_ratio=0.05)
        et_icmp = tag_hud("ICMP: fragmentacion necesaria, MTU=1400",
                          font_size=18, color=C_CAPA)
        et_icmp.move_to(DOWN * 1.35)
        self.play(Create(aviso), run_time=0.8)
        self.play(FadeIn(et_icmp), run_time=0.4)
        self.wait(2.3)

        # --- momento: el emisor ajusta su tamano ---------------------------
        self.play(FadeOut(aviso), FadeOut(et_icmp), run_time=0.4)
        rot.mostrar(pie_curso("El emisor baja su tamano a 1400 y repite: "
                              "ya nadie se queja."),
                    zona="abajo", run_time=0.5)
        tab = tabla(TABLA_MTU_CAB, TABLA_MTU_FILAS,
                   anchos=[1.0, 1.2, 1.3, 5.9], alto=0.42, fs=14,
                   color_cab=C_CAPA, resaltar=2)
        tab.move_to(DOWN * 0.65)
        self.play(FadeIn(tab), run_time=1.0)
        et_final = tag_hud("MTU del camino: %d B  (reduccion de %d B)"
                           % (PMTU_OK["mtu_camino"], PMTU_OK["reduccion"]),
                           font_size=19)
        et_final.next_to(tab, DOWN, buff=0.30)
        self.play(FadeIn(et_final), run_time=0.5)
        self.wait(3.4)

        # --- momento: agujero negro si se filtra el ICMP --------------------
        self.play(FadeOut(topo), FadeOut(tab), FadeOut(et_final),
                  run_time=0.5)
        rot.mostrar(pie_curso("Pero si un firewall filtra ese ICMP, el "
                              "mensaje nunca llega: el emisor no se "
                              "entera de nada."),
                    zona="abajo", run_time=0.5)
        topo2 = topologia(POS_MTU, ARISTAS_MTU, TIPOS_MTU, costos=True,
                         tam=0.46, fs=15)
        topo2.move_to(UP * 1.35)
        self.play(FadeIn(topo2.enlaces), FadeIn(topo2.nodos), run_time=0.8)
        pk2 = ficha("1500 DF", lado=0.62, fs=13, color=C_PAQUETE)
        pk2.move_to(topo2.punto("origen"))
        self.add(pk2)
        self.play(MoveAlongPath(pk2, topo2.camino(["origen", "R1", "R2"])),
                  run_time=1.0)
        tope2 = VMobject()
        tope2.set_points_as_corners([topo2.punto("R2") + DOWN * 0.36,
                                     topo2.enlace("R2", "R3").punto_en(0.32)
                                     + DOWN * 0.36])
        self.play(MoveAlongPath(pk2, tope2), run_time=0.4)
        self.play(pk2.animate.set_color(C_PERDIDA), run_time=0.3)
        self.play(pk2.animate.scale(1.5).set_opacity(0.0), run_time=0.6)
        self.remove(pk2)
        cruz = tag_hud("X  el ICMP se filtra: nunca sale de aqui",
                       font_size=17, color=C_PERDIDA)
        cruz.next_to(topo2.enlace("R2", "R3").punto_en(0.32), DOWN,
                    buff=0.55)
        self.play(FadeIn(cruz), run_time=0.4)
        self.wait(1.2)

        rot.mostrar(pie_curso("Sin el aviso, la conexion se cuelga sin "
                              "motivo aparente: el agujero negro de "
                              "PMTUD."),
                    zona="abajo", run_time=0.5)
        et_negro = tag_hud("agujero negro: %d intentos, cero respuesta"
                           % PMTU_NEGRO["intentos"], font_size=20,
                           color=C_PERDIDA)
        et_negro.move_to(DOWN * 1.35)
        puntos = tag_hud(". . .", font_size=26, color=C_PERDIDA)
        puntos.next_to(et_negro, DOWN, buff=0.28)
        self.play(FadeIn(et_negro), run_time=0.5)
        self.play(FadeIn(puntos), run_time=0.4)
        self.wait(2.6)

        # --- cierre de la leccion -------------------------------------------
        cierre_leccion(
            self, rot,
            "La red no es opaca.",
            "Sabe quejarse, si la dejas.",
            "Siguiente: HTTP, pedir y responder.",
            topo2, cruz, et_negro, puntos, espera=4.6)
