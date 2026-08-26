class Clip1(Scene):
    """8.2.1 - Tres tramos que nunca estan vivos a la vez: el apreton de
    TCP no falla por mala suerte, falla por definicion. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El enlace que no esta")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la cadena hasta casa --------------------------------
        rot.mostrar(pie_curso("Un rover al otro lado de Marte. Entre el y "
                              "casa hay tres tramos, no un cable."),
                    zona="abajo", run_time=0.5)
        pos = {"rover": (-4.6, 0.0), "orbitador": (-1.55, 0.0),
               "DSN": (1.55, 0.0), "control": (4.6, 0.0)}
        aristas = {("rover", "orbitador"): None,
                   ("orbitador", "DSN"): None,
                   ("DSN", "control"): None}
        tipos = {"rover": "host", "orbitador": "satelite",
                 "DSN": "router", "control": "servidor"}
        cadena = topologia(pos, aristas, tipos, costos=False, tam=0.46)
        cadena.shift(UP * 2.05)
        self.play(FadeIn(cadena.enlaces), FadeIn(cadena.nodos), run_time=1.1)
        self.wait(4.0)

        # --- momento: el plan de contactos --------------------------------
        rot.mostrar(pie_curso("Cada tramo solo existe a ratos. El plan de "
                              "contactos dice exactamente cuando."),
                    zona="abajo", run_time=0.5)
        plan = plan_contactos()
        plan.move_to(DOWN * 0.45)
        self.play(Create(plan.mobiliario), FadeIn(plan.carriles),
                  FadeIn(plan.etiquetas), run_time=1.0)
        self.play(LaggedStart(*[GrowFromEdge(b, LEFT) for b in plan.barras],
                              lag_ratio=0.4), run_time=1.4)
        cifras = cifras_apiladas(
            [("%d ventanas: %s h con enlace de %s = %s %%"
              % (VENT["n"], fmt(VENT["horas_con_enlace"], 1),
                 fmt(VENT["horas_totales"], 0),
                 fmt(VENT["pct_con_enlace"], 0)), C_CALCULO),
             ("huecos: de %s a %s h, y de %s a %s h"
              % (fmt(HUECO_LARGO[0], 1), fmt(HUECO_LARGO[1], 1),
                 fmt(HUECO_CORTO[0], 1), fmt(HUECO_CORTO[1], 1)),
              C_PERDIDA)],
            fs=20, pos=DOWN * 2.35)
        self.play(FadeIn(cifras, shift=0.12 * UP), run_time=0.6)
        self.wait(3.8)

        # --- momento: ningun instante tiene la ruta entera ----------------
        rot.mostrar(pie_curso("Mira cualquier instante: como mucho hay UN "
                              "tramo vivo, nunca los tres."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(cifras), run_time=0.35)
        alto_barrido = (y_carril(plan, 0) - y_carril(plan, 2)) / 2.0 + 0.28
        centro_y = (y_carril(plan, 0) + y_carril(plan, 2)) / 2.0
        linea = Line(np.array([x_hora(plan, 0), centro_y + alto_barrido, 0.0]),
                     np.array([x_hora(plan, 0), centro_y - alto_barrido, 0.0]),
                     color=C_TITULO, stroke_width=3.0)
        et_ahora = tag_hud("ahora", font_size=17, color=C_TITULO)
        et_ahora.next_to(linea, UP, buff=0.10)
        ahora = VGroup(linea, et_ahora)
        self.play(FadeIn(ahora), run_time=0.4)
        self.play(ahora.animate.shift(
            RIGHT * (x_hora(plan, H_FIN) - x_hora(plan, H_INI))),
            run_time=3.2, rate_func=linear)
        veredicto = tag_hud("no hay camino completo en NINGUN instante",
                            font_size=22, color=C_PERDIDA)
        veredicto.move_to(DOWN * 2.35)
        self.play(FadeIn(veredicto), run_time=0.5)
        self.wait(3.4)

        # --- momento: el SYN que no tiene a quien saludar ------------------
        rot.mostrar(pie_curso("Por eso el apreton de TCP no falla por mala "
                              "suerte aqui: falla por definicion."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(veredicto), FadeOut(ahora), run_time=0.35)
        syn = ficha(SYN["flags"], lado=0.52, fs=14)
        syn.move_to(cadena.punto("rover") + UP * 0.46)
        self.play(FadeIn(syn, scale=1.3), run_time=0.45)
        self.play(syn.animate.move_to(cadena.punto("orbitador") + UP * 0.46),
                  run_time=1.0)
        corte = cruz((cadena.punto("orbitador") + cadena.punto("DSN")) / 2.0)
        self.play(FadeIn(corte, scale=1.5), run_time=0.4)
        self.play(syn.animate.set_color(C_PERDIDA), run_time=0.35)
        razon = cifras_apiladas(
            [("SYN seq %d enviado: nadie al otro lado" % SYN["seq"],
              C_PERDIDA),
             (SIN_CAMINO["por_que"], C_TENUE)],
            fs=20, pos=DOWN * 2.35)
        self.play(FadeIn(razon, shift=0.12 * UP), run_time=0.6)
        self.wait(4.4)
