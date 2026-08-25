class Clip2(Scene):
    """1.1.2 - Internet hace lo contrario: trocea el mensaje y rotula cada
    trozo con su destino. Van por donde pueden. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Trocear y rotular")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mensaje entero -----------------------------------
        rot.mostrar(pie_curso("Internet no reserva nada. Toma el mensaje "
                              "entero y lo parte."),
                    zona="abajo", run_time=0.5)
        bloque = Rectangle(width=6.4, height=0.90, stroke_color=C_PAQUETE,
                           stroke_width=2.6, fill_color=C_PAQUETE,
                           fill_opacity=0.16)
        bloque.move_to(UP * 1.15)
        et_bloque = tag_hud("mensaje: %s bytes" % f"{MSG_BYTES:,}".replace(
            ",", " "), font_size=20, color=C_PAQUETE)
        et_bloque.move_to(bloque.get_center())
        self.play(FadeIn(bloque), FadeIn(et_bloque), run_time=0.8)
        self.wait(4.6)

        # --- momento: los trozos con su rotulo ----------------------------
        rot.mostrar(pie_curso("Cada trozo lleva su propia direccion. "
                              "Nadie le guarda el sitio a nadie."),
                    zona="abajo", run_time=0.5)
        n = TROZO["paquetes"]
        trozos = VGroup()
        for i in range(n):
            c = Rectangle(width=0.62, height=0.62, stroke_color=C_PAQUETE,
                          stroke_width=2.0, fill_color=C_PAQUETE,
                          fill_opacity=0.14)
            d = tag_hud(str(i + 1), font_size=17, color=C_PAQUETE)
            d.move_to(c.get_center())
            trozos.add(VGroup(c, d))
        trozos.arrange(RIGHT, buff=0.16)
        trozos.move_to(UP * 1.15)
        self.play(FadeOut(et_bloque), run_time=0.3)
        self.play(ReplacementTransform(bloque, trozos), run_time=1.2)
        pk = paquete([("Cabecera IP", 1.0, "20 B"),
                      ("Cabecera TCP", 1.0, "20 B"),
                      ("Carga util", 3.2, "%d B" % TROZO["util_por_paquete"])],
                     ancho=6.0, alto=0.62)
        pk.move_to(DOWN * 0.55)
        guia = DashedLine(trozos[0].get_bottom() + DOWN * 0.06,
                          pk.campo("Cabecera IP").get_top() + UP * 0.30,
                          color=C_EJE, stroke_width=1.6)
        self.play(Create(guia), FadeIn(pk), run_time=1.0)
        self.wait(4.4)

        # --- momento: viajan por donde pueden -----------------------------
        rot.mostrar(pie_curso("Van por donde pueden: caminos distintos, "
                              "y llegan desordenados."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(pk), FadeOut(guia), FadeOut(trozos), run_time=0.6)
        topo = topologia(POS_RED, ARISTAS_RED, TIPOS_RED, costos=False)
        topo.scale(0.82).move_to(UP * 0.75)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=0.8)
        caminos = []
        for ruta in (CAMINO_ALTO, CAMINO_BAJO):
            v = VMobject()
            v.set_points_as_corners([topo.punto(k) for k in ruta])
            caminos.append(v)
        viajeros = VGroup(*[
            VGroup(Square(0.34, stroke_color=C_PAQUETE, stroke_width=2.0,
                          fill_color=C_PAQUETE, fill_opacity=0.20),
                   tag_hud(str(i + 1), font_size=14, color=C_PAQUETE))
            for i in range(4)])
        for v in viajeros:
            v[1].move_to(v[0].get_center())
            v.move_to(topo.punto("A"))
        self.add(viajeros)
        self.play(LaggedStart(*[
            MoveAlongPath(v, caminos[i % 2]) for i, v in enumerate(viajeros)],
            lag_ratio=0.28), run_time=3.0)
        self.play(FadeOut(viajeros), run_time=0.3)
        orden = VGroup(*[
            VGroup(Square(0.44, stroke_color=C_PAQUETE, stroke_width=2.0,
                          fill_color=C_PAQUETE, fill_opacity=0.12),
                   tag_hud(str(k), font_size=16, color=C_PAQUETE))
            for k in ORDEN_LLEGADA])
        for c in orden:
            c[1].move_to(c[0].get_center())
        orden.arrange(RIGHT, buff=0.14).move_to(DOWN * 1.75)
        et_orden = tag_hud("orden de llegada", font_size=17, color=C_EJE)
        et_orden.next_to(orden, UP, buff=0.20)
        self.play(FadeIn(et_orden),
                  LaggedStart(*[FadeIn(c, shift=0.15 * UP) for c in orden],
                              lag_ratio=0.16), run_time=1.6)
        self.wait(3.6)

        # --- momento: lo que cuesta rotular -------------------------------
        rot.mostrar(pie_curso("Rotular cuesta bytes. Barato si el paquete "
                              "va lleno; caro si va casi vacio."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(topo.enlaces), FadeOut(topo.nodos),
                  FadeOut(orden), FadeOut(et_orden), run_time=0.5)
        cifras = VGroup(
            tag_hud("%d paquetes de %d B utiles"
                    % (TROZO["paquetes"], TROZO["util_por_paquete"]),
                    font_size=21),
            tag_hud("cabeceras: %d B  ->  %s %% del cable"
                    % (TROZO["bytes_cabecera"],
                       fmt(TROZO["sobrecosto_pct"], 1)), font_size=21),
            tag_hud("un mensaje de 100 B  ->  %s %% del cable"
                    % fmt(TROZO_CHICO["sobrecosto_pct"], 1),
                    font_size=21, color=C_PERDIDA),
        ).arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        cifras.move_to(UP * 0.30)
        self.play(LaggedStart(*[FadeIn(c, shift=0.14 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.6)
        self.wait(5.0)
