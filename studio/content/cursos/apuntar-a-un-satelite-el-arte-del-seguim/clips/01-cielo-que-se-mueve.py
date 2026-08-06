class Clip1(Scene):
    """1 - El cielo que no se queda quieto. Portada del curso ("Apuntar a
    un satelite" / "el arte del seguimiento"), HUD Modulo 01 y titulo.
    Sobre el mapa del mundo (imagen_mapa, alto 4.6) se dibuja la traza
    terrestre ambar de una orbita LEO inclinada (sinusoide de +-51°, dos
    periodos, generada aqui con numpy) y una estacion cian fija en CDMX
    (puntos_en_mapa). Un circulo verde translucido crece sobre la
    estacion (su huella de visibilidad) y un punto ambar recorre la
    traza completa con MoveAlongPath, virando a verde cuando cae dentro
    del circulo. Cierra con el pie gancho del curso. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)

        # --- momento: portada del curso -----------------------------------
        portada = VGroup(
            titulo_marca("Apuntar a un satélite", font_size=42),
            Text("el arte del seguimiento", font_size=24, color=C_ACENTO),
        ).arrange(DOWN, buff=0.26)
        portada.move_to(ORIGIN)

        self.play(Write(portada[0]), run_time=1.3)
        self.play(FadeIn(portada[1], shift=0.18 * UP), run_time=0.7)
        self.wait(2.0)

        modulo = hud_modulo("Modulo 01")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        self.play(FadeOut(portada, shift=0.5 * UP), run_time=0.7)

        titulo = titulo_curso("El cielo que no se queda quieto")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- momento: el escenario, mapa con traza y estacion --------------
        mapa = imagen_mapa(alto_escena=4.6)
        mapa.move_to(np.array([0.0, -0.15, 0.0]))

        n_muestras = 260
        t = np.linspace(0.0, 1.0, n_muestras)
        lon = -180.0 + 360.0 * t
        lat = 51.0 * np.sin(2.0 * (2.0 * np.pi) * t)      # 2 periodos
        lonlat = np.column_stack([lon, lat])
        traza = traza_terrestre(lonlat, mapa, color=C_SAT)
        traza_vm = traza[0]

        centro_estacion = puntos_en_mapa(mapa, [(-99.0, 19.0)])[0]
        estacion = Dot(centro_estacion, radius=0.075, color=C_ANTENA)

        escena_mapa = Group(mapa, traza, estacion)

        self.play(FadeIn(mapa), run_time=0.6)
        self.play(Create(traza), run_time=1.8)
        self.play(FadeIn(estacion, scale=0.5), run_time=0.4)

        # --- momento: la estacion fija, el satelite veloz -------------------
        rot.mostrar(pie_curso("Una estación fija. Un satélite a "
                              "27 000 km/h."), zona="abajo", run_time=0.45)
        self.wait(5.3)

        # --- momento: la huella de visibilidad -------------------------------
        radio_visibilidad = 0.75
        circulo = Circle(radius=radio_visibilidad, color=C_OK,
                         stroke_width=2.2)
        circulo.set_fill(color=C_OK, opacity=0.16)
        circulo.set_stroke(color=C_OK, opacity=0.65)
        circulo.move_to(centro_estacion)
        escena_mapa.add(circulo)

        self.play(GrowFromCenter(circulo), run_time=0.8)

        # --- momento: el satelite recorre la traza ---------------------------
        punto = Dot(traza_vm.get_start(), radius=0.075, color=C_SAT)
        escena_mapa.add(punto)

        def _color_por_proximidad(mob):
            d = float(np.linalg.norm(mob.get_center() - centro_estacion))
            mob.set_color(C_OK if d <= radio_visibilidad else C_SAT)

        self.play(FadeIn(punto, scale=0.6), run_time=0.35)
        rot.mostrar(pie_curso("Cruza tu cielo en diez minutos... si sabes "
                              "hacia dónde mirar."), zona="abajo",
                   run_time=0.45)
        punto.add_updater(_color_por_proximidad)
        self.play(MoveAlongPath(punto, traza_vm, rate_func=linear),
                  run_time=4.6)
        punto.remove_updater(_color_por_proximidad)
        _color_por_proximidad(punto)
        self.wait(1.3)

        # --- momento: la ventana pequeña donde se juega todo -------------------
        rot.mostrar(pie_curso("Todo el juego ocurre en esa pequeña "
                              "ventana."), zona="abajo", run_time=0.45)
        self.play(Indicate(circulo, scale_factor=1.12, color=C_OK),
                  run_time=1.0)
        self.wait(4.3)

        # --- momento: el gancho -----------------------------------------------
        rot.mostrar(pie_curso("Apuntar es resolver dónde, cuándo y a qué "
                              "velocidad."), zona="abajo", run_time=0.45)
        self.wait(5.6)
