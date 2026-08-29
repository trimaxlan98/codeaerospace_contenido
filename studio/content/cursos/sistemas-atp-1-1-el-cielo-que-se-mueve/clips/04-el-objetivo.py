class Clip4(Scene):
    """1.1.4 - De donde sale el objetivo: el haz. En banda S cabe
    holgado; en Ka, el mismo error casi no cabe. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))
        rot.mostrar(titulo_curso("El objetivo"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        # --- la montura y su haz -----------------------------------------
        mont = montura(alto=2.0)
        mont.apuntar(el_deg=38.0)
        mont.shift(LEFT * 4.35 + DOWN * 1.30 - mont.pivote)
        self.play(FadeIn(mont), run_time=0.9)
        self.wait(0.5)

        # los DOS haces a la MISMA escala angular: si cada uno se dibuja
        # a su escala, el de Ka saldria del tamano del de S y la
        # comparacion mentiria.
        h_s = haz(TH3_S, OBJETIVO_DEG, largo=3.5, escala_ang=ESC_HAZ)
        # el haz SALE del plato: se ancla por su vertice al borde del
        # plato de la montura, o se ve flotando suelto en mitad del cuadro
        boca = mont.plato.get_center() + RIGHT * 0.10 + UP * 0.10
        h_s.shift(boca - h_s.vertice)
        t_s = tag_hud(f"banda S {fmt(TH3_S, 2)} deg", font_size=21)
        t_s.next_to(h_s, DOWN, buff=0.30)

        self.play(Create(h_s.bordes), FadeIn(h_s.sector),
                  Create(h_s.eje), run_time=1.4)
        self.play(FadeIn(h_s.satelite, scale=1.6), FadeIn(t_s),
                  run_time=0.7)
        self.wait(1.4)

        rot.mostrar(cifra_pie(f"haz {fmt(TH3_S, 2)} grados"), zona="abajo")
        self.wait(1.8)
        rot.mostrar(formula_pie(r"\theta_{3dB} \approx 70\,\lambda / D"),
                    zona="abajo")
        self.wait(2.4)

        # --- el mismo error, otra banda ----------------------------------
        h_ka = h_s.gemela(TH3_KA)
        h_ka.shift(boca - h_ka.vertice)
        t_ka = tag_hud(f"banda Ka {fmt(TH3_KA, 2)} deg", font_size=21,
                       color=C_PELIGRO)
        t_ka.move_to(t_s)

        # El SECTOR si es gemelo (misma estructura, otro angulo) y admite
        # Transform. Los dos ROTULOS no lo son -- "banda S 3.18 deg" y
        # "banda Ka 0.23 deg" tienen distinto numero de glifos -- y el
        # Transform los dejaba sin cambiar: en el frame se veia el haz de
        # Ka con la etiqueta de S. Se relevan por fundido, en orden.
        self.play(Transform(h_s, h_ka), run_time=1.8)
        self.play(FadeOut(t_s), run_time=0.30)
        self.play(FadeIn(t_ka), run_time=0.30)
        self.wait(1.8)

        rot.mostrar(cifra_pie(f"mismo error {fmt(OBJETIVO_DEG, 1)} deg"),
                    zona="abajo")
        self.wait(2.2)

        panel = panel_cifras(f"S  {fmt(TH3_S, 2)} deg",
                             (f"Ka {fmt(TH3_KA, 2)} deg", C_PELIGRO),
                             f"objetivo {fmt(OBJETIVO_DEG, 1)} deg")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(2.6)

        # --- el cierre ----------------------------------------------------
        cierre_leccion(self, rot,
                       "Diez minutos al dia.",
                       "Una decima de grado.",
                       mont, h_s, t_ka, panel, espera=4.4)
