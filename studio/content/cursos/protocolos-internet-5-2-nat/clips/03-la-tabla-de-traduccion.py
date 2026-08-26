class Clip3(Scene):
    """5.2.3 - La tabla de traduccion: nat_traducir() reescribe origen Y
    puerto, y anota la fila. Dos aparatos piden el mismo puerto de origen
    (51000): el router los renumera a 40000 y 40001. Y al volver, la
    traduccion se deshace. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La tabla de traduccion")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        ANCHOS_TAB = [1.5, 2.3, 1.7, 3.0, 1.5]
        CABS_TAB = ["Aparato", "IP privada", "Pto origen", "Destino",
                   "Pto NAT"]

        # --- momento: el primer paquete sale ------------------------------
        rot.mostrar(pie_curso("La laptop manda un paquete a un sitio web "
                              "con puerto de origen 51000."),
                    zona="abajo", run_time=0.5)
        f0 = FILAS_NAT[0]
        paq = paquete([("Origen", 1.4, "%s:%s" % (f0[1], f0[2])),
                      ("Destino", 1.4, f0[3])], ancho=7.2, alto=0.85,
                     fs=16)
        paq.move_to(UP * 2.1)
        self.play(FadeIn(paq, shift=0.2 * DOWN), run_time=0.8)
        self.wait(2.8)

        # --- momento: el router reescribe origen Y puerto -------------------
        rot.mostrar(pie_curso("El router reescribe el origen: la IP "
                              "privada desaparece, aparece la publica "
                              "con un puerto nuevo.", font_size=22),
                    zona="abajo", run_time=0.5)
        paq.iluminar("Origen")
        nuevo = paq.con_valores({"Origen": "%s:%s" % (NAT_IP_PUBLICA,
                                                       f0[4])})
        self.play(Transform(paq, nuevo), run_time=0.9)
        tab = tabla(CABS_TAB, [f0], anchos=ANCHOS_TAB, alto=0.50, fs=15,
                   filas_max=3, resaltable=True, resaltar=0)
        tab.move_to(DOWN * 0.55)
        self.play(FadeIn(tab), run_time=0.6)
        self.wait(2.6)

        # --- momento: otro aparato pide el MISMO puerto ---------------------
        rot.mostrar(pie_curso("Otro aparato pide el mismo puerto de "
                              "origen, 51000. El router ya lo tiene "
                              "anotado.", font_size=22),
                    zona="abajo", run_time=0.5)
        f1 = FILAS_NAT[1]
        paq2 = paquete([("Origen", 1.4, "%s:%s" % (f1[1], f1[2])),
                       ("Destino", 1.4, f1[3])], ancho=7.2, alto=0.85,
                      fs=16)
        paq2.move_to(UP * 2.1)
        self.play(FadeOut(paq), run_time=0.4)
        self.play(FadeIn(paq2, shift=0.2 * DOWN), run_time=0.7)
        paq2.iluminar("Origen", color=C_PERDIDA)
        self.play(Indicate(paq2.valor("Origen"), color=C_PERDIDA,
                           scale_factor=1.15), run_time=0.8)
        self.wait(1.6)

        rot.mostrar(pie_curso("Lo renumera: el segundo sale por el "
                              "puerto publico 40001, no por el 40000.",
                              font_size=22),
                    zona="abajo", run_time=0.5)
        nuevo2 = paq2.con_valores({"Origen": "%s:%s" % (NAT_IP_PUBLICA,
                                                        f1[4])})
        nuevo2.iluminar("Origen", color=C_CIFRA)
        self.play(Transform(paq2, nuevo2), run_time=0.9)
        fila01 = tab.con_filas([f0, f1], resaltar=1)
        self.play(Transform(tab, fila01), run_time=0.5)
        et_renum = tag_hud("mismo puerto de origen  ->  renumerados: %d"
                           % RENUMERADOS, font_size=19, color=C_CIFRA)
        et_renum.next_to(tab, DOWN, buff=0.35)
        self.play(FadeIn(et_renum), run_time=0.4)
        self.wait(3.2)

        # --- momento: la tercera sesion completa la tabla -----------------
        rot.mostrar(pie_curso("Un tercer aparato abre otra sesion: la "
                              "tabla ya tiene tres filas, tres puertos "
                              "distintos.", font_size=22),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(paq2), FadeOut(et_renum), run_time=0.4)
        fila012 = tab.con_filas(FILAS_NAT, resaltar=2)
        self.play(Transform(tab, fila012), run_time=0.6)
        et_usados = tag_hud("puertos usados: %d" % PUERTOS_USADOS,
                            font_size=19, color=C_CIFRA)
        et_usados.next_to(tab, DOWN, buff=0.35)
        self.play(FadeIn(et_usados), run_time=0.4)
        self.wait(3.0)

        # --- momento: la respuesta vuelve, y la traduccion se deshace -------
        rot.mostrar(pie_curso("Cuando la respuesta vuelve al puerto "
                              "publico 40000, el router deshace la "
                              "traduccion.", font_size=22),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_usados), run_time=0.3)
        fila_final = tab.con_filas(FILAS_NAT, resaltar=0)
        self.play(Transform(tab, fila_final), run_time=0.5)
        vuelta = paquete([("Origen", 1.4, "%s:443" % f0[3].split(":")[0]),
                         ("Destino", 1.4, "%s:%s" % (NAT_IP_PUBLICA,
                                                     f0[4]))],
                        ancho=7.2, alto=0.85, fs=16, color=C_OK)
        vuelta.move_to(UP * 2.1)
        self.play(FadeIn(vuelta, shift=0.2 * UP), run_time=0.7)
        self.wait(1.6)
        vuelta.iluminar("Destino", color=C_OK)
        entregada = vuelta.con_valores(
            {"Destino": "%s:%s" % (f0[1], f0[2])}, color=C_OK)
        entregada.iluminar("Destino", color=C_OK)
        self.play(Transform(vuelta, entregada), run_time=0.9)
        self.wait(3.6)
