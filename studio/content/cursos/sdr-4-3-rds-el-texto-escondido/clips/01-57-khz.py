class Clip1(Scene):
    """4.3.1 - El espectro del MPX con RDS: la subportadora vive en 57 kHz,
    tres saltos de 19 kHz (el piloto) mas alla del piloto mismo. La
    relacion se calcula en pantalla; 1187.5 bit/s es la norma (gris).
    (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("57 kHz"), zona="arriba", run_time=0.6)
        self.wait(0.4)

        rds_bb = S.rds_banda_base(np.tile(BITS_PS, 2))
        y, _, _ = S.mpx(n=len(rds_bb), rds=rds_bb)
        f_full, db_full = S.espectro_db(y, FS, nfft=8192)
        f, db = S.para_dibujar(f_full, db_full, 900, 0.0, 60e3)
        esp = S.Espectro(f, db, piso=-60.0, techo=2.0, ancho=12.2, alto=3.5,
                         color=C_SENAL)
        esp.move_to(DOWN * 0.3)
        ticks = esp.marcas([0, 19e3, 38e3, 57e3], ["0", "19", "38", "57"])
        u = tag_junto(ticks[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.7)
        self.wait(0.5)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=1.9)
        self.wait(2.0)

        # --- el piloto, referencia -----------------------------------------
        m_piloto = esp.marca_f(S.F_PILOTO, color=C_DATO)
        et_piloto = tag_junto(m_piloto, "piloto", UP, buff=0.16,
                              font_size=18, color=C_DATO)
        self.play(Create(m_piloto), FadeIn(et_piloto), run_time=0.6)
        self.wait(1.8)

        # --- el RDS resaltado en 57 kHz --------------------------------
        banda_rds = esp.banda(S.F_RDS - 1.4e3, S.F_RDS + 1.4e3,
                              color=C_CALCULO, opacidad=0.24)
        m_rds = esp.marca_f(S.F_RDS, color=C_CALCULO)
        et_rds = tag_junto(m_rds, "RDS", UP, buff=0.16, font_size=18,
                           color=C_CALCULO)
        self.play(FadeIn(banda_rds), Create(m_rds), FadeIn(et_rds),
                  run_time=0.8)
        self.wait(2.2)

        # --- tres saltos de 19 kHz hasta el 57 kHz --------------------------
        y_fila = esp.en(0.0, esp.techo)[1] + 0.85
        mult = int(round(S.F_RDS / S.F_PILOTO))
        paso = S.F_PILOTO
        saltos = VGroup()
        for k in range(mult):
            a = esp.en(k * paso, esp.techo)
            b = esp.en((k + 1) * paso, esp.techo)
            fl = Arrow(np.array([a[0], y_fila, 0.0]),
                      np.array([b[0], y_fila, 0.0]), buff=0.04,
                      color=C_CALCULO, stroke_width=3.2,
                      max_tip_length_to_length_ratio=0.2)
            saltos.add(fl)
        self.play(*[GrowArrow(fl) for fl in saltos], run_time=1.4)
        et_x3 = tag_hud(f"x{mult}", font_size=20, color=C_CALCULO)
        et_x3.next_to(saltos, UP, buff=0.14)
        self.play(FadeIn(et_x3), run_time=0.4)
        self.wait(2.6)

        k_rds = int(S.F_RDS / 1e3)
        k_piloto = int(S.F_PILOTO / 1e3)
        rot.mostrar(cifra_pie(f"{k_rds} = {mult} x {k_piloto}"),
                    zona="abajo", run_time=0.5)
        self.wait(5.2)
        rot.mostrar(dato_pie(f"{fmt(S.RDS_BPS, 1)} bit/s"), zona="abajo",
                    run_time=0.5)
        self.wait(6.2)
