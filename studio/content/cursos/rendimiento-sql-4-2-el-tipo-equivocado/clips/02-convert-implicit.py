class Clip2(Scene):
    """4.2.2 - El plan (derecha a izquierda): Select <- Index Seek sobre el
    indice de email. Como la columna se convierte, el operador se vuelve
    Index Scan: aparece el aviso triangular junto a Select con el rotulo
    CONVERT_IMPLICIT (Space Mono). (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("CONVERT_IMPLICIT en el plan"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        lineas_codigo = ["SELECT * FROM clientes",
                         "WHERE email = @email"]
        q = S.codigo(lineas_codigo, font_size=23)
        q.to_corner(UL, buff=0.55).shift(DOWN * 0.55)
        self.play(FadeIn(q, shift=RIGHT * 0.2), run_time=0.7)
        self.wait(1.4)

        # --- el plan, de derecha a izquierda -------------------------------
        indice = S.operador("Index Seek email", color=C_BUENO, ancho=4.0,
                            alto=0.95, font_size=23)
        select = S.operador("Select", color=C_TENUE, ancho=2.4, alto=0.95,
                            font_size=24)
        VGroup(select, indice).arrange(RIGHT, buff=1.9).move_to(DOWN * 1.15)
        flecha = Arrow(indice.get_left(), select.get_right(), buff=0.1,
                      stroke_width=5.0, color=C_TENUE,
                      max_tip_length_to_length_ratio=0.13)
        self.play(FadeIn(indice, shift=UP * 0.2), run_time=0.6)
        self.wait(0.6)
        self.play(Create(flecha), FadeIn(select, shift=UP * 0.2), run_time=0.7)
        et_plan = tag_junto(VGroup(select, indice, flecha), "plan esperado",
                            DOWN, buff=0.32, color=C_BUENO)
        self.play(FadeIn(et_plan), run_time=0.4)
        self.wait(3.0)

        # --- pero la columna se convierte: el seek se vuelve scan ----------
        self.play(FadeOut(et_plan), run_time=0.3)
        indice_scan = S.operador("Index Scan email", color=C_MALO, ancho=4.0,
                                 alto=0.95, font_size=23)
        indice_scan.move_to(indice)
        self.play(Transform(indice, indice_scan),
                  flecha.animate.set_color(C_MALO), run_time=0.9)
        self.wait(1.0)

        aviso = icono_aviso(lado=0.75, color=C_MOTOR)
        aviso.next_to(select, UP, buff=0.4)
        self.play(FadeIn(aviso, shift=DOWN * 0.15), run_time=0.6)
        self.wait(0.6)

        et_convert = tag_hud("CONVERT_IMPLICIT", font_size=19, color=C_MALO)
        et_convert.next_to(aviso, UP, buff=0.25)
        self.play(FadeIn(et_convert), run_time=0.5)
        self.wait(2.0)

        et_scan = tag_junto(indice, "recorre todo", DOWN, buff=0.3,
                            color=C_MALO)
        self.play(FadeIn(et_scan), run_time=0.4)
        self.wait(13.5)
