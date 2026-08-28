class Clip3(Scene):
    """8.1.3 - Meter tres ceros entre cada par de muestras no cambia la
    señal, pero llena su espectro de copias: las imagenes. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 08"))
        rot.mostrar(titulo_curso("Meter ceros"), zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- la secuencia con los ceros metidos ----------------------------
        n_ver = 32
        sec = Secuencia(X_CEROS[:n_ver], 0, (-1.6, 1.6), ancho=10.4, alto=1.7,
                        color=C_TENUE, radio=0.045)
        sec.move_to(UP * 2.55)
        self.play(FadeIn(sec.ejes), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(sec.tallo(i)) for i in range(n_ver)],
                              lag_ratio=0.02),
                  LaggedStart(*[FadeIn(sec.punto(i)) for i in range(n_ver)],
                              lag_ratio=0.02), run_time=1.6)
        self.wait(2.0)

        reales = list(range(0, n_ver, L_INT))
        marcas = VGroup(*[sec.marcar(i, color=C_MUESTRA) for i in reales])
        et_reales = tag_hud("reales", font_size=18, color=C_MUESTRA)
        et_reales.next_to(sec, LEFT, buff=0.28)
        self.play(LaggedStart(*[Create(m) for m in marcas], lag_ratio=0.1),
                  FadeIn(et_reales), run_time=1.3)
        rot.mostrar(cifra_pie(f"{L_INT - 1} ceros entre cada par"),
                    zona="abajo", run_time=0.5)
        self.wait(3.4)

        # --- el espectro se llena de copias ---------------------------------
        ed = EspectroDoble(F_EJE_I, DB_I, piso_db=-70.0, ancho=9.6, alto=2.15,
                           color=C_BANDA)
        ed.move_to(DOWN * 1.6)
        et_i = tag_hud("espectro", font_size=18, color=C_TENUE)
        et_i.next_to(ed, UP, buff=0.16).align_to(ed, LEFT)
        self.play(FadeIn(ed.ejes), FadeIn(et_i), run_time=0.4)
        self.play(Create(ed.curva), FadeIn(ed.area), run_time=1.4)
        self.wait(2.2)

        marca_img = ed.marca_f(F_IMAGEN_1, color=C_RUIDO)
        et_img = tag_hud("imagen", font_size=19, color=C_RUIDO)
        et_img.next_to(ed.en(F_IMAGEN_1, 0.0), UP, buff=0.14)
        self.play(Create(marca_img), FadeIn(et_img), run_time=0.8)
        rot.mostrar(cifra_pie(f"imagen en {fmt(F_IMAGEN_1, 0)} Hz"),
                    zona="abajo", run_time=0.5)
        self.wait(4.2)

        panel = panel_cifras((f"{len(X_CORTA)} -> {len(X_CEROS)} muestras",
                             C_SALIDA))
        panel.move_to(RIGHT * 3.0 + UP * 0.55)
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(9.9)
