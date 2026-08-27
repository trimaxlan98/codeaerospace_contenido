class Clip3(Scene):
    """1.3.3 - Sobremuestrear aleja las imagenes: el MISMO filtro de
    reconstruccion pasa de -11.7 dB a -39.9 dB de atenuacion. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("Alejar las imagenes"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        f_max = FS_OSR
        f_eje, db_800 = replicas(F_BASE, DB_BASE, FS, f_max=f_max)
        _, db_osr = replicas(F_BASE, DB_BASE, FS_OSR, f_max=f_max)
        ed = EspectroDoble(f_eje, db_800, piso_db=-60.0, ancho=11.2,
                           alto=2.6, color=C_BANDA)
        ed.move_to(DOWN * 0.55)
        self.play(FadeIn(ed), run_time=0.9)
        self.wait(1.8)

        # --- el filtro de reconstruccion, fijo -------------------------------
        resp = butter_db(f_eje, FC_REC, ORDEN_REC)
        curva_h = VMobject(color=C_IDEAL, stroke_width=3.0)
        curva_h.set_points_as_corners([ed.en(f, d) for f, d in
                                       zip(f_eje, resp)])
        # tag_hud: tag_junto con dos palabras pierde el hueco del espacio
        # en Rajdhani ("filtrofijo"); Space Mono si lo dibuja.
        et_h = tag_hud("filtro fijo", font_size=19, color=C_IDEAL)
        et_h.next_to(ed, UP, buff=0.18)
        self.play(Create(curva_h), FadeIn(et_h), run_time=1.6)
        self.wait(1.8)
        self.play(FadeOut(et_h), run_time=0.4)

        marca_im = ed.marca_f(F_IMAGEN, color=C_RUIDO)
        punto_im = Dot(ed.en(F_IMAGEN, ATEN_IMAGEN), color=C_RUIDO,
                       radius=0.075)
        et_im = tag_hud(f"{fmt(F_IMAGEN, 0)} Hz", font_size=19,
                        color=C_RUIDO)
        et_im.next_to(ed.en(F_IMAGEN, 0.0), UP, buff=0.12)
        self.play(Create(marca_im), FadeIn(punto_im), FadeIn(et_im),
                  run_time=1.0)
        self.wait(2.0)

        rot.mostrar(cifra_pie(f"{fmt(F_IMAGEN, 0)} Hz = "
                              f"{fmt(ATEN_IMAGEN, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)

        # --- sobremuestrear x4: la imagen se aleja ----------------------------
        gem = ed.con_db(db_osr)
        marca_osr = ed.marca_f(F_IMAGEN_OSR, color=C_SALIDA)
        punto_osr = Dot(ed.en(F_IMAGEN_OSR, ATEN_IMAGEN_OSR), color=C_SALIDA,
                        radius=0.075)
        et_osr = tag_hud(f"{fmt(F_IMAGEN_OSR, 0)} Hz", font_size=19,
                         color=C_SALIDA)
        et_osr.next_to(ed.en(F_IMAGEN_OSR, 0.0), UP, buff=0.12)
        self.play(FadeOut(marca_im), FadeOut(punto_im), FadeOut(et_im),
                  run_time=0.5)
        self.play(Transform(ed.curva, gem.curva),
                  Transform(ed.area, gem.area), Create(marca_osr),
                  FadeIn(punto_osr), FadeIn(et_osr), run_time=2.4)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"{fmt(F_IMAGEN_OSR, 0)} Hz = "
                              f"{fmt(ATEN_IMAGEN_OSR, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(3.8)

        panel = panel_cifras((f"x1: {fmt(ATEN_IMAGEN, 1)} dB", C_RUIDO),
                             (f"x4: {fmt(ATEN_IMAGEN_OSR, 1)} dB", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.6)
