class Clip2(Scene):
    """2.3.2 - A 4 dB las nubes se ensanchan hasta tocarse: los simbolos
    que caen en region ajena se pintan de rojo y se CUENTAN sobre los
    mismos puntos que estan en pantalla. (~35 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("Cuando la nube cruza la frontera")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: de donde veniamos (12 dB) ---------------------------
        rot.mostrar(pie_curso("Volvemos a las nubes de 12 dB: cada "
                              "simbolo, dentro de su region."),
                    zona="abajo", run_time=0.5)
        piq = plano_iq(unidad=1.35, alcance=ALCANCE_IQ)
        piq.move_to(LEFT * 3.0 + DOWN * 0.15)
        regiones = piq.regiones(CAMPO_QPSK, XS_QPSK, color=C_BANDA,
                                grosor=3.0)
        simbolos = piq.puntos(PQ, radio=0.085, color=C_BIT)
        # las dos nubes se parten con la MISMA mascara (la de 4 dB): asi
        # son gemelas de estructura identica y el Transform empareja
        # punto con punto, sin que ningun simbolo cambie de grupo
        nube_ok = piq.nube(RX_ALTO[~MAL_BAJO], color=C_SENAL,
                           maximo=N_NUBE, radio=0.032)
        nube_cruza = piq.nube(RX_ALTO[MAL_BAJO], color=C_SENAL,
                              maximo=N_NUBE, radio=0.032)
        et_alto = tag_hud(f"Eb/N0 = {fmt(EBN0_ALTO, 0)} dB", font_size=22)
        et_alto.move_to(piq.p(0, ALCANCE_IQ) + UP * 0.42)
        self.play(FadeIn(piq), FadeIn(regiones), run_time=0.8)
        self.play(FadeIn(nube_ok), FadeIn(nube_cruza),
                  FadeIn(simbolos), run_time=1.0)
        self.bring_to_front(simbolos)
        rot.mostrar(et_alto, zona="cifra", run_time=0.4)
        self.wait(4.2)

        # --- momento: menos potencia, mas ruido ---------------------------
        rot.mostrar(pie_curso("Bajamos la potencia a 4 dB: el ruido se "
                              "ensancha y las nubes se tocan."),
                    zona="abajo", run_time=0.5)
        nube_ok_4 = piq.nube(RX_BAJO[~MAL_BAJO], color=C_SENAL,
                             maximo=N_NUBE, radio=0.032)
        nube_cruza_4 = piq.nube(RX_BAJO[MAL_BAJO], color=C_SENAL,
                                maximo=N_NUBE, radio=0.032)
        et_bajo = tag_hud(f"Eb/N0 = {fmt(EBN0_BAJO, 0)} dB", font_size=22)
        et_bajo.move_to(et_alto)
        rot.mostrar(et_bajo, zona="cifra", run_time=0.4)
        self.play(Transform(nube_ok, nube_ok_4),
                  Transform(nube_cruza, nube_cruza_4), run_time=1.8)
        self.wait(4.4)

        # --- momento: los que cruzaron, rojos y contados ------------------
        rot.mostrar(pie_curso(f"{N_MAL_BAJO} llegadas cayeron en la region "
                              f"del vecino: el receptor las leera mal."),
                    zona="abajo", run_time=0.5)
        self.play(nube_cruza.animate.set_color(C_RUIDO), run_time=0.8)
        anillos = VGroup(*[
            Circle(radius=0.12, color=C_RUIDO, stroke_width=2.2).move_to(
                piq.p(z)) for z in RX_BAJO[MAL_BAJO]])
        self.play(LaggedStart(*[GrowFromCenter(a) for a in anillos],
                              lag_ratio=0.06), run_time=1.6)
        cuentas = panel_derecha(
            tag_hud(f"simbolos = {N_VIS}", font_size=20),
            tag_hud(f"en region ajena = {N_MAL_BAJO}", font_size=20),
            tag_hud(f"bits errados = {BITS_MAL_BAJO} de {N_BITS_VIS}",
                    font_size=20),
            buff=0.26)
        self.play(FadeIn(cuentas), run_time=0.6)
        self.wait(4.4)

        # --- momento: el conteo es la BER ---------------------------------
        rot.mostrar(pie_curso("Con Gray, el vecino cambia un solo bit: la "
                              "cuenta sale de los puntos que ves."),
                    zona="abajo", run_time=0.5)
        ber = MathTex(r"\mathrm{BER} = \frac{%d}{%d} = %s"
                      % (BITS_MAL_BAJO, N_BITS_VIS, sci(BER_NUBE)),
                      font_size=38, color=C_CALCULO)
        ber.next_to(cuentas, DOWN, buff=0.45)
        self.play(FadeIn(ber, shift=0.15 * UP), run_time=0.7)
        self.wait(6.0)
