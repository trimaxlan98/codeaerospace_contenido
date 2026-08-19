class Clip1(Scene):
    """1.3.1 - Tres vectores en el plano; el tercero resulta ser una
    combinacion de los otros dos: sobra, no aporta una direccion nueva.
    (~37 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 01"))

        titulo = titulo_curso("El vector que sobra")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: tres vectores en el plano -----------------------------
        pl = plano_leccion(vivo=False)
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("Tres vectores en el plano. ¿Hacen falta "
                              "los tres?"), zona="abajo", run_time=0.5)
        u = vector(pl, U1, color=C_VEC, nombre=r"\vec u")
        v = vector(pl, V1, color=C_VEC_2, nombre=r"\vec v")
        w = vector(pl, W1, color=C_IMG, nombre=r"\vec w")
        self.play(GrowArrow(u.flecha), FadeIn(u.etiqueta), run_time=0.8)
        self.play(GrowArrow(v.flecha), FadeIn(v.etiqueta), run_time=0.8)
        self.play(GrowArrow(w.flecha), FadeIn(w.etiqueta), run_time=0.8)
        self.wait(3.6)

        # --- momento: reconstruir w con u y v -------------------------------
        rot.mostrar(pie_curso("Lo probamos: quitamos u y v, e intentamos "
                              "reconstruir w solo con ellos."),
                    zona="abajo", run_time=0.5)
        self.play(FadeOut(u.flecha), FadeOut(u.etiqueta),
                  FadeOut(v.flecha), FadeOut(v.etiqueta), run_time=0.7)
        self.wait(0.6)

        comb = combinacion(pl, A_W, U1, B_W, V1, color_u=C_VEC,
                           color_v=C_VEC_2, mostrar_res=False)
        et_a = MathTex(fmt(A_W, 1) + r"\,\vec u", font_size=28, color=C_VEC)
        et_a.move_to(pl.p(A_W * U1 * 0.5) + 0.4 * UP)
        rot.mostrar(pie_curso("Primero, u tal cual: su coeficiente es "
                              "uno."), zona="abajo", run_time=0.5)
        self.play(GrowArrow(comb.au), FadeIn(et_a), run_time=0.9)
        self.wait(2.6)

        et_b = MathTex(fmt(B_W, 1) + r"\,\vec v", font_size=28, color=C_VEC_2)
        et_b.move_to(pl.p(A_W * U1 + B_W * V1 * 0.5) + 0.4 * RIGHT)
        rot.mostrar(pie_curso("Y desde su punta, v estirado por uno "
                              "coma cinco."), zona="abajo", run_time=0.5)
        self.play(GrowArrow(comb.bv), FadeIn(et_b), run_time=0.9)
        self.wait(2.8)

        rot.mostrar(pie_curso("Aterriza justo en la punta de w: w sobra, "
                              "ya estaba en el plano de u y v."),
                    zona="abajo", run_time=0.5)
        self.play(Indicate(w.flecha, color=C_IMG, scale_factor=1.06),
                  run_time=0.9)
        self.wait(3.2)

        # --- momento: la cuenta que lo confirma ------------------------------
        rot.mostrar(pie_curso("Se puede resolver al revés: qué a y qué b "
                              "hacen a·u + b·v = w."), zona="abajo",
                    run_time=0.5)
        coefs = resolver(np.column_stack([U1, V1]), W1)
        cif_a = tag_hud("a = " + fmt(coefs[0], 1), font_size=20, color=C_VEC)
        cif_b = tag_hud("b = " + fmt(coefs[1], 1), font_size=20,
                        color=C_VEC_2)
        panel = panel_derecha(cif_a, cif_b)
        self.play(FadeIn(panel, shift=0.15 * LEFT), run_time=0.7)
        self.wait(4.2)

        rot.mostrar(pie_curso("Un vector que ya estaba en el span de los "
                              "otros no añade nada nuevo."), zona="abajo",
                    run_time=0.5)
        self.wait(4.4)
