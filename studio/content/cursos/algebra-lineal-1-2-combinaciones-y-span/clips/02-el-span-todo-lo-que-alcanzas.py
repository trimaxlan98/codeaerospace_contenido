class Clip2(Scene):
    """1.2.2 - El span es todo lo que a*u + b*v puede alcanzar: si u y v no
    estan alineados, un barrido de (a, b) llena el plano entero. (~38 s)"""

    def construct(self):
        rot = Rotulos(self)
        self.add(hud_modulo("Modulo 02"))

        titulo = titulo_curso("El span: todo lo que alcanzas")
        rot.mostrar(titulo, zona="arriba", run_time=0.6)
        self.wait(0.3)

        # --- momento: u y v otra vez ---------------------------------------
        pl = plano_leccion(vivo=False)
        u = vector(pl, U_COMB, color=C_VEC, nombre=r"\vec u")
        v = vector(pl, V_COMB, color=C_VEC_2, nombre=r"\vec v")
        self.play(FadeIn(pl), run_time=0.8)
        rot.mostrar(pie_curso("El span de u y v es TODO lo que a*u + b*v "
                              "puede alcanzar."), zona="abajo", run_time=0.5)
        self.play(GrowArrow(u.flecha), GrowArrow(v.flecha), FadeIn(u.etiqueta),
                  FadeIn(v.etiqueta), run_time=0.9)
        self.wait(4.6)

        # --- momento: barrido de (a, b) -------------------------------------
        rot.mostrar(pie_curso("Barremos (a, b): cada pareja deja una marca "
                              "verde en su punta."), zona="abajo",
                    run_time=0.5)
        self.wait(1.0)
        puntas = VGroup()
        for a in BARRIDO_AB:
            for b in BARRIDO_AB:
                coords = a * U_COMB + b * V_COMB
                puntas.add(pl.punto(coords, color=C_IMG, radio=0.045))
        self.play(LaggedStart(*[FadeIn(p) for p in puntas], lag_ratio=0.02),
                  run_time=5.0)
        self.wait(3.4)

        # --- momento: el manto que cubre el plano ---------------------------
        rot.mostrar(pie_curso("Las marcas no dejan huecos: barriendo (a, b) "
                              "se cubre el plano completo."), zona="abajo",
                    run_time=0.5)
        manto = Rectangle(width=config.frame_width, height=config.frame_height,
                          color=C_IMG, fill_color=C_IMG, fill_opacity=0.12,
                          stroke_width=0)
        manto.move_to(ORIGIN)
        self.play(FadeIn(manto), run_time=1.4)
        self.wait(5.2)

        rot.mostrar(pie_curso("Dos vectores no alineados generan las dos "
                              "dimensiones enteras del plano: su span."),
                    zona="abajo", run_time=0.5)
        self.wait(6.4)
