class Clip1(Scene):
    """2.3.1 - La nube AWGN: el canal suma ruido gaussiano y cada
    simbolo llega desplazado. A 12 dB las nubes quedan apretadas y
    ninguno de los 500 simbolos sale de su region. (~33 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("La nube AWGN")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la constelacion limpia ------------------------------
        rot.mostrar(pie_curso("La sonda transmite QPSK: cuatro fases, dos "
                              "bits en cada simbolo."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.35, alcance=ALCANCE_IQ)
        piq.move_to(LEFT * 3.0 + DOWN * 0.15)
        simbolos = piq.puntos(PQ, radio=0.085, color=C_BIT)
        etiquetas = VGroup(*[
            tag_hud("".join(str(int(b)) for b in BQ[i]), font_size=17,
                    color=C_TENUE).move_to(piq.p(z * 1.58))
            for i, z in enumerate(PQ)])
        self.play(FadeIn(piq), run_time=0.7)
        self.play(LaggedStart(*[GrowFromCenter(d) for d in simbolos],
                              lag_ratio=0.18), run_time=1.1)
        self.play(FadeIn(etiquetas), run_time=0.5)
        self.wait(4.3)

        # --- momento: el ruido empuja cada llegada ------------------------
        rot.mostrar(pie_curso("El canal suma ruido termico: la llegada es "
                              "el simbolo MAS un empujon al azar."),
                    zona="abajo", run_time=0.5)
        # la llegada mas empujada de la nube del simbolo 00: el mismo
        # array que se dibujara despues, sin cifra escrita a mano
        _de_00 = np.flatnonzero(IDX_VIS == 0)
        r0 = RX_ALTO[_de_00[int(np.argmax(np.abs(RX_ALTO[_de_00] - PQ[0])))]]
        empujon = flecha_libre(piq, PQ[0], r0, color=C_RUIDO, grosor=3.4,
                               punta_len=0.14)
        llegada = Dot(piq.p(r0), radius=0.07, color=C_SENAL)
        suma = MathTex("r", "=", "s", "+", "n", font_size=42)
        suma[0].set_color(C_SENAL)     # lo recibido
        suma[2].set_color(C_BIT)       # el simbolo enviado
        suma[4].set_color(C_RUIDO)     # el ruido
        et_suma = tag_junto(suma, "n: gaussiano, de media cero",
                            direccion=DOWN, buff=0.24, font_size=19)
        bloque_suma = VGroup(suma, et_suma)
        bloque_suma.move_to(RIGHT * 3.5 + UP * 0.35)
        self.play(Create(empujon), FadeIn(llegada), run_time=0.9)
        self.play(FadeIn(bloque_suma, shift=0.15 * UP), run_time=0.6)
        self.wait(4.6)

        # --- momento: quinientas llegadas, cuatro nubes -------------------
        rot.mostrar(pie_curso("Quinientos simbolos despues, el ruido ha "
                              "dibujado cuatro nubes apretadas."),
                    zona="abajo", run_time=0.5)
        nube = piq.nube(RX_ALTO, color=C_SENAL, maximo=N_NUBE, radio=0.032)
        cifras = panel_derecha(
            tag_hud(f"Eb/N0 = {fmt(EBN0_ALTO, 0)} dB", font_size=20),
            tag_hud(f"simbolos = {N_VIS}", font_size=20),
            buff=0.26)
        self.play(FadeOut(empujon), FadeOut(llegada),
                  FadeOut(bloque_suma), run_time=0.5)
        self.play(FadeIn(nube, scale=0.7), run_time=1.4)
        self.bring_to_front(simbolos)   # el simbolo enviado, sobre su nube
        self.play(FadeIn(cifras), run_time=0.5)
        self.wait(4.2)

        # --- momento: la ley del receptor ---------------------------------
        rot.mostrar(pie_curso("El receptor decide por cercania: estas "
                              "cuatro regiones son toda su ley."),
                    zona="abajo", run_time=0.5)
        # las fronteras de decision caen sobre los ejes: se pintan en
        # naranja (el color de las regiones asignadas) y cada cuadrante
        # se tine para que se vean como TERRITORIOS, no como mobiliario
        regiones = piq.regiones(CAMPO_QPSK, XS_QPSK, color=C_BANDA,
                                grosor=3.0)
        lado = ALCANCE_IQ * piq.u
        cuadrantes = VGroup(*[
            Rectangle(width=lado, height=lado, stroke_width=0,
                      fill_color=C_BANDA, fill_opacity=0.08).move_to(
                piq.p(sx * ALCANCE_IQ / 2.0, sy * ALCANCE_IQ / 2.0))
            for sx, sy in ((1, 1), (-1, 1), (-1, -1), (1, -1))])
        self.play(Create(regiones), run_time=1.1)
        self.play(LaggedStart(*[FadeIn(c) for c in cuadrantes],
                              lag_ratio=0.25), run_time=1.5)
        self.bring_to_front(nube, simbolos, regiones)
        et_fuera = tag_hud(f"fuera de region = {N_MAL_ALTO}", font_size=20)
        et_fuera.next_to(cifras, DOWN, buff=0.3)
        self.play(FadeIn(et_fuera, shift=0.12 * UP), run_time=0.5)
        self.wait(4.6)
