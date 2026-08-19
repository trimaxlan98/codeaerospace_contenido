class Clip1(Scene):
    """5.1.1 - Dos vectores son perpendiculares exactamente cuando su
    producto punto es cero: v gira hasta el angulo recto y la cifra baja
    a 0.0 con el. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Perpendicular es producto punto cero")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: los dos vectores y su angulo -------------------------
        pl = plano_leccion(vivo=False)
        u = vector(pl, U_PERP, color=C_VEC, nombre=r"\vec u")
        v = vector(pl, V_PERP_INICIAL, color=C_VEC_2, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos vectores cualesquiera forman un "
                              "ángulo. ¿Cuándo es de 90 grados exactos?"),
                    zona="abajo", run_time=0.5)
        self.play(GrowArrow(u.flecha), GrowArrow(v.flecha), run_time=0.9)
        self.play(FadeIn(u.etiqueta), FadeIn(v.etiqueta), run_time=0.3)
        ang = marca_angulo(pl, U_PERP, V_PERP_INICIAL, radio=0.7,
                           color=C_CALCULO)
        self.play(Create(ang.arco), FadeIn(ang.texto), run_time=0.7)
        self.wait(3.2)

        # --- momento: el producto punto en cifra ----------------------------
        rot.mostrar(pie_curso("El producto punto: multiplica componente a "
                              "componente y suma. Ahora mismo no es cero."),
                    zona="abajo", run_time=0.5)
        cifra_dot = tag_hud("u . v = " + fmt(DOT_PERP_INICIAL, 1),
                            font_size=20)
        panel = panel_derecha(cifra_dot)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        # --- momento: v gira hacia el angulo recto --------------------------
        movil = v
        movil_ang = ang
        movil_cifra = cifra_dot

        def girar(coords, dot_val, pie):
            nonlocal movil, movil_ang, movil_cifra
            rot.mostrar(pie_curso(pie), zona="abajo", run_time=0.5)
            destino = movil.con_coords(coords, nombre=r"\vec v")
            nuevo_ang = marca_angulo(pl, U_PERP, coords, radio=0.7,
                                     color=C_CALCULO)
            nueva_cifra = tag_hud("u . v = " + fmt(dot_val, 1), font_size=20)
            nueva_cifra.move_to(movil_cifra)
            self.play(Transform(movil, destino), Transform(movil_ang, nuevo_ang),
                      Transform(movil_cifra, nueva_cifra), run_time=1.3)
            self.wait(2.6)

        girar(V_PERP_PASO1, DOT_PERP_PASO1,
             "v gira. Cuanto más se acerca a los 90 grados, más chica la "
             "cifra.")
        girar(V_PERP_PASO2, DOT_PERP_PASO2,
             "Sigue girando: la cifra sigue bajando, en línea con el "
             "ángulo.")
        girar(V_PERP_FINAL, DOT_PERP_FINAL,
             "Y en el ángulo recto exacto, el producto punto se hace "
             "cero.")
        self.wait(1.6)

        # --- cierre del clip -------------------------------------------------
        rot.mostrar(pie_curso("Perpendicular no es una forma de hablar: "
                              "es que u . v = 0.0, ni más ni menos."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(movil_ang.texto, color=C_CALCULO, scale_factor=1.1),
                  Indicate(movil_cifra, color=C_CALCULO, scale_factor=1.1),
                  run_time=0.9)
        self.wait(3.8)
