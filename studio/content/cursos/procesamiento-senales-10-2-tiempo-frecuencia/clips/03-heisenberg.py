class Clip3(Scene):
    """10.2.3 - Los dos espectrogramas de la misma señal, ventana 64 y
    ventana 256. La celda cambia de forma; su AREA, no: el producto vale
    1.00 en los dos. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 10"))
        rot.mostrar(titulo_curso("Heisenberg, en cifras"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        n_c, n_l = NPER          # 64 (corta) y 256 (larga)

        # La frecuencia del golpe, medida en la malla: la columna de su
        # instante contra una columna anterior sin el.
        j_g = int(np.argmin(np.abs(T_S[n_l] - T_GOLPE)))
        f_golpe = float(F_S[n_l][int(np.argmax(S_DB[n_l][:, j_g]
                                               - S_DB[n_l][:, j_g - 3]))])

        # --- las dos mallas ------------------------------------------------
        # Mismo k en los DOS ejes: es lo unico que conserva la FORMA de la
        # celda, que es justamente lo que compara este clip.
        k = 3
        piezas, tags, cifras = {}, {}, {}
        for n, lado in ((n_c, LEFT), (n_l, RIGHT)):
            esp = Espectrograma(T_S[n][::k], F_S[n][::k],
                                S_DB[n][::k, ::k], ancho=5.5, alto=2.8,
                                piso_db=-60.0)
            esp.move_to(lado * 3.3 + UP * 0.30)
            piezas[n] = esp
            t = tag_hud(f"ventana {n}", font_size=20, color=C_MUESTRA)
            t.next_to(esp, UP, buff=0.20)
            tags[n] = t
            c = tag_hud(f"dt {fmt(DT[n], 0)}   df {fmt(DF[n], 4)}",
                        font_size=19, color=C_CALCULO)
            c.next_to(esp, DOWN, buff=0.22)
            cifras[n] = c

        for n in (n_c, n_l):
            esp = piezas[n]
            cols = VGroup(*[VGroup(*[esp.celda(i, j)
                                     for i in range(esp.n_f)])
                            for j in range(esp.n_t)])
            self.play(FadeIn(esp.ejes), FadeIn(tags[n]), run_time=0.55)
            self.play(LaggedStart(*[FadeIn(c) for c in cols],
                                  lag_ratio=1.6 / esp.n_t),
                      run_time=1.7)
            self.add(esp.celdas)
            rot.mostrar(cifra_pie(f"dt = {fmt(DT[n], 0)} muestras"),
                        zona="abajo", run_time=0.5)
            self.wait(1.7)

        # --- el mismo golpe, visto por las dos ------------------------------
        marcas = VGroup(*[piezas[n].marca_t(T_GOLPE, color=C_CALCULO)
                          for n in (n_c, n_l)])
        self.play(*[Create(m) for m in marcas], run_time=0.9)
        rot.mostrar(cifra_pie(f"golpe en t = {int(T_GOLPE)}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        # --- UNA celda: la corta es alta y fina; la larga, baja y ancha ----
        recuadros = VGroup()
        etiquetas = VGroup()
        for n, lado in ((n_c, LEFT), (n_l, RIGHT)):
            esp = piezas[n]
            j = int(np.argmin(np.abs(esp.t - T_GOLPE)))
            i = int(np.argmin(np.abs(esp.f - f_golpe)))
            r = SurroundingRectangle(esp.celda(i, j), color=C_CALCULO,
                                     buff=0.0, stroke_width=2.6)
            # el rotulo cae DENTRO de la malla: con fondo propio para
            # que no se lea encima de las celdas.
            e = _con_fondo(tag_hud("una celda", font_size=18,
                                   color=C_CALCULO), buff=0.10)
            e.next_to(r, lado, buff=0.16)
            recuadros.add(r)
            etiquetas.add(e)
        self.play(*[Create(r) for r in recuadros],
                  *[FadeIn(e) for e in etiquetas], run_time=0.9)
        self.play(*[FadeIn(c) for c in cifras.values()], run_time=0.6)
        rot.mostrar(cifra_pie(f"df {fmt(DF[n_c], 4)} y {fmt(DF[n_l], 4)}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        # --- y su AREA, que es la misma -------------------------------------
        productos = VGroup()
        for n in (n_c, n_l):
            p = tag_hud(f"dt x df = {fmt(PRODUCTO[n], 2)}", font_size=21,
                        color=C_SALIDA)
            p.next_to(cifras[n], DOWN, buff=0.24)
            productos.add(p)
        self.play(LaggedStart(*[FadeIn(p, shift=0.15 * UP)
                                for p in productos], lag_ratio=0.45),
                  run_time=1.2)
        rot.mostrar(cifra_pie(f"producto {fmt(PRODUCTO[n_c], 2)} y "
                              f"{fmt(PRODUCTO[n_l], 2)}", color=C_SALIDA),
                    zona="abajo", run_time=0.5)
        self.wait(3.0)
        self.play(*[Indicate(p, color=C_SALIDA, scale_factor=1.12)
                    for p in productos], run_time=0.9)
        self.wait(2.2)

        rot.mostrar(formula_pie(r"\Delta t \cdot \Delta f = 1"),
                    zona="abajo", run_time=0.5)
        self.wait(6.4)
