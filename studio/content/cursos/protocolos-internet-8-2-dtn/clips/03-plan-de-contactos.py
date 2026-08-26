class Clip3(Scene):
    """8.2.3 - El ruteo por grafo de contactos no busca por donde, sino
    cuando: el bundle espera su ventana, y la espera se mide. (~29 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 03"))
        DY_B = 0.30          # el bundle viaja SOBRE su carril

        def _rel_a(h):
            return reloj_h(h).move_to(DOWN * 1.25)

        titulo = titulo_curso("Plan de contactos")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: el mapa tiene reloj ---------------------------------
        rot.mostrar(pie_curso("Rutear aqui no es saber por donde. Es saber "
                              "cuando."),
                    zona="abajo", run_time=0.5)
        filas = [["%s > %s" % (v["de"], v["a"]), fmt(v["desde"], 1),
                  fmt(v["hasta"], 1), fmt(v["horas"], 1)]
                 for v in VENT["ventanas"]]
        t_plan = tabla(["tramo", "desde h", "hasta h", "dura h"], filas,
                       anchos=[3.4, 1.7, 1.7, 1.7], alto=0.52, fs=18)
        t_plan.move_to(UP * 0.35)
        for i in range(len(filas)):        # `Tabla` pinta la fila
            for j in (1, 2, 3):            # entera: las cifras se
                t_plan.celda(i, j).set_color(C_CALCULO)   # repintan
        self.play(FadeIn(t_plan), run_time=0.8)
        self.wait(4.4)

        # --- momento: el primer salto sale en su ventana -------------------
        rot.mostrar(pie_curso("El bundle sale en la primera ventana: el "
                              "orbitador esta ahi ahora."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(t_plan), run_time=0.4)
        plan = plan_contactos()
        plan.move_to(UP * 0.75)
        self.play(FadeIn(plan), run_time=0.9)
        b = ficha("B", lado=0.36, fs=15)
        b.move_to(en_plan(plan, 0.0, 0, dy=DY_B))
        rel = reloj_h(0.0)
        rel.move_to(DOWN * 1.25)
        self.play(FadeIn(b, scale=1.6), FadeIn(rel), run_time=0.5)
        lineas = cifras_apiladas(
            [("salto %d   %-19s espera %s h"
              % (i + 1, "%s > %s" % (p["de"], p["a"]),
                 fmt(p["espera_h"], 2)), C_CALCULO)
             for i, p in enumerate(PASOS)],
            fs=18, buff=0.15, pos=DOWN * 2.25)
        self.play(b.animate.move_to(en_plan(plan, T_SALTO[0], 1,
                                            dy=DY_B)), run_time=0.8)
        self.play(Transform(rel, _rel_a(T_SALTO[0])), run_time=0.12)
        self.play(FadeIn(lineas[0]), run_time=0.4)
        self.wait(2.6)

        # --- momento: la espera larga se mide ------------------------------
        rot.mostrar(pie_curso("Y ahi se para. No hay ruta que buscar: hay "
                              "una ventana que esperar."),
                    zona="abajo", run_time=0.5)
        for k in range(1, 11):
            h = T_SALTO[0] + (PASOS[1]["ventana"][0] - T_SALTO[0]) * k / 10.0
            self.play(Transform(rel, _rel_a(h)), run_time=0.10)
            self.play(b.animate.move_to(en_plan(plan, h, 1, dy=DY_B)),
                      run_time=0.22)
        barra2 = Rectangle(width=x_hora(plan, PASOS[1]["ventana"][0]) -
                           x_hora(plan, T_SALTO[0]), height=0.09,
                           stroke_width=0.0, fill_color=C_COLA,
                           fill_opacity=0.9)
        barra2.move_to(en_plan(plan, (T_SALTO[0] + PASOS[1]["ventana"][0])
                               / 2.0, 1, dy=-0.26))
        self.play(GrowFromEdge(barra2, LEFT), FadeIn(lineas[1]), run_time=0.6)
        self.wait(2.6)

        # --- momento: el ultimo tramo y la entrega -------------------------
        rot.mostrar(pie_curso("Otra espera, mas corta, y el ultimo tramo. El "
                              "plan no busca el camino corto."),
                    zona="abajo", run_time=0.5)
        self.play(b.animate.move_to(en_plan(plan, T_SALTO[1], 2,
                                            dy=DY_B)), run_time=0.6)
        self.play(Transform(rel, _rel_a(T_SALTO[1])), run_time=0.12)
        for k in range(1, 6):
            h = T_SALTO[1] + (PASOS[2]["ventana"][0] - T_SALTO[1]) * k / 5.0
            self.play(Transform(rel, _rel_a(h)), run_time=0.10)
            self.play(b.animate.move_to(en_plan(plan, h, 2, dy=DY_B)),
                      run_time=0.22)
        barra3 = Rectangle(width=x_hora(plan, PASOS[2]["ventana"][0]) -
                           x_hora(plan, T_SALTO[1]), height=0.09,
                           stroke_width=0.0, fill_color=C_COLA,
                           fill_opacity=0.9)
        barra3.move_to(en_plan(plan, (T_SALTO[1] + PASOS[2]["ventana"][0])
                               / 2.0, 2, dy=-0.26))
        self.play(GrowFromEdge(barra3, LEFT), FadeIn(lineas[2]), run_time=0.6)
        self.play(b.animate.move_to(en_plan(plan, T_SALTO[2], 2, dy=DY_B))
                  .set_color(C_OK), run_time=0.5)
        self.play(Transform(rel, _rel_a(T_SALTO[2])), run_time=0.12)
        et_ent = tag_hud("entregado a las %s h" % fmt(DTN["total_h"], 2),
                         font_size=21, color=C_OK)
        et_ent.next_to(rel, RIGHT, buff=0.70)
        self.play(FadeIn(et_ent), run_time=0.5)
        self.wait(3.6)
