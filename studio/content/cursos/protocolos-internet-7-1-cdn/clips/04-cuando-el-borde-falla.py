class Clip4(Scene):
    """7.1.4 - El PoP de Madrid cae; BGP re-enruta a los usuarios que
    dependian de el al siguiente sitio mas cercano. La latencia media sube
    un poco, pero nadie se queda sin servicio. Cierre de la leccion.
    (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Cuando el borde falla")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        def pos(c, dy=-0.3):
            x, y = POS_MUNDO[c]
            return np.array([x, y + dy, 0.0])

        # --- momento: el PoP de Madrid cae -----------------------------------
        rot.mostrar(pie_curso("El PoP de Madrid se cae. Su direccion sigue "
                              "anunciada desde los otros siete."),
                    zona="abajo", run_time=0.5)
        nodos = {}
        sitios = VGroup()
        for c in SITIOS_ANYCAST:
            n = nodo("servidor", c, 0.42, fs=12)
            n.move_to(pos(c))
            nodos[c] = n
            sitios.add(n)
        londres = nodo("host", "Londres", 0.42, fs=12)
        londres.move_to(pos("Londres"))
        self.play(LaggedStart(*[FadeIn(n) for n in sitios], lag_ratio=0.1),
                  FadeIn(londres), run_time=1.2)
        self.wait(1.0)
        cruz = tag_hud("X", font_size=30, color=C_PERDIDA)
        cruz.move_to(nodos["Madrid"].centro() + UP * 0.55)
        self.play(FadeIn(cruz, scale=1.6),
                  nodos["Madrid"].forma.animate.set_stroke(C_PERDIDA,
                                                          width=3.0),
                  run_time=0.6)
        self.wait(3.0)

        # --- momento: BGP re-enruta -------------------------------------------
        rot.mostrar(pie_curso("BGP deja de anunciar esa ruta: los usuarios "
                              "que caian ahi van al siguiente sitio mas "
                              "cercano."),
                    zona="abajo", run_time=0.5)
        ruta_madrid = enlace(nodos["Madrid"].centro(), nodos["Lagos"].centro(),
                             color=C_COLA, punteada=True)
        ruta_londres = enlace(londres.centro(), nodos["Lagos"].centro(),
                              color=C_COLA, punteada=True)
        self.play(Create(ruta_madrid.linea), Create(ruta_londres.linea),
                  run_time=0.8)
        paq_m = ficha("GET", lado=0.28, color=C_COLA)
        paq_m.move_to(ruta_madrid.a)
        paq_l = ficha("GET", lado=0.28, color=C_COLA)
        paq_l.move_to(ruta_londres.a)
        self.play(MoveAlongPath(paq_m, ruta_madrid.linea),
                  MoveAlongPath(paq_l, ruta_londres.linea), run_time=0.8,
                  rate_func=linear)
        et_re = tag_hud("%d usuarios re-enrutados a Lagos"
                        % ANYCAST_CAIDA["n_movidos"], font_size=19,
                        color=C_COLA)
        et_re.to_edge(DOWN, buff=1.55)
        self.play(FadeIn(et_re), run_time=0.4)
        self.wait(3.6)

        # --- momento: sube la latencia, nadie se queda sin servicio -----------
        mapa = VGroup(sitios, londres, cruz, ruta_madrid, ruta_londres,
                     paq_m, paq_l, et_re)
        self.play(FadeOut(mapa), run_time=0.6)
        rot.mostrar(pie_curso("La latencia media sube un poco. Nadie se "
                              "queda sin servicio."),
                    zona="abajo", run_time=0.5)
        barra_antes = regla_viajes(1, etiqueta="antes de la caida",
                                   ms=ANYCAST_8["media_ms"])
        barra_antes.move_to(UP * 0.7)
        barra_despues = regla_viajes(1, etiqueta="con Madrid caido",
                                     ms=ANYCAST_CAIDA["despues"]["media_ms"])
        barra_despues.move_to(DOWN * 0.2)
        self.play(FadeIn(barra_antes), run_time=0.5)
        self.wait(0.8)
        self.play(FadeIn(barra_despues), run_time=0.5)
        subida = tag_hud("+%s ms de media"
                         % fmt(ANYCAST_CAIDA["subida_ms"], 1), font_size=19,
                         color=C_CIFRA)
        subida.move_to(DOWN * 1.15)
        sin_servicio = tag_hud("%d usuarios sin servicio"
                               % ANYCAST_CAIDA["sin_servicio"], font_size=19,
                               color=C_OK)
        sin_servicio.move_to(DOWN * 1.75)
        self.play(FadeIn(subida), run_time=0.4)
        self.play(FadeIn(sin_servicio), run_time=0.4)
        self.wait(4.0)

        # --- cierre de la leccion ----------------------------------------------
        cierre_leccion(
            self, rot,
            "No puedes hacer la luz mas rapida.",
            "Puedes poner la respuesta mas cerca.",
            "Siguiente: colas, latencia y bufferbloat.",
            barra_antes, barra_despues, subida, sin_servicio, espera=5.5)
