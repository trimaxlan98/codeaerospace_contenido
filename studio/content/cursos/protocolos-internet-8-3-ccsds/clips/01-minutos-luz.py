class Clip1(Scene):
    """8.3.1 - El retardo a Marte no es una cifra: es un rango que da la
    vuelta al ano, de 4.3 a 21.0 minutos luz de ida. (~31 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Minutos luz")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: la curva del ano ------------------------------------
        rot.mostrar(pie_curso("El retardo a Marte no es un numero: cambia "
                              "con la posicion de los dos planetas."),
                    zona="abajo", run_time=0.5)
        gr = grafica(IDA_EN, (UA_CERCA, UA_LEJOS), (0.0, 22.0),
                     ancho=7.4, alto=3.4, color=C_CIFRA, muestras=61,
                     etiqueta_x="distancia (UA)",
                     etiqueta_y="minutos luz de ida")
        gr.shift(UP * 0.45 + LEFT * 0.45)
        # Las etiquetas de los ejes son hijos internos de `Grafica`: si se
        # animan `.ejes` y `.curva` por separado, no salen.
        rotulos_ejes = VGroup(*[m for m in gr.submobjects
                                if m is not gr.ejes and m is not gr.curva])
        self.play(FadeIn(gr.ejes), FadeIn(rotulos_ejes), run_time=0.6)
        self.play(Create(gr.curva), run_time=1.4)
        self.wait(4.6)

        # --- momento: los dos extremos del ano ----------------------------
        rot.mostrar(pie_curso("De la oposicion a la conjuncion la distancia "
                              "se multiplica casi por cinco."),
                    zona="abajo", run_time=0.5)
        d_cerca = Dot(gr.punto_de(UA_CERCA), radius=0.075, color=C_OK)
        d_lejos = Dot(gr.punto_de(UA_LEJOS), radius=0.075, color=C_PERDIDA)
        et_cerca = VGroup(
            tag_hud("%s min luz" % fmt(IDA_CERCA, 1), font_size=19),
            tag_hud("%s millones de km" % fmt(KM_CERCA / 1e6, 0),
                    font_size=14, color=C_TENUE),
        # El punto cercano cae en la esquina del plano (sobre el eje Y):
        # cualquier rotulo a su derecha lo tacha la curva y cualquiera
        # debajo lo tacha el eje X. Fuera del plano, a la izquierda.
        ).arrange(DOWN, buff=0.12, aligned_edge=RIGHT)
        et_cerca.next_to(d_cerca, LEFT, buff=0.22)
        et_lejos = VGroup(
            tag_hud("%s min luz" % fmt(IDA_LEJOS, 1), font_size=19),
            tag_hud("%s millones de km" % fmt(KM_LEJOS / 1e6, 0),
                    font_size=14, color=C_TENUE),
        ).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        et_lejos.next_to(d_lejos, RIGHT, buff=0.22)
        self.play(FadeIn(d_cerca, scale=1.6), FadeIn(d_lejos, scale=1.6),
                  run_time=0.5)
        self.play(FadeIn(et_cerca, shift=0.10 * UP),
                  FadeIn(et_lejos, shift=0.10 * UP), run_time=0.7)
        self.wait(4.8)

        # --- momento: un ping son dos viajes ------------------------------
        rot.mostrar(pie_curso("Un ping son dos viajes. Aqui estan el mejor y "
                              "el peor caso, dibujados a escala."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(gr.ejes), FadeOut(gr.curva),
                  FadeOut(rotulos_ejes), FadeOut(d_cerca), FadeOut(d_lejos),
                  FadeOut(et_cerca), FadeOut(et_lejos), run_time=0.7)
        r_cerca = regla_viajes(2, etiqueta="cerca",
                               ancho_viaje=IDA_CERCA * ESCALA_MIN, alto=0.46,
                               fs=14, nombres=["ida", "vuelta"])
        r_lejos = regla_viajes(2, etiqueta="lejos",
                               ancho_viaje=IDA_LEJOS * ESCALA_MIN, alto=0.46,
                               fs=14, nombres=["ida", "vuelta"])
        # Las dos reglas comparten borde izquierdo: asi la LONGITUD es el
        # tiempo y las dos se comparan a ojo.
        r_cerca.move_to(UP * 1.42)
        r_lejos.move_to(UP * 0.38)
        for r in (r_cerca, r_lejos):
            r.shift(RIGHT * (X_REGLAS - r.viaje(0).get_left()[0]))
        ms_cerca = tag_hud("%s min de ida y vuelta" % fmt(RTT_CERCA, 1),
                           font_size=20)
        ms_cerca.next_to(r_cerca.viaje(1), RIGHT, buff=0.32)
        ms_lejos = tag_hud("%s min de ida y vuelta" % fmt(RTT_LEJOS, 1),
                           font_size=20)
        ms_lejos.next_to(r_lejos.viaje(1), RIGHT, buff=0.32)
        self.play(FadeIn(r_cerca), FadeIn(ms_cerca), run_time=0.6)
        self.play(FadeIn(r_lejos), FadeIn(ms_lejos), run_time=0.6)
        self.wait(4.8)

        # --- momento: contra el peor retardo de la Tierra ------------------
        rot.mostrar(pie_curso("El mejor caso de Marte es lo que la Tierra no "
                              "ve jamas, ni por satelite."),
                    zona="abajo", run_time=0.5)
        cifras = VGroup(
            tag_hud("GEO, el peor RTT de Internet   %s ms"
                    % fmt(GEO_RTT_MS, 1), font_size=20),
            tag_hud("Marte, el MEJOR de los casos   %s min"
                    % fmt(RTT_CERCA, 1), font_size=20, color=C_PAQUETE),
            tag_hud("uno cabe en el otro            %s veces"
                    % fmt(VECES_GEO, 0), font_size=20),
        ).arrange(DOWN, buff=0.22, aligned_edge=LEFT)
        cifras.move_to(DOWN * 1.42)
        self.play(LaggedStart(*[FadeIn(c, shift=0.12 * UP) for c in cifras],
                              lag_ratio=0.35), run_time=1.5)
        self.wait(5.4)
