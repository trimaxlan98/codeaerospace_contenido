class Clip8(Scene):
    """8 - El precio de la cera. Misma area, tres formas: el hexagono usa
    menos pared (Hales 1999). El panal tesela, se vuelve basalto, y el
    curso cierra su tesis a pantalla limpia. (~40 s)"""

    def construct(self):
        rot = Rotulos(self)

        modulo = hud_modulo("Modulo 08")
        self.play(FadeIn(modulo, shift=0.18 * RIGHT), run_time=0.5)
        titulo = titulo_curso("El precio de la cera")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)

        # --- momento: misma area, tres formas -----------------------------
        rot.mostrar(pie_curso("Misma área, tres formas: el hexágono usa "
                              "menos pared que nadie."), zona="abajo",
                    run_time=0.5)
        area = 1.55
        teselas = VGroup()
        for n, col in ((3, C_EJE), (4, C_EJE), (6, C_REGLA)):
            forma = tesela_unidad(n, area=area, color=col)
            cifra = Text(f"{PERIMETROS[n] * math.sqrt(area):.2f}",
                         font=FUENTE_HUD, font_size=18,
                         color=C_TENUE if n != 6 else C_REGLA)
            cifra.next_to(forma, DOWN, buff=0.30)
            teselas.add(VGroup(forma, cifra))
        teselas.arrange(RIGHT, buff=1.15).move_to(UP * 0.35)
        pared = tag_junto(teselas, "pared por celda", UP, buff=0.35,
                          font_size=17)
        self.play(LaggedStart(*[FadeIn(t, shift=0.2 * UP) for t in teselas],
                              lag_ratio=0.3), FadeIn(pared), run_time=1.6)
        self.play(Indicate(teselas[2][0], color=C_REGLA), run_time=0.9)
        self.wait(3.4)

        # --- momento: la abeja lo practicaba; Hales lo demostro -----------
        rot.mostrar(pie_curso(f"La abeja lo practicaba; Hales lo demostró "
                              f"en {HALES}."), zona="abajo", run_time=0.5)
        self.play(FadeOut(teselas), FadeOut(pared), run_time=0.5)
        abejas = panal(5, 9, lado=0.44)
        abejas.move_to(UP * 0.35)
        self.play(abejas.aparecer(run_time=2.4))
        self.wait(1.8)

        # --- momento: el panal se vuelve piedra ---------------------------
        basalto = panal(5, 9, lado=0.44, color=C_EJE, semilla=3)
        basalto.move_to(UP * 0.35)
        etiqueta = tag_hud("basalto columnar", font_size=15, color=C_TENUE)
        etiqueta.move_to(RIGHT * 4.35 + UP * 2.55)
        self.play(Transform(abejas, basalto), run_time=1.4)
        rot.mostrar(etiqueta, zona="tag", run_time=0.4)
        self.wait(2.2)

        # --- momento: lo mas barato ---------------------------------------
        rot.mostrar(pie_curso("La naturaleza no sabe matemáticas: hace lo "
                              "más barato."), zona="abajo", run_time=0.5)
        self.play(FadeOut(abejas), run_time=0.7)
        rot.limpiar("tag", run_time=0.3)

        minis = VGroup(
            filotaxis(130, escala=0.62),
            espiral_log(vueltas=2.2, escala=0.62),
            arbol_fractal(5, escala=0.42),
            gato_dormido(escala=0.52),
            tesela_unidad(6, area=0.75, color=C_REGLA),
        )
        minis.arrange(RIGHT, buff=0.95).move_to(UP * 0.35)
        self.play(LaggedStart(*[FadeIn(m, shift=0.18 * UP) for m in minis],
                              lag_ratio=0.2), run_time=2.0)
        self.wait(3.2)

        # --- momento: cierre del curso ------------------------------------
        rot.limpiar("arriba", run_time=0.4)
        rot.limpiar("abajo", run_time=0.3)
        self.play(FadeOut(minis), run_time=0.7)
        cierre = VGroup(
            titulo_marca("La naturaleza no sabe matemáticas.",
                         font_size=38),
            Text("Matemáticas es el nombre de lo que no desperdicia.",
                 font_size=26, color=C_CONSTANTE),
        ).arrange(DOWN, buff=0.4)
        cierre.move_to(UP * 0.2)
        self.play(Write(cierre[0]), run_time=1.4)
        self.play(FadeIn(cierre[1], shift=0.18 * UP), run_time=0.8)
        self.wait(5.6)
