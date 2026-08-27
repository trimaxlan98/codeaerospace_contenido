class Clip2(Scene):
    """1.1.2 - Muestrear COPIA el espectro cada fs. La banda base y sus
    replicas, con la guarda medida. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El espectro se repite"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        f_eje, db_base = replicas(F_BASE, DB_BASE, FS, f_max=1000.0,
                                  copias=(0,))
        _, db_todo = replicas(F_BASE, DB_BASE, FS, f_max=1000.0)
        ed = EspectroDoble(f_eje, db_base, piso_db=-60.0, ancho=11.4,
                           alto=2.7, color=C_BANDA)
        ed.move_to(DOWN * 0.30)
        et_f = tag_hud("Hz", font_size=20, color=C_TENUE)
        et_f.next_to(ed.en(1000.0, -60.0), RIGHT, buff=0.14)
        cero = tag_hud("0", font_size=19, color=C_TENUE)
        cero.next_to(ed.en(0.0, -60.0), DOWN, buff=0.16)

        self.play(FadeIn(ed.ejes), FadeIn(et_f), FadeIn(cero), run_time=0.6)
        self.play(Create(ed.curva), FadeIn(ed.area), run_time=2.0)
        self.wait(1.6)

        # --- lo que ocupa la senal ----------------------------------------
        borde = ed.marca_f(BANDA, color=C_CALCULO)
        borde_izq = ed.marca_f(-BANDA, color=C_CALCULO)
        self.play(Create(borde), Create(borde_izq), run_time=0.9)
        rot.mostrar(cifra_pie(f"banda = {fmt(BANDA, 1)} Hz"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- aparecen las copias ------------------------------------------
        gem = ed.con_db(db_todo)
        marca_fs = ed.marca_f(FS, color=C_MUESTRA)
        marca_fs_i = ed.marca_f(-FS, color=C_MUESTRA)
        et_fs = tag_hud(f"fs = {fmt(FS, 0)} Hz", font_size=20,
                        color=C_MUESTRA)
        et_fs.next_to(ed.en(FS, 0.0), UP, buff=0.16)
        self.play(Transform(ed.curva, gem.curva),
                  Transform(ed.area, gem.area),
                  Create(marca_fs), Create(marca_fs_i), FadeIn(et_fs),
                  run_time=2.2)
        self.wait(2.4)

        rot.mostrar(formula_pie(r"X_s(f) = \sum_k X(f - k\,f_s)"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- la guarda ----------------------------------------------------
        hueco = ed.banda(BANDA, FS - BANDA, color=C_SALIDA, opacidad=0.20)
        et_g = tag_junto(hueco, "guarda", UP, buff=0.10, font_size=20,
                         color=C_SALIDA)
        self.play(FadeIn(hueco), FadeIn(et_g), run_time=0.9)
        self.wait(1.8)
        rot.mostrar(cifra_pie(f"guarda = {fmt(GUARDA_OK, 1)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras(f"fs = {fmt(FS, 0)} Hz",
                             f"banda = {fmt(BANDA, 1)} Hz",
                             (f"guarda = {fmt(GUARDA_OK, 1)} Hz", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)
        rot.mostrar(formula_pie(r"f_s > 2\,B"), zona="abajo", run_time=0.5)
        self.wait(4.2)
