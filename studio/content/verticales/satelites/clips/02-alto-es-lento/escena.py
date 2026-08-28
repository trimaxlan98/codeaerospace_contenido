class Clip(Scene):
    """02 · Alto es lento — el periodo manda.

    Cuatro alturas en la misma columna, concentricas y A ESCALA: LEO a 550
    km casi pegado al planeta, los 2000, los 20200 de GPS y la GEO a 35786.
    Los cuatro satelites arrancan a la vez y giran a su ritmo REAL: cuando
    el de abajo lleva vuelta y media, el de arriba no ha hecho ni la decima
    parte. El de arriba parece parado, y por eso la antena de tu casa no se
    mueve.

    Los cuatro periodos los resuelve `satelites.periodo_orbital` con la
    tercera de Kepler durante el render. El de la GEO cae en el dia sidereo
    (23 h 56 min), que es una CONSTANTE: va en gris.
    """

    R_TIERRA = 0.42                   # radio del planeta en unidades
    ALTURAS = (550.0, 2000.0, 20200.0, 35786.0)
    VUELTAS_LEO = 1.5                 # vueltas que da el de abajo en el plano

    def construct(self):
        datos = [sa.periodo_orbital(h) for h in self.ALTURAS]
        t_leo = datos[0]["segundos"]

        marca = hud_pieza("02 . alto es lento")
        tierra = globo(self.R_TIERRA, y=Y_ESCENA, relleno=0.55)
        centro = tierra.get_center()

        anillos, sats = [], []
        for h in self.ALTURAS:
            r = self.R_TIERRA * (1.0 + h / sa.R_TIERRA_KM)
            aro = Circle(radius=r, stroke_color=C_EJE, stroke_width=1.6,
                         stroke_opacity=0.55)
            aro.move_to(centro)
            anillos.append(DashedVMobject(aro, num_dashes=80))
            punto = Dot(radius=0.085, color=C_SAT)
            punto.move_to(centro + RIGHT * r)
            sats.append(punto)

        self.play(FadeIn(marca, shift=DOWN * 0.16), run_time=0.55)
        self.play(GrowFromCenter(tierra), run_time=0.8)

        # --- las cuatro alturas, una a una, con su periodo -----------
        pie = None
        for i, (h, d, aro, punto) in enumerate(zip(self.ALTURAS, datos,
                                                   anillos, sats)):
            if d["minutos"] < 600:
                valor, unidad = f"{d['minutos']:.1f}", "minutos"
            else:
                valor, unidad = f"{d['horas']:.2f}", "horas"
            sub = f"{int(h)} km"
            nuevo = medida(valor, unidad, sub, color=C_MEDIDO,
                           color_sub=C_EXTERNO)
            self.play(Create(aro), FadeIn(punto, scale=1.6), run_time=0.75)
            if pie is None:
                self.play(FadeIn(nuevo.etiqueta), FadeIn(nuevo.sub),
                          FadeIn(nuevo.numero, scale=1.06), run_time=0.5)
            else:
                cambiar(self, [pie.etiqueta, pie.numero, pie.sub],
                        [nuevo.etiqueta, nuevo.numero, nuevo.sub],
                        salida=0.24, entrada=0.28)
            pie = nuevo
            self.wait(0.85 if i < 3 else 0.30)

        # --- y ahora los cuatro a la vez, a su ritmo real -----------
        radios = [self.R_TIERRA * (1.0 + h / sa.R_TIERRA_KM)
                  for h in self.ALTURAS]
        ritmos = [t_leo / d["segundos"] for d in datos]
        grupo = VGroup(*sats)

        def mover(_g, alpha):
            for punto, r, ritmo in zip(sats, radios, ritmos):
                ang = 2.0 * np.pi * alpha * self.VUELTAS_LEO * ritmo
                punto.move_to(centro + r * np.array([np.cos(ang),
                                                     np.sin(ang), 0.0]))

        # Durante el giro, la cifra tiene que hablar DEL GIRO: dejar la de
        # la GEO con un pie que dice "a la vez" empareja un numero con otra
        # cosa, que es la manera mas facil de mentir sin querer.
        lento = medida(f"{datos[-1]['segundos'] / t_leo:.2f}",
                       "veces mas lento", "el de arriba", color=C_MEDIDO,
                       color_sub=C_EXTERNO)
        cambiar(self, [pie.etiqueta, pie.numero, pie.sub],
                [lento.etiqueta, lento.numero, lento.sub],
                salida=0.24, entrada=0.28)
        pie = lento
        self.play(UpdateFromAlphaFunc(grupo, mover), run_time=11.0,
                  rate_func=linear)
        self.wait(0.8)

        # --- el remate: el de arriba no se ha movido ----------------
        vueltas = [self.VUELTAS_LEO * r for r in ritmos]
        # "por cada 1.50 del bajo" medía 6.42 y la zona segura son 5.76: el
        # guardian aborto el render. La cifra no cambia, el rotulo si.
        pie_final = medida(f"{vueltas[-1]:.2f}", "vueltas arriba",
                           f"y {self.VUELTAS_LEO:.2f} abajo", color=C_MEDIDO,
                           color_sub=C_EXTERNO)
        cambiar(self, [pie.etiqueta, pie.numero, pie.sub],
                [pie_final.etiqueta, pie_final.numero, pie_final.sub],
                salida=0.26, entrada=0.30)
        self.play(sats[-1].animate.scale(1.7).set_color("#ffd48a"),
                  run_time=0.7, rate_func=there_and_back)
        self.wait(2.8)

        # --- y por eso la GEO se queda quieta sobre el mismo sitio ---
        pie_geo = medida(f"{datos[-1]['horas']:.3f}", "horas la geo",
                         "el dia sidereo", color=C_MEDIDO,
                         color_sub=C_EXTERNO)
        cambiar(self, [pie_final.etiqueta, pie_final.numero, pie_final.sub],
                [pie_geo.etiqueta, pie_geo.numero, pie_geo.sub],
                salida=0.26, entrada=0.30)
        self.wait(2.6)

        fundido_final(self, run_time=0.9, cola=0.5)
