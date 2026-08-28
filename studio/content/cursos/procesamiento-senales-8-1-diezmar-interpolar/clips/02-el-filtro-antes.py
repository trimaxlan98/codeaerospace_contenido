class Clip2(Scene):
    """8.1.2 - El filtro antialias visto en frecuencia, y lo que cambia
    filtrar ANTES de diezmar: el alias de 2600 Hz se hunde bajo el piso.
    (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("El filtro va antes"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la respuesta del antialias -----------------------------------
        resp = RespuestaFrec(W_AA, MAG_AA, ancho=8.4, alto=2.1, piso_db=-90.0,
                             techo_db=6.0, color=C_SALIDA)
        resp.move_to(UP * 1.25)
        et_r = tag_hud("H antialias", font_size=18, color=C_TENUE)
        et_r.next_to(resp, UP, buff=0.16).align_to(resp, LEFT)
        self.play(FadeIn(resp.ejes), FadeIn(et_r), run_time=0.4)
        self.play(Create(resp.curva), run_time=1.3)
        self.wait(1.8)

        w_2600 = F_ALTA_M / (FS_M / 2.0) * np.pi
        marca = resp.marca_w(w_2600, color=C_RUIDO)
        punto = resp.punto(w_2600, color=C_RUIDO)
        self.play(Create(marca), FadeIn(punto), run_time=0.7)
        rot.mostrar(cifra_pie(f"{fmt(ATEN_AA, 1)} dB en {fmt(F_ALTA_M, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        panel = panel_cifras(f"orden = {ORDEN_AA} taps",
                             (f"corte = {fmt(FC_AA, 0)} Hz", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.0)

        grupo_resp = VGroup(resp.ejes, resp.curva, marca, punto, et_r)
        self.play(FadeOut(grupo_resp), FadeOut(panel), run_time=0.6)

        # --- los dos diezmados, mismo eje: gemelas -------------------------
        alias_ix = int(np.argmin(np.abs(F_EJE_D - F_ALIAS_M)))
        db_antes = float(DB_D[alias_ix])
        db_despues = float(DB_OK[alias_ix])

        ed = EspectroDoble(F_EJE_D, DB_D, piso_db=-90.0, ancho=8.6, alto=2.5,
                           color=C_BANDA)
        ed.move_to(DOWN * 0.55)
        et_e = tag_hud("sin filtro", font_size=19, color=C_RUIDO)
        et_e.next_to(ed, UP, buff=0.18).align_to(ed, LEFT)
        self.play(FadeIn(ed.ejes), FadeIn(et_e), run_time=0.4)
        self.play(Create(ed.curva), FadeIn(ed.area), run_time=1.3)
        marca_imp = ed.marca_f(F_ALIAS_M, color=C_RUIDO)
        et_imp = tag_hud("alias", font_size=18, color=C_RUIDO)
        et_imp.next_to(ed.en(F_ALIAS_M, 0.0), UP, buff=0.12)
        self.play(Create(marca_imp), FadeIn(et_imp), run_time=0.7)
        rot.mostrar(cifra_pie(f"{fmt(db_antes, 1)} dB antes"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        gemela = ed.con_db(DB_OK, color=C_SALIDA)
        self.play(Transform(ed.curva, gemela.curva),
                  Transform(ed.area, gemela.area),
                  FadeOut(marca_imp), FadeOut(et_imp), run_time=1.4)
        et_e2 = tag_hud("con filtro", font_size=19, color=C_SALIDA)
        et_e2.move_to(et_e.get_center())
        rot.mostrar(cifra_pie(f"{fmt(db_despues, 1)} dB despues"),
                    zona="abajo", run_time=0.5)
        self.play(Transform(et_e, et_e2), run_time=0.5)
        self.wait(9.0)
