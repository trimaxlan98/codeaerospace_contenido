class Clip1(Scene):
    """5.3.1 - ICMP no lleva datos: lleva noticias. Un TTL real llega a
    cero (ttl_camino), el router lo descarta y el ICMP de "tiempo
    excedido" incluye la cabecera del paquete culpable, para que el
    emisor sepa exactamente de cual se queja. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("ICMP: el protocolo que se queja")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: un paquete normal carga algo -------------------------
        rot.mostrar(pie_curso("Un paquete normal carga algo: una pagina, "
                              "un video, un archivo."),
                    zona="abajo", run_time=0.5)
        pn = paquete(DATOS_NORMALES, ancho=6.4, alto=0.85, fs=16,
                    color=C_PAQUETE)
        pn.move_to(UP * 1.15)
        self.play(FadeIn(pn), run_time=0.8)
        self.wait(3.2)

        # --- momento: ICMP no carga nada de eso ------------------------------
        rot.mostrar(pie_curso("ICMP no carga nada de eso: carga una "
                              "noticia sobre la red misma."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pn), run_time=0.4)
        pi = paquete(ICMP_CAMPOS, ancho=6.4, alto=0.85, fs=15, color=C_CAPA)
        pi.move_to(UP * 1.15)
        self.play(FadeIn(pi), run_time=0.8)
        self.wait(3.2)

        # --- momento: un TTL real que se agota --------------------------
        self.play(FadeOut(pi), run_time=0.4)
        rot.mostrar(pie_curso("Por ejemplo: un paquete sale con tres "
                              "saltos de vida."),
                    zona="abajo", run_time=0.5)
        topo = topologia(POS_TTL1, ARISTAS_TTL1, TIPOS_TTL1, costos=False,
                        tam=0.46, fs=15)
        topo.move_to(UP * 0.60)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        cont = tag_hud("TTL  03", font_size=26)
        cont.move_to(np.array([5.30, 1.80, 0.0]))
        p = ficha("", lado=0.30)
        p.move_to(topo.punto("origen"))
        self.add(p)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(1.4)

        # --- momento: baja salto a salto y muere en R3 -----------------------
        rot.mostrar(pie_curso("Baja uno por salto. En R3 llega a cero: "
                              "ese router lo descarta."),
                    zona="abajo", run_time=0.5)
        for i, r in enumerate(TTL_CAM["ruta"]):
            a, b = PATH_TTL[i], PATH_TTL[i + 1]
            self.play(MoveAlongPath(p, topo.camino([a, b])), run_time=0.7)
            nuevo = tag_hud("TTL  %02d" % r["ttl"], font_size=26)
            nuevo.move_to(cont.get_center())
            self.play(Transform(cont, nuevo), run_time=0.3)
        self.play(p.animate.set_color(C_PERDIDA),
                  cont.animate.set_color(C_PERDIDA), run_time=0.3)
        self.play(p.animate.scale(1.7).set_opacity(0.0), run_time=0.6)
        self.remove(p)
        aviso = Arrow(topo.punto("R3") + UP * 0.62,
                     topo.punto("origen") + UP * 0.62, color=C_CAPA,
                     stroke_width=3.0, buff=0.10,
                     max_tip_length_to_length_ratio=0.06)
        et_icmp = tag_hud("ICMP: tiempo excedido", font_size=20,
                          color=C_CAPA)
        et_icmp.move_to(DOWN * 1.85)
        self.play(Create(aviso), run_time=0.8)
        self.play(FadeIn(et_icmp), run_time=0.4)
        self.wait(2.6)

        # --- momento: la cabecera culpable viaja dentro ----------------------
        self.play(FadeOut(topo), FadeOut(cont), FadeOut(aviso),
                  FadeOut(et_icmp), run_time=0.5)
        rot.mostrar(pie_curso("Para que el emisor sepa de cual se queja, "
                              "el ICMP mete dentro la cabecera entera del "
                              "paquete culpable."),
                    zona="abajo", run_time=0.5)
        cab = cabecera(CAMPOS_IPV4, CULPABLE["valores"], ancho=CAB_ANCHO,
                      alto_fila=CAB_ALTO, fs=CAB_FS)
        cab.move_to(UP * 0.95)
        cab.iluminar("TTL", C_PERDIDA, rotulo=True)
        et_cab = tag_hud("el paquete que R3 acaba de tirar", font_size=18,
                         color=C_EJE)
        et_cab.next_to(cab, DOWN, buff=0.30)
        self.play(FadeIn(cab), run_time=1.0)
        self.play(FadeIn(et_cab), run_time=0.4)
        self.wait(4.0)

        # --- momento: los tres avisos de esta leccion -------------------
        self.play(FadeOut(cab), FadeOut(et_cab), run_time=0.4)
        rot.mostrar(pie_curso("Tres de esos avisos son los que vamos a "
                              "usar hoy."),
                    zona="abajo", run_time=0.5)
        filas_icmp = VGroup(*[
            tag_hud("tipo %-4s  %s" % (cod, texto), font_size=20,
                    color=C_CAPA)
            for cod, texto in LISTA_ICMP]).arrange(DOWN, buff=0.30,
                                                   aligned_edge=LEFT)
        filas_icmp.move_to(UP * 0.30)
        self.play(LaggedStart(*[FadeIn(f, shift=0.12 * UP)
                                for f in filas_icmp], lag_ratio=0.4),
                  run_time=1.4)
        self.wait(3.6)
