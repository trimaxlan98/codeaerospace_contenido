class Clip1(Scene):
    """6.2.1 - Un Chebyshev de orden 10 es estable; guardar sus 11
    coeficientes con 16 bits saca dos polos del circulo. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 06"))
        rot.mostrar(titulo_curso("La forma directa revienta"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        b16 = BITS[0]

        # --- el filtro que se diseno: 10 polos dentro del circulo ---------
        pz = PlanoZ([], POLOS_EXACTOS, unidad=2.00, alcance=1.30,
                    color_polo=C_MUESTRA)
        pz.shift(LEFT * 3.45 + DOWN * 0.15 - pz.en(0))
        pz.circulo.set_color(C_DATO)
        for marca in pz.polos:
            marca.scale(0.55)
        self.play(Create(pz.ejes), Create(pz.circulo), run_time=1.0)
        et_circ = tag_hud("|z| = 1", font_size=19, color=C_DATO)
        et_circ.move_to(pz.en(-1.15 - 1.15j))
        self.play(FadeIn(et_circ), run_time=0.4)
        self.play(LaggedStart(*[FadeIn(m) for m in pz.polos],
                              lag_ratio=0.08), run_time=1.4)
        rot.mostrar(cifra_pie(f"orden = {ORDEN}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.5)

        p_max = max([z for z in POLOS_EXACTOS if z.imag >= 0], key=abs)
        r_ex = Line(pz.en(0), pz.en(p_max), color=C_MUESTRA,
                    stroke_width=2.2)
        self.play(Create(r_ex), run_time=0.8)
        rot.mostrar(cifra_pie(f"radio maximo {RADIO_EXACTO:.4f}"),
                    zona="abajo", run_time=0.5)
        self.wait(2.0)

        # --- guardar los coeficientes con 16 bits -------------------------
        rot.mostrar(cifra_pie(f"{len(A)} coeficientes / {b16} bits"),
                    zona="abajo", run_time=0.5)
        self.wait(1.2)

        pol_q = pz.con_pz([], POLOS_DIRECTA[b16]).polos
        pol_q.set_color(C_RUIDO)
        for marca in pol_q:
            marca.scale(0.55)
        self.play(LaggedStart(*[FadeIn(m) for m in pol_q], lag_ratio=0.06),
                  run_time=1.4)
        self.wait(1.0)

        r_q = Circle(radius=RADIO_DIRECTA[b16] * pz.unidad, color=C_RUIDO,
                     stroke_width=1.8, stroke_opacity=0.70)
        r_q.move_to(pz.en(0))
        self.play(Create(r_q), run_time=0.9)
        rot.mostrar(cifra_pie(f"{b16} bits -> radio "
                              f"{RADIO_DIRECTA[b16]:.4f}"), zona="abajo",
                    run_time=0.5)
        p_fuera = max([z for z in POLOS_DIRECTA[b16] if z.imag >= 0],
                      key=abs)
        et_fuera = tag_hud("fuera del circulo", font_size=19, color=C_RUIDO)
        et_fuera.move_to(pz.en(-0.55 + 1.30j))
        self.play(FadeIn(et_fuera), run_time=0.5)
        self.wait(2.0)

        # --- lo que eso le hace a la respuesta ----------------------------
        rf = respuesta_dibujo(W, MAG, ancho=5.0, alto=2.0, piso_db=-90.0,
                              techo_db=8.0, color=C_SALIDA)
        rf.move_to(RIGHT * 3.6 + DOWN * 0.95)
        et_rf = tag_hud("|H| en dB", font_size=19, color=C_TENUE)
        et_rf.next_to(rf, DOWN, buff=0.18)
        self.play(FadeIn(rf), FadeIn(et_rf), run_time=0.9)
        rot.mostrar(cifra_pie(f"pico exacto {PICO_EXACTO:+.2f} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(1.8)

        gem = rf.con_mag(MAG_DIRECTA[b16], color=C_RUIDO)
        self.play(Transform(rf.curva, gem.curva), run_time=1.2)
        rot.mostrar(cifra_pie(f"{b16} bits: {PICO_DIRECTA[b16]:+.2f} dB"),
                    zona="abajo", run_time=0.5)
        self.wait(2.4)

        panel = panel_cifras(
            (f"exacto {RADIO_EXACTO:.4f}", C_MUESTRA),
            (f"{b16} bits {RADIO_DIRECTA[b16]:.4f}", C_RUIDO),
            (f"{BITS[1]} bits {RADIO_DIRECTA[BITS[1]]:.4f}", C_RUIDO),
            # "estable False" es un literal de Python, no castellano: el
# rotulo dice lo que significa, y sigue saliendo de la variable.
            (f"{b16} bits: "
             f"{'estable' if ESTABLE_DIRECTA[b16] else 'inestable'}",
             C_RUIDO))
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.2)

        self.play(FadeOut(rf), FadeOut(et_rf), run_time=0.8)
        rot.mostrar(cifra_pie(f"{b16} bits -> radio "
                              f"{RADIO_DIRECTA[b16]:.4f}"), zona="abajo",
                    run_time=0.5)
        self.wait(3.4)
