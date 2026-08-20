class Clip3(Scene):
    """1.1.3 - Cortar el paisaje a alturas fijas y aplastar los cortes al
    suelo: el mapa topografico de curvas de nivel. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))

        titulo = titulo_curso("El mapa: curvas de nivel")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: cortar a una altura fija ----------------------------
        esp = espacio_leccion()
        sup = superficie3(esp, PAISAJE, n=15, opacidad=0.5)
        self.play(FadeIn(esp), FadeIn(sup), run_time=1.0)
        rot.mostrar(pie_curso("Cortemos el paisaje a una altura fija, "
                              "como quien rebana."), zona="abajo",
                    run_time=0.5)
        nivel = NIVEL_PASEO
        e = 2.6
        tapa = Polygon(esp.p(-e, -e, nivel), esp.p(e, -e, nivel),
                       esp.p(e, e, nivel), esp.p(-e, e, nivel),
                       stroke_color=C_CIFRA, stroke_width=1.6,
                       stroke_opacity=0.7, fill_color=C_CIFRA,
                       fill_opacity=0.12)
        self.play(FadeIn(tapa, shift=0.3 * DOWN), run_time=1.0)
        corte = curva_nivel3(esp, PAISAJE, nivel, n=70, color=C_VEC)
        cifra = tag_hud(f"altura = {fmt(nivel)}", font_size=20, color=C_VEC)
        cifra.to_corner(UR, buff=0.55).shift(DOWN * 0.5)
        self.play(Create(corte), FadeIn(cifra), run_time=1.2)
        self.wait(3.2)

        # --- momento: todos los cortes, aplastados al suelo ---------------
        rot.mostrar(pie_curso("El corte deja una curva. Aplastémosla al "
                              "suelo, y con ella a sus hermanas."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(tapa), run_time=0.4)
        cortes = VGroup(corte)
        for nv in (NIVELES[1], NIVELES[4]):
            c = curva_nivel3(esp, PAISAJE, nv, n=70,
                             color=color_calor(nv / Z_MAX), grosor=2.6)
            cortes.add(c)
            self.play(Create(c), run_time=0.7)
        aplastados = VGroup(*[
            curva_nivel3(esp, PAISAJE, nv, n=70, en_altura=False,
                         color=color_calor(nv / Z_MAX), grosor=2.6)
            for nv in (nivel, NIVELES[1], NIVELES[4])])
        self.play(Transform(cortes, aplastados), run_time=1.8)
        self.wait(3.0)

        # --- momento: el mapa completo en 2D ------------------------------
        rot.mostrar(pie_curso("Visto desde arriba, eso es un mapa "
                              "topográfico: las curvas de nivel."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(sup), FadeOut(cortes), FadeOut(esp),
                  FadeOut(cifra), run_time=0.9)
        pl = plano_leccion()
        mapa = curvas_nivel(pl, PAISAJE, niveles=NIVELES, n=100)
        leyenda = VGroup()
        for nv in NIVELES:
            fila = VGroup(Dot(radius=0.055, color=color_calor(nv / Z_MAX)),
                          tag_hud(fmt(nv), font_size=16,
                                  color=color_calor(nv / Z_MAX)))
            fila.arrange(RIGHT, buff=0.12)
            leyenda.add(fila)
        panel = panel_derecha(*leyenda[::-1], buff=0.14)
        self.play(FadeIn(pl), run_time=0.7)
        self.play(LaggedStart(*[Create(c) for c in mapa.curvas],
                              lag_ratio=0.2), run_time=2.4)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.6)
        self.wait(3.4)

        rot.mostrar(pie_curso("Donde las curvas se aprietan, el terreno "
                              "empina; donde se separan, es llano."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(mapa.curvas[4], scale_factor=1.03), run_time=0.8)
        self.wait(4.2)
