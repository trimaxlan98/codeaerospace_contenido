class Clip3(Scene):
    """4.1.3 - La ventana al espacio: al mismo ángulo de salida, subir
    la frecuencia cambia el destino. Por debajo de fp rebota siempre;
    por encima, la capa deja de ser espejo y se vuelve ventana. Por eso
    el satcom vive de VHF hacia arriba. (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("La ventana al espacio")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.4)

        # --- momento: mismo angulo, tres frecuencias ---------------------------
        frecs = (5.0e6, 15.0e6, 300.0e6)
        ven = ventana_iono(frecuencias=frecs)
        ven.move_to(DOWN * 0.35)
        rot.mostrar(pie_curso("Tres rayos, el mismo ángulo de salida, "
                              "tres frecuencias distintas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeIn(ven.suelo), FadeIn(ven.capa), run_time=0.7)
        self.wait(3.6)

        # Los tres rayos convergen arriba: las etiquetas van en una lista
        # fija fuera de la geometria (esquina superior derecha), no
        # pegadas a cada rayo, para que nunca se encimen entre si.
        etiquetas = VGroup(*[
            tag_hud(f"{f / 1e6:.0f} MHz: {c}", font_size=16)
            for f, c in zip(frecs, ven.comportamientos)])
        etiquetas.arrange(DOWN, aligned_edge=RIGHT, buff=0.2)
        etiquetas.to_corner(UR, buff=0.55).shift(DOWN * 0.5)

        # --- momento: el primero rebota ------------------------------------
        rot.mostrar(pie_curso("Cinco megahercios: por debajo de la "
                              "frecuencia de plasma. Rebota, como "
                              "antes."), zona="abajo", run_time=0.5)
        self.play(Create(ven.rayo(0)), FadeIn(etiquetas[0]), run_time=1.0)
        self.wait(4.2)

        # --- momento: el segundo cruza ---------------------------------------
        rot.mostrar(pie_curso("Quince megahercios: por encima de fp. La "
                              "capa deja de ser espejo y se abre."),
                    zona="abajo", run_time=0.5)
        self.play(Create(ven.rayo(1)), FadeIn(etiquetas[1]), run_time=1.0)
        self.wait(4.2)

        # --- momento: el tercero, muy por encima -------------------------------
        rot.mostrar(pie_curso("Trescientos megahercios: ni se entera de "
                              "que la capa está ahí. Cruza limpio."),
                    zona="abajo", run_time=0.5)
        self.play(Create(ven.rayo(2)), FadeIn(etiquetas[2]), run_time=1.0)
        self.wait(4.4)

        rot.mostrar(pie_curso("Para hablar con un satélite hay que "
                              "comprar frecuencia POR ENCIMA del techo: "
                              "el satcom vive de VHF hacia arriba."),
                    zona="abajo", run_time=0.5)
        self.wait(4.8)

        rot.mostrar(pie_curso("De reojo: el rebote oblicuo aguanta algo "
                              "más que fp — esa frecuencia límite es la "
                              "MUF."), zona="abajo", run_time=0.5)
        self.wait(4.6)
