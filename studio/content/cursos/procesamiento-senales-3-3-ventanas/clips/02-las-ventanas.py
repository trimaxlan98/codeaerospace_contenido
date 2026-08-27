class Clip2(Scene):
    """3.3.2 - Cuatro ventanas: hunden el lobulo lateral a costa de
    ensanchar el principal. El mismo tono con cada una. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("Las ventanas"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        col = {"rect": C_RUIDO, "hann": C_CALCULO,
               "hamming": C_MUESTRA, "blackman": C_IDEAL}
        nom = {"rect": "rect", "hann": "hann",
               "hamming": "hamm", "blackman": "black"}

        # --- arriba a la izquierda: las cuatro formas ----------------------
        def _forma(w):
            idx = np.arange(len(w))
            return lambda u: float(np.interp(u, idx, w))

        cajas = {v: grafica(_forma(V[v]), (0.0, N_VENT - 1.0), (0.0, 1.12),
                            ancho=5.0, alto=1.75, color=col[v],
                            muestras=257)
                 for v in VENTANAS}
        for c in cajas.values():
            c.move_to(LEFT * 3.7 + UP * 1.62)
        et_n = tag_hud(f"n = {N_VENT}", font_size=18, color=C_TENUE)
        et_n.next_to(cajas["rect"], DOWN, buff=0.20)
        self.play(FadeIn(cajas["rect"].ejes), FadeIn(et_n), run_time=0.5)

        # --- arriba a la derecha: el lateral mas alto de cada una ----------
        filas_lat = VGroup(*[tag_hud(f"{nom[v]}  {fmt(LATERAL[v], 1)} dB",
                                     font_size=20, color=col[v])
                             for v in VENTANAS])
        filas_lat.arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        filas_lat.move_to(RIGHT * 3.6 + UP * 1.55)
        cab = tag_hud("lobulo lateral", font_size=18, color=C_TENUE)
        cab.next_to(filas_lat, UP, buff=0.26)
        self.play(FadeIn(cab), run_time=0.4)

        for i, v in enumerate(VENTANAS):
            self.play(Create(cajas[v].curva), FadeIn(filas_lat[i]),
                      run_time=1.25)
        rot.mostrar(cifra_pie(f"lateral: {fmt(LATERAL['rect'], 1)} a "
                              f"{fmt(LATERAL['blackman'], 1)} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.6)

        # --- abajo: el MISMO tono entre bins con cada ventana --------------
        z = slice(88, 114)
        esp = {}
        for v, db in (("rect", DB_ENTRE_RECT), ("hann", DB_ENTRE_HANN),
                      ("blackman", DB_ENTRE_BLACK)):
            e = EspectroDoble(F_EJE[z], db[z], piso_db=-85.0, ancho=9.2,
                              alto=1.95, color=col[v])
            e.move_to(DOWN * 1.62 + LEFT * 0.60)
            esp[v] = e
        et_f = tag_hud(f"tono en {fmt(F_ENTRE_BINS, 1)} Hz", font_size=18,
                       color=C_TENUE)
        et_f.next_to(esp["rect"], UP, buff=0.14)
        et_f.align_to(esp["rect"], LEFT)
        self.play(FadeIn(esp["rect"].ejes), FadeIn(et_f), run_time=0.5)

        leyenda = VGroup(*[tag_hud(nom[v], font_size=19, color=col[v])
                           for v in ("rect", "hann", "blackman")])
        leyenda.arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        leyenda.next_to(esp["rect"], RIGHT, buff=0.34)
        for i, v in enumerate(("rect", "hann", "blackman")):
            self.play(Create(esp[v].curva), FadeIn(leyenda[i]),
                      run_time=1.5)
        self.wait(2.8)

        # --- lo que se paga: el lobulo principal se ensancha ---------------
        filas_lob = VGroup(*[tag_hud(f"{nom[v]}  {fmt(LOBULO[v], 2)} bins",
                                     font_size=20, color=col[v])
                             for v in VENTANAS])
        filas_lob.arrange(DOWN, buff=0.30, aligned_edge=LEFT)
        filas_lob.move_to(filas_lat.get_center())
        cab2 = tag_hud("lobulo principal", font_size=18, color=C_TENUE)
        cab2.next_to(filas_lob, UP, buff=0.26)
        self.play(FadeOut(filas_lat), FadeOut(cab), run_time=0.45)
        self.play(FadeIn(filas_lob), FadeIn(cab2), run_time=0.55)
        rot.mostrar(cifra_pie(f"lobulo: {fmt(LOBULO['rect'], 2)} a "
                              f"{fmt(LOBULO['blackman'], 2)} bins"),
                    zona="abajo", run_time=0.5)
        self.wait(1.6)

        # los nulos del lobulo principal, sobre el mismo tono
        nulos = {}
        for v in ("rect", "blackman"):
            medio = 0.5 * LOBULO[v] * RESOLUCION
            nulos[v] = VGroup(
                esp["rect"].marca_f(F_ENTRE_BINS - medio, color=col[v]),
                esp["rect"].marca_f(F_ENTRE_BINS + medio, color=col[v]))
        self.play(Create(nulos["rect"]), run_time=0.8)
        self.wait(1.6)
        self.play(Create(nulos["blackman"]), run_time=0.8)
        self.wait(2.4)

        # --- el compromiso, en dos cifras ----------------------------------
        caida = LATERAL["blackman"] - LATERAL["rect"]
        ancho_x = LOBULO["blackman"] / LOBULO["rect"]
        rot.mostrar(cifra_pie(f"lateral {fmt(caida, 1)} dB, lobulo "
                              f"x{fmt(ancho_x, 2)}"),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)
