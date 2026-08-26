class Clip3(Scene):
    """3.3.3 - Tres rutas al mismo prefijo: BGP mira la local-pref antes
    que la longitud del camino, asi que gana la que conviene y no la mas
    corta. Se cambia un numero y la decision cambia. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La politica decide")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: tres anuncios del mismo prefijo ---------------------
        rot.mostrar(pie_curso("%s aprende el mismo prefijo por tres vecinos "
                              "distintos." % DECIDE),
                    zona="abajo", run_time=0.5)
        mini = topologia(POS_DECISION, ARISTAS_DECISION, costos=False,
                         tam=0.44, fs=14)
        etiquetas_a(mini, ETIQ_DECISION)
        mini.nodo(DECIDE).forma.set_stroke(C_CIFRA, width=3.4)
        self.play(FadeIn(mini.enlaces), FadeIn(mini.nodos), run_time=0.8)
        et_pref = tag_hud("los tres anuncian  %s" % PREFIJO, font_size=19,
                          color=C_PAQUETE)
        et_pref.move_to(RIGHT * 0.6 + UP * 2.18)
        self.play(FadeIn(et_pref), run_time=0.4)
        tab = tabla(["Vecino", "AS-path", "Saltos", "Local-pref"],
                    list(FILAS_RUTAS), anchos=[1.5, 2.9, 1.2, 1.7],
                    alto=0.56, fs=19, resaltable=True)
        tab.move_to(RIGHT * 0.6 + UP * 0.55)
        self.play(FadeIn(tab), run_time=0.8)
        self.wait(4.2)

        # --- momento: lo que diria la distancia ---------------------------
        rot.mostrar(pie_curso("Si mandara la distancia ganaria %s: %d "
                              "saltos, el camino mas corto."
                              % (GANA_DISTANCIA, SALTOS_DISTANCIA)),
                    zona="abajo", run_time=0.5)
        self.play(Transform(tab, tab.con_filas(list(FILAS_RUTAS),
                                               resaltar=I_DISTANCIA)),
                  run_time=0.6)
        self.wait(4.4)

        # --- momento: la local-pref decide antes --------------------------
        rot.mostrar(pie_curso("Pero BGP mira antes la local-pref: cuanto le "
                              "conviene a %s cada ruta." % DECIDE),
                    zona="abajo", run_time=0.5)
        columna = VGroup(tab.textos[3], *[tab.celda(i, 3)
                                          for i in range(len(FILAS_RUTAS))])
        self.play(Indicate(columna, color=C_CIFRA, scale_factor=1.25),
                  run_time=1.0)
        self.play(Transform(tab, tab.con_filas(list(FILAS_RUTAS),
                                               resaltar=I_POLITICA)),
                  run_time=0.6)
        cifras = VGroup(
            tag_hud("%s es cliente de %s: esa ruta le da dinero"
                    % (GANA_POLITICA, DECIDE), font_size=20, color=C_CAPA),
            tag_hud("gana %s por %s" % (GANA_POLITICA,
                                        BGP_POLITICA["razon"]),
                    font_size=21),
            tag_hud("y es el camino MAS largo: %d saltos frente a %d"
                    % (SALTOS_POLITICA, SALTOS_DISTANCIA), font_size=20,
                    color=C_PAQUETE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(RIGHT * 0.6 + DOWN * 1.62)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.32), run_time=1.2)
        self.wait(4.6)

        # --- momento: se iguala la local-pref -----------------------------
        rot.mostrar(pie_curso("Cambia un numero, iguala las local-pref, y "
                              "la eleccion cambia sola."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifras), run_time=0.4)
        self.play(Transform(tab, tab.con_filas(list(FILAS_RUTAS_EMPATE),
                                               resaltar=I_DISTANCIA)),
                  run_time=0.9)
        cifras2 = VGroup(
            tag_hud("empate en local-pref: %d y %d"
                    % (LP_PAR, LP_PAR), font_size=20, color=C_CAPA),
            tag_hud("gana %s por %s" % (GANA_DISTANCIA,
                                        BGP_DISTANCIA["razon"]),
                    font_size=21),
            tag_hud("solo ahora cuenta la distancia: %d saltos"
                    % SALTOS_DISTANCIA, font_size=20, color=C_PAQUETE),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras2.move_to(RIGHT * 0.6 + DOWN * 1.62)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras2],
                              lag_ratio=0.32), run_time=1.2)
        self.wait(4.4)

        # --- momento: la moraleja -----------------------------------------
        rot.mostrar(pie_curso("La distancia solo decide cuando el interes "
                              "empata."),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
