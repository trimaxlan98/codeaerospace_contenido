from comunicaciones import TrenBits  # noqa: E402


class Clip3(Scene):
    """6.2.3 - La trama HDLC: arriba, sus 5 tramos a proporcion (233 bits);
    abajo, bandera 01111110 al inicio y al final (gris, norma) y en medio
    (zoom) el tramo real donde S.ais_trama inserto el unico bit de relleno
    tras cinco unos seguidos (buscado por patron en TRAMA, no a mano).
    Cian: 233 bits en la trama, 1 bit de relleno. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("La bandera y el relleno"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- localizar el bit insertado: el UNICO tramo de cinco unos
        # seguidos en el cuerpo (RELLENO == 1 lo garantiza unico) -----------
        ini_cuerpo = 24 + len(S.BANDERA)
        fin_cuerpo = len(TRAMA) - len(S.BANDERA) - 8
        s_cuerpo = "".join(str(int(b)) for b in TRAMA[ini_cuerpo:fin_cuerpo])
        j = s_cuerpo.find("11111")
        idx_relleno = ini_cuerpo + j + 5

        lo, hi = idx_relleno - 6, idx_relleno + 3
        local = idx_relleno - lo

        # --- arriba: los 5 tramos de la trama, a proporcion -----------------
        tramos = [(24, C_EJE), (len(S.BANDERA), C_DATO),
                  (fin_cuerpo - ini_cuerpo, C_TITULO),
                  (len(S.BANDERA), C_DATO), (8, C_EJE)]
        w_total = 10.8
        barra = VGroup()
        x = -w_total / 2
        for n, color in tramos:
            w = w_total * n / len(TRAMA)
            r = Rectangle(width=w, height=0.62, stroke_width=1.3,
                         stroke_color=C_EJE, fill_color=color,
                         fill_opacity=0.55)
            r.move_to(RIGHT * (x + w / 2))
            barra.add(r)
            x += w
        barra.move_to(UP * 1.85)
        et_barra = tag_junto(barra, "la trama entera", UP, buff=0.2,
                             font_size=22, color=C_TENUE)
        cuerpo_rect = barra[2]

        self.play(Create(barra), run_time=1.6)
        self.play(FadeIn(et_barra), run_time=0.4)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"{len(TRAMA)} bits en la trama"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- abajo: bandera - zoom - bandera --------------------------------
        lado_flag, lado_det = 0.3, 0.56
        tb_f1 = TrenBits(S.BANDERA, lado=lado_flag, color=C_DATO)
        tb_f2 = TrenBits(S.BANDERA, lado=lado_flag, color=C_DATO)
        tb_det = TrenBits(TRAMA[lo:hi], lado=lado_det, color=C_TITULO)
        e1 = Text("...", font=FUENTE_HUD, font_size=26, color=C_TENUE)
        e2 = Text("...", font=FUENTE_HUD, font_size=26, color=C_TENUE)

        fila = VGroup(tb_f1, e1, tb_det, e2, tb_f2).arrange(RIGHT, buff=0.32)
        fila.move_to(DOWN * 1.15)

        # el extremo apunta a la ULTIMA celda (derecha), lejos de donde
        # entrara despues la llave "cinco unos" (columnas 1-5, izquierda),
        # para que la linea no la atraviese.
        flecha = DashedLine(cuerpo_rect.get_bottom() + DOWN * 0.05,
                            tb_det.celdas[-1].get_top() + UP * 0.08,
                            color=C_TENUE, stroke_width=2.0,
                            dash_length=0.08)

        et_f1 = tag_junto(tb_f1, "bandera", UP, buff=0.22, font_size=19,
                          color=C_DATO)
        et_f2 = tag_junto(tb_f2, "bandera", UP, buff=0.22, font_size=19,
                          color=C_DATO)

        self.play(Create(flecha), run_time=0.6)
        self.play(Create(tb_f1.celdas), FadeIn(et_f1), run_time=0.7)
        self.play(FadeIn(tb_f1.digitos), run_time=0.5)
        self.wait(0.4)
        self.play(FadeIn(e1), run_time=0.3)
        self.play(Create(tb_det.celdas), run_time=0.9)
        self.play(FadeIn(tb_det.digitos), run_time=0.6)
        self.wait(0.5)
        self.play(FadeIn(e2), run_time=0.3)
        self.play(Create(tb_f2.celdas), FadeIn(et_f2), run_time=0.7)
        self.play(FadeIn(tb_f2.digitos), run_time=0.5)
        self.wait(1.2)

        # --- zoom: cinco unos seguidos y el cero insertado, resaltado ------
        cinco = VGroup(*[tb_det.celda(i) for i in range(1, 6)])
        llave = Brace(cinco, UP, buff=0.16, color=C_TENUE)
        et_cinco = tag_junto(llave, "cinco unos", UP, buff=0.14,
                             font_size=19, color=C_TENUE)
        self.play(GrowFromCenter(llave), FadeIn(et_cinco), run_time=0.7)
        self.wait(1.4)

        tb_det.marcar(local, color=C_CALCULO)
        et_relleno = tag_junto(tb_det.celda(local), "relleno", DOWN,
                               buff=0.22, font_size=19, color=C_CALCULO)
        self.play(tb_det.celda(local).animate.set_stroke(C_CALCULO,
                                                          width=3.0),
                  tb_det.digito(local).animate.set_color(C_CALCULO),
                  FadeIn(et_relleno), run_time=0.8)
        self.wait(1.3)

        rot.mostrar(cifra_pie(f"{RELLENO} bit de relleno", color=C_CALCULO),
                    zona="abajo", run_time=0.5)
        self.wait(11.0)
