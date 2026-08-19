class Clip4(Scene):
    """5.1.4 - Rotaciones y reflexiones mueven la rejilla entera sin
    deformar ni una celda (ortogonales, det +-1); la cizalla, en cambio,
    conserva el área pero SÍ deforma: no es ortogonal. Cierra la lección.
    (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Mover sin deformar")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        pl = plano_leccion()
        # OJO: v NUNCA se reasigna tras un anim_matriz: sus .coords se
        # quedan a propósito en V_MOVER, para que cada llamada siguiente
        # calcule el M PURO desde el original (no una cadena de matrices).
        v = vector(pl, V_MOVER, color=C_VEC, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Algunas matrices mueven la rejilla entera "
                              "sin deformar ni una celda."), zona="abajo",
                    run_time=0.5)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.8)
        celda = celdas(pl, np.eye(2), celdas_ij=((0, 0),), color=C_AREA,
                       opacidad=0.3)
        self.play(FadeIn(celda), run_time=0.4)
        self.wait(2.4)

        panel_m = panel_derecha(matriz_columnas(ROT_MOVER, font_size=32))
        cifras = VGroup(
            tag_hud("det = " + fmt(DET_ROT_MOVER, 1), font_size=18),
            tag_hud("ortogonal: " + ("si" if ORTOG_ROT_MOVER else "no"),
                   font_size=18),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        panel_c = panel_derecha(cifras)
        panel_c.next_to(panel_m, DOWN, buff=0.2).align_to(panel_m, RIGHT)

        # --- momento: la rotacion --------------------------------------------
        rot.mostrar(pie_curso("Una rotación: la rejilla gira entera, y "
                              "cada celda sigue siendo el mismo cuadrado."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(panel_m, shift=0.15 * LEFT), run_time=0.5)
        celda_r = celdas(pl, ROT_MOVER, celdas_ij=((0, 0),), color=C_AREA,
                         opacidad=0.3)
        self.play(*pl.anim_matriz(ROT_MOVER, v), Transform(celda, celda_r),
                  run_time=1.5)
        self.play(FadeIn(panel_c, shift=0.15 * LEFT), run_time=0.5)
        self.wait(2.8)

        # --- momento: la reflexion --------------------------------------------
        rot.mostrar(pie_curso("Una reflexión también: voltea la rejilla, "
                              "pero no la deforma."), zona="abajo",
                    run_time=0.5)
        panel_m2 = panel_derecha(matriz_columnas(REFLEX_MOVER, font_size=32))
        cifras2 = VGroup(
            tag_hud("det = " + fmt(DET_REFLEX_MOVER, 1), font_size=18),
            tag_hud("ortogonal: " + ("si" if ORTOG_REFLEX_MOVER else "no"),
                   font_size=18),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        panel_c2 = panel_derecha(cifras2)
        panel_c2.next_to(panel_m2, DOWN, buff=0.2).align_to(panel_m2, RIGHT)
        self.play(FadeOut(panel_m), FadeOut(panel_c), run_time=0.4)
        celda_f = celdas(pl, REFLEX_MOVER, celdas_ij=((0, 0),), color=C_AREA,
                         opacidad=0.3)
        self.play(*pl.anim_matriz(REFLEX_MOVER, v), Transform(celda, celda_f),
                  FadeIn(panel_m2, shift=0.15 * LEFT), run_time=1.5)
        self.play(FadeIn(panel_c2, shift=0.15 * LEFT), run_time=0.5)
        self.wait(2.8)

        # --- momento: contraejemplo, la cizalla --------------------------------
        rot.mostrar(pie_curso("Pero cuidado: la cizalla también conserva "
                              "el área. ¿También mueve sin deformar?"),
                    zona="abajo", run_time=0.5)
        panel_m3 = panel_derecha(matriz_columnas(CIZALLA_MOVER, font_size=32))
        cifras3 = VGroup(
            tag_hud("det = " + fmt(DET_CIZALLA_MOVER, 1), font_size=18),
            tag_hud("ortogonal: " + ("si" if ORTOG_CIZALLA_MOVER else "no"),
                   font_size=18),
        ).arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        panel_c3 = panel_derecha(cifras3)
        panel_c3.next_to(panel_m3, DOWN, buff=0.2).align_to(panel_m3, RIGHT)
        self.play(FadeOut(panel_m2), FadeOut(panel_c2), run_time=0.4)
        celda_c = celdas(pl, CIZALLA_MOVER, celdas_ij=((0, 0),), color=C_AREA,
                         opacidad=0.3)
        self.play(*pl.anim_matriz(CIZALLA_MOVER, v), Transform(celda, celda_c),
                  FadeIn(panel_m3, shift=0.15 * LEFT), run_time=1.5)
        self.wait(2.0)
        rot.mostrar(pie_curso("No: la celda se vuelve un paralelogramo. "
                              "Área igual no basta: falta ortogonalidad."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(panel_c3, shift=0.15 * LEFT), run_time=0.5)
        self.wait(3.2)

        # --- cierre de la leccion -----------------------------------------------
        cierre_leccion(self, rot, "Ortogonal: se mueve todo",
                       "y no se deforma nada.",
                       "La próxima lección generaliza esto: la SVD "
                       "encuentra ejes para cualquier matriz.",
                       pl, v, celda, panel_m3, panel_c3)
