class Clip3(Scene):
    """6.3.3 - SQL Server 2025 (OPPO) bifurca el plan en 2 variantes segun
    que parametros llegan NULL. La variante del cliente usa un Seek: 6
    lecturas (verde) contra las 20,010 de antes (rojo); duelo en escala
    log con aviso. Honestidad: estatus y fecha siguen sin indice propio,
    20,005 lecturas (ambar). (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("OPPO"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        # --- el plan se bifurca en 2 variantes -----------------------------
        proc = S.operador("buscar_pedidos", color=C_TITULO, ancho=3.4,
                          alto=0.85, font_size=20)
        proc.move_to(UP * 1.85)
        self.play(FadeIn(proc), run_time=0.5)
        self.wait(0.5)

        # NOTA: S.operador()/S.texto() con un nombre de DOS palabras
        # ("Variante cliente") renderizo el espacio comido ("Variantecliente"),
        # aunque "Scan pedidos" (clip 2) si lo respeto: se evita con nombres
        # de una sola palabra en las cajas.
        var_a = S.operador("Cliente", color=C_BUENO, ancho=2.6, alto=0.85,
                           font_size=22)
        var_b = S.operador("Otros", color=C_TENUE, ancho=2.6, alto=0.85,
                           font_size=22)
        VGroup(var_a, var_b).arrange(RIGHT, buff=2.2).next_to(
            proc, DOWN, buff=1.0)

        fa = Arrow(proc.get_bottom(), var_a.get_top(), buff=0.12,
                  stroke_width=3.6, color=C_BUENO,
                  max_tip_length_to_length_ratio=0.14)
        fb = Arrow(proc.get_bottom(), var_b.get_top(), buff=0.12,
                  stroke_width=3.0, color=C_TENUE,
                  max_tip_length_to_length_ratio=0.14)
        self.play(Create(fa), Create(fb), FadeIn(var_a), FadeIn(var_b),
                  run_time=0.9)
        et_var = tag_motor(f"{OPPO_VAR} variantes")
        et_var.next_to(proc, UP, buff=0.24)
        self.play(FadeIn(et_var), run_time=0.4)
        self.wait(2.2)

        # --- la variante del cliente: Select <- Seek --------------------------
        select = S.operador("Select", color=C_TITULO, ancho=1.7, alto=0.68,
                            font_size=18)
        seek = S.operador("Seek", color=C_BUENO, ancho=1.7, alto=0.68,
                          font_size=18)
        VGroup(select, seek).arrange(RIGHT, buff=1.3).next_to(
            var_a, DOWN, buff=0.7)
        f_plan = Arrow(seek.get_left(), select.get_right(), buff=0.08,
                      stroke_width=3.2, color=C_BUENO,
                      max_tip_length_to_length_ratio=0.14)
        self.play(FadeIn(select, shift=UP * 0.15), FadeIn(seek, shift=UP * 0.15),
                  run_time=0.6)
        self.play(Create(f_plan), run_time=0.5)
        et_seek = tag_junto(seek, "para el 501", DOWN, buff=0.22,
                            color=C_BUENO)
        self.play(FadeIn(et_seek), run_time=0.4)
        self.wait(2.2)

        arriba = VGroup(proc, var_a, var_b, fa, fb, et_var, select, seek,
                        f_plan, et_seek)
        self.play(FadeOut(arriba), run_time=0.7)
        self.wait(0.2)

        # --- el duelo: 20,010 (antes) contra 6 (con OPPO) ----------------------
        largo = 7.4
        maximo = CATCHALL_SIN
        base_x = LEFT * 3.4

        bar_roja = S.barra_lecturas(CATCHALL_SIN, maximo, largo=largo,
                                    alto=0.6, color=C_MALO, log=True)
        bar_roja.shift(base_x + UP * 0.9)
        bar_verde = S.barra_lecturas(CATCHALL_OPPO, maximo, largo=largo,
                                     alto=0.6, color=C_BUENO, log=True)
        bar_verde.shift(base_x + DOWN * 0.9)

        base = Line(base_x + UP * 1.7, base_x + DOWN * 1.7,
                   stroke_color=C_TENUE, stroke_width=2)
        self.play(Create(base), run_time=0.5)
        aviso = tag_junto(base, "escala logaritmica", DOWN, buff=0.3)
        self.play(FadeIn(aviso), run_time=0.4)
        self.wait(0.6)

        lab_r = tag_junto(bar_roja, "sin OPPO", LEFT, buff=0.3, color=C_MALO)
        self.play(GrowFromEdge(bar_roja, LEFT), FadeIn(lab_r), run_time=0.9)
        tag_r = tag_motor(lecturas(CATCHALL_SIN))
        tag_r.next_to(bar_roja, RIGHT, buff=0.2)
        self.play(FadeIn(tag_r), run_time=0.4)
        self.wait(1.4)

        lab_v = tag_junto(bar_verde, "con OPPO", LEFT, buff=0.3,
                          color=C_BUENO)
        self.play(GrowFromEdge(bar_verde, LEFT), FadeIn(lab_v), run_time=0.9)
        tag_v = tag_motor(lecturas(CATCHALL_OPPO))
        tag_v.next_to(bar_verde, RIGHT, buff=0.2)
        self.play(FadeIn(tag_v), run_time=0.4)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"{S.miles(round(RAZON_OPPO))}x menos lecturas"),
                   zona="abajo", run_time=0.5)
        self.play(Indicate(bar_roja, color=C_MALO, scale_factor=1.04),
                  Indicate(bar_verde, color=C_BUENO, scale_factor=1.08),
                  run_time=1.0)
        self.wait(3.0)

        # --- honestidad: estatus y fecha siguen sin indice ----------------------
        duelo = VGroup(base, aviso, bar_roja, lab_r, tag_r, bar_verde, lab_v,
                       tag_v)
        self.play(FadeOut(duelo), run_time=0.7)
        rot.limpiar("abajo", run_time=0.3)
        self.wait(0.2)

        mini_muro = S.MuroPaginas(columnas=14, filas=6, lado=0.155, sep=0.045,
                                  color=C_MALO, opacidad=0.4)
        mini_muro.move_to(UP * 0.05)
        self.play(FadeIn(mini_muro, shift=UP * 0.15), run_time=0.6)
        et_honesto = tag_junto(mini_muro, "estatus y fecha", UP, buff=0.3)
        et_sin = tag_junto(mini_muro, "sin indice propio", DOWN, buff=0.28,
                          color=C_MALO)
        self.play(FadeIn(et_honesto), FadeIn(et_sin), run_time=0.5)
        self.wait(1.2)
        rot.mostrar(motor_pie(lecturas(CATCHALL_OTROS)), zona="abajo",
                   run_time=0.5)
        self.wait(6.0)
