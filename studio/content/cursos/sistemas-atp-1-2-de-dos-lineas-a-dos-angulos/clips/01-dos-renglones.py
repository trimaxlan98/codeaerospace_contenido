class Clip1(Scene):
    """1.2.1 - El TLE no es magia: dos renglones de 69 caracteres con
    campos de columna fija. Se encienden uno a uno hasta llegar al
    movimiento medio, la puerta a la leccion siguiente. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Dos renglones de 69 caracteres"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        tarjeta = tarjeta_tle(font_size=17)
        tarjeta.scale(1.18)
        tarjeta.move_to(LEFT * 0.75 + DOWN * 0.35)
        self.play(FadeIn(tarjeta.caja), Write(tarjeta.texto), run_time=1.8)
        self.wait(0.7)

        # el conteo de columnas: los DOS renglones caben en 69 caracteres
        t_69 = tag_junto(tarjeta, "69 caracteres", direccion=DOWN,
                         buff=0.30, font_size=17)
        self.play(FadeIn(t_69), run_time=0.7)
        self.wait(1.9)
        self.play(FadeOut(t_69), run_time=0.4)

        # --- los campos se encienden uno a uno -----------------------------
        # tarjeta.campos preserva el orden de _CAMPOS_TLE: epoca,
        # inclinacion, raan, excentricidad, movimiento_medio. El rotulo
        # que nombra el campo activo va SIEMPRE en el mismo sitio fijo
        # (bajo el titulo): anclarlo al campo mismo lo saca del cuadro
        # cuando el campo cae cerca del borde derecho de la tarjeta.
        etiquetas = (
            ("epoca", "epoca"),
            ("inclinacion", "inclinacion"),
            ("raan", "RAAN"),
            ("excentricidad", "excentricidad"),
            ("movimiento_medio", "n"),
        )
        rotulo_campo = None
        for clave, nombre in etiquetas:
            campo = tarjeta.campos[clave]
            t = tag_hud(nombre, font_size=22, color=C_CALCULO)
            t.move_to(UP * 1.35)
            if rotulo_campo is not None:
                self.play(FadeOut(rotulo_campo), run_time=0.25)
            self.play(Indicate(campo, color=C_CALCULO, scale_factor=1.18),
                      campo.animate.set_color(C_CALCULO), FadeIn(t),
                      run_time=0.9)
            rotulo_campo = t
            self.wait(1.0)

        # --- el punto implicito de la excentricidad ------------------------
        t_exc = tag_junto(tarjeta.campos["excentricidad"],
                          "punto implicito", direccion=DOWN, buff=0.14,
                          font_size=16)
        self.play(FadeIn(t_exc), run_time=0.5)
        self.wait(1.6)
        self.play(FadeOut(t_exc), run_time=0.3)

        # --- vuelve a n: la puerta de la leccion siguiente ------------------
        self.play(FadeOut(rotulo_campo), run_time=0.3)
        rotulo_campo = None
        campo_n = tarjeta.campos["movimiento_medio"]
        self.play(Indicate(campo_n, color=C_CALCULO, scale_factor=1.25),
                  run_time=0.9)
        marco = SurroundingRectangle(campo_n, color=C_CALCULO,
                                    stroke_width=2.2, buff=0.06)
        self.play(Create(marco), run_time=0.6)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"n = {fmt(N_REV_DIA, 1)} rev/dia"),
                    zona="abajo")
        self.wait(6.2)
