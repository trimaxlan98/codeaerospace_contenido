class Clip2(Scene):
    """5.1.2 - Cortar la sinc deja una oreja junto a la transicion, y esa
    oreja NO se va por mucho orden que se le eche. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 05"))
        rot.mostrar(titulo_curso("La oreja de Gibbs"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        w20, m20, _ = respuesta_frec(H_ORDEN[20], [1.0], 2048)
        rf = respuesta_dibujo(w20, m20, ancho=9.6, alto=3.4, piso_db=-60.0,
                              techo_db=8.0, color=C_SALIDA)
        rf.move_to(DOWN * 0.35)
        et_w = tag_hud("w / pi", font_size=18, color=C_TENUE)
        et_w.next_to(rf.en(np.pi, -60.0), DR, buff=0.10)
        cero = rf.en(0.0, 0.0)
        linea_0 = DashedLine(cero, rf.en(np.pi, 0.0), color=C_TENUE,
                             stroke_width=1.2, dash_length=0.06)
        self.play(FadeIn(rf), FadeIn(et_w), FadeIn(linea_0), run_time=1.0)
        rot.mostrar(cifra_pie(f"orden = 20"), zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- la oreja ------------------------------------------------------
        lupa = Circle(radius=0.42, color=C_RUIDO, stroke_width=2.0)
        lupa.move_to(rf.en(F_SOBREPICO * np.pi, SOBREPICO[20]))
        et_ore = tag_hud(f"{SOBREPICO[20]:+.2f} dB", font_size=19,
                         color=C_RUIDO)
        et_ore.next_to(lupa, UP, buff=0.14)
        self.play(Create(lupa), FadeIn(et_ore), run_time=0.9)
        self.wait(2.4)

        # --- subir el orden: la transicion mejora, la oreja no -------------
        for o in (40, 80, 160):
            w, m, _ = respuesta_frec(H_ORDEN[o], [1.0], 2048)
            gem = rf.con_mag(m)
            et_o = tag_hud(f"{SOBREPICO[o]:+.2f} dB", font_size=19,
                           color=C_RUIDO)
            nueva_lupa = Circle(radius=0.42, color=C_RUIDO, stroke_width=2.0)
            nueva_lupa.move_to(rf.en(gibbs_db(H_ORDEN[o], FC, FS_D)[1]
                                     * np.pi, SOBREPICO[o]))
            et_o.next_to(nueva_lupa, UP, buff=0.14)
            rot.mostrar(cifra_pie(f"orden = {o}"), zona="abajo",
                        run_time=0.45)
            self.play(Transform(rf.curva, gem.curva),
                      Transform(lupa, nueva_lupa),
                      Transform(et_ore, et_o), run_time=1.3)
            self.wait(1.9)

        panel = panel_cifras(*[(f"{o}: {SOBREPICO[o]:+.2f} dB",
                                C_RUIDO if o > 20 else C_TENUE)
                               for o in ORDENES])
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)
        rot.mostrar(cifra_pie(f"atenuacion {fmt(ATEN_ORDEN[20], 1)} -> "
                              f"{fmt(ATEN_ORDEN[160], 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.2)
