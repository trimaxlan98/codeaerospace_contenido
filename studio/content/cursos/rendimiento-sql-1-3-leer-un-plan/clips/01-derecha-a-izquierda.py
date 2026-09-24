class Clip1(Scene):
    """1.3.1 - Un plan de 3 operadores (Scan -> Filter -> Select) se lee de
    derecha a izquierda: un cursor recorre las cajas en ese orden mientras
    se iluminan, y el grosor de cada flecha es el numero de filas que pasa
    por ahi (1.5 M contra 191). (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("De derecha a izquierda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- las tres cajas: Select tambien es un operador -----------------
        scan = S.operador("Scan", color=C_TITULO)
        filt = S.operador("Filter", color=C_TITULO)
        sel = S.operador("Select", color=C_TITULO)
        plan = VGroup(sel, filt, scan)
        plan.arrange(RIGHT, buff=2.1)
        plan.move_to(UP * 0.35)

        # --- flechas: el grosor es log10(filas) ----------------------------
        f1 = S.flecha_plan(scan.get_left(), filt.get_right(), FILAS_PED,
                           color=C_TENUE)
        f2 = S.flecha_plan(filt.get_left(), sel.get_right(), C501,
                           color=C_TENUE)

        # --- el cursor de lectura: un triangulo que apunta a la izquierda --
        cursor = Triangle(color=C_TITULO, fill_color=C_TITULO,
                          fill_opacity=1.0, stroke_width=0).scale(0.13)
        cursor.rotate(-PI / 2)
        cursor.move_to(scan.get_top() + UP * 0.55)

        self.wait(0.3)
        self.play(FadeIn(scan, shift=UP * 0.15), FadeIn(cursor), run_time=0.7)
        self.play(scan.caja.animate.set_stroke(C_BUENO, width=3.4), run_time=0.5)
        self.wait(1.2)

        self.play(Create(f1), run_time=0.9)
        et1 = tag_hud(f"{S.miles(FILAS_PED)} filas", font_size=18)
        et1.move_to((scan.get_left() + filt.get_right()) / 2 + UP * 0.55)
        self.play(FadeIn(et1), run_time=0.4)
        self.wait(1.8)

        self.play(cursor.animate.move_to(filt.get_top() + UP * 0.55), run_time=0.6)
        self.play(FadeIn(filt, shift=UP * 0.15), run_time=0.6)
        self.play(filt.caja.animate.set_stroke(C_BUENO, width=3.4), run_time=0.5)
        self.wait(1.0)

        self.play(Create(f2), run_time=0.9)
        et2 = tag_hud(f"{S.miles(C501)} filas", font_size=18)
        et2.move_to((filt.get_left() + sel.get_right()) / 2 + UP * 0.55)
        self.play(FadeIn(et2), run_time=0.4)
        self.wait(1.8)

        self.play(cursor.animate.move_to(sel.get_top() + UP * 0.55), run_time=0.6)
        self.play(FadeIn(sel, shift=UP * 0.15), run_time=0.6)
        self.play(sel.caja.animate.set_stroke(C_BUENO, width=3.4), run_time=0.5)
        self.wait(2.6)

        razon = S.razon(FILAS_PED, C501)
        rot.mostrar(cifra_pie(f"{S.miles(razon)} veces menos filas"),
                    zona="abajo", run_time=0.5)
        self.wait(12.0)
