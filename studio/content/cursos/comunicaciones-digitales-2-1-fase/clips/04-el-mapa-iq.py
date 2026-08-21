class Clip4(Scene):
    """2.1.4 - El mapa IQ es el idioma: cada punto un mensaje, d_min
    MEDIDA la resistencia al ruido. Cierre de leccion. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("El mapa IQ es el idioma")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el plano de todo el curso --------------------------------
        rot.mostrar(pie_curso("Este plano es el idioma de todo el curso: "
                              "cada punto, un mensaje."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.4, alcance=1.65)
        piq.move_to(DOWN * 0.15)
        puntos_qpsk = piq.puntos(PUNTOS_QPSK, bits=BITS_TABLA_QPSK,
                                 color=C_BIT, radio=0.09, font_size=16)
        self.play(FadeIn(piq), run_time=0.7)
        self.play(LaggedStart(*[FadeIn(p, scale=0.4) for p in puntos_qpsk],
                              lag_ratio=0.12), run_time=1.2)
        self.wait(4.5)

        # --- momento: la distancia es resistencia al ruido -----------------------
        rot.mostrar(pie_curso("La distancia entre dos puntos es la "
                              "resistencia al ruido: mas lejos, mas "
                              "dificil confundirlos."),
                    zona="abajo", run_time=0.5)
        p_a, p_b = PUNTOS_QPSK[_I_A], PUNTOS_QPSK[_I_B]
        seg_dmin = Line(piq.p(p_a), piq.p(p_b), color=C_CIFRA,
                        stroke_width=3.2)
        et_dmin = llave(seg_dmin, texto=f"d_min = {fmt(DMIN_QPSK, 2)}",
                        direccion=UP, font_size=19, color=C_CIFRA)
        self.play(Create(seg_dmin), run_time=0.8)
        self.play(FadeIn(et_dmin), run_time=0.5)
        self.wait(4.8)

        # --- momento: BPSK separaba mas, con menos bits --------------------------
        rot.mostrar(pie_curso("BPSK separaba sus dos mensajes el doble: "
                              "menos bits, mas margen frente al ruido."),
                    zona="abajo", run_time=0.5)
        panel = panel_derecha(
            tag_hud(f"d_min BPSK = {fmt(DMIN_BPSK, 2)}", color=C_BIT),
            tag_hud(f"d_min QPSK = {fmt(DMIN_QPSK, 2)}", color=C_CIFRA),
            tag_hud(f"misma energia = {fmt(ENERGIA_QPSK, 1)}",
                    color=C_SENAL))
        self.play(FadeIn(panel), run_time=0.6)
        self.wait(5.5)

        # --- cierre de leccion -----------------------------------------------
        cierre_leccion(
            self, rot,
            "La onda es la misma.",
            "El mensaje vive en su fase.",
            "Siguiente leccion: mas bits por simbolo, QAM y APSK.",
            piq, puntos_qpsk, seg_dmin, et_dmin, panel)
