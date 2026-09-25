class Clip4(Scene):
    """4.1.4 - Mover el calculo: DATEADD(DAY, 30, fecha_pedido) envuelve la
    columna y fuerza el mismo recorrido completo que YEAR() (la fila del
    indice, abajo, se enciende ENTERA en rojo mientras el contador sube).
    Reescrita del otro lado del '>', el calculo cae sobre el literal: el
    DATEADD cruza en pantalla, la fila se apaga salvo un tramo final
    proporcional (los ultimos 30 dias, calculado) que se enciende en
    verde, y el motor vuelve a entrar por un rango. Cierre. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Mover el calculo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        header = S.codigo(["SELECT id_pedido, total", "FROM pedidos"],
                          font_size=20)
        header.to_corner(UL, buff=0.6).shift(DOWN * 0.7)
        self.play(FadeIn(header, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.3)

        linea_mal = "WHERE DATEADD(DAY, 30, fecha_pedido)"
        predicado_a = S.codigo([linea_mal, "  > '2026-09-15'"], font_size=20)
        predicado_a.next_to(header, DOWN, buff=0.18).align_to(header, LEFT)
        i, j = pos_sin_espacios(linea_mal, "DATEADD(")
        predicado_a.lineas[0][i:j].set_color(C_MALO)
        self.play(FadeIn(predicado_a, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.0)

        # --- la fila del indice, abajo: llena la mitad inferior del cuadro --
        lista = fila_lista(columnas=28, lado=0.33, sep=0.08)
        lista.move_to(DOWN * 1.9)
        self.play(FadeIn(lista), run_time=0.7)
        et_lista = tag_junto(lista, "indice por fecha", UP, buff=0.3)
        self.play(FadeIn(et_lista), run_time=0.3)
        self.wait(0.6)

        cont = Contador(0, rotulo="lecturas", font_size=38, digitos=4)
        cont.move_to(RIGHT * 3.7 + UP * 0.35)
        self.play(FadeIn(cont), run_time=0.4)
        etiqueta = tag_junto(cont, "indice completo", DOWN, buff=0.24)
        self.play(FadeIn(etiqueta), run_time=0.3)
        self.wait(0.5)

        # DATEADD envuelve la columna: la fila entera se enciende en rojo
        # MIENTRAS el contador sube (misma causa, mismo tiempo)
        cont.anim(self, M["dateadd_mal"], run_time=2.4,
                 extra=[LaggedStart(*lista.encender(range(len(lista)), C_MALO, 0.85),
                                    lag_ratio=0.03)])
        self.wait(3.0)

        # --- cruzar: el DATEADD se muda al otro lado del ">" -----------------
        linea_bien = "  DATEADD(DAY, -30, '2026-09-15')"
        predicado_b = S.codigo(["WHERE fecha_pedido >", linea_bien],
                               font_size=20)
        predicado_b.move_to(predicado_a, aligned_edge=LEFT)
        ib, jb = pos_sin_espacios(linea_bien, "DATEADD(")
        predicado_b.lineas[1][ib:jb].set_color(C_BUENO)

        chip = predicado_a.lineas[0][i:j].copy()
        predicado_a.lineas[0][i:j].set_opacity(0)
        chip_target = predicado_b.lineas[1][ib:jb].copy()
        predicado_b.lineas[1][ib:jb].set_opacity(0)
        self.add(chip)

        etiqueta2 = tag_junto(cont, "solo el rango", DOWN, buff=0.24)

        # el tramo verde final: ancho REAL, proporcional a las filas con
        # fecha_pedido > '2026-08-16' (el mismo corte que deja el DATEADD
        # movido), no un numero de celdas a ojo
        n_verdes = max(1, round(FRACCION_30D * len(lista)))
        corte = len(lista) - n_verdes
        apagar_rojo = [lista.celda(k).animate.set_fill(C_TENUE, 0.16)
                      .set_stroke(C_TENUE, opacity=0.6) for k in range(corte)]
        encender_verde = [lista.celda(k).animate.set_fill(C_BUENO, 0.9)
                          .set_stroke(C_BUENO) for k in range(corte, len(lista))]

        vt = ValueTracker(M["dateadd_mal"])
        cont.num.add_updater(lambda m: cont.fijar(vt.get_value()))
        self.play(FadeOut(predicado_a), FadeIn(predicado_b),
                  Transform(chip, chip_target),
                  FadeOut(etiqueta), FadeIn(etiqueta2),
                  vt.animate.set_value(M["dateadd_bien"]),
                  *apagar_rojo, *encender_verde,
                  run_time=1.6)
        cont.num.clear_updaters()
        cont.fijar(M["dateadd_bien"])
        predicado_b.lineas[1][ib:jb].set_opacity(1)
        self.remove(chip)
        self.wait(0.4)

        cola = VGroup(*[lista.celda(k) for k in range(corte, len(lista))])
        cola_tag = tag_junto(cola, "ultimos 30 dias", DOWN, buff=0.28,
                             color=C_BUENO)
        self.play(FadeIn(cola_tag), run_time=0.4)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"{round(RAZON_DATEADD)}x menos lecturas"),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(cont, color=C_BUENO, scale_factor=1.06),
                  Indicate(predicado_b.lineas[1][ib:jb], color=C_BUENO),
                  run_time=1.0)
        self.wait(4.0)

        grupo = VGroup(header, predicado_b, cont, etiqueta2, lista, et_lista,
                       cola_tag)
        cierre_leccion(self, rot, "La columna va sola.",
                       "El calculo, del otro lado.", grupo, espera=7.0)
