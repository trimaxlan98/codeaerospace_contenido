class Clip2(Scene):
    """10.1.2 - El modulo de la analitica sigue la amplitud instantanea:
    envolvente medida contra la real, error rms medido en el interior
    (sin los 50 primeros ni los 50 ultimos, donde la transformada tiene
    borde). (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("La envolvente"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la señal modulada, como curva continua -------------------------
        caja = Secuencia(X_A, 0, (-1.65, 1.65), ancho=10.8, alto=2.6,
                         color=C_SENAL, eje_y=False)
        caja.move_to(UP * 0.55)
        n_ejes = np.arange(N_A)
        curva_x = caja.curva_de(n_ejes, X_A, color=C_SENAL, grosor=1.6)
        et_x = tag_hud("x[n]", font_size=19, color=C_SENAL)
        et_x.next_to(caja, LEFT, buff=0.24)
        self.play(FadeIn(caja.ejes), FadeIn(et_x), run_time=0.5)
        self.play(Create(curva_x), run_time=2.4)
        self.wait(2.0)

        # --- la envolvente real: la amplitud que trae la modulacion --------
        curva_real = caja.curva_de(n_ejes, ENV_REAL, color=C_IDEAL,
                                   grosor=4.6)
        self.play(Create(curva_real), run_time=1.8)
        self.wait(1.4)

        # --- la medida: |analitica|, encima, pegada a la real ---------------
        curva_medida = caja.curva_de(n_ejes, ENV_MEDIDA, color=C_CALCULO,
                                     grosor=2.0)
        # t = 0.46 cae en un MAXIMO de la envolvente (que son 3 Hz sobre
        # 1 s: maximos en 1/12, 5/12, 9/12) y el rotulo quedaba sobre la
        # curva. En t = 0.25 la envolvente esta en su minimo.
        i_et = int(0.25 * N_A)
        et_med = tag_hud("envolvente", font_size=18, color=C_CALCULO)
        et_med.move_to(caja.en(i_et, 1.5))
        self.play(Create(curva_medida), FadeIn(et_med), run_time=2.0)
        rot.mostrar(cifra_pie("practicamente pegadas"), zona="abajo",
                    run_time=0.5)
        self.wait(2.6)

        # --- el interior donde se mide, sin los bordes -----------------------
        marca_i0 = caja.vertical_en(50, color=C_TENUE)
        marca_i1 = caja.vertical_en(N_A - 50, color=C_TENUE)
        et_int = tag_hud("borde excluido", font_size=15, color=C_TENUE)
        et_int.next_to(marca_i0, DOWN, buff=0.14)
        self.play(FadeIn(marca_i0), FadeIn(marca_i1), FadeIn(et_int),
                  run_time=0.8)
        rot.mostrar(cifra_pie(f"error rms {fmt(ERR_ENV, 4)}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.0)

        panel = panel_cifras(f"modulacion {fmt(F_MOD, 0)} Hz",
                             (f"error rms {fmt(ERR_ENV, 4)}", C_CALCULO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.8)
        rot.mostrar(formula_pie(r"A(t) = |x_a(t)|"), zona="abajo",
                    run_time=0.5)
        self.wait(6.6)
