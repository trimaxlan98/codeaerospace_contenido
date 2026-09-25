class Clip1(Scene):
    """4.2.1 - Dos formas del mismo correo: VARCHAR guarda un byte por
    caracter, NVARCHAR guarda dos (misma cantidad de caracteres, el doble
    de ancho). La columna email es VARCHAR y tiene su indice ordenado; el
    parametro que manda la aplicacion llega como N'...' (NVARCHAR). Por
    precedencia de tipos gana NVARCHAR: la conversion cae sobre la columna,
    y cada entrada del indice se convierte una por una. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("VARCHAR y NVARCHAR"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- beat A: dos formas del mismo correo ---------------------------
        correo = S.email(4242)
        fila_v = fila_bytes(len(correo), ancho_char=0.22, alto=0.5,
                            color=C_INDICE)
        fila_v.move_to(UP * 1.55)
        et_correo = tag_hud(correo, font_size=18, color=C_TENUE)
        et_correo.next_to(fila_v, UP, buff=0.22)
        self.play(FadeIn(fila_v, shift=DOWN * 0.15), run_time=0.7)
        self.play(FadeIn(et_correo), run_time=0.4)
        et_v = tag_junto(fila_v, "VARCHAR", DOWN, buff=0.22, color=C_INDICE)
        self.play(FadeIn(et_v), run_time=0.4)
        rot.mostrar(dato_pie("1 byte por caracter"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        fila_nv = fila_bytes(len(correo), ancho_char=0.44, alto=0.5,
                             color=C_INDICE)
        fila_nv.move_to(DOWN * 0.55)
        self.play(FadeIn(fila_nv, shift=DOWN * 0.15), run_time=0.7)
        et_nv = tag_junto(fila_nv, "NVARCHAR", DOWN, buff=0.22, color=C_TENUE)
        self.play(FadeIn(et_nv), run_time=0.4)
        rot.mostrar(dato_pie("2 bytes por caracter"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        beat_a = VGroup(fila_v, et_correo, et_v, fila_nv, et_nv)
        self.play(FadeOut(beat_a), run_time=0.6)
        rot.limpiar(zona="abajo", run_time=0.3)
        self.wait(0.2)

        # --- beat B: la columna (con su indice) y el parametro N'...' -----
        ids_muestra = [3, 42, 87, 501, 4242]
        correos_idx = sorted(S.email(i) for i in ids_muestra)
        lista = lista_indice_email(correos_idx, ancho=3.7, alto=0.44,
                                   buff=0.12, color=C_INDICE)
        lista.move_to(LEFT * 3.5)
        et_lista = tag_junto(lista, "indice ordenado por email", UP,
                             buff=0.28, color=C_INDICE)
        self.play(LaggedStart(*[FadeIn(e, shift=RIGHT * 0.15) for e in lista],
                              lag_ratio=0.2), run_time=1.4)
        self.play(FadeIn(et_lista), run_time=0.4)
        self.wait(1.0)

        lineas_codigo = ["EXEC buscar_cliente", f"  @email = N'{correo}'"]
        q = S.codigo(lineas_codigo, font_size=19)
        q.move_to(RIGHT * 3.1 + UP * 0.9)
        self.play(FadeIn(q, shift=LEFT * 0.2), run_time=0.7)
        self.wait(0.6)

        i, _ = pos_sin_espacios(lineas_codigo[1], "N'")
        n_glifo = q.lineas[1][i:i + 1]
        self.play(n_glifo.animate.set_color(C_MALO).scale(1.7), run_time=0.6)
        self.play(n_glifo.animate.scale(1 / 1.7), run_time=0.4)
        et_param = tag_junto(q, "parametro NVARCHAR", DOWN, buff=0.22,
                             color=C_MALO)
        self.play(FadeIn(et_param), run_time=0.4)
        self.wait(2.0)

        self.play(FadeOut(VGroup(q, et_param, et_lista)),
                  lista.animate.scale(1.2).move_to(DOWN * 0.35),
                  run_time=0.7)
        self.wait(0.2)

        # --- beat C: precedencia -> la conversion cae sobre la columna -----
        box_v = S.operador("VARCHAR", color=C_INDICE, ancho=2.1, alto=0.62,
                           font_size=20)
        box_nv = S.operador("NVARCHAR", color=C_TENUE, ancho=2.4, alto=0.62,
                            font_size=20)
        VGroup(box_v, box_nv).arrange(RIGHT, buff=1.5).move_to(UP * 2.15)
        flecha_gana = Arrow(box_v.get_right(), box_nv.get_left(), buff=0.1,
                            stroke_width=3.0, color=C_TENUE,
                            max_tip_length_to_length_ratio=0.2)
        self.play(FadeIn(box_v), FadeIn(box_nv), run_time=0.6)
        self.play(Create(flecha_gana), run_time=0.5)
        et_gana = tag_junto(box_nv, "gana", UP, buff=0.18, color=C_TITULO)
        self.play(box_nv.animate.scale(1.15),
                  box_v.animate.set_opacity(0.4), FadeIn(et_gana),
                  run_time=0.7)
        self.wait(1.2)

        flecha_baja = Arrow(box_nv.get_bottom(), lista.get_top(), buff=0.15,
                            stroke_width=3.4, color=C_MALO,
                            max_tip_length_to_length_ratio=0.14)
        et_conv = tag_junto(flecha_baja, "conversion", RIGHT, buff=0.22,
                            color=C_MALO)
        self.play(GrowArrow(flecha_baja), FadeIn(et_conv), run_time=0.8)
        self.wait(0.6)

        for entrada in lista:
            self.play(entrada.caja.animate.set_stroke(C_MALO, width=2.6)
                      .set_fill(C_MALO, 0.24),
                      entrada.texto.animate.set_color(C_MALO), run_time=0.4)
        self.wait(0.6)

        et_orden = tag_junto(lista, "el orden no sirve", DOWN, buff=0.3,
                             font_size=26, color=C_MALO)
        self.play(FadeIn(et_orden), run_time=0.5)
        self.wait(3.0)
