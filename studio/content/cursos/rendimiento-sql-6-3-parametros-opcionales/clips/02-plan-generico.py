class Clip2(Scene):
    """6.3.2 - Un unico plan generico atiende las tres llamadas: Select <-
    Filter (revisa las 3 condiciones IS NULL OR, una por una) <- Scan
    ancho de pedidos. Para el cliente 501 ese plan cuesta 20,010 lecturas
    (ambar), camino en rojo. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Plan generico"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el plan, de derecha a izquierda: Select <- Filter <- Scan --------
        select = S.operador("Select", color=C_TITULO, ancho=1.9, alto=0.85,
                            font_size=22)
        filtro = S.operador("Filter", color=C_MALO, ancho=2.3, alto=0.85,
                            font_size=22)
        scan = S.operador("Scan pedidos", color=C_MALO, ancho=4.6, alto=1.4,
                          font_size=24)
        VGroup(select, filtro, scan).arrange(RIGHT, buff=1.35).move_to(
            DOWN * 0.75)

        f2 = Arrow(scan.get_left(), filtro.get_right(), buff=0.1,
                  stroke_width=5.6, color=C_MALO,
                  max_tip_length_to_length_ratio=0.1)
        f1 = Arrow(filtro.get_left(), select.get_right(), buff=0.1,
                  stroke_width=4.4, color=C_MALO,
                  max_tip_length_to_length_ratio=0.12)

        self.play(FadeIn(scan, shift=UP * 0.15), run_time=0.6)
        et_ancho = tag_junto(scan, "toda la tabla", UP, buff=0.24)
        self.play(FadeIn(et_ancho), run_time=0.4)
        self.wait(1.4)
        self.play(Create(f2), FadeIn(filtro, shift=UP * 0.15), run_time=0.7)
        et_filtro = tag_junto(filtro, "un filtro por fila", DOWN, buff=0.22,
                              color=C_MALO)
        self.play(FadeIn(et_filtro), run_time=0.4)
        self.wait(1.4)

        # --- recordatorio: las 3 formas de preguntar convergen en el filtro ----
        etiquetas_top = ["solo cliente", "solo estatus", "solo fecha"]
        anclas = VGroup(*[Dot(radius=0.001, fill_opacity=0)
                          for _ in etiquetas_top])
        anclas.arrange(DOWN, buff=1.05)
        anclas.to_corner(UL, buff=0.8).shift(DOWN * 0.1)
        labels = VGroup(*[tag_junto(a, et, RIGHT, buff=0.02)
                          for a, et in zip(anclas, etiquetas_top)])
        flechas_top = VGroup(*[
            Arrow(lab.get_right(), filtro.get_top(), buff=0.15,
                  stroke_width=2.6, color=C_TENUE,
                  max_tip_length_to_length_ratio=0.08)
            for lab in labels])
        self.play(FadeIn(labels, shift=RIGHT * 0.15), run_time=0.7)
        self.play(LaggedStart(*[Create(f) for f in flechas_top],
                              lag_ratio=0.3), run_time=1.1)
        self.wait(1.2)

        self.play(Create(f1), FadeIn(select, shift=UP * 0.15), run_time=0.6)
        self.wait(1.0)

        et_talla = tag_junto(labels, "una talla unica", DOWN, buff=0.45)
        self.play(FadeIn(et_talla), run_time=0.4)
        self.wait(1.8)

        # --- cliente 501: 20,010 lecturas ---------------------------------------
        cont = Contador(0, rotulo="lecturas", font_size=44, digitos=6)
        cont.next_to(scan, DOWN, buff=0.9)
        self.play(FadeIn(cont), run_time=0.4)
        cont.anim(self, CATCHALL_SIN, run_time=3.4,
                 extra=[scan.caja.animate.set_stroke(C_MALO, width=3.4),
                        filtro.caja.animate.set_stroke(C_MALO, width=3.0)])
        self.wait(1.0)
        et_501 = tag_junto(cont, "para el cliente 501", UP, buff=0.3)
        self.play(FadeIn(et_501), run_time=0.4)
        self.wait(10.5)
