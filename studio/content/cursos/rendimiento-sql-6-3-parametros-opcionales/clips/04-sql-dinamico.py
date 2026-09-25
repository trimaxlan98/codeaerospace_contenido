class Clip4(Scene):
    """6.3.4 - SQL dinamico: el texto de la consulta se arma solo con los
    filtros presentes (sp_executesql). Las lineas que no aplican se
    apagan; la que aplica se enciende, y cambia de caso en caso. Para el
    cliente 501: 6 lecturas (ambar). Cierre de la leccion. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("SQL dinamico"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        base = "SELECT ... FROM pedidos WHERE 1=1"
        l_cli = "  AND id_cliente = @id_cliente"
        l_est = "  AND estatus = @estatus"
        l_fec = "  AND fecha_pedido >= @desde"
        q = S.codigo([base, l_cli, l_est, l_fec], font_size=22)
        q.move_to(LEFT * 3.1 + UP * 0.5)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.8)
        self.wait(1.2)

        linea_cli, linea_est, linea_fec = q.lineas[1], q.lineas[2], q.lineas[3]
        et_arma = tag_junto(q, "solo lo que llega", DOWN, buff=0.3)
        self.play(FadeIn(et_arma), run_time=0.5)
        self.wait(1.6)

        # --- caso 1: solo llega el cliente ---------------------------------
        self.play(linea_est.animate.set_opacity(0.16),
                  linea_fec.animate.set_opacity(0.16), run_time=0.8)
        et_caso1 = tag_junto(q, "solo cliente", UP, buff=0.32, color=C_BUENO)
        self.play(FadeIn(et_caso1), run_time=0.4)
        self.wait(2.2)

        # --- caso 2: solo llega el estatus (mismo patron, otra forma) ------
        self.play(FadeOut(et_caso1), run_time=0.3)
        self.play(linea_cli.animate.set_opacity(0.16),
                  linea_est.animate.set_opacity(1.0), run_time=0.9)
        et_caso2 = tag_junto(q, "solo estatus", UP, buff=0.32, color=C_BUENO)
        self.play(FadeIn(et_caso2), run_time=0.4)
        self.wait(2.2)

        # --- vuelve al caso del cliente: el que se mide --------------------
        self.play(FadeOut(et_caso2), run_time=0.3)
        self.play(linea_cli.animate.set_opacity(1.0),
                  linea_est.animate.set_opacity(0.16), run_time=0.9)
        et_caso3 = tag_junto(q, "solo cliente", UP, buff=0.32, color=C_BUENO)
        self.play(FadeIn(et_caso3), run_time=0.4)
        self.wait(1.8)

        # --- se ejecuta: 6 lecturas, al otro lado del cuadro ----------------
        cont = Contador(0, rotulo="lecturas", font_size=58, digitos=3)
        cont.move_to(RIGHT * 3.4 + UP * 0.5)
        flecha = Arrow(linea_cli.get_right(), cont.get_left(), buff=0.3,
                      stroke_width=3.4, color=C_BUENO,
                      max_tip_length_to_length_ratio=0.1)
        self.play(Create(flecha), run_time=0.6)
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, DINAMICO, run_time=1.6)
        self.wait(3.6)

        cierre_leccion(self, rot, "Un plan por forma de pregunta,",
                       "no uno para todas.",
                       q, et_arma, et_caso3, flecha, cont, espera=7.5)
