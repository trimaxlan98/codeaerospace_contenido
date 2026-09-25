class Clip1(Scene):
    """5.1.1 - El giro: los simbolos de RX (QPSK con un desfase de
    frecuencia de DF_RS ciclos/simbolo, SNR 15 dB) entran en tandas de 40.
    Cada simbolo llega girado ~1.33 grados mas que el anterior, asi que la
    nube se estira en un anillo en vez de caer en los 4 puntos de la
    QPSK. El color de cada tanda pasa de ambar oscuro a ambar claro con
    el tiempo, para que el giro se vea sin necesitar una cifra nueva: el
    parametro (gris) es el mismo GRADOS del bloque de numeros. (~32 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("El giro"), zona="arriba", run_time=0.6)
        self.wait(0.6)

        plano = S.PlanoIQ(unidad=1.5, alcance=1.75)
        plano.move_to(UP * 0.1)
        self.play(Create(plano.ejes), Create(plano.unidad_circulo),
                  run_time=0.9)
        self.wait(0.8)

        # --- los simbolos entran en tandas de 40: la nube se hace anillo ---
        tanda = 40
        ntandas = 10
        # interpolate_color EXIGE ManimColor: C_SENAL es un str
        c_senal_mc = ManimColor(C_SENAL)
        oscuro = interpolate_color(ManimColor(BLACK), c_senal_mc, 0.35)
        claro = interpolate_color(c_senal_mc, ManimColor(WHITE), 0.55)
        for i in range(ntandas):
            color_i = interpolate_color(oscuro, claro, i / (ntandas - 1))
            seg = RX[i * tanda:(i + 1) * tanda]
            nube_i = plano.nube(seg, color=color_i, maximo=tanda,
                                radio=0.05)
            self.play(FadeIn(nube_i), run_time=0.5)
            self.wait(0.35)
        self.wait(1.8)

        rot.mostrar(dato_pie(f"{fmt(GRADOS, 2)} grados por simbolo"),
                    zona="abajo", run_time=0.5)
        self.wait(18.0)
