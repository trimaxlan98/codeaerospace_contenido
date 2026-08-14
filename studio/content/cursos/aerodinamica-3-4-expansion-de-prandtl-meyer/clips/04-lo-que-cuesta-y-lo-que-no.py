class Clip4(Scene):
    """3.4.4 - Contraste conceptual: expansion isentropica vs. choque
    irreversible.

    El mismo giro, en los dos sentidos, sobre el plano T-s de la leccion
    1.2. Comprimir mueve el estado a la derecha; expandir lo baja recto. Y
    de esa asimetria sale una consecuencia de ingenieria: comprimir y
    expandir en serie NO devuelve al punto de partida. Cierre de la leccion.
    (~41 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Lo que cuesta y lo que no")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        ts = diagrama_ts(ancho=5.4, alto=2.9)
        ts.move_to(DOWN * 0.25)
        self.play(FadeIn(ts.ejes), run_time=0.6)

        uno = ts.estado(0.22, 0.46, "1", color=C_TENUE, direccion=LEFT)
        self.play(FadeIn(uno, scale=1.5), run_time=0.5)
        rot.mostrar(pie_curso("El mismo flujo, y el mismo giro de quince "
                              "grados. En los dos sentidos."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        # --- comprimir: a la derecha ---------------------------------------
        compresion = ts.trayecto([(0.22, 0.46), (0.56, 0.80)], color=C_SUPER)
        dos = ts.estado(0.56, 0.80, "choque", color=C_SUPER, direccion=UR)
        self.play(Create(compresion), run_time=0.8)
        self.play(FadeIn(dos, scale=1.4), run_time=0.5)
        rot.mostrar(pie_curso("Hacia dentro: choque. Sube la temperatura y "
                              "sube la entropía."), zona="abajo",
                    run_time=0.5)
        self.wait(4.8)

        # --- expandir: recto hacia abajo -----------------------------------
        expansion_ts = ts.trayecto([(0.22, 0.46), (0.22, 0.14)], color=C_SUB)
        tres = ts.estado(0.22, 0.14, "abanico", color=C_SUB, direccion=DOWN)
        self.play(Create(expansion_ts), run_time=0.8)
        self.play(FadeIn(tres, scale=1.4), run_time=0.5)
        rot.mostrar(pie_curso("Hacia fuera: abanico. Baja la temperatura y "
                              "la entropía no se mueve."), zona="abajo",
                    run_time=0.5)
        self.wait(5.0)

        rot.mostrar(pie_curso("La misma pared, el mismo ángulo, y uno de los "
                              "dos es gratis."), zona="abajo", run_time=0.5)
        self.wait(4.8)

        # --- la consecuencia -----------------------------------------------
        rot.mostrar(pie_curso("Y tiene consecuencia: comprimir y luego "
                              "expandir no te devuelve al punto de "
                              "partida."), zona="abajo", run_time=0.5)
        self.wait(5.2)

        # --- cierre de la leccion ------------------------------------------
        self.play(FadeOut(VGroup(ts, uno, compresion, dos, expansion_ts,
                                 tres)), run_time=0.8)
        cierre = VGroup(
            titulo_marca("Girar hacia dentro deja cicatriz.", font_size=35,
                         color=C_SUPER),
            titulo_marca("Hacia fuera, no.", font_size=35,
                         color=C_SUB)).arrange(DOWN, buff=0.28)
        cierre.move_to(DOWN * 0.1)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeIn(cierre, shift=0.18 * UP), run_time=1.0)
        self.wait(4.0)
