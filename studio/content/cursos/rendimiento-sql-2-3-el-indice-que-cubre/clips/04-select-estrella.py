class Clip4(Scene):
    """2.3.4 - SELECT * pide comentarios, que no vive en la hoja ancha: el
    lookup vuelve y las lecturas regresan a 597 (solo en el contador: no se
    repite abajo). Cierre de la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("SELECT * lo rompe"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- recordatorio: la hoja ancha, con lo que SI trae --------------
        hoja = fila_de([celda_campo(n, color=C_BUENO)
                        for n in ("id_cliente", "id_pedido", "fecha_pedido",
                                  "estatus", "total")], buff=0.14)
        falta = celda_campo("comentarios", color=C_MALO, relleno=0.05)
        falta.next_to(hoja, RIGHT, buff=0.6)
        grupo_filas = VGroup(hoja, falta)
        grupo_filas.move_to(UP * 1.85)

        et_hoja = tag_junto(hoja, "la hoja lo tiene", UP, buff=0.24,
                            color=C_BUENO)
        self.play(FadeIn(hoja), run_time=0.7)
        self.play(FadeIn(et_hoja), run_time=0.4)
        self.wait(1.0)

        et_falta = tag_junto(falta, "no esta aqui", UP, buff=0.24,
                             color=C_MALO)
        self.play(FadeIn(falta, shift=LEFT * 0.15), run_time=0.6)
        self.play(FadeIn(et_falta), run_time=0.4)
        self.wait(1.8)

        # --- el codigo: SELECT * ------------------------------------------
        q = S.codigo(["SELECT *", "FROM pedidos",
                      "WHERE id_cliente = 501"], font_size=20)
        q.move_to(LEFT * 3.9 + DOWN * 1.15)
        self.play(FadeIn(q, shift=UP * 0.2), run_time=0.7)
        self.wait(0.4)
        estrella = q.lineas[0][6:7]
        self.play(estrella.animate.set_color(C_MALO).scale(1.5), run_time=0.6)
        self.play(estrella.animate.scale(1 / 1.5), run_time=0.4)
        et_pide = tag_junto(q, "pide todo", DOWN, buff=0.2, color=C_MALO)
        self.play(FadeIn(et_pide), run_time=0.4)
        self.wait(2.0)

        # --- vuelve el viaje: un lookup activo, esta vez rojo -------------
        tabla = RoundedRectangle(width=1.5, height=1.0, corner_radius=0.1,
                                 stroke_color=C_MALO, stroke_width=2.0)
        tabla.move_to(RIGHT * 3.9 + DOWN * 1.15)
        t_tabla = Text("agrupado", font_size=20, color=C_MALO)
        t_tabla.move_to(tabla)
        flecha = Arrow(falta.get_bottom() + DOWN * 0.15, tabla.get_top(),
                      buff=0.1, stroke_width=3.5, color=C_MALO,
                      max_tip_length_to_length_ratio=0.14)
        self.play(FadeIn(tabla, t_tabla), run_time=0.5)
        self.play(GrowArrow(flecha), run_time=0.7)
        et_vuelve = tag_junto(flecha, "vuelve el lookup", RIGHT, buff=0.25,
                             color=C_MALO)
        self.play(FadeIn(et_vuelve), run_time=0.4)
        self.wait(1.6)

        # --- el contador dice 597: no se repite abajo (una sola vez) ------
        cont = Contador(0, rotulo="lecturas", font_size=34, digitos=3)
        cont.next_to(tabla, DOWN, buff=0.6)
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, M["c501_select_estrella"], run_time=1.6)
        self.wait(4.2)

        cierre_leccion(self, rot, "Pide solo lo que usas.",
                       "El indice ya lo tiene.",
                       hoja, et_hoja, falta, et_falta, q, et_pide, tabla,
                       t_tabla, flecha, et_vuelve, cont, espera=5.5)
