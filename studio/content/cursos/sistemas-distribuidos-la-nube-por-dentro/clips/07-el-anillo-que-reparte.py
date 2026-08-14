class Clip7(Scene):
    """7 - El anillo que reparte. Nodos y claves viven en el mismo circulo
    (hash md5 real): cada clave pertenece al primer nodo a favor de las
    manecillas. Entra un nodo y solo cambia de duenio el arco que ese
    nodo cubre: la fraccion se MIDE contando claves. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 07")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El anillo que reparte")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # El anillo, a la izquierda; la columna de cifras, a la derecha.
        # OJO: `con_nodo_extra()` reconstruye a tamano de constructor, asi
        # que el anillo destino se escala con este MISMO factor.
        FACTOR = 0.92
        an = anillo_hash()
        an.scale(FACTOR).shift(LEFT * 1.9 + UP * 0.15)
        centro = an._ancla.get_center()
        nodos_vg = VGroup(*an.nodos.values())
        claves_vg = VGroup(*an.claves.values())
        col = RIGHT * 3.45

        # --- momento: nodos y claves en el mismo circulo ------------------
        rot.mostrar(pie_curso("¿Qué nodo guarda qué clave? El hash los pone "
                              "en el mismo círculo."),
                    zona="abajo", run_time=0.5)

        t_nodos = tag_hud(f"{len(an.nodos)} nodos", font_size=19,
                          color=C_NODO).move_to(col + UP * 2.05)
        t_claves = tag_hud(f"{len(an.claves)} claves", font_size=19,
                           color=C_MENSAJE).move_to(col + UP * 1.50)

        self.play(Create(an.circulo), run_time=0.9)
        self.play(FadeIn(nodos_vg, scale=0.5),
                  FadeIn(t_nodos, shift=0.10 * UP), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(d, scale=0.6) for d in claves_vg],
                              lag_ratio=0.06),
                  FadeIn(t_claves, shift=0.10 * UP), run_time=1.5)
        self.wait(2.2)

        # --- momento: el duenio es el siguiente nodo ----------------------
        rot.mostrar(pie_curso("Cada clave es del primer nodo a favor de las "
                              "manecillas."),
                    zona="abajo", run_time=0.5)

        ejemplos = ("clave-0", "clave-9")
        flechas = VGroup(*[
            CurvedArrow(an.clave(c).get_center(),
                        an.nodo(an.asignacion[c]).get_center(),
                        angle=-0.55, color=C_TENUE, stroke_width=2.2,
                        tip_length=0.16)
            for c in ejemplos])
        self.play(LaggedStart(*[Create(f) for f in flechas], lag_ratio=0.35),
                  run_time=1.0)
        self.play(*[Indicate(an.clave(c), color=C_TIEMPO, scale_factor=1.7)
                    for c in ejemplos],
                  *[Indicate(an.nodo(an.asignacion[c]), color=C_TIEMPO,
                             scale_factor=1.5) for c in ejemplos],
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: entra un nodo nuevo ---------------------------------
        rot.mostrar(pie_curso("Entra una máquina más al anillo."),
                    zona="abajo", run_time=0.5)

        con = an.con_nodo_extra(NODO_NUEVO)
        con.scale(FACTOR, about_point=centro)   # mismo factor que el anillo
        nuevo = con.nodo(NODO_NUEVO)
        t_nuevo = tag_junto(nuevo, "nodo nuevo", direccion=LEFT, buff=0.34,
                            font_size=17, color=C_OK)

        self.play(FadeIn(nuevo, scale=0.4), run_time=0.5)
        self.play(Flash(nuevo.get_center(), color=C_OK, flash_radius=0.42,
                        line_length=0.16), run_time=0.5)
        self.play(FadeIn(t_nuevo, shift=0.10 * RIGHT), run_time=0.5)
        self.wait(3.4)

        # --- momento: solo se mueve un arco -------------------------------
        rot.mostrar(pie_curso("Solo cambian de dueño las claves de un arco. "
                              "El resto ni se entera."),
                    zona="abajo", run_time=0.5)

        movidas = an.claves_movidas(NODO_NUEVO)
        cifra = tag_hud(f"se mueve {an.fraccion_movida(NODO_NUEVO):.0%}",
                        font_size=30, color=C_OK).move_to(col + UP * 0.30)
        detalle = tag_hud(f"({len(movidas)} de {len(an.claves)} claves, "
                          f"contadas)", font_size=16,
                          color=C_TENUE).move_to(col + DOWN * 0.35)

        self.play(LaggedStart(*[an.clave(c).animate.set_color(C_OK)
                                for c in movidas], lag_ratio=0.14),
                  run_time=1.6)
        self.wait(0.5)
        self.play(FadeIn(cifra, shift=0.12 * UP), run_time=0.8)
        self.play(FadeIn(detalle, shift=0.10 * UP), run_time=0.6)
        self.wait(3.0)

        # --- momento: asi crece la nube -----------------------------------
        rot.mostrar(pie_curso("Así crece la nube: sin reordenar el mundo, "
                              "como predice la teoría."),
                    zona="abajo", run_time=0.5)

        teoria = tag_hud(f"1/(n+1) = {1.0 / (len(an.nodos) + 1):.0%} "
                         f"en promedio", font_size=17,
                         color=C_TIEMPO).move_to(col + DOWN * 1.15)
        self.play(FadeIn(teoria, shift=0.10 * UP), run_time=0.7)
        self.wait(5.5)
