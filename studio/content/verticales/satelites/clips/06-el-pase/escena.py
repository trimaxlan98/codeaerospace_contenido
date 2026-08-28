class Clip(Scene):
    """06 · El pase — lo que ves desde el suelo.

    La misma orbita, desde abajo. La boveda polar es el cielo entero visto
    en planta: el borde es el horizonte y el centro, justo encima de tu
    cabeza. El satelite entra por un lado, sube casi al cenit y se va. Dura
    ocho minutos y cuarto, y son el 8.6 % de lo que tarda en dar la vuelta.

    El pase lo mide `satelites.pase`, que barre el NODO del plano orbital
    para quedarse con el mas alto (barrer la fase no sirve: recorre la misma
    traza desde otro punto). El azimut sale de `satelites.azimut`.
    """

    ALTURA_KM = 550.0
    EL_MIN = 10.0
    LAT, LON = 19.43, -99.13          # una estacion cualquiera
    R_BOVEDA = 2.45

    def construct(self):
        p = sa.pase(self.LAT, self.LON, self.ALTURA_KM, 53.0, self.EL_MIN)
        i, j, k = p["indices"]
        az, el = p["azimut"][i:j + 1], p["elevacion"][i:j + 1]
        centro = UP * (Y_ESCENA + 0.35)

        def cielo(az_deg, el_deg):
            """(azimut, elevacion) -> punto de la boveda. Norte arriba, el
            este a la derecha: el cielo se dibuja en planta."""
            r = self.R_BOVEDA * (1.0 - np.clip(el_deg, 0.0, 90.0) / 90.0)
            a = np.radians(90.0 - az_deg)
            return centro + r * np.array([np.cos(a), np.sin(a), 0.0])

        marca = hud_pieza("06 . el pase")
        aros = VGroup()
        for grados, ancho in ((0.0, 2.6), (30.0, 1.4), (60.0, 1.4)):
            aro = Circle(radius=self.R_BOVEDA * (1.0 - grados / 90.0),
                         stroke_color=C_EJE, stroke_width=ancho,
                         stroke_opacity=0.9 if grados == 0 else 0.55)
            aro.move_to(centro)
            aros.add(aro)
        cruz = VGroup(
            Line(cielo(0, 0), cielo(180, 0), stroke_color=C_EJE,
                 stroke_width=1.2, stroke_opacity=0.4),
            Line(cielo(90, 0), cielo(270, 0), stroke_color=C_EJE,
                 stroke_width=1.2, stroke_opacity=0.4))
        cardinales = VGroup()
        for texto, grados in (("n", 0.0), ("e", 90.0), ("s", 180.0),
                              ("o", 270.0)):
            t = hud(texto, font_size=17, color=C_EXTERNO)
            t.move_to(cielo(grados, 0) * 1.0
                      + (cielo(grados, 0) - centro) * 0.13)
            cardinales.add(t)
        estacion = Dot(centro, radius=0.07, color=C_TIERRA)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(Create(aros[0]), FadeIn(estacion, scale=1.6), run_time=0.9)
        self.play(Create(aros[1]), Create(aros[2]), Create(cruz),
                  FadeIn(cardinales), run_time=1.0)
        self.wait(0.5)

        # --- el pase, punto a punto ---------------------------------
        pts = np.array([cielo(a, e) for a, e in zip(az, el)])
        arco = poli(pts[:, :2], color=C_SAT, grosor=3.4, suave=True)
        sat = Dot(pts[0], radius=0.10, color=C_SAT).set_z_index(20)
        pie = medida(f"{p['el_max_deg']:.1f}", "grados de altura",
                     "casi el cenit", color=C_MEDIDO, color_sub=C_SAT)
        vivos = [pie.etiqueta, pie.numero, pie.sub]

        self.play(FadeIn(sat, scale=2.0), run_time=0.4)
        self.play(Create(arco), MoveAlongPath(sat, arco), run_time=6.5,
                  rate_func=linear)
        self.play(*[FadeIn(m) for m in vivos], run_time=0.55)
        self.play(sat.animate.scale(1.8).set_opacity(0.0), run_time=0.6)
        self.wait(2.4)

        minutos = medida(f"{p['duracion_min']:.2f}", "minutos de pase",
                         "de un lado a otro", color=C_MEDIDO,
                         color_sub=C_EXTERNO)
        nuevos = [minutos.etiqueta, minutos.numero, minutos.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(3.0)

        # --- y a la vuelta siguiente ya no pasa por aqui ------------
        # Se busco el pase de las vueltas +1, +2, +3, -1 y -2 desde la misma
        # estacion: NO HAY NINGUNO. La razon es una resta, y se enseña: la
        # traza se corre 2662 km al oeste y la huella solo alcanza 1664.
        corr = sa.corrimiento_traza(self.ALTURA_KM)
        alcance = sa.radio_huella_km(self.ALTURA_KM, self.EL_MIN)
        escala_barra = 2.05 / corr["km_ecuador"]
        y_base = 0.15
        x_a, x_b = -1.35, 1.35
        rot_a = hud("se corre", font_size=18, color=C_PERDIDO)
        rot_b = hud("alcanza", font_size=18, color=C_ENLACE)
        alto_a = corr["km_ecuador"] * escala_barra
        alto_b = alcance * escala_barra
        rot_a.move_to([x_a, y_base + alto_a + 0.40, 0])
        rot_b.move_to([x_b, y_base + alto_a + 0.40, 0])
        barra_a = Rectangle(width=0.70, height=alto_a, stroke_width=0,
                            fill_color=C_PERDIDO, fill_opacity=0.85)
        barra_b = Rectangle(width=0.70, height=alto_b, stroke_width=0,
                            fill_color=C_ENLACE, fill_opacity=0.85)
        barra_a.move_to([x_a, y_base + alto_a / 2, 0])
        barra_b.move_to([x_b, y_base + alto_b / 2, 0])

        oeste = medida(f"{corr['km_ecuador']:.0f}", "km al oeste",
                       f"huella: {alcance:.0f} km", color=C_MEDIDO,
                       color_sub=C_ENLACE)
        nuevos = [oeste.etiqueta, oeste.numero, oeste.sub]
        self.play(FadeOut(arco), FadeOut(aros), FadeOut(cruz),
                  FadeOut(cardinales), FadeOut(estacion), run_time=0.7)
        self.play(FadeIn(rot_a), FadeIn(rot_b), run_time=0.45)
        for barra, alto, x in ((barra_a, alto_a, x_a), (barra_b, alto_b, x_b)):
            barra.save_state()
            barra.stretch_to_fit_height(0.02)
            barra.move_to([x, y_base + 0.01, 0])
        self.add(barra_a, barra_b)
        self.play(Restore(barra_a), Restore(barra_b), run_time=1.5,
                  rate_func=rate_functions.ease_out_cubic)
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        vivos = nuevos
        self.wait(5.0)

        # --- por eso lo ves tan poco --------------------------------
        fraccion = medida(f"{100 * p['fraccion_del_periodo']:.1f}",
                          "por ciento", "de su orbita",
                          color=C_MEDIDO, color_sub=C_PERDIDO)
        nuevos = [fraccion.etiqueta, fraccion.numero, fraccion.sub]
        cambiar(self, vivos, nuevos, salida=0.24, entrada=0.30)
        self.wait(3.0)

        for mob in self.mobjects:
            mob.clear_updaters()
        self.play(*[FadeOut(m) for m in self.mobjects], run_time=0.9)
        self.remove(*self.mobjects)
        self.wait(0.5)
