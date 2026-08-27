class Clip1(Scene):
    """2.2.1 - La convolucion EN MARCHA: h volteada recorre x, los
    productos se encienden y y[n] crece tallo a tallo. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))
        rot.mostrar(titulo_curso("Deslizar y sumar"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        d = deslizador(X_CORTO, H_CORTO, ancho=6.8, alto=1.15,
                       separacion=1.45)
        d.shift(RIGHT * 0.9 + UP * 0.05)

        et_x = tag_junto(d.sx, "x[n]", LEFT, buff=0.28, font_size=20,
                         color=C_SENAL)
        et_p = tag_junto(d.sp, "productos", LEFT, buff=0.28, font_size=20,
                         color=C_CALCULO)
        et_y = tag_junto(d.sy, "y[n]", LEFT, buff=0.28, font_size=20,
                         color=C_SALIDA)

        # --- la entrada, quieta -------------------------------------------
        self.play(FadeIn(d.sx.ejes), FadeIn(et_x), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(d.sx.tallo(i)) for i in range(N_X)],
                              lag_ratio=0.06),
                  LaggedStart(*[FadeIn(d.sx.punto(i)) for i in range(N_X)],
                              lag_ratio=0.06), run_time=1.5)
        self.wait(0.7)

        # --- h llega en su orden natural y SE VOLTEA -----------------------
        nat = d.sh.con_valores(H_CORTO)
        et_h0 = tag_junto(nat, "h[n]", DOWN, buff=0.16, font_size=20,
                          color=C_MUESTRA)
        self.play(FadeIn(nat), FadeIn(et_h0), run_time=0.8)
        self.wait(0.9)

        rot.mostrar(formula_pie(r"y[n] = \sum_k x[k]\,h[n-k]"),
                    zona="abajo", run_time=0.5)
        self.wait(1.5)

        et_h = tag_junto(d.sh, "h volteada", DOWN, buff=0.16,
                         font_size=20, color=C_MUESTRA)
        self.play(Transform(nat, d.sh), run_time=1.3)
        self.play(FadeOut(et_h0), FadeIn(et_h), run_time=0.5)
        self.wait(1.0)
        # el relevo invisible: `nat` ya es identica a d.sh
        self.remove(nat)
        self.add(d.sh)

        # --- los dos carriles que se van a llenar --------------------------
        rot.mostrar(cifra_pie(f"{N_X} x {M_H} muestras"), zona="abajo",
                    run_time=0.5)
        self.play(FadeIn(d.sp.ejes), FadeIn(et_p), FadeIn(d.sy.ejes),
                  FadeIn(et_y), run_time=0.7)
        self.wait(0.5)

        # --- el deslizamiento ----------------------------------------------
        # El resalte y la marca son UN solo mobject que se TRANSFORMA en
        # su siguiente posicion: con FadeOut(previo) + FadeIn(nuevo) en la
        # misma animacion los dos rectangulos coexisten medio segundo, y
        # el frame muestreado enseña dos ventanas de solape a la vez.
        res = d.resalte(0)
        marca = d.marca_salida(0)
        for n in range(N_SALIDA):
            salto = d.paso_a(n)
            anims = [d.sh.animate.shift(salto), et_h.animate.shift(salto),
                     Transform(d.sp, d.productos_en(n)),
                     Transform(d.sy, d.salida_hasta(n))]
            if n == 0:
                anims += [FadeIn(res), FadeIn(marca)]
            else:
                anims += [Transform(res, d.resalte(n)),
                          Transform(marca, d.marca_salida(n))]
            self.play(*anims, run_time=1.5)

        self.play(FadeOut(res), FadeOut(marca), run_time=0.5)
        self.wait(1.2)

        # --- la salida entera, y su pico -----------------------------------
        pico = int(np.argmax(np.abs(Y_CORTO)))
        marca_pico = d.sy.marcar(pico, color=C_CALCULO)
        self.play(FadeIn(marca_pico), run_time=0.5)
        rot.mostrar(cifra_pie(f"y[{pico}] = {fmt(Y_CORTO[pico], 3)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        rot.mostrar(cifra_pie(f"{N_SALIDA} salidas calculadas"),
                    zona="abajo", run_time=0.5)
        self.wait(3.8)
