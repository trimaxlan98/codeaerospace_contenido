class Clip1(Scene):
    """4.3.1 - Una lista ordenada de apellidos (ilustrativa): LIKE 'Gar%'
    conoce el PRINCIPIO del valor, asi que el motor salta directo al tramo
    y solo revisa esas filas (dos marcas, tramo verde). LIKE '%cia' solo
    conoce el FINAL: no hay donde saltar, asi que revisa la lista entera
    (todo en rojo). Los dos devuelven lo mismo: los clientes que en verdad
    se apellidan Garcia. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Prefijo y sufijo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el codigo: se conoce el principio -----------------------------
        q1 = S.codigo(["SELECT id_cliente", "FROM clientes",
                       "WHERE apellido LIKE 'Gar%'"], font_size=20)
        q1.to_corner(UL, buff=0.6).shift(DOWN * 0.8)
        self.play(FadeIn(q1, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.0)

        # --- la lista ordenada, en dos columnas -----------------------------
        col_izq = columna_apellidos(COLUMNA_IZQ)
        col_der = columna_apellidos(COLUMNA_DER)
        listas = VGroup(col_izq, col_der).arrange(RIGHT, buff=1.0)
        listas.move_to(RIGHT * 1.55 + DOWN * 0.05)
        self.play(LaggedStart(*[FadeIn(f, shift=RIGHT * 0.15)
                               for f in (*col_izq, *col_der)], lag_ratio=0.03),
                  run_time=1.8)
        tag_lista = tag_junto(listas, "apellidos ordenados", UP, buff=0.3)
        self.play(FadeIn(tag_lista), run_time=0.4)
        muestra = tag_junto(listas, "muestra ilustrativa", DOWN, buff=0.3)
        self.play(FadeIn(muestra), run_time=0.4)
        self.wait(1.6)

        # --- se conoce el principio: dos marcas, tramo verde ----------------
        y_arriba = col_izq[GARCIA_DESDE].get_top()[1] + 0.05
        y_abajo = col_izq[GARCIA_HASTA].get_bottom()[1] - 0.05
        x_marca = col_izq.get_left()[0] - 0.28
        marcas = corchete(y_arriba, y_abajo, x_marca, C_BUENO)
        self.play(Create(marcas), run_time=0.6)
        self.play(*[col_izq[i].fondo.animate.set_fill(C_BUENO, 0.4)
                    .set_stroke(C_BUENO) for i in
                    range(GARCIA_DESDE, GARCIA_HASTA + 1)], run_time=0.9)
        rango = tag_junto(marcas, "rango en la lista", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(FadeIn(rango), run_time=0.4)
        self.wait(1.4)

        rot.mostrar(motor_pie(lecturas(LIKE_PREFIJO)), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        # --- se conoce solo el final: no hay donde saltar -------------------
        q2 = S.codigo(["SELECT id_cliente", "FROM clientes",
                       "WHERE apellido LIKE '%cia'"], font_size=20)
        q2.move_to(q1)
        self.play(FadeOut(q1), FadeOut(marcas), FadeOut(rango), run_time=0.6)
        self.play(FadeIn(q2, shift=RIGHT * 0.2), run_time=0.6)
        self.wait(0.8)

        todas = VGroup(*col_izq, *col_der)
        self.play(LaggedStart(*[f.fondo.animate.set_fill(C_MALO, 0.45)
                               .set_stroke(C_MALO) for f in todas],
                              lag_ratio=0.045), run_time=3.2)
        self.wait(1.0)

        rot.mostrar(motor_pie(lecturas(LIKE_SUFIJO)), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- mismo resultado en los dos ------------------------------------
        rot.mostrar(cifra_pie(f"{S.miles(GARCIA_TOTAL)} apellidos Garcia"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)
