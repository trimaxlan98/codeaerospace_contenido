class Clip3(Scene):
    """1.1.3 - fs=300: las copias se solapan. El modo de 220 Hz reaparece
    en 80 Hz y la reconstruccion miente. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Cuando las copias se tocan"),
                    zona="arriba", run_time=0.6)
        self.wait(0.3)

        f_eje, db_800 = replicas(F_BASE, DB_BASE, FS, f_max=1000.0)
        _, db_300 = replicas(F_BASE, DB_BASE, FS_MALA, f_max=1000.0)
        ed = EspectroDoble(f_eje, db_800, piso_db=-60.0, ancho=11.4,
                           alto=2.4, color=C_BANDA)
        ed.move_to(UP * 1.28)
        marca_fs = ed.marca_f(FS, color=C_MUESTRA)
        et_fs = tag_hud(f"fs = {fmt(FS, 0)} Hz", font_size=20,
                        color=C_MUESTRA)
        et_fs.next_to(ed.en(FS, 0.0), UP, buff=0.14)
        self.play(FadeIn(ed), FadeIn(marca_fs), FadeIn(et_fs), run_time=0.9)
        self.wait(1.6)

        # --- bajar el muestreo: las copias se acercan ---------------------
        gem = ed.con_db(db_300)
        marca_fs2 = ed.marca_f(FS_MALA, color=C_MUESTRA)
        et_fs2 = tag_hud(f"fs = {fmt(FS_MALA, 0)} Hz", font_size=20,
                         color=C_MUESTRA)
        et_fs2.next_to(ed.en(FS_MALA, 0.0), UP, buff=0.14)
        self.play(Transform(ed.curva, gem.curva),
                  Transform(ed.area, gem.area),
                  Transform(marca_fs, marca_fs2),
                  Transform(et_fs, et_fs2), run_time=2.4)
        self.wait(2.0)

        zona = ed.banda(FS_MALA - BANDA, BANDA, color=C_RUIDO, opacidad=0.26)
        self.play(FadeIn(zona), run_time=0.7)
        rot.mostrar(cifra_pie(f"solape = {fmt(SOLAPE_MALO, 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        # --- lo mismo, visto en el tiempo ---------------------------------
        n_t = 24
        tk_t = np.arange(n_t) / FS_MALA
        x_t = np.sin(2 * np.pi * F_ALTA * tk_t)
        sec = Secuencia(x_t, 0, (-1.25, 1.25), ancho=8.6, alto=1.9,
                        color=C_MUESTRA)
        sec.move_to(DOWN * 1.72)
        t_den = np.linspace(0.0, (n_t - 1) / FS_MALA, 800)
        c_alta = sec.curva_de(t_den * FS_MALA,
                              np.sin(2 * np.pi * F_ALTA * t_den),
                              color=C_SENAL, grosor=2.4)
        et_alta = tag_hud(f"{fmt(F_ALTA, 0)} Hz", font_size=19,
                          color=C_SENAL)
        et_alta.next_to(sec.en(1.0, 1.25), UP, buff=0.08)
        self.play(FadeIn(sec.ejes), Create(c_alta), FadeIn(et_alta),
                  run_time=1.6)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(n_t)],
                              lag_ratio=0.05),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(n_t)],
                              lag_ratio=0.05), run_time=1.8)
        self.wait(1.8)

        c_alias = sec.curva_de(t_den * FS_MALA,
                               -np.sin(2 * np.pi * F_ALIAS * t_den),
                               color=C_RUIDO, grosor=2.6)
        et_alias = tag_hud(f"parece {fmt(F_ALIAS, 0)} Hz", font_size=19,
                           color=C_RUIDO)
        et_alias.next_to(sec.en(23.5, 0.55), RIGHT, buff=0.18)
        self.play(c_alta.animate.set_stroke(opacity=0.22), run_time=0.6)
        self.play(Create(c_alias), FadeIn(et_alias), run_time=1.8)
        self.wait(2.4)

        rot.mostrar(cifra_pie(f"{fmt(F_ALTA, 0)} Hz -> "
                              f"{fmt(F_ALIAS, 0)} Hz"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras(
            (f"{fmt(FS_MALA, 0)} Hz: error {fmt(ERR_MALA, 3)}", C_RUIDO),
            (f"{fmt(FS, 0)} Hz: error {fmt(ERR_BIEN, 3)}", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
