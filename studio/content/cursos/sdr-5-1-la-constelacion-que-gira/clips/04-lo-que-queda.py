class Clip4(Scene):
    """5.1.4 - Lo que queda: RX corregido con el desfase MEDIDO (RX_CORR
    = RX * exp(-j2pi*DF_EST*k)) vuelve a caer en los 4 puntos de la QPSK,
    con la nube de ruido alrededor de cada uno. El anillo (RX) y la nube
    corregida (RX_CORR) son GEMELAS: mismo numero de puntos, mismo orden
    (misma magnitud en ambas: corregir solo gira la fase), asi que se
    anima con Transform. Cierre de la leccion. (~30 s)"""

    def construct(self):
        rot = Rotulos(self)
        rot.mostrar(titulo_curso("Lo que queda"), zona="arriba",
                    run_time=0.6)
        self.wait(0.6)

        plano = S.PlanoIQ(unidad=1.5, alcance=1.75)
        plano.move_to(UP * 0.1)
        self.play(Create(plano.ejes), Create(plano.unidad_circulo),
                  run_time=0.8)
        # entro por sus hijos (Create introducer=True): consolidar en UN
        # solo mobjeto de escena antes de tratarlo como grupo en el cierre.
        self.remove(*plano.get_family())
        self.add(plano)
        self.wait(0.4)

        n_pts = 400
        nube = plano.nube(RX[:n_pts], color=C_SENAL, maximo=n_pts,
                          radio=0.05)
        self.play(FadeIn(nube), run_time=1.0)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"corrige {fmt(GRADOS_EST, 3)} grados"),
                    zona="abajo", run_time=0.5)
        self.wait(1.6)

        # --- se corrige: el anillo vuelve a los 4 puntos --------------------
        nube_corr = plano.nube(RX_CORR[:n_pts], color=C_SENAL,
                               maximo=n_pts, radio=0.05)
        self.play(Transform(nube, nube_corr), run_time=2.2)
        self.wait(5.5)

        cierre_leccion(
            self, rot,
            "Cada receptor mide su propio error",
            "antes de leer un solo bit.",
            plano, nube, espera=13.0)
