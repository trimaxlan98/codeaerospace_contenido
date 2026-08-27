class Clip3(Scene):
    """4.2.3 - El mismo resonador con el polo a tres radios: cuanto mas
    cerca del circulo, mas alto y mas estrecho el pico. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))
        rot.mostrar(titulo_curso("Acercar el polo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        r0, r1, r2 = RADIOS
        colores = {r0: C_SENAL, r1: C_SALIDA, r2: C_IDEAL}

        pz = plano_z(PZ[r0][0], PZ[r0][1], unidad=1.95, alcance=1.28)
        pz.move_to(LEFT * 3.95 + UP * 0.15)

        def _tags(r):
            d = float(por_distancias(*PZ[r], W0)[2].min())
            g = VGroup(tag_hud(f"r = {fmt(r, 2)}", font_size=22,
                               color=C_MUESTRA),
                       tag_hud(f"corta = {fmt(d, 3)}", font_size=20,
                               color=C_RUIDO))
            g.arrange(DOWN, buff=0.16)
            g.next_to(pz, DOWN, buff=0.20)
            return g

        et = _tags(r0)
        self.play(FadeIn(pz.ejes), FadeIn(pz.circulo), run_time=0.6)
        self.play(FadeIn(pz.polos), FadeIn(et), run_time=0.6)
        self.wait(0.8)

        # --- las tres respuestas comparten eje (gemelas de con_mag) --------
        piso = min(float(MAG[r].min()) for r in RADIOS) - 4.0
        techo = PICO[r2] + 4.0
        rf = respuesta_dibujo(W_EJE[r0], MAG[r0], ancho=5.0, alto=2.6,
                              piso_db=piso, techo_db=techo, color=colores[r0])
        rf.move_to(RIGHT * 4.0 + UP * 0.15)
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf.ejes, DOWN, buff=0.26)
        marca = rf.marca_w(W0)
        marca.set_stroke(opacity=0.5)
        self.play(FadeIn(rf.ejes), FadeIn(et_rf), FadeIn(marca),
                  run_time=0.5)
        self.play(Create(rf.curva), run_time=1.8)
        rot.mostrar(cifra_pie(f"pico {fmt(PICO[r0], 1)} dB "
                              f"ancho {fmt(ANCHO_3DB[r0], 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- el polo se acerca al circulo ---------------------------------
        for r in (r1, r2):
            gemela = pz.con_pz(PZ[r][0], PZ[r][1])
            self.play(Transform(pz, gemela), Transform(et, _tags(r)),
                      run_time=1.6)
            self.wait(0.8)
            curva = rf.con_mag(MAG[r], color=colores[r]).curva
            self.play(Create(curva), run_time=1.6)
            rot.mostrar(cifra_pie(f"pico {fmt(PICO[r], 1)} dB "
                                  f"ancho {fmt(ANCHO_3DB[r], 3)}"),
                        zona="abajo", run_time=0.5)
            self.wait(2.6)

        # --- las tres, juntas ----------------------------------------------
        panel = panel_cifras(
            *[(f"{fmt(r, 2)}: {fmt(PICO[r], 1)} dB", colores[r])
              for r in RADIOS])
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.4)

        # --- lo que mide "ancho": la banda por encima de -3 dB -------------
        def _banda(r):
            m = MAG[r]
            dentro = np.where(m > m.max() - 3.0)[0]
            return rf.banda(W_EJE[r][dentro[0]], W_EJE[r][dentro[-1]],
                            color=colores[r], opacidad=0.20)

        rot.mostrar(cifra_pie(f"ancho {fmt(ANCHO_3DB[r0], 3)} a "
                              f"{fmt(ANCHO_3DB[r2], 3)}"),
                    zona="abajo", run_time=0.5)
        banda = _banda(r0)
        self.play(FadeIn(banda), run_time=0.5)
        self.wait(2.0)
        self.play(Transform(banda, _banda(r2)), run_time=1.0)
        self.wait(3.0)
