class Clip1(Scene):
    """8.1.1 - Quedarse con 1 de cada 4 muestras sin filtrar: el tono de
    2600 Hz que ya no cabe reaparece en 600 Hz. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("Tirar muestras"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la señal: dos tonos, en el tiempo -----------------------------
        n_ver = 64
        sec = Secuencia(X_M[:n_ver], 0, (-1.7, 1.7), ancho=10.4, alto=1.85,
                        color=C_MUESTRA, radio=0.045)
        sec.move_to(UP * 2.35)
        self.play(FadeIn(sec.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(n_ver)],
                              lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(n_ver)],
                              lag_ratio=0.02), run_time=1.6)
        rot.mostrar(cifra_pie(f"{fmt(F_BAJA, 0)} Hz y {fmt(F_ALTA_M, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(2.8)

        # --- su espectro: el tono alto SI cabe ------------------------------
        ed1 = EspectroDoble(F_EJE_M, DB_M, piso_db=-60.0, ancho=5.4, alto=2.0,
                            color=C_BANDA)
        ed1.move_to(DOWN * 1.55 + LEFT * 3.35)
        marca_baja = ed1.marca_f(F_BAJA, color=C_MUESTRA)
        marca_alta = ed1.marca_f(F_ALTA_M, color=C_MUESTRA)
        et_o = tag_hud("original", font_size=18, color=C_TENUE)
        et_o.next_to(ed1, UP, buff=0.16).align_to(ed1, LEFT)
        self.play(FadeIn(ed1.ejes), FadeIn(et_o), run_time=0.4)
        self.play(Create(ed1.curva), FadeIn(ed1.area), run_time=1.4)
        self.play(Create(marca_baja), Create(marca_alta), run_time=0.7)
        self.wait(2.0)

        # --- se queda 1 de cada 4: los que sobreviven, marcados -------------
        vivos = [i for i in range(n_ver) if i % M_DIEZ == 0]
        marcas = VGroup(*[sec.marcar(i, color=C_CALCULO) for i in vivos])
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.08),
                  run_time=1.4)
        rot.mostrar(cifra_pie(f"1 de {M_DIEZ} muestras"), zona="abajo",
                    run_time=0.5)
        self.wait(2.8)

        self.play(FadeOut(sec.ejes), FadeOut(sec.tallos), FadeOut(sec.puntos),
                  FadeOut(marcas), run_time=0.6)

        # --- el segundo espectro: el impostor --------------------------------
        ed2 = EspectroDoble(F_EJE_D, DB_D, piso_db=-60.0, ancho=5.4, alto=2.0,
                            color=C_BANDA)
        ed2.move_to(DOWN * 1.55 + RIGHT * 3.35)
        et_d = tag_hud("diezmado", font_size=18, color=C_TENUE)
        et_d.next_to(ed2, UP, buff=0.16).align_to(ed2, LEFT)
        self.play(FadeIn(ed2.ejes), FadeIn(et_d), run_time=0.4)
        self.play(Create(ed2.curva), FadeIn(ed2.area), run_time=1.4)
        self.wait(1.6)

        marca_impostor = ed2.marca_f(F_ALIAS_M, color=C_RUIDO)
        et_imp = tag_hud("alias", font_size=19, color=C_RUIDO)
        et_imp.next_to(ed2.en(F_ALIAS_M, 0.0), UP, buff=0.14)
        self.play(Create(marca_impostor), FadeIn(et_imp), run_time=0.8)
        rot.mostrar(cifra_pie(f"alias en {fmt(F_ALIAS_M, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        panel = panel_cifras(f"fs = {fmt(FS_M, 0)} Hz",
                             (f"fs nueva = {fmt(FS_NUEVA, 0)} Hz", C_SALIDA),
                             (f"alias = {fmt(F_ALIAS_M, 0)} Hz", C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(6.6)
