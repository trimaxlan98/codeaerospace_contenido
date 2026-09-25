class Clip2(Scene):
    """5.1.2 - A la cuarta potencia: los 4 puntos ideales de la QPSK (45,
    135, 225, 315 grados) elevados a la cuarta caen TODOS en el mismo
    punto (180 grados): la modulacion desaparece y solo queda el giro.
    Luego el espectro de RX**4 (ciclos por simbolo, eje +-0.05) tiene UNA
    raya en 4 veces el desfase, marcada en cian.

    OJO libreria: S.espectro_db no hace zero-padding (reparte x en
    segmentos de `nfft` muestras y los multiplica por una ventana de esa
    misma longitud); con RX de 2048 muestras, nfft=8192 revienta por
    mismatch de formas ValueError: operands could not be broadcast
    together with shapes (2048,) (8192,) (medido en el scratchpad, ver
    informe). Aqui se usa nfft=len(RX)=2048, que sí es valido y deja ver
    una unica raya limpia en la ventana +-0.05. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("A la cuarta potencia"), zona="arriba",
                    run_time=0.6)
        self.wait(0.8)

        # --- los 4 puntos ideales y su cuarta potencia: un solo punto ------
        p_izq = S.PlanoIQ(unidad=1.7, alcance=1.5)
        p_izq.move_to(LEFT * 3.4)
        p_der = S.PlanoIQ(unidad=1.7, alcance=1.5)
        p_der.move_to(RIGHT * 3.4)
        self.play(Create(p_izq.ejes), Create(p_izq.unidad_circulo),
                  run_time=0.8)
        self.remove(*p_izq.get_family())
        self.add(p_izq)
        self.wait(0.6)

        dots_izq = p_izq.puntos(S.QPSK, color=C_SENAL, radio=0.09)
        et_qpsk = tag_junto(p_izq, "QPSK", UP, buff=0.25, font_size=22,
                            color=C_SENAL)
        self.play(FadeIn(dots_izq), FadeIn(et_qpsk), run_time=0.7)
        self.wait(1.4)

        self.play(Create(p_der.ejes), Create(p_der.unidad_circulo),
                  run_time=0.6)
        self.remove(*p_der.get_family())
        self.add(p_der)
        self.wait(0.6)
        rot.mostrar(formula_pie(r"z \rightarrow z^{4}"), zona="abajo",
                    run_time=0.5)
        self.wait(1.6)

        dots_der = VGroup(*[p_der.punto(z ** 4, color=C_SENAL, radio=0.09)
                            for z in S.QPSK])
        self.play(*[TransformFromCopy(dots_izq[i], dots_der[i])
                   for i in range(4)], run_time=1.6)
        self.wait(1.8)
        rot.limpiar(zona="abajo", run_time=0.3)
        self.wait(0.3)

        # --- el espectro de RX**4: una sola raya en 4 x el desfase ---------
        self.play(FadeOut(VGroup(p_izq, p_der, dots_izq, dots_der,
                                 et_qpsk)), run_time=0.8)

        f, db = S.espectro_db(RX ** 4, 1.0, nfft=len(RX))
        fr, dbr = S.para_dibujar(f, db, puntos=900, f_lo=-0.05, f_hi=0.05)
        esp = S.Espectro(fr, dbr, piso=-40.0, techo=3.0, ancho=11.0,
                         alto=3.8, color=C_SENAL)
        ticks = esp.marcas([-0.05, 0.0, 0.05], ["-0.05", "0", "0.05"])
        u = tag_junto(ticks[-1], "ciclos/simb", RIGHT, buff=0.2,
                     font_size=18)
        self.play(Create(esp.ejes), FadeIn(ticks), FadeIn(u), run_time=0.9)
        self.wait(0.8)
        self.play(Create(esp.curva), FadeIn(esp.area), run_time=2.2)
        self.wait(1.6)

        pico4 = 4.0 * DF_EST
        marca = esp.marca_f(pico4, color=C_CALCULO)
        et_marca = tag_junto(marca, "4 x el giro", UP, buff=0.16,
                             font_size=20, color=C_CALCULO)
        self.play(Create(marca), FadeIn(et_marca), run_time=0.7)
        self.wait(2.0)
        self.wait(9.0)
