class Clip2(Scene):
    """3.3.2 - El MISMO error de 0.1 grados sobre el MISMO plato: en
    banda S se pierden 0.012 dB y en Ka 2.21 dB. Ciento ochenta y seis
    veces mas por cambiar de banda, no de antena. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        rot.mostrar(titulo_curso("S contra Ka"), zona="arriba",
                    run_time=0.6)
        self.wait(0.3)

        X0 = -5.05           # vertice de los dos haces: el MISMO plato
        LARGO = 3.90         # el haz acaba en x = -1.15: deja sitio
        V_S = np.array([X0, 1.30, 0.0])
        V_KA = np.array([X0, -1.85, 0.0])

        def platito(v):
            """El reflector de 3 m dibujado dos veces: es el mismo plato,
            solo cambia la banda que alimenta."""
            r = 0.30
            a = Arc(radius=r, start_angle=PI * 0.72, angle=PI * 0.56,
                    color=C_CALCULO, stroke_width=4.0)
            a.move_arc_center_to(v + RIGHT * r)
            a.shift(LEFT * 0.10)
            return a

        p_s, p_ka = platito(V_S), platito(V_KA)
        self.play(FadeIn(p_s), FadeIn(p_ka), run_time=0.7)

        # --- los dos haces, a la MISMA escala angular --------------------
        # ESC_HAZ es la misma para los dos: si cada uno se dibujara a su
        # escala el de Ka saldria del tamano del de S y la comparacion
        # mentiria. Dibujados asi, el de Ka es un pelo.
        h_s = haz(TH3_S, error_deg=OBJETIVO_DEG, largo=LARGO,
                  escala_ang=ESC_HAZ)
        h_s.shift(V_S - h_s.vertice)
        h_ka = haz(TH3_KA, error_deg=OBJETIVO_DEG, largo=LARGO,
                   escala_ang=ESC_HAZ)
        h_ka.shift(V_KA - h_ka.vertice)

        # Los rotulos viven en el pasillo entre la punta de los haces
        # (x = -1.15) y las barras (x = 3.4): con el haz largo, "deg" se
        # subia al eje de la grafica.
        t_s = tag_hud(f"banda S {fmt(TH3_S, 2)} deg", font_size=21)
        t_s.move_to(RIGHT * 1.15 + UP * 1.28)
        t_ka = tag_hud(f"banda Ka {fmt(TH3_KA, 2)} deg", font_size=21,
                       color=C_PELIGRO)
        t_ka.move_to(RIGHT * 1.15 + DOWN * 1.42)

        self.play(Create(h_s.bordes), FadeIn(h_s.sector), Create(h_s.eje),
                  run_time=1.3)
        self.play(FadeIn(t_s), run_time=0.5)
        self.wait(0.8)
        self.play(Create(h_ka.bordes), FadeIn(h_ka.sector),
                  Create(h_ka.eje), run_time=1.3)
        self.play(FadeIn(t_ka), run_time=0.5)
        self.wait(1.0)

        rot.mostrar(cifra_pie(f"mismo plato {fmt(D_PLATO, 0)} m"),
                    zona="abajo")
        self.wait(2.2)

        # --- el mismo error, dibujado igual en los dos -------------------
        self.play(FadeIn(h_s.satelite, scale=1.8),
                  FadeIn(h_ka.satelite, scale=1.8), run_time=0.8)
        self.wait(0.6)
        rot.mostrar(cifra_pie(f"mismo error {fmt(OBJETIVO_DEG, 1)} grados"),
                    zona="abajo")
        self.wait(1.6)
        # en S el satelite queda pegado al eje de un cono ancho; en Ka, el
        # mismo desvio lo deja rozando el borde del haz.
        self.play(Indicate(h_s.satelite, color=C_SAT, scale_factor=2.2),
                  run_time=0.9)
        self.play(Indicate(h_ka.satelite, color=C_SAT, scale_factor=2.2),
                  run_time=0.9)
        self.wait(1.4)

        # --- lo que cuesta, banda a banda --------------------------------
        l_s = tag_hud(f"{fmt(L_S, 3)} dB", font_size=22)
        l_s.move_to(RIGHT * 1.15 + UP * 0.70)
        l_ka = tag_hud(f"{fmt(L_KA, 2)} dB", font_size=22, color=C_PELIGRO)
        l_ka.move_to(RIGHT * 1.15 + DOWN * 2.00)

        rot.mostrar(cifra_pie(f"banda S {fmt(L_S, 3)} dB"), zona="abajo")
        self.play(FadeIn(l_s), run_time=0.5)
        self.wait(1.9)
        rot.mostrar(cifra_pie(f"banda Ka {fmt(L_KA, 2)} dB",
                              color=C_PELIGRO), zona="abajo")
        self.play(FadeIn(l_ka), run_time=0.5)
        self.wait(2.1)

        # --- la razon, en escala log (la pieza lo rotula sola) -----------
        barras = barras_comparar([L_S, L_X, L_KA], ["S", "X", "Ka"],
                                 ancho=3.0, alto=1.8, log=True,
                                 unidad="dB",
                                 colores=[C_CALCULO, C_CALCULO, C_PELIGRO])
        barras.move_to(RIGHT * 4.90 + DOWN * 1.45)
        self.play(FadeIn(barras), run_time=0.9)
        self.wait(1.9)

        rot.mostrar(cifra_pie(f"{fmt(RAZON_KA, 0)} veces mas"),
                    zona="abajo")
        self.wait(2.4)
        # y al reves: en Ka, gastar solo una decima de dB exige veinte
        # veces menos error del que da un rotor comercial.
        rot.mostrar(cifra_pie(f"Ka admite {fmt(ERR_KA_ADMISIBLE, 3)} deg"),
                    zona="abajo")
        self.wait(2.4)

        panel = panel_cifras(f"S  {fmt(L_S, 3)} dB",
                             (f"Ka {fmt(L_KA, 2)} dB", C_PELIGRO),
                             f"razon {fmt(RAZON_KA, 0)}x")
        self.play(FadeIn(panel), run_time=0.7)
        self.wait(3.4)
