class Clip3(Scene):
    """6.1.3 - Teorema de Euler: en el giro compuesto hay UNA direccion que
    no se mueve, el vector propio de valor 1. El abanico gira a su
    alrededor. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El eje que no se mueve")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # unidad 0.62 (frente a 0.8 en el clip 2): aqui el giro se aplica
        # DOS veces y bajo R^2 la esquina del suelo vivo sube a 4.24
        # unidades de espacio (medido sobre la proyeccion); con 0.8 la punta
        # de arriba se come el titulo.
        esp = espacio3(unidad=0.62, alcance=3)
        esp.move_to(LEFT * 1.15 + UP * 0.18)
        esp.suelo.set_stroke(opacity=0.95)
        self.play(FadeIn(esp), run_time=0.9)
        rot.mostrar(pie_curso("El mismo giro del clip anterior. Y tres "
                              "flechas cualesquiera."), zona="abajo",
                    run_time=0.5)
        # El abanico vive en el plano perpendicular al eje: al girar resbala
        # sobre ese plano y se ve que da vueltas ALREDEDOR de la fucsia.
        aban = [vector3(esp, v, color=C_VEC, grosor=3.6) for v in ABANICO]
        self.play(*[GrowArrow(a.flecha) for a in aban], run_time=0.9)
        self.wait(3.2)

        # --- momento: la flecha fucsia --------------------------------------
        rot.mostrar(pie_curso("Y una más, en fucsia. Esta no es una flecha "
                              "cualquiera."), zona="abajo", run_time=0.5)
        eje = vector3(esp, EJE_COMP * LARGO_EJE, color=C_PROPIO,
                      nombre=r"\vec e", grosor=5.0)
        self.play(GrowArrow(eje.flecha), run_time=0.8)
        self.play(FadeIn(eje.etiqueta), run_time=0.3)
        self.wait(3.6)

        # --- momento: el giro ------------------------------------------------
        rot.mostrar(pie_curso("Giramos. Las tres rojas se mueven; el suelo "
                              "también. Mira la fucsia."), zona="abajo",
                    run_time=0.5)
        self.wait(0.4)
        self.play(*esp.anim_matriz(R_COMP, eje, *aban), run_time=2.4)
        self.wait(2.6)

        # --- momento: R e = e -------------------------------------------------
        rot.mostrar(pie_curso("No se ha movido ni un pelo. R por ella da "
                              "ella misma: es un vector propio de valor uno."),
                    zona="abajo", run_time=0.5)
        et_eje = tag_hud("eje de giro", font_size=17, color=C_PROPIO)
        col_eje = vector_columna(EJE_COMP, color=C_PROPIO, dec=DEC_EJE,
                                 font_size=26)
        t_desvio = tag_hud("|R e - e| = " + fmt(DESVIO_EJE, 2), font_size=17)
        t_ang = tag_hud("angulo = " + fmt(ANG_COMP, 1) + " grados",
                        font_size=17)
        panel = panel_derecha(et_eje, col_eje, t_desvio, t_ang, buff=0.2)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        rot.mostrar(formula_pie(r"R\,\vec e = \vec e", color=C_PROPIO),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(eje, color=C_PROPIO, scale_factor=1.06),
                  run_time=0.8)
        self.wait(3.8)

        # --- momento: otra vez ------------------------------------------------
        rot.mostrar(pie_curso("Repite el giro y sigue clavada. Eso es un "
                              "eje: la dirección que el giro respeta."),
                    zona="abajo", run_time=0.5)
        self.wait(0.3)
        # anim_matriz es el estado TOTAL: dos giros seguidos son R @ R.
        self.play(*esp.anim_matriz(R_COMP @ R_COMP, eje, *aban), run_time=2.2)
        self.wait(2.4)

        rot.mostrar(pie_curso("Euler lo demostró para todas: toda rotación "
                              "en 3D tiene un eje y un ángulo."),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)
