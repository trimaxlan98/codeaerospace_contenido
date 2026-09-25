class Clip3(Scene):
    """4.1.3 - Misma columna, dos envolturas: CAST(fecha AS DATE) contra un
    literal se convierte en un rango de un dia (17 lecturas medidas, y el
    dia real trae 1,344 pedidos); CONVERT(CHAR(10), ...) produce texto, no
    una fecha, y el motor no puede armar ningun rango: recorre la lista
    entera. La fila del indice baja y crece para llenar la mitad inferior
    del cuadro. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("CAST si, CONVERT no"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        lista = fila_lista(columnas=28, lado=0.33, sep=0.08)
        lista.move_to(DOWN * 1.35)
        self.play(FadeIn(lista), run_time=0.9)
        et_lista = tag_junto(lista, "indice por fecha", UP, buff=0.3)
        self.play(FadeIn(et_lista), run_time=0.4)
        self.wait(0.8)

        # --- CAST: se convierte en un rango pequeno --------------------------
        qa = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      "WHERE CAST(fecha_pedido AS DATE)",
                      "  = '2026-09-01'"], font_size=20)
        qa.move_to(UP * 1.55)
        self.play(FadeIn(qa, shift=DOWN * 0.2), run_time=0.8)
        self.wait(1.4)

        pareja = VGroup(lista.celda(23), lista.celda(24))
        self.play(pareja.animate.set_fill(C_BUENO, 0.9).set_stroke(C_BUENO),
                  run_time=0.7)
        rango_tag = tag_junto(qa, "se vuelve un rango", DOWN, buff=0.22,
                              color=C_BUENO)
        self.play(FadeIn(rango_tag), run_time=0.4)
        self.wait(0.6)
        et_cast = tag_motor(lecturas(M["cast_date"]))
        et_cast.next_to(pareja, UP, buff=0.3)
        self.play(FadeIn(et_cast), run_time=0.5)
        self.wait(1.6)

        # el dia que CAST convierte en rango: cuantos pedidos trae de verdad
        rot.mostrar(cifra_pie(f"{S.miles(FILAS_DIA_CAST)} pedidos ese dia"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        self.play(FadeOut(qa), FadeOut(rango_tag), FadeOut(et_cast),
                  FadeOut(et_lista),
                  pareja.animate.set_fill(C_TENUE, 0.16)
                  .set_stroke(C_TENUE, opacity=0.6),
                  run_time=0.8)
        rot.limpiar("abajo", run_time=0.4)
        self.wait(0.4)

        # --- CONVERT: produce texto, no hay rango que armar -------------------
        linea_convert = "WHERE CONVERT(CHAR(10),"
        qb = S.codigo(["SELECT id_pedido, total", "FROM pedidos",
                      linea_convert,
                      "  fecha_pedido, 120) = '2026-09-01'"], font_size=20)
        qb.move_to(UP * 1.55)
        i, j = pos_sin_espacios(linea_convert, "CONVERT(")
        qb.lineas[2][i:j].set_color(C_MALO)
        self.play(FadeIn(qb, shift=DOWN * 0.2), run_time=0.8)
        self.wait(0.6)
        texto_tag = tag_junto(qb, "no hay rango", DOWN, buff=0.22,
                              color=C_MALO)
        self.play(FadeIn(texto_tag), run_time=0.4)
        self.wait(1.8)

        self.play(LaggedStart(*lista.encender(range(len(lista)), C_MALO, 0.85),
                              lag_ratio=0.02), run_time=1.8)
        scan_tag = tag_junto(lista, "scan", UP, buff=0.3, color=C_MALO)
        self.play(FadeIn(scan_tag), run_time=0.4)
        self.wait(9.5)
