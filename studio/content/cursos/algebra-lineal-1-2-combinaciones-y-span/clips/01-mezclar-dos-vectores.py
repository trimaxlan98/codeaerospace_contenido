class Clip1(Scene):
    """1.2.1 - Mezclar u y v con escalares a, b: cada pareja (a, b) manda la
    punta de a*u + b*v a un punto distinto del plano. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("Mezclar dos vectores")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: u y v ---------------------------------------------
        pl = plano_leccion(vivo=False)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Dos vectores, u y v. Cada uno con su propio "
                              "escalar: a y b."), zona="abajo", run_time=0.5)
        u = vector(pl, U_COMB, color=C_VEC, nombre=r"\vec u")
        v = vector(pl, V_COMB, color=C_VEC_2, nombre=r"\vec v")
        self.play(GrowArrow(u.flecha), GrowArrow(v.flecha), run_time=0.9)
        self.play(FadeIn(u.etiqueta), FadeIn(v.etiqueta), run_time=0.3)
        self.wait(3.4)

        # --- momento: la primera combinacion ------------------------------
        rot.mostrar(pie_curso("a*u + b*v: se estira cada uno por su "
                              "escalar y se ponen cola con punta."),
                    zona="abajo", run_time=0.5)
        a0, b0 = PAREJAS[0]
        comb = combinacion(pl, a0, U_COMB, b0, V_COMB, color_res=C_IMG,
                           color_u=C_VEC, color_v=C_VEC_2)
        cifra_a = tag_hud(f"a = {fmt(a0)}", font_size=20, color=C_VEC)
        cifra_b = tag_hud(f"b = {fmt(b0)}", font_size=20, color=C_VEC_2)
        panel = panel_derecha(cifra_a, cifra_b)
        self.play(GrowArrow(comb.au), GrowArrow(comb.bv), run_time=0.9)
        self.play(GrowArrow(comb.res), FadeIn(panel, shift=0.15 * LEFT),
                  run_time=0.8)
        self.wait(3.0)

        puntas = VGroup(pl.punto(comb.coords, color=C_IMG, radio=0.06))
        self.add(puntas)

        # --- momento: cambiar (a, b) y ver la punta saltar -----------------
        rot.mostrar(pie_curso("Cambia (a, b) y la punta salta a otro punto "
                              "del plano."), zona="abajo", run_time=0.5)
        self.wait(0.6)

        movil = comb
        for (a, b) in PAREJAS[1:]:
            destino = combinacion(pl, a, U_COMB, b, V_COMB, color_res=C_IMG,
                                  color_u=C_VEC, color_v=C_VEC_2)
            nueva_a = tag_hud(f"a = {fmt(a)}", font_size=20, color=C_VEC)
            nueva_a.move_to(cifra_a)
            nueva_b = tag_hud(f"b = {fmt(b)}", font_size=20, color=C_VEC_2)
            nueva_b.move_to(cifra_b)
            self.play(Transform(movil, destino), Transform(cifra_a, nueva_a),
                      Transform(cifra_b, nueva_b), run_time=1.3)
            punto = pl.punto(a * U_COMB + b * V_COMB, color=C_IMG, radio=0.06)
            puntas.add(punto)
            self.add(punto)
            self.wait(2.2)

        rot.mostrar(pie_curso("Cuatro parejas, cuatro puntos distintos: "
                              "¿hasta dónde llega si probamos todas?"),
                    zona="abajo", run_time=0.5)
        self.wait(4.6)
