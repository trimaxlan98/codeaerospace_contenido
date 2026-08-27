class Clip2(Scene):
    """2.2.2 - La salida es mas larga que la entrada: N + M - 1. Los
    M-1 primeros y los M-1 ultimos son transitorios. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Longitud y bordes"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        sx = Secuencia(X_CORTO, 0, None, ancho=4.4, alto=1.3,
                       color=C_SENAL)
        sx.move_to(LEFT * 3.4 + UP * 1.75)
        sh = Secuencia(H_CORTO, 0, None, ancho=2.2, alto=1.3,
                       color=C_MUESTRA)
        sh.move_to(RIGHT * 3.0 + UP * 1.75)
        sy = Secuencia(Y_CORTO, 0, None, ancho=10.0, alto=2.0,
                       color=C_SALIDA, eje_y=False)
        sy.move_to(DOWN * 1.35)

        et_x = tag_junto(sx, "x[n]", UP, buff=0.12, font_size=20,
                         color=C_SENAL)
        et_h = tag_junto(sh, "h[n]", UP, buff=0.12, font_size=20,
                         color=C_MUESTRA)
        et_y = tag_junto(sy, "y[n]", LEFT, buff=0.24, font_size=20,
                         color=C_SALIDA)

        # --- lo que entra --------------------------------------------------
        self.play(FadeIn(sx.ejes), FadeIn(et_x), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sx.tallo(i)) for i in range(N_X)],
                              lag_ratio=0.07),
                  LaggedStart(*[FadeIn(sx.punto(i)) for i in range(N_X)],
                              lag_ratio=0.07), run_time=1.3)
        ll_x = llave(sx, f"N = {N_X}", DOWN, font_size=22, color=C_SENAL)
        self.play(FadeIn(ll_x), run_time=0.6)
        self.wait(0.6)

        self.play(FadeIn(sh.ejes), FadeIn(et_h), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sh.tallo(i)) for i in range(M_H)],
                              lag_ratio=0.09),
                  LaggedStart(*[FadeIn(sh.punto(i)) for i in range(M_H)],
                              lag_ratio=0.09), run_time=1.0)
        ll_h = llave(sh, f"M = {M_H}", DOWN, font_size=22, color=C_MUESTRA)
        self.play(FadeIn(ll_h), run_time=0.6)
        self.wait(1.0)

        # --- lo que sale ---------------------------------------------------
        rot.mostrar(formula_pie(r"N + M - 1"), zona="abajo", run_time=0.5)
        self.play(FadeIn(sy.ejes), FadeIn(et_y), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(sy.tallo(i))
                                for i in range(N_SALIDA)], lag_ratio=0.06),
                  LaggedStart(*[FadeIn(sy.punto(i))
                                for i in range(N_SALIDA)], lag_ratio=0.06),
                  run_time=1.6)
        self.wait(1.4)
        rot.mostrar(cifra_pie(f"salida = {N_SALIDA} muestras"),
                    zona="abajo", run_time=0.5)
        self.wait(2.2)

        # --- cuantas muestras solapan en cada extremo -----------------------
        vent, marca, cuenta = None, None, None
        for n in (0, M_H - 1, N_SALIDA - 1):
            ks = PASOS[n]["k"]
            nueva_v = sx.ventana(min(ks), max(ks), color=C_CALCULO)
            nueva_m = sy.marcar(n, color=C_CALCULO)
            texto = "producto" if len(ks) == 1 else "productos"
            nueva_c = tag_hud(f"{len(ks)} {texto}", font_size=20)
            nueva_c.next_to(sy.en(n, 0.0), DOWN, buff=0.52)
            anims = [FadeIn(nueva_v), FadeIn(nueva_m), FadeIn(nueva_c)]
            if vent is not None:
                anims += [FadeOut(vent), FadeOut(marca), FadeOut(cuenta)]
            self.play(*anims, run_time=0.8)
            self.wait(1.5)
            vent, marca, cuenta = nueva_v, nueva_m, nueva_c
        self.play(FadeOut(vent), FadeOut(marca), FadeOut(cuenta),
                  run_time=0.6)

        # --- las tres zonas -------------------------------------------------
        v_ini = sy.ventana(0, M_H - 2, color=C_MUESTRA, opacidad=0.16)
        v_med = sy.ventana(M_H - 1, M_H - 2 + N_LLENOS, color=C_SALIDA,
                           opacidad=0.16)
        v_fin = sy.ventana(N_SALIDA - M_H + 1, N_SALIDA - 1, color=C_IDEAL,
                           opacidad=0.16)
        t_ini = tag_junto(v_ini, "transitorio", UP, buff=0.12, font_size=19,
                          color=C_MUESTRA)
        t_med = tag_junto(v_med, "llenos", UP, buff=0.12, font_size=19,
                          color=C_SALIDA)
        t_fin = tag_junto(v_fin, "transitorio", UP, buff=0.12, font_size=19,
                          color=C_IDEAL)
        self.play(FadeIn(v_ini), FadeIn(t_ini), FadeIn(v_fin),
                  FadeIn(t_fin), run_time=0.9)
        rot.mostrar(cifra_pie(f"transitorio = {M_H - 1} muestras"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        self.play(FadeIn(v_med), FadeIn(t_med), run_time=0.9)
        rot.mostrar(cifra_pie(f"llenos = {N_LLENOS} muestras"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras(f"N = {N_X}", f"M = {M_H}",
                             (f"salida = {N_SALIDA}", C_SALIDA),
                             (f"llenos = {N_LLENOS}", C_SALIDA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(4.0)
