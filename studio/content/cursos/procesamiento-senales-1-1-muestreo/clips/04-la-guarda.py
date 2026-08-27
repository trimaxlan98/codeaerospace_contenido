class Clip4(Scene):
    """1.1.4 - El antialias recorta ANTES de muestrear: el solape cae 31
    dB y se paga con banda. Cierre de la leccion. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La banda de guarda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        f_eje, db_300 = replicas(F_BASE, DB_BASE, FS_MALA, f_max=1000.0)
        _, db_300_aa = replicas(F_BASE, DB_AA, FS_MALA, f_max=1000.0)
        _, db_base = replicas(F_BASE, DB_BASE, FS_MALA, f_max=1000.0,
                              copias=(0,))
        _, db_base_aa = replicas(F_BASE, DB_AA, FS_MALA, f_max=1000.0,
                                 copias=(0,))
        ed = EspectroDoble(f_eje, db_base, piso_db=-60.0, ancho=11.4,
                           alto=2.7, color=C_BANDA)
        ed.move_to(DOWN * 0.30)
        self.play(FadeIn(ed), run_time=0.8)
        self.wait(1.2)

        # --- el filtro, dibujado sobre el mismo eje -----------------------
        resp = butter_db(f_eje, FC_AA, ORDEN_AA)
        curva_h = VMobject(color=C_IDEAL, stroke_width=3.0)
        curva_h.set_points_as_corners([ed.en(f, d) for f, d in
                                       zip(f_eje, resp)])
        et_h = tag_junto(curva_h, "antialias", UP, buff=0.12, font_size=20,
                         color=C_IDEAL)
        et_h.next_to(ed.en(-620.0, -14.0), UP, buff=0.10)
        self.play(Create(curva_h), FadeIn(et_h), run_time=1.8)
        self.wait(1.6)

        marca_alta = ed.marca_f(F_ALTA, color=C_RUIDO)
        et_aten = tag_hud(f"H({fmt(F_ALTA, 0)} Hz) = {fmt(ATEN_AA, 1)} dB",
                          font_size=20, color=C_IDEAL)
        et_aten.next_to(ed.en(F_ALTA, 0.0), UR, buff=0.10)
        self.play(Create(marca_alta), FadeIn(et_aten), run_time=1.0)
        self.wait(2.4)

        # --- la banda base se recorta -------------------------------------
        gem_base = ed.con_db(db_base_aa)
        self.play(Transform(ed.curva, gem_base.curva),
                  Transform(ed.area, gem_base.area), run_time=1.8)
        self.wait(2.0)

        # --- y ahora si, muestrear a 300 ----------------------------------
        self.play(FadeOut(curva_h), FadeOut(et_h), FadeOut(et_aten),
                  FadeOut(marca_alta), run_time=0.7)
        gem_rep = ed.con_db(db_300_aa)
        marca_fs = ed.marca_f(FS_MALA, color=C_MUESTRA)
        et_fs = tag_hud(f"fs = {fmt(FS_MALA, 0)} Hz", font_size=20,
                        color=C_MUESTRA)
        et_fs.next_to(ed.en(FS_MALA, 0.0), UP, buff=0.14)
        self.play(Transform(ed.curva, gem_rep.curva),
                  Transform(ed.area, gem_rep.area),
                  Create(marca_fs), FadeIn(et_fs), run_time=2.0)
        self.wait(2.2)

        rot.mostrar(cifra_pie(f"solape {fmt(SOLAPE_MALO, 1)} -> "
                              f"{fmt(SOLAPE_AA, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.2)

        # --- lo que cuesta -------------------------------------------------
        util = banda_ocupada(F_BASE, DB_AA, -40.0)
        panel = panel_cifras((f"banda util = {fmt(util, 0)} Hz", C_RUIDO),
                             (f"antes = {fmt(BANDA, 0)} Hz", C_TENUE))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)

        cierre_leccion(self, rot, "Muestrear no pierde nada.",
                       "Si el espectro cabe entre replicas.",
                       ed, marca_fs, et_fs, panel)
