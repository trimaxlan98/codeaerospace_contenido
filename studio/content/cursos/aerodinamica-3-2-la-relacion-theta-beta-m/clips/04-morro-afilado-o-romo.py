class Clip4(Scene):
    """3.2.4 - Implicaciones de diseño: bordes de ataque afilados vs. romos.

    El diagrama theta-beta-M se convierte aqui en una decision de ingenieria:
    afilado si quieres poca perdida, romo si lo que quieres es no derretirte.
    Y el criterio para elegir es el mismo numero — theta_max. Cierre de la
    leccion. (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Morro afilado o romo")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- afilado: onda pegada, poca perdida ----------------------------
        afilado = onda_oblicua(M_EJEMPLO, THETA_EJEMPLO, largo=2.3,
                               entrada=1.7)
        grupo_afilado = VGroup(afilado.pared, afilado.choque,
                               afilado.flujo_entrada)
        grupo_afilado.move_to(LEFT * 3.3 + UP * 0.45)
        datos_afilado = VGroup(
            Text("afilado", font_size=22, color=C_SUB),
            Text(f"p02/p01 = {DEBIL['p02/p01']:.4f}", font=FUENTE_HUD,
                 font_size=17, color=C_SUB)).arrange(DOWN, buff=0.14)
        datos_afilado.next_to(grupo_afilado, DOWN, buff=0.30)

        self.play(FadeIn(grupo_afilado), FadeIn(datos_afilado), run_time=0.9)
        rot.mostrar(pie_curso("Morro afilado: la onda se pega y es débil. "
                              "Casi no se pierde presión de estancamiento."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- romo: onda desprendida, mucha perdida -------------------------
        # El choque desprendido es NORMAL en el eje, asi que su perdida es la
        # del choque normal de M1: por eso se calcula con choque_normal.
        normal = choque_normal(M_EJEMPLO)
        morro = Arc(radius=0.62, start_angle=PI / 2, angle=PI, color=C_TENUE,
                    stroke_width=3.0).set_fill(C_EJE, opacity=0.45)
        cuerpo = Rectangle(width=1.4, height=1.24, stroke_width=3.0,
                           color=C_TENUE).set_fill(C_EJE, opacity=0.45)
        cuerpo.next_to(morro, RIGHT, buff=0)
        romo = VGroup(morro, cuerpo)
        arco = Arc(radius=1.05, start_angle=PI - 1.05, angle=2.10,
                   arc_center=romo.get_left() + RIGHT * 0.62,
                   color=C_SUPER, stroke_width=3.6)
        grupo_romo = VGroup(romo, arco)
        grupo_romo.move_to(RIGHT * 3.3 + UP * 0.45)
        datos_romo = VGroup(
            Text("romo", font_size=22, color=C_SUPER),
            Text(f"p02/p01 = {normal['p02/p01']:.4f}", font=FUENTE_HUD,
                 font_size=17, color=C_SUPER)).arrange(DOWN, buff=0.14)
        datos_romo.next_to(grupo_romo, DOWN, buff=0.30)

        self.play(FadeIn(grupo_romo), FadeIn(datos_romo), run_time=0.9)
        rot.mostrar(pie_curso("Morro romo: la onda se desprende y en el eje "
                              "es normal. Se pierde muchísimo más."),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso(f"Un {(1 - DEBIL['p02/p01']) * 100:.0f} % "
                              f"frente a un "
                              f"{(1 - normal['p02/p01']) * 100:.0f} %. "
                              "Parece obvio cuál elegir."), zona="abajo",
                    run_time=0.5)
        self.wait(5.2)

        rot.mostrar(pie_curso("Y sin embargo una cápsula de reentrada es "
                              "roma a propósito."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("Porque esa onda separada del cuerpo se lleva "
                              "el calor lejos del morro."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(grupo_afilado, datos_afilado, grupo_romo,
                                 datos_romo)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Afilado si quieres empuje.", font_size=36,
                         color=C_SUB),
            titulo_marca("Romo si quieres volver.", font_size=36,
                         color=C_SUPER)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
