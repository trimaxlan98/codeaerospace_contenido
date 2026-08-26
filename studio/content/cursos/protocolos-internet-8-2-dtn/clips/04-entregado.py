class Clip4(Scene):
    """8.2.4 - El bundle llega entero horas despues por un camino que nunca
    existio completo; TCP, por esa misma ruta, no entrega nada. Cierre de
    la leccion. (~34 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 04"))

        titulo = titulo_curso("Entregado")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el bundle llega a casa ------------------------------
        rot.mostrar(pie_curso("Salto a salto, con su espera en cada "
                              "custodio, el bundle llega al fin."),
                    zona="abajo", run_time=0.5)
        pos = {"rover": (-4.6, 0.0), "orbitador": (-1.55, 0.0),
               "DSN": (1.55, 0.0), "control": (4.6, 0.0)}
        aristas = {("rover", "orbitador"): None,
                   ("orbitador", "DSN"): None,
                   ("DSN", "control"): None}
        tipos = {"rover": "host", "orbitador": "satelite",
                 "DSN": "router", "control": "servidor"}
        cadena = topologia(pos, aristas, tipos, costos=False, tam=0.46)
        cadena.shift(UP * 1.75)
        self.play(FadeIn(cadena.enlaces), FadeIn(cadena.nodos), run_time=0.9)
        b = ficha("B", lado=0.46, fs=15)
        b.move_to(cadena.punto("rover") + UP * 0.50)
        self.play(FadeIn(b, scale=1.3), run_time=0.4)
        for i, p in enumerate(PASOS):
            self.play(b.animate.move_to(cadena.punto(p["a"]) + UP * 0.50),
                      run_time=0.62)
            et = tag_hud("t = %s h" % fmt(p["t_h"], 2), font_size=17,
                         color=C_CALCULO)
            et.next_to(b, UP, buff=0.16)
            self.play(FadeIn(et), run_time=0.22)
            self.play(FadeOut(et), run_time=0.18)
        self.play(b.animate.set_color(C_OK),
                  cadena.nodo("control").forma.animate.set_stroke(
                      C_OK, width=3.6), run_time=0.4)
        et_ok = cifras_apiladas(
            [("entregado: %s MB enteros y verificados, %s h despues"
              % (fmt(TAM_MB, 0), fmt(DTN["total_h"], 2)), C_OK)],
            fs=21, pos=UP * 0.42)
        self.play(FadeIn(et_ok, shift=0.12 * UP), run_time=0.5)
        self.wait(3.2)

        # --- momento: casi todo el viaje fue estar quieto ------------------
        rot.mostrar(pie_curso("Y casi todo ese viaje fue estar quieto: el "
                              "almacen, no el cable."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(et_ok), run_time=0.3)
        ancho_barra = 8.6
        w_ret = ancho_barra * DTN["retenido_h"] / DTN["total_h"]
        w_enl = ancho_barra - w_ret
        seg_ret = Rectangle(width=w_ret, height=0.46, stroke_width=0.0,
                            fill_color=C_COLA, fill_opacity=0.85)
        seg_enl = Rectangle(width=w_enl, height=0.46, stroke_width=0.0,
                            fill_color=C_OK, fill_opacity=0.95)
        barra = VGroup(seg_ret, seg_enl).arrange(RIGHT, buff=0.0)
        barra.move_to(DOWN * 0.30)
        et_ret = tag_hud("retenido en custodios  %s h" % fmt(
            DTN["retenido_h"], 2), font_size=20, color=CODE_BG)
        et_ret.move_to(seg_ret.get_center())
        et_enl = tag_hud("en el enlace  %s h" % fmt(EN_ENLACE_H, 2),
                         font_size=19, color=C_OK)
        et_enl.next_to(seg_enl, UP, buff=0.30)
        flecha = Line(et_enl.get_bottom() + DOWN * 0.04,
                      seg_enl.get_top() + UP * 0.04, color=C_OK,
                      stroke_width=2.0)
        self.play(GrowFromEdge(barra, LEFT), run_time=0.8)
        self.play(FadeIn(et_ret), FadeIn(et_enl), Create(flecha),
                  run_time=0.5)
        et_pct = tag_hud("%s %% del viaje total (%s h) fue espera"
                         % (fmt(PCT_RETENIDO, 0), fmt(DTN["total_h"], 2)),
                         font_size=21, color=C_CALCULO)
        et_pct.move_to(DOWN * 1.30)
        self.play(FadeIn(et_pct), run_time=0.5)
        self.wait(3.6)

        # --- momento: la comparacion honesta ------------------------------
        rot.mostrar(pie_curso("Misma ruta y mismo plan: TCP no entrega nada "
                              "nunca; DTN entrega entero."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(barra), FadeOut(et_ret), FadeOut(et_enl),
                  FadeOut(flecha), FadeOut(et_pct), run_time=0.4)
        comp = tabla(["protocolo", "entrega", "cuando"],
                     [["TCP", "nada, nunca", "-"],
                      ["DTN", "%s MB enteros" % fmt(TAM_MB, 0),
                       "%s h" % fmt(DTN["total_h"], 2)]],
                     anchos=[2.2, 3.0, 2.0], alto=0.56, fs=19)
        comp.move_to(DOWN * 0.35)
        for j in range(3):
            comp.celda(0, j).set_color(C_PERDIDA)
            comp.celda(1, j).set_color(C_OK)
        self.play(FadeIn(comp), run_time=0.7)
        et_por = tag_hud("por un camino que no existio completo ni un "
                         "instante", font_size=20, color=C_TENUE)
        et_por.move_to(DOWN * 1.85)
        self.play(FadeIn(et_por), run_time=0.5)
        self.wait(3.8)

        # --- cierre de la leccion -----------------------------------------
        cierre_leccion(
            self, rot,
            "Internet supone que siempre hay camino.",
            "Fuera de casa, esa suposicion se cae.",
            "Siguiente: Internet interplanetario, CCSDS y Marte.",
            comp, et_por, cadena, b, espera=4.6)
