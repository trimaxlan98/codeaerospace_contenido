class Clip2(Scene):
    """3.3.2 - Un anuncio de prefijo viaja y cada AS se anade al camino:
    el AS-path crece a la vista y el bucle se detecta solo, porque un AS
    acaba viendo su propio numero. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Camino de vectores")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        topo = topologia(POS_ANILLO, ARISTAS_ANILLO, {"AS700": "servidor"},
                         costos=False, tam=0.46, fs=14)
        etiquetas_a(topo, ETIQ_ANILLO)

        # --- momento: quien es el dueno del prefijo -----------------------
        rot.mostrar(pie_curso("%s es el dueno de un prefijo y se lo cuenta "
                              "a sus vecinos." % ANILLO[0]),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(topo.enlaces), FadeIn(topo.nodos), run_time=1.0)
        et_pref = tag_hud(PREFIJO, font_size=19, color=C_PAQUETE)
        et_pref.move_to(topo.punto(ANILLO[0]) + DOWN * 0.98)
        self.play(FadeIn(et_pref),
                  topo.nodo(ANILLO[0]).forma.animate.set_stroke(
                      C_PAQUETE, width=3.4), run_time=0.5)
        self.wait(3.6)

        # --- momento: el camino se escribe salto a salto ------------------
        rot.mostrar(pie_curso("Cada AS que reenvia el anuncio se anade al "
                              "principio del camino."),
                    zona="abajo", run_time=0.5)
        tab = tabla(["AS que recibe", "AS-path que ve"],
                    [FILAS_ANUNCIO[0]], anchos=[2.2, 3.4], alto=0.48,
                    fs=17, filas_max=len(FILAS_ANUNCIO), resaltable=True)
        tab.move_to(RIGHT * 2.9 + DOWN * 0.35)
        self.play(FadeIn(tab), run_time=0.7)

        tok = ficha("UPD", lado=0.62, fs=15)
        tok.move_to(tramo(topo, ANILLO[0], ANILLO[1]).get_start())
        self.play(FadeIn(tok, scale=1.3), run_time=0.4)

        def _hasta(i):
            """Trayecto CONTINUO: de donde esta la ficha al siguiente AS.
            Encadenar `tramo` a secas la teletransporta en cada relevo."""
            v = VMobject()
            v.set_points_as_corners([
                tok.get_center(),
                tramo(topo, ANILLO[i - 1], ANILLO[i], 0.0, 0.66).get_end()])
            return v

        def _salto(i, run=0.95):
            """El anuncio cruza al AS i-esimo y la tabla gana una fila."""
            self.play(MoveAlongPath(tok, _hasta(i)), run_time=run)
            nueva = tab.con_filas(list(FILAS_ANUNCIO[:i]))
            self.play(Transform(tab, nueva),
                      topo.nodo(ANILLO[i]).forma.animate.set_stroke(
                          C_OK, width=3.2), run_time=0.42)

        for i in (1, 2, 3):
            _salto(i)
        self.wait(2.2)

        # --- momento: el vector es el camino entero -----------------------
        rot.mostrar(pie_curso("No es una distancia: es la lista completa de "
                              "por donde ha pasado."),
                    zona="abajo", run_time=0.5)
        _salto(4)
        self.wait(3.8)

        # --- momento: el anuncio vuelve al origen -------------------------
        rot.mostrar(pie_curso("%s recibe su propio anuncio de vuelta, con "
                              "cuatro numeros delante." % ANILLO[0]),
                    zona="abajo", run_time=0.5)
        self.play(MoveAlongPath(tok, _hasta(5)), run_time=0.95)
        nueva = tab.con_filas(list(FILAS_ANUNCIO), resaltar=FILA_BUCLE)
        self.play(Transform(tab, nueva), run_time=0.45)
        self.wait(4.0)

        # --- momento: se ve a si mismo y descarta -------------------------
        rot.mostrar(pie_curso("Ve su propio numero en el camino: eso es un "
                              "bucle, y lo descarta."),
                    zona="abajo", run_time=0.5)
        celda = tab.celda(FILA_BUCLE, 1)
        propio = Rectangle(width=0.56, height=0.36, color=C_PERDIDA,
                           stroke_width=2.8)
        propio.move_to(celda.get_right() + LEFT * 0.22)
        tacha = Line(tab.fila(FILA_BUCLE).get_left() + LEFT * 0.14,
                     tab.fila(FILA_BUCLE).get_right() + RIGHT * 0.14,
                     color=C_PERDIDA, stroke_width=3.0)
        tacha.move_to(tab.fila(FILA_BUCLE).get_center())
        self.play(FadeIn(propio, scale=1.6), run_time=0.5)
        self.play(Indicate(propio, color=C_PERDIDA, scale_factor=1.35),
                  run_time=0.7)
        self.play(FadeIn(tacha), FadeOut(tok), run_time=0.5)
        et_regla = tag_hud("BGP evita bucles sin conocer el mapa: "
                           "le basta leer el camino", font_size=19,
                           color=C_CIFRA)
        et_regla.move_to(DOWN * 2.62)
        self.play(FadeIn(et_regla), run_time=0.5)
        self.wait(4.2)
