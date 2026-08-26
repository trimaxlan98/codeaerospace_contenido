class Clip1(Scene):
    """7.1.1 - Contra la velocidad de la luz no se optimiza: la distancia
    real entre Ciudad de Mexico y Madrid fija un RTT minimo que ningun
    router del mundo puede bajar. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El viaje largo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el pedido cruza el mundo ----------------------------
        rot.mostrar(pie_curso("Un usuario en Ciudad de Mexico pide algo a "
                              "un servidor que vive en Madrid."),
                    zona="abajo", run_time=0.5)
        origen = nodo("host", "CDMX", 0.55)
        origen.move_to(LEFT * 5.2 + UP * 0.3)
        destino = nodo("servidor", "Madrid", 0.55)
        destino.move_to(RIGHT * 5.2 + UP * 0.3)
        cable = enlace(origen.centro(), destino.centro(), color=C_RED,
                       punteada=True)
        self.play(FadeIn(origen), FadeIn(destino), run_time=0.6)
        self.play(Create(cable.linea), run_time=1.0)
        dist = tag_hud("%s km" % fmt(D_CDMX_MADRID, 0), font_size=20,
                       color=C_CIFRA)
        dist.next_to(cable, UP, buff=0.22)
        self.play(FadeIn(dist), run_time=0.4)
        paq = ficha("GET", lado=0.42)
        paq.move_to(cable.a)
        self.play(FadeIn(paq), run_time=0.3)
        self.wait(4.0)

        # --- momento: el viaje ida y vuelta a la velocidad de la luz -------
        rot.mostrar(pie_curso("Nueve mil kilometros, ida y vuelta, a la "
                              "velocidad de la luz en fibra: dos tercios "
                              "de c."),
                    zona="abajo", run_time=0.5)
        self.play(MoveAlongPath(paq, cable.linea), run_time=1.6,
                  rate_func=linear)
        vuelta = enlace(destino.centro(), origen.centro())
        respuesta = ficha("200", lado=0.42, color=C_OK)
        respuesta.move_to(vuelta.a)
        self.play(FadeIn(respuesta), run_time=0.2)
        self.play(MoveAlongPath(respuesta, vuelta.linea), run_time=1.6,
                  rate_func=linear)
        limite = regla_viajes(1, etiqueta="limite fisico (2c/3)",
                              ms=RTT_MIN_LARGO)
        limite.move_to(DOWN * 1.55)
        self.play(FadeIn(limite), run_time=0.6)
        self.wait(4.0)

        # --- momento: eso no se negocia ------------------------------------
        rot.mostrar(pie_curso("Ni el mejor router del mundo baja esa "
                              "cifra: es la luz, no es software."),
                    zona="abajo", run_time=0.5)
        medido = regla_viajes(1, etiqueta="medido, con routers de por medio",
                              ms=RTT_REAL_LARGO)
        medido.move_to(DOWN * 2.35)
        self.play(FadeIn(medido), run_time=0.6)
        self.wait(4.5)

        # --- momento: lo que si se puede mover ------------------------------
        rot.mostrar(pie_curso("Contra la velocidad de la luz no se "
                              "optimiza. Se acorta el camino."),
                    zona="abajo", run_time=0.5)
        self.wait(6.5)
