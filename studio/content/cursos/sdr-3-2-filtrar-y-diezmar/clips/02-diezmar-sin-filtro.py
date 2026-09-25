class Clip2(Scene):
    """3.2.2 - Diezmar sin filtro: un tono deseado en -40 kHz y una vecina
    del mismo nivel en +500 kHz; al diezmar por 10 sin filtrar, la vecina se
    pliega dentro del canal, en +20 kHz, tan fuerte como el. Con filtro,
    desaparece. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Diezmar sin filtro"), zona="arriba",
                    run_time=0.6)
        self.wait(0.5)

        # --- el escenario: canal deseado + vecina, mismo nivel -------------
        n = 1 << 16
        x = S.tono(-40e3, FS, n) + S.tono(500e3, FS, n)
        nfft = 2048
        f_antes, db_antes = S.espectro_db(x, FS, nfft=nfft)
        fr_a, dbr_a = S.para_dibujar(f_antes, db_antes, 900, -1.2e6, 1.2e6)

        esp_a = S.Espectro(fr_a, dbr_a, piso=-60.0, techo=4.0, ancho=11.6,
                           alto=4.0, color=C_TENUE)
        esp_a.move_to(UP * 0.2)
        ticks_a = esp_a.marcas([-1.2e6, -0.6e6, 0.0, 0.6e6, 1.2e6],
                               ["-1200", "-600", "0", "600", "1200"])
        u_a = tag_junto(ticks_a[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp_a.ejes), FadeIn(ticks_a), FadeIn(u_a),
                  run_time=0.8)
        self.play(Create(esp_a.curva), FadeIn(esp_a.area), run_time=1.6)
        self.wait(0.8)

        m_can = esp_a.marca_f(-40e3, color=C_SENAL)
        t_can = tag_junto(m_can, "canal", UP, buff=0.16, font_size=20,
                          color=C_SENAL)
        m_vec = esp_a.marca_f(500e3, color=C_RUIDO)
        t_vec = tag_junto(m_vec, "vecina", UP, buff=0.16, font_size=20,
                          color=C_RUIDO)
        self.play(Create(m_can), FadeIn(t_can), Create(m_vec), FadeIn(t_vec),
                  run_time=0.9)
        self.wait(2.4)

        grupo_a = VGroup(esp_a, ticks_a, u_a, m_can, t_can, m_vec, t_vec)
        self.play(FadeOut(grupo_a), run_time=0.7)
        self.wait(0.2)

        # --- diezmar por 10 sin filtro: la vecina se pliega en +20 kHz -----
        y_sin = S.diezmar(x, 10)
        fs2 = FS / 10
        f_desp, db_sin = S.espectro_db(y_sin, fs2, nfft=nfft)
        fr_d, dbr_sin = S.para_dibujar(f_desp, db_sin, 900, -120e3, 120e3)

        esp_d = S.Espectro(fr_d, dbr_sin, piso=-60.0, techo=4.0, ancho=11.6,
                           alto=4.0, color=C_SENAL)
        esp_d.move_to(UP * 0.2)
        ticks_d = esp_d.marcas([-120e3, -60e3, 0.0, 60e3, 120e3],
                               ["-120", "-60", "0", "60", "120"])
        u_d = tag_junto(ticks_d[-1], "kHz", RIGHT, buff=0.2, font_size=20)
        self.play(Create(esp_d.ejes), FadeIn(ticks_d), FadeIn(u_d),
                  run_time=0.7)
        self.play(Create(esp_d.curva), FadeIn(esp_d.area), run_time=1.6)
        self.wait(0.8)

        m_pleg = esp_d.marca_f(F_PLEG, color=C_RUIDO)
        t_pleg = tag_junto(m_pleg, "vecina plegada", UP, buff=0.16,
                           font_size=20, color=C_RUIDO)
        self.play(Create(m_pleg), FadeIn(t_pleg), run_time=0.8)
        self.wait(1.6)
        rot.mostrar(cifra_pie(f"{fmt(FUGA_SIN, 1)} dBc: igual de fuerte"),
                    zona="abajo", run_time=0.5)
        self.wait(4.4)

        # --- con filtro, la vecina plegada desaparece -----------------------
        h_canal = S.fir_paso_bajo(N_TAPS, 100e3, FS)
        y_con = S.diezmar(x, 10, h_canal)
        _, db_con = S.espectro_db(y_con, fs2, nfft=nfft)
        _, dbr_con = S.para_dibujar(f_desp, db_con, 900, -120e3, 120e3)

        esp_c = esp_d.con_db(dbr_con, color=C_SENAL)
        self.play(Transform(esp_d.curva, esp_c.curva),
                  Transform(esp_d.area, esp_c.area),
                  FadeOut(m_pleg), FadeOut(t_pleg), run_time=1.8)
        self.wait(1.2)
        rot.mostrar(cifra_pie(f"menos de {FUGA_TECHO} dBc"), zona="abajo",
                    run_time=0.5)
        self.wait(6.2)
