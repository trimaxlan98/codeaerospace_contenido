class Clip3(Scene):
    """6.1.3 - Al MISMO orden 8, cada dB de atenuacion se paga con rizado, y
    el pago se ve en los polos: cuanto mas cerca del filo, mas dB. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("Las tres familias"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        COLOR = {"butter": C_IDEAL, "cheby1": C_MUESTRA, "elip": C_SALIDA}
        POL = {k: zpk(*FILTROS[k])[1] for k in FAMILIAS}

        # --- el cuadro comun: mismo eje, mismas bandas -------------------
        w0, m0, _ = RESP["butter"]
        rf = respuesta_dibujo(w0, m0, ancho=7.6, alto=3.0, piso_db=-80.0,
                              techo_db=8.0, color=COLOR["butter"])
        rf.move_to(LEFT * 3.05 + DOWN * 1.05)
        banda_p = rf.banda(0.0, F_PASO * np.pi, color=C_SALIDA,
                           opacidad=0.10)
        banda_r = rf.banda(F_RECHAZO * np.pi, np.pi, color=C_RUIDO,
                           opacidad=0.10)
        nivel = DashedLine(rf.en(0.0, -ATEN_PEDIDA),
                           rf.en(np.pi, -ATEN_PEDIDA), color=C_DATO,
                           stroke_width=1.4, dash_length=0.07)
        et_niv = tag_hud(f"-{fmt(ATEN_PEDIDA, 0)} dB", font_size=18,
                         color=C_DATO)
        et_niv.next_to(rf.en(0.05 * np.pi, -ATEN_PEDIDA), RIGHT,
                       buff=0.10).shift(UP * 0.24)
        et_w = tag_hud("w / pi", font_size=18, color=C_TENUE)
        et_w.next_to(rf.en(np.pi, -80.0), RIGHT, buff=0.20)
        self.play(FadeIn(rf.ejes), FadeIn(banda_p), FadeIn(banda_r),
                  FadeIn(et_w), run_time=0.7)
        self.play(Create(nivel), FadeIn(et_niv), run_time=0.7)

        # --- el mismo orden 8, visto por sus polos ------------------------
        pz = plano_z((), POL["butter"], unidad=1.06, alcance=1.22)
        pz.move_to(RIGHT * 4.30 + DOWN * 0.85)

        def _marcas(pol):
            """Las X de los polos, encogidas: a radio 0.994 una X de tamano
            normal cruza el circulo y se leeria como inestable."""
            g = pz.con_pz((), pol).polos
            for m in g:
                m.scale(0.62)
            return g

        for _m in pz.polos:
            _m.scale(0.62)
        et_pz = tag_hud("plano z", font_size=18, color=C_TENUE)
        et_pz.next_to(pz, DOWN, buff=0.16)
        et_rad = tag_hud(f"polos a {fmt(RADIO_MAX['butter'], 3)}",
                         font_size=19, color=COLOR["butter"])
        et_rad.next_to(pz, UP, buff=0.20)
        self.play(FadeIn(pz), FadeIn(et_pz), run_time=0.7)
        self.wait(0.8)

        # --- butter: plano, pero flojo ------------------------------------
        rot.mostrar(cifra_pie(f"butter {fmt(ATEN['butter'], 1)} dB",
                              color=COLOR["butter"]), zona="abajo",
                    run_time=0.5)
        self.play(Create(rf.curva), run_time=1.6)
        self.play(FadeIn(et_rad), run_time=0.5)
        self.wait(2.4)

        curvas = {"butter": rf.curva}
        for k in ("cheby1", "elip"):
            w, m, _ = RESP[k]
            gem = rf.con_mag(m, color=COLOR[k])
            nuevo_rad = tag_hud(f"polos a {fmt(RADIO_MAX[k], 3)}",
                                font_size=19, color=COLOR[k])
            nuevo_rad.move_to(et_rad.get_center())
            rot.mostrar(cifra_pie(f"{k} {fmt(ATEN[k], 1)} dB",
                                  color=COLOR[k]), zona="abajo",
                        run_time=0.5)
            self.play(*[c.animate.set_stroke(opacity=0.38)
                        for c in curvas.values()], run_time=0.4)
            self.play(Create(gem.curva), run_time=1.6)
            self.add(gem.curva)
            curvas[k] = gem.curva
            self.play(Transform(pz.polos, _marcas(POL[k])),
                      Transform(et_rad, nuevo_rad), run_time=1.1)
            self.add(et_pz)
            self.wait(2.5)

        # --- el rizado: lo que cuesta cada dB -----------------------------
        panel = panel_cifras(*[(f"{k} {fmt(ATEN[k], 1)} dB riz "
                                f"{fmt(RIZADO[k], 3)}", COLOR[k])
                               for k in FAMILIAS])
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        # el eliptico riza en las DOS bandas
        lupa = VGroup(*[SurroundingRectangle(b, color=COLOR["elip"],
                                            stroke_width=2.0, buff=0.02)
                        for b in (banda_p, banda_r)])
        self.play(Create(lupa), run_time=0.8)
        rot.mostrar(cifra_pie(f"elip riza {fmt(RIZADO['elip'], 3)} dB",
                              color=COLOR["elip"]), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        self.play(FadeOut(lupa), run_time=0.4)
        rot.mostrar(cifra_pie(f"elip: polos a "
                              f"{fmt(RADIO_MAX['elip'], 3)}",
                              color=COLOR["elip"]), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)
