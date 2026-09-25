class Clip3(Scene):
    """5.3.3 - dbo.fn_TotalCliente(id_cliente) es una funcion escalar: por
    cada una de las 500 filas que devuelve el SELECT (el TOP (500) de la
    consulta, no una medicion) el motor la llama por separado, fila a
    fila. El contador de llamadas (gris: no es una lectura del motor)
    sube hasta 500. Tiempo medido para las 500 llamadas: 17.6 s (ambar).
    (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Funcion escalar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        # --- el codigo: una funcion dentro del SELECT -------------------------
        q = S.codigo(["SELECT TOP (500) id_cliente,",
                      "  dbo.fn_TotalCliente(id_cliente)",
                      "FROM clientes"], font_size=19)
        q.move_to(LEFT * 3.4 + UP * 1.9)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        linea = "  dbo.fn_TotalCliente(id_cliente)"
        plano = linea.replace(" ", "")
        objetivo = "dbo.fn_TotalCliente(id_cliente)"
        i = plano.find(objetivo)
        marca = SurroundingRectangle(q.lineas[1][i:i + len(objetivo)],
                                     color=C_TITULO, buff=0.06,
                                     stroke_width=2.2)
        self.play(Create(marca), run_time=0.7)
        tag_fn = tag_junto(q, "una funcion por fila", DOWN, buff=0.26)
        self.play(FadeIn(tag_fn), run_time=0.4)
        self.wait(2.0)

        # --- el bucle: la funcion se llama una y otra vez ----------------------
        bucle = bucle_llamada(ancho=3.2, alto=1.15, color=C_TENUE)
        bucle.move_to(RIGHT * 3.0 + UP * 1.7)
        self.play(FadeIn(bucle.caja, shift=LEFT * 0.2), run_time=0.6)
        self.play(Create(bucle[1]), run_time=0.8)
        tag_rep = tag_junto(bucle, "una llamada por fila", DOWN, buff=0.5,
                            color=C_TENUE)
        self.play(FadeIn(tag_rep), run_time=0.4)
        self.wait(1.4)

        # --- el contador de llamadas: NO es una lectura del motor (gris) -------
        cont = Contador(0, rotulo="llamadas", font_size=54, digitos=3,
                       color=C_TENUE)
        cont.move_to(RIGHT * 3.0 + DOWN * 1.3)
        self.play(FadeIn(cont), run_time=0.4)
        self.wait(0.5)
        cont.anim(self, TOP_500, run_time=3.2,
                 extra=[bucle.caja.caja.animate.set_stroke(C_TENUE, width=3.0)])
        self.wait(2.4)

        # --- el tiempo que cuestan las 500 llamadas, medido en el motor --------
        rot.mostrar(motor_pie(tiempo(UDF_140)), zona="abajo", run_time=0.5)
        self.wait(14.5)
