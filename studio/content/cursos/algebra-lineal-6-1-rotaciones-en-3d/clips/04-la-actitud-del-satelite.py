class Clip4(Scene):
    """6.1.4 - La actitud de un satelite es una matriz, y para pasar de una
    a otra basta UN giro alrededor del eje de Euler. Cierra la
    leccion. (~41 s)"""

    def _satelite(self, esp, R):
        """El cubesat con actitud R, SIN su `.eje_z` rojo: la actitud se lee
        con la triada (satelite3 solo trae ese eje, y en rojo choca con el
        codigo de colores de las columnas)."""
        sat = satelite3(esp, R, tam=1.0, color_panel=CODE_MUTED)
        sat.remove(sat.eje_z)
        return sat

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("La actitud del satélite")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el cubesat alineado ------------------------------------
        # unidad 0.75 y el espacio corrido a la izquierda: durante el giro el
        # suelo vivo llega a +-4.24 unidades de ancho (medido sobre la
        # proyeccion) y con 0.9 se metia bajo el panel de cifras.
        esp = espacio3(unidad=0.75, alcance=3)
        esp.move_to(LEFT * 1.5 + UP * 0.1)
        esp.suelo.set_stroke(opacity=0.95)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("Un cubesat. Su actitud es esto: hacia dónde "
                              "apunta cada uno de sus tres ejes."),
                    zona="abajo", run_time=0.5)
        sat = self._satelite(esp, np.eye(3))
        tri = triada3(esp, np.eye(3), largo=LARGO_TRIADA)
        self.play(FadeIn(sat), run_time=0.7)
        self.play(*[GrowArrow(e.flecha) for e in tri.ejes], run_time=0.7)
        self.wait(2.8)

        # --- momento: la actitud A -------------------------------------------
        rot.mostrar(pie_curso("Lo llevamos a la actitud A: "
                              + fmt(GUINADA_A, 0) + " de guiñada y "
                              + fmt(ALABEO_A, 0) + " de alabeo."),
                    zona="abajo", run_time=0.5)
        self.wait(0.3)
        self.play(Transform(sat, self._satelite(esp, R_A)),
                  *esp.anim_matriz(R_A, *tri.ejes), run_time=1.8)
        self.wait(2.8)

        # --- momento: la actitud B (fantasma) ---------------------------------
        rot.mostrar(pie_curso("Y tiene que quedar así: la tríada apagada es "
                              "la actitud B."), zona="abajo", run_time=0.5)
        # El fantasma se dibuja un 18% mas largo que la triada viva: al
        # aterrizar, sus puntas apagadas asoman por delante de las flechas
        # solidas y se VE que han caido en la misma direccion (si midieran
        # lo mismo, quedaria tapado y no se sabria si llego o no).
        fantasma = triada3(esp, R_B, largo=LARGO_TRIADA * 1.18, grosor=2.6)
        fantasma.set_opacity(0.55)
        self.play(FadeIn(fantasma), run_time=0.8)
        self.wait(3.4)

        # --- momento: el eje del giro ------------------------------------------
        rot.mostrar(pie_curso("De A a B hay infinitos caminos. Pero un solo "
                              "giro basta, y su eje sale de la cuenta."),
                    zona="abajo", run_time=0.5)
        # Sin etiqueta: la punta del eje aterriza justo sobre la "y" que
        # espacio3 clava al final de su eje cian (y que no se puede mover
        # desde fuera). Quien nombra la flecha es la cabecera fucsia del
        # panel.
        eje = vector3(esp, EJE_AB * LARGO_EJE_AB, color=C_PROPIO, grosor=5.0)
        et_eje = tag_hud("eje de la maniobra", font_size=17, color=C_PROPIO)
        col_eje = vector_columna(EJE_AB, color=C_PROPIO, dec=DEC_EJE,
                                 font_size=26)
        t_ang = tag_hud("angulo = " + fmt(ANG_AB, 1) + " grados", font_size=17)
        t_err = tag_hud("error A -> B = " + fmt(DESVIO_AB, 2), font_size=17)
        panel = panel_derecha(et_eje, col_eje, t_ang, t_err, buff=0.2)
        self.play(GrowArrow(eje.flecha), run_time=0.8)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        # --- momento: la maniobra, en un solo giro -----------------------------
        rot.mostrar(pie_curso("Un giro de " + fmt(ANG_AB, 1) + " grados "
                              "alrededor de esa flecha. Uno solo."),
                    zona="abajo", run_time=0.5)
        self.wait(0.4)
        # El giro se reparte en PASOS_AB tramos: cada tramo es el estado
        # TOTAL rot3_eje(eje, t*angulo) @ R_A, no un incremento.
        for k in range(1, PASOS_AB + 1):
            R_k = rot3_eje(EJE_AB, (k / PASOS_AB) * ANG_AB) @ R_A
            self.play(Transform(sat, self._satelite(esp, R_k)),
                      *esp.anim_matriz(R_k, *tri.ejes),
                      run_time=3.0 / PASOS_AB, rate_func=linear)
        self.wait(2.2)

        # --- momento: ha aterrizado en B ---------------------------------------
        rot.mostrar(pie_curso("Ha caído justo encima de B. Un eje y un "
                              "ángulo: eso era toda la maniobra."),
                    zona="abajo", run_time=0.5)
        self.play(*[Indicate(tri.ejes[j], color=c, scale_factor=1.08)
                    for j, c in enumerate((C_I, C_J, C_K))], run_time=0.9)
        self.wait(3.2)

        # --- cierre de la leccion ---------------------------------------------
        cierre_leccion(self, rot, "Toda rotación tiene un eje.",
                       "La actitud es un eje y un ángulo.",
                       "¿Y si el vector no fuera una flecha, sino una "
                       "función entera? Siguiente lección.",
                       esp, sat, tri, fantasma, eje, panel)
