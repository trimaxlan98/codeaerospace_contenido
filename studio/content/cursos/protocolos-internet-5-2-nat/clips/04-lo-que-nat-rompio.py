class Clip4(Scene):
    """5.2.4 - Lo que NAT rompio: nadie de afuera inicia nada sin permiso
    (nat_entrante(), 2 de 4 bloqueados). Cierre honesto en dos
    direcciones: le regalo 20 anos a IPv4 y rompio el extremo a extremo.
    Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Lo que NAT rompio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: puertas para salir sobran, para entrar no hay ------
        rot.mostrar(pie_curso("Puertas para salir sobran. Puertas para "
                              "entrar, no hay ninguna."),
                    zona="abajo", run_time=0.5)
        nube = nodo("nube", "Internet", 0.55)
        nube.move_to(RIGHT * 3.4 + UP * 1.3)
        router = nodo("router", "router", 0.55)
        router.move_to(UP * 1.3)
        casa = VGroup(nodo("host", None, 0.30), nodo("host", None, 0.30))
        casa.arrange(DOWN, buff=0.65)
        casa.move_to(LEFT * 3.4 + UP * 1.3)
        lineas_casa = VGroup(*[Line(h.centro(), router.centro(),
                                    color=C_RED, stroke_width=1.3,
                                    stroke_opacity=0.6) for h in casa])
        link_ext = enlace(router.centro(), nube.centro())
        self.play(FadeIn(casa), Create(lineas_casa), FadeIn(router),
                  Create(link_ext.linea), FadeIn(nube), run_time=1.2)
        self.wait(1.4)
        intento = Arrow(nube.centro(), router.centro(), color=C_PERDIDA,
                        buff=0.42, stroke_width=3.4)
        self.play(Create(intento), run_time=0.6)
        cruz = tag_hud("X", font_size=30, color=C_PERDIDA)
        cruz.move_to(router.centro() + UP * 0.55)
        et_bloq = tag_hud("conexion no solicitada: bloqueada",
                          font_size=18, color=C_PERDIDA)
        et_bloq.next_to(router, DOWN, buff=1.2)
        self.play(FadeIn(cruz, scale=1.4), FadeIn(et_bloq), run_time=0.5)
        self.wait(3.2)

        # --- momento: nat_entrante(), contado -----------------------------
        rot.mostrar(pie_curso("Cuatro intentos de entrar desde afuera. "
                              "Solo pasan los que ya tenian una fila."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(casa, lineas_casa, router, link_ext.linea,
                                 nube, intento, cruz, et_bloq)),
                  run_time=0.6)
        filas_entra = [[str(p["puerto"]), "PASA" if p["pasa"] else
                       "BLOQUEADO"] for p in NAT_ENTRA["pasos"]]
        tab2 = tabla(["Puerto publico", "Resultado"], filas_entra,
                    anchos=[3.2, 3.0], alto=0.52, fs=17)
        tab2.move_to(UP * 0.35)
        for i, p in enumerate(NAT_ENTRA["pasos"]):
            tab2.celda(i, 1).set_color(C_OK if p["pasa"] else C_PERDIDA)
        self.play(FadeIn(tab2), run_time=0.9)
        et_bloqn = tag_hud("bloqueados: %d de %d" % (BLOQUEADOS,
                                                      TOTAL_INTENTOS),
                           font_size=20, color=C_PERDIDA)
        et_bloqn.next_to(tab2, DOWN, buff=0.40)
        self.play(FadeIn(et_bloqn), run_time=0.5)
        self.wait(4.2)

        # --- momento: honestidad en las dos direcciones -------------------
        rot.mostrar(pie_curso("NAT le regalo veinte anos a IPv4. Pero "
                              "rompio el contacto directo entre dos "
                              "extremos.", font_size=22),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(VGroup(tab2, et_bloqn)), run_time=0.5)
        soluciones = tag_hud("por eso existen STUN, TURN y el "
                             "agujereado de UDP", font_size=20,
                             color=C_CIFRA)
        soluciones.move_to(UP * 0.2)
        self.play(FadeIn(soluciones, shift=0.15 * UP), run_time=0.7)
        self.wait(4.4)
        self.play(FadeOut(soluciones), run_time=0.4)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "NAT le regalo veinte anos a IPv4.",
            "Y a cambio se quedo con la llave de la puerta.",
            "Siguiente: ver la red, ICMP, ping y traceroute.",
            espera=5.0)
