class Clip1(Scene):
    """1.2.1 - Cuantizar es elegir el escalon mas cercano: 16 niveles, un
    paso de 0.125 y un error rojo que vive debajo. Con 8 bits el error se
    aplana y la SQNR de la senal entera pasa de 22.2 a 46.2 dB. (~36 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("La escalera y su error"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- una ventana corta, para que los escalones se vean ------------
        n_v = 200
        t_v, x_v = T_Q[:n_v], X_Q[:n_v]
        esc = Escalera(t_v, x_v, BITS_GRUESO, ancho=9.6, alto=2.5,
                       alto_err=0.95)
        esc.shift(UP * 0.45)

        self.play(FadeIn(esc.ejes), run_time=0.5)
        self.play(Create(esc.curva), run_time=2.0)
        self.wait(1.2)

        # --- los 16 niveles del conversor --------------------------------
        nivel_v, _ = cuantizar(x_v, BITS_GRUESO)
        rejilla = VGroup(*[
            DashedLine(esc.en(t_v[0], nv), esc.en(t_v[-1], nv),
                       color=C_MUESTRA, stroke_width=1.3, dash_length=0.07)
            for nv in nivel_v])
        rejilla.set_stroke(opacity=0.38)
        self.play(LaggedStart(*[Create(l) for l in rejilla], lag_ratio=0.05),
                  run_time=1.8)
        rot.mostrar(cifra_pie(f"paso = {fmt(PASO_GRUESO, 3)}"), zona="abajo",
                    run_time=0.5)
        self.wait(2.0)

        # --- la senal se apoya en el escalon mas cercano ------------------
        self.play(Create(esc.pasos), run_time=2.4)
        self.wait(1.4)

        # --- lo que sobra: el error --------------------------------------
        et_err = tag_junto(esc.error_caja, "error", LEFT, buff=0.18,
                           font_size=19, color=C_RUIDO)
        self.play(FadeIn(esc.error_caja), FadeIn(et_err), run_time=1.0)
        self.wait(1.6)

        panel = panel_cifras(f"bits = {BITS_GRUESO}",
                             f"niveles = {NIVELES_GRUESO}",
                             (f"paso = {fmt(PASO_GRUESO, 3)}", C_MUESTRA))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        # --- de 4 a 8 bits: el error se aplana en la MISMA escala ---------
        # (la caja de error de la gemela se autoescala a su propio paso;
        # para que el rojo se vea encoger se dibuja con `en_error` de esta)
        gem = esc.con_bits(BITS_MEDIO)
        err_fino = VMobject(color=C_RUIDO, stroke_width=2.0)
        err_fino.set_points_as_corners([esc.en_error(a, b) for a, b in
                                        zip(t_v, ERR_MEDIO[:n_v])])
        panel_2 = panel_cifras(f"bits = {BITS_MEDIO}",
                               f"niveles = {2 ** BITS_MEDIO}",
                               (f"paso = {fmt(PASO_MEDIO, 4)}", C_MUESTRA))

        self.play(FadeOut(rejilla), FadeOut(panel), run_time=0.6)
        rot.mostrar(cifra_pie(f"paso {fmt(PASO_GRUESO, 3)} -> "
                              f"{fmt(PASO_MEDIO, 4)}"), zona="abajo",
                    run_time=0.5)
        self.play(Transform(esc.pasos, gem.pasos),
                  Transform(esc.error_caja[1], err_fino),
                  FadeIn(panel_2), run_time=2.4)
        self.wait(3.0)

        # --- la cifra se mide sobre la senal ENTERA -----------------------
        esc_todo = Escalera(T_Q, X_Q, BITS_GRUESO, ancho=9.6, alto=2.5,
                            alto_err=0.95)
        esc_todo.shift(UP * 0.45)
        panel_3 = panel_cifras(f"bits = {BITS_GRUESO}",
                               f"niveles = {NIVELES_GRUESO}",
                               (f"paso = {fmt(PASO_GRUESO, 3)}", C_MUESTRA))
        rot.limpiar("abajo", run_time=0.5)
        self.play(FadeOut(esc.ejes), FadeOut(esc.curva), FadeOut(esc.pasos),
                  FadeOut(esc.error_caja), FadeOut(et_err), FadeOut(panel_2),
                  run_time=0.8)
        self.play(FadeIn(esc_todo.ejes), Create(esc_todo.curva),
                  run_time=1.6)
        self.play(Create(esc_todo.pasos), FadeIn(esc_todo.error_caja),
                  FadeIn(panel_3), run_time=2.0)
        self.wait(1.6)

        rot.mostrar(cifra_pie(f"SQNR {fmt(SQNR_GRUESO, 1)} -> "
                              f"{fmt(SQNR_MEDIO, 1)} dB"), zona="abajo",
                    run_time=0.5)
        self.wait(4.0)
