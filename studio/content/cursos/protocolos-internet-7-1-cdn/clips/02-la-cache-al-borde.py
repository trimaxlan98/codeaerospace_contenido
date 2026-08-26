class Clip2(Scene):
    """7.1.2 - Guardar una copia cerca del usuario evita el viaje largo del
    clip anterior. La cache es finita: acierta segun la localidad de los
    pedidos y segun su propio tamano. No todo se puede guardar. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("La cache al borde")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la copia cerca frente al viaje largo ------------------
        rot.mostrar(pie_curso("Una CDN guarda una copia cerca del usuario: "
                              "si esta ahi, unos milisegundos; si no, hay "
                              "que ir hasta el origen."),
                    zona="abajo", run_time=0.5)
        usuario = nodo("host", "CDMX", 0.5)
        usuario.move_to(LEFT * 5.0 + UP * 0.2)
        pop = nodo("servidor", "PoP CDMX", 0.5)
        pop.move_to(LEFT * 1.6 + UP * 1.7)
        origen = nodo("servidor", "Madrid", 0.5)
        origen.move_to(RIGHT * 5.2 + UP * 0.2)
        cable_corto = enlace(usuario.centro(), pop.centro(), color=C_RED)
        cable_largo = enlace(usuario.centro(), origen.centro(), color=C_RED,
                             punteada=True)
        self.play(FadeIn(usuario), FadeIn(pop), FadeIn(origen), run_time=0.6)
        self.play(Create(cable_corto.linea), Create(cable_largo.linea),
                  run_time=1.0)
        self.wait(1.0)

        pedido = ficha("GET")
        pedido.move_to(cable_corto.a)
        self.play(FadeIn(pedido), run_time=0.2)
        self.play(MoveAlongPath(pedido, cable_corto.linea), run_time=0.5,
                  rate_func=linear)
        vuelta_corta = enlace(pop.centro(), usuario.centro())
        respuesta = ficha("200", color=C_OK)
        respuesta.move_to(vuelta_corta.a)
        self.play(FadeIn(respuesta), run_time=0.2)
        self.play(MoveAlongPath(respuesta, vuelta_corta.linea), run_time=0.5,
                  rate_func=linear)
        corto_ms = regla_viajes(1, etiqueta="PoP cercano", ms=RTT_BORDE)
        corto_ms.move_to(DOWN * 1.5)
        self.play(FadeIn(corto_ms), run_time=0.5)
        self.wait(1.0)

        pedido2 = ficha("GET")
        pedido2.move_to(cable_largo.a)
        self.play(FadeIn(pedido2), run_time=0.2)
        self.play(MoveAlongPath(pedido2, cable_largo.linea), run_time=1.0,
                  rate_func=linear)
        largo_ms = regla_viajes(1, etiqueta="ir hasta el origen (Madrid)",
                                ms=RTT_REAL_LARGO)
        largo_ms.move_to(DOWN * 2.3)
        self.play(FadeIn(largo_ms), run_time=0.5)
        self.wait(3.2)

        # --- momento: la cache es finita: localidad y tamano ----------------
        demo = VGroup(usuario, pop, origen, cable_corto, cable_largo, pedido,
                     respuesta, pedido2, corto_ms, largo_ms)
        self.play(FadeOut(demo), run_time=0.6)
        rot.mostrar(pie_curso("La cache es finita: acierta mas si los "
                              "pedidos se repiten, y si hay mas sitio "
                              "guardado."),
                    zona="abajo", run_time=0.5)
        curva = grafica(ACIERTO_DE_ZIPF, (0.3, 2.0), (0, 80), ancho=7.0,
                        alto=2.7, color=C_CIFRA, muestras=87,
                        etiqueta_x="localidad (zipf)", etiqueta_y="acierto %")
        curva.move_to(UP * 0.4)
        self.play(FadeIn(curva), run_time=1.0)
        marcas = VGroup()
        for z in (0.6, 1.1, 1.8):
            marcas.add(curva.vertical_en(z),
                      Dot(curva.punto_de(z), radius=0.06, color=C_CIFRA))
        cifras_zipf = VGroup(*[
            tag_hud("zipf %s -> %s%%" % (fmt(z, 1),
                                         fmt(CDN_ZIPF[z]["tasa_acierto"], 1)),
                    font_size=16, color=C_CIFRA)
            for z in (0.6, 1.1, 1.8)]).arrange(DOWN, buff=0.14,
                                              aligned_edge=LEFT)
        cifras_zipf.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.2),
                  FadeIn(cifras_zipf), run_time=1.2)
        self.wait(1.4)

        grupo_zipf = VGroup(curva, marcas, cifras_zipf)
        self.play(FadeOut(grupo_zipf), run_time=0.5)
        filas_cache = [[str(c), "%s%%" % fmt(CDN_CACHE[c]["tasa_acierto"], 1)]
                      for c in (4, 8, 20)]
        t = tabla(["objetos en cache", "acierto"], filas_cache,
                 anchos=[2.8, 1.7], alto=0.44, fs=16)
        t.move_to(UP * 0.2)
        self.play(FadeIn(t), run_time=0.8)
        self.wait(4.0)

        # --- momento: lo que si se cachea y lo que no -----------------------
        self.play(FadeOut(t), run_time=0.5)
        rot.mostrar(pie_curso("Y no todo se puede guardar: lo estatico si, "
                              "lo que cambia por usuario, no."),
                    zona="abajo", run_time=0.5)
        cacheable = tag_hud("%s%% SI se cachea: imagenes, video, JS estatico"
                            % fmt(CDN_CACHEABLE_PCT, 0), font_size=19,
                            color=C_OK)
        no_cacheable = tag_hud("%s%% siempre al origen: paginas dinamicas, "
                               "tu carrito" % fmt(CDN_NOCACHE_PCT, 0),
                               font_size=19, color=C_RED)
        grupo_final = VGroup(cacheable, no_cacheable).arrange(DOWN, buff=0.34)
        grupo_final.move_to(UP * 0.2)
        self.play(FadeIn(cacheable), run_time=0.5)
        self.play(FadeIn(no_cacheable), run_time=0.5)
        self.wait(5.5)
