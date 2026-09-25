class Clip4(Scene):
    """4.2.4 - El arreglo: el parametro del procedimiento pasa de NVARCHAR a
    VARCHAR (el tipo de la columna). Dos paneles gemelos, cambia solo el
    tipo (resaltado en sus glifos). Cierre de la leccion. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El arreglo"), zona="arriba", run_time=0.6)
        self.wait(0.5)

        linea_antes = "  @email NVARCHAR(120)"
        linea_despues = "  @email VARCHAR(120)"
        cabecera = "CREATE PROCEDURE buscar_cliente"

        q1 = S.codigo([cabecera, linea_antes], font_size=19)
        q1.move_to(LEFT * 3.35 + UP * 0.2)
        i, j = pos_sin_espacios(linea_antes, "NVARCHAR")
        q1.lineas[1][i:j].set_color(C_MALO)
        et1 = tag_junto(q1, "antes", UP, buff=0.24, color=C_MALO)
        self.play(FadeIn(q1, shift=RIGHT * 0.2), run_time=0.7)
        self.play(FadeIn(et1), run_time=0.4)
        self.wait(1.8)

        q2 = S.codigo([cabecera, linea_despues], font_size=19)
        q2.move_to(RIGHT * 3.35 + UP * 0.2)
        i2, j2 = pos_sin_espacios(linea_despues, "VARCHAR")
        q2.lineas[1][i2:j2].set_color(C_BUENO)
        et2 = tag_junto(q2, "despues", UP, buff=0.24, color=C_BUENO)
        self.play(FadeIn(q2, shift=LEFT * 0.2), run_time=0.7)
        self.play(FadeIn(et2), run_time=0.4)
        self.wait(1.2)

        n1 = q1.lineas[1][i:j]
        n2 = q2.lineas[1][i2:j2]
        self.play(Indicate(n1, color=C_MALO, scale_factor=1.15),
                  Indicate(n2, color=C_BUENO, scale_factor=1.15), run_time=1.0)
        et_solo = tag_junto(VGroup(q1, q2), "cambia solo el tipo", DOWN,
                            buff=0.4)
        self.play(FadeIn(et_solo), run_time=0.4)
        self.wait(2.2)

        self.play(FadeOut(et_solo), run_time=0.3)
        rot.mostrar(motor_pie(lecturas(EMAIL_V)), zona="abajo", run_time=0.5)
        self.wait(9.0)

        cierre_leccion(self, rot, "El tipo del parametro",
                       "es el tipo de la columna.",
                       q1, et1, q2, et2, espera=6.5)
