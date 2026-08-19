class Clip4(Scene):
    """2.2.4 - En 3D pasa lo mismo: alabear y luego cabecear no es lo
    mismo que cabecear y luego alabear. Cierra la lección. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Girar un satélite")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: dos espacios identicos, lado a lado -------------------
        esp_izq = espacio3(unidad=0.62, alcance=3)
        esp_izq.move_to(LEFT * 3.5 + CENTRO_PLANO)
        esp_der = espacio3(unidad=0.62, alcance=3)
        esp_der.move_to(RIGHT * 3.5 + CENTRO_PLANO)
        sat_izq = satelite3(esp_izq, R=np.eye(3), tam=0.8)
        sat_der = satelite3(esp_der, R=np.eye(3), tam=0.8)
        et_izq = tag_hud("alabeo, luego cabeceo", font_size=16)
        et_izq.move_to(LEFT * 3.5 + UP * 2.7)
        et_der = tag_hud("cabeceo, luego alabeo", font_size=16)
        et_der.move_to(RIGHT * 3.5 + UP * 2.7)
        self.play(FadeIn(esp_izq), FadeIn(esp_der), FadeIn(sat_izq),
                  FadeIn(sat_der), FadeIn(et_izq), FadeIn(et_der),
                  run_time=0.9)
        rot.mostrar(pie_curso("Un satélite en 3D. Dos giros, dos "
                              "órdenes distintos."), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        # --- momento: izquierda, alabeo y luego cabeceo ---------------------
        rot.mostrar(pie_curso("Izquierda: alabeo (eje x) y luego "
                              "cabeceo (eje y)."), zona="abajo",
                    run_time=0.5)
        self.wait(0.6)
        nuevo_izq_1 = satelite3(esp_izq, R=R_ALABEO, tam=0.8)
        self.play(*esp_izq.anim_matriz(R_ALABEO),
                  Transform(sat_izq, nuevo_izq_1), run_time=1.8)
        self.wait(2.4)
        nuevo_izq_2 = satelite3(esp_izq, R=R_AC, tam=0.8)
        self.play(*esp_izq.anim_matriz(R_AC),
                  Transform(sat_izq, nuevo_izq_2), run_time=1.8)
        self.wait(3.0)

        # --- momento: derecha, cabeceo y luego alabeo ------------------------
        rot.mostrar(pie_curso("Derecha: cabeceo primero, alabeo "
                              "después. Los mismos giros, otro orden."),
                    zona="abajo", run_time=0.5)
        self.wait(0.6)
        nuevo_der_1 = satelite3(esp_der, R=R_CABECEO, tam=0.8)
        self.play(*esp_der.anim_matriz(R_CABECEO),
                  Transform(sat_der, nuevo_der_1), run_time=1.8)
        self.wait(2.4)
        nuevo_der_2 = satelite3(esp_der, R=R_CA, tam=0.8)
        self.play(*esp_der.anim_matriz(R_CA),
                  Transform(sat_der, nuevo_der_2), run_time=1.8)
        self.wait(3.2)

        # --- momento: dos actitudes distintas -------------------------------
        rot.mostrar(pie_curso("Las dos actitudes finales son distintas: "
                              "mismos giros, otro orden, otro "
                              "satélite."), zona="abajo", run_time=0.5)
        self.play(Indicate(sat_izq.eje_z, color=C_VEC, scale_factor=1.15),
                  Indicate(sat_der.eje_z, color=C_VEC, scale_factor=1.15),
                  run_time=1.0)
        self.wait(3.4)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(self, rot, "Componer es multiplicar.",
                       "Y el orden se nota.",
                       "Y cuando compones, ¿qué le pasa al área? La "
                       "siguiente lección lo mide.",
                       esp_izq, esp_der, sat_izq, sat_der, et_izq, et_der)
