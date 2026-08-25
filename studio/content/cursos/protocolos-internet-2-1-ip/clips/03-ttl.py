class Clip3(Scene):
    """2.1.3 - TTL: el seguro contra los bucles. El paquete da vueltas, el
    contador baja de 64 a 0 y muere en el salto 64. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("TTL: el seguro contra los bucles")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_BUCLE, ARISTAS_BUCLE, TIPOS_BUCLE,
                         costos=False, tam=0.46, fs=14)
        topo.move_to(UP * 0.72)

        def marcador(salto):
            t = tag_hud("TTL  %02d" % TTL_EN(salto), font_size=30)
            t.move_to(np.array([5.30, 1.80, 0.0]))
            return t

        # --- momento: el camino se cierra sobre si mismo ------------------
        rot.mostrar(pie_curso("Basta una tabla mal escrita para que el "
                              "camino se cierre sobre si mismo."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        aro = VGroup(*[topo.enlace(a, b).linea.copy().set_stroke(
            C_PERDIDA, width=5.0)
            for a, b in (("R1", "R2"), ("R2", "R3"),
                         ("R3", "R4"), ("R4", "R1"))])
        self.play(LaggedStart(*[Create(x) for x in aro], lag_ratio=0.4),
                  run_time=1.6)
        et_bucle = tag_hud("cuatro routers que se apuntan en circulo",
                           font_size=20, color=C_PERDIDA)
        et_bucle.move_to(DOWN * 2.05)
        self.play(FadeIn(et_bucle), run_time=0.4)
        self.wait(2.8)

        # --- momento: el freno que trae cada datagrama --------------------
        self.play(FadeOut(et_bucle), run_time=0.3)
        rot.mostrar(pie_curso("Sin freno daria vueltas para siempre. IP le "
                              "pone uno: el tiempo de vida."),
                    zona="abajo", run_time=0.5)
        p = ficha("", lado=0.30)
        p.move_to(topo.punto("A"))
        cont = tag_hud("TTL  %02d" % TTL0, font_size=30)
        cont.move_to(np.array([5.30, 1.80, 0.0]))
        et_cont = tag_hud("resta uno por salto", font_size=17,
                          color=C_EJE)
        et_cont.next_to(cont, DOWN, buff=0.22)
        self.add(p)
        self.play(FadeIn(cont), FadeIn(et_cont), run_time=0.4)
        self.play(MoveAlongPath(p, ruta_de(topo, ["A", "R1"])), run_time=0.7)
        self.play(Transform(cont, marcador(1)), run_time=0.25)
        for s in range(2, 6):
            self.play(MoveAlongPath(p, ruta_de(
                topo, [TTL_RUTA[s - 2]["nodo"], TTL_RUTA[s - 1]["nodo"]])),
                run_time=0.5)
            self.play(Transform(cont, marcador(s)), run_time=0.22)
        self.wait(2.2)

        # --- momento: dieciseis vueltas -----------------------------------
        rot.mostrar(pie_curso("Cuatro routers por vuelta: el contador baja "
                              "vuelta tras vuelta, sin llegar nunca."),
                    zona="abajo", run_time=0.5)
        for s in range(6, 18):
            self.play(MoveAlongPath(p, ruta_de(
                topo, [TTL_RUTA[s - 2]["nodo"], TTL_RUTA[s - 1]["nodo"]])),
                Transform(cont, marcador(s)), run_time=0.20)
        et_vueltas = tag_hud("%d saltos por vuelta  x  %d vueltas  =  %d "
                             "saltos" % (len(CICLO), TTL_VUELTAS,
                                         TTL_SALTOS), font_size=21)
        et_vueltas.move_to(DOWN * 2.05)
        puntos = tag_hud(". . .", font_size=26, color=C_EJE)
        puntos.next_to(cont, UP, buff=0.24)
        self.play(FadeIn(puntos), Transform(cont, marcador(61)),
                  run_time=0.6)
        self.play(FadeIn(et_vueltas), run_time=0.5)
        self.wait(2.8)

        # --- momento: el salto 64 -----------------------------------------
        self.play(FadeOut(et_vueltas), FadeOut(puntos), run_time=0.3)
        rot.mostrar(pie_curso("En el salto %d el contador llega a cero: ese "
                              "router lo tira y avisa al origen."
                              % TTL_SALTOS),
                    zona="abajo", run_time=0.5)
        for s in (62, 63, 64):
            self.play(MoveAlongPath(p, ruta_de(
                topo, [TTL_RUTA[s - 2]["nodo"], TTL_RUTA[s - 1]["nodo"]])),
                Transform(cont, marcador(s)), run_time=0.45)
        self.play(p.animate.set_color(C_PERDIDA),
                  cont.animate.set_color(C_PERDIDA), run_time=0.3)
        self.play(p.animate.scale(1.8).set_opacity(0.0), run_time=0.6)
        self.remove(p)
        aviso = Arrow(topo.punto(TTL_NODO_FINAL), topo.punto("A"),
                      color=C_CAPA, stroke_width=3.0, buff=0.42,
                      max_tip_length_to_length_ratio=0.07)
        et_icmp = tag_hud("ICMP: tiempo excedido", font_size=20, color=C_CAPA)
        et_icmp.move_to(DOWN * 1.60)
        self.play(Create(aviso), run_time=0.8)
        self.play(FadeIn(et_icmp), run_time=0.4)
        et_cuenta = tag_hud("saltos hasta morir:  %d" % TTL_SALTOS,
                            font_size=22)
        et_cuenta.move_to(DOWN * 2.20)
        self.play(FadeIn(et_cuenta), run_time=0.5)
        self.wait(3.6)
